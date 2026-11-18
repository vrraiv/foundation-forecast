"""Assemble, at one origin, the target history and the conditioning panel from `as_of` only.

Everything a model or benchmark receives passes through here, so the information set is
defined in exactly one place:

- target: the resolved vintage series (ffcast.data.targets), transformed within the vintage;
- monthly conditioning: OECD / RTD monthly series visible at the origin, transformed;
  daily financial series aggregated to month means over days strictly before the origin
  (the current, incomplete month is dropped);
- quarterly conditioning: OECD / RTD quarterly series, transformed.

Input modes (config backtest.input_modes): "realtime" uses `as_of(origin)`; "revised" uses the
vintage visible at a pinned later date (`revised_as_of`, the data snapshot date) cut to the
reference periods visible at the origin, so the information horizon is identical and only the
values differ. Level blocks (`monthly_lv`, `quarterly_lv`) hold the same series untransformed
for the levels variant; variable selection is always made on the transformed block so both
variants see the same variables.

Series whose transform is undefined (non-positive levels for log_diff) are dropped and named
in the result so the drop is visible.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import pandas as pd

from ..config import Config
from ..data import targets as tg
from ..data.store import as_of
from ..data.transform import monthly_eom_ffill_from_daily, monthly_mean_from_daily, transform

FIN_TRANSFORM = {"rate": "diff", "index": "log_diff"}


@dataclass
class Panel:
    origin: dt.date
    econ: str
    target: str
    target_sid: str
    source_role: str
    freq: str
    kind: str  # transform kind of the target
    target_levels: pd.Series
    target_tr: pd.Series
    monthly: pd.DataFrame  # transformed, target first when the target is monthly
    quarterly: pd.DataFrame  # transformed, target first when the target is quarterly
    dropped: list[str] = field(default_factory=list)
    input_mode: str = "realtime"
    monthly_lv: pd.DataFrame | None = None  # same columns as `monthly`, untransformed
    quarterly_lv: pd.DataFrame | None = None

    def univariate(self, space: str = "transformed") -> pd.Series:
        if space == "level":
            return self.target_levels.loc[self.target_tr.index[0] :]
        return self.target_tr

    def multivariate(
        self,
        max_vars: int | None = None,
        min_coverage: float = 0.8,
        max_stale: int = 12,
        balanced: bool = False,
        space: str = "transformed",
    ) -> pd.DataFrame:
        """Target plus same-frequency conditioning variables, aligned on the target's index.

        Selection rule (fixed in advance): keep conditioning columns, in config order, whose
        coverage of the target's last `window` periods is at least `min_coverage` and whose last
        observation is no more than `max_stale` periods older than the target's last; stop at
        `max_vars` columns including the target. The ragged edge at the end is kept as NaN."""
        block = self.monthly if self.freq == "M" else self.quarterly
        tcol = block.columns[0]
        idx = block.index[block[tcol].notna()]
        window = idx[-(240 if self.freq == "M" else 80) :]
        last_t = idx[-1]
        keep = [tcol]
        for c in block.columns[1:]:
            col = block[c]
            cov = col.reindex(window).notna().mean()
            obs = col.dropna()
            if obs.empty or cov < min_coverage:
                continue
            stale = int(block.index.get_loc(last_t)) - int(block.index.get_loc(obs.index[-1]))
            if stale > max_stale:
                continue
            keep.append(c)
            if max_vars is not None and len(keep) >= max_vars:
                break
        if space == "level":
            lv = self.monthly_lv if self.freq == "M" else self.quarterly_lv
            if lv is None:
                raise ValueError("panel was built without level blocks")
            block = lv
        out = block.loc[window[0] :, keep]
        if balanced:
            # For models that cannot take missing values: end at the target's last observation,
            # DROP conditioning columns whose last observation is earlier than the target's (no
            # values are invented at the ragged edge), carry forward interior gaps only, and
            # keep the rows where everything is observed.
            out = out.loc[:last_t].copy()
            keep_cols = [tcol] + [c for c in out.columns[1:] if out[c].dropna().index[-1] == last_t]
            out = out[keep_cols]
            out.iloc[:, 1:] = out.iloc[:, 1:].ffill()
            out = out.dropna()
        return out

    def target_periods(self, horizon: int) -> list[str]:
        """Reference periods that forecast steps 1..horizon refer to: the periods after the
        target's last observation in its own vintage."""
        last = self.target_tr.index[-1]
        if self.freq == "M":
            p = pd.Period(last, freq="M")
            return [f"{(p + h).year}-{(p + h).month:02d}" for h in range(1, horizon + 1)]
        p = pd.Period(last.replace("-Q", "Q"), freq="Q")
        return [f"{(p + h).year}-Q{(p + h).quarter}" for h in range(1, horizon + 1)]


def _cond_sid(spec: dict, econ: str) -> str:
    src = spec["source"]
    if src == "oecd":
        return f"oecd:{econ}.{spec['freq']}.{spec['measure']}.{spec['unit']}.{spec['activity']}"
    if src == "ecb_rtd":
        return f"rtd:{spec['key']}"
    if src == "ecb_sdw":
        return f"ecb:{spec['flow']}.{spec['key']}"
    if src in ("valet_daily", "valet_monthly"):
        return f"valet:{spec['series']}"
    raise ValueError(src)


