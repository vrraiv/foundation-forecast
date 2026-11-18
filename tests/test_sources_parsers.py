"""Parser tests on inline synthetic files shaped like the real ones."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from ffcast.data.sources import ecb_rtd, oecd
from ffcast.data.store import as_of

RTD_CSV = """KEY,FREQ,REF_AREA,ADJUSTMENT,RT_ECON_CONCEPT,RT_DENOM,TIME_PERIOD,OBS_VALUE,OBS_STATUS,ACTION,VALID_FROM,VALID_TO
RTD.Q.S0.S.G_GDPM_TO_C.E,Q,S0,S,G_GDPM_TO_C,E,2000-Q1,100.0,A,Replace,2001-01-03T14:30:00Z,
RTD.Q.S0.S.G_GDPM_TO_C.E,Q,S0,S,G_GDPM_TO_C,E,2000-Q1,101.0,A,Replace,2001-03-07T14:30:00Z,
RTD.Q.S0.S.G_GDPM_TO_C.E,Q,S0,S,G_GDPM_TO_C,E,2000-Q2,200.0,A,Replace,2001-03-07T14:30:00Z,
RTD.Q.S0.S.G_GDPM_TO_C.E,Q,S0,S,G_GDPM_TO_C,E,1990-Q1,5.0,A,Replace,2001-01-03T14:30:00Z,
RTD.Q.S0.S.G_GDPM_TO_C.E,Q,S0,S,G_GDPM_TO_C,E,1990-Q1,,,Delete,,2002-05-02T13:30:00Z
"""


def test_rtd_changelog_as_of(tmp_path: Path):
    p = tmp_path / "rtd.csv"
    p.write_text(RTD_CSV, encoding="utf-8")
    table, problems = ecb_rtd.normalise(p)
    assert problems == []
    sid = "rtd:Q.S0.S.G_GDPM_TO_C.E"
    v1 = as_of(table, [sid], dt.date(2001, 2, 1))[sid]
    assert v1.to_dict() == {"1990-Q1": 5.0, "2000-Q1": 100.0}
    v2 = as_of(table, [sid], dt.date(2001, 4, 1))[sid]
    assert v2.to_dict() == {"1990-Q1": 5.0, "2000-Q1": 101.0, "2000-Q2": 200.0}
    v3 = as_of(table, [sid], dt.date(2002, 6, 1))[sid]
    assert v3.to_dict() == {"2000-Q1": 101.0, "2000-Q2": 200.0}  # 1990-Q1 deleted
    # same-day strictness: the 2001-03-07 vintage is not visible at an origin on 2001-03-07
    assert as_of(table, [sid], dt.date(2001, 3, 7))[sid].to_dict() == v1.to_dict()


def test_rtd_replace_without_date_is_a_problem_not_a_guess(tmp_path: Path):
    bad = RTD_CSV + "RTD.Q.S0.S.G_GDPM_TO_C.E,Q,S0,S,G_GDPM_TO_C,E,2000-Q3,300.0,A,Replace,,\n"
    p = tmp_path / "rtd.csv"
    p.write_text(bad, encoding="utf-8")
    table, problems = ecb_rtd.normalise(p)
    assert len(problems) == 1 and "without VALID_FROM" in problems[0]
    assert "2000-Q3" not in set(table["ref_period"])


OECD_CSV = """DATAFLOW,REF_AREA,FREQ,MEASURE,UNIT_MEASURE,ACTIVITY,EDITION,TIME_PERIOD,OBS_VALUE,OBS_STATUS,UNIT_MULT,DECIMALS,BASE_PER
X,CAN,M,CP,IX,_Z,202401,2023-10,100.0,A,0,0,2015
X,CAN,M,CP,IX,_Z,202401,2023-11,101.0,A,0,0,2015
X,CAN,M,CP,IX,_Z,202402,2023-10,100.0,A,0,0,2015
X,CAN,M,CP,IX,_Z,202402,2023-11,101.5,A,0,0,2015
X,CAN,M,CP,IX,_Z,202402,2023-12,102.0,A,0,0,2015
X,CAN,M,CP,IX,_Z,202403,2023-11,101.5,A,0,0,2015
X,CAN,M,CP,IX,_Z,202403,2023-12,102.0,A,0,0,2015
X,CAN,M,CP,IX,_Z,202403,2024-01,103.0,A,0,0,2015
"""


def test_oecd_editions_to_changelog_same_month_rule(tmp_path: Path):
    p = tmp_path / "oecd.csv"
    p.write_text(OECD_CSV, encoding="utf-8")
    table = oecd.normalise(p, rule="checked_same_month", day_of_month=25)
    sid = "oecd:CAN.M.CP.IX._Z"
    assert set(table["vintage_date"]) == {
        dt.date(2024, 1, 25),
        dt.date(2024, 2, 25),
        dt.date(2024, 3, 25),
    }
    # origin 25 Feb 2024 (strict): only the January edition is visible
    assert as_of(table, [sid], dt.date(2024, 2, 25))[sid].to_dict() == {
        "2023-10": 100.0,
        "2023-11": 101.0,
    }
    # origin 26 Feb: February edition visible, revision to 2023-11 applied
    assert as_of(table, [sid], dt.date(2024, 2, 26))[sid].to_dict() == {
        "2023-10": 100.0,
        "2023-11": 101.5,
        "2023-12": 102.0,
    }
    # March edition dropped 2023-10: it must disappear, not persist from an older edition
    assert as_of(table, [sid], dt.date(2024, 4, 1))[sid].to_dict() == {
        "2023-11": 101.5,
        "2023-12": 102.0,
        "2024-01": 103.0,
    }


def test_oecd_conservative_rule_shifts_to_next_month(tmp_path: Path):
    p = tmp_path / "oecd.csv"
    p.write_text(OECD_CSV, encoding="utf-8")
    table = oecd.normalise(p, rule="conservative", day_of_month=25)
    assert set(table["vintage_date"]) == {
        dt.date(2024, 2, 1),
        dt.date(2024, 3, 1),
        dt.date(2024, 4, 1),
    }
    sid = "oecd:CAN.M.CP.IX._Z"
    assert as_of(table, [sid], dt.date(2024, 2, 25))[sid].to_dict() == {
        "2023-10": 100.0,
        "2023-11": 101.0,
    }


def test_oecd_edition_content_check(tmp_path: Path):
    p = tmp_path / "oecd.csv"
    p.write_text(OECD_CSV, encoding="utf-8")
    chk = oecd.edition_content_check(p)
    assert chk["lag_months"].tolist() == [2, 2, 2]
