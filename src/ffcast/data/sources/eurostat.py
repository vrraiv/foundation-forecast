"""Eurostat dissemination API (JSON-stat 2.0). Latest data only: each download is a snapshot
dated by its download day. Used for live runs and for lag-only series."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pandas as pd

from ..raw import RawFile, RawStore
from ..store import snapshots_to_changelog

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
SOURCE = "eurostat"


def series_id(dataset: str, filters: dict[str, str]) -> str:
    f = ".".join(f"{k}={v}" for k, v in sorted(filters.items()))
    return f"{SOURCE}:{dataset}[{f}]"


def download(store: RawStore, dataset: str, filters: dict[str, str], geo: str) -> RawFile:
    params = {"format": "JSON", "lang": "EN", "geo": geo, **filters}
    name = f"{dataset}_{geo}_" + "_".join(f"{k}-{v}" for k, v in sorted(filters.items())) + ".json"
    return store.fetch(SOURCE, name, f"{BASE}/{dataset}", params=params)


def parse_jsonstat(path: Path) -> tuple[pd.Series, str]:
    """Return (series indexed by period string, updated timestamp). Requires every
    dimension except time to have exactly one category."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    dims = d["dimension"]
    order = d["id"]
    sizes = d["size"]
    time_dim = "time"
    for k, n in zip(order, sizes, strict=True):
        if k != time_dim and n != 1:
            raise ValueError(f"{path}: dimension {k} has {n} categories; filters must pin it")
    times = dims[time_dim]["category"]["index"]
    # index may be a dict label->position or a list
    if isinstance(times, dict):
        pos_to_label = {v: k for k, v in times.items()}
    else:
        pos_to_label = dict(enumerate(times))
    vals = d["value"]
    out = {}
    for pos, label in pos_to_label.items():
        v = vals.get(str(pos))
        if v is not None:
            out[_period(label)] = float(v)
    return pd.Series(out, dtype=float).sort_index(), d.get("updated", "")


def _period(label: str) -> str:
    # Eurostat: "2024-01", "2024-Q1", "2024"
    return label


def normalise(path: Path, dataset: str, filters: dict[str, str], download_date: dt.date) -> pd.DataFrame:
    ser, updated = parse_jsonstat(path)
    sid = series_id(dataset, filters)
    return snapshots_to_changelog([(download_date, f"download {download_date} (updated {updated})", ser)], sid, SOURCE)
