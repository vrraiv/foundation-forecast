"""Live forecast registry (Phase 5): snapshot, forecast, seal, ledger, verify.

One run for an origin date does this, in order:

  1. snapshot: download the public data into `<root>/origins/<origin>/snapshot/` (raw files and
     the normalised change-log tables), never into the backtest's `data/normalised`;
  2. forecast: every active foundation model and every benchmark, in two information sets
     (`realtime`: the backtest rule applied at the origin; `live`: everything public at the run,
     see `ffcast.registry.live`), through the backtest's own panel, benchmark and worker code;
  3. seal: write `forecasts.parquet` and `status.parquet` byte-reproducibly, draw a random salt,
     copy the pins (config, lockfiles), and write `manifest.json` with the salted commitments,
     the snapshot digest, the pins' hashes, the weights digests and the code commit;
  4. ledger: append the SHA-256 of the manifest to the hash chain and time-stamp the entry.

Everything under `<root>` is private. The ledger holds hashes and dates only. `verify` checks
every ledger entry against the private files; `recompute` reruns the forecasts of a stored
origin from its stored snapshot and compares the files byte for byte."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import secrets
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..config import DEFAULT_CONFIG, Config, load_config
from ..origins import origin_date
from . import ledger as lg

REPO = Path(__file__).resolve().parents[3]
REGISTRY_ROOT = REPO / "registry"
LEDGER_PATH = REPO / "ledger" / "ledger.jsonl"
PREREG_PATH = REPO / "PREREGISTRATION.md"
AMENDMENTS_PATH = REPO / "PREREGISTRATION_AMENDMENTS.md"
FORMAT = 1
MODES = ("realtime", "live")

FORECAST_COLS = [
    "origin",
    "econ",
    "target",
    "freq",
    "model",
    "variant",
    "input_mode",
    "space",
    "step",
    "target_period",
    "quantile",
    "value",
    "mean",
    "series_id",
    "source_role",
]
STATUS_COLS = [
    "origin",
    "econ",
    "target",
    "freq",
    "model",
    "variant",
    "input_mode",
    "status",
    "note",
    "series_id",
    "source_role",
    "last_period",
    "last_level",
    "n_history",
    "n_vars",
]


@dataclass(frozen=True)
class Paths:
    root: Path = REGISTRY_ROOT
    ledger: Path = LEDGER_PATH

    def origin_dir(self, origin: dt.date | str) -> Path:
        o = origin if isinstance(origin, str) else origin.isoformat()
        return self.root / "origins" / o

    @property
    def prereg_copy(self) -> Path:
        return self.root / "prereg" / "PREREGISTRATION.md"


# ------------------------------------------------------------------ hashing helpers


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text_lf(path: Path) -> str:
    """SHA-256 of a text file with line endings normalised to LF, so that a Windows checkout
    and a Unix checkout of the same commit give the same hash."""
    return sha256_bytes(Path(path).read_bytes().replace(b"\r\n", b"\n"))


def commitment(salt_hex: str, path: Path) -> str:
    """Salted commitment to a file: SHA-256 over the salt bytes followed by the file bytes.
    Without the salt the hash of a small or guessable file could be confirmed by trial."""
    h = hashlib.sha256()
    h.update(bytes.fromhex(salt_hex))
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path) -> tuple[str, int]:
    """One hash for a directory: SHA-256 over sorted lines `relative/posix/path sha256`."""
    lines = []
    for p in sorted(Path(root).rglob("*")):
        if p.is_file():
            lines.append(f"{p.relative_to(root).as_posix()} {sha256_file(p)}\n")
    h = hashlib.sha256()
    for line in lines:
        h.update(line.encode("utf-8"))
    return h.hexdigest(), len(lines)


def design_hash(cfg: Config) -> str:
    """Hash of the parsed configuration (independent of comments and line endings). The
    pre-registration quotes it; a config change after the freeze changes it. The two operating
    switches of the registry (enabled, time-stamping mode) are left out: turning the registry on
    is not a design change."""
    raw = cfg.model_dump(mode="json")
    raw["registry"] = {
        k: v
        for k, v in raw["registry"].items()
        if k not in ("enabled", "opentimestamps", "ots_calendars")
    }
    s = json.dumps(raw, sort_keys=True, separators=(",", ":"), default=str)
    return sha256_bytes(s.encode("utf-8"))


def write_frame(df: pd.DataFrame, path: Path) -> None:
    """Byte-reproducible parquet: fixed column order, sorted rows, no pandas metadata."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    tbl = pa.Table.from_pandas(df, preserve_index=False).replace_schema_metadata(None)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(tbl, tmp, compression="zstd", version="2.6", write_statistics=False)
    os.replace(tmp, path)


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(REPO), capture_output=True, text=True, check=True)
    return r.stdout.strip()


