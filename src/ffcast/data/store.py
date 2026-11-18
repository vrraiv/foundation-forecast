"""Normalised vintage table and the `as_of` function.

Every source is reduced to one change-log table with columns

    series_id     str   e.g. "oecd:CAN.M.CP.IX._Z", "rtd:M.S0.N.P_C_OV.X"
    ref_period    str   "YYYY-MM" or "YYYY-Qn"
    value         float NaN on a delete
    vintage_date  date  the publication date of the vintage (never the reference date)
    action        str   "R" (replace/insert) or "D" (delete)
    source        str   provider name
    vintage_label str   provider's own vintage identifier (edition code, VALID_FROM, release)

A full snapshot source (OECD editions, StatCan releases) is converted to this form by
diffing consecutive snapshots, emitting R for new or changed values and D for periods that
disappear. A change-log source (ECB RTD) maps directly. `as_of` therefore has one
semantics: for each period, the last row dated strictly before (or on) the origin wins,
and a D row means the period is absent.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd

from .raw import DATA_ROOT

COLUMNS = ["series_id", "ref_period", "value", "vintage_date", "action", "source", "vintage_label"]
NORMALISED_ROOT = DATA_ROOT / "normalised"


def empty_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "series_id": pd.Series(dtype="string"),
            "ref_period": pd.Series(dtype="string"),
            "value": pd.Series(dtype="float64"),
            "vintage_date": pd.Series(dtype="object"),
            "action": pd.Series(dtype="string"),
            "source": pd.Series(dtype="string"),
            "vintage_label": pd.Series(dtype="string"),
        }
    )


def validate_table(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"vintage table missing columns {missing}")
    out = df[COLUMNS].copy()
    out["vintage_date"] = pd.to_datetime(out["vintage_date"]).dt.date
    if not out["action"].isin(["R", "D"]).all():
        raise ValueError("action must be R or D")
    if (out.loc[out["action"] == "R", "value"].isna()).any():
        raise ValueError("R rows must carry a value")
    return out.reset_index(drop=True)


def snapshots_to_changelog(
    snapshots: Iterable[tuple[dt.date, str, pd.Series]],
    series_id: str,
    source: str,
) -> pd.DataFrame:
    """Diff an ordered sequence of full snapshots into R/D rows.

    `snapshots` yields (vintage_date, vintage_label, series indexed by ref_period) in
    ascending vintage order. Two snapshots with the same vintage_date are not allowed."""
    rows: list[dict] = []
    prev: pd.Series | None = None
    last_date: dt.date | None = None
    for vdate, label, snap in snapshots:
        if last_date is not None and vdate <= last_date:
            raise ValueError(f"{series_id}: snapshots must have strictly increasing dates")
        last_date = vdate
        snap = snap.dropna().astype(float)
        snap.index = snap.index.astype(str)
        if prev is None:
            changed = snap
            deleted: pd.Index = pd.Index([])
        else:
            common = snap.index.intersection(prev.index)
            # Tolerance absorbs float-representation noise in provider CSVs (e.g. 5.1 printed
            # as 5.09999999999999 in a later OECD edition); real revisions are far larger.
            diff = common[
                ~np.isclose(snap[common].to_numpy(), prev[common].to_numpy(), rtol=1e-9, atol=1e-12)
            ]
            new = snap.index.difference(prev.index)
            changed = snap[diff.union(new)]
            deleted = prev.index.difference(snap.index)
        for p, v in changed.items():
            rows.append(_row(series_id, p, float(v), vdate, "R", source, label))
        for p in deleted:
            rows.append(_row(series_id, p, np.nan, vdate, "D", source, label))
        prev = snap
    if not rows:
        return empty_table()
    return validate_table(pd.DataFrame(rows))


def _row(sid: str, period: str, value: float, vdate: dt.date, action: str, source: str, label: str) -> dict:
    return {
        "series_id": sid,
        "ref_period": period,
        "value": value,
        "vintage_date": vdate,
        "action": action,
        "source": source,
        "vintage_label": label,
    }


def as_of(
    table: pd.DataFrame,
    series_ids: Iterable[str],
    origin: dt.date,
    *,
    strict: bool = True,
) -> dict[str, pd.Series]:
    """Return, per series, the vintage visible at `origin`.

    strict=True (the project default) uses vintage_date < origin; strict=False uses <=.
    This is the only function models and benchmarks may use to obtain data."""
    ids = list(series_ids)
    vd = pd.to_datetime(table["vintage_date"])
    cutoff = pd.Timestamp(origin)
    mask = (vd < cutoff) if strict else (vd <= cutoff)
    sub = table.loc[mask & table["series_id"].isin(ids)].copy()
    sub["_vd"] = vd[mask & table["series_id"].isin(ids)]
    out: dict[str, pd.Series] = {}
    for sid in ids:
        s = sub[sub["series_id"] == sid]
        if s.empty:
            out[sid] = pd.Series(dtype="float64", name=sid)
            continue
        # stable sort so that, within one vintage date, later file rows win (D after R etc.)
        s = s.sort_values(["ref_period", "_vd"], kind="stable")
        last = s.groupby("ref_period", sort=True).tail(1)
        last = last[last["action"] == "R"]
        ser = pd.Series(last["value"].to_numpy(dtype=float), index=last["ref_period"].to_numpy(), name=sid)
        ser.index.name = "ref_period"
        out[sid] = ser.sort_index()
    return out


def latest_vintage_date(table: pd.DataFrame, series_id: str) -> dt.date | None:
    s = table.loc[table["series_id"] == series_id, "vintage_date"]
    return None if s.empty else max(pd.to_datetime(s).dt.date)


def revised_view(
    table: pd.DataFrame,
    series_ids: Iterable[str],
    origin: dt.date,
    revised_as_of: dt.date,
    *,
    strict: bool = True,
) -> dict[str, pd.Series]:
    """The "revised" input for Q1: the vintage visible at `revised_as_of` (a pinned snapshot
    date, not "now"), truncated to the reference periods that were visible at `origin`."""
    ids = list(series_ids)
    rt = as_of(table, ids, origin, strict=strict)
    rev = as_of(table, ids, revised_as_of, strict=strict)
    out = {}
    for sid in ids:
        visible = rt[sid].index
        out[sid] = rev[sid].reindex(visible).dropna()
    return out


def first_appearance(table: pd.DataFrame, series_id: str) -> pd.Series:
    """For each ref_period, the first vintage_date on which an R row appeared (release
    calendar input)."""
    s = table[(table["series_id"] == series_id) & (table["action"] == "R")]
    g = s.groupby("ref_period")["vintage_date"].min()
    return g.sort_index()


def write_table(df: pd.DataFrame, path: Path) -> str:
    """Write parquet and return its SHA-256 (content pin)."""
    from .raw import sha256_file

    path.parent.mkdir(parents=True, exist_ok=True)
    df = validate_table(df)
    df["vintage_date"] = pd.to_datetime(df["vintage_date"])
    df.to_parquet(path, index=False)
    return sha256_file(path)


def read_table(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return validate_table(df)


def read_all(root: Path = NORMALISED_ROOT) -> pd.DataFrame:
    parts = [read_table(p) for p in sorted(Path(root).glob("*.parquet"))]
    if not parts:
        return empty_table()
    return pd.concat(parts, ignore_index=True)
