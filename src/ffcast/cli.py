"""Command-line entry points. Phase 1 stubs; later phases fill them in."""

from __future__ import annotations

import typer

app = typer.Typer(no_args_is_help=True, help="foundation-forecast tasks")


@app.command()
def data() -> None:
    """Download and normalise vintage data (Phase 2)."""
    raise typer.Exit(code=_not_implemented("data"))


@app.command()
def backtest() -> None:
    """Run the historical backtest (Phase 4)."""
    raise typer.Exit(code=_not_implemented("backtest"))


@app.command()
def score() -> None:
    """Regenerate scoring tables (Phase 4)."""
    raise typer.Exit(code=_not_implemented("score"))


@app.command("registry-run")
def registry_run(origin: str = typer.Argument("", help="Origin date YYYY-MM-DD")) -> None:
    """Run one live registry origin (Phase 5)."""
    raise typer.Exit(code=_not_implemented("registry-run"))


def _not_implemented(name: str) -> int:
    typer.echo(f"{name}: not implemented yet (see STATUS.md for the current phase)", err=True)
    return 2
