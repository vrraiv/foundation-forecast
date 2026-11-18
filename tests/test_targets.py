"""Resolver and outturn rules on synthetic vintages."""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ffcast.config import load_config
from ffcast.data import pseudo
from ffcast.data.store import snapshots_to_changelog
from ffcast.data.targets import history, outturn, resolve


def _snaps(sid, source, snaps):
    return snapshots_to_changelog(
        [(d, d.isoformat(), pd.Series(v, dtype=float)) for d, v in snaps], sid, source
    )


def test_primary_then_fallback_by_vintage_availability():
    cfg = load_config()
    # CA gdp: primary dbnomics (statcan_rt mapping), fallback oecd
    prim = "dbnomics:STATCAN/36100431/estim_24.price_1.sea_adj_1"
    fb = "oecd:CA.Q.B1GQ_Q.XDC._T"
    t = pd.concat(
        [
            _snaps(
                fb,
                "oecd",
                [
                    (dt.date(2011, 1, 24), {"2009-Q3": 1.0}),
                    (dt.date(2013, 1, 24), {"2009-Q3": 1.0, "2012-Q3": 2.0}),
                ],
            ),
            _snaps(prim, "dbnomics", [(dt.date(2012, 11, 30), {"2012-Q3": 2.1})]),
        ],
        ignore_index=True,
    )
    r = resolve(cfg, t, "CA", "gdp", dt.date(2011, 1, 25))
    assert r.series_id == fb and r.source_role == "fallback"
    r = resolve(cfg, t, "CA", "gdp", dt.date(2012, 12, 25))
    assert r.series_id == prim and r.source_role == "primary"
    h, r2 = history(cfg, t, "CA", "gdp", dt.date(2012, 12, 25))
    assert h.to_dict() == {"2012-Q3": 2.1}


def test_outturn_first_release_and_revised_from_same_source():
    sid = "s"
    t = _snaps(
        sid,
        "test",
        [
            (dt.date(2020, 2, 24), {"2020-01": 1.0}),
            (dt.date(2020, 6, 24), {"2020-01": 1.2}),
            (dt.date(2021, 6, 24), {"2020-01": 1.5}),
        ],
    )
    o = outturn(t, sid, "2020-01", months_after=12)
    assert o.first_release == 1.0 and o.first_release_date == dt.date(2020, 2, 24)
    # 12 months after 2020-02-24 is 2021-02-24: the 2020-06 vintage is the latest visible
    assert o.revised_12m == 1.2 and o.revised_12m_date == dt.date(2021, 2, 24)
    assert outturn(t, sid, "2030-01").first_release is None


def test_pseudo_vintage_dates_are_eve_of_next_origin_and_never_after_snapshot():
    snap = pd.Series({"2024-01": 100.0, "2024-02": 101.0, "2026-10": 120.0})
    tab = pseudo.build(
        snap, "valet:X", months_after=1, day_of_month=25, available_on=dt.date(2026, 11, 18)
    )
    d = dict(zip(tab["ref_period"], tab["vintage_date"], strict=True))
    assert d["2024-01"] == dt.date(2024, 2, 24)
    assert d["2024-02"] == dt.date(2024, 3, 24)
    assert d["2026-10"] == dt.date(2026, 11, 18)  # capped at the snapshot date
    assert set(tab["series_id"]) == {"pseudo:valet:X"}