def code_state() -> tuple[str, bool]:
    return _git("rev-parse", "HEAD"), bool(_git("status", "--porcelain"))


# ------------------------------------------------------------------ snapshot


def take_snapshot(cfg: Config, odir: Path, download_date: dt.date) -> dict:
    """Download into `<odir>/snapshot/{raw,normalised}`. Same pipeline as `ffcast data`, other
    folders, so the backtest's data (whose hashes sit in every backtest cache key) is untouched."""
    from ..data.pipeline import run_data
    from ..data.raw import RawStore

    snap = odir / "snapshot"
    store = RawStore(root=snap / "raw", today=download_date)
    rep = run_data(cfg, store, out_root=snap / "normalised")
    return {
        "series": len(rep.series),
        "problems": list(rep.problems),
        "download_failures": list(store.failures),
    }


def load_snapshot(odir: Path) -> tuple[pd.DataFrame, dict]:
    from ..data.store import read_all
    from ..eval.backtest import data_manifest

    norm = odir / "snapshot" / "normalised"
    return read_all(norm), data_manifest(norm)


# ------------------------------------------------------------------ forecasts


def _run_mode(
    cfg: Config,
    table: pd.DataFrame,
    manifest: dict,
    origin: dt.date,
    label: str,
    workdir: Path,
    models: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Benchmarks and foundation models for every target at one origin, through the backtest's
    stage functions, with all files under `workdir`. Rows come back labelled `label`."""
    from ..eval import backtest as bt
    from ..models import lean
    from ..models.runner import model_settings
    from ..models.weights import ensure_weights, weights_digest

    threads = str(int(cfg.backtest.get("threads_per_process", 4)))
    for var in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        os.environ[var] = threads
    if workdir.exists():
        shutil.rmtree(workdir)
    store = workdir / "store"
    (workdir / "requests").mkdir(parents=True)
    bt._G.clear()
    bt._G.update(
        cfg=cfg, table=table, manifest=manifest, revised_as_of=bt.revised_as_of_date(table)
    )
    cells = {(e, t, "realtime") for e in cfg.economies for t in cfg.targets[e]}
    res = bt.stage1_origin(origin, ["realtime"], cells, {m: set(cells) for m in models}, str(store))
    fms = cfg.foundation_models()
    digests = {}
    for m in models:
        wdir, man = ensure_weights(
            fms[m], allow_download=model_settings(cfg, m).get("allow_download", True)
        )
        digests[m] = weights_digest(man)
        tasks = res["tasks"].get(m, [])
        if tasks:
            req = bt.fm_request(cfg, m, wdir, digests[m], tasks, [origin.isoformat()])
            name = f"{m}__{origin.isoformat()}__{origin.isoformat()}.json"
            (workdir / "requests" / name).write_text(json.dumps(req), encoding="utf-8")
    (workdir / "task_meta.json").write_text(json.dumps(res["task_meta"]), encoding="utf-8")
    (workdir / "skipped.json").write_text(json.dumps(res["skipped"]), encoding="utf-8")
    (workdir / "weights.json").write_text(json.dumps(digests), encoding="utf-8")
    workers = lean.run_all(workdir / "requests", workdir / "responses") if models else {}
    rep = bt.stage3(workdir, cfg=cfg, root=store, manifest=manifest) if models else {}
    o = origin.isoformat()
    fparts, mparts = [], []
    for kind in ("bench", "fm"):
        fp, mp = store / "forecasts" / kind / f"{o}.parquet", store / "meta" / kind / f"{o}.parquet"
        if fp.exists():
            fparts.append(pd.read_parquet(fp))
        if mp.exists():
            mparts.append(pd.read_parquet(mp))
    f = pd.concat(fparts, ignore_index=True) if fparts else pd.DataFrame(columns=FORECAST_COLS)
    s = pd.concat(mparts, ignore_index=True) if mparts else pd.DataFrame(columns=STATUS_COLS)
    f["input_mode"] = label
    s["input_mode"] = label
    return f, s, {"workers": workers, **rep, "weights": digests}


def _canonical(f: pd.DataFrame, s: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    f = f[FORECAST_COLS].copy()
    f["step"] = f["step"].astype("int64")
    for c in ("quantile", "value", "mean"):
        f[c] = pd.to_numeric(f[c], errors="coerce").astype("float64")
    for c in ("origin", "econ", "target", "freq", "model", "variant", "input_mode", "space"):
        f[c] = f[c].astype(str)
    for c in ("target_period", "series_id", "source_role"):
        f[c] = f[c].astype(str)
    f = f.sort_values(
        ["input_mode", "econ", "target", "model", "variant", "space", "step", "quantile"],
        kind="stable",
    ).reset_index(drop=True)
    s = s[STATUS_COLS].copy()
    # skipped cells may appear once per stage (benchmarks, models): keep one row each
    s = s.drop_duplicates(["econ", "target", "model", "variant", "input_mode", "status", "note"])
    for c in STATUS_COLS:
        if c in ("last_level", "n_history", "n_vars"):
            s[c] = pd.to_numeric(s[c], errors="coerce").astype("float64")
        else:
            s[c] = s[c].astype("object").where(s[c].notna(), "").astype(str)
    s = s.sort_values(
        ["input_mode", "econ", "target", "model", "variant", "status", "note"], kind="stable"
    ).reset_index(drop=True)
    return f, s


def compute_forecasts(
    cfg: Config,
    table: pd.DataFrame,
    manifest: dict,
    origin: dt.date,
    workdir: Path,
    models: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Forecast and status frames of one origin in canonical form, from a snapshot table only."""
    from .live import live_inputs

    models = list(cfg.active_foundation_models()) if models is None else models
    info: dict = {}
    f1, s1, info["realtime"] = _run_mode(
        cfg, table, manifest, origin, "realtime", workdir / "realtime", models
    )
    cfg_live, table_live, notes = live_inputs(cfg, table, origin)
    f2, s2, info["live"] = _run_mode(
        cfg_live, table_live, manifest, origin, "live", workdir / "live", models
    )
    info["live_notes"] = notes
    f, s = _canonical(
        pd.concat([f1, f2], ignore_index=True), pd.concat([s1, s2], ignore_index=True)
    )
    return f, s, info


# ------------------------------------------------------------------ seal


def _pins(cfg: Config, models: list[str]) -> dict[str, Path]:
    fms = cfg.foundation_models()
    out = {"configs/default.yaml": DEFAULT_CONFIG, "uv.lock": REPO / "uv.lock"}
    for env in sorted({fms[m].env for m in models}):
        out[f"envs/{env}/uv.lock"] = REPO / "envs" / env / "uv.lock"
    return out


def stamp(
    paths: Paths,
    odir: Path | None,
    entry: dict,
    mode: str,
    calendars: list[str] | None = None,
) -> Path:
    """Time-stamp one ledger entry. `stub` writes a placeholder and contacts nobody. `ots`
    obtains an OpenTimestamps proof from public calendar servers (see `ots_stamp` for exactly
    what is sent)."""
    pdir = (odir if odir is not None else paths.root / "prereg") / "proofs"
    pdir.mkdir(parents=True, exist_ok=True)
    if mode == "stub":
        p = pdir / f"entry_{entry['seq']:04d}.ots.stub"
        p.write_text(
            json.dumps(
                {
                    "entry_hash": entry["entry_hash"],
                    "mode": "stub",
                    "note": "placeholder: no OpenTimestamps proof was requested for this entry",
                },
                indent=1,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return p
    if mode == "ots":
        digest_file = pdir / f"entry_{entry['seq']:04d}.txt"
        digest_file.write_text(entry["entry_hash"] + "\n", encoding="utf-8", newline="\n")
        proof = digest_file.with_suffix(".txt.ots")
        ots_stamp(digest_file, proof, calendars or DEFAULT_CALENDARS)
        return proof
    raise ValueError(f"unknown opentimestamps mode {mode!r}")


DEFAULT_CALENDARS = (
    "https://a.pool.opentimestamps.org",
    "https://b.pool.opentimestamps.org",
    "https://finney.calendar.eternitywall.com",
)


def ots_stamp(path: Path, proof: Path, calendars: tuple[str, ...] | list[str]) -> list[str]:
    """Write a standard OpenTimestamps proof for `path` next to it. What leaves the machine is
    one 32-byte value per calendar: SHA-256 of (SHA-256 of the file, followed by a random
    nonce), so not even the entry hash itself is sent. The proof starts as a calendar
    commitment ("pending") and can be upgraded to a Bitcoin attestation and verified later with
    any OpenTimestamps client; at least one calendar must accept, else nothing is written and
    the step can be repeated. (The reference command-line client does not run on Windows; this
    uses its library directly.)"""
    from opentimestamps.calendar import RemoteCalendar
    from opentimestamps.core.op import OpAppend, OpSHA256
    from opentimestamps.core.serialize import StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    with open(path, "rb") as fh:
        detached = DetachedTimestampFile.from_fd(OpSHA256(), fh)
    tip = detached.timestamp.ops.add(OpAppend(secrets.token_bytes(16))).ops.add(OpSHA256())
    accepted, errors = [], []
    for url in calendars:
        try:
            tip.merge(RemoteCalendar(url).submit(tip.msg, timeout=30))
            accepted.append(url)
        except Exception as e:  # noqa: BLE001 - any one calendar may be down
            errors.append(f"{url}: {type(e).__name__}")
    if not accepted:
        raise RuntimeError("no OpenTimestamps calendar accepted the digest: " + "; ".join(errors))
    tmp = proof.with_suffix(proof.suffix + ".tmp")
    with open(tmp, "wb") as fh:
        detached.serialize(StreamSerializationContext(fh))
    os.replace(tmp, proof)
    return accepted


def ots_check(path: Path, proof: Path) -> str | None:
    """None if `proof` is a well-formed OpenTimestamps proof of `path` with at least one
    attestation (pending or complete); otherwise what is wrong. This checks that the proof
    belongs to the file, not the Bitcoin attestation itself."""
    from opentimestamps.core.serialize import StreamDeserializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    try:
        with open(proof, "rb") as fh:
            detached = DetachedTimestampFile.deserialize(StreamDeserializationContext(fh))
    except Exception as e:  # noqa: BLE001
        return f"proof file unreadable ({type(e).__name__})"
    if detached.file_digest.hex() != sha256_file(path):
        return "proof is for a different file"
    if not list(detached.timestamp.all_attestations()):
        return "proof carries no attestation"
    return None


def seal(
    cfg: Config,
    paths: Paths,
    origin: dt.date,
    f: pd.DataFrame,
    s: pd.DataFrame,
    *,
    run_utc: str,
    run_date: dt.date,
    models: list[str],
    weights: dict[str, str],
    snapshot_report: dict,
    live_notes: list[dict],
    dry_run: bool,
    commit: str,
    dirty: bool,
) -> dict:
    """Write the private files of one origin and append its ledger entry. Returns the entry."""
    odir = paths.origin_dir(origin)
    write_frame(f, odir / "forecasts.parquet")
    write_frame(s, odir / "status.parquet")
    salt = secrets.token_hex(32)
    (odir / "salt.hex").write_text(salt + "\n", encoding="utf-8", newline="\n")
    pin_hashes = {}
    for rel, src in _pins(cfg, models).items():
        dst = odir / "pins" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))
        pin_hashes[rel] = sha256_file(dst)
    digest, nfiles = tree_digest(odir / "snapshot")
    fms = cfg.foundation_models()
    entries = lg.read(paths.ledger)
    counts = s.groupby(["input_mode", "status"]).size().rename("n").reset_index().to_dict("records")
    manifest = {
        "registry_format": FORMAT,
        "origin": origin.isoformat(),
        "run_utc": run_utc,
        "run_date": run_date.isoformat(),
        "late": run_date > origin,
        "days_late": (run_date - origin).days,
        "dry_run": dry_run,
        "code_commit": commit,
        "tree_dirty": dirty,
        "design_hash": design_hash(cfg),
        "preregistration_sha256": entries[0]["payload_sha256"] if entries else None,
        "amendments_sha256": sha256_text_lf(AMENDMENTS_PATH) if AMENDMENTS_PATH.exists() else None,
        "forecasts": {
            "file": "forecasts.parquet",
            "commitment_sha256": commitment(salt, odir / "forecasts.parquet"),
            "rows": int(len(f)),
        },
        "status": {
            "file": "status.parquet",
            "commitment_sha256": commitment(salt, odir / "status.parquet"),
            "rows": int(len(s)),
            "counts": counts,
        },
        "snapshot": {
            "digest": digest,
            "files": nfiles,
            "series": snapshot_report.get("series"),
            "problems": snapshot_report.get("problems", []),
            "download_failures": snapshot_report.get("download_failures", []),
        },
        "pins": pin_hashes,
        "models": {
            m: {"hf_id": fms[m].hf_id, "revision": fms[m].revision, "weights_digest": weights[m]}
            for m in models
        },
        "input_modes": list(MODES),
        "live_notes": live_notes,
    }
    mpath = odir / "manifest.json"
    mpath.write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return record(cfg, paths, origin)


def record(cfg: Config, paths: Paths, origin: dt.date) -> dict:
    """Ledger line and time stamp for a sealed origin. Safe to repeat: a run interrupted after
    its manifest was written, or after the ledger line but before the time stamp (which needs
    the network), is completed here without touching the sealed files. `recorded_utc` is the
    time the line is appended, i.e. when the commitment first exists in the ledger."""
    odir = paths.origin_dir(origin)
    mpath = odir / "manifest.json"
    if not mpath.exists():
        raise RuntimeError(f"origin {origin} has no sealed manifest")
    entries = lg.read(paths.ledger)
    entry = next(
        (e for e in entries if e["kind"] == "run" and e["origin"] == origin.isoformat()), None
    )
    if entry is None:
        entry = lg.append(
            paths.ledger,
            kind="run",
            origin=origin.isoformat(),
            payload_sha256=sha256_file(mpath),
            recorded_utc=dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        )
    elif entry["payload_sha256"] != sha256_file(mpath):
        raise RuntimeError(f"origin {origin}: the ledger line is for a different manifest")
    missing: list[str] = []
    _check_proof(odir, entry, missing)
    if missing:
        stamp(
            paths,
            odir,
            entry,
            cfg.registry.get("opentimestamps", "stub"),
            cfg.registry.get("ots_calendars"),
        )
    return entry


# ------------------------------------------------------------------ commands


def init_genesis(paths: Paths, prereg: Path = PREREG_PATH, cfg: Config | None = None) -> dict:
    """First ledger entry: the hash of the pre-registration text (LF line endings). A private
    copy of the text as hashed is kept under `<root>/prereg/`."""
    cfg = cfg or load_config()
    text = Path(prereg).read_bytes().replace(b"\r\n", b"\n")
    existing = lg.read(paths.ledger)
    if existing:
        e0 = existing[0]
        missing: list[str] = []
        _check_proof(paths.root / "prereg", e0, missing)
        if len(existing) == 1 and e0["payload_sha256"] == sha256_bytes(text) and missing:
            # entry 0 was appended but its time stamp failed (network): finish that only
            stamp(
                paths,
                None,
                e0,
                cfg.registry.get("opentimestamps", "stub"),
                cfg.registry.get("ots_calendars"),
            )
            return e0
        raise RuntimeError("the ledger already has entries; the pre-registration is entry 0")
    paths.prereg_copy.parent.mkdir(parents=True, exist_ok=True)
    paths.prereg_copy.write_bytes(text)
    entry = lg.append(
        paths.ledger,
        kind="preregistration",
        origin=None,
        payload_sha256=sha256_bytes(text),
        recorded_utc=dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    )
    stamp(
        paths,
        None,
        entry,
        cfg.registry.get("opentimestamps", "stub"),
        cfg.registry.get("ots_calendars"),
    )
    return entry


def current_origin(cfg: Config, today: dt.date) -> dt.date:
    """The origin a run started today belongs to: this month's origin if it has been reached,
    otherwise last month's (which makes the run late)."""
    o = origin_date(today.year, today.month, cfg.origins.day_of_month)
    if o <= today:
        return o
    y, m = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
    return origin_date(y, m, cfg.origins.day_of_month)


def status(paths: Paths, cfg: Config | None = None, today: dt.date | None = None) -> dict:
    """Where the registry stands today: the origin a run would be for, and whether that origin
    is done (in the ledger, with its proof). `due` is what a scheduled job acts on."""
    cfg = cfg or load_config()
    today = today or dt.date.today()
    origin = current_origin(cfg, today)
    entries = lg.read(paths.ledger)
    entry = next(
        (e for e in entries if e["kind"] == "run" and e["origin"] == origin.isoformat()), None
    )
    proof_problems: list[str] = []
    if entry is not None:
        _check_proof(paths.origin_dir(origin), entry, proof_problems)
    started = bool(entries) and entries[0]["kind"] == "preregistration"
    # an origin from before the pre-registration was hashed is not part of the record
    in_record = started and origin >= dt.datetime.fromisoformat(entries[0]["recorded_utc"]).date()
    done = entry is not None and not proof_problems
    return {
        "today": today.isoformat(),
        "enabled": bool(cfg.registry.get("enabled", False)),
        "preregistered": started,
        "origin": origin.isoformat(),
        "days_late": (today - origin).days,
        "in_ledger": entry is not None,
        "done": done,
        "due": bool(cfg.registry.get("enabled", False)) and in_record and not done,
    }


def registry_run(
    origin: dt.date | None = None,
    *,
    paths: Paths | None = None,
    cfg: Config | None = None,
    dry_run: bool = False,
    today: dt.date | None = None,
    models: list[str] | None = None,
    accept_incomplete: bool = False,
) -> dict:
    cfg = cfg or load_config()
    paths = paths or Paths()
    today = today or dt.date.today()
    origin = origin or current_origin(cfg, today)
    if origin > today:
        raise RuntimeError(f"origin {origin} is in the future (today is {today})")
    if origin != origin_date(origin.year, origin.month, cfg.origins.day_of_month):
        raise RuntimeError(f"{origin} is not an origin date under the configured calendar")
    commit, dirty = code_state()
    if not dry_run:
        if not cfg.registry.get("enabled", False):
            raise RuntimeError("registry.enabled is false: live runs wait for HUMAN GATE 5")
        if dirty:
            raise RuntimeError("uncommitted changes in the working tree: commit before a live run")
        if paths.root.resolve() != REGISTRY_ROOT.resolve():
            raise RuntimeError("a live run writes to the registry folder only")
    elif paths.root.resolve() == REGISTRY_ROOT.resolve():
        raise RuntimeError("a dry run must use a scratch root, not the registry folder")
    if not dry_run and origin != current_origin(cfg, today):
        raise RuntimeError(
            f"origin {origin} has been overtaken by {current_origin(cfg, today)}: a missed "
            "month is not back-filled"
        )
    entries = lg.read(paths.ledger)
    if not entries or entries[0]["kind"] != "preregistration":
        raise RuntimeError("the ledger has no pre-registration entry (run registry-init first)")
    odir = paths.origin_dir(origin)
    listed = any(e["kind"] == "run" and e["origin"] == origin.isoformat() for e in entries)
    if (odir / "manifest.json").exists():
        problems: list[str] = []
        if listed:
            entry = next(e for e in entries if e["kind"] == "run" and e["origin"] == str(origin))
            _check_proof(odir, entry, problems)
        if listed and not problems:
            raise RuntimeError(f"origin {origin} is already sealed and in the ledger")
        # sealed, but the ledger line or the time stamp is missing: finish that, change nothing
        return {
            "origin": origin.isoformat(),
            "completed": True,
            "entry": record(cfg, paths, origin),
        }
    if listed:
        raise RuntimeError(f"origin {origin} is in the ledger but its private files are missing")
    models = list(cfg.active_foundation_models()) if models is None else models
    run_utc = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    snap = take_snapshot(cfg, odir, dt.datetime.now(dt.UTC).date())
    if snap["download_failures"] and not accept_incomplete:
        # nothing is sealed: files already downloaded today are reused when the run is repeated
        raise RuntimeError(
            f"snapshot incomplete, {len(snap['download_failures'])} download(s) failed after "
            "retries; repeat the run, or pass accept_incomplete to seal without them: "
            + "; ".join(snap["download_failures"][:5])
        )
    table, manifest = load_snapshot(odir)
    f, s, info = compute_forecasts(cfg, table, manifest, origin, odir / "work", models)
    entry = seal(
        cfg,
        paths,
        origin,
        f,
        s,
        run_utc=run_utc,
        run_date=today,
        models=models,
        weights=info["live"]["weights"],
        snapshot_report=snap,
        live_notes=info["live_notes"],
        dry_run=dry_run,
        commit=commit,
        dirty=dirty,
    )
    return {
        "origin": origin.isoformat(),
        "late": today > origin,
        "entry": entry,
        "forecast_rows": int(len(f)),
        "status_counts": s.groupby(["input_mode", "status"]).size().to_dict(),
        "snapshot_problems": len(snap["problems"]),
        "workers": {k: info[k].get("workers") for k in MODES},
    }


def recompute(origin: dt.date, paths: Paths, cfg_path: Path | None = None) -> dict:
    """Rerun a stored origin from its stored snapshot and pinned config; compare byte for byte."""
    odir = paths.origin_dir(origin)
    man = json.loads((odir / "manifest.json").read_text(encoding="utf-8"))
    cfg = load_config(cfg_path or odir / "pins" / "configs" / "default.yaml")
    table, manifest = load_snapshot(odir)
    tmp = odir / "recompute"
    f, s, _ = compute_forecasts(cfg, table, manifest, origin, tmp / "work", list(man["models"]))
    write_frame(f, tmp / "forecasts.parquet")
    write_frame(s, tmp / "status.parquet")
    out = {
        k: sha256_file(tmp / f"{k}.parquet") == sha256_file(odir / f"{k}.parquet")
        for k in ("forecasts", "status")
    }
    if all(out.values()):
        shutil.rmtree(tmp)
    return out


def verify(paths: Paths) -> list[str]:
    """Check every ledger entry against the private files. Returns the list of problems."""
    from ..models.weights import MODELS_ROOT, weights_digest

    entries = lg.read(paths.ledger)
    problems = lg.check_chain(entries)
    if not entries:
        return ["the ledger is empty"]
    for e in entries:
        tag = f"entry {e.get('seq')}"
        if e.get("kind") == "preregistration":
            if not paths.prereg_copy.exists():
                problems.append(f"{tag}: private copy of the pre-registration is missing")
            elif sha256_file(paths.prereg_copy) != e["payload_sha256"]:
                problems.append(f"{tag}: pre-registration text does not match the ledger")
            _check_proof(paths.root / "prereg", e, problems)
            continue
        odir = paths.origin_dir(e["origin"])
        tag = f"{tag} (origin {e['origin']})"
        mpath = odir / "manifest.json"
        if not mpath.exists():
            problems.append(f"{tag}: manifest missing")
            continue
        if sha256_file(mpath) != e["payload_sha256"]:
            problems.append(f"{tag}: manifest does not match the ledger")
            continue
        man = json.loads(mpath.read_text(encoding="utf-8"))
        if man["origin"] != e["origin"]:
            problems.append(f"{tag}: manifest is for origin {man['origin']}")
        if man.get("preregistration_sha256") != entries[0]["payload_sha256"]:
            problems.append(f"{tag}: manifest names a different pre-registration")
        salt_path = odir / "salt.hex"
        if not salt_path.exists():
            problems.append(f"{tag}: salt missing")
        else:
            salt = salt_path.read_text(encoding="utf-8").strip()
            for key in ("forecasts", "status"):
                fp = odir / man[key]["file"]
                if not fp.exists():
                    problems.append(f"{tag}: {man[key]['file']} missing")
                    continue
                try:
                    ok = commitment(salt, fp) == man[key]["commitment_sha256"]
                except ValueError:
                    ok = False
                if not ok:
                    problems.append(f"{tag}: {man[key]['file']} or salt does not match")
        digest, nfiles = tree_digest(odir / "snapshot")
        if digest != man["snapshot"]["digest"]:
            problems.append(
                f"{tag}: data snapshot changed ({nfiles} files, manifest has "
                f"{man['snapshot']['files']})"
            )
        for rel, h in man["pins"].items():
            p = odir / "pins" / rel
            if not p.exists() or sha256_file(p) != h:
                problems.append(f"{tag}: pinned file {rel} missing or changed")
        for m, info in man["models"].items():
            wman = MODELS_ROOT / info["hf_id"].replace("/", "__") / info["revision"]
            wman = wman / "MANIFEST.sha256.json"
            if wman.exists() and (
                weights_digest(json.loads(wman.read_text(encoding="utf-8")))
                != info["weights_digest"]
            ):
                problems.append(f"{tag}: weights manifest of {m} differs from the run's digest")
        _check_proof(odir, e, problems)
    listed = {e["origin"] for e in entries if e.get("kind") == "run"}
    odirs = paths.root / "origins"
    if odirs.exists():
        for d in sorted(odirs.iterdir()):
            if (d / "manifest.json").exists() and d.name not in listed:
                problems.append(f"origin {d.name}: sealed run has no ledger entry")
    return problems


def _check_proof(base: Path, entry: dict, problems: list[str]) -> None:
    pdir = base / "proofs"
    stub = pdir / f"entry_{entry['seq']:04d}.ots.stub"
    ots = pdir / f"entry_{entry['seq']:04d}.txt.ots"
    if stub.exists():
        if json.loads(stub.read_text(encoding="utf-8")).get("entry_hash") != entry["entry_hash"]:
            problems.append(f"entry {entry['seq']}: time-stamp placeholder is for another hash")
    elif ots.exists():
        txt = pdir / f"entry_{entry['seq']:04d}.txt"
        if not txt.exists() or txt.read_text(encoding="utf-8").strip() != entry["entry_hash"]:
            problems.append(f"entry {entry['seq']}: time-stamped file is not the entry hash")
        elif (bad := ots_check(txt, ots)) is not None:
            problems.append(f"entry {entry['seq']}: {bad}")
    else:
        problems.append(f"entry {entry['seq']}: no time-stamp proof or placeholder")
