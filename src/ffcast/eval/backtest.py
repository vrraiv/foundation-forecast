"""Backtest harness (Phase 4): origins x targets x input modes x models, three stages.

  stage 1 (heavy, parallel over origins): build panels through `as_of` only, run the classical
          benchmarks, write `forecasts/bench/<origin>.parquet` + `meta/bench/<origin>.parquet`,
          and write foundation-model request files (one per model per chunk of origins);
  stage 2 (lean process, ffcast.models.lean): run the workers;
  stage 3 (heavy): parse responses into `forecasts/fm/<origin>.parquet` + `meta/fm/...`,
          then build `outturns.parquet`, `cumulative_outturns.parquet` and `run_manifest.json`.

Every row carries a cache key (config slice + data-manifest hashes of the series used + weights
digest). An origin/model whose stored key matches is skipped; `verify` recomputes a sample and
compares values exactly.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from ..bench import ARDirect, BVARMinnesota, DynamicFactorMQBench, EqualWeight, Naive
from ..config import Config, load_config
from ..data.store import NORMALISED_ROOT, read_all
from ..models.interface import QuantileForecast
from ..models.panel import Panel, build_panel
from ..models.runner import make_task, model_settings
from ..models.weights import ensure_weights, weights_digest
from ..origins import origins_between
from .outturns import OUTTURN_COLUMNS, OutturnBuilder
from .store import (
    BACKTEST_ROOT,
    FORECAST_COLUMNS,
    META_COLUMNS,
    forecast_rows,
    read_forecasts,
    read_meta,
    stable_hash,
    write_atomic,
)

REPO = Path(__file__).resolve().parents[3]

# Bumped when the benchmark code changes in a way that alters results, so that stored benchmark
# cells are recomputed while foundation-model keys stay untouched. History:
#   1: first full run, 2026-11-18 07:52.
#   2: numerical-validity guard; DFM estimated with `em_initialization` from config (the
#      statsmodels default initialisation broke down at 52 of 5,200 cells: log-likelihood about
#      -1e54, forecasts up to 1e97; found by the benchmark-only scoring pass of 2026-11-18).
BENCH_CODE_VERSION = 2

DEFAULT_VALIDITY = {"max_abs_sd_multiple": 50.0, "min_llf": -1.0e10}


def validity_rule(cfg: Config) -> dict:
    return {**DEFAULT_VALIDITY, **cfg.backtest.get("validity", {})}


def invalid_reason(
    values, mean, history_sd: float, llf: float | None = None, rule: dict | None = None
) -> str | None:
    """Why a forecast is a numerical failure, or None. A failure is a non-finite value, a
    log-likelihood below `min_llf` (estimation broke down) or a quantile or mean whose absolute
    size exceeds `max_abs_sd_multiple` standard deviations of the model's own input history (in
    the space the model forecast in). Failures are stored as status `error`, never as values."""
    rule = {**DEFAULT_VALIDITY, **(rule or {})}
    v = np.asarray(values, dtype=float)
    parts = [v] if mean is None else [v, np.asarray(mean, dtype=float)]
    if any(not np.isfinite(x).all() for x in parts):
        return "non-finite forecast values"
    if llf is not None and (not np.isfinite(llf) or llf < rule["min_llf"]):
        return f"log-likelihood {llf:.3g} below {rule['min_llf']:.3g}"
    scale = max(float(history_sd) if np.isfinite(history_sd) else 0.0, 1e-12)
    big = max(float(np.abs(x).max()) for x in parts)
    if big > rule["max_abs_sd_multiple"] * scale:
        return (
            f"|forecast| {big:.3g} exceeds {rule['max_abs_sd_multiple']:g} x history sd {scale:.3g}"
        )
    return None


# ------------------------------------------------------------------ keys and manifest


def data_manifest(root: Path = NORMALISED_ROOT) -> dict:
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    return m.get("series", m)


def revised_as_of_date(table: pd.DataFrame) -> dt.date:
    """Pinned snapshot date for the revised input mode: the day after the newest vintage in
    the normalised data (so `as_of(..., strict=False)` sees everything downloaded)."""
    return max(pd.to_datetime(table["vintage_date"]).dt.date) + dt.timedelta(days=1)


def _series_for(cfg: Config, econ: str, target: str) -> list[str]:
    from ..data.targets import series_id_for
    from ..models.panel import _cond_sid

    t = cfg.targets[econ][target]
    sids = []
    if t.vintages:
        sids.append(series_id_for(t.vintages, econ, t.freq, target))
        if t.vintages.get("fallback"):
            sids.append(series_id_for(t.vintages["fallback"], econ, t.freq, target))
    sids += [_cond_sid(s, econ) for s in cfg.conditioning.get(econ, [])]
    return sids


def _data_hashes(manifest: dict, sids: list[str]) -> list[tuple[str, str]]:
    out = []
    for sid in sids:
        entry = manifest.get(sid)
        out.append((sid, entry["sha256"] if isinstance(entry, dict) else str(entry)))
    return out


def cache_key(
    cfg: Config,
    manifest: dict,
    econ: str,
    target: str,
    model: str,
    *,
    weights: str | None = None,
) -> str:
    """Config slice + data hashes + weights digest that determine one (target, model) result."""
    fm = cfg.models["foundation"].get(model)
    slice_ = {
        # `latest` names the live-data source, which the backtest never reads (vintages and
        # pseudo-vintage bases live under `vintages`), so switching it leaves keys unchanged
        "target": {
            k: v for k, v in cfg.targets[econ][target].model_dump().items() if k != "latest"
        },
        "conditioning": cfg.conditioning.get(econ, []),
        "horizons": cfg.horizons,
        "origins": cfg.origins.model_dump(),
        "vintage_sources": cfg.vintage_sources,
        "backtest": {
            k: v
            for k, v in cfg.backtest.items()
            # execution details and the validity guard (applied when rows are stored; it turns
            # values into `error` rows and never changes a value) are not part of the key
            if k
            not in (
                "parallel_benchmark_processes",
                "origins_per_worker_request",
                "cache",
                "validity",
            )
        },
        "quantiles": cfg.scoring["quantiles"],
        "model": model,
        "model_cfg": fm if fm else cfg.models["benchmarks"].get(model),
        "settings": model_settings(cfg, model) if fm else cfg.models["benchmarks"],
        "weights": weights,
        "data": _data_hashes(manifest, _series_for(cfg, econ, target)),
    }
    if not fm:
        slice_["bench_code"] = BENCH_CODE_VERSION
    return stable_hash(slice_)[:16]


# ------------------------------------------------------------------ benchmarks at one origin

BENCH_UNI = ("naive", "ar")


def run_benchmarks(
    cfg: Config, panel: Panel, horizon: int, qs
) -> tuple[dict[str, QuantileForecast], dict[str, float], dict[str, str]]:
    out: dict[str, QuantileForecast] = {}
    rt: dict[str, float] = {}
    err: dict[str, str] = {}
    b = cfg.models["benchmarks"]
    t0 = time.perf_counter()
    out["naive"] = Naive().forecast(panel.univariate(), horizon, qs)
    rt["naive"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    out["ar"] = ARDirect(b["ar"]["max_lag"][panel.freq]).forecast(panel.univariate(), horizon, qs)
    rt["ar"] = time.perf_counter() - t0
    bv = b["bvar"]
    t0 = time.perf_counter()
    mv = panel.multivariate(bv["max_vars"])
    if mv.shape[1] >= 2:
        try:
            out["bvar"] = BVARMinnesota(
                bv["lags"][panel.freq],
                bv["lambda_grid"],
                bv["soc_grid"],
                bv["dio_grid"],
                bv["decay"],
                bv["draws"],
                0,
                bv["max_vars"],
                bv.get("min_balanced", {}).get(panel.freq, 72),
            ).forecast(mv, horizon, qs)
        except Exception as e:  # noqa: BLE001
            err["bvar"] = str(e)[:300]
    else:
        err["bvar"] = "fewer than two variables"
    rt["bvar"] = time.perf_counter() - t0
    d = b["dfm"]
    t0 = time.perf_counter()
    try:
        dfm = DynamicFactorMQBench(
            d["factors"],
            d["factor_order"],
            d["idiosyncratic_ar1"],
            d["max_vars"],
            d.get("maxiter", 100),
            em_initialization=d.get("em_initialization", True),
        )
        if panel.freq == "M":
            q = panel.quarterly if not panel.quarterly.empty else None
            out["dfm"] = dfm.forecast(panel.monthly, horizon, qs, quarterly=q)
        else:
            out["dfm"] = dfm.forecast(
                panel.monthly, horizon, qs, quarterly=panel.quarterly, target_is_quarterly=True
            )
    except Exception as e:  # noqa: BLE001
        err["dfm"] = str(e)[:300]
    rt["dfm"] = time.perf_counter() - t0
    # numerical-validity guard, before the combination so a failed member cannot contaminate it
    rule = validity_rule(cfg)
    hist_sd = float(panel.target_tr.astype(float).std())
    for m in list(out):
        bad = invalid_reason(out[m].values, out[m].mean, hist_sd, out[m].meta.get("loglike"), rule)
        if bad:
            err[m] = f"numerical failure: {bad}"
            del out[m]
    members = b["combo_bench"]["of"]
    if all(m in out for m in members) or not cfg.backtest.get("combos_require_all_members", True):
        combo = EqualWeight("combo_bench", members).combine(out)
        if combo is not None:
            out["combo_bench"] = combo
            rt["combo_bench"] = 0.0
    else:
        err["combo_bench"] = "missing member: " + ",".join(m for m in members if m not in out)
    return out, rt, err


def _norm_period(p) -> str | None:
    if p is None:
        return None
    s = str(p)
    return s if "-Q" in s or len(s) == 7 else s.replace("Q", "-Q")


# ------------------------------------------------------------------ stage 1

_G: dict = {}


def _init_worker(threads: int, config_path: str | None) -> None:
    for var in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        os.environ[var] = str(threads)
    _G["cfg"] = load_config(config_path) if config_path else load_config()
    _G["table"] = read_all()
    _G["manifest"] = data_manifest()
    _G["revised_as_of"] = revised_as_of_date(_G["table"])


def _meta_row(
    origin,
    econ,
    target,
    freq,
    model,
    variant,
    mode,
    status,
    note,
    panel: Panel | None,
    cache,
    n_vars=None,
    runtime=None,
) -> dict:
    return {
        "origin": origin.isoformat(),
        "econ": econ,
        "target": target,
        "freq": freq,
        "model": model,
        "variant": variant,
        "input_mode": mode,
        "status": status,
        "note": note,
        "series_id": panel.target_sid if panel else None,
        "source_role": panel.source_role if panel else None,
        "last_period": str(panel.target_tr.index[-1]) if panel else None,
        "last_level": float(panel.target_levels.iloc[-1]) if panel else None,
        "n_history": int(len(panel.target_tr)) if panel else None,
        "n_vars": n_vars,
        "runtime_s": runtime,
        "cache_key": cache,
    }


def panels_at_origin(
    cfg: Config, table: pd.DataFrame, origin: dt.date, modes: list[str], revised_as_of: dt.date
) -> tuple[dict[tuple[str, str, str], Panel], list[dict]]:
    """Panels per (econ, target, input_mode) plus meta rows for skipped targets."""
    panels: dict[tuple[str, str, str], Panel] = {}
    skipped: list[dict] = []
    minp = cfg.backtest["min_history_periods"]
    for econ in cfg.economies:
        for tname, t in cfg.targets[econ].items():
            for mode in modes:
                if t.blocked:
                    skipped.append(
                        _meta_row(
                            origin,
                            econ,
                            tname,
                            t.freq,
                            "-",
                            "-",
                            mode,
                            "skipped",
                            f"blocked: {t.blocked[:120]}",
                            None,
                            None,
                        )
                    )
                    continue
                if mode == "revised" and t.exclude_from_q1:
                    skipped.append(
                        _meta_row(
                            origin,
                            econ,
                            tname,
                            t.freq,
                            "-",
                            "-",
                            mode,
                            "skipped",
                            "exclude_from_q1: pseudo-vintage target has no revised mode",
                            None,
                            None,
                        )
                    )
                    continue
                p = build_panel(cfg, table, econ, tname, origin, mode, revised_as_of)
                if p is None:
                    skipped.append(
                        _meta_row(
                            origin,
                            econ,
                            tname,
                            t.freq,
                            "-",
                            "-",
                            mode,
                            "skipped",
                            "no resolvable vintage at origin",
                            None,
                            None,
                        )
                    )
                    continue
                if len(p.target_tr) < minp[t.freq]:
                    skipped.append(
                        _meta_row(
                            origin,
                            econ,
                            tname,
                            t.freq,
                            "-",
                            "-",
                            mode,
                            "skipped",
                            f"in-vintage history {len(p.target_tr)} < {minp[t.freq]}",
                            p,
                            None,
                        )
                    )
                    continue
                panels[(econ, tname, mode)] = p
    return panels, skipped


def stage1_origin(
    origin: dt.date, modes: list[str], run_bench: bool, fm_models: list[str], out_root: str
) -> dict:
    """Runs inside a worker process. Returns {'origin', 'tasks': {model: [task dicts]}, 'task_meta': {...}}."""
    cfg: Config = _G["cfg"]
    table: pd.DataFrame = _G["table"]
    manifest = _G["manifest"]
    root = Path(out_root)
    qs = tuple(cfg.scoring["quantiles"])
    max_vars = cfg.models["benchmarks"]["bvar"]["max_vars"]
    panels, meta = panels_at_origin(cfg, table, origin, modes, _G["revised_as_of"])
    frows: list[dict] = []
    bench_models = ["naive", "ar", "bvar", "dfm", "combo_bench"]
    if run_bench:
        for (econ, tname, mode), p in panels.items():
            horizon = max(cfg.horizons[p.freq])
            periods = p.target_periods(horizon)
            keys = {m: cache_key(cfg, manifest, econ, tname, m) for m in bench_models}
            fcs, rts, errs = run_benchmarks(cfg, p, horizon, qs)
            for m in bench_models:
                variant = "univariate" if m in BENCH_UNI else "multivariate"
                if m in fcs:
                    fc = fcs[m]
                    s1 = _norm_period(fc.meta.get("step1_period"))
                    if s1 is not None and s1 != periods[0]:
                        meta.append(
                            _meta_row(
                                origin,
                                econ,
                                tname,
                                p.freq,
                                m,
                                variant,
                                mode,
                                "error",
                                f"step 1 refers to {s1}, expected {periods[0]}",
                                p,
                                keys[m],
                            )
                        )
                        continue
                    fc = fc.sorted() if (np.diff(fc.values, axis=1) < 0).any() else fc
                    nv = (
                        len(fc.meta.get("vars", []))
                        or fc.meta.get("n_monthly")
                        or (1 if variant == "univariate" else None)
                    )
                    frows += forecast_rows(
                        origin=origin,
                        econ=econ,
                        target=tname,
                        freq=p.freq,
                        model=m,
                        variant=variant,
                        input_mode=mode,
                        space="transformed",
                        target_periods=periods,
                        quantiles=qs,
                        values=fc.values,
                        mean=fc.mean,
                        series_id=p.target_sid,
                        source_role=p.source_role,
                        cache_key=keys[m],
                    )
                    meta.append(
                        _meta_row(
                            origin,
                            econ,
                            tname,
                            p.freq,
                            m,
                            variant,
                            mode,
                            "ok",
                            "",
                            p,
                            keys[m],
                            nv,
                            round(rts.get(m, 0.0), 3),
                        )
                    )
                else:
                    meta.append(
                        _meta_row(
                            origin,
                            econ,
                            tname,
                            p.freq,
                            m,
                            variant,
                            mode,
                            "error",
                            errs.get(m, "no forecast"),
                            p,
                            keys[m],
                            None,
                            round(rts.get(m, 0.0), 3),
                        )
                    )
        write_atomic(
            pd.DataFrame(frows, columns=FORECAST_COLUMNS),
            root / "forecasts" / "bench" / f"{origin.isoformat()}.parquet",
        )
        write_atomic(
            pd.DataFrame(meta, columns=META_COLUMNS),
            root / "meta" / "bench" / f"{origin.isoformat()}.parquet",
        )
    # foundation-model tasks
    tasks: dict[str, list[dict]] = {}
    task_meta: dict[str, dict] = {}
    spaces = ["transformed"] + (["level"] if "levels" in cfg.backtest.get("variants", []) else [])
    for mname in fm_models:
        fm = cfg.foundation_models()[mname]
        for (econ, tname, mode), p in panels.items():
            horizon = max(cfg.horizons[p.freq])
            for variant in fm.variants:
                for space in spaces:
                    if variant == "univariate":
                        hist = p.univariate(space)
                        nv = 1
                    else:
                        hist = p.multivariate(max_vars, balanced=True, space=space)
                        nv = hist.shape[1]
                        if nv < 2:
                            continue
                    tid = f"{origin.isoformat()}|{econ}|{tname}|{variant}|{mode}|{space}"
                    tasks.setdefault(mname, []).append(
                        make_task(tid, hist, p.freq, horizon, qs).__dict__ | {"quantiles": list(qs)}
                    )
                    task_meta[f"{mname}:{tid}"] = {
                        "tid": tid,
                        "origin": origin.isoformat(),
                        "econ": econ,
                        "target": tname,
                        "freq": p.freq,
                        "model": mname,
                        "variant": variant,
                        "input_mode": mode,
                        "space": space,
                        "horizon": horizon,
                        "periods": p.target_periods(horizon),
                        "n_vars": nv,
                        "series_id": p.target_sid,
                        "source_role": p.source_role,
                        "last_period": str(p.target_tr.index[-1]),
                        "last_level": float(p.target_levels.iloc[-1]),
                        "n_history": int(len(p.target_tr)),
                    }
    skipped_fm = [m for m in meta if m["status"] == "skipped"]
    return {
        "origin": origin.isoformat(),
        "tasks": tasks,
        "task_meta": task_meta,
        "skipped": skipped_fm,
    }


def _bench_done(root: Path, cfg: Config, manifest: dict, origin: dt.date) -> bool:
    p = root / "meta" / "bench" / f"{origin.isoformat()}.parquet"
    if not p.exists():
        return False
    m = pd.read_parquet(p)
    m = m[m["status"] != "skipped"]
    if m.empty:
        return True
    for (econ, tname, model), g in m.groupby(["econ", "target", "model"]):
        if set(g["cache_key"]) != {cache_key(cfg, manifest, econ, tname, model)}:
            return False
    return True


def _fm_done(
    root: Path, cfg: Config, manifest: dict, origin: dt.date, model: str, wkey: str
) -> bool:
    p = root / "meta" / "fm" / f"{origin.isoformat()}.parquet"
    if not p.exists():
        return False
    m = pd.read_parquet(p)
    m = m[(m["model"] == model) & (m["status"] != "skipped")]
    if m.empty:
        return False
    for (econ, tname), g in m.groupby(["econ", "target"]):
        if set(g["cache_key"]) != {cache_key(cfg, manifest, econ, tname, model, weights=wkey)}:
            return False
    return True


def stage1(
    origins: list[dt.date],
    workdir: Path,
    *,
    cfg: Config | None = None,
    modes: list[str] | None = None,
    run_bench: bool = True,
    models: list[str] | None = None,
    processes: int | None = None,
    force: bool = False,
    root: Path = BACKTEST_ROOT,
) -> dict:
    cfg = cfg or load_config()
    modes = modes or list(cfg.backtest["input_modes"])
    manifest = data_manifest()
    fms = cfg.foundation_models()
    models = [m for m in (list(fms) if models is None else models) if m in fms]
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "requests").mkdir(exist_ok=True)
    weights: dict[str, tuple[Path, str]] = {}
    for m in models:
        settings = model_settings(cfg, m)
        wdir, man = ensure_weights(fms[m], allow_download=settings.get("allow_download", True))
        weights[m] = (wdir, weights_digest(man))
    # what is left to do
    todo_bench = [
        o for o in origins if run_bench and (force or not _bench_done(root, cfg, manifest, o))
    ]
    todo_fm = {
        m: [o for o in origins if force or not _fm_done(root, cfg, manifest, o, m, weights[m][1])]
        for m in models
    }
    todo_origins = sorted(set(todo_bench) | {o for v in todo_fm.values() for o in v})
    report = {
        "origins": len(origins),
        "bench_todo": len(todo_bench),
        "fm_todo": {m: len(v) for m, v in todo_fm.items()},
    }
    if not todo_origins:
        return report
    nproc = processes or int(cfg.backtest.get("parallel_benchmark_processes", 4))
    threads = int(cfg.backtest.get("threads_per_process", 4))
    results = []
    t0 = time.perf_counter()
    with ProcessPoolExecutor(
        max_workers=nproc, initializer=_init_worker, initargs=(threads, None)
    ) as ex:
        futs = {
            ex.submit(
                stage1_origin,
                o,
                modes,
                o in todo_bench,
                [m for m in models if o in todo_fm[m]],
                str(root),
            ): o
            for o in todo_origins
        }
        for f in futs:
            results.append(f.result())
    report["stage1_s"] = round(time.perf_counter() - t0, 1)
    # request files: one per model per chunk of origins
    chunk = int(cfg.backtest.get("origins_per_worker_request", 12))
    task_meta: dict[str, dict] = {}
    for r in results:
        task_meta.update(r["task_meta"])
    skipped = [s for r in results for s in r["skipped"]]
    n_req = 0
    for m in models:
        per_origin = [(r["origin"], r["tasks"].get(m, [])) for r in results if r["tasks"].get(m)]
        for i in range(0, len(per_origin), chunk):
            part = per_origin[i : i + chunk]
            tasks = [t for _, ts in part for t in ts]
            wdir, digest = weights[m]
            settings = model_settings(cfg, m)
            sizes = (
                [
                    (wdir / f).stat().st_size
                    for f in json.loads((wdir / "MANIFEST.sha256.json").read_text())["files"]
                    if (wdir / f).exists()
                ]
                if (wdir / "MANIFEST.sha256.json").exists()
                else []
            )
            largest_mb = max(sizes, default=0) // (1 << 20)
            settings = {
                **settings,
                "min_free_commit_mb": settings.get("min_free_commit_mb", 2 * largest_mb + 600),
            }
            req = {
                "model": fms[m].hf_id,
                "env": fms[m].env,
                "weights_dir": str(wdir),
                "weights_digest": digest,
                "settings": settings,
                "tasks": tasks,
                "origins": [o for o, _ in part],
            }
            name = f"{m}__{part[0][0]}__{part[-1][0]}.json"
            (workdir / "requests" / name).write_text(json.dumps(req), encoding="utf-8")
            n_req += 1
    (workdir / "task_meta.json").write_text(json.dumps(task_meta), encoding="utf-8")
    (workdir / "skipped.json").write_text(json.dumps(skipped), encoding="utf-8")
    (workdir / "weights.json").write_text(
        json.dumps({m: d for m, (_, d) in weights.items()}), encoding="utf-8"
    )
    report["requests"] = n_req
    report["fm_tasks"] = len(task_meta)
    return report


# ------------------------------------------------------------------ stage 3


def stage3(workdir: Path, *, cfg: Config | None = None, root: Path = BACKTEST_ROOT) -> dict:
    cfg = cfg or load_config()
    manifest = data_manifest()
    qs = tuple(cfg.scoring["quantiles"])
    rule = validity_rule(cfg)
    meta_path = workdir / "task_meta.json"
    task_meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    weights = (
        json.loads((workdir / "weights.json").read_text(encoding="utf-8"))
        if (workdir / "weights.json").exists()
        else {}
    )
    skipped = (
        json.loads((workdir / "skipped.json").read_text(encoding="utf-8"))
        if (workdir / "skipped.json").exists()
        else []
    )
    status_file = workdir / "responses" / "_status.json"
    status = json.loads(status_file.read_text(encoding="utf-8")) if status_file.exists() else {}
    by_origin_rows: dict[str, list[dict]] = {}
    by_origin_meta: dict[str, list[dict]] = {}
    for s in skipped:
        by_origin_meta.setdefault(s["origin"], []).append(s)
    n_ok = n_err = 0
    for rp in sorted((workdir / "requests").glob("*.json")):
        req = json.loads(rp.read_text(encoding="utf-8"))
        model = rp.name.split("__")[0]
        resp_path = workdir / "responses" / rp.name
        resp = json.loads(resp_path.read_text(encoding="utf-8")) if resp_path.exists() else None
        for t in req["tasks"]:
            tm = task_meta[f"{model}:{t['id']}"]
            key = cache_key(
                cfg, manifest, tm["econ"], tm["target"], model, weights=weights.get(model)
            )
            base = dict(
                origin=dt.date.fromisoformat(tm["origin"]),
                econ=tm["econ"],
                target=tm["target"],
                freq=tm["freq"],
                model=model,
                variant=tm["variant"],
                input_mode=tm["input_mode"],
            )
            mrow = {
                "origin": tm["origin"],
                "econ": tm["econ"],
                "target": tm["target"],
                "freq": tm["freq"],
                "model": model,
                "variant": tm["variant"] + ("" if tm["space"] == "transformed" else "_levels"),
                "input_mode": tm["input_mode"],
                "status": "ok",
                "note": "",
                "series_id": tm["series_id"],
                "source_role": tm["source_role"],
                "last_period": tm["last_period"],
                "last_level": tm["last_level"],
                "n_history": tm["n_history"],
                "n_vars": tm["n_vars"],
                "runtime_s": None,
                "cache_key": key,
            }
            r = resp["results"].get(t["id"]) if resp else None
            if r is None:
                mrow["status"] = "error"
                mrow["note"] = (
                    resp["errors"].get(t["id"], "missing")
                    if resp
                    else "worker failed: " + status.get(rp.stem, "no response")[-200:]
                )[:300]
                n_err += 1
            else:
                q = np.asarray(r["quantiles"], dtype=float)
                if (np.diff(q, axis=1) < 0).any():
                    q = np.sort(q, axis=1)
                mean = r.get("mean")
                hist0 = np.asarray(t["history"][0], dtype=float)
                hist0 = hist0[np.isfinite(hist0)]
                bad = invalid_reason(
                    q, mean, float(hist0.std()) if len(hist0) > 1 else 0.0, None, rule
                )
                if bad:
                    mrow["status"] = "error"
                    mrow["note"] = f"numerical failure: {bad}"[:300]
                    n_err += 1
                    by_origin_meta.setdefault(tm["origin"], []).append(mrow)
                    continue
                by_origin_rows.setdefault(tm["origin"], []).extend(
                    forecast_rows(
                        **base,
                        space=tm["space"],
                        target_periods=tm["periods"],
                        quantiles=qs,
                        values=q,
                        mean=None if mean is None else np.asarray(mean, dtype=float),
                        series_id=tm["series_id"],
                        source_role=tm["source_role"],
                        cache_key=key,
                    )
                )
                mrow["runtime_s"] = r.get("runtime_s")
                n_ok += 1
            # variant label for FM rows: the forecast rows keep variant + space separately
            by_origin_meta.setdefault(tm["origin"], []).append(mrow)
    models_run = {rp.name.split("__")[0] for rp in (workdir / "requests").glob("*.json")}
    for origin in sorted(set(by_origin_rows) | set(by_origin_meta)):
        fpath = root / "forecasts" / "fm" / f"{origin}.parquet"
        mpath = root / "meta" / "fm" / f"{origin}.parquet"
        new_rows = pd.DataFrame(by_origin_rows.get(origin, []), columns=FORECAST_COLUMNS)
        new_meta = pd.DataFrame(by_origin_meta.get(origin, []), columns=META_COLUMNS)
        if fpath.exists():
            old = pd.read_parquet(fpath)
            old = old[~old["model"].isin(models_run)]
            new_rows = pd.concat([old, new_rows], ignore_index=True)
        if mpath.exists():
            oldm = pd.read_parquet(mpath)
            oldm = oldm[~oldm["model"].isin(models_run | {"-"})]
            new_meta = pd.concat([oldm, new_meta], ignore_index=True)
        write_atomic(new_rows, fpath)
        write_atomic(new_meta, mpath)
    return {
        "fm_ok": n_ok,
        "fm_error": n_err,
        "origins_written": len(set(by_origin_rows) | set(by_origin_meta)),
    }


# ------------------------------------------------------------------ outturns and manifest


def build_outturns(cfg: Config | None = None, root: Path = BACKTEST_ROOT) -> dict:
    cfg = cfg or load_config()
    table = read_all()
    fc = read_forecasts(root)
    if fc.empty:
        return {"outturns": 0}
    ob = OutturnBuilder(cfg, table)
    kinds = {(e, t): cfg.targets[e][t].transform for e in cfg.economies for t in cfg.targets[e]}
    rows = []
    for (econ, target, sid, freq), g in fc.groupby(["econ", "target", "series_id", "freq"]):
        for period in sorted(g["target_period"].unique()):
            rows.append(ob.outturn(econ, target, sid, freq, kinds[(econ, target)], period))
    out = pd.DataFrame(rows, columns=OUTTURN_COLUMNS)
    write_atomic(out, root / "outturns.parquet")
    # cumulative outturns for the levels variant: keyed by (series, last_period, period)
    meta = read_meta(root)
    lv = fc[fc["space"] == "level"][
        ["econ", "target", "series_id", "origin", "target_period"]
    ].drop_duplicates()
    crow = []
    if not lv.empty:
        lp = (
            meta.dropna(subset=["last_period"])
            .drop_duplicates(["origin", "econ", "target", "input_mode"])[
                ["origin", "econ", "target", "last_period"]
            ]
            .drop_duplicates(["origin", "econ", "target"])
        )
        lv = lv.merge(lp, on=["origin", "econ", "target"], how="left")
        for (econ, target, sid, last_period, period), _ in lv.groupby(
            ["econ", "target", "series_id", "last_period", "target_period"]
        ):
            first, revised = ob.cumulative_outturn(
                sid, target, kinds[(econ, target)], last_period, period
            )
            crow.append(
                {
                    "econ": econ,
                    "target": target,
                    "series_id": sid,
                    "last_period": last_period,
                    "period": period,
                    "first_release": first,
                    "revised_12m": revised,
                }
            )
    write_atomic(
        pd.DataFrame(
            crow,
            columns=[
                "econ",
                "target",
                "series_id",
                "last_period",
                "period",
                "first_release",
                "revised_12m",
            ],
        ),
        root / "cumulative_outturns.parquet",
    )
    return {
        "outturns": len(out),
        "late_first_releases": int(out["late"].sum()),
        "cumulative": len(crow),
    }


def write_run_manifest(
    cfg: Config | None = None, root: Path = BACKTEST_ROOT, extra: dict | None = None
) -> dict:
    cfg = cfg or load_config()
    from ..config import DEFAULT_CONFIG

    man = data_manifest()
    m = {
        "written_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "config_sha256": stable_hash(json.loads(json.dumps(cfg.model_dump(), default=str))),
        "config_path": str(DEFAULT_CONFIG),
        "data_manifest_sha256": stable_hash(man),
        "n_series": len(man),
        "revised_as_of": revised_as_of_date(read_all()).isoformat(),
        **(extra or {}),
    }
    wf = root / "run_manifest.json"
    if wf.exists():
        old = json.loads(wf.read_text(encoding="utf-8"))
        m["first_written_utc"] = old.get("first_written_utc", old.get("written_utc"))
        m["first_config_sha256"] = old.get("first_config_sha256", old.get("config_sha256"))
        if m["first_config_sha256"] != m["config_sha256"]:
            m["config_changed_since_first_run"] = True
        if old.get("config_change_note") and "config_change_note" not in m:
            m["config_change_note"] = old["config_change_note"]
    else:
        m["first_written_utc"] = m["written_utc"]
        m["first_config_sha256"] = m["config_sha256"]
    root.mkdir(parents=True, exist_ok=True)
    wf.write_text(json.dumps(m, indent=1), encoding="utf-8")
    return m


# ------------------------------------------------------------------ origins and verify


def origin_list(
    cfg: Config, window: str, first: str | None = None, last: str | None = None
) -> list[dt.date]:
    day = cfg.origins.day_of_month
    today = dt.date.today()
    if window == "primary":
        f = dt.date.fromisoformat(cfg.origins.first)
    elif window in ("extension", "all"):
        f = dt.date.fromisoformat(cfg.origins.extension_first)
    else:
        raise ValueError(window)
    last_d = (
        dt.date.fromisoformat(cfg.origins.first) - dt.timedelta(days=1)
        if window == "extension"
        else today
    )
    if first:
        f = dt.date.fromisoformat(first)
    if last:
        last_d = dt.date.fromisoformat(last)
    return origins_between(f, last_d, day)


def verify_bench(
    origins: list[dt.date], cfg: Config | None = None, root: Path = BACKTEST_ROOT
) -> dict:
    """Recompute the benchmarks at the given origins in-process and compare with the stored rows."""
    cfg = cfg or load_config()
    _init_worker(int(cfg.backtest.get("threads_per_process", 4)), None)
    stored = read_forecasts(root, origins)
    stored = stored[stored["model"].isin(["naive", "ar", "bvar", "dfm", "combo_bench"])]
    tmp = root / "_verify"
    res = {"origins": [o.isoformat() for o in origins], "mismatches": []}
    for o in origins:
        stage1_origin(o, list(cfg.backtest["input_modes"]), True, [], str(tmp))
        new = pd.read_parquet(tmp / "forecasts" / "bench" / f"{o.isoformat()}.parquet")
        old = stored[stored["origin"] == o.isoformat()]
        keys = ["econ", "target", "model", "variant", "input_mode", "step", "quantile"]
        m = old.merge(new, on=keys, suffixes=("_old", "_new"))
        if len(m) != len(old) or len(m) != len(new):
            res["mismatches"].append(
                {
                    "origin": o.isoformat(),
                    "rows_old": len(old),
                    "rows_new": len(new),
                    "joined": len(m),
                }
            )
            continue
        bad = m[m["value_old"] != m["value_new"]]
        if not bad.empty:
            res["mismatches"].append(
                {
                    "origin": o.isoformat(),
                    "rows_differ": int(len(bad)),
                    "max_abs": float((bad["value_old"] - bad["value_new"]).abs().max()),
                }
            )
    res["identical"] = not res["mismatches"]
    return res


if __name__ == "__main__":
    import sys

    stage = sys.argv[1]
    spec = json.loads(sys.argv[2])
    if stage == "stage1":
        rep = stage1(
            [dt.date.fromisoformat(o) for o in spec["origins"]],
            Path(spec["workdir"]),
            modes=spec.get("modes"),
            run_bench=spec.get("run_bench", True),
            models=spec.get("models"),
            processes=spec.get("processes"),
            force=spec.get("force", False),
        )
        print(json.dumps(rep))
    elif stage == "stage3":
        rep = stage3(Path(spec["workdir"]))
        rep.update(build_outturns())
        rep.update(
            {
                "manifest": write_run_manifest(
                    extra={
                        "last_stage3_workdir": spec["workdir"],
                        **({"config_change_note": spec["note"]} if spec.get("note") else {}),
                    }
                )["config_sha256"]
            }
        )
        print(json.dumps(rep))
    elif stage == "verify":
        res = verify_bench([dt.date.fromisoformat(o) for o in spec["origins"]])
        res["verified_utc"] = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
        stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        (BACKTEST_ROOT / f"verify_{stamp}.json").write_text(json.dumps(res, indent=1))
        print(json.dumps(res))
        if res["mismatches"]:
            raise SystemExit(3)
    else:
        raise SystemExit("usage: backtest.py stage1|stage3|verify JSON")
