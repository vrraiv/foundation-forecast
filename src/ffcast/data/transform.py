"""Stationary transforms applied within one vintage, and their inverses.

log_diff : 100 * diff(log(x))   (percent growth, one period)
diff     : diff(x)              (percentage-point change, e.g. unemployment rate)

Transforms are always computed inside a single `as_of` vintage, so rebasings never leak in.
Multi-step forecasts in the transformed space are cumulated back to levels with the last
observed level of the same vintage."""

from __future__ import annotations

import numpy as np
import pandas as pd


def transform(series: pd.Series, kind: str) -> pd.Series:
    s = series.astype(float)
    if kind == "log_diff":
        if (s <= 0).any():
            raise ValueError("log_diff needs strictly positive levels")
        return (100.0 * np.log(s).diff()).dropna()
    if kind == "diff":
        return s.diff().dropna()
    raise ValueError(f"unknown transform {kind!r}")


def cumulate_to_levels(last_level: float, steps: np.ndarray, kind: str) -> np.ndarray:
    """Map a path of transformed-space values (one per step) to levels."""
    steps = np.asarray(steps, dtype=float)
    if kind == "log_diff":
        return last_level * np.exp(np.cumsum(steps) / 100.0)
    if kind == "diff":
        return last_level + np.cumsum(steps)
    raise ValueError(kind)


def levels_to_transform_path(levels: np.ndarray, last_level: float, kind: str) -> np.ndarray:
    """Inverse of cumulate_to_levels for a forecast path of levels."""
    lv = np.concatenate([[last_level], np.asarray(levels, dtype=float)])
    if kind == "log_diff":
        return 100.0 * np.diff(np.log(lv))
    if kind == "diff":
        return np.diff(lv)
    raise ValueError(kind)


def monthly_mean_from_daily(daily: pd.Series) -> pd.Series:
    """Aggregate a daily (own-dated) series to calendar-month means; index 'YYYY-MM'."""
    if daily.empty:
        return pd.Series(dtype=float)
    idx = pd.to_datetime(daily.index)
    s = pd.Series(daily.to_numpy(dtype=float), index=idx)
    m = s.groupby(idx.strftime("%Y-%m")).mean()
    m.index.name = "ref_period"
    return m


def monthly_eom_ffill_from_daily(daily: pd.Series, through: "dt.date") -> pd.Series:
    """For date-of-change series (policy rates): forward-fill to a daily calendar up to the day
    before `through` and take each complete month's last value; index 'YYYY-MM'."""
    import datetime as dt

    if daily.empty:
        return pd.Series(dtype=float)
    idx = pd.to_datetime(daily.index)
    s = pd.Series(daily.to_numpy(dtype=float), index=idx).sort_index()
    end = pd.Timestamp(through) - pd.Timedelta(days=1)
    cal = pd.date_range(s.index[0], end, freq="D")
    f = s.reindex(cal).ffill()
    eom = f.groupby(cal.strftime("%Y-%m")).last()
    # drop the incomplete current month
    cur = pd.Timestamp(through).strftime("%Y-%m")
    eom = eom[eom.index < cur]
    eom.index.name = "ref_period"
    return eom


def quarterly_mean_from_monthly(monthly: pd.Series) -> pd.Series:
    idx = pd.PeriodIndex(monthly.index, freq="M")
    q = pd.Series(monthly.to_numpy(dtype=float), index=idx).groupby(idx.asfreq("Q")).mean()
    q.index = [f"{p.year}-Q{p.quarter}" for p in q.index]
    return q
