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
    import subprocess
    import sys
    from pathlib import Path

    from .models import lean

    dt.date.fromisoformat(origin)  # validate
    root = Path(__file__).resolve().parents[2]
    suffix = "_fm" if skip_bench else ""
    workdir = root / "data" / "smoke" / f"{origin}{suffix}"
    out = root / "data" / "smoke" / f"smoke_{origin}{suffix}.csv"
    # stage 1 (heavy, exits): panels, benchmarks, worker request files
    r1 = subprocess.run(
        [
            sys.executable,
            "-m",
            "ffcast.models.smoke",
            "stage1",
            origin,
            str(workdir),
            models,
            "0" if skip_bench else "1",
        ],
        cwd=str(root),
    )
    if r1.returncode != 0:
        raise typer.Exit(code=r1.returncode)
    # stage 2 (this lean process): workers one at a time
    status = lean.run_all(workdir / "requests", workdir / "responses")
    for k, v in status.items():
        typer.echo(f"worker {k}: {'ok' if v == 'ok' else 'FAILED: ' + v.splitlines()[-1][:160]}")
    # stage 3 (heavy): checks and tables
    r3 = subprocess.run(
        [sys.executable, "-m", "ffcast.models.smoke", "stage3", str(workdir), str(out)],
        cwd=str(root),
    )
    raise typer.Exit(code=r3.returncode)


@app.command()
def backtest(
    window: str = typer.Option("primary", help="primary | extension | all"),
    first: str = typer.Option("", help="First origin YYYY-MM-DD (overrides the window start)"),
    last: str = typer.Option("", help="Last origin YYYY-MM-DD (overrides the window end)"),
    models: str = typer.Option("", help="Comma-separated foundation models (default all)"),
    modes: str = typer.Option("", help="Comma-separated input modes (default from config)"),
    skip_bench: bool = typer.Option(False, help="Do not run the classical benchmarks"),
    skip_fm: bool = typer.Option(False, help="Do not run the foundation models"),
    processes: int = typer.Option(0, help="Benchmark processes (default from config)"),
    force: bool = typer.Option(False, help="Recompute even when the cache key matches"),
    verify: int = typer.Option(
        0, help="Recompute benchmarks at N stored origins and compare instead of running"
    ),
) -> None:
    """Phase 4 backtest: three stages (heavy stage 1 and 3 in subprocesses, lean stage 2)."""
    import datetime as dt
    import json
    import subprocess
    import sys
    from pathlib import Path

    from .config import load_config
    from .eval.backtest import BACKTEST_ROOT, origin_list
    from .models import lean

    cfg = load_config()
    origins = origin_list(cfg, window, first or None, last or None)
    root = Path(__file__).resolve().parents[2]
    if verify:
        import random

        rng = random.Random(0)
        from .eval.store import read_meta

        have = sorted({dt.date.fromisoformat(o) for o in read_meta()["origin"].unique()})
        pick = rng.sample(have, min(verify, len(have)))
        spec = json.dumps({"origins": [o.isoformat() for o in pick]})
        r = subprocess.run(
            [sys.executable, "-m", "ffcast.eval.backtest", "verify", spec], cwd=str(root)
        )
        raise typer.Exit(code=r.returncode)
    workdir = BACKTEST_ROOT / "work" / dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    spec = {
        "origins": [o.isoformat() for o in origins],
        "workdir": str(workdir),
        "modes": [m for m in modes.split(",") if m] or None,
        "run_bench": not skip_bench,
        "models": [] if skip_fm else ([m for m in models.split(",") if m] or None),
        "processes": processes or None,
        "force": force,
    }
    typer.echo(f"{len(origins)} origins {origins[0]} .. {origins[-1]}; workdir {workdir}")
    r1 = subprocess.run(
        [sys.executable, "-m", "ffcast.eval.backtest", "stage1", json.dumps(spec)], cwd=str(root)
    )
    if r1.returncode != 0:
        raise typer.Exit(code=r1.returncode)
    if (workdir / "requests").exists() and any((workdir / "requests").glob("*.json")):
        status = lean.run_all(workdir / "requests", workdir / "responses")
        for k, v in status.items():
            typer.echo(
                f"worker {k}: {'ok' if v == 'ok' else 'FAILED: ' + v.splitlines()[-1][:160]}"
            )
    r3 = subprocess.run(
        [
            sys.executable,
            "-m",
            "ffcast.eval.backtest",
            "stage3",
            json.dumps({"workdir": str(workdir)}),
        ],
        cwd=str(root),
    )
    raise typer.Exit(code=r3.returncode)


@app.command()
def score() -> None:
    """Regenerate every scoring table from the forecast store (Phase 4). Output stays under
    data/backtest/tables (private until Gate 4)."""
    from .eval.backtest import build_outturns
    from .eval.bias import write_bias_tables
    from .eval.scoring import score_tables, write_tables

    rep = build_outturns()
    typer.echo(f"outturns: {rep}")
    tables = score_tables()
    if not tables:
        typer.echo("no forecasts stored")
        raise typer.Exit(code=1)
    d = write_tables(tables)
    typer.echo(f"wrote {d} ({', '.join(f'{k}={len(v)}' for k, v in tables.items())})")
    typer.echo(f"wrote {write_bias_tables()}")


@app.command()
def spf(
    models: str = typer.Option("", help="Comma-separated foundation models (default all)"),
    skip_bench: bool = typer.Option(False, help="Do not run the classical benchmarks"),
    skip_models: bool = typer.Option(False, help="Only rebuild tables from stored model points"),
) -> None:
    """ECB SPF comparison (Phase 4, Q4): survey windows, matched model runs at the survey
    deadlines, outturns in survey definitions and fixed-event regressions. Tables stay under
    data/backtest/tables."""
    from .eval.spf import run_spf

    rep = run_spf(
        models=[m for m in models.split(",") if m] or None,
        run_bench=not skip_bench,
        skip_models=skip_models,
    )
    typer.echo(str(rep))


@app.command("registry-run")
def registry_run(origin: str = typer.Argument("", help="Origin date YYYY-MM-DD")) -> None:
    """Run one live registry origin (Phase 5)."""
    raise typer.Exit(code=_not_implemented("registry-run"))


def _not_implemented(name: str) -> int:
    typer.echo(f"{name}: not implemented yet (see STATUS.md for the current phase)", err=True)
    return 2
