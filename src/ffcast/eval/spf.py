"""ECB Survey of Professional Forecasters: microdata, matched model forecasts, outturns and
the Q4 bias regressions on fixed-event (calendar-year) targets. Tables only.

Survey definitions (SPF dataset description): HICP and core HICP inflation as year-on-year
percentage changes, real GDP growth year-on-year, unemployment rate in percent of the labour
force; calendar-year targets are annual averages; rolling targets are one and two years ahead
of the latest published month/quarter.

Matched model forecasts. For each round with a known survey window (docs/spf_rounds.md) the
models are run at origin = survey end + 1 day (information published on or before the last
survey day), on the euro-area targets hicp, hicp_core, gdp and unemp, with a horizon long enough
to reach December (Q4) of the year after next. The point path is the model mean where the model
reports one, else the median, in the transformed space; it is cumulated to a level path from the
last observed level of the same vintage and converted to the survey definition:
  HICP / core:  calendar year Y: 100 * (mean_m P_{Y,m} / mean_m P_{Y-1,m} - 1);
                rolling month T: 100 * (P_T / P_{T-12} - 1);
  GDP:          calendar year Y: annual average of quarterly levels, growth over Y-1;
                rolling quarter: 100 * (L_T / L_{T-4} - 1);
  unemployment: calendar year Y: mean of monthly rates in Y; rolling month: the rate at T.
Observed months of the current year come from the vintage, forecast months from the path.

Outturns for the same definitions: first release = inside the first vintage containing the last
period needed (December of Y, or T); revised = inside the vintage 12 months later.

Fixed-event regressions: for every forecaster (and for each model, the consensus mean and the
cross-model mean) and every calendar-year target, consecutive rounds give revision
f_k - f_{k-1} and error y - f_k; error is regressed on revision, pooled with forecaster fixed
effects (within transformation) for the survey panel, HAC standard errors.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, load_config
from ..data.raw import RawStore
from ..data.store import as_of, first_appearance, read_all
from ..models.lean import run_all
from ..models.panel import build_panel
from ..models.runner import make_task, model_settings
from ..models.weights import ensure_weights, weights_digest
from .backtest import run_benchmarks
from .bias import _hac_ols
from .outturns import add_months
from .store import BACKTEST_ROOT, write_atomic

SPF_ROOT = BACKTEST_ROOT / "spf"
VARIABLES = {
    "INFLATION EXPECTATIONS": "HICP",
    "CORE INFLATION EXPECTATIONS": "CORE",
    "GROWTH EXPECTATIONS": "RGDP",
    "EXPECTED UNEMPLOYMENT RATE": "UNEM",
}
TARGET_FOR = {"HICP": "hicp", "CORE": "hicp_core", "RGDP": "gdp", "UNEM": "unemp"}
_MON = {
    m: i + 1
    for i, m in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    )
}


# ------------------------------------------------------------------ microdata


def load_microdata(zip_path: Path) -> pd.DataFrame:
    """Tidy point forecasts: round, variable, target, target_type, forecaster, point."""
    rows = []
    with zipfile.ZipFile(zip_path) as z:
        for name in sorted(z.namelist()):
            rnd = name[:-4]
            var = None
            for line in z.read(name).decode("utf-8-sig", errors="replace").splitlines():
                if not line.strip(","):
                    continue
                head = line.split(",")[0]
                if not head[:1].isdigit():
                    if head.startswith("TARGET_PERIOD"):
                        continue
                    var = next((v for k, v in VARIABLES.items() if head.startswith(k)), None)
                    continue
                if var is None:
                    continue
                parts = line.split(",")
                if len(parts) < 3 or parts[2] == "":
                    continue
                try:
                    point = float(parts[2])
                except ValueError:
                    continue
                rows.append(
                    {
                        "round": rnd,
                        "variable": var,
                        "target": parts[0],
                        "forecaster": int(parts[1]),
                        "point": point,
                    }
                )
    df = pd.DataFrame(rows)
    ry = df["round"].str[:4].astype(int)
    tt = np.where(
        df["target"].str.fullmatch(r"\d{4}"),
        "calendar",
        np.where(df["target"].str.contains("Q"), "rolling_q", "rolling_m"),
    )
    df["target_type"] = tt
    ty = df["target"].str[:4].astype(int)
    df.loc[(df["target_type"] == "calendar") & (ty - ry >= 3), "target_type"] = "longterm"
    return df


def survey_windows(store: RawStore | None = None) -> dict[str, dict]:
    store = store or RawStore()
    days = store.list_days("ecb-spf")
    for d in reversed(days):
        p = store.dir_for("ecb-spf", d) / "survey_windows.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))["rounds"]
    raise FileNotFoundError("run `python -m ffcast.eval.spf_rounds` first")


# ------------------------------------------------------------------ survey-definition arithmetic


def _period_index(freq: str, last: str, horizon: int) -> list[str]:
    if freq == "M":
        p = pd.Period(last, freq="M")
        return [f"{(p + h).year}-{(p + h).month:02d}" for h in range(1, horizon + 1)]
    p = pd.Period(last.replace("-Q", "Q"), freq="Q")
    return [f"{(p + h).year}-Q{(p + h).quarter}" for h in range(1, horizon + 1)]


def level_path(levels: pd.Series, point: np.ndarray, kind: str, freq: str) -> pd.Series:
    """Observed levels (within vintage) followed by the levels implied by the point path."""
    last = float(levels.iloc[-1])
    if kind == "log_diff":
        fut = last * np.exp(np.cumsum(point) / 100.0)
    else:
        fut = last + np.cumsum(point)
    idx = _period_index(freq, str(levels.index[-1]), len(point))
    return pd.concat([levels.astype(float), pd.Series(fut, index=idx)])


def survey_value(path: pd.Series, variable: str, target: str, freq: str) -> float | None:
    """Value of a survey target (calendar year 'YYYY', rolling 'YYYYMon' or 'YYYYQn') on a
    level path indexed by 'YYYY-MM' or 'YYYY-Qn'."""
    if re.fullmatch(r"\d{4}", target):
        y = int(target)
        cur = path[[p.startswith(f"{y}-") for p in path.index]]
        prev = path[[p.startswith(f"{y - 1}-") for p in path.index]]
        need = 12 if freq == "M" else 4
        if len(cur) < need or len(prev) < need:
            return None
        if variable == "UNEM":
            return float(cur.mean())
        return float(100.0 * (cur.mean() / prev.mean() - 1.0))
    if "Q" in target:
        per = f"{target[:4]}-{target[4:]}"
        prev = f"{int(target[:4]) - 1}-{target[4:]}"
    else:
        per = f"{target[:4]}-{_MON[target[4:7]]:02d}"
        prev = f"{int(target[:4]) - 1}-{_MON[target[4:7]]:02d}"
    if per not in path.index:
        return None
    if variable == "UNEM":
        return float(path[per])
    if prev not in path.index:
        return None
    return float(100.0 * (path[per] / path[prev] - 1.0))


# ------------------------------------------------------------------ matched model runs


def _horizon(freq: str, last: str, round_year: int) -> int:
    """Steps from the last observed period to December / Q4 of round_year + 2."""
    if freq == "M":
        p = pd.Period(last, freq="M")
        return (round_year + 2 - p.year) * 12 + (12 - p.month)
    p = pd.Period(last.replace("-Q", "Q"), freq="Q")
    return (round_year + 2 - p.year) * 4 + (4 - p.quarter)


def spf_stage1(
    cfg: Config,
    rounds: dict[str, dict],
    workdir: Path,
    models: list[str] | None = None,
    run_bench: bool = True,
) -> dict:
    table = read_all()
    qs = tuple(cfg.scoring["quantiles"])
    fms = cfg.foundation_models()
    models = [m for m in (models or list(fms)) if m in fms]
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "requests").mkdir(exist_ok=True)
    meta: dict[str, dict] = {}
    bench_rows: list[dict] = []
    tasks: dict[str, list] = {m: [] for m in models}
    for rnd, w in sorted(rounds.items()):
        origin = dt.date.fromisoformat(w["end"]) + dt.timedelta(days=1)
        ry = int(rnd[:4])
        for var, tname in TARGET_FOR.items():
            t = cfg.targets["EA"][tname]
            if t.blocked:
                continue
            p = build_panel(cfg, table, "EA", tname, origin)
            if p is None:
                continue
            horizon = _horizon(p.freq, str(p.target_tr.index[-1]), ry)
            if horizon <= 0:
                continue
            base = {
                "round": rnd,
                "origin": origin.isoformat(),
                "variable": var,
                "target": tname,
                "freq": p.freq,
                "kind": p.kind,
                "series_id": p.target_sid,
                "source_role": p.source_role,
                "last_period": str(p.target_tr.index[-1]),
                "horizon": horizon,
            }
            if run_bench:
                fcs, rts, errs = run_benchmarks(cfg, p, horizon, qs)
                for m, fc in fcs.items():
                    pt = fc.mean if fc.mean is not None else fc.median()
                    bench_rows.append(
                        {
                            **base,
                            "model": m,
                            "point_path": json.dumps([float(x) for x in pt]),
                            "levels": json.dumps(
                                {str(k): float(v) for k, v in p.target_levels.items()}
                            ),
                        }
                    )
            for m in models:
                tid = f"{rnd}|{var}"
                tasks[m].append(
                    make_task(tid, p.univariate(), p.freq, horizon, qs).__dict__
                    | {"quantiles": list(qs)}
                )
                meta[f"{m}:{tid}"] = {
                    **base,
                    "tid": tid,
                    "levels": {str(k): float(v) for k, v in p.target_levels.items()},
                }
    for m in models:
        if not tasks[m]:
            continue
        settings = model_settings(cfg, m)
        wdir, man = ensure_weights(fms[m], allow_download=settings.get("allow_download", True))
        maxh = max(t["horizon"] for t in tasks[m])
        if m == "timesfm25" and settings.get("max_horizon", 12) < maxh:
            settings = {
                **settings,
                "max_horizon": int(maxh),
            }  # SPF horizons exceed the backtest setting; recorded in the request
        req = {
            "model": fms[m].hf_id,
            "env": fms[m].env,
            "weights_dir": str(wdir),
            "weights_digest": weights_digest(man),
            "settings": settings,
            "tasks": tasks[m],
        }
        (workdir / "requests" / f"{m}.json").write_text(json.dumps(req), encoding="utf-8")
    (workdir / "task_meta.json").write_text(json.dumps(meta), encoding="utf-8")
    write_atomic(pd.DataFrame(bench_rows), SPF_ROOT / "bench_paths.parquet")
    return {
        "rounds": len(rounds),
        "bench_rows": len(bench_rows),
        "fm_tasks": sum(len(v) for v in tasks.values()),
    }


def spf_stage3(cfg: Config, workdir: Path) -> pd.DataFrame:
    """Model point forecasts in survey definitions, one row per (round, model, variable, target)."""
    meta = json.loads((workdir / "task_meta.json").read_text(encoding="utf-8"))
    micro = load_microdata(_zip_path())
    targets_by_round_var = micro.groupby(["round", "variable"])["target"].unique()
    rows = []
    paths = []  # (base, model, point array, levels)
    for rp in sorted((workdir / "requests").glob("*.json")):
        m = rp.stem
        resp_path = workdir / "responses" / rp.name
        if not resp_path.exists():
            continue
        resp = json.loads(resp_path.read_text(encoding="utf-8"))
        for tid, r in resp["results"].items():
            tm = meta[f"{m}:{tid}"]
            q = np.asarray(r["quantiles"], dtype=float)
            pt = (
                np.asarray(r["mean"], dtype=float)
                if r.get("mean") is not None
                else q[:, q.shape[1] // 2]
            )
            paths.append((tm, m, pt, tm["levels"]))
    bp = SPF_ROOT / "bench_paths.parquet"
    if bp.exists():
        for _, r in pd.read_parquet(bp).iterrows():
            paths.append(
                (
                    r.to_dict(),
                    r["model"],
                    np.asarray(json.loads(r["point_path"])),
                    json.loads(r["levels"]),
                )
            )
    for tm, model, pt, levels in paths:
        lv = pd.Series(levels)
        path = level_path(lv, pt, tm["kind"], tm["freq"])
        for target in targets_by_round_var.get((tm["round"], tm["variable"]), []):
            v = survey_value(path, tm["variable"], target, tm["freq"])
            if v is None:
                continue
            rows.append(
                {
                    "round": tm["round"],
                    "origin": tm["origin"],
                    "variable": tm["variable"],
                    "target": target,
                    "model": model,
                    "point": v,
                    "series_id": tm["series_id"],
                    "source_role": tm["source_role"],
                    "last_period": tm["last_period"],
                    "freq": tm["freq"],
                    "kind": tm["kind"],
                }
            )
    out = pd.DataFrame(rows)
    write_atomic(out, SPF_ROOT / "model_points.parquet")
    return out


def _zip_path() -> Path:
    st = RawStore()
    for d in reversed(st.list_days("ecb-spf")):
        p = st.dir_for("ecb-spf", d) / "SPF_individual_forecasts_by_round.zip"
        if p.exists():
            return p
    raise FileNotFoundError("SPF zip not in the raw store")


# ------------------------------------------------------------------ outturns in survey definitions


def spf_outturns(cfg: Config, points: pd.DataFrame, months_after: int = 12) -> pd.DataFrame:
    table = read_all()
    rows = []
    fa_cache: dict[str, pd.Series] = {}
    for (variable, target, sid, freq, _kind), _ in points.groupby(
        ["variable", "target", "series_id", "freq", "kind"]
    ):
        if sid not in fa_cache:
            fa_cache[sid] = first_appearance(table, sid)
        fa = fa_cache[sid]
        # last period needed
        if re.fullmatch(r"\d{4}", target):
            last = f"{target}-12" if freq == "M" else f"{target}-Q4"
        elif "Q" in target:
            last = f"{target[:4]}-{target[4:]}"
        else:
            last = f"{target[:4]}-{_MON[target[4:7]]:02d}"
        if last not in fa.index:
            rows.append(
                {
                    "variable": variable,
                    "target": target,
                    "series_id": sid,
                    "first_release": np.nan,
                    "revised_12m": np.nan,
                    "first_release_date": None,
                }
            )
            continue
        d0 = pd.Timestamp(fa[last]).date()
        vals = []
        for when, strict in (
            (d0 + dt.timedelta(days=1), True),
            (add_months(d0, months_after), False),
        ):
            v = as_of(table, [sid], when, strict=strict)[sid]
            if cfg.backtest.get("revision_rounding", {}).get(TARGET_FOR[variable]) is not None:
                v = v.round(cfg.backtest["revision_rounding"][TARGET_FOR[variable]])
            vals.append(survey_value(v, variable, target, freq))
        rows.append(
            {
                "variable": variable,
                "target": target,
                "series_id": sid,
                "first_release": vals[0],
                "revised_12m": vals[1],
                "first_release_date": d0.isoformat(),
            }
        )
    out = pd.DataFrame(rows)
    write_atomic(out, SPF_ROOT / "outturns_spf.parquet")
    return out


# ------------------------------------------------------------------ regressions


def fixed_event_rows(df: pd.DataFrame, id_col: str, outturn_col: str) -> pd.DataFrame:
    """Consecutive-round revisions and errors per (id, variable, calendar-year target)."""
    rows = []
    for (fid, var, target), g in df.groupby([id_col, "variable", "target"]):
        g = g.sort_values("round")
        if len(g) < 2 or g[outturn_col].isna().all():
            continue
        f = g["point"].to_numpy(dtype=float)
        y = float(g[outturn_col].iloc[0])
        for k in range(1, len(g)):
            rows.append(
                {
                    "id": fid,
                    "variable": var,
                    "target": target,
                    "round": g["round"].iloc[k],
                    "revision": f[k] - f[k - 1],
                    "error": y - f[k],
                }
            )
    return pd.DataFrame(rows)


def _within(df: pd.DataFrame, by: str) -> pd.DataFrame:
    out = df.copy()
    for c in ("revision", "error"):
        out[c] = out[c] - out.groupby(by)[c].transform("mean")
    return out


def spf_regressions(
    cfg: Config, micro: pd.DataFrame, points: pd.DataFrame, outturns: pd.DataFrame, rounds: dict
) -> pd.DataFrame:
    used = sorted(rounds)
    micro = micro[(micro["round"].isin(used)) & (micro["target_type"] == "calendar")]
    o = outturns[["variable", "target", "first_release", "revised_12m"]]
    micro = micro.merge(o, on=["variable", "target"], how="left")
    cons = (
        micro.groupby(
            ["round", "variable", "target", "first_release", "revised_12m"], dropna=False
        )["point"]
        .mean()
        .reset_index()
    )
    cons["forecaster"] = "consensus"
    pts = points[points["target"].str.fullmatch(r"\d{4}")].merge(
        o, on=["variable", "target"], how="left"
    )
    fm_members = cfg.models["benchmarks"]["combo_fm"]["of"]
    avg = (
        pts[pts["model"].isin(fm_members)]
        .groupby(["round", "variable", "target", "first_release", "revised_12m"], dropna=False)
        .agg(point=("point", "mean"), n=("model", "nunique"))
        .reset_index()
    )
    avg = avg[avg["n"] == len(fm_members)].drop(columns="n")
    avg["model"] = "combo_fm"
    pts = pd.concat([pts, avg[pts.columns.intersection(avg.columns)]], ignore_index=True)
    rows = []
    for outturn in ("first_release", "revised_12m"):
        # individual forecasters, pooled with forecaster fixed effects, per variable
        ind = fixed_event_rows(micro, "forecaster", outturn)
        for var, g in ind.groupby("variable"):
            if len(g) < 30:
                continue
            w = _within(g, "id")
            b, se, a, n = _hac_ols(w["error"].to_numpy(), w["revision"].to_numpy(), 3)
            rows.append(
                {
                    "who": "spf_individual_fe",
                    "variable": var,
                    "outturn": outturn,
                    "n": n,
                    "n_ids": g["id"].nunique(),
                    "beta": b,
                    "se_hac": se,
                    "t": b / se if se > 0 else np.nan,
                }
            )
        # consensus
        cr = fixed_event_rows(cons, "forecaster", outturn)
        for var, g in cr.groupby("variable"):
            if len(g) < 12:
                continue
            b, se, a, n = _hac_ols(g["error"].to_numpy(), g["revision"].to_numpy(), 3)
            rows.append(
                {
                    "who": "spf_consensus",
                    "variable": var,
                    "outturn": outturn,
                    "n": n,
                    "n_ids": 1,
                    "beta": b,
                    "se_hac": se,
                    "t": b / se if se > 0 else np.nan,
                }
            )
        # models, same rounds and targets
        mr = fixed_event_rows(pts, "model", outturn)
        for (model, var), g in mr.groupby(["id", "variable"]):
            if len(g) < 12:
                continue
            b, se, a, n = _hac_ols(g["error"].to_numpy(), g["revision"].to_numpy(), 3)
            rows.append(
                {
                    "who": f"model:{model}",
                    "variable": var,
                    "outturn": outturn,
                    "n": n,
                    "n_ids": 1,
                    "beta": b,
                    "se_hac": se,
                    "t": b / se if se > 0 else np.nan,
                }
            )
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ driver


def run_spf(
    cfg: Config | None = None,
    models: list[str] | None = None,
    run_bench: bool = True,
    skip_models: bool = False,
) -> dict:
    cfg = cfg or load_config()
    rounds = survey_windows()
    workdir = SPF_ROOT / "work"
    rep = {"rounds_used": len(rounds)}
    if not skip_models:
        rep.update(spf_stage1(cfg, rounds, workdir, models, run_bench))
        if any((workdir / "requests").glob("*.json")):
            rep["workers"] = run_all(workdir / "requests", workdir / "responses")
    points = spf_stage3(cfg, workdir)
    out = spf_outturns(cfg, points)
    micro = load_microdata(_zip_path())
    write_atomic(micro, SPF_ROOT / "spf_microdata.parquet")
    reg = spf_regressions(cfg, micro, points, out, rounds)
    d = BACKTEST_ROOT / "tables"
    d.mkdir(parents=True, exist_ok=True)
    reg.to_csv(d / "bias_spf_fixed_event.csv", index=False)
    rep.update({"model_points": len(points), "outturns": len(out), "regression_rows": len(reg)})
    return rep


if __name__ == "__main__":
    import sys

    print(
        json.dumps(
            run_spf(models=[m for m in sys.argv[1].split(",") if m] if len(sys.argv) > 1 else None),
            default=str,
        )
    )
