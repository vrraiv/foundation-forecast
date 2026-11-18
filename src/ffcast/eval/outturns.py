"""Realised outturns for scoring, both definitions, from the same series the forecast used.

first_release : the value in the first vintage that contains the period, transformed inside
                that vintage (ffcast.data.targets.outturn_transformed);
revised_12m   : the vintage visible 12 months after the first release, transformed inside it.

Late first releases. A first release counts only if it appeared no later than
`median_lag + max_staleness_days[source]` days after the period end, where median_lag is the
series' median first-appearance lag over all its periods (config `backtest.late_first_release:
median_lag_plus_staleness`). Later first appearances are kept in the table with `late=True` and
the first-release value set to NaN; the revised outturn is unaffected.

Cumulative outturns (levels variant): the change from the last observed level at the origin to
the level at the target period, computed inside the first vintage containing the target period
(and inside the 12-months-later vintage), so rebasings cancel.
"""

from __future__ import annotations

import calendar
import datetime as dt
from functools import cache

import numpy as np
import pandas as pd

from ..config import Config
from ..data.store import as_of, first_appearance
from ..data.transform import transform

OUTTURN_COLUMNS = [
    "econ",
    "target",
    "series_id",
    "freq",
    "period",
    "first_release",
    "first_release_date",
    "late",
    "lag_days",
    "lag_limit_days",
    "revised_12m",
    "revised_12m_date",
]


def period_end(period: str) -> dt.date:
    if "-Q" in period:
        y, q = int(period[:4]), int(period[-1])
        m = 3 * q
    else:
        y, m = int(period[:4]), int(period[5:7])
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def add_months(d: dt.date, k: int) -> dt.date:
    idx = d.year * 12 + (d.month - 1) + k
    y, m = idx // 12, idx % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


class OutturnBuilder:
    """Caches per-series first-appearance calendars and lag limits for one table."""

    def __init__(self, cfg: Config, table: pd.DataFrame, months_after: int = 12) -> None:
        self.cfg = cfg
        self.table = table
        self.months_after = months_after
        self._fa: dict[str, pd.Series] = {}
        self._limit: dict[str, float] = {}
        self._vintage_cache: dict[tuple[str, dt.date, bool], pd.Series] = {}

    def first_appearance(self, sid: str) -> pd.Series:
        if sid not in self._fa:
            self._fa[sid] = first_appearance(self.table, sid)
        return self._fa[sid]

    def lag_limit_days(self, sid: str) -> float:
        """median first-appearance lag (days after period end) + the source's staleness limit."""
        if sid not in self._limit:
            fa = self.first_appearance(sid)
            lags = pd.Series(
                {p: (pd.Timestamp(v).date() - period_end(p)).days for p, v in fa.items()},
                dtype=float,
            )
            # Only periods that ended after the series' first vintage can have been first
            # released inside the sample; back history added by the first vintage or by a later
            # extension (DBnomics 36-10-0431 adds 1961-2012 chained-dollar history in a later
            # vintage) is not a first release and would distort the median.
            if not fa.empty:
                first_v = pd.Timestamp(fa.min()).date()
                lags = lags[[p for p in lags.index if period_end(p) >= first_v]]
            median = float(lags.median()) if len(lags) else 0.0
            limits = self.cfg.vintage_sources.get("max_staleness_days", {})
            stale = float(limits.get(sid.split(":")[0], 0))
            self._limit[sid] = median + stale
        return self._limit[sid]

    def _vintage(self, sid: str, when: dt.date, strict: bool) -> pd.Series:
        key = (sid, when, strict)
        if key not in self._vintage_cache:
            self._vintage_cache[key] = as_of(self.table, [sid], when, strict=strict)[sid]
        return self._vintage_cache[key]

    def rounding(self, target: str) -> int | None:
        r = self.cfg.backtest.get("revision_rounding", {})
        return r.get(target)

    def outturn(self, econ: str, target: str, sid: str, freq: str, kind: str, period: str) -> dict:
        fa = self.first_appearance(sid)
        row = {
            "econ": econ,
            "target": target,
            "series_id": sid,
            "freq": freq,
            "period": period,
            "first_release": np.nan,
            "first_release_date": None,
            "late": False,
            "lag_days": np.nan,
            "lag_limit_days": self.lag_limit_days(sid),
            "revised_12m": np.nan,
            "revised_12m_date": None,
        }
        if period not in fa.index:
            return row
        d0 = pd.Timestamp(fa[period]).date()
        lag = (d0 - period_end(period)).days
        row["first_release_date"] = d0.isoformat()
        row["lag_days"] = lag
        d1 = add_months(d0, self.months_after)
        row["revised_12m_date"] = d1.isoformat()
        rnd = self.rounding(target)
        v0 = self._vintage(sid, d0 + dt.timedelta(days=1), True)
        v1 = self._vintage(sid, d1, False)
        if rnd is not None:
            v0 = v0.round(rnd)
            v1 = v1.round(rnd)
        row["revised_12m"] = _transformed_value(v1, kind, period)
        if lag > row["lag_limit_days"]:
            row["late"] = True  # first release too late to count; value withheld
        else:
            row["first_release"] = _transformed_value(v0, kind, period)
        return row

    def cumulative_outturn(
        self, sid: str, target: str, kind: str, last_period: str, period: str
    ) -> tuple[float, float]:
        """(first-release, revised) cumulative change from `last_period` to `period`, each
        inside one vintage. NaN when either period is missing in that vintage."""
        fa = self.first_appearance(sid)
        if period not in fa.index:
            return np.nan, np.nan
        d0 = pd.Timestamp(fa[period]).date()
        d1 = add_months(d0, self.months_after)
        rnd = self.rounding(target)
        out = []
        for when, strict in ((d0 + dt.timedelta(days=1), True), (d1, False)):
            v = self._vintage(sid, when, strict)
            if rnd is not None:
                v = v.round(rnd)
            if last_period not in v.index or period not in v.index:
                out.append(np.nan)
                continue
            a, b = float(v[last_period]), float(v[period])
            if kind == "log_diff":
                out.append(100.0 * np.log(b / a) if a > 0 and b > 0 else np.nan)
            else:
                out.append(b - a)
        first, revised = out
        lag = (d0 - period_end(period)).days
        if lag > self.lag_limit_days(sid):
            first = np.nan
        return first, revised


def _transformed_value(vintage: pd.Series, kind: str, period: str) -> float:
    try:
        t = transform(vintage, kind)
    except ValueError:
        return np.nan
    return float(t[period]) if period in t.index else np.nan


@cache
def _noop():  # keeps lru_cache import used for future per-process caching
    return None
