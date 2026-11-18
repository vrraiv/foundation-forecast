"""Compare the benchmark forecast store with a backed-up copy, row for row.

Usage: python scripts/compare_bench_stores.py data/backtest/_backup_bench_20261118T122416

Reports, for AR, BVAR and naive: rows compared, rows whose value or mean differs, the largest
absolute difference; rows present in only one store (with the cells involved); the DFM status
cross-tabulation on common cells; and the validity-guard trips by model. Reads only; prints counts
and cell names, never forecast values beyond the maximum absolute difference. Used after the
2026-11-18 benchmark recompute (docs/backtest.md, Deviations 2 and 3)."""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data" / "backtest"
KEYS = [
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
]
MKEYS = ["origin", "econ", "target", "variant", "input_mode"]


def main(backup: Path) -> int:
    new_f, new_m = ROOT / "forecasts" / "bench", ROOT / "meta" / "bench"
    old_f, old_m = backup / "forecasts_bench", backup / "meta_bench"
    names = sorted(p.name for p in new_f.glob("*.parquet") if (old_f / p.name).exists())
    print(f"origins in both stores: {len(names)}")
    tot = {m: [0, 0, 0.0] for m in ("ar", "bvar", "naive")}
    only_new = collections.Counter()
    only_old = collections.Counter()
    dfm = []
    trips = collections.Counter()
    for name in names:
        fn, fo = pd.read_parquet(new_f / name), pd.read_parquet(old_f / name)
        for mdl, acc in tot.items():
            a = fn[fn.model == mdl][KEYS + ["value", "mean"]]
            b = fo[fo.model == mdl][KEYS + ["value", "mean"]]
            m = a.merge(b, on=KEYS, how="outer", suffixes=("_n", "_o"), indicator=True)
            both = m[m._merge == "both"]
            only_new.update(
                zip(m[m._merge == "left_only"].econ, m[m._merge == "left_only"].target, strict=True)
            )
            only_old.update(
                zip(
                    m[m._merge == "right_only"].econ,
                    m[m._merge == "right_only"].target,
                    strict=True,
                )
            )
            d = np.nan_to_num(
                np.abs(
                    both[["value_n", "mean_n"]].to_numpy() - both[["value_o", "mean_o"]].to_numpy()
                )
            )
            acc[0] += len(both)
            acc[1] += int((d > 0).any(axis=1).sum()) if len(d) else 0
            acc[2] = max(acc[2], float(d.max()) if len(d) else 0.0)
        mn, mo = pd.read_parquet(new_m / name), pd.read_parquet(old_m / name)
        dn = mn[mn.model == "dfm"][MKEYS + ["status"]]
        do = mo[mo.model == "dfm"][MKEYS + ["status"]]
        dfm.append(dn.merge(do, on=MKEYS, how="inner", suffixes=("_new", "_old")))
        g = mn[mn.note.astype(str).str.startswith("numerical failure")]
        trips.update(g.model.tolist())
    print("rows compared, rows differing, max abs diff:")
    for mdl, (n, bad, mx) in tot.items():
        print(f"  {mdl:6s} {n:>10,d} {bad:>8,d} {mx:.3g}")
    print(f"rows only in the current store: {sum(only_new.values()):,} {dict(only_new)}")
    print(f"rows only in the backup:        {sum(only_old.values()):,} {dict(only_old)}")
    d = pd.concat(dfm)
    print(f"DFM status on {len(d):,} common cells (rows old, columns new):")
    print(pd.crosstab(d.status_old, d.status_new).to_string())
    print(f"validity-guard trips by model: {dict(trips)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
