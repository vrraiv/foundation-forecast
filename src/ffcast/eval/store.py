"""Forecast store for the backtest (Phase 4).

Layout under `data/backtest/` (git-ignored; forecast values are private):

    forecasts/{bench,fm}/<origin>.parquet   one file per origin and model family, atomic writes
    meta/{bench,fm}/<origin>.parquet        one row per (origin, econ, target, model, variant, input_mode)
    outturns.parquet             one row per (econ, target, series_id, period)
    run_manifest.json            config hash, data manifest hash, weights digests, code version

Forecast rows: origin, econ, target, freq, model, variant, input_mode, space, step,
target_period, quantile, value, mean, series_id, source_role, cache_key.

`space` is "transformed" for the stationary variant and "level" for the levels variant (the
level quantile at each step; `last_level` and `last_period` are in the meta rows so scoring can
map it back exactly).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import pandas as pd

from ..data.store import DATA_ROOT

BACKTEST_ROOT = DATA_ROOT / "backtest"

FORECAST_COLUMNS = [
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
    "quantile",
    "value",
    "mean",
    "series_id",
    "source_role",
    "cache_key",
]

META_COLUMNS = [
    "origin",
    "econ",
    "target",
    "freq",
    "model",
    "variant",
    "input_mode",
    "status",  # ok | skipped | error
    "note",
    "series_id",
    "source_role",
    "last_period",
    "last_level",
    "n_history",
    "n_vars",
    "runtime_s",
    "cache_key",
]


def stable_hash(obj) -> str:
    """SHA-256 of a canonical JSON encoding."""
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def write_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def forecast_path(root: Path, origin: dt.date) -> Path:
    return root / "forecasts" / f"{origin.isoformat()}.parquet"


def meta_path(root: Path, origin: dt.date) -> Path:
    return root / "meta" / f"{origin.isoformat()}.parquet"


def empty_forecasts() -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in FORECAST_COLUMNS})


def empty_meta() -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in META_COLUMNS})


def _files(root: Path, kind: str, origins: list[dt.date] | None) -> list[Path]:
    """`<root>/<kind>/{bench,fm}/<origin>.parquet`."""
    d = root / kind
    files = sorted(d.glob("*/*.parquet")) if d.exists() else []
    if origins is not None:
        want = {o.isoformat() for o in origins}
        files = [f for f in files if f.stem in want]
    return files


def read_forecasts(
    root: Path = BACKTEST_ROOT, origins: list[dt.date] | None = None
) -> pd.DataFrame:
    files = _files(root, "forecasts", origins)
    if not files:
        return empty_forecasts()
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


def read_meta(root: Path = BACKTEST_ROOT, origins: list[dt.date] | None = None) -> pd.DataFrame:
    files = _files(root, "meta", origins)
    if not files:
        return empty_meta()
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


def forecast_rows(
    *,
    origin: dt.date,
    econ: str,
    target: str,
    freq: str,
    model: str,
    variant: str,
    input_mode: str,
    space: str,
    target_periods: list[str],
    quantiles: tuple[float, ...],
    values,
    mean,
    series_id: str,
    source_role: str,
    cache_key: str,
) -> list[dict]:
    rows = []
    for h, period in enumerate(target_periods):
        for j, q in enumerate(quantiles):
            rows.append(
                {
                    "origin": origin.isoformat(),
                    "econ": econ,
                    "target": target,
                    "freq": freq,
                    "model": model,
                    "variant": variant,
                    "input_mode": input_mode,
                    "space": space,
                    "step": h + 1,
                    "target_period": period,
                    "quantile": float(q),
                    "value": float(values[h, j]),
                    "mean": None if mean is None else float(mean[h]),
                    "series_id": series_id,
                    "source_role": source_role,
                    "cache_key": cache_key,
                }
            )
    return rows
