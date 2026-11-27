"""Export the backtest for the public site (PLAN.md Phase 7, step 3).

Writes JSON files to `site/public/data/`, which are committed to the repository and are the only
backtest data the site reads. The browser filters and draws; it computes no score.

What is written, and nothing else:

- `scores.json`: the score table for the site's main slice (primary window, first-release
  outturn), every input mode, sample and split, with model-confidence-set membership and the PIT
  histogram on the rows where they exist (split `all`).
- `scores_more.json`: the same columns (without the PIT) for the other window and outturn
  combinations, for the tables and appendix pages.
- `series_<ECON>_<target>.json`: for each scored horizon and input mode, the forecast dates, the
  target period, the first-release outturn, and each model's median and interval bounds.
- `meta.json`: targets, horizons, windows, model facts from the configuration, and the hash of
  the published summary the tables belong to.

Left out on purpose: retired models (TimesFM 3.0, owner decision 2026-11-26), the levels variants,
input series, vintages, revised outturn values, and anything from the live registry. The live
page reads `ledger/ledger.jsonl` at build time instead.

The export refuses to run unless the private tables are the published ones: the SHA-256 of
`tables/SUMMARY.md` must equal the hash stated in the public copy under `docs/`. Output is
deterministic (sorted rows, fixed rounding, no time stamps), so a re-run on the same store
changes no byte.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import pandas as pd

from .config import Config, load_config
from .eval.scoring import load_scored_frame
from .eval.store import BACKTEST_ROOT

REPO = Path(__file__).resolve().parents[2]
SITE_DATA = REPO / "site" / "public" / "data"
PUBLISHED_SUMMARY = REPO / "docs" / "results_backtest_2026-11-19.md"

VARIANTS = ("univariate", "multivariate")
MAIN = {"window": "primary", "outturn": "first_release"}
SCORE_DP = 6  # the public tables print three decimals; six keeps every printed digit exact
SERIES_DP = 4

KEYS = [
    "econ",
    "target",
    "horizon",
    "model",
    "variant",
    "input_mode",
    "outturn",
    "sample",
    "window",
]
SCORE_COLS = {  # name in the file -> column in scores.csv
    "econ": "econ",
    "target": "target",
    "h": "horizon",
    "model": "model",
    "variant": "variant",
    "mode": "input_mode",
    "outturn": "outturn",
    "sample": "sample",
    "window": "window",
    "split": "split",
    "n": "n",
    "rmsfe": "rmsfe",
    "mae": "mae",
    "bias": "bias",
    "wql": "wql",
    "cov80": "coverage80",
    "rel_rmsfe": "rel_rmsfe",
    "rel_mae": "rel_mae",
    "dm_p": "dm_p",
    "mcs": "in_mcs90",
}
INTS = {"h", "n"}
TEXT = {"econ", "target", "model", "variant", "mode", "outturn", "sample", "window", "split"}


class ExportError(RuntimeError):
    pass


def published_summary_hash(doc: Path = PUBLISHED_SUMMARY) -> str:
    m = re.search(
        r"SHA-256 of\s+the file as stored \(bytes\): `([0-9a-f]{64})`",
        doc.read_text(encoding="utf-8"),
    )
    if not m:
        raise ExportError(f"no summary hash found in {doc}")
    return m.group(1)


def _num(x, dp: int):
    if x is None or pd.isna(x):
        return None
    x = float(x)
    if not math.isfinite(x):
        return None
    r = round(x, dp)
    return 0.0 if r == 0 else r  # no negative zero


def _dump(obj) -> bytes:
    return (
        json.dumps(obj, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n"
    ).encode()


def _score_rows(s: pd.DataFrame, with_pit: bool) -> dict:
    cols = [*SCORE_COLS, *(["pit"] if with_pit else [])]
    s = s.sort_values([*KEYS, "split"], kind="mergesort")
    rows = []
    for r in s.to_dict("records"):
        row = []
        for name, src in SCORE_COLS.items():
            v = r[src]
            if name in TEXT:
                row.append(str(v))
            elif name in INTS:
                row.append(int(v))
            elif name == "mcs":
                row.append(None if pd.isna(v) or r["split"] != "all" else bool(v))
            else:
                row.append(_num(v, SCORE_DP))
        if with_pit:
            p = r["pit"]
            row.append(
                [_num(x, SCORE_DP) for x in p]
                if isinstance(p, list) and r["split"] == "all"
                else None
            )
        rows.append(row)
    return {"cols": cols, "rows": rows}


def build(
    cfg: Config | None = None, root: Path = BACKTEST_ROOT, doc: Path = PUBLISHED_SUMMARY
) -> dict[str, bytes]:
    """Every file of the export as bytes, keyed by file name. Reads the store; writes nothing."""
    cfg = cfg or load_config()
    tables = root / "tables"
    want = published_summary_hash(doc)
    got = hashlib.sha256((tables / "SUMMARY.md").read_bytes()).hexdigest()
    if got != want:
        raise ExportError(
            f"{tables / 'SUMMARY.md'} has SHA-256 {got}, but the published summary is {want}: "
            "the tables are not the published ones, so nothing is exported"
        )
    retired = set(cfg.models.get("retired") or [])

    def keep(d: pd.DataFrame) -> pd.DataFrame:
        return d[~d["model"].isin(retired) & d["variant"].isin(VARIANTS)]

    s = keep(pd.read_csv(tables / "scores.csv"))
    m = keep(pd.read_csv(tables / "mcs.csv"))
    p = keep(pd.read_csv(tables / "pit.csv"))
    p = p.assign(pit=p[[f"bin{i}" for i in range(10)]].values.tolist())
    s = s.merge(m[[*KEYS, "in_mcs90"]], on=KEYS, how="left").merge(
        p[[*KEYS, "pit"]], on=KEYS, how="left"
    )
    main = (s["window"] == MAIN["window"]) & (s["outturn"] == MAIN["outturn"])
    files = {
        "scores.json": _dump(_score_rows(s[main], with_pit=True)),
        "scores_more.json": _dump(_score_rows(s[~main], with_pit=False)),
    }

    cover = cfg.scoring["interval_coverage"]
    lo, hi = f"q{(1 - cover) / 2:.1f}", f"q{1 - (1 - cover) / 2:.1f}"
    tr, _ = load_scored_frame(cfg, root)
    tr = keep(tr[(tr["origin"] >= cfg.origins.first) & (tr["space"] == "transformed")])
    origins: set[str] = set()
    for (e, t), g in sorted(tr.groupby(["econ", "target"]), key=lambda kv: kv[0]):
        cells = {}
        for (h, mode), gh in sorted(g.groupby(["horizon", "input_mode"]), key=lambda kv: kv[0]):
            if int(h) not in cfg.horizons[cfg.targets[e][t].freq]:
                continue
            gh = gh.dropna(subset=["first_release"])
            if gh.empty:
                continue
            base = gh.drop_duplicates("origin").sort_values("origin")
            idx = pd.Index(base["origin"])
            origins.update(str(o) for o in idx)
            cell = {
                "origin": [str(o) for o in idx],
                "period": base["target_period"].astype(str).tolist(),
                "y": [_num(v, SERIES_DP) for v in base["first_release"]],
                "m": {},
            }
            for (mo, va), gm in sorted(gh.groupby(["model", "variant"]), key=lambda kv: kv[0]):
                gm = gm.drop_duplicates("origin").set_index("origin").reindex(idx)
                cell["m"][f"{mo}|{va}"] = [
                    [_num(v, SERIES_DP) for v in gm[c]] for c in ("q0.5", lo, hi)
                ]
            cells[f"{int(h)}|{mode}"] = cell
        files[f"series_{e}_{t}.json"] = _dump(cells)

    fms = {k: v for k, v in cfg.foundation_models().items() if k not in retired}
    bench = cfg.models["benchmarks"]
    meta = {
        "source": {
            "summary": doc.relative_to(REPO).as_posix() if doc.is_relative_to(REPO) else doc.name,
            "summary_sha256": want,
        },
        "economies": list(cfg.economies),
        "targets": {
            e: {
                t: {"name": v.name, "freq": v.freq, "transform": v.transform}
                for t, v in cfg.targets[e].items()
                if (e, t) in {k for k, _ in tr.groupby(["econ", "target"])}
            }
            for e in cfg.economies
        },
        "horizons": {k: list(v) for k, v in cfg.horizons.items()},
        "first_origin": cfg.origins.first,
        "scored_origins": {"first": min(origins), "last": max(origins), "n": len(origins)},
        "extension_first_origin": cfg.origins.extension_first,
        "covid_window": list(cfg.exclusion_windows["covid"]),
        "interval": {"coverage": cover, "lower": lo, "upper": hi},
        "foundation_models": {
            k: {
                "hf_id": v.hf_id,
                "revision": v.revision,
                "licence": v.licence,
                "weights_date": v.weights_date,
                "training_cutoff": v.training_cutoff,
                "variants": list(v.variants),
            }
            for k, v in fms.items()
        },
        "benchmarks": sorted(k for k in bench if k not in retired),
        "combinations": {
            k: list(v["of"]) for k, v in bench.items() if isinstance(v, dict) and "of" in v
        },
        "series_layout": {
            "cell_key": "horizon|input_mode",
            "model_key": "model|variant",
            "values": ["median", "lower", "upper"],
        },
        "live_first_scoring_min_origins": cfg.registry["first_scoring_min_origins"],
    }
    files["meta.json"] = _dump(meta)
    return dict(sorted(files.items()))


def write(files: dict[str, bytes], out: Path = SITE_DATA) -> Path:
    """Write the export, removing JSON files from an earlier export that are no longer produced."""
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.json"):
        if old.name not in files:
            old.unlink()
    for name, data in files.items():
        (out / name).write_bytes(data)
    return out
