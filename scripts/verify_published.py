"""Verify a published registry origin against the public ledger, using the standard library only.

Usage: python scripts/verify_published.py ledger/ledger.jsonl <folder with the release assets>

Checks: the ledger chain; that the manifest's SHA-256 equals the `payload_sha256` of the ledger
line for its origin; that the salted commitments in the manifest match `forecasts.parquet` and
`status.parquet` with the published salt; that the time-stamped file holds that line's entry
hash. The OpenTimestamps proof itself is checked with `ots verify` (not included here).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

FIELDS = ("seq", "kind", "origin", "payload_sha256", "recorded_utc", "prev")


def sha256_file(p: Path, prefix: bytes = b"") -> str:
    h = hashlib.sha256(prefix)
    h.update(p.read_bytes())
    return h.hexdigest()


def main(ledger: Path, folder: Path) -> list[str]:
    problems: list[str] = []
    entries = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
    prev = "0" * 64
    for i, e in enumerate(entries):
        body = json.dumps({k: e[k] for k in FIELDS}, sort_keys=True, separators=(",", ":"))
        if e["seq"] != i or e["prev"] != prev:
            problems.append(f"ledger entry {i}: chain broken")
        if hashlib.sha256(body.encode("utf-8")).hexdigest() != e["entry_hash"]:
            problems.append(f"ledger entry {i}: entry_hash does not match")
        prev = e["entry_hash"]
    man = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    hits = [e for e in entries if e["kind"] == "run" and e["origin"] == man["origin"]]
    if len(hits) != 1:
        return problems + [f"origin {man['origin']}: not exactly one ledger line"]
    e = hits[0]
    if sha256_file(folder / "manifest.json") != e["payload_sha256"]:
        problems.append("manifest.json does not match the ledger line")
    salt = bytes.fromhex((folder / "salt.hex").read_text(encoding="utf-8").strip())
    for key in ("forecasts", "status"):
        if sha256_file(folder / man[key]["file"], salt) != man[key]["commitment_sha256"]:
            problems.append(f"{man[key]['file']} does not match its commitment")
    txt = folder / f"entry_{e['seq']:04d}.txt"
    if not txt.exists() or txt.read_text(encoding="utf-8").strip() != e["entry_hash"]:
        problems.append(f"{txt.name} missing or not the entry hash")
    return problems


if __name__ == "__main__":
    probs = main(Path(sys.argv[1]), Path(sys.argv[2]))
    for p in probs:
        print("PROBLEM:", p)
    print("verified" if not probs else "verification FAILED")
    sys.exit(1 if probs else 0)
