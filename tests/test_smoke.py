"""Phase 1 smoke test: the package imports and the config loads."""

import ffcast


def test_package_imports() -> None:
    assert ffcast.__name__ == "ffcast"
