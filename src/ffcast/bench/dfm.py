"""Mixed-frequency dynamic factor model via statsmodels DynamicFactorMQ.

Monthly variables (target first) form the monthly block; quarterly variables enter as
quarterly series (the statsmodels aggregation convention for flows in growth rates). The
ragged edge is handled natively by the Kalman filter. Factors, factor lag order and the
idiosyncratic AR(1) option are fixed in the config. EM estimation at each origin; quantiles
from the Gaussian forecast distribution of the target."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from ..models.interface import QuantileForecast, gaussian_quantiles


class DynamicFactorMQBench:
    name = "dfm"

    def __init__(
        self,
        factors: int = 2,
        factor_order: int = 2,
        idiosyncratic_ar1: bool = True,
        max_vars: int = 20,
        maxiter: int = 200,
    ) -> None:
        self.factors = factors
        self.factor_order = factor_order
        self.idiosyncratic_ar1 = idiosyncratic_ar1
        self.max_vars = max_vars
        self.maxiter = maxiter

    def forecast(
        self,
        monthly: pd.DataFrame,
        horizon: int,
        quantiles,
        quarterly: pd.DataFrame | None = None,
        target_is_quarterly: bool = False,
    ) -> QuantileForecast:
        from statsmodels.tsa.statespace.dynamic_factor_mq import DynamicFactorMQ

        m = monthly.astype(float).copy()
        if m.shape[1] > self.max_vars:
            m = m.iloc[:, : self.max_vars]
        m.index = pd.PeriodIndex(m.index, freq="M")
        q = None
        if quarterly is not None and not quarterly.empty:
            q = quarterly.astype(float).copy()
            q.index = pd.PeriodIndex([p.replace("-Q", "Q") for p in q.index], freq="Q")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mod = DynamicFactorMQ(
                m,
                endog_quarterly=q,
                factors=self.factors,
                factor_orders=self.factor_order,
                idiosyncratic_ar1=self.idiosyncratic_ar1,
                standardize=True,
            )
            res = mod.fit(disp=False, maxiter=self.maxiter)
            steps = horizon if not target_is_quarterly else horizon * 3
            fc = res.get_forecast(steps)
        target = (
            (q.columns[0] if target_is_quarterly else m.columns[0])
            if q is not None or not target_is_quarterly
            else m.columns[0]
        )
        mean = fc.predicted_mean[target].to_numpy()
        sd = np.maximum(fc.se_mean[target].to_numpy(dtype=float), 1e-6)
        if target_is_quarterly:
            # keep quarter-end months only
            idx = [i for i, p in enumerate(fc.predicted_mean.index) if p.month % 3 == 0][:horizon]
            mean, sd = mean[idx], sd[idx]
        qs = tuple(quantiles)
        return QuantileForecast(
            qs,
            gaussian_quantiles(mean, sd, qs),
            mean,
            {
                "loglike": float(res.llf),
                "n_monthly": m.shape[1],
                "n_quarterly": 0 if q is None else q.shape[1],
            },
        )
