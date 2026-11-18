"""OECD short-term economic statistics revisions dataset (monthly snapshot editions).

Vintage = EDITION (YYYYMM). The dataset carries no publication day, so the vintage date is
assigned by a rule from the config:

  same_month_eve : edition M dated the day before the origin day of month M, so it is
                   visible at that month's origin. An assumption about OECD publication
                   timing; the evidence (edition content versus national release dates) is
                   tabulated in docs/data_quality.md section 4.
  conservative   : edition M dated the first day of month M+1, so it is visible only at
                   the next month's origin.

Levels are NOT comparable across editions (index bases change silently); downstream code
must compute growth rates within one vintage, which `as_of` guarantees.
"""

from __future__ import annotations

import calendar as _cal
import datetime as dt
import io
from pathlib import Path

import pandas as pd

from ..raw import RawFile, RawStore
from ..store import empty_table, snapshots_to_changelog

BASE = "https://sdmx.oecd.org/public/rest/data"
DATAFLOW = "OECD.SDD.STES,DSD_STES_REVISIONS@DF_STES_REVISIONS,4.0"
SOURCE = "oecd"


def key(ref_area: str, freq: str, measure: str, unit: str, activity: str, edition: str = "") -> str:
    return f"{ref_area}.{freq}.{measure}.{unit}.{activity}.{edition}"


def series_id(ref_area: str, freq: str, measure: str, unit: str, activity: str) -> str:
    return f"{SOURCE}:{ref_area}.{freq}.{measure}.{unit}.{activity}"


def download(store: RawStore, ref_area: str, freq: str, measure: str, unit: str, activity: str) -> RawFile:
    """All editions of one series, CSV without labels (labels contain quoted commas)."""
    k = key(ref_area, freq, measure, unit, activity)
    url = f"{BASE}/{DATAFLOW}/{k}"
    name = f"{ref_area}_{freq}_{measure}_{unit}_{activity}.csv"
    return store.fetch(SOURCE, name, url, params={"format": "csvfile"}, timeout=600)


def parse_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    need = {"REF_AREA", "FREQ", "MEASURE", "UNIT_MEASURE", "ACTIVITY", "EDITION", "TIME_PERIOD", "OBS_VALUE"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    return df


def edition_vintage_date(edition: str, rule: str, day_of_month: int) -> dt.date:
    """Assign a publication date to a month-stamped edition.

    same_month_eve : edition M is dated the day before the origin day of month M, so it is
                     visible at that month's origin under the strict `as_of` rule. This is an
                     ASSUMPTION about OECD's publication timing, supported by edition content
                     (docs/data_quality.md section 4) but not by a published schedule.
    conservative   : edition M is dated the first day of M+1 (visible one origin later).
    """
    y, m = int(edition[:4]), int(edition[4:6])
    if rule == "same_month_eve":
        return dt.date(y, m, max(1, min(day_of_month - 1, _cal.monthrange(y, m)[1])))
    if rule == "conservative":
        y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
        return dt.date(y2, m2, 1)
    raise ValueError(f"unknown oecd_edition_rule {rule!r}")


def normalise(path: Path, rule: str, day_of_month: int) -> pd.DataFrame:
    """One raw CSV (one series, all editions) -> change-log table."""
    df = parse_csv(path)
    if df.empty:
        return empty_table()
    first = df.iloc[0]
    sid = series_id(first.REF_AREA, first.FREQ, first.MEASURE, first.UNIT_MEASURE, first.ACTIVITY)
    if df[["REF_AREA", "FREQ", "MEASURE", "UNIT_MEASURE", "ACTIVITY"]].drop_duplicates().shape[0] != 1:
        raise ValueError(f"{path}: more than one series in file")

    def snaps():
        for ed, g in df.groupby("EDITION", sort=True):
            s = pd.Series(g["OBS_VALUE"].to_numpy(), index=g["TIME_PERIOD"].to_numpy())
            s = s[~s.index.duplicated(keep="last")]
            yield edition_vintage_date(ed, rule, day_of_month), ed, s

    return snapshots_to_changelog(snaps(), sid, SOURCE)


def editions_in(path: Path) -> list[str]:
    return sorted(parse_csv(path)["EDITION"].unique())


def months_between(edition: str, period: str) -> int:
    """Edition month minus the month in which `period` ends (quarters end in month 3q)."""
    ey, em = int(edition[:4]), int(edition[4:6])
    if "-Q" in period:
        py, pm = int(period[:4]), int(period[-1]) * 3
    else:
        py, pm = int(period[:4]), int(period[5:7])
    return (ey * 12 + em) - (py * 12 + pm)


def edition_content_check(path: Path) -> pd.DataFrame:
    """Per edition: newest reference period it contains, and the lag in months between the
    edition month and that period. Used by the calendar checks for the same-month rule."""
    df = parse_csv(path)
    rows = []
    for ed, g in df.groupby("EDITION", sort=True):
        newest = max(g["TIME_PERIOD"])
        ey, em = int(ed[:4]), int(ed[4:6])
        if "-Q" in newest:
            py, pq = int(newest[:4]), int(newest[-1])
            pm = pq * 3
        else:
            py, pm = int(newest[:4]), int(newest[5:7])
        rows.append({"edition": ed, "newest_period": newest, "lag_months": (ey * 12 + em) - (py * 12 + pm)})
    return pd.DataFrame(rows)


def read_bytes_csv(b: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(b), dtype=str)
