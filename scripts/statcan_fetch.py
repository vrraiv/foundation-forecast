"""Fetch Statistics Canada full-table CSV zips through the Web Data Service, for use from a
GitHub Actions runner (the owner's sixfigures repository shows the WDS answers runners while it
challenges home connections). Standard library only; nothing is parsed here.

    python -I scripts/statcan_fetch.py --out DIR 18100004 36100107 ...

Writes DIR/<pid>-eng.zip for each table that downloads as a real zip, and DIR/manifest.json
with, per table: the WDS link, bytes, SHA-256, fetch time (UTC), HTTP status and the first
characters of any non-zip body (a Cloudflare challenge page is recorded, never saved whole).
The exit code is 0 when every table arrived and 2 otherwise, so the artifact is still uploaded.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

WDS = "https://www150.statcan.gc.ca/t1/wds/rest/"
HEADERS = {
    "User-Agent": "foundation-forecast-fetch/0.1 (GitHub Actions; public data; contact via repository)"
}


def _get(url: str, timeout: int = 120) -> tuple[int, bytes, dict]:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:4000], dict(e.headers)


def fetch_table(pid: str, out: Path) -> dict:
    rec: dict = {
        "pid": pid,
        "fetched_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }
    status, body, headers = _get(f"{WDS}getFullTableDownloadCSV/{pid}/en")
    rec["link_status"] = status
    rec["server"] = headers.get("Server") or headers.get("server")
    if status != 200:
        rec["error"] = f"link request HTTP {status}: {body[:200].decode('utf-8', 'replace')!r}"
        return rec
    try:
        obj = json.loads(body)
    except ValueError:
        rec["error"] = f"link response not JSON: {body[:200].decode('utf-8', 'replace')!r}"
        return rec
    url = obj.get("object")
    rec["url"] = url
    if obj.get("status") != "SUCCESS" or not url:
        rec["error"] = f"WDS refused: {obj}"
        return rec
    status, body, headers = _get(url, timeout=900)
    rec["file_status"] = status
    if status != 200:
        rec["error"] = f"download HTTP {status}: {body[:200].decode('utf-8', 'replace')!r}"
        return rec
    path = out / f"{pid}-eng.zip"
    path.write_bytes(body)
    if not zipfile.is_zipfile(path):
        rec["error"] = f"not a zip: {body[:200].decode('utf-8', 'replace')!r}"
        path.unlink()
        return rec
    with zipfile.ZipFile(path) as z:
        rec["members"] = z.namelist()
    rec["bytes"] = len(body)
    rec["sha256"] = hashlib.sha256(body).hexdigest()
    rec["file"] = path.name
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("pids", nargs="+")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pids = [p.strip() for arg in a.pids for p in arg.split(",") if p.strip()]
    bad = [p for p in pids if not (p.isdigit() and len(p) == 8)]
    if bad:
        sys.exit(f"product ids must be 8 digits: {bad}")
    records = [fetch_table(p, out) for p in pids]
    (out / "manifest.json").write_text(
        json.dumps({"source": WDS, "tables": records}, indent=1), encoding="utf-8"
    )
    ok = [r for r in records if "sha256" in r]
    for r in records:
        print(
            f"{r['pid']}: "
            + (
                f"{r['bytes']:,} bytes sha256 {r['sha256'][:16]}"
                if "sha256" in r
                else f"FAILED {r.get('error')}"
            )
        )
    return 0 if len(ok) == len(records) else 2


if __name__ == "__main__":
    raise SystemExit(main())
