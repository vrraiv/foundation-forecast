"""Pseudo-vintages for series that are not revised (or for which no vintage source exists).

From a single latest snapshot, each reference period m is given the vintage date on which it
is assumed to have become public: the eve of the origin of month m + `months_after_period`.
Values are the latest ones, which equals the first release only if the series is unrevised;
these series are therefore excluded from the real-time-versus-revised comparison (Q1) and the
assumption is recorded in the config and docs/data_quality.md."""

from __future__ import annotations

import calendar
import datetime as dt

import pandas as pd

from .store import validate_table


def pseudo_series_id(base_sid: str) -> str:
    return f"pseudo:{base_sid}"


def _shift_month(y: int, m: int, k: int) -> tuple[int, int]:
    idx = y * 12 + (m - 1) + k
    return idx // 12, idx % 12 + 1


def pseudo_vintage_date(period: str, months_after: int, day_of_month: int) -> dt.date:
    if "-Q" in period:
        y, q = int(period[:4]), int(period[-1])
        m = q * 3
    else:
        y, m = int(period[:4]), int(period[5:7])
    yy, mm = _shift_month(y, m, months_after)
    day = max(1, min(day_of_month - 1, calendar.monthrange(yy, mm)[1]))
    return dt.date(yy, mm, day)


def build(
    snapshot: pd.Series,
    base_sid: str,
    months_after: int,
    day_of_month: int,
    available_on: dt.date,
    late_months: dict | None = None,
) -> pd.DataFrame:
    """`late_months` maps a reference month number to a longer lag (e.g. {1: 2}: January
    observations become visible one origin later than other months)."""
    late = {int(k): int(v) for k, v in (late_months or {}).items()}
    rows = []
    for p, v in snapshot.dropna().items():
        month = int(str(p)[5:7]) if "-Q" not in str(p) else None
        lag = late.get(month, months_after) if month is not None else months_after
        vd = pseudo_vintage_date(str(p), lag, day_of_month)
        if vd > available_on:
            # the snapshot itself was taken before this pseudo date: do not pretend it was public
            vd = available_on
        rows.append((pseudo_series_id(base_sid), str(p), float(v), vd, "R", "pseudo", f"lag {months_after}m from {base_sid}"))
    out = pd.DataFrame(rows, columns=["series_id", "ref_period", "value", "vintage_date", "action", "source", "vintage_label"])
    return validate_table(out)
