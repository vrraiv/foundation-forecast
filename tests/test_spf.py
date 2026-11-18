"""ECB SPF parsing and survey-definition arithmetic on synthetic inputs."""

from __future__ import annotations

import datetime as dt
import zipfile

import numpy as np
import pandas as pd
import pytest

from ffcast.eval import spf
from ffcast.eval.spf_rounds import parse_window


def test_parse_window_phrasings():
    assert parse_window("The survey was conducted between 2 and 7 October 2026.") == (
        dt.date(2026, 10, 2),
        dt.date(2026, 10, 7),
    )
    assert parse_window("conducted between 30 June and 4 July 2025") == (
        dt.date(2025, 6, 30),
        dt.date(2025, 7, 4),
    )
    assert parse_window("conducted between 31 of March and 6 April 2016") == (
        dt.date(2016, 3, 31),
        dt.date(2016, 4, 6),
    )
    assert parse_window("The survey was conducted between 4 and 11 January.", 2017) == (
        dt.date(2017, 1, 4),
        dt.date(2017, 1, 11),
    )
    assert parse_window("The survey was conducted on 1–11 October 2021 with 58 responses") == (
        dt.date(2021, 10, 1),
        dt.date(2021, 10, 11),
    )
    assert parse_window("conducted over 4–10 April. The total", 2018) == (
        dt.date(2018, 4, 4),
        dt.date(2018, 4, 10),
    )
    assert parse_window("was conducted between 7 and 13 of January 2020; 72 responses") == (
        dt.date(2020, 1, 7),
        dt.date(2020, 1, 13),
    )
    assert parse_window("the round conducted in the first quarter of 2026") is None
    assert parse_window("between 4 and 11 January.") is None  # no year and no round year


def test_load_microdata_from_synthetic_zip(tmp_path):
    csv = (
        "INFLATION EXPECTATIONS; YEAR-ON-YEAR CHANGE IN HICP,,,\n"
        "TARGET_PERIOD,FCT_SOURCE,POINT,TN1_0\n"
        "2024,1,2.5,0\n2024,6,2.4,0\n2025Jun,1,2.1,\n2025Jun,6,,\n2029,1,2.0,\n"
        ",,,\n"
        "GROWTH EXPECTATIONS; YEAR-ON-YEAR CHANGE IN REAL GDP,,,\n"
        "TARGET_PERIOD,FCT_SOURCE,POINT,TN1_0\n"
        "2025Q1,1,1.2,\n2025,1,1.3,\n"
        ",,,\nASSUMPTIONS,,,\nTARGET_PERIOD,FCT_SOURCE,IR,OIL\n2024,1,3.5,80\n"
    )
    z = tmp_path / "spf.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("2024Q3.csv", "﻿" + csv)
    m = spf.load_microdata(z)
    assert len(m) == 6  # the empty POINT and the ASSUMPTIONS block are dropped
    assert set(m["variable"]) == {"HICP", "RGDP"}
    tt = dict(zip(m["target"], m["target_type"], strict=False))
    assert (
        tt["2024"] == "calendar"
        and tt["2025Jun"] == "rolling_m"
        and tt["2025Q1"] == "rolling_q"
        and tt["2029"] == "longterm"
    )


def test_survey_definitions_on_level_paths():
    idx = [f"{y}-{mo:02d}" for y in range(2023, 2027) for mo in range(1, 13)]
    path = pd.Series(100 * 1.02 ** (np.arange(len(idx)) / 12), index=idx)
    assert spf.survey_value(path, "HICP", "2025", "M") == pytest.approx(2.0, abs=1e-9)
    assert spf.survey_value(path, "HICP", "2025Jun", "M") == pytest.approx(2.0, abs=1e-9)
    assert spf.survey_value(path, "HICP", "2027", "M") is None  # incomplete year
    u = pd.Series(np.linspace(6, 7, len(idx)), index=idx)
    assert spf.survey_value(u, "UNEM", "2025", "M") == pytest.approx(
        u[[p.startswith("2025") for p in idx]].mean()
    )
    assert spf.survey_value(u, "UNEM", "2025May", "M") == pytest.approx(float(u["2025-05"]))
    qidx = [f"{y}-Q{q}" for y in range(2023, 2028) for q in range(1, 5)]
    q = pd.Series(100 * 1.01 ** np.arange(len(qidx)), index=qidx)
    assert spf.survey_value(q, "RGDP", "2025Q1", "Q") == pytest.approx(100 * (1.01**4 - 1))
    assert spf.survey_value(q, "RGDP", "2025", "Q") == pytest.approx(100 * (1.01**4 - 1))
    # level path from a point path in log-differences
    lp = spf.level_path(
        pd.Series({"2024-04": 100.0, "2024-05": 101.0}), np.array([1.0, 1.0]), "log_diff", "M"
    )
    assert list(lp.index) == ["2024-04", "2024-05", "2024-06", "2024-07"]
    assert lp["2024-07"] == pytest.approx(101.0 * np.exp(0.02))
    assert spf._horizon("M", "2024-05", 2024) == 31 and spf._horizon("Q", "2024-Q1", 2024) == 11


def test_fixed_event_rows_and_within_transform():
    df = pd.DataFrame(
        {
            "forecaster": [1, 1, 1, 2, 2],
            "variable": ["HICP"] * 5,
            "target": ["2025"] * 5,
            "round": ["2024Q1", "2024Q2", "2024Q3", "2024Q1", "2024Q2"],
            "point": [2.0, 2.2, 2.1, 1.8, 1.9],
            "first_release": [2.3] * 5,
        }
    )
    fe = spf.fixed_event_rows(df, "forecaster", "first_release")
    assert len(fe) == 3
    r1 = fe[fe["id"] == 1].sort_values("round")
    assert r1["revision"].tolist() == pytest.approx([0.2, -0.1]) and r1[
        "error"
    ].tolist() == pytest.approx([0.1, 0.2])
    w = spf._within(fe, "id")
    assert abs(w.groupby("id")["error"].mean()).max() < 1e-12
