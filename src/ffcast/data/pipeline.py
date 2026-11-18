"""`ffcast data`: download every configured source into data/raw, normalise into
data/normalised/*.parquet, and write a manifest with content hashes. Failures are recorded in
data/normalised/problems.txt and never patched over."""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from ..config import Config, load_config
from . import pseudo
from .raw import DownloadError, RawStore
from .sources import dbnomics, ecb_rtd, eurostat, financial, oecd, statcan, valet
from .store import NORMALISED_ROOT, as_of, read_table, snapshots_to_changelog, write_table

OECD_AREAS = {"CA": ["CAN"], "EA": ["EA18", "EA19", "EA20"]}
MAX_EDITION_LAG_MONTHS = 12  # an edition whose newest observation is older than this is broken
EUROSTAT_GEO_DEFAULT = {"EA": "EA21"}
RTD_BULK = {
    "quarterly.zip": "https://data.ecb.europa.eu/sites/default/files/2024-08/quarterly.zip",
    "monthly.zip": "https://data.ecb.europa.eu/sites/default/files/2024-08/monthly.zip",
}


@dataclass
class RunReport:
    download_date: dt.date
    series: dict[str, dict] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    def add(self, sid: str, path: Path, sha: str, rows: int, source: str, raw: list[str]) -> None:
        self.series[sid] = {
            "path": str(path),
            "sha256": sha,
            "rows": rows,
            "source": source,
            "raw_files": raw,
        }

    def problem(self, msg: str) -> None:
        self.problems.append(msg)


