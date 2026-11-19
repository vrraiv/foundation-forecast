"""Registry (Phase 5): ledger chain, sealing, verification and tamper detection, on synthetic
files. No model runs and no network: the forecast frames are made up."""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ffcast.config import load_config as _load_config
from ffcast.registry import core
from ffcast.registry import ledger as lg
from ffcast.registry.live import live_inputs


def load_config():
    """The project configuration with time-stamping forced to the offline placeholder: tests
    never contact the public calendar servers (the key is not part of the design hash)."""
    cfg = _load_config()
    raw = cfg.model_dump()
    raw["registry"] = {**raw["registry"], "opentimestamps": "stub"}
    return type(cfg)(**raw)


@pytest.fixture(autouse=True)
def _no_timestamp_network(monkeypatch: pytest.MonkeyPatch):
    def refuse(*args, **kwargs):
        raise AssertionError("a test tried to request a real time stamp")

    monkeypatch.setattr(core, "ots_stamp", refuse)


ORIGINS = [dt.date(2026, 11, 25), dt.date(2026, 12, 25), dt.date(2027, 1, 25)]


def _frames(seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    rows = []
    for mode in core.MODES:
        for step in (1, 2):
            for q in (0.1, 0.5, 0.9):
                rows.append(
                    {
                        "origin": "x",
                        "econ": "CA",
                        "target": "cpi",
                        "freq": "M",
                        "model": "naive",
                        "variant": "univariate",
                        "input_mode": mode,
                        "space": "transformed",
                        "step": step,
                        "target_period": f"2026-1{step}",
                        "quantile": q,
                        "value": float(rng.normal()),
                        "mean": None,
                        "series_id": "s",
                        "source_role": "primary",
                    }
                )
    f = pd.DataFrame(rows)
    s = pd.DataFrame(
        [
            {
                "origin": "x",
                "econ": "CA",
                "target": "cpi",
                "freq": "M",
                "model": "naive",
                "variant": "univariate",
                "input_mode": m,
                "status": "ok",
                "note": "",
                "series_id": "s",
                "source_role": "primary",
                "last_period": "2026-10",
                "last_level": 1.0,
                "n_history": 100,
                "n_vars": 1,
            }
            for m in core.MODES
        ]
    )
    return core._canonical(f, s)


@pytest.fixture
def reg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A registry with a pre-registration and three sealed origins."""
    import ffcast.models.weights as w

    # the made-up weights digests must not be compared with weights on this machine
    monkeypatch.setattr(w, "MODELS_ROOT", tmp_path / "no-models")
    cfg = load_config()
    paths = core.Paths(root=tmp_path / "registry", ledger=tmp_path / "ledger" / "ledger.jsonl")
    prereg = tmp_path / "PREREGISTRATION.md"
    prereg.write_text("# Pre-registration\n\ntext\n", encoding="utf-8")
    core.init_genesis(paths, prereg, cfg)
    models = list(cfg.active_foundation_models())
    for i, o in enumerate(ORIGINS):
        snap = paths.origin_dir(o) / "snapshot" / "normalised"
        snap.mkdir(parents=True)
        (snap / "a.parquet").write_bytes(b"data-%d" % i)
        (snap / "manifest.json").write_text("{}", encoding="utf-8")
        f, s = _frames(i)
        core.seal(
            cfg,
            paths,
            o,
            f,
            s,
            run_utc=f"2026-11-25T18:00:0{i}+00:00",
            run_date=o,
            models=models,
            weights={m: "0" * 64 for m in models},
            snapshot_report={"series": 1, "problems": []},
            live_notes=[],
            dry_run=True,
            commit="0" * 40,
            dirty=False,
        )
    return paths


def test_clean_registry_verifies(reg: core.Paths) -> None:
    assert core.verify(reg) == []
    entries = lg.read(reg.ledger)
    assert [e["kind"] for e in entries] == ["preregistration", "run", "run", "run"]
    assert entries[1]["prev"] == entries[0]["entry_hash"]
    # the public ledger holds hashes and dates only
    for e in entries:
        assert set(e) == {*lg.FIELDS, "entry_hash"}


def test_forecast_file_is_byte_reproducible(tmp_path: Path) -> None:
    f, s = _frames(7)
    core.write_frame(f, tmp_path / "a.parquet")
    core.write_frame(
        f.sample(frac=1.0, random_state=1).pipe(lambda d: core._canonical(d, s)[0]),
        tmp_path / "b.parquet",
    )
    assert core.sha256_file(tmp_path / "a.parquet") == core.sha256_file(tmp_path / "b.parquet")


def test_salted_commitment_differs_from_plain_hash(reg: core.Paths) -> None:
    odir = reg.origin_dir(ORIGINS[0])
    man = json.loads((odir / "manifest.json").read_text(encoding="utf-8"))
    plain = core.sha256_file(odir / "forecasts.parquet")
    assert man["forecasts"]["commitment_sha256"] != plain
    assert plain not in (odir / "manifest.json").read_text(encoding="utf-8")
    assert plain not in reg.ledger.read_text(encoding="utf-8")


def _tamper_forecast(reg: core.Paths) -> None:
    odir = reg.origin_dir(ORIGINS[1])
    f = pd.read_parquet(odir / "forecasts.parquet")
    f.loc[0, "value"] += 1e-9
    core.write_frame(f, odir / "forecasts.parquet")


def _tamper_status(reg: core.Paths) -> None:
    odir = reg.origin_dir(ORIGINS[1])
    s = pd.read_parquet(odir / "status.parquet")
    s.loc[0, "status"] = "error"
    core.write_frame(s, odir / "status.parquet")


def _tamper_snapshot(reg: core.Paths) -> None:
    (reg.origin_dir(ORIGINS[0]) / "snapshot" / "normalised" / "a.parquet").write_bytes(b"other")


def _add_snapshot_file(reg: core.Paths) -> None:
    (reg.origin_dir(ORIGINS[0]) / "snapshot" / "normalised" / "b.parquet").write_bytes(b"new")


def _tamper_manifest(reg: core.Paths) -> None:
    p = reg.origin_dir(ORIGINS[2]) / "manifest.json"
    p.write_text(p.read_text(encoding="utf-8").replace('"late": false', '"late": true'), "utf-8")


def _tamper_salt(reg: core.Paths) -> None:
    (reg.origin_dir(ORIGINS[0]) / "salt.hex").write_text("ab" * 32 + "\n", encoding="utf-8")


def _tamper_pin(reg: core.Paths) -> None:
    p = reg.origin_dir(ORIGINS[0]) / "pins" / "uv.lock"
    p.write_bytes(p.read_bytes() + b"\n# edited\n")


def _tamper_prereg(reg: core.Paths) -> None:
    reg.prereg_copy.write_text("# Pre-registration\n\nother text\n", encoding="utf-8")


def _edit_ledger_field(reg: core.Paths) -> None:
    lines = reg.ledger.read_text(encoding="utf-8").splitlines()
    e = json.loads(lines[2])
    e["recorded_utc"] = "2026-01-01T00:00:00+00:00"
    lines[2] = json.dumps(e, sort_keys=True, separators=(",", ":"))
    reg.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _edit_ledger_and_rehash(reg: core.Paths) -> None:
    """Swap one manifest and recompute that entry's own hash: the next entry's `prev` breaks."""
    lines = reg.ledger.read_text(encoding="utf-8").splitlines()
    e = json.loads(lines[1])
    e["payload_sha256"] = "f" * 64
    e["entry_hash"] = lg.entry_hash(e)
    lines[1] = json.dumps(e, sort_keys=True, separators=(",", ":"))
    reg.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _delete_middle_entry(reg: core.Paths) -> None:
    lines = reg.ledger.read_text(encoding="utf-8").splitlines()
    del lines[2]
    reg.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _delete_last_entry(reg: core.Paths) -> None:
    lines = reg.ledger.read_text(encoding="utf-8").splitlines()
    reg.ledger.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")


def _reorder_entries(reg: core.Paths) -> None:
    lines = reg.ledger.read_text(encoding="utf-8").splitlines()
    lines[1], lines[2] = lines[2], lines[1]
    reg.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _delete_forecast(reg: core.Paths) -> None:
    (reg.origin_dir(ORIGINS[1]) / "forecasts.parquet").unlink()


def _delete_origin(reg: core.Paths) -> None:
    shutil.rmtree(reg.origin_dir(ORIGINS[1]))


def _swap_forecasts_between_origins(reg: core.Paths) -> None:
    a = reg.origin_dir(ORIGINS[0]) / "forecasts.parquet"
    b = reg.origin_dir(ORIGINS[1]) / "forecasts.parquet"
    x, y = a.read_bytes(), b.read_bytes()
    a.write_bytes(y)
    b.write_bytes(x)


def _remove_proof(reg: core.Paths) -> None:
    for p in (reg.origin_dir(ORIGINS[0]) / "proofs").iterdir():
        p.unlink()


@pytest.mark.parametrize(
    "tamper",
    [
        _tamper_forecast,
        _tamper_status,
        _tamper_snapshot,
        _add_snapshot_file,
        _tamper_manifest,
        _tamper_salt,
        _tamper_pin,
        _tamper_prereg,
        _edit_ledger_field,
        _edit_ledger_and_rehash,
        _delete_middle_entry,
        _delete_last_entry,
        _reorder_entries,
        _delete_forecast,
        _delete_origin,
        _swap_forecasts_between_origins,
        _remove_proof,
    ],
)
def test_tampering_makes_verify_fail(reg: core.Paths, tamper) -> None:
    tamper(reg)
    assert core.verify(reg) != []


def test_ledger_is_append_only(reg: core.Paths) -> None:
    with pytest.raises(RuntimeError, match="already has a ledger entry"):
        lg.append(
            reg.ledger,
            kind="run",
            origin=ORIGINS[0].isoformat(),
            payload_sha256="a" * 64,
            recorded_utc="2027-01-01T00:00:00+00:00",
        )
    with pytest.raises(RuntimeError, match="first ledger entry"):
        lg.append(
            reg.ledger,
            kind="preregistration",
            origin=None,
            payload_sha256="a" * 64,
            recorded_utc="2027-01-01T00:00:00+00:00",
        )


def test_run_needs_a_preregistration_entry(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="must start with it"):
        lg.append(
            tmp_path / "ledger.jsonl",
            kind="run",
            origin="2026-11-25",
            payload_sha256="a" * 64,
            recorded_utc="2026-11-25T00:00:00+00:00",
        )


def test_live_run_is_refused_before_gate_5(tmp_path: Path) -> None:
    cfg = load_config()
    if cfg.registry.get("enabled", False):
        pytest.skip("registry enabled by the owner")
    with pytest.raises(RuntimeError, match="HUMAN GATE 5"):
        core.registry_run(dt.date(2026, 10, 26), cfg=cfg, today=dt.date(2026, 11, 19))
    with pytest.raises(RuntimeError, match="scratch root"):
        core.registry_run(dt.date(2026, 10, 26), cfg=cfg, today=dt.date(2026, 11, 19), dry_run=True)
    with pytest.raises(RuntimeError, match="future"):
        core.registry_run(
            dt.date(2026, 11, 25),
            cfg=cfg,
            today=dt.date(2026, 11, 19),
            dry_run=True,
            paths=core.Paths(root=tmp_path, ledger=tmp_path / "l.jsonl"),
        )


def test_current_origin_and_lateness() -> None:
    cfg = load_config()
    assert core.current_origin(cfg, dt.date(2026, 11, 25)) == dt.date(2026, 11, 25)
    assert core.current_origin(cfg, dt.date(2026, 11, 27)) == dt.date(2026, 11, 25)
    assert core.current_origin(cfg, dt.date(2026, 11, 19)) == dt.date(2026, 10, 26)
    assert core.current_origin(cfg, dt.date(2027, 1, 4)) == dt.date(2026, 12, 25)


def _table(rows: list[tuple[str, str, float, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "series_id": [r[0] for r in rows],
            "ref_period": [r[1] for r in rows],
            "value": [r[2] for r in rows],
            "vintage_date": [dt.date.fromisoformat(r[3]) for r in rows],
            "action": "R",
            "source": "t",
            "vintage_label": "t",
        }
    )


def test_live_series_joins_national_data_to_vintage_history() -> None:
    """Canadian retail: the national series starts late; earlier periods take the vintage
    source's growth rates, later ones the national series', and vintages dated after the origin
    become visible in live mode only."""
    cfg = load_config()
    nat = "statcan:20100067:v1446870183"
    oecd = "oecd:CA.M.TOVM.IX.G47"
    months = [f"2024-{m:02d}" for m in range(1, 13)]
    oecd_vals = [100.0 * 1.01**i for i in range(12)]
    rows = [(oecd, p, v, "2026-11-01") for p, v in zip(months, oecd_vals, strict=True)]
    # a newer edition, dated after the origin by the conservative rule, revises the last month
    rows.append((oecd, months[-1], oecd_vals[-1] * 1.5, "2026-12-01"))
    # national series: starts 2024-07, other units (x 500), and has one more month
    nat_months = months[6:] + ["2025-01"]
    nat_vals = [500.0 * v for v in oecd_vals[6:]] + [500.0 * oecd_vals[-1] * 1.02]
    rows += [(nat, p, v, "2026-11-25") for p, v in zip(nat_months, nat_vals, strict=True)]
    table = _table(rows)
    origin = dt.date(2026, 11, 25)
    cfg_live, t_live, notes = live_inputs(cfg, table, origin)
    assert cfg_live.targets["CA"]["retail"].vintages == {"source": "live"}
    from ffcast.data.store import as_of

    s = as_of(t_live, ["live:CA.retail"], origin)["live:CA.retail"]
    assert list(s.index) == months + ["2025-01"]
    growth = np.diff(np.log(s.to_numpy()))
    assert np.allclose(growth[:11], np.log(1.01))  # vintage growth before the join, national after
    assert np.isclose(growth[11], np.log(1.02))
    assert np.isclose(s.loc["2024-07"], nat_vals[0])  # levels are the national series' levels
    # the backtest rule at the same origin does not see the edition dated 2026-12-01 ...
    assert np.isclose(as_of(table, [oecd], origin)[oecd].loc["2024-12"], oecd_vals[-1])
    # ... and live mode does
    assert np.isclose(as_of(t_live, [oecd], origin)[oecd].loc["2024-12"], oecd_vals[-1] * 1.5)
    note = next(n for n in notes if n.get("target") == "retail" and n.get("econ") == "CA")
    assert note["history_from"] == oecd and note["joined_at"] == "2024-07"


def test_preregistration_quotes_the_current_design_hash() -> None:
    """The pre-registration names the configuration it describes; a config change that alters
    the design must be noticed (before the freeze: update the text; after it: write an
    amendment)."""
    import re

    text = core.PREREG_PATH.read_text(encoding="utf-8")
    m = re.search(r"^Design hash: `([0-9a-f]{64})`$", text, flags=re.M)
    assert m, "PREREGISTRATION.md has no design hash line"
    assert m.group(1) == core.design_hash(load_config())


def test_design_hash_ignores_the_operating_switches() -> None:
    cfg = load_config()
    raw = cfg.model_dump()
    raw["registry"] = {**raw["registry"], "enabled": True, "opentimestamps": "ots"}
    assert core.design_hash(type(cfg)(**raw)) == core.design_hash(cfg)
    raw["horizons"] = {"M": [1, 3], "Q": [1]}
    assert core.design_hash(type(cfg)(**raw)) != core.design_hash(cfg)


def test_interrupted_run_is_completed_without_touching_sealed_files(
    reg: core.Paths, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sealed but not in the ledger, or in the ledger but not time-stamped: `record` finishes
    the job and the sealed files keep their bytes."""
    cfg = load_config()
    o = ORIGINS[2]
    odir = reg.origin_dir(o)
    before = {p.name: core.sha256_file(p) for p in odir.iterdir() if p.is_file()}
    # 1. the time stamp was never written
    for p in (odir / "proofs").iterdir():
        p.unlink()
    assert core.verify(reg) != []
    core.record(cfg, reg, o)
    assert core.verify(reg) == []
    # 2. the ledger line was never appended either
    lines = reg.ledger.read_text(encoding="utf-8").splitlines()
    reg.ledger.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    for p in (odir / "proofs").iterdir():
        p.unlink()
    assert core.verify(reg) != []
    entry = core.record(cfg, reg, o)
    assert entry["origin"] == o.isoformat() and core.verify(reg) == []
    assert before == {p.name: core.sha256_file(p) for p in odir.iterdir() if p.is_file()}
    # 3. nothing to do: no second line
    n = len(lg.read(reg.ledger))
    core.record(cfg, reg, o)
    assert len(lg.read(reg.ledger)) == n


def test_missed_month_is_not_backfilled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = load_config()
    raw = cfg.model_dump()
    raw["registry"] = {**raw["registry"], "enabled": True}
    cfg_on = type(cfg)(**raw)
    monkeypatch.setattr(core, "code_state", lambda: ("0" * 40, False))
    monkeypatch.setattr(core, "REGISTRY_ROOT", tmp_path)
    paths = core.Paths(root=tmp_path, ledger=tmp_path / "ledger.jsonl")
    with pytest.raises(RuntimeError, match="not back-filled"):
        core.registry_run(
            dt.date(2026, 10, 26), cfg=cfg_on, paths=paths, today=dt.date(2026, 11, 26)
        )
    # the current origin gets past that check (and stops at the missing pre-registration)
    with pytest.raises(RuntimeError, match="no pre-registration entry"):
        core.registry_run(
            dt.date(2026, 11, 25), cfg=cfg_on, paths=paths, today=dt.date(2026, 11, 26)
        )


def test_opentimestamps_proof_check(tmp_path: Path) -> None:
    """A proof built with the library (no network: a made-up calendar attestation) is accepted
    for its file and rejected for any other file or when damaged."""
    from opentimestamps.core.notary import PendingAttestation
    from opentimestamps.core.op import OpSHA256
    from opentimestamps.core.serialize import StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    f = tmp_path / "entry.txt"
    f.write_text("ab" * 32 + "\n", encoding="utf-8", newline="\n")
    with open(f, "rb") as fh:
        d = DetachedTimestampFile.from_fd(OpSHA256(), fh)
    d.timestamp.attestations.add(PendingAttestation("https://calendar.example"))
    proof = tmp_path / "entry.txt.ots"
    with open(proof, "wb") as fh:
        d.serialize(StreamSerializationContext(fh))
    assert core.ots_check(f, proof) is None
    other = tmp_path / "other.txt"
    other.write_text("cd" * 32 + "\n", encoding="utf-8", newline="\n")
    assert core.ots_check(other, proof) == "proof is for a different file"
    proof.write_bytes(proof.read_bytes()[:20])
    assert core.ots_check(f, proof) is not None


def test_status_says_when_a_run_is_due(reg: core.Paths) -> None:
    cfg = load_config()
    raw = cfg.model_dump()
    raw["registry"] = {**raw["registry"], "enabled": True}
    on = type(cfg)(**raw)
    # the fixture's pre-registration line is stamped now; pretend it was made before the origins
    assert core.status(reg, on, dt.date(2026, 11, 25))["in_ledger"] is True
    assert core.status(reg, on, dt.date(2026, 11, 25))["due"] is False
    st = core.status(reg, on, dt.date(2027, 2, 26))
    assert st["origin"] == "2027-02-25" and st["in_ledger"] is False and st["days_late"] == 1
    assert st["due"] is True
    assert core.status(reg, cfg, dt.date(2027, 2, 26))["due"] is cfg.registry.get("enabled", False)


def _load_check_ledger():
    import importlib.util

    p = core.REPO / "scripts" / "check_ledger.py"
    spec = importlib.util.spec_from_file_location("check_ledger", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_public_ledger_check_agrees_with_the_registry(reg: core.Paths) -> None:
    """scripts/check_ledger.py is a standalone copy of the chain rules for the public workflow."""
    cl = _load_check_ledger()
    entries = lg.read(reg.ledger)
    assert cl.check_chain(entries) == [] and lg.check_chain(entries) == []
    assert all(cl.entry_hash(e) == lg.entry_hash(e) for e in entries)
    bad = [dict(e) for e in entries]
    bad[1]["payload_sha256"] = "f" * 64
    assert cl.check_chain(bad) and lg.check_chain(bad)
    assert cl.check_chain(entries[:1] + entries[2:]) and cl.check_chain(entries[1:])
    # presence: origins due after the pre-registration line's date
    e0 = dict(entries[0], recorded_utc="2026-11-20T00:00:00+00:00")
    exp = cl.expected_origins([e0], dt.date(2027, 1, 26), 25, 1)
    assert exp == ["2026-11-25", "2026-12-25", "2027-01-25"]
    assert cl.expected_origins([e0], dt.date(2027, 1, 25), 25, 1) == ["2026-11-25", "2026-12-25"]
    assert cl.origin_date(2026, 10, 25) == dt.date(2026, 10, 26)
