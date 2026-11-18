"""Naive benchmark on the transformed series: historical mean for differenced data (the
random walk in levels), with Gaussian quantiles from the historical standard deviation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..models.interface import QuantileForecast, gaussian_quantiles


class Naive:
    name = "naive"

    def __init__(self, window: int | None = None) -> None:
        self.window = window  # None = full history

    def forecast(
        self, history: pd.Series | pd.DataFrame, horizon: int, quantiles
    ) -> QuantileForecast:
        y = (
            (history.iloc[:, 0] if isinstance(history, pd.DataFrame) else history)
            .astype(float)
            .dropna()
        )
        if self.window:
            y = y.iloc[-self.window :]
        mu, sd = float(y.mean()), float(y.std(ddof=1)) if len(y) > 1 else 0.0
        mean = np.full(horizon, mu)
        return QuantileForecast(
            tuple(quantiles),
            gaussian_quantiles(mean, np.full(horizon, sd), tuple(quantiles)),
            mean,
            {"n": len(y)},
        )
