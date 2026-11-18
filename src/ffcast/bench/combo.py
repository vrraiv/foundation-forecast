"""Equal-weight combination of quantile forecasts (Vincentisation: average each quantile)."""

from __future__ import annotations

import numpy as np

from ..models.interface import QuantileForecast


class EqualWeight:
    def __init__(self, name: str, members: list[str]) -> None:
        self.name = name
        self.members = members

    def combine(self, forecasts: dict[str, QuantileForecast]) -> QuantileForecast | None:
        parts = [forecasts[m] for m in self.members if m in forecasts]
        if not parts:
            return None
        qs = parts[0].quantiles
        if any(p.quantiles != qs or p.horizon != parts[0].horizon for p in parts):
            raise ValueError("members must share quantiles and horizon")
        vals = np.mean([p.values for p in parts], axis=0)
        means = [p.mean for p in parts if p.mean is not None]
        mean = np.mean(means, axis=0) if len(means) == len(parts) else None
        return QuantileForecast(
            qs, vals, mean, {"members": [m for m in self.members if m in forecasts]}
        )
