"""Load and validate the single configuration file."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "default.yaml"


class Origins(BaseModel):
    day_of_month: int = Field(ge=1, le=28)
    strict_before: bool
    first: str
    extension_first: str
    min_history_years: int


class Target(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    freq: Literal["M", "Q"]
    vintages: dict[str, Any] | None
    latest: dict[str, Any]
    transform: Literal["log_diff", "diff"]
    exclude_from_q1: bool = False
    blocked: str | None = None


class FoundationModel(BaseModel):
    hf_id: str
    revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    weights_date: str
    training_cutoff: str | None = None  # YYYY-MM from the model card; None when not stated
    licence: str
    env: str
    variants: list[Literal["univariate", "multivariate"]]


class Config(BaseModel):
    economies: list[str]
    origins: Origins
    horizons: dict[Literal["M", "Q"], list[int]]
    outturns: list[str]
    transforms: dict[str, str]
    exclusion_windows: dict[str, list[str]]
    vintage_sources: dict[str, Any]
    targets: dict[str, dict[str, Target]]
    conditioning: dict[str, list[dict[str, Any]]]
    models: dict[str, Any]
    backtest: dict[str, Any]
    scoring: dict[str, Any]
    registry: dict[str, Any]

    def foundation_models(self) -> dict[str, FoundationModel]:
        return {k: FoundationModel(**v) for k, v in self.models["foundation"].items()}

    def active_foundation_models(self) -> dict[str, FoundationModel]:
        """Foundation models that default runs and the live registry use: all but the retired
        ones, whose stored results stay scorable through `foundation_models`."""
        retired = set(self.models.get("retired") or [])
        return {k: v for k, v in self.foundation_models().items() if k not in retired}


def load_config(path: Path | str = DEFAULT_CONFIG) -> Config:
    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return Config(**raw)
