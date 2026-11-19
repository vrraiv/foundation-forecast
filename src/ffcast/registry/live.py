"""The `live` information set of a registry run: everything public at the time of the run.

The backtest rule (`realtime` mode) dates each vintage conservatively and hides whatever is dated
on or after the origin. A live run does not need that caution against look-ahead: its snapshot is
taken, hashed and time-stamped on the run day, so nothing in it can postdate the run. `live` mode
therefore uses

  - for each target, the national `latest` series named in the config, as downloaded; where that
    series starts later than the vintage history (Canadian retail starts in 2017), earlier
    periods come from the newest vintage of the target's vintage source, rescaled to join at the
    first live period (ratio for log-difference targets, shift for difference targets), so every
    growth rate before the join is the vintage source's and every one after it the national one;
  - for each conditioning series, its newest downloaded vintage.

Implementation: a copy of the snapshot table in which vintages dated on or after the origin are
re-dated to the day before it (order preserved) and each target gets a synthetic series
`live:<econ>.<target>`, plus a copy of the config whose targets point at those series. The
ordinary panel builder and `as_of` then do the rest; no second code path builds panels."""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ..config import Config
from ..data.pipeline import EUROSTAT_GEO_DEFAULT
from ..data.sources import eurostat, valet
from ..data.store import as_of
from ..data.targets import series_id_for
from ..data.transform import transform

FAR = dt.date(9999, 1, 1)


def latest_series_ids(spec: dict, econ: str, table_sids: set[str]) -> list[str]:
    """Series ids the `latest` spec (and its fallback) may have produced, in order of preference."""
    out: list[str] = []
    src = spec["source"]
    if src == "eurostat":
        filters = dict(spec["filters"])
        geo = filters.pop("geo", EUROSTAT_GEO_DEFAULT.get(econ, "EA21"))
        out.append(eurostat.series_id(spec["dataset"], {**filters, "geo": geo}))
    elif src == "valet":
        out.append(valet.series_id(spec["series"]))
    elif src == "statcan_wds":
        out.append(f"statcan:{spec['table']}:v{spec['vector']}")
    elif src == "statcan_manual":
        out += sorted(s for s in table_sids if s.startswith(f"statcan:{spec['table']}:"))
    if spec.get("fallback"):
        out += [s for s in latest_series_ids(spec["fallback"], econ, table_sids) if s not in out]
    return out


def _newest(table: pd.DataFrame, sid: str) -> pd.Series:
    return as_of(table, [sid], FAR)[sid].dropna()


def live_levels(
    cfg: Config, table: pd.DataFrame, econ: str, target: str, sids: set[str]
) -> tuple[pd.Series | None, dict]:
    """Level series of one target for `live` mode, with a note describing how it was built."""
    t = cfg.targets[econ][target]
    note: dict = {"econ": econ, "target": target}
    if t.blocked:
        note["status"] = "blocked"
        return None, note
    live = pd.Series(dtype="float64")
    for sid in latest_series_ids(t.latest, econ, sids):
        if sid in sids:
            live = _newest(table, sid)
            if not live.empty:
                note["latest_series"] = sid
                break
    if live.empty:
        note["status"] = "no latest series in the snapshot"
        return None, note
    note.update(status="ok", live_first=str(live.index[0]), live_last=str(live.index[-1]))
    specs = []
    if t.vintages:
        specs.append(t.vintages)
        if t.vintages.get("fallback"):
            specs.append(t.vintages["fallback"])
    for spec in specs:
        if spec["source"] == "pseudo":
            continue  # a pseudo-vintage is a re-dating of the latest series itself
        vsid = series_id_for(spec, econ, t.freq, target)
        if vsid not in sids:
            continue
        vint = _newest(table, vsid)
        if vint.empty:
            continue
        t0 = live.index[0]
        common = live.index.intersection(vint.index)
        if len(common) > 2:
            try:
                a = transform(live.loc[common], t.transform)
                b = transform(vint.loc[common], t.transform)
                note["overlap_periods"] = int(len(a))
                note["overlap_max_abs_diff_transformed"] = round(float((a - b).abs().max()), 6)
            except ValueError:
                pass
        if vint.index[0] < t0 and t0 in vint.index:
            back = vint[vint.index < t0]
            if t.transform == "log_diff":
                back = back * (live.loc[t0] / vint.loc[t0])
            else:
                back = back + (live.loc[t0] - vint.loc[t0])
            live = pd.concat([back, live])
            note.update(history_from=vsid, history_periods=int(len(back)), joined_at=str(t0))
        break
    return live.sort_index(), note


def live_inputs(
    cfg: Config, table: pd.DataFrame, origin: dt.date
) -> tuple[Config, pd.DataFrame, list[dict]]:
    """(config, table, notes) such that `realtime` panels at `origin` built from them are the
    `live` panels."""
    sids = set(table["series_id"].unique())
    day_before = origin - dt.timedelta(days=1)
    t2 = table.copy()
    t2["_orig"] = pd.to_datetime(t2["vintage_date"]).dt.date
    t2 = t2.sort_values(["series_id", "_orig"], kind="stable").reset_index(drop=True)
    late = t2["_orig"] >= origin
    t2["vintage_date"] = [
        day_before if is_late else d for d, is_late in zip(t2["_orig"], late, strict=True)
    ]
    t2 = t2.drop(columns="_orig")
    notes: list[dict] = [{"vintage_rows_redated": int(late.sum())}]
    raw = cfg.model_dump()
    extra = []
    for econ in cfg.economies:
        for tname in cfg.targets[econ]:
            lv, note = live_levels(cfg, table, econ, tname, sids)
            notes.append(note)
            raw["targets"][econ][tname]["vintages"] = {"source": "live"}
            raw["targets"][econ][tname]["exclude_from_q1"] = False
            if lv is None:
                continue
            extra.append(
                pd.DataFrame(
                    {
                        "series_id": f"live:{econ}.{tname}",
                        "ref_period": lv.index.astype(str),
                        "value": lv.to_numpy(dtype=float),
                        "vintage_date": day_before,
                        "action": "R",
                        "source": "live",
                        "vintage_label": f"live@{origin.isoformat()}",
                    }
                )
            )
    if extra:
        t2 = pd.concat([t2, *[e[list(t2.columns)] for e in extra]], ignore_index=True)
    return Config(**raw), t2, notes
