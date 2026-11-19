"""Hash-chained ledger: one JSON object per line, values are hashes and dates only.

An entry commits to a private payload (the pre-registration text, or a run manifest) by its
SHA-256 and to the previous entry by `prev`. `entry_hash` is the SHA-256 of the canonical JSON of
the other fields. The ledger file is the only part of the registry meant to become public."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

GENESIS_PREV = "0" * 64
FIELDS = ("seq", "kind", "origin", "payload_sha256", "recorded_utc", "prev")
KINDS = ("preregistration", "run")


def entry_hash(entry: dict) -> str:
    body = {k: entry[k] for k in FIELDS}
    s = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def append(
    path: Path, *, kind: str, origin: str | None, payload_sha256: str, recorded_utc: str
) -> dict:
    if kind not in KINDS:
        raise ValueError(f"unknown ledger entry kind {kind!r}")
    entries = read(path)
    problems = check_chain(entries)
    if problems:
        raise RuntimeError("ledger is not intact, refusing to append: " + "; ".join(problems[:3]))
    if kind == "preregistration" and entries:
        raise RuntimeError("the pre-registration must be the first ledger entry")
    if kind == "run" and (not entries or entries[0]["kind"] != "preregistration"):
        raise RuntimeError("no pre-registration entry: the ledger must start with it")
    if kind == "run" and any(e["kind"] == "run" and e["origin"] == origin for e in entries):
        raise RuntimeError(f"origin {origin} already has a ledger entry (append-only)")
    entry = {
        "seq": len(entries),
        "kind": kind,
        "origin": origin,
        "payload_sha256": payload_sha256,
        "recorded_utc": recorded_utc,
        "prev": entries[-1]["entry_hash"] if entries else GENESIS_PREV,
    }
    entry["entry_hash"] = entry_hash(entry)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")
    return entry


def check_chain(entries: list[dict]) -> list[str]:
    """Structural problems of the chain itself (edits, reordering, removed middle entries)."""
    problems = []
    prev = GENESIS_PREV
    seen_origins: set[str] = set()
    for i, e in enumerate(entries):
        missing = [k for k in (*FIELDS, "entry_hash") if k not in e]
        if missing:
            problems.append(f"entry {i}: missing fields {missing}")
            continue
        if e["seq"] != i:
            problems.append(f"entry {i}: seq is {e['seq']}")
        if e["prev"] != prev:
            problems.append(f"entry {i}: prev does not match the hash of the entry before it")
        if entry_hash(e) != e["entry_hash"]:
            problems.append(f"entry {i}: entry_hash does not match its contents")
        if i == 0 and e["kind"] != "preregistration":
            problems.append("entry 0 is not the pre-registration")
        if i > 0 and e["kind"] != "run":
            problems.append(f"entry {i}: kind {e['kind']!r} after the first entry")
        if e["kind"] == "run":
            if e["origin"] in seen_origins:
                problems.append(f"entry {i}: origin {e['origin']} appears twice")
            seen_origins.add(e["origin"])
        prev = e["entry_hash"]
    return problems
