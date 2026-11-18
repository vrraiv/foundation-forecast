"""Checks on the downloaded vintage data. They skip (visibly) when data/normalised is absent,
so a fresh clone passes; STATUS.md records whether they ran.

Two kinds of check:
1. Cross-source agreement: the same economic quantity from two independent providers
   (OECD vs DBnomics/StatCan for Canada; ECB RTD vs Eurostat for the euro area; Bank of
   Canada Valet vs OECD for CPI). Growth rates are compared because index bases differ.
2. Revision spot checks: a first-release value and a later value that are known to differ,
   three per economy, with the values pinned here.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from ffcast.data.store import NORMALISED_ROOT, as_of, read_all

pytestmark = pytest.mark.skipif(
    not any(NORMALISED_ROOT.glob("*.parquet")), reason="no normalised data (run `ffcast data`)"
)


@pytest.fixture(scope="module")
def table():
    return read_all()


def _one(table, prefix):
    ids = [s for s in table["series_id"].unique() if s.startswith(prefix)]
    assert len(ids) == 1, ids
    return ids[0]


def _growth(s):
    return s.astype(float).pct_change() * 100


def _yoy(s):
    return (s.astype(float) / s.astype(float).shift(12) - 1) * 100


# ---- 1. cross-source agreement --------------------------------------------------------------


def test_canada_gdp_oecd_edition_matches_statcan_release_growth(table):
    oe = "oecd:CA.Q.B1GQ_Q.XDC._T"
    db = "dbnomics:STATCAN/36100431/estim_24.price_1.sea_adj_1"
    origin = dt.date(2024, 12, 26)
    a, b = as_of(table, [oe, db], origin).values()
    common = a.index.intersection(b.index)[-8:]
    np.testing.assert_allclose(_growth(a)[common], _growth(b)[common], atol=5e-3)


def test_euro_area_gdp_rtd_latest_matches_eurostat_latest_growth(table):
    rt = "rtd:Q.S0.S.G_GDPM_TO_C.E"
    eu = _one(table, "eurostat:namq_10_gdp[geo=EA21.na_item=B1GQ")
    origin = dt.date(2026, 11, 19)
    a, c = as_of(table, [rt, eu], origin).values()
    common = a.index.intersection(c.index)[-8:]
    np.testing.assert_allclose(_growth(a)[common], _growth(c)[common], atol=5e-3)


def test_canada_cpi_valet_matches_oecd_yoy(table):
    v, oc = "valet:V41690973", "oecd:CA.M.CP.IX._Z"
    a = as_of(table, [v], dt.date(2026, 11, 19))[v]
    b = as_of(table, [oc], dt.date(2026, 11, 26))[oc]
    common = a.index.intersection(b.index)[-12:]
    np.testing.assert_allclose(_yoy(a)[common], _yoy(b)[common], atol=0.01)


def test_canada_headline_cpi_is_unrevised_across_recent_editions(table):
    oc = "oecd:CA.M.CP.IX._Z"
    s = table[(table["series_id"] == oc) & (table["action"] == "R")]
    recent = s[s["ref_period"] >= "2019-01"]
    # each reference period appears exactly once as an R row (first release) unless rebased;
    # a rebasing changes every period at once, so count periods with more than one R row
    counts = recent.groupby("ref_period").size()
    multi = counts[counts > 1]
    # allow rebasing vintages (all periods change together), reject isolated revisions
    if not multi.empty:
        changed_dates = (
            recent[recent["ref_period"].isin(multi.index)].groupby("vintage_date").size()
        )
        assert (changed_dates >= 0.9 * len(counts)).all(), changed_dates


# ---- 2. revision spot checks (first release differs from a later vintage) --------------------


@pytest.mark.parametrize(
    ("sid", "period", "first_origin", "first_value", "later_origin", "later_value"),
    [
        # Canada
        (
            "oecd:CA.M.UNEMP.PT_LF._T",
            "2024-02",
            dt.date(2024, 5, 26),
            5.8,
            dt.date(2025, 3, 26),
            5.9,
        ),
        (
            "dbnomics:STATCAN/36100431/estim_24.price_1.sea_adj_1",
            "2012-Q3",
            dt.date(2012, 12, 1),
            1661699.0,
            dt.date(2014, 1, 1),
            1663804.0,
        ),
        (
            "oecd:CA.M.TOVM.IX.G47",
            "2019-06",
            dt.date(2019, 9, 26),
            111.53,
            dt.date(2020, 9, 26),
            110.63,
        ),
        # Euro area
        (
            "rtd:Q.S0.S.G_GDPM_TO_C.E",
            "2025-Q1",
            dt.date(2025, 6, 5),
            3260736.18066679,
            dt.date(2026, 11, 19),
            3318714.43881293,
        ),
        (
            "rtd:M.S0.S.L_UNETO.F",
            "2024-01",
            dt.date(2024, 3, 26),
            6.43568,
            dt.date(2026, 11, 19),
            6.5,
        ),
        (
            "rtd:Q.S0.S.G_FCHI_TO_C.E",
            "2025-Q1",
            dt.date(2025, 7, 26),
            1698171.67909291,
            dt.date(2026, 11, 19),
            1736826.88337862,
        ),
    ],
)
def test_revision_spot_check(
    table, sid, period, first_origin, first_value, later_origin, later_value
):
    first = as_of(table, [sid], first_origin)[sid].get(period)
    later = as_of(table, [sid], later_origin)[sid].get(period)
    assert first is not None and later is not None
    assert first != later, "expected a revision between the two vintages"
    if first_value is not None:
        assert first == pytest.approx(first_value, rel=1e-9)
        assert later == pytest.approx(later_value, rel=1e-9)
