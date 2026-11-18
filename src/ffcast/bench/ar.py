"""Direct multi-step AR(p) with p chosen by BIC on the one-step regression (p <= max_lag).

For each horizon h a separate regression y_{t+h} = c + sum_j b_j y_{t+1-j} + e is estimated
by OLS; the forecast is the fitted value at the last observation and the predictive standard
deviation is the residual standard error (Gaussian quantiles). The lag order is chosen once
per origin by BIC on the h=1 regression and reused for all horizons, so no choice depends on
anything beyond the origin's information set."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..models.interface import QuantileForecast, gaussian_quantiles


def _lagmat(y: np.ndarray, p: int, h: int) -> tuple[np.ndarray, np.ndarray]:
    """Rows t = p-1 .. T-1-h: X = [1, y_t, ..., y_{t-p+1}], target y_{t+h}."""
    T = len(y)
    rows = []
    tgt = []
    for t in range(p - 1, T - h):
        rows.append([1.0, *y[t - p + 1 : t + 1][::-1]])
        tgt.append(y[t + h])
    return np.asarray(rows), np.asarray(tgt)


def select_lag_bic(y: np.ndarray, max_lag: int, min_obs: int = 20) -> int:
    best_p, best_bic = 1, np.inf
    for p in range(1, max_lag + 1):
        X, z = _lagmat(y, p, 1)
        n = len(z)
        if n < min_obs or n <= X.shape[1]:
            break
        beta, *_ = np.linalg.lstsq(X, z, rcond=None)
        resid = z - X @ beta
        sigma2 = max(float(resid @ resid) / n, 1e-12)
        bic = n * np.log(sigma2) + X.shape[1] * np.log(n)
        if bic < best_bic:
            best_p, best_bic = p, bic
    return best_p


class ARDirect:
    name = "ar"

    def __init__(self, max_lag: int) -> None:
        self.max_lag = max_lag

    def forecast(
        self, history: pd.Series | pd.DataFrame, horizon: int, quantiles
    ) -> QuantileForecast:
        y = (
            (history.iloc[:, 0] if isinstance(history, pd.DataFrame) else history)
            .astype(float)
            .dropna()
            .to_numpy()
        )
        p = select_lag_bic(y, self.max_lag)
        means, sds = [], []
        for h in range(1, horizon + 1):
            X, z = _lagmat(y, p, h)
            if len(z) <= X.shape[1] + 2:
                means.append(float(np.mean(y)))
                sds.append(float(np.std(y, ddof=1)))
                continue
            beta, *_ = np.linalg.lstsq(X, z, rcond=None)
            resid = z - X @ beta
            dof = len(z) - X.shape[1]
            sd = float(np.sqrt(resid @ resid / dof))
            x_last = np.array([1.0, *y[-p:][::-1]])
            means.append(float(x_last @ beta))
            sds.append(sd)
        mean = np.asarray(means)
        q = gaussian_quantiles(mean, np.asarray(sds), tuple(quantiles))
        return QuantileForecast(tuple(quantiles), q, mean, {"p": p, "n": len(y)})
