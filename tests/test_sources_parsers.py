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
    table = oecd.normalise(p, rule="same_month_eve", day_of_month=25)
    sid = "oecd:CAN.M.CP.IX._Z"
    assert set(table["vintage_date"]) == {
        dt.date(2024, 1, 24),
        dt.date(2024, 2, 24),
        dt.date(2024, 3, 24),
    }
    # origin 24 Feb 2024 (strict): only the January edition is visible
    assert as_of(table, [sid], dt.date(2024, 2, 24))[sid].to_dict() == {
        "2023-10": 100.0,
        "2023-11": 101.0,
    }
    # origin 25 Feb (the origin day): February edition visible, revision to 2023-11 applied
    assert as_of(table, [sid], dt.date(2024, 2, 25))[sid].to_dict() == {
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


def test_oecd_same_month_rule_visible_at_every_origin(tmp_path: Path):
    """Under same_month_eve, edition M must be visible at the month-M origin for every month,
    including months where the origin rolls forward over a weekend."""
    from ffcast.data.sources.oecd import edition_vintage_date
    from ffcast.origins import origin_date

    for y in range(2015, 2027):
        for m in range(1, 13):
            ed = f"{y}{m:02d}"
            vd = edition_vintage_date(ed, "same_month_eve", 25)
            o = origin_date(y, m, 25)
            assert vd < o, (ed, vd, o)
            vd_c = edition_vintage_date(ed, "conservative", 25)
            assert vd_c > o, (ed, vd_c, o)


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


def test_statcan_manual_latest_selects_one_vector_by_labels(tmp_path: Path):
    import datetime as dt
    import zipfile

    import pytest

    from ffcast.data.sources import statcan

    csv = (
        '"REF_DATE","GEO","DGUID","Products and product groups","UOM","UOM_ID","SCALAR_FACTOR",'
        '"SCALAR_ID","VECTOR","COORDINATE","VALUE","STATUS","SYMBOL","TERMINATED","DECIMALS"\n'
        '"2020-01","Canada","2016A000011124","All-items","2002=100","17","units","0","v41690973","2.2","136.8","","","","1"\n'
        '"2020-01","Canada","2016A000011124","All-items excluding food and energy","2002=100","17","units","0","v41691233","2.9","131.0","","","","1"\n'
        '"2020-02","Canada","2016A000011124","All-items excluding food and energy","2002=100","17","units","0","v41691233","2.9","131.5","","","","1"\n'
        '"2020-03","Canada","2016A000011124","All-items excluding food and energy","2002=100","17","units","0","v41691233","2.9","","..","","","1"\n'
        '"2020-01","Ontario","2016A000235","All-items excluding food and energy","2002=100","17","units","0","v41691999","9.9","130.0","","","","1"\n'
    )
    z = tmp_path / "18100004-eng.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("18100004.csv", "\ufeff" + csv)
        zf.writestr("18100004_MetaData.csv", "x")
    member = {"GEO": "Canada", "Products and product groups": "All-items excluding food and energy"}
    table, sid = statcan.normalise_manual_latest(z, "18100004", member, dt.date(2026, 11, 18))
    assert sid == "statcan:18100004:v41691233"
    got = dict(zip(table["ref_period"], table["value"], strict=True))
    assert got == {"2020-01": 131.0, "2020-02": 131.5}  # '..' row dropped, Ontario excluded
    assert set(table["vintage_date"]) == {dt.date(2026, 11, 18)}
    with pytest.raises(ValueError, match="available"):
        statcan.select_member(
            statcan.read_table_zip(z), {"GEO": "Canada", "Products and product groups": "Core"}
        )
    with pytest.raises(ValueError, match="vectors"):
        statcan.select_member(
            statcan.read_table_zip(z),
            {"Products and product groups": "All-items excluding food and energy"},
        )


def test_statcan_wds_vector_json_parses_monthly_and_quarterly(tmp_path: Path):
    import json

    import pytest

    from ffcast.data.sources import statcan

    def pt(ref, val, freq, status=0, release="2026-11-16T08:30"):
        return {
            "refPer": ref,
            "value": val,
            "decimals": 1,
            "scalarFactorCode": 0,
            "symbolCode": 0,
            "statusCode": status,
            "securityLevelCode": 0,
            "releaseTime": release,
            "frequencyCode": freq,
        }

    monthly = [
        {
            "status": "SUCCESS",
            "object": {
                "responseStatusCode": 0,
                "productId": 18100256,
                "coordinate": "1.9.0.0.0.0.0.0.0.0",
                "vectorId": 1675033092,
                "vectorDataPoint": [
                    pt("2026-07-01", 158.5, 6, status=8),  # 'F' too unreliable: dropped
                    pt("2026-08-01", 158.9, 6, status=3),  # quality 'A': kept
                    pt("2026-09-01", None, 6, status=1),  # '..' not available
                    pt("2026-10-01", 159.2, 6),
                ],
            },
        }
    ]
    pm = tmp_path / "18100256_v1675033092.json"
    pm.write_text(json.dumps(monthly), encoding="utf-8")
    table, sid = statcan.normalise_wds_latest(pm, "18100256", 1675033092, dt.date(2026, 11, 18))
    assert sid == "statcan:18100256:v1675033092"
    assert dict(zip(table["ref_period"], table["value"], strict=True)) == {
        "2026-08": 158.9,
        "2026-10": 159.2,
    }
    assert set(table["vintage_date"]) == {dt.date(2026, 11, 18)}
    with pytest.raises(ValueError, match="wanted v41690973"):
        statcan.normalise_wds_latest(pm, "18100256", "v41690973", dt.date(2026, 11, 18))

    quarterly = [
        {
            "status": "SUCCESS",
            "object": {
                "productId": 36100104,
                "vectorId": 62305752,
                "vectorDataPoint": [pt("2026-01-01", 2400000, 9), pt("2026-04-01", 2410000, 9)],
            },
        }
    ]
    pq = tmp_path / "36100104_v62305752.json"
    pq.write_text(json.dumps(quarterly), encoding="utf-8")
    _, vid, ser, info = statcan.parse_vector_json(pq)
    assert vid == "62305752" and list(ser.index) == ["2026-Q1", "2026-Q2"]
    assert info["frequencyCode"] == 9 and info["last_release_time"] == "2026-11-16T08:30"
    pq.write_text(json.dumps([{"status": "FAILED", "object": "bad vector"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="not SUCCESS"):
        statcan.parse_vector_json(pq)
