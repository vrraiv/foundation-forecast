"""Common forecasting interface.

forecast(history, horizon, quantiles) -> QuantileForecast

`history` is a pandas Series (univariate) or DataFrame (multivariate, target in column 0)
indexed by ref_period strings, already transformed by the caller and already restricted to
the information set of the origin (it must come from `ffcast.data.store.as_of`). Forecasters
never see dates beyond the index they are given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class QuantileForecast:
    quantiles: tuple[float, ...]
    values: np.ndarray  # shape (horizon, n_quantiles), non-decreasing along quantiles
    mean: np.ndarray | None = None
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        v = np.asarray(self.values, dtype=float)
        if v.ndim != 2 or v.shape[1] != len(self.quantiles):
            raise ValueError(
                f"values shape {v.shape} does not match {len(self.quantiles)} quantiles"
            )
        object.__setattr__(self, "values", v)

    @property
    def horizon(self) -> int:
        return self.values.shape[0]

    def median(self) -> np.ndarray:
        if 0.5 in self.quantiles:
            return self.values[:, self.quantiles.index(0.5)]
        raise ValueError("0.5 not among quantiles")

    def sorted(self) -> QuantileForecast:
        """Enforce monotone quantiles by sorting across the quantile axis (rearrangement)."""
        return QuantileForecast(
            self.quantiles,
            np.sort(self.values, axis=1),
            self.mean,
            {**self.meta, "rearranged": True},
        )

    def to_rows(self) -> list[dict]:
        return [
            {"step": h + 1, "quantile": q, "value": float(self.values[h, j])}
            for h in range(self.horizon)
            for j, q in enumerate(self.quantiles)
        ]


class Forecaster(Protocol):
    name: str

    def forecast(
        self, history: pd.Series | pd.DataFrame, horizon: int, quantiles: tuple[float, ...]
    ) -> QuantileForecast: ...


def gaussian_quantiles(
    mean: np.ndarray, sd: np.ndarray, quantiles: tuple[float, ...]
) -> np.ndarray:
    from scipy.stats import norm

    z = norm.ppf(np.asarray(quantiles))
    return np.asarray(mean)[:, None] + np.asarray(sd)[:, None] * z[None, :]
