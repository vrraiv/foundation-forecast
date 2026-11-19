"""Target resolver: maps (economy, target, origin) to exactly one vintage series and provides
the model-facing history and the outturns, both from that same source.

Rule (fixed in advance): a target lists a primary vintage source and optionally a fallback.
At an origin, the primary is used if it has a vintage dated before the origin that is no older
than the source's `max_staleness_days` (config `vintage_sources.max_staleness_days`, e.g. 100
days for the ECB RTD whose normal gap is at most 98 days); otherwise the fallback is used if
it satisfies the same test. A source that has silently stopped updating (the RTD unemployment
key had no vintage between 2024-03-06 and 2025-07-23) therefore hands over to the fallback
instead of serving a stale information set. The source actually used is returned with every result so it can be
recorded next to each forecast. Histories from two sources are never merged."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import pandas as pd

from .store import as_of, first_appearance

_STATCAN_RT_TO_DBNOMICS = {
    ("36100431", "gdp"): "dbnomics:STATCAN/36100431/estim_24.price_1.sea_adj_1",
    ("36100431", "consumption"): "dbnomics:STATCAN/36100431/estim_12.price_1.sea_adj_1",
}


def series_id_for(spec: dict, econ: str, freq: str, target: str) -> str:
    src = spec["source"]
    if src == "oecd":
        return f"oecd:{econ}.{freq}.{spec['measure']}.{spec['unit']}.{spec['activity']}"
    if src == "ecb_rtd":
        return f"rtd:{spec['key']}"
    if src == "statcan_rt":
        return _STATCAN_RT_TO_DBNOMICS[(spec["table"], target)]
    if src == "pseudo":
        return f"pseudo:{spec['base']}"
    if src == "live":
        # registry only (ffcast.registry.live): the national `latest` series joined to the
        # vintage history; never present in the backtest data
        return f"live:{econ}.{target}"
    raise ValueError(f"unknown vintage source {src!r}")


@dataclass(frozen=True)
class Resolved:
    series_id: str
    source_role: str  # "primary" or "fallback"


def resolve(cfg, table: pd.DataFrame, econ: str, target: str, origin: dt.date) -> Resolved | None:
    t = cfg.targets[econ][target]
    if not t.vintages:
        return None
    limits = cfg.vintage_sources.get("max_staleness_days", {})
    primary = series_id_for(t.vintages, econ, t.freq, target)
    if _fresh_vintage_before(table, primary, origin, limits):
        return Resolved(primary, "primary")
    fb = t.vintages.get("fallback")
    if fb:
        fsid = series_id_for(fb, econ, t.freq, target)
        if _fresh_vintage_before(table, fsid, origin, limits):
            return Resolved(fsid, "fallback")
    return None


def _fresh_vintage_before(table: pd.DataFrame, sid: str, origin: dt.date, limits: dict) -> bool:
    s = table.loc[table["series_id"] == sid, "vintage_date"]
    if s.empty:
        return False
    before = pd.to_datetime(s).dt.date
    before = before[before < origin]
    if before.empty:
        return False
    limit = limits.get(sid.split(":")[0])
    if limit is None:
        return True
    return (origin - before.max()).days <= int(limit)


def history(
    cfg, table: pd.DataFrame, econ: str, target: str, origin: dt.date
) -> tuple[pd.Series, Resolved] | None:
    r = resolve(cfg, table, econ, target, origin)
    if r is None:
        return None
    return as_of(table, [r.series_id], origin)[r.series_id], r


@dataclass(frozen=True)
class Outturn:
    period: str
    series_id: str
    first_release: float | None
    first_release_date: dt.date | None
    revised_12m: float | None
    revised_12m_date: dt.date | None


def outturn(table: pd.DataFrame, sid: str, period: str, months_after: int = 12) -> Outturn:
    """First release = value in the earliest vintage containing `period`; revised =
    the vintage visible 12 months after that date (strict), same source."""
    fa = first_appearance(table, sid)
    if period not in fa.index:
        return Outturn(period, sid, None, None, None, None)
    d0 = pd.Timestamp(fa[period]).date()
    first = as_of(table, [sid], d0 + dt.timedelta(days=1))[sid].get(period)
    d1 = _add_months(d0, months_after)
    later = as_of(table, [sid], d1, strict=False)[sid].get(period)
    return Outturn(
        period,
        sid,
        None if first is None else float(first),
        d0,
        None if later is None else float(later),
        d1,
    )


def outturn_transformed(
    table: pd.DataFrame, sid: str, period: str, kind: str, months_after: int = 12
) -> Outturn:
    """Outturns in the transformed space (growth or change), each computed INSIDE one vintage:
    the first vintage containing `period` gives the first-release growth from that vintage's
    own previous-period value; the vintage visible `months_after` months later gives the
    revised growth, again from its own previous value. A rebasing between the two vintages
    therefore cancels out."""
    from .transform import transform

    fa = first_appearance(table, sid)
    if period not in fa.index:
        return Outturn(period, sid, None, None, None, None)
    d0 = pd.Timestamp(fa[period]).date()
    v0 = as_of(table, [sid], d0 + dt.timedelta(days=1))[sid]
    d1 = _add_months(d0, months_after)
    v1 = as_of(table, [sid], d1, strict=False)[sid]

    def g(v):
        try:
            t = transform(v, kind)
        except ValueError:
            return None
        return None if period not in t.index else float(t[period])

    return Outturn(period, sid, g(v0), d0, g(v1), d1)


def _add_months(d: dt.date, k: int) -> dt.date:
    import calendar

    idx = d.year * 12 + (d.month - 1) + k
    y, m = idx // 12, idx % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))
