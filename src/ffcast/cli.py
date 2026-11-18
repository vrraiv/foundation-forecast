"""Command-line entry points. Phase 1 stubs; later phases fill them in."""

from __future__ import annotations

import typer

app = typer.Typer(no_args_is_help=True, help="foundation-forecast tasks")


@app.command()
def data() -> None:
    """Download and normalise vintage data into data/raw and data/normalised."""
    from .data.pipeline import run_data

    rep = run_data()
    for sid, meta in sorted(rep.series.items()):
        typer.echo(f"{sid}: {meta['rows']} rows  sha256 {meta['sha256'][:12]}")
    if rep.problems:
        typer.echo(
            f"\n{len(rep.problems)} problem(s) recorded in data/normalised/problems.txt:", err=True
        )
        for p in rep.problems:
            typer.echo(f"  - {p}", err=True)


@app.command()
def quality() -> None:
    """Validate the RTD rebuild against ECB bulk files and write docs/data_quality.md."""
    from pathlib import Path

    from .config import load_config
    from .data import quality as q
    from .data import validate
    from .data.raw import RAW_ROOT
    from .data.store import NORMALISED_ROOT, read_all

    cfg = load_config()
    table = read_all()
    if table.empty:
        typer.echo("no normalised data; run `ffcast data` first", err=True)
        raise typer.Exit(code=2)
    bulk = None
    zips = sorted(RAW_ROOT.glob("rtd-bulk/*/quarterly.zip"))
    if zips:
        res = []
        for key in validate.BULK_COLUMN_PATTERNS:
            if f"rtd:{key}" in set(table["series_id"]):
                res += validate.compare_key(table, key, zips[-1])
        bulk = validate.summarise(res)
        bad = [r for r in res if not r.ok]
        typer.echo(
            f"bulk validation: {len(res)} vintage files compared, {len(bad)} with differences"
        )
        for r in bad[:10]:
            typer.echo(
                f"  {r.key} {r.bulk_file}: bulk {r.n_bulk} rebuilt {r.n_rebuilt} "
                f"match {r.n_match}; e.g. {r.mismatches[:3]}"
            )
    problems_file = NORMALISED_ROOT / "problems.txt"
    problems = (
        problems_file.read_text(encoding="utf-8").splitlines() if problems_file.exists() else []
    )
    text = q.build_report(table, cfg, bulk, problems)
    out = Path(__file__).resolve().parents[2] / "docs" / "data_quality.md"
    q.write_report(text, out)
    typer.echo(f"wrote {out}")


@app.command()
def smoke(
    origin: str = typer.Option("2024-06-25", help="Origin date YYYY-MM-DD"),
    models: str = typer.Option("", help="Comma-separated foundation models to run (default all)"),
    skip_bench: bool = typer.Option(False, help="Skip the classical benchmarks"),
) -> None:
    """Phase 3 smoke test: every model and benchmark forecasts every target at one origin."""
    import datetime as dt
    from pathlib import Path

    from .models.smoke import run_smoke

    mlist = [m for m in models.split(",") if m] or None
    suffix = "_fm" if skip_bench else ""
    out = Path(__file__).resolve().parents[2] / "data" / "smoke" / f"smoke_{origin}{suffix}.csv"
    df = run_smoke(
        dt.date.fromisoformat(origin), models=mlist, out_path=out, run_bench=not skip_bench
    )
    with_pd_options = df.to_string(index=False, max_colwidth=60)
    typer.echo(with_pd_options)
    bad = df[~df["ok"] & (df["variant"] != "wall")]
    typer.echo(f"\n{len(df)} rows, {len(bad)} failed checks; written to {out}")


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
