# foundation-forecast

Real-time evaluation of open time-series foundation models (Chronos-2, TimesFM 2.5, TiRex,
TiRex-2, Moirai 2.0) against AR, BVAR and dynamic-factor benchmarks on Canadian and
euro-area macro data, using genuine data vintages, plus a privately held, hash-anchored
live forecast registry.

- `PLAN.md`: design brief and source of truth for scope.
- `STATUS.md`: current state, decisions, deviations from the plan.
- `docs/feasibility.md`: Phase 0 findings; `docs/probes/`: raw probe reports.
- `configs/default.yaml`: the single configuration file (targets, horizons, origins, models).
- `docs/results_backtest_2026-11-18.md`: tables of the first full backtest (disclosure approved at Gate 4); `docs/backtest.md`: design, deviations, run log.

## Setup

```
uv sync --extra dev
uv run just check      # ruff + pytest
uv run just --list     # data, backtest, score, registry-run
```

Python 3.12 via `uv`; CPU-only torch. Each foundation model runs in its own environment
(see `docs/probes/models.md`). `data/` and `registry/` are git-ignored and never committed.

## Commit guard

Run `git config core.hooksPath .githooks` once per clone. The pre-commit hook refuses
parquet, CSV, zip, log, registry and data files. The same rule is in `.gitignore`.
