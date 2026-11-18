"""Bank of Canada Valet API. Latest data only (snapshot per download day). Carries Canadian
CPI (StatCan v41690973) and the Bank's core measures without the StatCan bot challenge."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pandas as pd

from ..raw import RawFile, RawStore
from ..store import snapshots_to_changelog

BASE = "https://www.bankofcanada.ca/valet/observations"
SOURCE = "valet"


def series_id(series: str) -> str:
    return f"{SOURCE}:{series}"


def download(store: RawStore, series: str) -> RawFile:
    return store.fetch(SOURCE, f"{series}.json", f"{BASE}/{series}/json")


def parse(path: Path, series: str) -> pd.Series:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    out = {}
    for obs in d["observations"]:
        v = obs.get(series, {}).get("v")
        if v not in (None, ""):
            out[_period(obs["d"])] = float(v)
    return pd.Series(out, dtype=float).sort_index()


def _period(d: str) -> str:
    # Valet dates monthly series as YYYY-MM-01
    return d[:7]


def normalise(path: Path, series: str, download_date: dt.date) -> pd.DataFrame:
    ser = parse(path, series)
    return snapshots_to_changelog(
        [(download_date, f"download {download_date}", ser)], series_id(series), SOURCE
    )
