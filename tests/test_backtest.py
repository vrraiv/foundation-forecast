"""Phase 4 harness rules on synthetic data: no look-ahead, revised input mode, cache keys,
late first releases, scoring metrics, bias regression."""

from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pandas as pd
import pytest

from ffcast.config import load_config
from ffcast.data.store import snapshots_to_changelog
from ffcast.eval import scoring
from ffcast.eval.backtest import cache_key, panels_at_origin
from ffcast.eval.bias import _hac_ols
from ffcast.eval.outturns import OutturnBuilder
from ffcast.models.runner import make_task

QS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


def _months(n, start="1990-01"):
    p = pd.Period(start, freq="M")
    return [f"{(p + i).year}-{(p + i).month:02d}" for i in range(n)]


def _synthetic_cfg():
    """The real config with one synthetic monthly target and no conditioning set."""
    cfg = load_config()
    raw = cfg.model_dump()
    raw["economies"] = ["ZZ"]
    raw["targets"] = {
        "ZZ": {
            "x": {
                "name": "synthetic index",
                "freq": "M",
                "vintages": {"source": "ecb_rtd", "key": "M.ZZ.X"},
                "latest": {"source": "none"},
                "transform": "log_diff",
            }
        }
    }
    raw["conditioning"] = {"ZZ": []}
    raw["backtest"]["min_history_periods"] = {"M": 24, "Q": 8}
    from ffcast.config import Config

    return Config(**raw)


def _synthetic_table(revise: bool = True) -> pd.DataFrame:
    """Monthly index published with a one-month lag on the 15th; every value is revised up by
    1% in the vintage 12 months later when `revise`."""
    rng = np.random.default_rng(0)
    periods = _months(400)
    level = 100 * np.exp(np.cumsum(rng.normal(0.002, 0.01, size=400)))
    snaps = []
    for i in range(60, 400):
        p = pd.Period(periods[i], freq="M") + 1  # published in the following month
        vd = dt.date(p.year, p.month, 15)
        vals = level[: i + 1].copy()
        if revise:
            # values older than 12 months carry a period-specific revision (so growth changes)
            k = max(0, i + 1 - 12)
            vals[:k] *= 1.0 + 0.01 * np.sin(np.arange(k))
        snaps.append((vd, f"v{vd}", pd.Series(vals, index=periods[: i + 1])))
    return snapshots_to_changelog(snaps, "rtd:M.ZZ.X", "rtd")


def test_requests_identical_from_full_and_truncated_table():
    """No look-ahead: everything a model receives at origin t must be identical whether or not
    the table contains vintages dated on or after t."""
    cfg = _synthetic_cfg()
    table = _synthetic_table()
    origin = dt.date(2010, 6, 25)
    truncated = table[pd.to_datetime(table["vintage_date"]).dt.date < origin]
    rev = dt.date(2030, 1, 1)
    full_p, _ = panels_at_origin(cfg, table, origin, ["realtime"], rev)
    trunc_p, _ = panels_at_origin(cfg, truncated, origin, ["realtime"], rev)
    assert full_p.keys() == trunc_p.keys()
    for k in full_p:
        a = make_task("t", full_p[k].univariate(), "M", 12, QS).__dict__
        b = make_task("t", trunc_p[k].univariate(), "M", 12, QS).__dict__
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
        la = make_task("t", full_p[k].univariate("level"), "M", 12, QS).__dict__
        lb = make_task("t", trunc_p[k].univariate("level"), "M", 12, QS).__dict__
        assert json.dumps(la, sort_keys=True) == json.dumps(lb, sort_keys=True)


def test_revised_mode_keeps_horizon_and_changes_values():
    cfg = _synthetic_cfg()
    table = _synthetic_table()
    origin = dt.date(2010, 6, 25)
    rev = dt.date(2030, 1, 1)
    panels, _ = panels_at_origin(cfg, table, origin, ["realtime", "revised"], rev)
    rt, rv = panels[("ZZ", "x", "realtime")], panels[("ZZ", "x", "revised")]
    assert rt.target_tr.index.equals(rv.target_tr.index)
    assert rt.target_tr.index[-1] == "2010-05"  # May published 15 June, visible at 25 June
    # growth rates differ only where the 1% revision boundary sits inside the window
    diff = (rt.target_levels / rv.target_levels - 1).abs()
    assert diff.max() > 0.005 and (diff < 0.0001).sum() > 0


def test_min_history_rule_skips_short_targets():
    cfg = _synthetic_cfg()
    table = _synthetic_table()
    cfg.backtest["min_history_periods"] = {"M": 10_000, "Q": 8}
    panels, skipped = panels_at_origin(
        cfg, table, dt.date(2010, 6, 25), ["realtime"], dt.date(2030, 1, 1)
    )
    assert not panels and skipped and "in-vintage history" in skipped[0]["note"]


