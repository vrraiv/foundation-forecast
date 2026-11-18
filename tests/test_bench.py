"""Benchmark sanity and limiting-case tests on simulated data."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ffcast.bench import ARDirect, BVARMinnesota, DynamicFactorMQBench, EqualWeight, Naive
from ffcast.bench.ar import select_lag_bic
from ffcast.bench.bvar import _dummies, _lags, _log_ml, _niw_posterior

QS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


def _ar1(n, phi, sd=1.0, seed=0, c=0.0):
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = c + phi * y[t - 1] + sd * rng.standard_normal()
    return y


def _periods(n):
    return [f"{2000 + i // 12}-{i % 12 + 1:02d}" for i in range(n)]


def test_naive_mean_and_monotone_quantiles():
    y = pd.Series(_ar1(200, 0.0), index=_periods(200))
    f = Naive().forecast(y, 6, QS)
    assert f.horizon == 6
    assert np.allclose(f.mean, y.mean())
    assert (np.diff(f.values, axis=1) >= 0).all()


def test_ar_bic_recovers_order_and_forecasts_persistence():
    y = _ar1(600, 0.8)
    assert select_lag_bic(y, 12) in (1, 2)
    s = pd.Series(y, index=_periods(600))
    f = ARDirect(12).forecast(s, 3, QS)
    # one-step forecast close to 0.8 * last value
    assert abs(f.mean[0] - 0.8 * y[-1]) < 0.5
    # uncertainty grows with horizon
    width = f.values[:, -1] - f.values[:, 0]
    assert width[2] > width[0]


def test_bvar_tight_prior_shrinks_to_zero_loose_prior_matches_ols():
    rng = np.random.default_rng(1)
    n, T, p = 2, 300, 1
    A = np.array([[0.5, 0.1], [0.0, 0.3]])
    Y = np.zeros((T, n))
    for t in range(1, T):
        Y[t] = A @ Y[t - 1] + rng.standard_normal(n)
    X, Yt = _lags(Y, p)
    ols = np.linalg.lstsq(X, Yt, rcond=None)[0]
    # loose Minnesota prior, no SOC/DIO: posterior mean ~ OLS
    Yd, Xd = _dummies(Y, p, lam=100.0, mu=np.inf, delta=np.inf, decay=1.0)
    B_loose, *_ = _niw_posterior(X, Yt, Xd, Yd)
    assert np.allclose(B_loose[1:], ols[1:], atol=0.03)
    # tight prior: lag coefficients ~ prior mean 0
    Yd, Xd = _dummies(Y, p, lam=1e-3, mu=np.inf, delta=np.inf, decay=1.0)
    B_tight, *_ = _niw_posterior(X, Yt, Xd, Yd)
    assert np.abs(B_tight[1:]).max() < 0.02
    # marginal likelihood prefers a moderate lambda over an absurdly tight one
    lml = {
        lam: _log_ml(X, Yt, *_dummies(Y, p, lam, np.inf, np.inf, 1.0)[::-1])
        for lam in (1e-3, 0.2, 100.0)
    }
    assert lml[0.2] > lml[1e-3]


def test_bvar_forecast_runs_with_ragged_edge():
    rng = np.random.default_rng(2)
    T = 240
    y1 = _ar1(T, 0.5, seed=3)
    y2 = 0.5 * y1 + rng.standard_normal(T)
    df = pd.DataFrame({"target": y1, "other": y2}, index=_periods(T))
    df.iloc[-1, 0] = np.nan  # target lags one month behind the indicator (ragged edge)
    df = df.dropna(how="all")
    m = BVARMinnesota(lags=2, lambda_grid=[0.1, 0.5], soc_grid=[1.0], dio_grid=[1.0], draws=100)
    f = m.forecast(df.iloc[:-1], 3, QS)  # balanced case
    assert f.horizon == 3 and (np.diff(f.values, axis=1) >= 0).all()
    g = m.forecast(df, 3, QS)  # with the ragged edge row
    assert g.horizon == 3 and np.isfinite(g.values).all()


def test_dfm_mixed_frequency_forecast_runs():
    rng = np.random.default_rng(4)
    T = 240
    f = _ar1(T, 0.7, seed=5)
    monthly = pd.DataFrame(
        {f"m{i}": 0.8 * f + rng.standard_normal(T) for i in range(4)}, index=_periods(T)
    )
    monthly.iloc[-1, 1:] = np.nan  # ragged edge
    qidx = [f"{2000 + i // 4}-Q{i % 4 + 1}" for i in range(T // 3)]
    quarterly = pd.DataFrame(
        {"q0": np.add.reduceat(f, np.arange(0, T, 3)) / 3 + 0.5 * rng.standard_normal(T // 3)},
        index=qidx,
    )
    bench = DynamicFactorMQBench(factors=1, factor_order=1, idiosyncratic_ar1=True, maxiter=50)
    out = bench.forecast(monthly, 3, QS, quarterly=quarterly)
    assert out.horizon == 3 and np.isfinite(out.values).all()


def test_equal_weight_combination():
    a = Naive().forecast(pd.Series(_ar1(100, 0.0), index=_periods(100)), 2, QS)
    b = Naive().forecast(pd.Series(_ar1(100, 0.0, seed=9) + 1, index=_periods(100)), 2, QS)
    c = EqualWeight("combo", ["a", "b"]).combine({"a": a, "b": b})
    assert np.allclose(c.values, (a.values + b.values) / 2)
    assert EqualWeight("combo", ["x"]).combine({"a": a}) is None


@pytest.mark.parametrize("horizon", [1, 4])
def test_ar_handles_short_quarterly_history(horizon):
    y = pd.Series(_ar1(40, 0.3), index=[f"{2000 + i // 4}-Q{i % 4 + 1}" for i in range(40)])
    f = ARDirect(4).forecast(y, horizon, QS)
    assert f.horizon == horizon and np.isfinite(f.values).all()
