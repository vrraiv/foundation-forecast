"""Data-quality report and release-calendar derivation from the normalised vintage table.

Produces docs/data_quality.md with, per series: vintage coverage and gaps, deletes, suspected
rebasings and composition breaks, in-vintage history depth at the window starts, publication
lags derived from first appearance, and the content evidence on OECD edition timing.
Tables only; no interpretation."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

from .store import as_of, first_appearance


def _period_end(p: str) -> dt.date:
    if "-Q" in p:
        y, q = int(p[:4]), int(p[-1])
        m = q * 3
    else:
        y, m = int(p[:4]), int(p[5:7])
    import calendar

    return dt.date(y, m, calendar.monthrange(y, m)[1])


def vintage_dates(table: pd.DataFrame, sid: str) -> list[dt.date]:
    s = table.loc[table["series_id"] == sid, "vintage_date"]
    return sorted(set(pd.to_datetime(s).dt.date))


def vintage_gaps(dates: list[dt.date], max_gap_days: int) -> list[tuple[dt.date, dt.date, int]]:
    out = []
    for a, b in zip(dates, dates[1:], strict=False):
        d = (b - a).days
        if d > max_gap_days:
            out.append((a, b, d))
    return out


def suspected_rebasings(
    table: pd.DataFrame, sid: str, share: float = 0.8
) -> list[tuple[dt.date, float, int]]:
    """Vintages where at least `share` of the periods common with the previous vintage changed
    by (nearly) the same ratio: a rebasing or a composition/definition break, not a data
    revision. Returns (vintage_date, median ratio, n periods changed)."""
    dates = vintage_dates(table, sid)
    out = []
    prev = None
    for d in dates:
        cur = as_of(table, [sid], d, strict=False)[sid]
        if prev is not None and len(prev) > 5:
            common = cur.index.intersection(prev.index)
            if len(common) > 5:
                ratio = (cur[common] / prev[common]).replace([np.inf, -np.inf], np.nan).dropna()
                changed = ratio[~np.isclose(ratio, 1.0, rtol=1e-9)]
                if len(changed) >= share * len(common):
                    med = float(np.median(changed))
                    spread = float(np.median(np.abs(changed - med)))
                    if spread < 0.01 * abs(med) and abs(med - 1.0) > 1e-4:
                        out.append((d, round(med, 5), int(len(changed))))
        prev = cur
    return out


def composition_labels(table: pd.DataFrame, sid: str) -> list[tuple[dt.date, str]]:
    """For OECD spliced series, the first vintage of each area code."""
    s = table[table["series_id"] == sid]
    if not s["vintage_label"].str.contains(":").any():
        return []
    lab = s.assign(area=s["vintage_label"].str.split(":").str[-1])
    firsts = lab.groupby("area")["vintage_date"].min().sort_values()
    return [(pd.Timestamp(v).date(), k) for k, v in firsts.items()]


def history_depth(table: pd.DataFrame, sid: str, origins: list[dt.date]) -> dict[dt.date, int]:
    return {o: len(as_of(table, [sid], o)[sid]) for o in origins}


def publication_lags(table: pd.DataFrame, sid: str) -> pd.Series:
    """Days between the end of the reference period and its first appearance in a vintage."""
    fa = first_appearance(table, sid)
    lags = {p: (pd.Timestamp(v).date() - _period_end(p)).days for p, v in fa.items()}
    return pd.Series(lags, dtype=float)


def oecd_edition_lag(raw_paths: list[str | Path]) -> pd.DataFrame:
    """For an OECD series: per edition, the newest reference period in the full edition
    snapshot and the edition-minus-period lag in months. Computed from the raw CSVs (full
    snapshots), not from the change log, whose rows per vintage only show what changed."""
    from .sources.oecd import edition_content_check

    parts = [edition_content_check(Path(p)) for p in raw_paths if Path(p).exists()]
    if not parts:
        return pd.DataFrame(columns=["edition", "newest_period", "lag_months"])
    return pd.concat(parts, ignore_index=True).sort_values("edition").reset_index(drop=True)


def raw_paths_for(sid: str, manifest_path: Path) -> list[str]:
    import json

    if not manifest_path.exists():
        return []
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    return m.get("series", {}).get(sid, {}).get("raw_files", [])


def revision_cluster_editions(table: pd.DataFrame, sid: str, min_periods: int = 6) -> pd.DataFrame:
    """Editions in which many prior-year months were revised at once (annual revision rounds).
    Used to see when the Canadian LFS January revision reaches the OECD edition."""
    s = table[(table["series_id"] == sid) & (table["action"] == "R")].copy()
    s["edition"] = s["vintage_label"].str.split(":").str[0]
    s["ref_year"] = s["ref_period"].str[:4].astype(int)
    s["ed_year"] = s["edition"].str[:4].astype(int)
    prior = s[s["ref_year"] < s["ed_year"]]
    counts = prior.groupby("edition")["ref_period"].nunique()
    return counts[counts >= min_periods].rename("n_prior_year_periods_revised").reset_index()


def build_report(
    table: pd.DataFrame,
    cfg,
    bulk_summary: pd.DataFrame | None = None,
    problems: list[str] | None = None,
) -> str:
    # Per-series work operates on a filtered sub-table: as_of on the full table per vintage is
    # quadratic in the number of series.
    _full = table

    def _sub(sid):
        return _full[_full["series_id"] == sid]

    origins = [
        dt.date.fromisoformat(cfg.origins.extension_first),
        dt.date.fromisoformat(cfg.origins.first),
    ]
    sids = sorted(table["series_id"].unique())
    lines = [
        "# Data quality report",
        "",
        f"Generated {dt.datetime.now(dt.UTC).date().isoformat()} from `data/normalised/` by `ffcast quality`. Tables only.",
        "",
        "## 1. Series coverage",
        "",
        "| series | source | vintages | first vintage | last vintage | periods (latest) | deletes | history at "
        + " / ".join(o.isoformat() for o in origins)
        + " |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for sid in sids:
        s = table[table["series_id"] == sid]
        dates = vintage_dates(_sub(sid), sid)
        latest = as_of(_sub(sid), [sid], dates[-1] + dt.timedelta(days=1))[sid]
        depth = history_depth(_sub(sid), sid, origins)
        lines.append(
            f"| `{sid}` | {s['source'].iloc[0]} | {len(dates)} | {dates[0]} | {dates[-1]} | {len(latest)} | {(s['action'] == 'D').sum()} | "
            + " / ".join(str(depth[o]) for o in origins)
            + " |"
        )
    lines += ["", "## 2. Vintage gaps, rebasings and composition breaks", ""]
    for sid in sids:
        s = table[table["series_id"] == sid]
        src = s["source"].iloc[0]
        if src in ("eurostat", "valet"):
            continue
        dates = vintage_dates(_sub(sid), sid)
        max_gap = 45 if src == "oecd" else 120
        gaps = vintage_gaps(dates, max_gap)
        reb = suspected_rebasings(_sub(sid), sid)
        comp = composition_labels(_sub(sid), sid)
        lines.append(f"### `{sid}`")
        lines.append("")
        lines.append(
            f"- Vintage gaps longer than {max_gap} days: "
            + (", ".join(f"{a} to {b} ({d} d)" for a, b, d in gaps) if gaps else "none")
        )
        lines.append(
            "- Suspected rebasings or definitional breaks (vintage, median ratio, periods): "
            + (", ".join(f"{d} ({r}, {n})" for d, r, n in reb) if reb else "none detected")
        )
        if comp:
            lines.append(
                "- Area-code composition splice (first vintage per code): "
                + ", ".join(f"{k} from {d}" for d, k in comp)
            )
        lines.append("")
    lines += [
        "",
        "## 3. Publication lags derived from first appearance (days after period end)",
        "",
        "| series | n periods | median | p10 | p90 | min | max |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for sid in sids:
        s = table[table["series_id"] == sid]
        if s["source"].iloc[0] in ("eurostat", "valet"):
            continue
        lag = publication_lags(_sub(sid), sid)
        # only periods first seen after the first vintage carry information
        first_v = vintage_dates(_sub(sid), sid)[0]
        fa = first_appearance(_sub(sid), sid)
        lag = lag[[p for p in lag.index if pd.Timestamp(fa[p]).date() > first_v]]
        if lag.empty:
            continue
        lines.append(
            f"| `{sid}` | {len(lag)} | {lag.median():.0f} | {lag.quantile(0.1):.0f} | {lag.quantile(0.9):.0f} | {lag.min():.0f} | {lag.max():.0f} |"
        )
    lines += [
        "",
        "## 4. OECD edition timing evidence (rule in use: `conservative`; `same_month_eve` is a variant)",
        "",
    ]
    lines.append(
        "Edition-minus-newest-period lag in months, per OECD series. A lag of 1 means edition M already contains the observation for month M-1. Editions whose newest period is more than 12 months old are truncated or stale editions and are listed separately."
    )
    lines.append("")
    from .store import NORMALISED_ROOT

    for sid in [s for s in sids if s.startswith("oecd:")]:
        el = oecd_edition_lag(raw_paths_for(sid, NORMALISED_ROOT / "manifest.json"))
        if el.empty:
            lines.append(f"- `{sid}`: raw files not available for the edition-content check")
            continue
        normal = el[el["lag_months"] <= 12]
        stale = el[el["lag_months"] > 12]
        lag1 = el[el["lag_months"] < 2]
        lines.append(
            f"- `{sid}`: lag min {normal['lag_months'].min()}, median {normal['lag_months'].median():.0f}, max {normal['lag_months'].max()} over {len(normal)} regular editions; "
            f"editions containing M-1: {len(lag1)}"
            + (
                f" ({', '.join(lag1['edition'].tolist()[:12])}{'...' if len(lag1) > 12 else ''})"
                if 0 < len(lag1) <= 400
                else ""
            )
            + f"; stale or truncated editions: {len(stale)}"
            + (
                f" ({', '.join(stale['edition'].tolist()[:8])}{'...' if len(stale) > 8 else ''})"
                if len(stale)
                else ""
            )
        )
    for sid in [s for s in sids if "UNEMP" in s and s.startswith("oecd:CA")]:
        rc = revision_cluster_editions(_sub(sid), sid)
        lines.append("")
        lines.append(
            f"- `{sid}` editions revising at least 6 prior-year months (annual LFS revision reaches the edition): "
            + ", ".join(f"{r.edition} ({r.n_prior_year_periods_revised})" for r in rc.itertuples())
        )
    if bulk_summary is not None and not bulk_summary.empty:
        lines += [
            "",
            "## 5. RTD change-log rebuild versus ECB bulk snapshot files (2001-2014)",
            "",
            "| key | files compared | files identical | periods compared | mismatching periods |",
            "| --- | --- | --- | --- | --- |",
        ]
        for key, g in bulk_summary.groupby("key"):
            lines.append(
                f"| `{key}` | {len(g)} | {int(g['ok'].sum())} | {int(g['n_match'].sum() + g['n_mismatch'].sum())} | {int(g['n_mismatch'].sum())} |"
            )
    if problems:
        lines += ["", "## 6. Problems recorded by the pipeline", ""] + [f"- {p}" for p in problems]
    notes = Path(__file__).resolve().parents[3] / "docs" / "data_quality_notes.md"
    if notes.exists():
        lines += ["", notes.read_text(encoding="utf-8").rstrip()]
    return "\n".join(lines) + "\n"


def write_report(text: str, path: Path) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")
