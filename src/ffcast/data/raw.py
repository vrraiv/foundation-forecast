"""Raw download store: bytes saved unmodified under data/raw/<source>/<download-date>/ with a
SHA-256 manifest. Nothing in the project reads a remote endpoint except through `fetch`."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import requests

DATA_ROOT = Path(__file__).resolve().parents[3] / "data"
RAW_ROOT = DATA_ROOT / "raw"
RETRY_WAITS = (10, 40)  # seconds before the second and third attempt of a download
USER_AGENT = "foundation-forecast-research/0.1 (public-data research client)"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class RawFile:
    source: str
    download_date: dt.date
    name: str
    path: Path
    sha256: str
    url: str | None
    fetched_at_utc: str
    http_status: int | None


class RawStore:
    """One directory per (source, download date); a manifest.json lists every file."""

    def __init__(self, root: Path = RAW_ROOT, today: dt.date | None = None) -> None:
        self.root = Path(root)
        self.today = today or dt.datetime.now(dt.UTC).date()
        self.failures: list[str] = []  # downloads that failed after every retry, this session

    def dir_for(self, source: str, day: dt.date | None = None) -> Path:
        d = self.root / source / (day or self.today).isoformat()
        d.mkdir(parents=True, exist_ok=True)
        return d

    def manifest_path(self, source: str, day: dt.date | None = None) -> Path:
        return self.dir_for(source, day) / "manifest.json"

    def _load_manifest(self, source: str, day: dt.date | None = None) -> dict:
        p = self.manifest_path(source, day)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {"source": source, "download_date": (day or self.today).isoformat(), "files": {}}

    def _save_manifest(self, source: str, m: dict, day: dt.date | None = None) -> None:
        self.manifest_path(source, day).write_text(
            json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def put(
        self,
        source: str,
        name: str,
        content: bytes,
        url: str | None = None,
        http_status: int | None = None,
        extra: dict | None = None,
    ) -> RawFile:
        d = self.dir_for(source)
        path = d / name
        path.write_bytes(content)
        digest = sha256_bytes(content)
        fetched = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
        m = self._load_manifest(source)
        m["files"][name] = {
            "sha256": digest,
            "bytes": len(content),
            "url": url,
            "fetched_at_utc": fetched,
            "http_status": http_status,
            **(extra or {}),
        }
        self._save_manifest(source, m)
        return RawFile(source, self.today, name, path, digest, url, fetched, http_status)

    def fetch(
        self,
        source: str,
        name: str,
        url: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int = 300,
        reuse: bool = True,
    ) -> RawFile:
        """GET `url` and store the body unmodified. If the same name exists for today and
        `reuse`, return the stored file without a network call (idempotent daily runs).
        Non-200 responses are stored too (with suffix .error) and raise. Network errors and
        HTTP 429/5xx are retried (three attempts, waiting 10 and 40 seconds); a download that
        still fails raises DownloadError and is listed in `self.failures`."""
        d = self.dir_for(source)
        if reuse and (d / name).exists():
            m = self._load_manifest(source)["files"].get(name)
            if m and m.get("http_status") == 200:
                return RawFile(
                    source,
                    self.today,
                    name,
                    d / name,
                    m["sha256"],
                    m.get("url"),
                    m["fetched_at_utc"],
                    200,
                )
        h = {"User-Agent": USER_AGENT, **(headers or {})}
        waits = RETRY_WAITS
        for attempt in range(len(waits) + 1):
            last = attempt == len(waits)
            try:
                resp = requests.get(url, params=params, headers=h, timeout=timeout)
            except requests.RequestException as e:
                if not last:
                    time.sleep(waits[attempt])
                    continue
                msg = f"{source}/{name}: {type(e).__name__} from {url} after {attempt + 1} attempts"
                self.failures.append(msg)
                raise DownloadError(msg) from e
            full_url = resp.url
            if resp.status_code == 200:
                return self.put(source, name, resp.content, full_url, 200)
            if (resp.status_code == 429 or resp.status_code >= 500) and not last:
                time.sleep(waits[attempt])
                continue
            self.put(source, name + ".error", resp.content, full_url, resp.status_code)
            msg = f"{source}/{name}: HTTP {resp.status_code} from {full_url}"
            self.failures.append(msg)
            raise DownloadError(msg)
        raise AssertionError("unreachable")

    def register_manual(self, source: str, path: Path, note: str) -> RawFile:
        """Hash and record a file the owner downloaded by hand (e.g. a StatCan zip fetched in a
        browser). The file is copied into the store; provenance is `manual`."""
        content = Path(path).read_bytes()
        return self.put(f"{source}-manual", Path(path).name, content, None, None, {"note": note})

    def list_days(self, source: str) -> list[dt.date]:
        d = self.root / source
        if not d.exists():
            return []
        return sorted(dt.date.fromisoformat(p.name) for p in d.iterdir() if p.is_dir())

    def verify(self, source: str, day: dt.date) -> list[str]:
        """Return names whose bytes no longer match the manifest."""
        m = self._load_manifest(source, day)
        bad = []
        for name, meta in m["files"].items():
            p = self.dir_for(source, day) / name
            if not p.exists() or sha256_file(p) != meta["sha256"]:
                bad.append(name)
        return bad


class DownloadError(RuntimeError):
    pass
