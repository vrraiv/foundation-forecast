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
        em_initialization: bool = True,
    ) -> None:
        self.factors = factors
        self.factor_order = factor_order
        self.idiosyncratic_ar1 = idiosyncratic_ar1
        self.max_vars = max_vars
        self.maxiter = maxiter
        # statsmodels' EM initialisation (PCA on the panel with missing values filled) broke down
        # on panels with long leading stretches where the target is unobserved and on columns
        # with very few observations (2026-11-18, 52 of 5,200 cells); the option is in config.
        self.em_initialization = em_initialization

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
            res = mod.fit(
                disp=False, maxiter=self.maxiter, em_initialization=self.em_initialization
            )
            # Steps refer to the periods after the target's last observation; the panel may
            # extend beyond it (ragged edge), in which case the first steps are in-sample
            # predictions of the missing target values from the Kalman smoother/filter.
            if target_is_quarterly:
                target = q.columns[0]
                last_obs = q[target].dropna().index[-1]
                start_p = (last_obs + 1).asfreq("M", how="end")
                n_steps = horizon * 3
            else:
                target = m.columns[0]
                last_obs = m[target].dropna().index[-1]
                start_p = last_obs + 1
                n_steps = horizon
            end_p = start_p + n_steps - 1
            # 'smoothed' uses every observation in the panel (incl. indicators observed
            # after the target's last value) for the in-sample part; the out-of-sample part is
            # the ordinary forecast
            pred = res.get_prediction(start=start_p, end=end_p, information_set="smoothed")
        mean_all = pred.predicted_mean[target]
        se_all = pred.se_mean[target]
        if target_is_quarterly:
            keep = [p for p in mean_all.index if p.month % 3 == 0][:horizon]
            mean = mean_all.loc[keep].to_numpy(dtype=float)
            sd = np.maximum(se_all.loc[keep].to_numpy(dtype=float), 1e-6)
        else:
            mean = mean_all.to_numpy(dtype=float)[:horizon]
            sd = np.maximum(se_all.to_numpy(dtype=float)[:horizon], 1e-6)
        if target_is_quarterly:
            p0 = mean_all.index[0].asfreq("Q")
            step1_period = f"{p0.year}-Q{p0.quarter}"
        else:
            step1_period = str(mean_all.index[0]) if len(mean_all) else None
        qs = tuple(quantiles)
        return QuantileForecast(
            qs,
            gaussian_quantiles(mean, sd, qs),
            mean,
            {
                "loglike": float(res.llf),
                "n_monthly": m.shape[1],
                "n_quarterly": 0 if q is None else q.shape[1],
                "step1_period": step1_period,
            },
        )