def _cond_freq(spec: dict) -> str:
    src = spec["source"]
    if src in ("ecb_sdw", "valet_daily"):
        return "D"
    if src == "valet_monthly":
        return "M"
    if src == "ecb_rtd":
        return spec["key"].split(".")[0]
    return spec["freq"]


_PERIOD_RE = {"M": r"^\d{4}-\d{2}$", "Q": r"^\d{4}-Q[1-4]$"}


def assert_regular_index(df: pd.DataFrame, freq: str) -> None:
    """Every panel index must be unique, in one label format and without gaps."""
    import re

    idx = list(df.index)
    if len(set(idx)) != len(idx):
        raise ValueError("panel index has duplicate periods")
    pat = re.compile(_PERIOD_RE[freq])
    bad = [p for p in idx if not pat.match(str(p))]
    if bad:
        raise ValueError(f"panel index has labels in the wrong format: {bad[:5]}")
    pi = pd.PeriodIndex([p.replace("-Q", "Q") for p in idx], freq=freq)
    expected = pd.period_range(pi[0], pi[-1], freq=freq)
    if len(expected) != len(pi) or (expected != pi).any():
        raise ValueError("panel index has gaps or is unsorted")


def _regularise(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Reindex to the full period range between first and last label and assert regularity."""
    if df.empty:
        return df
    pi = pd.PeriodIndex([str(p).replace("-Q", "Q") for p in df.index], freq=freq)
    full = pd.period_range(pi.min(), pi.max(), freq=freq)
    labels = [f"{p.year}-{p.month:02d}" if freq == "M" else f"{p.year}-Q{p.quarter}" for p in full]
    df = df.copy()
    df.index = [f"{p.year}-{p.month:02d}" if freq == "M" else f"{p.year}-Q{p.quarter}" for p in pi]
    out = df.reindex(labels)
    out.index.name = "ref_period"
    assert_regular_index(out, freq)
    return out


def build_panel(
    cfg: Config,
    table: pd.DataFrame,
    econ: str,
    target: str,
    origin: dt.date,
    input_mode: str = "realtime",
    revised_as_of: dt.date | None = None,
) -> Panel | None:
    if input_mode not in ("realtime", "revised"):
        raise ValueError(f"unknown input_mode {input_mode!r}")
    if input_mode == "revised" and revised_as_of is None:
        raise ValueError("revised input mode needs a pinned revised_as_of date")
    tcfg = cfg.targets[econ][target]
    h = tg.history(cfg, table, econ, target, origin)
    if h is None:
        return None
    levels, res = h
    levels = levels.dropna()
    if input_mode == "revised":
        # same resolved series, latest pinned vintage, cut to the periods visible at the origin
        rev = as_of(table, [res.series_id], revised_as_of, strict=False)[res.series_id]
        levels = rev.reindex(levels.index).dropna()
    if len(levels) < 3:
        return None
    kind = tcfg.transform
    try:
        ttr = transform(levels, kind)
    except ValueError:
        return None
    specs = cfg.conditioning.get(econ, [])
    sids = [_cond_sid(s, econ) for s in specs]
    raw = as_of(table, sids, origin)
    if input_mode == "revised":
        rev_raw = as_of(table, sids, revised_as_of, strict=False)
        raw = {sid: rev_raw[sid].reindex(raw[sid].index).dropna() for sid in sids}
    monthly, quarterly, monthly_lv, quarterly_lv, dropped = {}, {}, {}, {}, []
    for spec, sid in zip(specs, sids, strict=True):
        s = raw[sid].dropna()
        if s.empty:
            dropped.append(f"{sid}: no data at origin")
            continue
        fq = _cond_freq(spec)
        if fq == "D":
            if spec.get("agg", "mean") == "ffill_eom":
                s = monthly_eom_ffill_from_daily(s, origin)
            else:
                s = monthly_mean_from_daily(s)
                cur = origin.strftime("%Y-%m")
                s = s[s.index < cur]  # drop the incomplete current month
            fq = "M"
        try:
            tr = transform(s, spec["transform"])
        except ValueError as e:
            dropped.append(f"{sid}: {e}")
            continue
        if fq == "M":
            monthly[sid] = tr
            monthly_lv[sid] = s
        else:
            quarterly[sid] = tr
            quarterly_lv[sid] = s
    m = pd.DataFrame(monthly)
    q = pd.DataFrame(quarterly)
    m_lv = pd.DataFrame(monthly_lv)
    q_lv = pd.DataFrame(quarterly_lv)

    def _prepend(target: pd.Series, block: pd.DataFrame) -> pd.DataFrame:
        t = target.rename(res.series_id).to_frame()
        out = t if block.empty else pd.concat([t, block], axis=1)
        return out.loc[ttr.index[0] :]

    if tcfg.freq == "M":
        m = _prepend(ttr, m)
        m_lv = _prepend(levels, m_lv)
    else:
        q = _prepend(ttr, q)
        q_lv = _prepend(levels, q_lv)
    m = _regularise(m.sort_index(), "M")
    q = _regularise(q.sort_index(), "Q")
    m_lv = _regularise(m_lv.sort_index(), "M").reindex(m.index)[m.columns] if not m.empty else m_lv
    q_lv = _regularise(q_lv.sort_index(), "Q").reindex(q.index)[q.columns] if not q.empty else q_lv
    return Panel(
        origin,
        econ,
        target,
        res.series_id,
        res.source_role,
        tcfg.freq,
        kind,
        levels,
        ttr,
        m,
        q,
        dropped,
        input_mode,
        m_lv,
        q_lv,
    )
