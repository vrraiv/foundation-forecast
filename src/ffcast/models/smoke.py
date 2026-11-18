"""Phase 3 smoke test in three stages (see ffcast.models.lean): every model and benchmark
produces forecasts for one origin for every target, with mechanical magnitude checks and
recorded runtimes. Never compares with outturns.

Sane-magnitude rule (fixed in advance): every quantile of the h-step forecast in transformed
space must lie within [min - 3*sd, max + 3*sd] of the target's own transformed history at the
origin, quantiles must be non-decreasing, and every model's step 1 must refer to the first
period after the target's last observation in its own vintage.
"""

from __future__ import annotations

import datetime as dt
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..bench import ARDirect, BVARMinnesota, DynamicFactorMQBench, EqualWeight, Naive
from ..config import Config, load_config
from ..data.store import read_all
from .interface import QuantileForecast
from .panel import Panel, build_panel
from .runner import make_task, model_settings
from .weights import ensure_weights, weights_digest


@dataclass
class SmokeRow:
    econ: str
    target: str
    model: str
    variant: str
    horizon: int
    ok: bool
    note: str
    runtime_s: float
    median_h1: float | None
    step1_period: str | None = None
    n_vars: int | None = None


def sane_bounds(hist: pd.Series) -> tuple[float, float]:
    return float(hist.min() - 3 * hist.std()), float(hist.max() + 3 * hist.std())


def sane_values(v: np.ndarray, lo: float, hi: float) -> tuple[bool, str]:
    if not np.isfinite(v).all():
        return False, "non-finite values"
    if (np.diff(v, axis=1) < -1e-9).any():
        return False, "quantile crossing"
    if (v < lo).any() or (v > hi).any():
        return False, f"outside [{lo:.3g}, {hi:.3g}]"
    return True, ""


def sane(fc: QuantileForecast, hist: pd.Series) -> tuple[bool, str]:
    return sane_values(fc.values, *sane_bounds(hist))


def _norm_period(p) -> str | None:
    if p is None:
        return None
    s = str(p)
    return s if "-Q" in s or len(s) == 7 else s.replace("Q", "-Q")


def run_benchmarks(
    cfg: Config, panel: Panel, horizon: int, qs
) -> dict[str, tuple[QuantileForecast, float]]:
    out = {}
    bcfg = cfg.models["benchmarks"]
    t0 = time.perf_counter()
    out["naive"] = (Naive().forecast(panel.univariate(), horizon, qs), time.perf_counter() - t0)
    t0 = time.perf_counter()
    ar = ARDirect(bcfg["ar"]["max_lag"][panel.freq])
    out["ar"] = (ar.forecast(panel.univariate(), horizon, qs), time.perf_counter() - t0)
    b = bcfg["bvar"]
    t0 = time.perf_counter()
    mv = panel.multivariate(b["max_vars"])
    if mv.shape[1] >= 2:
        bv = BVARMinnesota(
            b["lags"][panel.freq],
            b["lambda_grid"],
            b["soc_grid"],
            b["dio_grid"],
            b["decay"],
            b["draws"],
            0,
            b["max_vars"],
            b.get("min_balanced", {}).get(panel.freq, 72),
        )
        out["bvar"] = (bv.forecast(mv, horizon, qs), time.perf_counter() - t0)
    d = bcfg["dfm"]
    t0 = time.perf_counter()
    try:
        dfm = DynamicFactorMQBench(
            d["factors"],
            d["factor_order"],
            d["idiosyncratic_ar1"],
            d["max_vars"],
            d.get("maxiter", 100),
        )
        if panel.freq == "M":
            q = panel.quarterly if not panel.quarterly.empty else None
            fc = dfm.forecast(panel.monthly, horizon, qs, quarterly=q)
        else:
            fc = dfm.forecast(
                panel.monthly, horizon, qs, quarterly=panel.quarterly, target_is_quarterly=True
            )
        out["dfm"] = (fc, time.perf_counter() - t0)
    except Exception as e:  # noqa: BLE001
        out["dfm"] = (None, time.perf_counter() - t0)
        out["dfm_error"] = str(e)[:300]
    return out


# ------------------------------------------------------------------ stage 1 (heavy)


