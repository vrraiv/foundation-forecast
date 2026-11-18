"""Scoring tables (Phase 4, PLAN section 2 "Scoring"). Tables only, no interpretation.

Cells: (econ, target, horizon, model, variant, input_mode, outturn, sample, window, split).
  outturn  first_release | revised_12m
  sample   full | ex_covid           (exclusion window on the TARGET period)
  window   primary (origins from cfg.origins.first) | all (extension included)
  split    all | pre | post          (origin before / on-or-after the model's weights_date;
                                      foundation models only; "all" for every model)

Metrics: n, rmsfe, mae, rel_rmsfe and rel_mae to the AR benchmark of the same cell (realtime
AR for realtime cells, revised AR for revised cells), Diebold-Mariano statistic against AR with
the Harvey-Leybourne-Newbold correction and its two-sided p-value (squared-error loss, Bartlett
kernel with h-1 lags), weighted quantile loss (mean pinball loss over the nine quantiles, times
two: a CRPS approximation), 80% interval coverage, and the PIT histogram as ten bin shares.
Model confidence set (Hansen, Lunde and Nason 2011, T_max statistic, moving-block bootstrap,
90% level) per cell group across all models with the same n.

Levels variant: level quantiles are mapped to the step-1 transform (scored with the main
tables as variant `<variant>_levels`) and to the cumulative h-step change (separate table,
absolute metrics only).
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from ..config import Config, load_config
from .store import BACKTEST_ROOT, read_forecasts, read_meta

TABLES = "tables"


# ------------------------------------------------------------------ loading and derived rows


def load_scored_frame(cfg: Config, root: Path = BACKTEST_ROOT) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Wide frame: one row per (origin, econ, target, model, variant, input_mode, step) with the
    nine quantiles as columns q0.1..q0.9, the mean, the target period, both outturns, and the
    tags used for sample splits. Second frame: the cumulative (levels-variant) rows."""
    fc = read_forecasts(root)
    meta = read_meta(root)
    if fc.empty:
        return pd.DataFrame(), pd.DataFrame()
    out = pd.read_parquet(root / "outturns.parquet")
    cum = (
        pd.read_parquet(root / "cumulative_outturns.parquet")
        if (root / "cumulative_outturns.parquet").exists()
        else pd.DataFrame()
    )
    qs = sorted(fc["quantile"].unique())
    keys = [
        "origin",
        "econ",
        "target",
        "freq",
        "model",
        "variant",
        "input_mode",
        "space",
        "step",
        "target_period",
        "series_id",
        "source_role",
    ]
    wide = fc.pivot_table(index=keys, columns="quantile", values="value", aggfunc="first")
    wide.columns = [f"q{q:.1f}" for q in wide.columns]
    means = fc.groupby(keys)["mean"].first()
    wide["mean"] = means
    wide = wide.reset_index()
    # last level per (origin, econ, target, input_mode) for the levels variant
    ll = meta.dropna(subset=["last_level"]).drop_duplicates(
        ["origin", "econ", "target", "input_mode"]
    )[["origin", "econ", "target", "input_mode", "last_period", "last_level"]]
    wide = wide.merge(ll, on=["origin", "econ", "target", "input_mode"], how="left")
    kinds = {(e, t): cfg.targets[e][t].transform for e in cfg.economies for t in cfg.targets[e]}
    wide["kind"] = [kinds[(e, t)] for e, t in zip(wide["econ"], wide["target"], strict=True)]
    qcols = [f"q{q:.1f}" for q in qs]
    # --- levels variant -> step-1 transform rows, and cumulative rows
    lv = wide[wide["space"] == "level"].copy()
    tr = wide[wide["space"] == "transformed"].copy()
    cum_rows = pd.DataFrame()
    if not lv.empty:

        def to_change(df, cols):
            a = df["last_level"].to_numpy()[:, None]
            v = df[cols].to_numpy(dtype=float)
            ld = df["kind"].to_numpy() == "log_diff"
            res = np.where(ld[:, None], 100.0 * np.log(v / a), v - a)
            return res

        cumv = lv.copy()
        cumv[qcols] = to_change(lv, qcols)
        cumv["mean"] = np.where(
            lv["kind"] == "log_diff",
            100.0 * np.log(lv["mean"].to_numpy(dtype=float) / lv["last_level"].to_numpy()),
            lv["mean"] - lv["last_level"],
        )
        cumv["variant"] = cumv["variant"] + "_levels"
        cumv["space"] = "cumulative"
        step1 = cumv[cumv["step"] == 1].copy()
        step1["space"] = "transformed"
        tr = pd.concat([tr, step1], ignore_index=True)
        if not cum.empty:
            cum_rows = cumv.merge(
                cum.rename(columns={"period": "target_period"}),
                on=["econ", "target", "series_id", "last_period", "target_period"],
                how="left",
            )
    # --- equal-weight combination of foundation models (all members present)
    members = cfg.models["benchmarks"]["combo_fm"]["of"]
    base = tr[(tr["model"].isin(members)) & (tr["variant"] == "univariate")]
    if not base.empty:
        g = base.groupby(
            [
                "origin",
                "econ",
                "target",
                "freq",
                "input_mode",
                "step",
                "target_period",
                "series_id",
                "source_role",
                "last_period",
                "last_level",
                "kind",
            ],
            dropna=False,
        )
        agg = g[qcols + ["mean"]].mean()
        cnt = g["model"].nunique()
        agg = agg[cnt == len(members)].reset_index()
        agg["model"] = "combo_fm"
        agg["variant"] = "univariate"
        agg["space"] = "transformed"
        tr = pd.concat([tr, agg[tr.columns]], ignore_index=True)
    # --- outturns
    o = out.rename(columns={"period": "target_period"})[
        ["econ", "target", "series_id", "target_period", "first_release", "late", "revised_12m"]
    ]
    tr = tr.merge(o, on=["econ", "target", "series_id", "target_period"], how="left")
    tr["horizon"] = tr["step"]
    return tr, cum_rows


