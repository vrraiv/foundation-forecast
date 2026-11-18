"""Phase 3 smoke test: every model and benchmark produces forecasts for one origin for every
target, with mechanical magnitude checks and recorded runtimes. Never compares with outturns.

Sane-magnitude rule (fixed in advance): every quantile of the h-step forecast in transformed
space must lie within [min - 3*sd, max + 3*sd] of the target's own transformed history at the
origin, and quantiles must be non-decreasing."""

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
from .runner import make_task, model_settings, run_worker, to_forecasts


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


def sane(fc: QuantileForecast, hist: pd.Series) -> tuple[bool, str]:
    v = fc.values
    if not np.isfinite(v).all():
        return False, "non-finite values"
    if (np.diff(v, axis=1) < -1e-9).any():
        return False, "quantile crossing"
    lo = hist.min() - 3 * hist.std()
    hi = hist.max() + 3 * hist.std()
    if (v < lo).any() or (v > hi).any():
        return False, f"outside [{lo:.3g}, {hi:.3g}]"
    return True, ""


def run_benchmarks(
    cfg: Config, panel: Panel, horizon: int, qs
) -> dict[str, tuple[QuantileForecast, float]]:
    out = {}
    bcfg = cfg.models["benchmarks"]
    t0 = time.perf_counter()
    out["naive"] = (Naive().forecast(panel.univariate(), horizon, qs), time.perf_counter() - t0)
    t0 = time.perf_counter()
    out["ar"] = (
        ARDirect(bcfg["ar"]["max_lag"][panel.freq]).forecast(panel.univariate(), horizon, qs),
        time.perf_counter() - t0,
    )
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
            fc = dfm.forecast(
                panel.monthly,
                horizon,
                qs,
                quarterly=panel.quarterly if not panel.quarterly.empty else None,
            )
        else:
            fc = dfm.forecast(
                panel.monthly, horizon, qs, quarterly=panel.quarterly, target_is_quarterly=True
            )
        out["dfm"] = (fc, time.perf_counter() - t0)
    except Exception as e:  # noqa: BLE001
        out["dfm"] = (None, time.perf_counter() - t0)
        out["dfm_error"] = str(e)[:300]
    return out


def run_smoke(
    origin: dt.date,
    cfg: Config | None = None,
    models: list[str] | None = None,
    out_path: Path | None = None,
    run_bench: bool = True,
) -> pd.DataFrame:
    cfg = cfg or load_config()
    table = read_all()
    qs = tuple(cfg.scoring["quantiles"])
    rows: list[SmokeRow] = []
    panels: dict[tuple[str, str], Panel] = {}
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
                fcs[name] = fc
                rows.append(
                    SmokeRow(
                        econ,
                        tname,
                        name,
                        "uni" if name in ("naive", "ar") else "multi",
                        horizon,
                        ok,
                        note,
                        round(rt, 3),
                        float(fc.median()[0]),
                    )
                )
            combo = EqualWeight(
                "combo_bench", cfg.models["benchmarks"]["combo_bench"]["of"]
            ).combine(fcs)
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
                    )
                )
    # foundation models: one worker call per model with all tasks
    fms = cfg.foundation_models()
    for mname, fm in fms.items():
        if models and mname not in models:
            continue
        tasks, meta = [], {}
        for (econ, tname), p in panels.items():
            horizon = max(cfg.horizons[p.freq])
            for variant in fm.variants:
                hist = (
                    p.univariate()
                    if variant == "univariate"
                    else p.multivariate(cfg.models["benchmarks"]["bvar"]["max_vars"])
                    .ffill()
                    .dropna()
                )
                if variant == "multivariate" and hist.shape[1] < 2:
                    continue
                tid = f"{econ}.{tname}.{variant}"
                tasks.append(make_task(tid, hist, p.freq, horizon, qs))
                meta[tid] = (econ, tname, variant, horizon, p)
        if not tasks:
            continue
        try:
            resp = run_worker(fm, model_settings(cfg, mname), tasks)
        except Exception as e:  # noqa: BLE001
            rows.append(
                SmokeRow(
                    "-", "-", mname, "-", 0, False, f"worker failed: {str(e)[-200:]}", 0.0, None
                )
            )
            continue
        fcs = to_forecasts(resp, tasks)
        for tid, (econ, tname, variant, horizon, p) in meta.items():
            if tid in fcs:
                ok, note = sane(fcs[tid], p.target_tr)
                rows.append(
                    SmokeRow(
                        econ,
                        tname,
                        mname,
                        variant[:5],
                        horizon,
                        ok,
                        note,
                        fcs[tid].meta["runtime_s"],
                        float(fcs[tid].median()[0]),
                    )
                )
            else:
                rows.append(
                    SmokeRow(
                        econ,
                        tname,
                        mname,
                        variant[:5],
                        horizon,
                        False,
                        resp["errors"].get(tid, "missing")[:200],
                        0.0,
                        None,
                    )
                )
        rows.append(
            SmokeRow(
                "-",
                "-",
                mname,
                "wall",
                0,
                True,
                f"worker wall time incl. load; weights {resp['weights_digest'][:12]}",
                resp["wall_s"],
                None,
            )
        )
    df = pd.DataFrame([asdict(r) for r in rows])
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        (out_path.with_suffix(".json")).write_text(
            json.dumps({"origin": origin.isoformat(), "rows": df.to_dict("records")}, indent=1),
            encoding="utf-8",
        )
    return df