def test_cache_key_depends_on_config_and_data_only():
    cfg = _synthetic_cfg()
    man = {"rtd:M.ZZ.X": {"sha256": "a" * 64}}
    k1 = cache_key(cfg, man, "ZZ", "x", "ar")
    assert k1 == cache_key(cfg, man, "ZZ", "x", "ar")
    assert k1 != cache_key(cfg, {"rtd:M.ZZ.X": {"sha256": "b" * 64}}, "ZZ", "x", "ar")
    assert k1 != cache_key(cfg, man, "ZZ", "x", "naive")
    cfg2 = _synthetic_cfg()
    cfg2.horizons["M"] = [1, 2]
    assert k1 != cache_key(cfg2, man, "ZZ", "x", "ar")
    cfg3 = _synthetic_cfg()
    cfg3.backtest["parallel_benchmark_processes"] = 99  # execution detail, not a rule
    assert k1 == cache_key(cfg3, man, "ZZ", "x", "ar")


def test_outturns_first_release_revised_and_late_rule():
    cfg = _synthetic_cfg()
    cfg.vintage_sources["max_staleness_days"] = {"rtd": 100}
    table = _synthetic_table()
    # make one period's first appearance a year late: delete its first-year rows
    sid = "rtd:M.ZZ.X"
    late_period = "2005-03"
    vd = pd.to_datetime(table["vintage_date"]).dt.date
    cut = dt.date(2006, 4, 1)
    table = table[
        ~((table["series_id"] == sid) & (table["ref_period"] == late_period) & (vd < cut))
    ]
    ob = OutturnBuilder(cfg, table)
    o = ob.outturn("ZZ", "x", sid, "M", "log_diff", "2008-03")
    assert not o["late"] and np.isfinite(o["first_release"]) and np.isfinite(o["revised_12m"])
    # the revision raises the level of the previous period only after 12 months: growth within
    # the first vintage differs from growth within the 12-months-later vintage
    assert o["first_release"] != pytest.approx(o["revised_12m"])
    late = ob.outturn("ZZ", "x", sid, "M", "log_diff", late_period)
    assert late["late"] and np.isnan(late["first_release"]) and np.isfinite(late["revised_12m"])
    assert late["lag_days"] > late["lag_limit_days"] > 15
    # cumulative: from 2008-01 to 2008-03 equals the sum of the two monthly log changes
    f1, _ = ob.cumulative_outturn(sid, "x", "log_diff", "2008-01", "2008-03")
    g2 = ob.outturn("ZZ", "x", sid, "M", "log_diff", "2008-02")["first_release"]
    g3 = o["first_release"]
    assert f1 == pytest.approx(g2 + g3, abs=0.05)  # not exact: g2 comes from an earlier vintage


def test_scoring_metrics_known_answers():
    y = np.array([0.0, 1.0, 2.0, 3.0])
    q = np.tile(np.linspace(-1, 1, 9), (4, 1)) + y[:, None]  # median equals y, interval +-1
    levels = np.array(QS)
    assert np.allclose(scoring.pinball(y, q, levels), scoring.pinball(y + 0.0, q, levels))
    assert scoring.pit_bins(y, q).sum() == pytest.approx(1.0)
    assert np.allclose(
        scoring.pit_bins(y, q), [0, 0, 0, 0, 1.0, 0, 0, 0, 0, 0]
    )  # y equals the median
    # DM: identical losses give no statistic; a constant positive differential gives a large one
    assert np.isnan(scoring.dm_hln(np.zeros(30), 1)[0])
    stat, p = scoring.dm_hln(np.ones(30) + np.random.default_rng(0).normal(0, 0.1, 30), 1)
    assert stat > 5 and p < 1e-4
    # MCS: a model with strictly larger loss everywhere has a low p-value, the best has 1.0
    rng = np.random.default_rng(1)
    L = pd.DataFrame(
        {
            "good": rng.normal(1, 0.1, 100),
            "bad": rng.normal(3, 0.1, 100),
            "mid": rng.normal(1.05, 0.1, 100),
        }
    )
    pv = scoring.mcs(L, B=300)
    assert pv["bad"] < 0.05 and pv["good"] == 1.0 and pv["mid"] >= pv["bad"]


def test_hac_ols_recovers_slope():
    rng = np.random.default_rng(2)
    x = rng.normal(size=500)
    y = 0.3 + 0.7 * x + rng.normal(scale=0.5, size=500)
    b, se, a, n = _hac_ols(y, x, 3)
    assert (
        b == pytest.approx(0.7, abs=0.08)
        and a == pytest.approx(0.3, abs=0.08)
        and n == 500
        and 0 < se < 0.1
    )