# ------------------------------------------------------------------ metrics


def pinball(y: np.ndarray, q: np.ndarray, levels: np.ndarray) -> np.ndarray:
    """Mean over quantile levels of the pinball loss, times two (CRPS approximation)."""
    d = y[:, None] - q
    loss = np.where(d >= 0, levels[None, :] * d, (levels[None, :] - 1.0) * d)
    return 2.0 * loss.mean(axis=1)


def pit_bins(y: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Share of outturns in each of the K+1 bins delimited by the K quantiles."""
    k = (y[:, None] > q).sum(axis=1)  # 0..K
    return np.bincount(k, minlength=q.shape[1] + 1) / len(y)


def dm_hln(d: np.ndarray, h: int) -> tuple[float, float]:
    """Diebold-Mariano on loss differentials d (model minus AR) with the HLN small-sample
    correction; Bartlett long-run variance with h-1 lags. Returns (statistic, p-value)."""
    n = len(d)
    if n < 8:
        return np.nan, np.nan
    dbar = d.mean()
    dc = d - dbar
    lrv = float(dc @ dc) / n
    for k in range(1, min(h, n)):
        w = 1.0 - k / h
        lrv += 2.0 * w * float(dc[k:] @ dc[:-k]) / n
    if lrv <= 0:
        return np.nan, np.nan
    dm = dbar / np.sqrt(lrv / n)
    corr = np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    stat = dm * corr
    p = 2.0 * stats.t.sf(abs(stat), df=n - 1)
    return float(stat), float(p)


def mcs(
    losses: pd.DataFrame,
    alpha: float = 0.10,
    B: int = 1000,
    block: int | None = None,
    seed: int = 0,
) -> dict[str, float]:
    """Hansen-Lunde-Nason model confidence set with the T_max statistic and a moving-block
    bootstrap. `losses`: T x M frame (no NaN). Returns MCS p-value per model (model is in the
    (1-alpha) MCS iff p >= alpha)."""
    L = losses.to_numpy(dtype=float)
    T, M = L.shape
    names = list(losses.columns)
    if M < 2 or T < 8:
        return {m: np.nan for m in names}
    rng = np.random.default_rng(seed)
    blk = block or max(2, int(round(T ** (1 / 3))))
    nblk = int(np.ceil(T / blk))
    starts = rng.integers(0, T - blk + 1, size=(B, nblk))
    idx = (starts[:, :, None] + np.arange(blk)[None, None, :]).reshape(B, -1)[:, :T]
    pvals: dict[str, float] = {}
    alive = list(range(M))
    p_prev = 0.0
    while len(alive) > 1:
        sub = L[:, alive]
        dbar_i = sub.mean(axis=0) - sub.mean()  # d_i. = mean_j (L_i - L_j)
        boot = L[idx][:, :, alive].mean(axis=1)  # B x m
        boot_di = boot - boot.mean(axis=1, keepdims=True)
        var_i = ((boot_di - dbar_i[None, :]) ** 2).mean(axis=0)
        t_i = dbar_i / np.sqrt(np.maximum(var_i, 1e-18))
        t_boot = (boot_di - dbar_i[None, :]) / np.sqrt(np.maximum(var_i, 1e-18))[None, :]
        tmax = t_i.max()
        p = float((t_boot.max(axis=1) >= tmax).mean())
        p = max(p, p_prev)
        worst = alive[int(np.argmax(t_i))]
        pvals[names[worst]] = p
        p_prev = p
        alive.remove(worst)
    pvals[names[alive[0]]] = 1.0
    return pvals


# ------------------------------------------------------------------ tables


def _in_window(periods: pd.Series, window: list[str]) -> np.ndarray:
    lo, hi = window
    p = periods.str.replace("-Q", "Q")
    pm = pd.PeriodIndex(p, freq="M") if not p.str.contains("Q").any() else None
    if pm is not None:
        return ((pm >= pd.Period(lo, "M")) & (pm <= pd.Period(hi, "M"))).to_numpy()
    out = np.zeros(len(p), dtype=bool)
    for i, s in enumerate(p):
        per = pd.Period(s, "Q") if "Q" in s else pd.Period(s, "M")
        a = pd.Period(lo, "Q") if "Q" in s else pd.Period(lo, "M")
        b = pd.Period(hi, "Q") if "Q" in s else pd.Period(hi, "M")
        out[i] = a <= per <= b
    return out


def score_tables(cfg: Config | None = None, root: Path = BACKTEST_ROOT) -> dict[str, pd.DataFrame]:
    cfg = cfg or load_config()
    tr, cum = load_scored_frame(cfg, root)
    if tr.empty:
        return {}
    qs = [c for c in tr.columns if c.startswith("q0.")]
    levels = np.array([float(c[1:]) for c in qs])
    lo_q, hi_q = (
        f"q{(1 - cfg.scoring['interval_coverage']) / 2:.1f}",
        f"q{1 - (1 - cfg.scoring['interval_coverage']) / 2:.1f}",
    )
    primary_first = cfg.origins.first
    covid = cfg.exclusion_windows["covid"]
    fms = cfg.foundation_models()
    tr["ex_covid"] = ~_in_window(tr["target_period"], covid)
    tr["primary"] = tr["origin"] >= primary_first
    rows = []
    pit_rows = []
    mcs_rows = []
    for (econ, target, freq), g_t in tr.groupby(["econ", "target", "freq"]):
        horizons = cfg.horizons[freq]
        for h in horizons:
            gh = g_t[g_t["horizon"] == h]
            for mode in sorted(gh["input_mode"].unique()):
                gm = gh[gh["input_mode"] == mode]
                for outturn in ("first_release", "revised_12m"):
                    for sample in ("full", "ex_covid"):
                        for window in ("primary", "all"):
                            sel = gm.copy()
                            if sample == "ex_covid":
                                sel = sel[sel["ex_covid"]]
                            if window == "primary":
                                sel = sel[sel["primary"]]
                            sel = sel.dropna(subset=[outturn])
                            if sel.empty:
                                continue
                            # AR reference (same cell)
                            ar = sel[
                                (sel["model"] == "ar") & (sel["variant"] == "univariate")
                            ].set_index("origin")
                            cell_losses: dict[str, pd.Series] = {}
                            for (model, variant), gmv in sel.groupby(["model", "variant"]):
                                gmv = gmv.drop_duplicates("origin").set_index("origin").sort_index()
                                y = gmv[outturn].to_numpy(dtype=float)
                                med = gmv["q0.5"].to_numpy(dtype=float)
                                Q = gmv[qs].to_numpy(dtype=float)
                                e = y - med
                                base = {
                                    "econ": econ,
                                    "target": target,
                                    "freq": freq,
                                    "horizon": h,
                                    "model": model,
                                    "variant": variant,
                                    "input_mode": mode,
                                    "outturn": outturn,
                                    "sample": sample,
                                    "window": window,
                                }
                                splits = [("all", np.ones(len(gmv), dtype=bool))]
                                if model in fms:
                                    wd = fms[model].weights_date
                                    origins = gmv.index.to_numpy()
                                    splits += [("pre", origins < wd), ("post", origins >= wd)]
                                    tc = fms[model].training_cutoff
                                    if tc:
                                        tcd = f"{tc}-01"
                                        splits += [
                                            ("pre_cutoff", origins < tcd),
                                            ("post_cutoff", origins >= tcd),
                                        ]
                                for split, mask in splits:
                                    if mask.sum() == 0:
                                        continue
                                    ys, es, Qs = y[mask], e[mask], Q[mask]
                                    r = dict(base, split=split, n=int(mask.sum()))
                                    r["rmsfe"] = float(np.sqrt(np.mean(es**2)))
                                    r["mae"] = float(np.mean(np.abs(es)))
                                    r["bias"] = float(np.mean(es))
                                    r["wql"] = float(pinball(ys, Qs, levels).mean())
                                    r["coverage80"] = float(
                                        np.mean(
                                            (ys >= Qs[:, list(qs).index(lo_q)])
                                            & (ys <= Qs[:, list(qs).index(hi_q)])
                                        )
                                    )
                                    # relative to AR on the same origins
                                    common = gmv.index[mask].intersection(ar.index)
                                    if len(common) >= 1 and model != "ar":
                                        ea = (
                                            ar.loc[common, outturn] - ar.loc[common, "q0.5"]
                                        ).to_numpy(dtype=float)
                                        em = (
                                            gmv.loc[common, outturn] - gmv.loc[common, "q0.5"]
                                        ).to_numpy(dtype=float)
                                        r["n_vs_ar"] = int(len(common))
                                        r["rel_rmsfe"] = (
                                            float(np.sqrt(np.mean(em**2)) / np.sqrt(np.mean(ea**2)))
                                            if np.mean(ea**2) > 0
                                            else np.nan
                                        )
                                        r["rel_mae"] = (
                                            float(np.mean(np.abs(em)) / np.mean(np.abs(ea)))
                                            if np.mean(np.abs(ea)) > 0
                                            else np.nan
                                        )
                                        r["dm_stat"], r["dm_p"] = dm_hln(em**2 - ea**2, h)
                                    rows.append(r)
                                    if split == "all":
                                        pit_rows.append(
                                            dict(
                                                base,
                                                n=int(len(ys)),
                                                **{
                                                    f"bin{i}": float(v)
                                                    for i, v in enumerate(pit_bins(ys, Qs))
                                                },
                                            )
                                        )
                                if len(gmv) >= 8:
                                    cell_losses[f"{model}|{variant}"] = pd.Series(
                                        e**2, index=gmv.index
                                    )
                            # model confidence set over models with complete common origins
                            if len(cell_losses) >= 2:
                                L = pd.DataFrame(cell_losses).dropna()
                                if len(L) >= 8:
                                    pv = mcs(L, alpha=0.10, block=max(2, h))
                                    for k, p in pv.items():
                                        model, variant = k.split("|")
                                        mcs_rows.append(
                                            {
                                                "econ": econ,
                                                "target": target,
                                                "freq": freq,
                                                "horizon": h,
                                                "input_mode": mode,
                                                "outturn": outturn,
                                                "sample": sample,
                                                "window": window,
                                                "model": model,
                                                "variant": variant,
                                                "n": int(len(L)),
                                                "mcs_p": p,
                                                "in_mcs90": bool(p >= 0.10),
                                            }
                                        )
    tables = {
        "scores": pd.DataFrame(rows),
        "pit": pd.DataFrame(pit_rows),
        "mcs": pd.DataFrame(mcs_rows),
    }
    if not cum.empty:
        crow = []
        cum["ex_covid"] = ~_in_window(cum["target_period"], covid)
        cum["primary"] = cum["origin"] >= primary_first
        for (econ, target, freq, h, model, variant, mode), g in cum.groupby(
            ["econ", "target", "freq", "step", "model", "variant", "input_mode"]
        ):
            if h not in cfg.horizons[freq]:
                continue
            for outturn in ("first_release", "revised_12m"):
                for sample in ("full", "ex_covid"):
                    for window in ("primary", "all"):
                        sel = g.copy()
                        if sample == "ex_covid":
                            sel = sel[sel["ex_covid"]]
                        if window == "primary":
                            sel = sel[sel["primary"]]
                        sel = sel.dropna(subset=[outturn])
                        if sel.empty:
                            continue
                        y = sel[outturn].to_numpy(dtype=float)
                        Q = sel[qs].to_numpy(dtype=float)
                        e = y - sel["q0.5"].to_numpy(dtype=float)
                        crow.append(
                            {
                                "econ": econ,
                                "target": target,
                                "freq": freq,
                                "horizon": h,
                                "model": model,
                                "variant": variant,
                                "input_mode": mode,
                                "outturn": outturn,
                                "sample": sample,
                                "window": window,
                                "n": len(y),
                                "rmsfe": float(np.sqrt(np.mean(e**2))),
                                "mae": float(np.mean(np.abs(e))),
                                "bias": float(np.mean(e)),
                                "wql": float(pinball(y, Q, levels).mean()),
                                "coverage80": float(
                                    np.mean(
                                        (y >= Q[:, list(qs).index(lo_q)])
                                        & (y <= Q[:, list(qs).index(hi_q)])
                                    )
                                ),
                            }
                        )
        tables["cumulative_levels"] = pd.DataFrame(crow)
    return tables


def write_tables(tables: dict[str, pd.DataFrame], root: Path = BACKTEST_ROOT) -> Path:
    d = root / TABLES
    d.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_csv(d / f"{name}.csv", index=False)
    lines = [
        f"# Backtest tables ({dt.date.today().isoformat()})",
        "",
        "Private: forecast-derived. Not for the public repo until Gate 4.",
        "",
    ]
    for name, df in tables.items():
        lines.append(
            f"- `{name}.csv`: {len(df)} rows"
            + (f", columns {list(df.columns)[:12]}" if len(df) else "")
        )
    (d / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d
