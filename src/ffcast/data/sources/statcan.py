"""Statistics Canada Web Data Service. As of 2026-11-17 every www150.statcan.gc.ca path answers
scripted clients with a Cloudflare challenge (HTTP 403). The downloader therefore records a
failure instead of data; files the owner downloads in a browser can be registered through
`RawStore.register_manual` and parsed with `parse_full_table_csv`."""

from __future__ import annotations

import datetime as dt
import io
import zipfile
from pathlib import Path

import pandas as pd

from ..raw import DownloadError, RawFile, RawStore
from ..store import empty_table, snapshots_to_changelog

WDS = "https://www150.statcan.gc.ca/t1/wds/rest"
SOURCE = "statcan"


def try_download_full_table(store: RawStore, product_id: str) -> RawFile | None:
    """getFullTableDownloadCSV returns a JSON with a zip URL; both hops may be challenged."""
    try:
        meta = store.fetch(SOURCE, f"{product_id}_download_link.json", f"{WDS}/getFullTableDownloadCSV/{product_id}/en")
    except DownloadError:
        return None
    import json

    obj = json.loads(meta.path.read_text(encoding="utf-8"))
    url = obj.get("object")
    if not url:
        return None
    try:
        return store.fetch(SOURCE, f"{product_id}-eng.zip", url, timeout=900)
    except DownloadError:
        return None


MANUAL_SOURCE = "statcan-manual"


def find_manual_table(store: RawStore, product_id: str) -> RawFile | None:
    """Newest owner-registered full-table zip `<product_id>-eng.zip` under
    data/raw/statcan-manual/<day>/, verified against its manifest hash. None if there is none."""
    name = f"{product_id}-eng.zip"
    for day in reversed(store.list_days(MANUAL_SOURCE)):
        p = store.dir_for(MANUAL_SOURCE, day) / name
        if not p.exists():
            continue
        if name in store.verify(MANUAL_SOURCE, day):
            raise ValueError(f"{p}: bytes do not match the manifest hash")
        meta = store._load_manifest(MANUAL_SOURCE, day)["files"][name]
        return RawFile(MANUAL_SOURCE, day, name, p, meta["sha256"], None, meta["fetched_at_utc"], None)
    return None


def select_member(df: pd.DataFrame, member: dict[str, str]) -> tuple[pd.DataFrame, str]:
    """Rows of one series, selected by exact dimension labels (e.g. GEO and the product label).
    The selection must map to exactly one VECTOR, which is returned and becomes part of the
    series id; nothing is guessed when labels do not match."""
    sub = df
    for col, val in member.items():
        if col not in sub.columns:
            raise ValueError(f"StatCan CSV has no column {col!r}; columns: {list(df.columns)}")
        sub = sub[sub[col] == val]
        if sub.empty:
            options = sorted(df[col].dropna().unique().tolist())[:40]
            raise ValueError(f"no rows with {col} == {val!r}; available: {options}")
    vectors = sorted(sub["VECTOR"].dropna().unique().tolist())
    if len(vectors) != 1:
        raise ValueError(f"selection {member} maps to {len(vectors)} vectors: {vectors[:10]}")
    return sub, vectors[0]


def manual_series_id(product_id: str, vector: str) -> str:
    return f"statcan:{product_id}:{vector}"


def normalise_manual_latest(path: Path, product_id: str, member: dict[str, str], download_date: dt.date) -> tuple[pd.DataFrame, str]:
    """One latest-data snapshot from an owner-supplied full-table zip. Returns the change-log
    table and its series id. Values flagged '..' (not available) are dropped."""
    df = parse_full_table_csv(read_table_zip(path))
    sub, vector = select_member(df, member)
    sub = sub.dropna(subset=["VALUE"])
    sid = manual_series_id(product_id, vector)
    if sub["REF_DATE"].duplicated().any():
        raise ValueError(f"{sid}: duplicated REF_DATE in selection")
    s = pd.Series(sub["VALUE"].to_numpy(dtype=float), index=sub["REF_DATE"].to_numpy()).sort_index()
    return snapshots_to_changelog([(download_date, f"manual file {download_date}", s)], sid, SOURCE), sid


def read_table_zip(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        name = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n][0]
        with z.open(name) as fh:
            return pd.read_csv(io.TextIOWrapper(fh, encoding="utf-8-sig"), dtype=str)


def parse_full_table_csv(df: pd.DataFrame) -> pd.DataFrame:
    need = {"REF_DATE", "VALUE", "VECTOR"}
    if not need <= set(df.columns):
        raise ValueError(f"StatCan CSV missing {need - set(df.columns)}")
    df = df.copy()
    df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
    return df


def normalise_realtime_table(
    df: pd.DataFrame, member_filter: dict[str, str], release_col: str, series_id: str
) -> pd.DataFrame:
    """A real-time table has one row per (release date, reference period). `member_filter`
    pins every other dimension; `release_col` is the vintage dimension (e.g. 'Release')."""
    sub = df
    for col, val in member_filter.items():
        sub = sub[sub[col] == val]
    if sub.empty:
        return empty_table()

    def snaps():
        rel = pd.to_datetime(sub[release_col], format="%B %d, %Y", errors="coerce")
        tmp = sub.assign(_rel=rel.dt.date)
        for d, g in tmp.groupby("_rel", sort=True):
            s = pd.Series(g["VALUE"].to_numpy(), index=g["REF_DATE"].to_numpy())
            yield d, g[release_col].iloc[0], s

    return snapshots_to_changelog(snaps(), series_id, SOURCE)


def normalise_latest(df: pd.DataFrame, member_filter: dict[str, str], series_id: str, download_date: dt.date) -> pd.DataFrame:
    sub = df
    for col, val in member_filter.items():
        sub = sub[sub[col] == val]
    s = pd.Series(sub["VALUE"].to_numpy(), index=sub["REF_DATE"].to_numpy())
    return snapshots_to_changelog([(download_date, f"download {download_date}", s)], series_id, SOURCE)
