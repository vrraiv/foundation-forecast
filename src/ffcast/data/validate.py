"""Validate the RTD change-log rebuild against the ECB's own 2001-2014 bulk snapshot files.

Each `quarterly_YYYYMM.csv` in quarterly.zip is a full vintage. We rebuild the vintage from
the change log as of the end of that month (inclusive) and compare whole vintages, period
by period, including periods that should be absent."""

from __future__ import annotations

import csv
import datetime as dt
import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from .store import as_of

# RTD key -> (name regexes that identify the matching bulk column in each era)
BULK_COLUMN_PATTERNS = {
    "Q.S0.S.G_GDPM_TO_C.E": [
        r"^ESA\.Q\.I\d\.S\.0000\.B1QG00\.1000\.TTTT\.Q\.U\.A$",
        r"^MNA\.Q\.Y\.I\d\.W2\.S1\.S1\.B\.B1GQ\._Z\._Z\._Z\.EUR\.LR\.N$",
    ],
    "Q.S0.S.G_FCHI_TO_C.E": [
        r"^ESA\.Q\.I\d\.S\.1415\.P31000\.0000\.TTTT\.Q\.U\.A$",
        r"^MNA\.Q\.Y\.I\d\.W0\.S1M\.S1\.D\.P31\._Z\._Z\._T\.EUR\.LR\.N$",
    ],
}


@dataclass
class VintageComparison:
    key: str
    bulk_file: str
    as_of_date: dt.date
    n_bulk: int
    n_rebuilt: int
    n_match: int
    mismatches: list[tuple[str, float | None, float | None]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.mismatches and self.n_bulk == self.n_rebuilt


def _period(label: str) -> str:
    label = label.strip()
    m = re.match(r"^Q([1-4])-(\d{4})$", label)
    if m:
        return f"{m.group(2)}-Q{m.group(1)}"
    m = re.match(r"^(\d{4})Q([1-4])$", label)
    if m:
        return f"{m.group(1)}-Q{m.group(2)}"
    return label


def read_bulk_vintage(zip_path: Path, member: str, patterns: list[str]) -> pd.Series | None:
    with zipfile.ZipFile(zip_path) as z:
        text = z.read(member).decode("utf-8-sig", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    names = rows[1]
    cols = [j for j, n in enumerate(names) if any(re.match(p, n.strip()) for p in patterns)]
    if not cols:
        return None
    j = cols[0]
    out = {}
    for r in rows[4:]:
        if not r or not r[0].strip() or j >= len(r):
            continue
        v = pd.to_numeric(r[j].strip(), errors="coerce")
        if pd.notna(v):
            out[_period(r[0])] = float(v)
    return pd.Series(out, dtype=float).sort_index()


def bulk_vintage_date(table: pd.DataFrame, sid: str, year: int, month: int) -> dt.date | None:
    """The bulk file for month M is the database frozen for the Monthly Bulletin of month M,
    i.e. the state of the RTD on about the 20th of M (the vintage dated on the eve of the
    first Governing Council meeting of the month, which can fall in the last days of M-1).
    Verified empirically: quarterly_200101 == vintage 2001-01-03, quarterly_200102 ==
    2001-01-31, quarterly_200204 == 2002-04-03, quarterly_200511 == 2005-11-02. Returns the
    latest vintage date on or before the 20th of M."""
    dates = sorted(
        set(pd.to_datetime(table.loc[table["series_id"] == sid, "vintage_date"]).dt.date)
    )
    hi = dt.date(year, month, 20)
    cands = [d for d in dates if d <= hi]
    return cands[-1] if cands else None


def compare_key(
    table: pd.DataFrame, key: str, zip_path: Path, months: list[str] | None = None, rtol=1e-6
) -> list[VintageComparison]:
    sid = f"rtd:{key}"
    pats = BULK_COLUMN_PATTERNS[key]
    results = []
    with zipfile.ZipFile(zip_path) as z:
        members = sorted(n for n in z.namelist() if n.endswith(".csv"))
    for m in members:
        ym = re.search(r"(\d{6})", m).group(1)
        if months and ym not in months:
            continue
        y, mo = int(ym[:4]), int(ym[4:])
        bulk = read_bulk_vintage(zip_path, m, pats)
        if bulk is None:
            continue
        asof_date = bulk_vintage_date(table, sid, y, mo)
        if asof_date is None:
            results.append(
                VintageComparison(
                    key,
                    m,
                    dt.date(y, mo, 1),
                    len(bulk),
                    0,
                    0,
                    [("no RTD vintage in window", None, None)],
                )
            )
            continue
        rebuilt = as_of(table, [sid], asof_date, strict=False)[sid]
        periods = sorted(set(bulk.index) | set(rebuilt.index))
        mism = []
        match = 0
        for p in periods:
            b = bulk.get(p)
            r = rebuilt.get(p)
            if b is None or r is None:
                mism.append((p, b, r))
            elif not np.isclose(b, r, rtol=rtol, atol=0):
                mism.append((p, b, r))
            else:
                match += 1
        results.append(VintageComparison(key, m, asof_date, len(bulk), len(rebuilt), match, mism))
    return results


def summarise(results: list[VintageComparison]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "key": r.key,
                "bulk_file": r.bulk_file,
                "as_of": r.as_of_date,
                "n_bulk": r.n_bulk,
                "n_rebuilt": r.n_rebuilt,
                "n_match": r.n_match,
                "n_mismatch": len(r.mismatches),
                "ok": r.ok,
            }
            for r in results
        ]
    )
