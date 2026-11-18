"""Lean worker launcher: standard library only (no numpy, no pandas), so the process that spawns
model workers holds almost no memory. Phase 4 and the smoke test run in three stages:

  stage 1 (heavy process, exits): build panels, run benchmarks, write worker request files;
  stage 2 (this module, lean process): run each worker in its own environment, one at a time;
  stage 3 (heavy process): read responses, score or check, write outputs.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENVS = REPO / "envs"
WORKERS = REPO / "workers"

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
    """Minimal, reproducible environment for workers (the parent's PATH and thread variables are
    not inherited; the interpreter is addressed by absolute path)."""
    base = os.environ
    env = {k: base[k] for k in _ENV_KEEP if k in base}
    sysroot = base.get("SYSTEMROOT", "C:\\Windows")
    if os.name == "nt":
        env["PATH"] = ";".join([sysroot + "\\System32", sysroot, sysroot + "\\System32\\Wbem"])
    else:
        env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
    env["PYTHONFAULTHANDLER"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    env["TOKENIZERS_PARALLELISM"] = "false"
    return env


def env_python(env: str) -> list[str]:
    for cand in (
        ENVS / env / ".venv" / "Scripts" / "python.exe",
        ENVS / env / ".venv" / "bin" / "python",
    ):
        if cand.exists():
            return [str(cand)]
    return ["uv", "run", "--project", str(ENVS / env), "python"]


def run_request(request_path: Path, response_path: Path, env: str, *, timeout: int = 7200) -> dict:
    """Run one worker on one request file. Returns the response dict (with wall time and the
    stderr tail added) or raises RuntimeError with the stderr tail."""
    # never let a stale response from an earlier run stand in for this one
    response_path.unlink(missing_ok=True)
    response_path.with_suffix(".error.txt").unlink(missing_ok=True)
    t0 = time.perf_counter()
    proc = subprocess.run(
        [*env_python(env), str(WORKERS / f"run_{env}.py"), str(request_path), str(response_path)],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
        env=worker_env(),
    )
    wall = time.perf_counter() - t0
    if proc.returncode != 0 or not response_path.exists():
        raise RuntimeError(f"worker {env} failed (rc={proc.returncode}):\n{proc.stderr[-4000:]}")
    resp = json.loads(response_path.read_text(encoding="utf-8"))
    resp["wall_s"] = round(wall, 2)
    resp["stderr_tail"] = proc.stderr[-2000:]
    response_path.write_text(json.dumps(resp, indent=1, sort_keys=True), encoding="utf-8")
    return resp


def run_all(requests_dir: Path, responses_dir: Path) -> dict[str, str]:
    """Run every `<model>.json` request in `requests_dir` sequentially. Each request file carries
    an `env` field naming the worker environment. Returns {model: 'ok' | error text}."""
    responses_dir.mkdir(parents=True, exist_ok=True)
    status: dict[str, str] = {}
    for rp in sorted(Path(requests_dir).glob("*.json")):
        req = json.loads(rp.read_text(encoding="utf-8"))
        env = req["env"]
        out = responses_dir / rp.name
        try:
            run_request(rp, out, env)
            status[rp.stem] = "ok"
        except Exception as e:  # noqa: BLE001
            status[rp.stem] = str(e)[-1500:]
            out.with_suffix(".error.txt").write_text(status[rp.stem], encoding="utf-8")
    (responses_dir / "_status.json").write_text(json.dumps(status, indent=1), encoding="utf-8")
    return status


if __name__ == "__main__":
    import sys

    st = run_all(Path(sys.argv[1]), Path(sys.argv[2]))
    for k, v in st.items():
        print(k, "ok" if v == "ok" else "FAILED: " + v.splitlines()[-1][:200])
