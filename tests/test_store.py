"""Core no-look-ahead guarantees, tested on synthetic vintages (no data files needed)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from ffcast.data.store import (
    as_of,
    first_appearance,
    revised_view,
    snapshots_to_changelog,
    validate_table,
)

PERIODS = [f"2020-{m:02d}" for m in range(1, 13)]


def _snapshot(values: dict[str, float]) -> pd.Series:
    return pd.Series(values, dtype=float)


def _table_from_snaps(snaps, sid="s", source="test"):
    return snapshots_to_changelog([(d, d.isoformat(), _snapshot(v)) for d, v in snaps], sid, source)


def test_changelog_reconstructs_each_snapshot_exactly():
    snaps = [
        (dt.date(2021, 1, 10), {"2020-01": 1.0, "2020-02": 2.0}),
        (dt.date(2021, 2, 10), {"2020-01": 1.1, "2020-02": 2.0, "2020-03": 3.0}),
        (dt.date(2021, 3, 10), {"2020-02": 2.2, "2020-03": 3.0}),  # 2020-01 deleted
    ]
    t = _table_from_snaps(snaps)
    for d, expect in snaps:
        got = as_of(t, ["s"], d + dt.timedelta(days=1))["s"]
        assert got.to_dict() == expect
    # strictly before the first vintage: nothing
    assert as_of(t, ["s"], dt.date(2021, 1, 10))["s"].empty
    # strict means a vintage dated on the origin is not visible
    assert as_of(t, ["s"], dt.date(2021, 2, 10))["s"].to_dict() == snaps[0][1]
    assert as_of(t, ["s"], dt.date(2021, 2, 10), strict=False)["s"].to_dict() == snaps[1][1]


# Values are rounded to 4 decimals: real data carry a few decimals, and the change-log diff
# deliberately ignores float-representation noise below 1e-9 relative.
vintage_strategy = st.lists(
    st.dictionaries(
        st.sampled_from(PERIODS),
        st.floats(-100, 100, allow_nan=False).map(lambda x: round(x, 4)),
        min_size=1,
    ),
    min_size=1,
    max_size=8,
)


@settings(max_examples=200, deadline=None)
@given(vintage_strategy, st.integers(0, 400))
def test_property_no_observation_dated_on_or_after_origin(snapshots, offset):
    dates = [dt.date(2021, 1, 1) + dt.timedelta(days=7 * i) for i in range(len(snapshots))]
    t = _table_from_snaps(list(zip(dates, snapshots, strict=True)))
    origin = dt.date(2021, 1, 1) + dt.timedelta(days=offset)
    out = as_of(t, ["s"], origin)["s"]
    # every returned value must come from a row dated strictly before origin
    visible = t[(pd.to_datetime(t["vintage_date"]).dt.date < origin)]
    assert set(out.index) <= set(visible["ref_period"])
    # and must equal the last visible snapshot
    idx = [i for i, d in enumerate(dates) if d < origin]
    expect = snapshots[idx[-1]] if idx else {}
    assert out.to_dict() == expect


@settings(max_examples=100, deadline=None)
@given(vintage_strategy, vintage_strategy)
def test_future_vintages_never_change_past_as_of(past, future):
    base = dt.date(2021, 1, 1)
    past_dates = [base + dt.timedelta(days=7 * i) for i in range(len(past))]
    origin = past_dates[-1] + dt.timedelta(days=1)
    future_dates = [origin + dt.timedelta(days=7 * (i + 1)) for i in range(len(future))]
    t_past = _table_from_snaps(list(zip(past_dates, past, strict=True)))
    t_all = _table_from_snaps(list(zip(past_dates + future_dates, past + future, strict=True)))
    a = as_of(t_past, ["s"], origin)["s"]
    b = as_of(t_all, ["s"], origin)["s"]
    pd.testing.assert_series_equal(a, b)


def test_revised_view_truncates_to_periods_visible_at_origin():
    snaps = [
        (dt.date(2021, 1, 10), {"2020-01": 1.0, "2020-02": 2.0}),
        (dt.date(2021, 6, 10), {"2020-01": 1.5, "2020-02": 2.5, "2020-03": 3.5, "2020-04": 4.5}),
    ]
    t = _table_from_snaps(snaps)
    rv = revised_view(t, ["s"], dt.date(2021, 2, 1), dt.date(2021, 7, 1))["s"]
    assert rv.to_dict() == {"2020-01": 1.5, "2020-02": 2.5}


def test_first_appearance_gives_release_dates():
    snaps = [
        (dt.date(2021, 1, 10), {"2020-01": 1.0}),
        (dt.date(2021, 2, 10), {"2020-01": 1.0, "2020-02": 2.0}),
    ]
    t = _table_from_snaps(snaps)
    fa = first_appearance(t, "s")
    assert fa.to_dict() == {"2020-01": dt.date(2021, 1, 10), "2020-02": dt.date(2021, 2, 10)}


def test_validate_rejects_replace_without_value():
    bad = pd.DataFrame(
        {
            "series_id": ["s"],
            "ref_period": ["2020-01"],
            "value": [np.nan],
            "vintage_date": [dt.date(2021, 1, 1)],
            "action": ["R"],
            "source": ["t"],
            "vintage_label": ["x"],
        }
    )
    try:
        validate_table(bad)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