def stage1(
    origin: dt.date,
    workdir: Path,
    cfg: Config | None = None,
    models: list[str] | None = None,
    run_bench: bool = True,
) -> None:
    cfg = cfg or load_config()
    table = read_all()
    qs = tuple(cfg.scoring["quantiles"])
    max_vars = cfg.models["benchmarks"]["bvar"]["max_vars"]
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "requests").mkdir(exist_ok=True)
    rows: list[SmokeRow] = []
    panels: dict[tuple[str, str], Panel] = {}
    task_meta: dict[str, dict] = {}
    for econ in cfg.economies:
        for tname, t in cfg.targets[econ].items():
            if t.blocked:
                rows.append(
                    SmokeRow(
                        econ, tname, "-", "-", 0, False, f"blocked: {t.blocked[:80]}", 0.0, None
                    )
                )
                continue
            p = build_panel(cfg, table, econ, tname, origin)
            if p is None:
                rows.append(
                    SmokeRow(econ, tname, "-", "-", 0, False, "no data at origin", 0.0, None)
                )
                continue
            panels[(econ, tname)] = p
            horizon = max(cfg.horizons[p.freq])
            expected = p.target_periods(horizon)[0]
            if not run_bench:
                continue
            bench = run_benchmarks(cfg, p, horizon, qs)
            fcs = {}
            for name, val in bench.items():
                if name.endswith("_error"):
                    rows.append(
                        SmokeRow(econ, tname, name[:-6], "uni", horizon, False, val, 0.0, None)
                    )
                    continue
                fc, rt = val
                if fc is None:
                    continue
                ok, note = sane(fc, p.target_tr)
                s1 = _norm_period(fc.meta.get("step1_period"))
                if s1 is not None and s1 != expected:
                    ok, note = False, f"step 1 refers to {s1}, expected {expected}"
                fcs[name] = fc
                nv = len(fc.meta.get("vars", [])) or fc.meta.get("n_monthly")
                variant = "uni" if name in ("naive", "ar") else "multi"
                rows.append(
                    SmokeRow(
                        econ,
                        tname,
                        name,
                        variant,
                        horizon,
                        ok,
                        note,
                        round(rt, 3),
                        float(fc.median()[0]),
                        expected,
                        nv,
                    )
                )
            members = cfg.models["benchmarks"]["combo_bench"]["of"]
            combo = EqualWeight("combo_bench", members).combine(fcs)
            if combo is not None:
                ok, note = sane(combo, p.target_tr)
                rows.append(
                    SmokeRow(
                        econ,
                        tname,
                        "combo_bench",
                        "multi",
                        horizon,
                        ok,
                        note,
                        0.0,
                        float(combo.median()[0]),
                        expected,
                        None,
                    )
                )
    # foundation-model requests, one file per model
    for mname, fm in cfg.foundation_models().items():
        if models and mname not in models:
            continue
        tasks = []
        for (econ, tname), p in panels.items():
            horizon = max(cfg.horizons[p.freq])
            lo, hi = sane_bounds(p.target_tr)
            for variant in fm.variants:
                if variant == "univariate":
                    hist = p.univariate()
                    nv = 1
                else:
                    hist = p.multivariate(max_vars, balanced=True)
                    nv = hist.shape[1]
                    if nv < 2:
                        continue
                tid = f"{econ}.{tname}.{variant}"
                tasks.append(make_task(tid, hist, p.freq, horizon, qs))
                task_meta[tid] = {
                    "econ": econ,
                    "target": tname,
                    "model": mname,
                    "variant": variant,
                    "horizon": horizon,
                    "lo": lo,
                    "hi": hi,
                    "expected_step1": p.target_periods(horizon)[0],
                    "n_vars": nv,
                }
        if not tasks:
            continue
        settings = model_settings(cfg, mname)
        wdir, manifest = ensure_weights(fm, allow_download=settings.get("allow_download", True))
        sizes = [(wdir / f).stat().st_size for f in manifest["files"] if (wdir / f).exists()]
        largest_mb = max(sizes, default=0) // (1 << 20)
        settings = {
            **settings,
            "min_free_commit_mb": settings.get("min_free_commit_mb", 2 * largest_mb + 600),
        }
        req = {
            "model": fm.hf_id,
            "env": fm.env,
            "weights_dir": str(wdir),
            "weights_digest": weights_digest(manifest),
            "settings": settings,
            "tasks": [t.__dict__ | {"quantiles": list(t.quantiles)} for t in tasks],
        }
        (workdir / "requests" / f"{mname}.json").write_text(json.dumps(req), encoding="utf-8")
    realised = {
        f"{e}.{t}": {
            "target_sid": p.target_sid,
            "source_role": p.source_role,
            "target_last": str(p.target_tr.index[-1]),
            "multivariate_vars": list(p.multivariate(max_vars).columns),
            "balanced_fm_vars": list(p.multivariate(max_vars, balanced=True).columns),
            "dropped": p.dropped,
        }
        for (e, t), p in panels.items()
    }
    (workdir / "panels.json").write_text(json.dumps(realised, indent=1), encoding="utf-8")
    (workdir / "bench_rows.json").write_text(
        json.dumps([asdict(r) for r in rows], indent=1), encoding="utf-8"
    )
    (workdir / "task_meta.json").write_text(json.dumps(task_meta, indent=1), encoding="utf-8")


