"""Shared helpers for worker scripts. Pure standard library + numpy; no ffcast import."""

from __future__ import annotations

import json
import os
import sys
import time


def load_request(argv):
    if len(argv) != 3:
        sys.exit("usage: worker.py REQUEST.json RESPONSE.json")
    with open(argv[1], encoding="utf-8") as fh:
        return json.load(fh)


def check_memory(min_free_mb: int = 4096) -> None:
    """Fail early with a clear message when the system is short of commit charge. Observed on
    2026-11-18: with 4 GB of commit free, loading the 925 MB TimesFM checkpoint crashed with an
    access violation inside safetensors (memory-mapped) or a null PyObject (bytes), depending
    on how much memory the parent process happened to hold."""
    if os.name != "nt":
        return
    import ctypes

    class MemStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_uint32),
            ("dwMemoryLoad", ctypes.c_uint32),
            ("ullTotalPhys", ctypes.c_uint64),
            ("ullAvailPhys", ctypes.c_uint64),
            ("ullTotalPageFile", ctypes.c_uint64),
            ("ullAvailPageFile", ctypes.c_uint64),
            ("ullTotalVirtual", ctypes.c_uint64),
            ("ullAvailVirtual", ctypes.c_uint64),
            ("ullAvailExtendedVirtual", ctypes.c_uint64),
        ]

    st = MemStatus()
    st.dwLength = ctypes.sizeof(st)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    free_mb = st.ullAvailPageFile // (1 << 20)
    if free_mb < min_free_mb:
        sys.exit(
            f"worker refused to start: only {free_mb} MB of commit charge available "
            f"(need {min_free_mb} MB to load model weights safely)"
        )


def setup_torch(settings):
    check_memory(int(settings.get("min_free_commit_mb", 4096)))
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")
    import torch

    torch.manual_seed(int(settings.get("seed", 0)))
    torch.set_num_threads(int(settings.get("threads", 4)))
    torch.use_deterministic_algorithms(True, warn_only=True)
    return torch


def versions(*mods):
    import importlib.metadata as md

    out = {}
    for m in mods:
        try:
            out[m] = md.version(m)
        except md.PackageNotFoundError:
            out[m] = None
    return out


def run_tasks(req, fn):
    results, errors = {}, {}
    for task in req["tasks"]:
        t0 = time.perf_counter()
        try:
            q, mean = fn(task)
            results[task["id"]] = {
                "quantiles": [[float(x) for x in row] for row in q],
                "mean": None if mean is None else [float(x) for x in mean],
                "runtime_s": round(time.perf_counter() - t0, 4),
            }
        except Exception as e:  # noqa: BLE001 - report, never crash the batch
            errors[task["id"]] = f"{type(e).__name__}: {e}"
    return results, errors


def write_response(argv, req, results, errors, vers):
    out = {
        "model": req["model"],
        "versions": vers,
        "seed": req["settings"].get("seed", 0),
        "threads": req["settings"].get("threads", 4),
        "results": results,
        "errors": errors,
    }
    with open(argv[2], "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
