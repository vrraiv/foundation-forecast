"""Assemble, at one origin, the target history and the conditioning panel from `as_of` only.

Everything a model or benchmark receives passes through here, so the information set is
defined in exactly one place:

- target: the resolved vintage series (ffcast.data.targets), transformed within the vintage;
- monthly conditioning: OECD / RTD monthly series visible at the origin, transformed;
  daily financial series aggregated to month means over days strictly before the origin
  (the current, incomplete month is dropped);
- quarterly conditioning: OECD / RTD quarterly series, transformed.

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
from ..data.transform import monthly_mean_from_daily, transform

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

    def univariate(self) -> pd.Series:
        return self.target_tr

    def multivariate(
        self, max_vars: int | None = None, min_coverage: float = 0.8, max_stale: int = 12
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
        out = block.loc[window[0] :, keep]
        return out


def _cond_sid(spec: dict, econ: str) -> str:
    src = spec["source"]
    if src == "oecd":
        return f"oecd:{econ}.{spec['freq']}.{spec['measure']}.{spec['unit']}.{spec['activity']}"
    if src == "ecb_rtd":
        return f"rtd:{spec['key']}"
    if src == "ecb_sdw":
        return f"ecb:{spec['flow']}.{spec['key']}"
    if src == "valet_daily":
        return f"valet:{spec['series']}"
    raise ValueError(src)


def _cond_kind(spec: dict) -> str:
    name = spec.get("name", "").lower()
    if spec["source"] in ("ecb_sdw", "valet_daily"):
        return "diff" if ("rate" in name or "yield" in name) else "log_diff"
    if any(w in name for w in ("rate", "confidence", "sentiment", "utilisation")):
        return "diff"
    return "log_diff"


def _cond_freq(spec: dict) -> str:
    if spec["source"] in ("ecb_sdw", "valet_daily"):
        return "D" if spec.get("series") != "M.BCPI" else "M"
    if spec["source"] == "ecb_rtd":
        return spec["key"].split(".")[0]
    return spec["freq"]


def build_panel(
    cfg: Config, table: pd.DataFrame, econ: str, target: str, origin: dt.date
) -> Panel | None:
    tcfg = cfg.targets[econ][target]
    h = tg.history(cfg, table, econ, target, origin)
    if h is None:
        return None
    levels, res = h
    levels = levels.dropna()
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
    monthly, quarterly, dropped = {}, {}, []
    for spec, sid in zip(specs, sids, strict=True):
        s = raw[sid].dropna()
        if s.empty:
            dropped.append(f"{sid}: no data at origin")
            continue
        fq = _cond_freq(spec)
        if fq == "D":
            s = monthly_mean_from_daily(s)
            cur = origin.strftime("%Y-%m")
            s = s[s.index < cur]  # drop the incomplete current month
            fq = "M"
        try:
            tr = transform(s, _cond_kind(spec))
        except ValueError as e:
            dropped.append(f"{sid}: {e}")
            continue
        if fq == "M":
            monthly[sid] = tr
        else:
            quarterly[sid] = tr
    m = pd.DataFrame(monthly)
    q = pd.DataFrame(quarterly)
    if tcfg.freq == "M":
        m = pd.concat([ttr.rename(res.series_id), m], axis=1)
        m = m.loc[ttr.index[0] :]
    else:
        q = pd.concat([ttr.rename(res.series_id), q], axis=1)
        q = q.loc[ttr.index[0] :]
    m = m.sort_index()
    q = q.sort_index()
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
    )
