"""Alignment and transformed-outturn rules on synthetic data."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest

from ffcast.bench import BVARMinnesota, DynamicFactorMQBench
from ffcast.data import pseudo
from ffcast.data.store import snapshots_to_changelog
from ffcast.data.targets import outturn_transformed
from ffcast.models.panel import assert_regular_index

QS = (0.1, 0.5, 0.9)


def _months(n, start="2000-01"):
    p = pd.Period(start, freq="M")
    return [f"{(p + i).year}-{(p + i).month:02d}" for i in range(n)]


def test_regular_index_rejects_mixed_labels_and_gaps():
    ok = pd.DataFrame({"x": [1.0, 2.0, 3.0]}, index=_months(3))
    assert_regular_index(ok, "M")
    mixed = pd.DataFrame({"x": [1.0, 2.0]}, index=["2000-01", "2000-02-01"])
    with pytest.raises(ValueError):
        assert_regular_index(mixed, "M")
    gap = pd.DataFrame({"x": [1.0, 2.0]}, index=["2000-01", "2000-03"])
    with pytest.raises(ValueError):
        assert_regular_index(gap, "M")


def test_bvar_step1_is_first_unobserved_target_period():
    rng = np.random.default_rng(0)
    n = 240
    y = np.zeros(n)
    x = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.5 * y[t - 1] + rng.standard_normal()
        x[t] = 0.8 * y[t] + 0.3 * rng.standard_normal()  # x is informative about y
    df = pd.DataFrame({"y": y, "x": x}, index=_months(n))
    ragged = df.copy()
    ragged.iloc[-1, 0] = np.nan  # x observed for the last month, y not
    m = BVARMinnesota(2, [0.2], [1.0], [1.0], 1.0, draws=200, seed=0, max_vars=12, min_balanced=72)
    f = m.forecast(ragged, 3, QS)
    assert f.meta["ragged_gap"] == 1
    assert f.meta["step1_period"] == df.index[-1]
    # conditioning on x_t (observed) must sharpen the step-1 forecast relative to no x info
    g = m.forecast(df.iloc[:-1], 3, QS)
    width_cond = f.values[0, 2] - f.values[0, 0]
    width_uncond = g.values[0, 2] - g.values[0, 0]
    assert width_cond < width_uncond


def test_dfm_step1_period_matches_target_last_plus_one():
    rng = np.random.default_rng(1)
    n = 180
    f = np.zeros(n)
    for t in range(1, n):
        f[t] = 0.7 * f[t - 1] + rng.standard_normal()
    monthly = pd.DataFrame(
        {f"m{i}": 0.8 * f + rng.standard_normal(n) for i in range(3)}, index=_months(n)
    )
    monthly.iloc[-2:, 0] = np.nan  # target lags two months behind the indicators
    out = DynamicFactorMQBench(1, 1, True, 12, 30).forecast(monthly, 3, QS)
    assert out.meta["step1_period"] == monthly.index[-2]
    assert out.horizon == 3


def test_outturn_transformed_is_invariant_to_rebasing():
    sid = "s"
    first = {"2020-01": 100.0, "2020-02": 101.0}
    rebased = {"2020-01": 50.0, "2020-02": 50.5, "2020-03": 51.0}  # same growth, new base
    t = snapshots_to_changelog(
        [
            (dt.date(2020, 3, 24), "a", pd.Series(first)),
            (dt.date(2021, 6, 24), "b", pd.Series(rebased)),
        ],
        sid,
        "test",
    )
    o = outturn_transformed(t, sid, "2020-02", "log_diff", months_after=12)
    assert o.first_release == pytest.approx(100 * np.log(101.0 / 100.0))
    assert o.revised_12m == pytest.approx(o.first_release)  # rebasing cancels within vintage


def test_pseudo_late_months_delay_january_by_one_origin():
    snap = pd.Series({"2019-01": 1.0, "2019-02": 1.0})
    tab = pseudo.build(snap, "valet:X", 1, 25, dt.date(2026, 11, 18), late_months={1: 2})
    d = dict(zip(tab["ref_period"], tab["vintage_date"], strict=True))
    assert d["2019-01"] == dt.date(2019, 3, 24)
    assert d["2019-02"] == dt.date(2019, 3, 24)
