"""ECB Real Time Database (dataflow RTD) via the ECB Data Portal API.

`includeHistory=true` returns a change log: one row per (TIME_PERIOD, change) with ACTION
(Replace / Delete), VALID_FROM and VALID_TO. Replace rows carry VALID_FROM (the vintage
timestamp, 15:30 CET on the eve of a Governing Council meeting). Delete rows carry a blank
VALID_FROM and the deletion time in VALID_TO. Both map onto the normalised change log:

    Replace -> action R, vintage_date = VALID_FROM date
    Delete  -> action D, vintage_date = VALID_TO date

A Replace row with a blank VALID_FROM would be undated and is an error (recorded, not
guessed).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..raw import RawFile, RawStore
from ..store import empty_table, validate_table

BASE = "https://data-api.ecb.europa.eu/service/data/RTD"
SOURCE = "rtd"


def series_id(key: str) -> str:
    return f"{SOURCE}:{key}"


def download_history(store: RawStore, key: str) -> RawFile:
    name = f"RTD_{key.replace('.', '_')}_history.csv"
    return store.fetch(
        SOURCE,
        name,
        f"{BASE}/{key}",
        params={"format": "csvdata", "includeHistory": "true"},
        timeout=600,
    )


def download_latest(store: RawStore, key: str) -> RawFile:
    name = f"RTD_{key.replace('.', '_')}_latest.csv"
    return store.fetch(SOURCE, name, f"{BASE}/{key}", params={"format": "csvdata"}, timeout=300)


def parse_history(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    need = {"KEY", "TIME_PERIOD", "OBS_VALUE", "ACTION", "VALID_FROM", "VALID_TO"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    return df


def normalise(path: Path) -> tuple[pd.DataFrame, list[str]]:
    """Returns (table, problems). Problems are rows that could not be dated; they are
    excluded from the table and must be recorded by the caller."""
    df = parse_history(path)
    if df.empty:
        return empty_table(), []
    keys = df["KEY"].unique()
    if len(keys) != 1:
        raise ValueError(f"{path}: expected one series key, got {list(keys)}")
    key = keys[0].removeprefix("RTD.")
    sid = series_id(key)
    problems: list[str] = []
    blank_replaces = 0
    rows = []
    for r in df.itertuples(index=False):
        act = r.ACTION
        if act == "Replace":
            if not r.VALID_FROM:
                problems.append(f"{sid} {r.TIME_PERIOD}: Replace without VALID_FROM")
                continue
            val = pd.to_numeric(r.OBS_VALUE, errors="coerce")
            if r.OBS_VALUE == "":
                # A Replace with an empty value is how the ECB removes an observation from the
                # vintage onward (seen for HICP 1990-1995 at 2024-04-10, OBS_STATUS Q).
                # Treated as a delete dated VALID_FROM; counted, not guessed.
                blank_replaces += 1
                rows.append(
                    (sid, r.TIME_PERIOD, np.nan, _date(r.VALID_FROM), "D", SOURCE, r.VALID_FROM)
                )
                continue
            if pd.isna(val):
                problems.append(
                    f"{sid} {r.TIME_PERIOD} @ {r.VALID_FROM}: non-numeric value {r.OBS_VALUE!r}"
                )
                continue
            rows.append(
                (sid, r.TIME_PERIOD, float(val), _date(r.VALID_FROM), "R", SOURCE, r.VALID_FROM)
            )
        elif act == "Delete":
            when = r.VALID_TO or r.VALID_FROM
            if not when:
                problems.append(f"{sid} {r.TIME_PERIOD}: Delete without VALID_TO")
                continue
            rows.append((sid, r.TIME_PERIOD, np.nan, _date(when), "D", SOURCE, when))
        else:
            problems.append(f"{sid} {r.TIME_PERIOD}: unknown ACTION {act!r}")
    if blank_replaces:
        problems.append(
            f"{sid}: {blank_replaces} Replace rows with empty value treated as deletes (info)"
        )
    if not rows:
        return empty_table(), problems
    out = pd.DataFrame(
        rows,
        columns=[
            "series_id",
            "ref_period",
            "value",
            "vintage_date",
            "action",
            "source",
            "vintage_label",
        ],
    )
    # Order within a vintage date: Deletes after Replaces of the same instant are rare; keep
    # file order (stable) which is what as_of relies on.
    return validate_table(out), problems


def _date(ts: str):
    return (
        pd.Timestamp(ts).tz_convert(None).date()
        if "+" in ts or ts.endswith("Z")
        else pd.Timestamp(ts).date()
    )


def parse_bulk_quarterly_csv(text: str) -> pd.DataFrame:
    """Parse one 2001-2014 bulk vintage file (wide: row0 titles, row1 'Name:' = SDW key,
    row2 'Description:', row3 'comments:', then rows 'Q1-2000', values or NA).
    Returns a long frame with columns sdw_key, ref_period ('YYYY-Qn'), value."""
    lines = text.splitlines()
    import csv

    rows = list(csv.reader(lines))
    names = rows[1]
    data = [r for r in rows[4:] if r and r[0]]
    out = []
    for r in data:
        period = r[0].strip()
        if "-" in period and period.startswith("Q"):
            q, y = period.split("-")
            period = f"{y}-{q}"
        elif "-" in period and period[:3].isalpha():  # 'Jan-2000' style
            mon, y = period.split("-")
            m = pd.Timestamp(f"{mon} 1 {y}").month
            period = f"{y}-{m:02d}"
        for j, v in enumerate(r[1:], start=1):
            if j >= len(names) or not names[j]:
                continue
            val = pd.to_numeric(v, errors="coerce")
            if pd.notna(val):
                out.append((names[j], period, float(val)))
    return pd.DataFrame(out, columns=["sdw_key", "ref_period", "value"])
