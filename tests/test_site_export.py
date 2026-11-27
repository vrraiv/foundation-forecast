"""The site export (Phase 7): exported numbers equal the published tables.

Three checks need only committed files, so they run on a clean clone:

1. every figure in the public results document (`docs/results_backtest_2026-11-19.md`: the
   headline tables and the first 400 rows of each view) equals the exported score, to the three
   decimals the document prints;
2. every exported score row is reproduced from the exported per-origin forecasts and outturns
   (n exactly; RMSFE, MAE and mean error within the rounding of the series files);
3. the export contains only what it should (no retired model, no levels variant, no stray file).

One check needs the private store and is skipped without it: re-running the export reproduces
the committed files byte for byte. Set FFCAST_BACKTEST_ROOT to point at a store elsewhere.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ffcast import site_export as se
from ffcast.config import load_config
from ffcast.eval.store import BACKTEST_ROOT

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "site" / "public" / "data"
DOC = REPO / "docs" / "results_backtest_2026-11-19.md"
CFG = load_config()
RETIRED = set(CFG.models.get("retired") or [])
PRINTED = 5e-4 + 1e-6  # the document prints three decimals; the export keeps six
SERIES = 1e-4 + 1e-6  # outturn and median are each rounded to four decimals

pytestmark = pytest.mark.skipif(
    not (DATA / "scores.json").exists(), reason="no site export committed"
)

HEADLINE = {
    "mode": "realtime",
    "outturn": "first_release",
    "sample": "full",
    "window": "primary",
    "split": "all",
}
LABELS = {
    "Scored forecasts (n)": "n",
    "Relative RMSFE to AR": "rel_rmsfe",
    "Relative MAE to AR": "rel_mae",
    "Diebold-Mariano p-value vs AR": "dm_p",
    "RMSFE (transformed units)": "rmsfe",
    "Mean error (outturn minus forecast)": "bias",
    "Weighted quantile loss": "wql",
    "80% interval coverage": "cov80",
    "Model confidence set (90%) membership": "mcs",
}
VIEWS = {  # section number in the document -> the dimension that varies, and what else differs from the headline
    "5.1": ("mode", {}),
    "5.1b": ("mode", {"outturn": "revised_12m"}),
    "5.2": ("outturn", {}),
    "5.3": ("split", {}),
    "5.3b": ("split", {}),
    "5.4": ("sample", {}),
    "5.5": ("window", {}),
}
DIMS = ["econ", "target", "h", "model", "variant", "mode", "outturn", "sample", "window", "split"]


def _load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def scores() -> dict[tuple, dict]:
    out = {}
    for name in ("scores.json", "scores_more.json"):
        f = _load(name)
        for row in f["rows"]:
            r = dict(zip(f["cols"], row, strict=True))
            key = tuple(r[d] for d in DIMS)
            assert key not in out, f"duplicate row {key}"
            out[key] = r
    return out


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _same(text: str, value, what) -> None:
    if text == "":
        assert value is None, what
    elif text in ("yes", "no"):
        assert value is (text == "yes"), what
    else:
        assert value is not None and abs(float(text) - value) <= PRINTED, (what, text, value)


def test_scores_equal_the_published_headline_tables(scores) -> None:
    lines = DOC.read_text(encoding="utf-8").splitlines()
    a = lines.index("## 4. Headline tables")
    b = next(i for i in range(a + 1, len(lines)) if lines[i].startswith("## "))
    econ = target = metric = hs = None
    checked, seen = 0, set()
    for line in lines[a:b]:
        if line.startswith("### "):
            econ, target = (x.strip() for x in line[4:].split("/"))
        elif line.startswith("**"):
            metric, hs = LABELS[line.strip("*")], None
        elif line.startswith("| model / variant"):
            hs = [int(c[1:]) for c in _cells(line)[1:]]
        elif line.startswith("| ") and hs:
            c = _cells(line)
            model, variant = (x.strip() for x in c[0].split("/"))
            if (
                model in RETIRED or variant not in se.VARIANTS
            ):  # the membership table also lists levels variants
                continue
            for h, text in zip(hs, c[1:], strict=True):
                key = (econ, target, h, model, variant, *HEADLINE.values())
                row = scores.get(key)
                if row is None:
                    assert text == "", f"{key} is in the document but not in the export"
                    continue
                _same(text, row[metric], (key, metric))
                seen.add(key)
                checked += 1
    exported = {k for k, r in scores.items() if all(r[d] == v for d, v in HEADLINE.items())}
    assert seen == exported, "the export and the document's headline tables cover different cells"
    assert checked > 5000, checked


def test_scores_equal_the_published_views(scores) -> None:
    lines = DOC.read_text(encoding="utf-8").splitlines()
    checked = {}
    view = cols = None
    for line in lines:
        if line.startswith("### 5."):
            view, cols = VIEWS.get(line.split()[1]), None
            name = line.split()[1]
        elif line.startswith("#"):
            view = None
        elif view and line.startswith("| econ |"):
            cols = _cells(line)
        elif view and cols and line.startswith("| ") and not line.startswith("|---"):
            free, fixed = view
            c = dict(zip(cols, _cells(line), strict=True))
            if c["model"] in RETIRED:
                continue
            for col, text in c.items():
                if ":" not in col:
                    continue
                metric, value = col.split(":")
                dims = {**HEADLINE, **fixed, free: value}
                key = (
                    c["econ"],
                    c["target"],
                    int(c["horizon"]),
                    c["model"],
                    c["variant"],
                    *dims.values(),
                )
                row = scores.get(key)
                if row is None:
                    assert text == "", f"{key} is in the document but not in the export"
                    continue
                _same(text, row[metric], (key, metric))
                checked[name] = checked.get(name, 0) + 1
    assert set(checked) == set(VIEWS), checked
    assert all(n > 300 for n in checked.values()), checked


def _in_covid(period: str, window: list[str]) -> bool:
    freq = "Q" if "Q" in period else "M"
    p = pd.Period(period.replace("-Q", "Q"), freq)
    return pd.Period(window[0], freq) <= p <= pd.Period(window[1], freq)


def test_every_main_score_is_reproduced_from_the_exported_series(scores) -> None:
    meta = _load("meta.json")
    fms = meta["foundation_models"]
    done = set()
    for econ, targets in meta["targets"].items():
        for target in targets:
            for cell_key, cell in _load(f"series_{econ}_{target}.json").items():
                h, mode = cell_key.split("|")
                origin = np.array(cell["origin"])
                y = np.array(cell["y"], dtype=float)
                covid = np.array([_in_covid(p, meta["covid_window"]) for p in cell["period"]])
                for mk, (med, lo, hi) in cell["m"].items():
                    model, variant = mk.split("|")
                    med = np.array(med, dtype=float)
                    have = ~np.isnan(med)
                    assert len(hi) == len(lo) == len(y)
                    assert all(
                        (a is None) == (b is None) == (c is None)
                        for a, b, c in zip(cell["m"][mk][0], lo, hi, strict=True)
                    )
                    splits = {"all": np.ones(len(y), dtype=bool)}
                    if model in fms:
                        wd = fms[model]["weights_date"]
                        splits |= {"pre": origin < wd, "post": origin >= wd}
                        if fms[model]["training_cutoff"]:
                            tc = fms[model]["training_cutoff"] + "-01"
                            splits |= {"pre_cutoff": origin < tc, "post_cutoff": origin >= tc}
                    for sample, smask in (
                        ("full", np.ones(len(y), dtype=bool)),
                        ("ex_covid", ~covid),
                    ):
                        for split, pmask in splits.items():
                            mask = have & smask & pmask
                            key = (
                                econ,
                                target,
                                int(h),
                                model,
                                variant,
                                mode,
                                "first_release",
                                sample,
                                "primary",
                                split,
                            )
                            row = scores.get(key)
                            if not mask.any():
                                assert row is None, key
                                continue
                            assert row is not None, (
                                f"{key}: in the series files but not in the scores"
                            )
                            e = y[mask] - med[mask]
                            assert row["n"] == int(mask.sum()), key
                            assert abs(row["rmsfe"] - np.sqrt(np.mean(e**2))) <= SERIES, key
                            assert abs(row["mae"] - np.mean(np.abs(e))) <= SERIES, key
                            assert abs(row["bias"] - np.mean(e)) <= SERIES, key
                            done.add(key)
    main = {
        k for k, r in scores.items() if r["window"] == "primary" and r["outturn"] == "first_release"
    }
    assert done == main, (
        f"{len(main - done)} main score rows are not reproduced from the series files"
    )


def test_export_holds_only_what_it_should(scores) -> None:
    meta = _load("meta.json")
    want = {"meta.json", "scores.json", "scores_more.json"} | {
        f"series_{e}_{t}.json" for e, ts in meta["targets"].items() for t in ts
    }
    assert {p.name for p in DATA.iterdir()} == want
    assert meta["source"]["summary_sha256"] == se.published_summary_hash(DOC)
    assert not RETIRED & set(meta["foundation_models"])
    for name in sorted(want):
        raw = (DATA / name).read_bytes()
        assert raw.endswith(b"\n") and b"\r" not in raw and b"NaN" not in raw, name
        for r in RETIRED:
            assert re.search(rf'"{r}[|"]', raw.decode("utf-8")) is None, f"{r} in {name}"
        assert b"levels" not in raw, name
    assert {r["variant"] for r in scores.values()} <= set(se.VARIANTS)
    for econ, targets in meta["targets"].items():
        for target, t in targets.items():
            cells = _load(f"series_{econ}_{target}.json")
            assert {int(k.split("|")[0]) for k in cells} == set(meta["horizons"][t["freq"]])
            for cell in cells.values():
                assert (
                    cell["origin"] == sorted(cell["origin"])
                    and cell["origin"][0] >= meta["first_origin"]
                )
                assert None not in cell["y"]


def test_export_refuses_tables_that_are_not_the_published_ones(tmp_path: Path) -> None:
    (tmp_path / "tables").mkdir()
    (tmp_path / "tables" / "SUMMARY.md").write_text("not the published summary\n", encoding="utf-8")
    with pytest.raises(se.ExportError, match="not the published ones"):
        se.build(CFG, root=tmp_path)


def test_rerunning_the_export_changes_no_byte() -> None:
    root = Path(os.environ.get("FFCAST_BACKTEST_ROOT") or BACKTEST_ROOT)
    if not (root / "tables" / "SUMMARY.md").exists():
        pytest.skip("no private backtest store here")
    files = se.build(CFG, root=root)
    assert set(files) == {p.name for p in DATA.iterdir()}
    for name, data in files.items():
        assert (DATA / name).read_bytes() == data, name
