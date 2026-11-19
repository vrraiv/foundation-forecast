"""The configuration file is the only place targets, horizons and models are defined."""

from ffcast.config import load_config


def test_default_config_loads() -> None:
    cfg = load_config()
    assert set(cfg.economies) == {"CA", "EA"}
    assert cfg.origins.day_of_month == 25
    assert cfg.origins.strict_before is True
    assert cfg.horizons["M"] == [1, 3, 6, 12]
    assert cfg.horizons["Q"] == [1, 2, 4]


def test_every_economy_has_six_targets() -> None:
    cfg = load_config()
    for econ in cfg.economies:
        assert len(cfg.targets[econ]) == 6, econ


def test_models_are_pinned_by_revision() -> None:
    cfg = load_config()
    fms = cfg.foundation_models()
    assert {"chronos2", "timesfm25", "timesfm3", "tirex", "tirex2", "moirai2"} <= set(fms)
    for fm in fms.values():
        assert len(fm.revision) == 40
    # retired models keep their pinned entry but are not run by default or in the live registry
    active = cfg.active_foundation_models()
    assert "timesfm3" not in active
    assert set(active) == {"chronos2", "timesfm25", "tirex", "tirex2", "moirai2"}
    assert "timesfm3" not in cfg.models["benchmarks"]["combo_fm"]["of"]