# ------------------------------------------------------------------ stage 3 (heavy)


def stage3(workdir: Path, out_csv: Path) -> pd.DataFrame:
    rows = [
        SmokeRow(**r) for r in json.loads((workdir / "bench_rows.json").read_text(encoding="utf-8"))
    ]
    meta = json.loads((workdir / "task_meta.json").read_text(encoding="utf-8"))
    status_file = workdir / "responses" / "_status.json"
    status = json.loads(status_file.read_text(encoding="utf-8")) if status_file.exists() else {}
    by_model: dict[str, list[str]] = {}
    for tid, m in meta.items():
        by_model.setdefault(m["model"], []).append(tid)
    for mname, tids in by_model.items():
        rp = workdir / "responses" / f"{mname}.json"
        if not rp.exists():
            msg = "worker failed: " + status.get(mname, "no response")[-200:]
            rows.append(SmokeRow("-", "-", mname, "-", 0, False, msg, 0.0, None))
            continue
        resp = json.loads(rp.read_text(encoding="utf-8"))
        req = json.loads((workdir / "requests" / f"{mname}.json").read_text(encoding="utf-8"))
        for tid in tids:
            m = meta[tid]
            r = resp["results"].get(tid)
            if r is None:
                err = resp["errors"].get(tid, "missing")[:200]
                rows.append(
                    SmokeRow(
                        m["econ"],
                        m["target"],
                        mname,
                        m["variant"][:5],
                        m["horizon"],
                        False,
                        err,
                        0.0,
                        None,
                        m["expected_step1"],
                        m["n_vars"],
                    )
                )
                continue
            q = np.sort(np.asarray(r["quantiles"], dtype=float), axis=1)
            ok, note = sane_values(q, m["lo"], m["hi"])
            rows.append(
                SmokeRow(
                    m["econ"],
                    m["target"],
                    mname,
                    m["variant"][:5],
                    m["horizon"],
                    ok,
                    note,
                    r["runtime_s"],
                    float(q[0, q.shape[1] // 2]),
                    m["expected_step1"],
                    m["n_vars"],
                )
            )
        note = (
            f"worker wall time incl. load; weights {req['weights_digest'][:12]}; "
            f"versions {resp.get('versions')}"
        )
        rows.append(SmokeRow("-", "-", mname, "wall", 0, True, note, resp.get("wall_s", 0.0), None))
    df = pd.DataFrame([asdict(r) for r in rows])
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df


if __name__ == "__main__":
    import sys

    stage = sys.argv[1]
    if stage == "stage1":
        origin = dt.date.fromisoformat(sys.argv[2])
        workdir = Path(sys.argv[3])
        models = ([m for m in sys.argv[4].split(",") if m] or None) if len(sys.argv) > 4 else None
        run_bench = (sys.argv[5] == "1") if len(sys.argv) > 5 else True
        stage1(origin, workdir, models=models, run_bench=run_bench)
    elif stage == "stage3":
        df = stage3(Path(sys.argv[2]), Path(sys.argv[3]))
        print(df.to_string(index=False, max_colwidth=70))
        bad = df[~df["ok"] & (df["variant"] != "wall")]
        print(f"\n{len(df)} rows, {len(bad)} failed checks; written to {sys.argv[3]}")
    else:
        raise SystemExit(
            "usage: smoke.py stage1 ORIGIN WORKDIR [MODELS] [RUN_BENCH] | stage3 WORKDIR OUT_CSV"
        )
