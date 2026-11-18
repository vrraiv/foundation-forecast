"""DBnomics mirror of Statistics Canada tables (provider STATCAN). Used only because StatCan's
own servers refuse scripted clients; rows are labelled `dbnomics`, never `statcan`.

Real-time table 36100431 ("Vintages of releases of GDP, expenditure-based") has dimensions
freq.geogr.price.sea_adj.estim.relea where `relea` is the release (vintage) labelled like
"November 30, 2012". One DBnomics series = one (estimate, price basis, adjustment, release).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..raw import RawFile, RawStore
from ..store import snapshots_to_changelog

BASE = "https://api.db.nomics.world/v22"
SOURCE = "dbnomics"


def series_id(dataset: str, estim: str, price: str, sea_adj: str) -> str:
    return f"{SOURCE}:STATCAN/{dataset}/{estim}.{price}.{sea_adj}"


def download_realtime(store: RawStore, dataset: str, estims: list[str], price: str, sea_adj: str) -> RawFile:
    dims = json.dumps({"estim": estims, "price": [price], "sea_adj": [sea_adj]})
    name = f"STATCAN_{dataset}_{'-'.join(estims)}_{price}_{sea_adj}.json"
    return store.fetch(
        SOURCE,
        name,
        f"{BASE}/series/STATCAN/{dataset}",
        params={"dimensions": dims, "observations": "1", "limit": "1000", "format": "json"},
        timeout=600,
    )


def parse(path: Path) -> tuple[pd.DataFrame, dict[str, str]]:
    """Return (long frame: estim, price, sea_adj, release_label, period, value) and the
    release-code -> label mapping."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    docs = d["series"]["docs"]
    if d["series"].get("num_found", len(docs)) > len(docs):
        raise ValueError(f"{path}: pagination needed ({d['series']['num_found']} > {len(docs)})")
    labels = d.get("dataset", {}).get("dimensions_values_labels", {}).get("relea", {})
    rows = []
    for s in docs:
        dims = s["dimensions"]
        rel_code = dims["relea"]
        rel_label = labels.get(rel_code) or s.get("dimensions_labels", {}).get("relea") or rel_code
        for p, v in zip(s["period"], s["value"], strict=True):
            if v is None or v == "NA":
                continue
            rows.append((dims["estim"], dims["price"], dims["sea_adj"], rel_label, _period(p), float(v)))
    return (
        pd.DataFrame(rows, columns=["estim", "price", "sea_adj", "release", "ref_period", "value"]),
        labels,
    )


def _period(p: str) -> str:
    # DBnomics quarterly periods are "2012-Q3"
    return p


def normalise(path: Path, dataset: str, estim: str, price: str, sea_adj: str) -> pd.DataFrame:
    df, _ = parse(path)
    sub = df[(df["estim"] == estim) & (df["price"] == price) & (df["sea_adj"] == sea_adj)]
    rel_dates = pd.to_datetime(sub["release"], format="%B %d, %Y", errors="coerce")
    if rel_dates.isna().any():
        bad = sub.loc[rel_dates.isna(), "release"].unique()
        raise ValueError(f"unparseable release labels: {bad}")
    sub = sub.assign(_rel=rel_dates.dt.date)

    def snaps():
        for d, g in sub.groupby("_rel", sort=True):
            yield d, g["release"].iloc[0], pd.Series(g["value"].to_numpy(), index=g["ref_period"].to_numpy())

    return snapshots_to_changelog(snaps(), series_id(dataset, estim, price, sea_adj), SOURCE)
