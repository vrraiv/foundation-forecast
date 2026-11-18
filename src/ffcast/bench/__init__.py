"""Classical benchmarks, re-estimated at every origin on that origin's vintage.

All benchmarks take the already-transformed, already-truncated history from `as_of` and
return quantile forecasts through the common interface. Hyperparameters are chosen by the
rules fixed in PLAN.md section 2 and configs/default.yaml, never by looking at outturns.
"""

from .ar import ARDirect
from .bvar import BVARMinnesota
from .combo import EqualWeight
from .dfm import DynamicFactorMQBench
from .naive import Naive

__all__ = ["ARDirect", "BVARMinnesota", "DynamicFactorMQBench", "EqualWeight", "Naive"]
