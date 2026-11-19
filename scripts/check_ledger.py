"""Public check of the forecast ledger. Standard library only, so it runs anywhere without
installing the project (the GitHub workflow `ledger.yml` and anyone with a copy of the file).

It needs nothing private. It checks what the public file can show by itself:

  chain       every line's own hash, each `prev`, the sequence numbers, the first line being the
              pre-registration, one line per origin (same rules as `ffcast.registry.ledger`);
  --previous  append-only: an earlier version of the file must be an exact prefix of this one;
  --expect    presence: once an origin day has passed (plus a grace period), the ledger must hold
              a line for it. Only origins after the pre-registration line are expected.

Exit code 0 if everything holds, 1 otherwise. A missing ledger file is not an error (the
registry has not been switched on); it is reported and the exit code is 0.

What it cannot check: that a line's hash corresponds to real forecasts. That needs the private
files and `ffcast registry-verify`."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

FIELDS = ("seq", "kind", "origin", "payload_sha256", "recorded_utc", "prev")


def entry_hash(e: dict) -> str:
    body = {k: e[k] for k in FIELDS}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def read(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def check_chain(entries: list[dict]) -> list[str]:
    problems, prev, seen = [], "0" * 64, set()
    for i, e in enumerate(entries):
        missing = [k for k in (*FIELDS, "entry_hash") if k not in e]
        if missing:
            problems.append(f"line {i}: missing fields {missing}")
            continue
        if e["seq"] != i:
            problems.append(f"line {i}: seq is {e['seq']}")
        if e["prev"] != prev:
            problems.append(f"line {i}: prev does not match the hash of the line before it")
        if entry_hash(e) != e["entry_hash"]:
            problems.append(f"line {i}: entry_hash does not match its contents")
        if (i == 0) != (e["kind"] == "preregistration"):
            problems.append(f"line {i}: kind {e['kind']!r} in this position")
        if e["kind"] == "run":
            if e["origin"] in seen:
                problems.append(f"line {i}: origin {e['origin']} appears twice")
            seen.add(e["origin"])
        prev = e["entry_hash"]
    return problems


def origin_date(year: int, month: int, day: int) -> dt.date:
    d = dt.date(year, month, day)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def expected_origins(entries: list[dict], today: dt.date, day: int, grace: int) -> list[str]:
    """Origins that should be in the ledger by `today`: every origin on or after the date of
    the pre-registration line whose day plus `grace` days has passed."""
    if not entries:
        return []
    start = dt.datetime.fromisoformat(entries[0]["recorded_utc"]).date()
    out, y, m = [], start.year, start.month
    while True:
        o = origin_date(y, m, day)
        if o + dt.timedelta(days=grace) > today:
            break
        if o >= start:
            out.append(o.isoformat())
        y, m = (y, m + 1) if m < 12 else (y + 1, 1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ledger", nargs="?", default="ledger/ledger.jsonl")
    ap.add_argument("--previous", help="earlier version of the ledger file (append-only check)")
    ap.add_argument("--expect", action="store_true", help="require a line for every past origin")
    ap.add_argument("--day", type=int, default=25, help="origin day of the month")
    ap.add_argument("--grace", type=int, default=1, help="days after the origin before it is due")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today, UTC)")
    a = ap.parse_args()
    path = Path(a.ledger)
    if not path.exists():
        print(f"{path}: no ledger yet (registry not switched on); nothing to check")
        return 0
    entries = read(path)
    problems = check_chain(entries)
    if a.previous and Path(a.previous).exists():
        old = Path(a.previous).read_text(encoding="utf-8").splitlines()
        new = path.read_text(encoding="utf-8").splitlines()
        if new[: len(old)] != old:
            problems.append("the ledger is not an extension of its previous version")
    if a.expect:
        today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(dt.UTC).date()
        have = {e["origin"] for e in entries if e.get("kind") == "run"}
        for o in expected_origins(entries, today, a.day, a.grace):
            if o not in have:
                problems.append(f"no ledger line for origin {o} (today is {today})")
    runs = [e for e in entries if e.get("kind") == "run"]
    last = runs[-1]["origin"] if runs else "-"
    print(f"{path}: {len(entries)} lines, {len(runs)} origins, last {last}")
    for p in problems:
        print(f"PROBLEM: {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
