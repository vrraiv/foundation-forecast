"""Disclosure of sealed origins under Amendment 1 (`PREREGISTRATION_AMENDMENTS.md`).

`bundle` copies an origin's sealed files byte for byte into a staging folder, adds a CSV export
of the forecasts and a short README, and refuses unless the origin is in the ledger, its manifest
matches the ledger line, the salted commitments match, and a real OpenTimestamps proof exists.
`release` uploads the bundle as the assets of the GitHub release `registry-<origin>`.

Nothing here writes to a sealed file or reads the data snapshot.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from . import core
from . import ledger as lg

SEALED = ("manifest.json", "salt.hex", "forecasts.parquet", "status.parquet")


class PublishError(RuntimeError):
    pass


def _entry_for(paths: core.Paths, origin: str) -> dict:
    entries = lg.read(paths.ledger)
    problems = lg.check_chain(entries)
    if problems:
        raise PublishError(f"ledger chain does not verify: {problems}")
    for e in entries:
        if e.get("kind") == "run" and e.get("origin") == origin:
            return e
    raise PublishError(f"origin {origin} has no ledger entry")


def check(paths: core.Paths, origin: str, allow_dry_run: bool = False) -> tuple[dict, list[Path]]:
    """Return the ledger entry and the files to publish, or raise PublishError."""
    e = _entry_for(paths, origin)
    odir = paths.origin_dir(origin)
    for name in SEALED:
        if not (odir / name).exists():
            raise PublishError(f"{origin}: {name} missing")
    if core.sha256_file(odir / "manifest.json") != e["payload_sha256"]:
        raise PublishError(f"{origin}: manifest does not match the ledger")
    man = json.loads((odir / "manifest.json").read_text(encoding="utf-8"))
    if man.get("dry_run") and not allow_dry_run:
        raise PublishError(f"{origin}: dry-run manifest")
    salt = (odir / "salt.hex").read_text(encoding="utf-8").strip()
    for key in ("forecasts", "status"):
        if core.commitment(salt, odir / man[key]["file"]) != man[key]["commitment_sha256"]:
            raise PublishError(f"{origin}: {man[key]['file']} does not match its commitment")
    pdir = odir / "proofs"
    txt = pdir / f"entry_{e['seq']:04d}.txt"
    ots = pdir / f"entry_{e['seq']:04d}.txt.ots"
    if not (txt.exists() and ots.exists()):
        raise PublishError(f"{origin}: not time-stamped yet (no OpenTimestamps proof)")
    if txt.read_text(encoding="utf-8").strip() != e["entry_hash"]:
        raise PublishError(f"{origin}: time-stamped file is not the entry hash")
    return e, [odir / n for n in SEALED] + [txt, ots]


def bundle(paths: core.Paths, origin: str, out: Path, allow_dry_run: bool = False) -> list[Path]:
    """Stage the release assets for one origin in `out` (created; must be empty)."""
    e, files = check(paths, origin, allow_dry_run)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise PublishError(f"{out} is not empty")
    staged = []
    for f in files:
        dst = out / f.name
        shutil.copyfile(f, dst)
        if core.sha256_file(dst) != core.sha256_file(f):
            raise PublishError(f"copy of {f.name} differs")
        staged.append(dst)
    import pandas as pd

    csv = out / "forecasts.csv"
    pd.read_parquet(out / "forecasts.parquet").to_csv(csv, index=False, lineterminator="\n")
    staged.append(csv)
    notes = out / "README.md"
    notes.write_text(release_notes(origin, e), encoding="utf-8", newline="\n")
    staged.append(notes)
    return staged


def release_notes(origin: str, e: dict) -> str:
    return f"""Live registry, origin {origin} (ledger entry {e["seq"]}).

Published under Amendment 1 of the pre-registration (`PREREGISTRATION_AMENDMENTS.md`). The
files `manifest.json`, `salt.hex`, `forecasts.parquet`, `status.parquet` and the time-stamp
proof are byte-identical to the files sealed at the run. `forecasts.csv` is a convenience export
of `forecasts.parquet`; the parquet file is the record.

Ledger entry hash: `{e["entry_hash"]}`
Manifest SHA-256 (ledger `payload_sha256`): `{e["payload_sha256"]}`

To verify with the Python standard library only, from a clone of the repository:

    python scripts/verify_published.py ledger/ledger.jsonl <folder with these assets>

For the proof: `ots verify entry_{e["seq"]:04d}.txt.ots` (OpenTimestamps client).

No error, score or ranking of the live forecasts is computed or shown by the project before 12
origins have first-release outturns (pre-registration §9 as amended).
"""


def release(origin: str, staged: list[Path], repo: str | None = None) -> str:
    """Create the GitHub release `registry-<origin>` with the staged assets (needs `gh`)."""
    tag = f"registry-{origin}"
    notes = next(p for p in staged if p.name == "README.md")
    assets = [str(p) for p in staged if p.name != "README.md"]
    cmd = [
        "gh",
        "release",
        "create",
        tag,
        *assets,
        "--title",
        f"Live registry: origin {origin}",
        "--notes-file",
        str(notes),
    ]
    if repo:
        cmd += ["--repo", repo]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise PublishError(f"gh release create failed: {res.stderr.strip()}")
    return res.stdout.strip()
