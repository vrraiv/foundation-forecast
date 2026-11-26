"""Disclosure under Amendment 1: byte-identical bundles, refusals, and the public verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from ffcast.registry import core, publish
from ffcast.registry import ledger as lg
from test_registry import ORIGINS, _no_timestamp_network, reg  # noqa: F401

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("vp", REPO / "scripts" / "verify_published.py")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)


def _fake_ots(paths: core.Paths, origin: str) -> None:
    """Replace the test's placeholder by a (fake) OpenTimestamps proof pair."""
    e = next(x for x in lg.read(paths.ledger) if x.get("origin") == origin)
    pdir = paths.origin_dir(origin) / "proofs"
    for p in pdir.glob("*.stub"):
        p.unlink()
    (pdir / f"entry_{e['seq']:04d}.txt").write_text(e["entry_hash"] + "\n", encoding="utf-8")
    (pdir / f"entry_{e['seq']:04d}.txt.ots").write_bytes(b"fake proof")


def test_refuses_without_a_real_time_stamp(reg: core.Paths, tmp_path: Path) -> None:  # noqa: F811
    with pytest.raises(publish.PublishError, match="time-stamped"):
        publish.bundle(reg, ORIGINS[0].isoformat(), tmp_path / "out", allow_dry_run=True)


def test_refuses_unknown_origin(reg: core.Paths, tmp_path: Path) -> None:  # noqa: F811
    with pytest.raises(publish.PublishError, match="no ledger entry"):
        publish.bundle(reg, "2030-01-25", tmp_path / "out", allow_dry_run=True)


def test_bundle_is_byte_identical_and_verifies(reg: core.Paths, tmp_path: Path) -> None:  # noqa: F811
    o = ORIGINS[1].isoformat()
    _fake_ots(reg, o)
    odir = reg.origin_dir(o)
    before = {p.name: core.sha256_file(p) for p in odir.iterdir() if p.is_file()}
    out = tmp_path / "out"
    staged = publish.bundle(reg, o, out, allow_dry_run=True)
    names = {p.name for p in staged}
    assert {
        "manifest.json",
        "salt.hex",
        "forecasts.parquet",
        "status.parquet",
        "forecasts.csv",
        "README.md",
    } <= names
    for n in publish.SEALED:
        assert core.sha256_file(out / n) == core.sha256_file(odir / n)
    # sealed files untouched
    assert before == {p.name: core.sha256_file(p) for p in odir.iterdir() if p.is_file()}
    assert vp.main(reg.ledger, out) == []
    # tampering is caught by the public verifier
    (out / "forecasts.parquet").write_bytes((out / "forecasts.parquet").read_bytes() + b"x")
    assert any("forecasts.parquet" in p for p in vp.main(reg.ledger, out))


def test_refuses_tampered_forecasts(reg: core.Paths, tmp_path: Path) -> None:  # noqa: F811
    o = ORIGINS[2].isoformat()
    _fake_ots(reg, o)
    f = reg.origin_dir(o) / "forecasts.parquet"
    f.write_bytes(f.read_bytes() + b"x")
    with pytest.raises(publish.PublishError, match="commitment"):
        publish.bundle(reg, o, tmp_path / "out", allow_dry_run=True)


def test_refuses_dry_run_manifests(reg: core.Paths, tmp_path: Path) -> None:  # noqa: F811
    o = ORIGINS[0].isoformat()
    _fake_ots(reg, o)
    with pytest.raises(publish.PublishError, match="dry-run"):
        publish.bundle(reg, o, tmp_path / "out")


def test_pending_needs_a_public_ledger_line_and_no_release(reg: core.Paths) -> None:  # noqa: F811
    runs = [e for e in lg.read(reg.ledger) if e["kind"] == "run"]
    public = {e["entry_hash"] for e in runs[:2]}  # third line not pushed yet
    released = {f"registry-{runs[0]['origin']}"}
    assert publish.pending(reg, released, public) == [runs[1]["origin"]]
    assert publish.pending(reg, released, set()) == []
