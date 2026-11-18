"""Forecast-origin calendar: one origin per month on a fixed day, rolled forward to the next
business day (Monday to Friday; statistical-office holidays are not applied, so an origin may
fall on a holiday, which only makes the information set slightly staler, never earlier)."""

from __future__ import annotations

import datetime as dt


def origin_date(year: int, month: int, day_of_month: int) -> dt.date:
    d = dt.date(year, month, day_of_month)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def origins_between(first: dt.date, last: dt.date, day_of_month: int) -> list[dt.date]:
    out = []
    y, m = first.year, first.month
    while True:
        o = origin_date(y, m, day_of_month)
        if o > last:
            break
        if o >= first:
            out.append(o)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out
