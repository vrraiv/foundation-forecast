"""Unrevised financial series, daily, dated by their own observation date.

Each observation (date d, value) becomes an R row with ref_period = d and vintage_date = d,
so `as_of(origin)` returns exactly the observations dated before the origin. Models
aggregate to monthly means or end-of-month values themselves. Policy-rate series from the
ECB are "date of change" series (sparse); consumers must forward-fill.

Providers: ECB Data Portal non-RTD flows (FM, EXR, YC) and Bank of Canada Valet daily series.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..raw import RawFile, RawStore
from ..store import validate_table

ECB_BASE = "https://data-api.ecb.europa.eu/service/data"
VALET_BASE = "https://www.bankofcanada.ca/valet/observations"


def ecb_series_id(flow: str, key: str) -> str:
    return f"ecb:{flow}.{key}"


def valet_series_id(series: str) -> str:
    return f"valet:{series}"


def download_ecb(store: RawStore, flow: str, key: str) -> RawFile:
    name = f"{flow}_{key.replace('.', '_')}.csv"
    return store.fetch("ecb-fin", name, f"{ECB_BASE}/{flow}/{key}", params={"format": "csvdata"}, timeout=300)


def download_valet(store: RawStore, series: str) -> RawFile:
    return store.fetch("valet", f"{series}.json", f"{VALET_BASE}/{series}/json", timeout=300)


def normalise_ecb(path: Path, flow: str, key: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    if df.empty:
        return validate_table(pd.DataFrame(columns=["series_id", "ref_period", "value", "vintage_date", "action", "source", "vintage_label"]))
    sid = ecb_series_id(flow, key)
    val = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    d = pd.to_datetime(df["TIME_PERIOD"], errors="coerce")
    ok = val.notna() & d.notna()
    out = pd.DataFrame(
        {
            "series_id": sid,
            "ref_period": d[ok].dt.strftime("%Y-%m-%d").to_numpy(),
            "value": val[ok].astype(float).to_numpy(),
            "vintage_date": d[ok].dt.date.to_numpy(),
            "action": "R",
            "source": "ecb",
            "vintage_label": "own-date",
        }
    )
    return validate_table(out)


def normalise_valet_monthly(path: Path, series: str) -> pd.DataFrame:
    """A monthly Valet series (dated YYYY-MM-01) that is not revised: ref_period 'YYYY-MM',
    vintage_date = last day of that month (own-dated; the Bank publishes within the month)."""
    import calendar

    d = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for obs in d["observations"]:
        v = obs.get(series, {}).get("v")
        if v in (None, ""):
            continue
        y, m = int(obs["d"][:4]), int(obs["d"][5:7])
        eom = pd.Timestamp(y, m, calendar.monthrange(y, m)[1]).date()
        rows.append((valet_series_id(series), f"{y}-{m:02d}", float(v), eom, "R", "valet", "own-month"))
    out = pd.DataFrame(rows, columns=["series_id", "ref_period", "value", "vintage_date", "action", "source", "vintage_label"])
    return validate_table(out)


def normalise_valet_daily(path: Path, series: str) -> pd.DataFrame:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for obs in d["observations"]:
        v = obs.get(series, {}).get("v")
        if v in (None, ""):
            continue
        day = pd.Timestamp(obs["d"]).date()
        rows.append((valet_series_id(series), day.isoformat(), float(v), day, "R", "valet", "own-date"))
    out = pd.DataFrame(rows, columns=["series_id", "ref_period", "value", "vintage_date", "action", "source", "vintage_label"])
    return validate_table(out)
