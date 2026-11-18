"""Phase 1 smoke test: the package imports and the config loads."""

import ffcast


def test_package_imports() -> None:
    assert ffcast.__name__ == "ffcast"


def test_stage3_keeps_every_model_when_task_ids_repeat(tmp_path):
    """Task ids repeat across models (same target, same variant); stage 3 must report all of
    them rather than the last model only (regression: 2026-11-18)."""
    import json

    from ffcast.models.smoke import stage3

    w = tmp_path
    (w / "requests").mkdir()
    (w / "responses").mkdir()
    (w / "bench_rows.json").write_text("[]", encoding="utf-8")
    meta = {}
    for m in ("alpha", "beta"):
        meta[f"{m}:CA.gdp.univariate"] = {
            "tid": "CA.gdp.univariate",
            "econ": "CA",
            "target": "gdp",
            "model": m,
            "variant": "univariate",
            "horizon": 2,
            "lo": -10.0,
            "hi": 10.0,
            "expected_step1": "2024-Q2",
            "n_vars": 1,
        }
        (w / "requests" / f"{m}.json").write_text(
            json.dumps({"weights_digest": "abc123def456xyz"}), encoding="utf-8"
        )
        (w / "responses" / f"{m}.json").write_text(
            json.dumps(
                {
                    "results": {
                        "CA.gdp.univariate": {
                            "quantiles": [[0.0, 0.5, 1.0], [0.0, 0.5, 1.0]],
                            "runtime_s": 0.1,
                        }
                    },
                    "errors": {},
                    "versions": {},
                    "wall_s": 1.0,
                }
            ),
            encoding="utf-8",
        )
    (w / "task_meta.json").write_text(json.dumps(meta), encoding="utf-8")
    df = stage3(w, w / "out.csv")
    checked = df[df["variant"] != "wall"]
    assert sorted(checked["model"]) == ["alpha", "beta"]
    assert checked["ok"].all()
    assert sorted(df[df["variant"] == "wall"]["model"]) == ["alpha", "beta"]
