"""Pinned model weights: download exactly the configured revision into data/models/, hash
every file, and load offline from that folder."""

from __future__ import annotations

import json
from pathlib import Path

from ..config import FoundationModel
from ..data.raw import DATA_ROOT, sha256_file

MODELS_ROOT = DATA_ROOT / "models"


def local_dir(fm: FoundationModel) -> Path:
    return MODELS_ROOT / fm.hf_id.replace("/", "__") / fm.revision


def ensure_weights(fm: FoundationModel, allow_download: bool = True) -> tuple[Path, dict]:
    """Return (folder, manifest). Downloads with huggingface_hub at the pinned revision if the
    folder is missing; otherwise verifies hashes against the stored manifest."""
    d = local_dir(fm)
    man = d / "MANIFEST.sha256.json"
    if man.exists():
        m = json.loads(man.read_text(encoding="utf-8"))
        bad = [f for f, h in m["files"].items() if not (d / f).exists() or sha256_file(d / f) != h]
        if bad:
            raise RuntimeError(f"{fm.hf_id}@{fm.revision}: files changed since download: {bad}")
        return d, m
    if not allow_download:
        raise FileNotFoundError(f"weights for {fm.hf_id}@{fm.revision} not present at {d}")
    from huggingface_hub import snapshot_download

    d.mkdir(parents=True, exist_ok=True)
    snapshot_download(fm.hf_id, revision=fm.revision, local_dir=str(d))
    files = {}
    for p in sorted(d.rglob("*")):
        if p.is_file() and p.name != "MANIFEST.sha256.json" and ".cache" not in p.parts:
            files[str(p.relative_to(d)).replace("\\", "/")] = sha256_file(p)
    m = {"hf_id": fm.hf_id, "revision": fm.revision, "files": files}
    man.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return d, m


def weights_digest(manifest: dict) -> str:
    """One hash for the whole snapshot: SHA-256 over sorted 'path sha' lines."""
    import hashlib

    h = hashlib.sha256()
    for f, s in sorted(manifest["files"].items()):
        h.update(f"{f} {s}\n".encode())
    return h.hexdigest()
