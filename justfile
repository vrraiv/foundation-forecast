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

# Run the historical backtest (Phase 4)
backtest:
    uv run ffcast backtest

# Regenerate scoring tables (Phase 4)
score:
    uv run ffcast score

# Run one live registry origin (Phase 5)
registry-run origin="":
    uv run ffcast registry-run {{origin}}
