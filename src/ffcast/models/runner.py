"""Run foundation-model workers in their own environments (see workers/_protocol.md)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, FoundationModel
from .interface import QuantileForecast
from .weights import ensure_weights, weights_digest

REPO = Path(__file__).resolve().parents[3]
ENVS = REPO / "envs"
WORKERS = REPO / "workers"


@dataclass
class Task:
    id: str
    freq: str
    history: list[list[float]]  # variates x T, target first
    horizon: int
    quantiles: tuple[float, ...]


_ENV_KEEP = (
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "HOME",
    "HOMEDRIVE",
    "HOMEPATH",
    "APPDATA",
    "LOCALAPPDATA",
    "PROGRAMDATA",
    "USERNAME",
    "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE",
    "LANG",
    "LC_ALL",
    "TZ",
    "HF_HOME",
    "HF_HUB_CACHE",
    "SSL_CERT_FILE",
    "REQUESTS_CA_BUNDLE",
)


def worker_env() -> dict[str, str]:
    """A minimal, reproducible environment for workers. The parent's environment is NOT
    inherited: importing pandas/pyarrow in the orchestrator prepends DLL directories to PATH
    that make torch/safetensors in the child crash with an access violation on Windows, and
    thread/BLAS variables would make runs machine-dependent. PATH is reduced to the system
    directories; the worker interpreter is addressed by absolute path."""
    base = os.environ
    env = {k: base[k] for k in _ENV_KEEP if k in base}
    sysroot = base.get("SYSTEMROOT", r"C:\Windows")
    if os.name == "nt":
        env["PATH"] = ";".join([sysroot + r"\System32", sysroot, sysroot + r"\System32\Wbem"])
    else:
        env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
    env["PYTHONFAULTHANDLER"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    env["TOKENIZERS_PARALLELISM"] = "false"
    return env


def _env_python(env: str) -> list[str]:
    """The interpreter of envs/<env>/.venv (created by `uv sync` in that folder); falls back to
    `uv run --project` when the venv is absent."""
    for cand in (
        ENVS / env / ".venv" / "Scripts" / "python.exe",
        ENVS / env / ".venv" / "bin" / "python",
    ):
        if cand.exists():
            return [str(cand)]
    return ["uv", "run", "--project", str(ENVS / env), "python"]


def run_worker(
    fm: FoundationModel, settings: dict, tasks: list[Task], *, timeout: int = 3600
) -> dict:
    wdir, manifest = ensure_weights(fm, allow_download=settings.get("allow_download", True))
    # Memory pre-flight threshold proportional to the snapshot size: twice the weights plus
    # 600 MB for torch, unless the config fixes a value.
    weights_mb = sum(
        (wdir / f).stat().st_size for f in manifest["files"] if (wdir / f).exists()
    ) // (1 << 20)
    settings = {
        **settings,
        "min_free_commit_mb": settings.get("min_free_commit_mb", 2 * weights_mb + 600),
    }
    req = {
        "model": fm.hf_id,
        "weights_dir": str(wdir),
        "settings": settings,
        "tasks": [t.__dict__ | {"quantiles": list(t.quantiles)} for t in tasks],
    }
    with tempfile.TemporaryDirectory() as td:
        rp, op = Path(td) / "request.json", Path(td) / "response.json"
        rp.write_text(json.dumps(req), encoding="utf-8")
        t0 = time.perf_counter()
        proc = subprocess.run(
            [*_env_python(fm.env), str(WORKERS / f"run_{fm.env}.py"), str(rp), str(op)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO),
            env=worker_env(),
        )
        wall = time.perf_counter() - t0
        if proc.returncode != 0 or not op.exists():
            raise RuntimeError(
                f"worker {fm.env} failed (rc={proc.returncode}):\n{proc.stderr[-4000:]}"
            )
        resp = json.loads(op.read_text(encoding="utf-8"))
    resp["wall_s"] = round(wall, 2)
    resp["weights_digest"] = weights_digest(manifest)
    resp["stderr_tail"] = proc.stderr[-2000:]
    return resp


def to_forecasts(resp: dict, tasks: list[Task]) -> dict[str, QuantileForecast]:
    out = {}
    for t in tasks:
        r = resp["results"].get(t.id)
        if r is None:
            continue
        q = np.asarray(r["quantiles"], dtype=float)
        mean = None if r.get("mean") is None else np.asarray(r["mean"], dtype=float)
        out[t.id] = QuantileForecast(
            t.quantiles,
            q,
            mean,
            {
                "runtime_s": r["runtime_s"],
                "weights_digest": resp["weights_digest"],
                "seed": resp["seed"],
            },
        ).sorted()
    return out


def make_task(
    task_id: str, history: pd.Series | pd.DataFrame, freq: str, horizon: int, quantiles
) -> Task:
    if isinstance(history, pd.Series):
        hist = [history.astype(float).tolist()]
    else:
        hist = [history[c].astype(float).tolist() for c in history.columns]
    return Task(task_id, freq, hist, int(horizon), tuple(float(q) for q in quantiles))


def model_settings(cfg: Config, name: str) -> dict:
    base = dict(cfg.models.get("settings", {}).get("common", {}))
    base.update(cfg.models.get("settings", {}).get(name, {}))
    return base
