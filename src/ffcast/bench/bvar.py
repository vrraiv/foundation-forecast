"""Bayesian VAR with a Minnesota (normal-inverse-Wishart) prior, hyperparameters chosen by
marginal likelihood on a fixed grid at each origin (Giannone, Lenza and Primiceri, 2015).

Implementation notes
- Conjugate NIW prior implemented with dummy observations (Banbura, Giannone, Reichlin 2010):
  Minnesota tightness lambda with lag decay, sum-of-coefficients prior (mu) and
  dummy-initial-observation prior (delta). The prior mean of the own first lag is 0 for the
  transformed (stationary) data used here, which the plan's transforms guarantee.
- Marginal likelihood is the closed-form NIW expression; the grid search is over
  (lambda, mu, delta) from the config, so no hyperparameter touches outturns.
- Ragged edge: variables whose last observation is earlier than the target's are completed
  with their posterior-mean conditional forecast (iterating the VAR forward with the known
  values of the other variables held fixed), so timely observations are used, not discarded.
- Forecast quantiles: posterior predictive by simulation (parameter draws from the NIW
  posterior plus Gaussian shocks), seeded.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from scipy.special import multigammaln

from ..models.interface import QuantileForecast


def _lags(Y: np.ndarray, p: int) -> tuple[np.ndarray, np.ndarray]:
    T, n = Y.shape
    X = np.ones((T - p, 1 + n * p))
    for j in range(1, p + 1):
        X[:, 1 + (j - 1) * n : 1 + j * n] = Y[p - j : T - j]
    return X, Y[p:]


def _dummies(
    Y: np.ndarray, p: int, lam: float, mu: float, delta: float, decay: float
) -> tuple[np.ndarray, np.ndarray]:
    """Dummy observations encoding the Minnesota + SOC + DIO priors (BGR 2010 appendix)."""
    T, n = Y.shape
    # scale: residual sd of univariate AR(p) regressions on the training sample
    sig = np.empty(n)
    for i in range(n):
        y = Y[:, i]
        X, z = _lagmat1(y, p)
        beta, *_ = np.linalg.lstsq(X, z, rcond=None)
        r = z - X @ beta
        sig[i] = np.sqrt(max(r @ r / max(len(z) - X.shape[1], 1), 1e-12))
    ybar = Y[:p].mean(axis=0)
    k = 1 + n * p
    rows_y, rows_x = [], []
    # Minnesota: prior mean 0 on all lags (stationary transforms);
    # prior variance lambda^2 / (j^decay)^2 * (sig_i / sig_j)^2
    for j in range(1, p + 1):
        for i in range(n):
            yd = np.zeros(n)
            xd = np.zeros(k)
            xd[1 + (j - 1) * n + i] = (j**decay) * sig[i] / lam
            rows_y.append(yd)
            rows_x.append(xd)
    # error covariance prior: diag(sig^2), n+2 degrees of freedom
    for i in range(n):
        yd = np.zeros(n)
        yd[i] = sig[i]
        rows_y.append(yd)
        rows_x.append(np.zeros(k))
    # intercept: very loose (epsilon)
    eps = 1e-4
    rows_y.append(np.zeros(n))
    xd = np.zeros(k)
    xd[0] = eps
    rows_x.append(xd)
    # sum of coefficients
    if mu and np.isfinite(mu):
        for i in range(n):
            yd = np.zeros(n)
            yd[i] = ybar[i] / mu
            xd = np.zeros(k)
            for j in range(p):
                xd[1 + j * n + i] = ybar[i] / mu
            rows_y.append(yd)
            rows_x.append(xd)
    # dummy initial observation
    if delta and np.isfinite(delta):
        yd = ybar / delta
        xd = np.zeros(k)
        xd[0] = 1.0 / delta
        for j in range(p):
            xd[1 + j * n : 1 + (j + 1) * n] = ybar / delta
        rows_y.append(yd)
        rows_x.append(xd)
    return np.asarray(rows_y), np.asarray(rows_x)


def _lagmat1(y: np.ndarray, p: int) -> tuple[np.ndarray, np.ndarray]:
    T = len(y)
    X = np.ones((T - p, 1 + p))
    for j in range(1, p + 1):
        X[:, j] = y[p - j : T - j]
    return X, y[p:]


def _niw_posterior(X: np.ndarray, Y: np.ndarray, Xd: np.ndarray, Yd: np.ndarray):
    Xs = np.vstack([X, Xd])
    Ys = np.vstack([Y, Yd])
    XtX = Xs.T @ Xs
    XtX_inv = np.linalg.pinv(XtX)
    B = XtX_inv @ Xs.T @ Ys
    E = Ys - Xs @ B
    S = E.T @ E
    T_star = Xs.shape[0]
    nu = T_star - Xs.shape[1]
    return B, S, XtX_inv, nu


def _log_ml(X: np.ndarray, Y: np.ndarray, Xd: np.ndarray, Yd: np.ndarray) -> float:
    """log p(Y | prior) = log p(Y, Yd) - log p(Yd) for the conjugate NIW with dummies."""
    n = Y.shape[1]

    def _lp(Xa, Ya):
        k = Xa.shape[1]
        T = Xa.shape[0]
        XtX = Xa.T @ Xa
        B = np.linalg.pinv(XtX) @ Xa.T @ Ya
        E = Ya - Xa @ B
        S = E.T @ E + 1e-8 * np.eye(n)
        nu = T - k
        if nu <= n - 1:
            return -np.inf
        sign, logdet_xtx = np.linalg.slogdet(XtX + 1e-10 * np.eye(k))
        sign2, logdet_s = np.linalg.slogdet(S)
        return (
            -0.5 * n * logdet_xtx
            - 0.5 * nu * logdet_s
            + multigammaln(nu / 2.0, n)
            - 0.5 * n * T * np.log(np.pi)
        )

    return float(_lp(np.vstack([X, Xd]), np.vstack([Y, Yd])) - _lp(Xd, Yd))


class BVARMinnesota:
    name = "bvar"

    def __init__(
        self,
        lags: int,
        lambda_grid,
        soc_grid,
        dio_grid,
        decay: float = 1.0,
        draws: int = 500,
        seed: int = 0,
        max_vars: int = 12,
    ) -> None:
        self.p = lags
        self.lambda_grid = list(lambda_grid)
        self.soc_grid = list(soc_grid)
        self.dio_grid = list(dio_grid)
        self.decay = decay
        self.draws = draws
        self.seed = seed
        self.max_vars = max_vars

    def _complete_ragged_edge(self, df: pd.DataFrame, B: np.ndarray) -> np.ndarray:
        """Fill trailing NaNs column by column with the VAR's own mean forecast conditional on the
        observed values of the other columns at the same date (iterated forward)."""
        Y = df.to_numpy(dtype=float).copy()
        p = self.p
        # interior gaps inside the first p rows cannot be forecast; carry values forward/back
        head = pd.DataFrame(Y[:p]).ffill().bfill().to_numpy()
        Y[:p] = head
        for t in range(p, Y.shape[0]):
            if not np.isnan(Y[t]).any():
                continue
            x = np.concatenate([[1.0], *[Y[t - j] for j in range(1, p + 1)]])
            pred = x @ B
            miss = np.isnan(Y[t])
            Y[t, miss] = pred[miss]
        return Y

    def forecast(self, history: pd.DataFrame, horizon: int, quantiles) -> QuantileForecast:
        df = history.astype(float).copy()
        if df.shape[1] > self.max_vars:
            df = df.iloc[:, : self.max_vars]
        # training sample: rows with all variables observed (the balanced part); the ragged edge
        # is completed afterwards with the estimated model
        full = df.dropna()
        min_rows = 10 * (1 + df.shape[1] * self.p)
        # If the balanced sample is too short, drop the column with the most gaps (never the
        # target) until it is long enough. Deterministic, depends only on the origin's vintage.
        while len(full) < min_rows and df.shape[1] > 1:
            gaps = df.iloc[:, 1:].isna().sum()
            df = df.drop(columns=[gaps.idxmax()])
            full = df.dropna()
            min_rows = 10 * (1 + df.shape[1] * self.p)
        if len(full) < 3 * (1 + self.p):
            raise ValueError("not enough balanced observations for the BVAR")
        first_full = full.index[0]
        df = df.loc[first_full:]
        Y = full.to_numpy()
        X, Yt = _lags(Y, self.p)
        best = None
        for lam, mu, delta in itertools.product(self.lambda_grid, self.soc_grid, self.dio_grid):
            Yd, Xd = _dummies(Y, self.p, lam, mu, delta, self.decay)
            lml = _log_ml(X, Yt, Xd, Yd)
            if best is None or lml > best[0]:
                best = (lml, lam, mu, delta, Xd, Yd)
        lml, lam, mu, delta, Xd, Yd = best
        B, S, XtX_inv, nu = _niw_posterior(X, Yt, Xd, Yd)
        Yfull = self._complete_ragged_edge(df, B)
        n = Yfull.shape[1]
        rng = np.random.default_rng(self.seed)
        sims = np.empty((self.draws, horizon))
        for d in range(self.draws):
            Sigma = _inv_wishart(rng, S, max(nu, n + 2))
            Bd = (
                B
                + np.linalg.cholesky(XtX_inv + 1e-12 * np.eye(XtX_inv.shape[0]))
                @ rng.standard_normal(B.shape)
                @ np.linalg.cholesky(Sigma).T
            )
            hist = Yfull.copy()
            path = []
            L = np.linalg.cholesky(Sigma)
            for _h in range(horizon):
                x = np.concatenate([[1.0], *[hist[-j] for j in range(1, self.p + 1)]])
                ynew = x @ Bd + L @ rng.standard_normal(n)
                hist = np.vstack([hist, ynew])
                path.append(ynew[0])
            sims[d] = path
        if not np.isfinite(sims).all():
            raise ValueError("BVAR simulation produced non-finite values")
        qs = tuple(quantiles)
        q = np.quantile(sims, qs, axis=0).T
        return QuantileForecast(
            qs,
            q,
            sims.mean(axis=0),
            {
                "lambda": lam,
                "soc": mu,
                "dio": delta,
                "log_ml": lml,
                "n": len(full),
                "vars": list(df.columns),
            },
        )


def _inv_wishart(rng: np.random.Generator, S: np.ndarray, nu: int) -> np.ndarray:
    n = S.shape[0]
    S_inv = np.linalg.pinv(S)
    L = np.linalg.cholesky(S_inv + 1e-10 * np.eye(n))
    Z = rng.standard_normal((int(nu), n)) @ L.T
    W = Z.T @ Z
    return np.linalg.pinv(W)