def safe_name(sid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", sid)


def run_data(
    cfg: Config | None = None, store: RawStore | None = None, out_root: Path = NORMALISED_ROOT
) -> RunReport:
    cfg = cfg or load_config()
    store = store or RawStore()
    rep = RunReport(download_date=store.today)
    rule = cfg.vintage_sources["oecd_edition_rule"]
    day = cfg.origins.day_of_month
    out_root.mkdir(parents=True, exist_ok=True)

    def save(sid: str, table: pd.DataFrame, source: str, raw: list[str]) -> None:
        if table.empty:
            rep.problem(f"{sid}: normalised table is empty; not written")
            return
        p = out_root / f"{safe_name(sid)}.parquet"
        sha = write_table(table, p)
        rep.add(sid, p, sha, len(table), source, raw)

    oecd_done: set[tuple] = set()
    pseudo_specs: list[tuple[str, str, dict]] = []
    for econ, targets in cfg.targets.items():
        for tname, t in targets.items():
            if t.blocked:
                rep.problem(f"{econ}/{tname}: BLOCKED: {t.blocked}")
            specs = []
            if t.vintages:
                specs.append(t.vintages)
                if t.vintages.get("fallback"):
                    specs.append(t.vintages["fallback"])
            for spec in specs:
                src = spec["source"]
                try:
                    if src == "pseudo":
                        pseudo_specs.append((econ, tname, spec))
                    elif src == "oecd":
                        k = (econ, t.freq, spec["measure"], spec["unit"], spec["activity"])
                        if k in oecd_done:
                            continue
                        oecd_done.add(k)
                        _oecd_series(store, rep, save, econ, t.freq, spec, rule, day)
                    elif src == "ecb_rtd":
                        _rtd_series(store, rep, save, spec["key"])
                    elif src == "statcan_rt":
                        _statcan_realtime(store, rep, save, spec["table"], tname)
                    else:
                        rep.problem(f"{econ}/{tname}: unknown vintage source {src}")
                except DownloadError as e:
                    rep.problem(f"{econ}/{tname} [{src}]: {e}")
            # latest data
            try:
                _latest(store, rep, save, econ, tname, t.latest)
            except DownloadError as e:
                rep.problem(f"{econ}/{tname} [latest {t.latest.get('source')}]: {e}")

    # pseudo-vintages are built from the latest snapshots downloaded above
    for econ, tname, spec in pseudo_specs:
        base = spec["base"]
        p = out_root / f"{safe_name(base)}.parquet"
        if not p.exists():
            rep.problem(f"{econ}/{tname}: pseudo-vintage base {base} not available")
            continue
        snap = as_of_latest(read_table(p), base)
        table = pseudo.build(
            snap, base, spec["months_after_period"], day, store.today, spec.get("late_months")
        )
        save(pseudo.pseudo_series_id(base), table, "pseudo", [str(p)])

    # conditioning set
    for econ, items in cfg.conditioning.items():
        for spec in items:
            src = spec["source"]
            try:
                if src == "oecd":
                    k = (econ, spec["freq"], spec["measure"], spec["unit"], spec["activity"])
                    if k in oecd_done:
                        continue
                    oecd_done.add(k)
                    _oecd_series(store, rep, save, econ, spec["freq"], spec, rule, day)
                elif src == "ecb_rtd":
                    _rtd_series(store, rep, save, spec["key"])
                elif src == "ecb_sdw":
                    rf = financial.download_ecb(store, spec["flow"], spec["key"])
                    save(
                        financial.ecb_series_id(spec["flow"], spec["key"]),
                        financial.normalise_ecb(rf.path, spec["flow"], spec["key"]),
                        "ecb",
                        [str(rf.path)],
                    )
                elif src == "valet_monthly":
                    rf = financial.download_valet(store, spec["series"])
                    save(
                        financial.valet_series_id(spec["series"]),
                        financial.normalise_valet_monthly(rf.path, spec["series"]),
                        "valet",
                        [str(rf.path)],
                    )
                elif src == "valet_daily":
                    rf = financial.download_valet(store, spec["series"])
                    save(
                        financial.valet_series_id(spec["series"]),
                        financial.normalise_valet_daily(rf.path, spec["series"]),
                        "valet",
                        [str(rf.path)],
                    )
                else:
                    rep.problem(f"conditioning {econ}: unknown source {src}")
            except DownloadError as e:
                rep.problem(f"conditioning {econ} {spec.get('name', spec)}: {e}")

    for spec in cfg.vintage_sources.get("cross_check_oecd", []):
        k = (spec["econ"], spec["freq"], spec["measure"], spec["unit"], spec["activity"])
        if k in oecd_done:
            continue
        oecd_done.add(k)
        try:
            _oecd_series(store, rep, save, spec["econ"], spec["freq"], spec, rule, day)
        except DownloadError as e:
            rep.problem(f"cross-check OECD {k}: {e}")

    for key in cfg.vintage_sources.get("cross_check_rtd_keys", []):
        try:
            _rtd_series(store, rep, save, key)
        except DownloadError as e:
            rep.problem(f"cross-check RTD {key}: {e}")

    for name, url in RTD_BULK.items():
        try:
            store.fetch("rtd-bulk", name, url, timeout=900)
        except DownloadError as e:
            rep.problem(f"RTD bulk {name}: {e}")

    (out_root / "manifest.json").write_text(
        json.dumps(
            {"download_date": rep.download_date.isoformat(), "series": rep.series},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_root / "problems.txt").write_text(
        "\n".join(rep.problems) + ("\n" if rep.problems else ""), encoding="utf-8"
    )
    return rep


def as_of_latest(table: pd.DataFrame, sid: str) -> pd.Series:
    last = max(pd.to_datetime(table["vintage_date"]).dt.date)
    return as_of(table, [sid], last, strict=False)[sid]


def _oecd_series(store, rep, save, econ, freq, spec, rule, day):
    raws, tables = [], []
    for area in OECD_AREAS[econ]:
        rf = oecd.download(store, area, freq, spec["measure"], spec["unit"], spec["activity"])
        raws.append(str(rf.path))
        tables.append(oecd.parse_csv(rf.path))
    df = pd.concat(tables, ignore_index=True)
    # Splice: each edition must come from exactly one area code
    per_ed = df.groupby("EDITION")["REF_AREA"].nunique()
    multi = per_ed[per_ed > 1]
    if not multi.empty:
        rep.problem(
            f"OECD {econ} {spec['measure']}: editions with more than one area code: {list(multi.index)[:5]}"
        )
        df = df[~df["EDITION"].isin(multi.index)]
    sid = f"oecd:{econ}.{freq}.{spec['measure']}.{spec['unit']}.{spec['activity']}"

    def snaps():
        for ed, g in df.groupby("EDITION", sort=True):
            s = pd.Series(g["OBS_VALUE"].to_numpy(), index=g["TIME_PERIOD"].to_numpy())
            s = s[~s.index.duplicated(keep="last")].dropna()
            if s.empty:
                rep.problem(f"{sid}: edition {ed} is empty; dropped")
                continue
            lag = oecd.months_between(ed, max(s.index))
            if lag > MAX_EDITION_LAG_MONTHS:
                # A truncated edition (newest observation years old) is a broken vintage. It is
                # dropped, never patched: the previous edition stays visible until the next
                # complete one. Recorded here and in docs/data_quality.md.
                rep.problem(
                    f"{sid}: edition {ed} truncated (newest period {max(s.index)}, lag {lag} months); dropped"
                )
                continue
            yield oecd.edition_vintage_date(ed, rule, day), f"{ed}:{g['REF_AREA'].iloc[0]}", s

    save(sid, snapshots_to_changelog(snaps(), sid, oecd.SOURCE), oecd.SOURCE, raws)


def _rtd_series(store, rep, save, key):
    rf = ecb_rtd.download_history(store, key)
    table, problems = ecb_rtd.normalise(rf.path)
    for p in problems:
        rep.problem(p)
    save(ecb_rtd.series_id(key), table, ecb_rtd.SOURCE, [str(rf.path)])


def _statcan_realtime(store, rep, save, table_id, tname):
    rf = statcan.try_download_full_table(store, table_id)
    if rf is None:
        rep.problem(
            f"statcan {table_id}: WDS unreachable (Cloudflare challenge); using DBnomics mirror"
        )
        if table_id != "36100431":
            rep.problem(f"statcan {table_id}: no mirror available; vintages not loaded")
            return
        estim = {"gdp": "estim_24", "consumption": "estim_12"}[tname]
        raw = dbnomics.download_realtime(
            store, table_id, ["estim_24", "estim_12"], "price_1", "sea_adj_1"
        )
        table = dbnomics.normalise(raw.path, table_id, estim, "price_1", "sea_adj_1")
        save(
            dbnomics.series_id(table_id, estim, "price_1", "sea_adj_1"),
            table,
            dbnomics.SOURCE,
            [str(raw.path)],
        )
        return
    rep.problem(
        f"statcan {table_id}: downloaded but real-time parsing not yet wired (Phase 2 follow-up)"
    )


def _latest(store, rep, save, econ, tname, spec):
    src = spec["source"]
    if src == "eurostat":
        filters = dict(spec["filters"])
        geo = filters.pop("geo", EUROSTAT_GEO_DEFAULT.get(econ, "EA21"))
        rf = eurostat.download(store, spec["dataset"], filters, geo)
        table = eurostat.normalise(rf.path, spec["dataset"], {**filters, "geo": geo}, store.today)
        save(
            eurostat.series_id(spec["dataset"], {**filters, "geo": geo}),
            table,
            eurostat.SOURCE,
            [str(rf.path)],
        )
    elif src == "valet":
        rf = valet.download(store, spec["series"])
        save(
            valet.series_id(spec["series"]),
            valet.normalise(rf.path, spec["series"], store.today),
            valet.SOURCE,
            [str(rf.path)],
        )
    elif src == "statcan":
        rf = statcan.try_download_full_table(store, spec["table"])
        if rf is None:
            rep.problem(
                f"{econ}/{tname}: statcan latest table {spec['table']} unreachable (Cloudflare challenge)"
            )
    elif src == "statcan_manual":
        rf = statcan.find_manual_table(store, spec["table"])
        if rf is None:
            rep.problem(
                f"{econ}/{tname}: no owner-supplied StatCan file {spec['table']}-eng.zip under data/raw/statcan-manual"
            )
        else:
            table, sid = statcan.normalise_manual_latest(
                rf.path, spec["table"], dict(spec["member"]), rf.download_date
            )
            save(sid, table, statcan.SOURCE, [str(rf.path)])
    else:
        rep.problem(f"{econ}/{tname}: unknown latest source {src}")
