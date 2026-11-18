# Task runner for foundation-forecast. Install: `uv sync --extra dev`, then `uv run just <target>`.

set shell := ["bash", "-cu"]
set windows-shell := ["bash", "-cu"]

default:
    @just --list

# Lint and format check
lint:
    uv run ruff check src tests
    uv run ruff format --check src tests

# Run the test suite
test:
    uv run pytest

# Lint, then test (CI-style)
check: lint test

# Download and normalise vintage data (Phase 2)
data:
    uv run ffcast data

# Run the historical backtest over every origin, both windows (Phase 4)
backtest:
    uv run ffcast backtest --window all

# Recompute the benchmarks at 5 stored origins and compare exactly
verify:
    uv run ffcast backtest --verify 5

# Regenerate every scoring table and the private summary (Phase 4)
score:
    uv run ffcast score

# ECB SPF comparison: matched model runs at the survey deadlines, then tables (Phase 4, Q4)
spf:
    uv run ffcast spf

# Run one live registry origin (Phase 5)
registry-run origin="":
    uv run ffcast registry-run {{origin}}
