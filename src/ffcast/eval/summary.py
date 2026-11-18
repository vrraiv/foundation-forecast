"""Private results summary for HUMAN GATE 4: `data/backtest/tables/SUMMARY.md`.

Tables only, assembled from the CSVs that `ffcast score` and `ffcast spf` write and from the
run's own bookkeeping (meta rows, outturns, run manifest, weights digests, verify result). The
slices shown were fixed before any foundation-model result existed (see the module history);
nothing here ranks, highlights or interprets. Output stays under `data/` (git-ignored).
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import pandas as pd

from ..config import Config, load_config
from .store import BACKTEST_ROOT, read_meta

TABLES = "tables"

# The headline slice: the primary pre-registered comparison, stated here and in the file header.
HEADLINE = {
    "input_mode": "realtime",
    "outturn": "first_release",
    "sample": "full",
    "window": "primary",
    "split": "all",
}
HEADLINE_VARIANTS = ("univariate", "multivariate")

# Keep the headline tables readable: one row per model/variant, one column per horizon.
_COLS = ["n", "rel_rmsfe", "rel_mae", "dm_p", "wql", "coverage80"]


# ------------------------------------------------------------------ markdown helpers


def _fmt(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int) or (isinstance(v, float) and float(v).is_integer() and abs(v) < 1e6):
        return f"{int(v)}"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def md_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    """Pipe table without external dependencies; numeric cells to three decimals."""
    if df is None or df.empty:
        return "_(no rows)_"
    body = df if max_rows is None else df.head(max_rows)
    cols = [str(c) for c in body.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in body.iterrows():
        lines.append("| " + " | ".join(_fmt(r[c]) for c in body.columns) + " |")
    if max_rows is not None and len(df) > max_rows:
        lines.append(f"\n_{len(df) - max_rows} more rows in the CSV_")
    return "\n".join(lines)


def _skip_reason(note: str) -> str:
    """Collapse numeric details so skip notes group by cause."""
    s = re.sub(r"\d+", "N", str(note))
    return s[:70]


def _read(d: Path, name: str) -> pd.DataFrame:
    p = d / f"{name}.csv"
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(p)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


# ------------------------------------------------------------------ sections


def section_run(root: Path) -> list[str]:
    out = ["## 1. Run bookkeeping", ""]
    mf = root / "run_manifest.json"
    if mf.exists():
        m = json.loads(mf.read_text(encoding="utf-8"))
        rows = [
            ("first written (UTC)", m.get("first_written_utc")),
            ("last written (UTC)", m.get("written_utc")),
            ("config sha256 at first run", m.get("first_config_sha256")),
            ("config sha256 now", m.get("config_sha256")),
            ("config changed since first run", bool(m.get("config_changed_since_first_run"))),
            ("config-change note", m.get("config_change_note", "")),
            ("data manifest sha256", m.get("data_manifest_sha256")),
            ("series in data manifest", m.get("n_series")),
            ("revised vintage date (`revised` mode)", m.get("revised_as_of")),
            ("last stage-3 workdir", m.get("last_stage3_workdir")),
        ]
        out.append(md_table(pd.DataFrame(rows, columns=["item", "value"])))
        wd = m.get("last_stage3_workdir")
        if wd and (Path(wd) / "weights.json").exists():
            w = json.loads((Path(wd) / "weights.json").read_text(encoding="utf-8"))
            out += ["", "Weights digests used by the foundation-model stage:", ""]
            out.append(
                md_table(pd.DataFrame(sorted(w.items()), columns=["model", "weights digest"]))
            )
    else:
        out.append("_(no run_manifest.json)_")
    vf = sorted(root.glob("verify_*.json"))
    out += ["", "### Verify (`ffcast backtest --verify N`)", ""]
    if vf:
        v = json.loads(vf[-1].read_text(encoding="utf-8"))
        out.append(
            f"Latest: `{vf[-1].name}`; origins recomputed: {len(v.get('origins', []))}; "
            f"mismatching origins: {len(v.get('mismatches', []))}."
        )
        if v.get("mismatches"):
            out += ["", "```", json.dumps(v["mismatches"], indent=1)[:3000], "```"]
    else:
        out.append("_(not run)_")
    return out


def section_coverage(root: Path) -> list[str]:
    meta = read_meta(root)
    out = ["## 2. Coverage", ""]
    if meta.empty:
        return [*out, "_(no meta rows)_"]
    origins = sorted(meta["origin"].astype(str).unique())
    out.append(
        f"Origins with stored rows: {len(origins)} ({origins[0]} to {origins[-1]}). "
        f"Meta rows: {len(meta)}."
    )
    out += ["", "### Status by model, variant and input mode", ""]
    st = (
        meta.groupby(["model", "variant", "input_mode", "status"])
        .size()
        .unstack("status", fill_value=0)
        .reset_index()
    )
    out.append(md_table(st))
    out += ["", "### Status by economy and target (all models)", ""]
    st2 = (
        meta.groupby(["econ", "target", "status"])
        .size()
        .unstack("status", fill_value=0)
        .reset_index()
    )
    out.append(md_table(st2))
    sk = meta[meta["status"] != "ok"]
    if not sk.empty:
        out += ["", "### Skip and error reasons", ""]
        rs = (
            sk.assign(reason=sk["note"].map(_skip_reason))
            .groupby(["status", "reason"])
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )
        out.append(md_table(rs, max_rows=40))
    ok = meta[meta["status"] == "ok"]
    if not ok.empty and "runtime_s" in ok:
        out += ["", "### Runtime (seconds per task, ok rows)", ""]
        rt = ok.groupby("model")["runtime_s"].agg(["count", "median", "mean", "max"]).reset_index()
        out.append(md_table(rt))
    return out


def section_outturns(root: Path) -> list[str]:
    out = ["## 3. Outturns", ""]
    p = root / "outturns.parquet"
    if not p.exists():
        return [*out, "_(no outturns.parquet)_"]
    o = pd.read_parquet(p)
    if o.empty:
        return [*out, "_(empty)_"]
    g = o.groupby(["econ", "target"])
    t = pd.DataFrame(
        {
            "periods": g.size(),
            "first_release_available": g["first_release"].count(),
            "late": g["late"].sum().astype(int),
            "revised_12m_available": g["revised_12m"].count(),
            "lag_limit_days": g["lag_limit_days"].first(),
            "median_lag_days": g["lag_days"].median(),
        }
    ).reset_index()
    out.append(md_table(t))
    out.append(
        "\nLate first releases are kept in the table but excluded from first-release scoring "
        "(`docs/backtest.md`, Outturns)."
    )
    return out


def _headline_frame(s: pd.DataFrame, econ: str, target: str, metric: str) -> pd.DataFrame:
    g = s[(s["econ"] == econ) & (s["target"] == target)]
    g = g.assign(row=g["model"] + " / " + g["variant"])
    w = g.pivot_table(index="row", columns="horizon", values=metric, aggfunc="first")
    w.columns = [f"h{int(c)}" for c in w.columns]
    return w.reset_index().rename(columns={"row": "model / variant"})


def section_headline(d: Path) -> list[str]:
    s = _read(d, "scores")
    out = ["## 4. Headline tables", ""]
    out.append(
        "Slice: "
        + ", ".join(f"{k} = `{v}`" for k, v in HEADLINE.items())
        + f", variants {', '.join(f'`{v}`' for v in HEADLINE_VARIANTS)}, configured horizons. "
        "Relative RMSFE and MAE are ratios to the direct AR of the same cell (below 1 means a "
        "smaller error than AR; no ranking implied). `dm_p` is the two-sided HLN-corrected "
        "Diebold-Mariano p-value against AR on squared errors. `in_mcs90` is membership of the "
        "90% model confidence set over models with complete common origins in the cell."
    )
    if s.empty:
        return [*out, "", "_(no scores.csv)_"]
    hs = s.copy()
    for k, v in HEADLINE.items():
        hs = hs[hs[k].astype(str) == v]
    hs = hs[hs["variant"].isin(HEADLINE_VARIANTS)]
    mcs = _read(d, "mcs")
    if not mcs.empty:
        mk = [k for k in HEADLINE if k in mcs.columns]
        for k in mk:
            mcs = mcs[mcs[k].astype(str) == HEADLINE[k]]
    for (econ, target), _ in hs.groupby(["econ", "target"]):
        out += ["", f"### {econ} / {target}", ""]
        for metric, label in [
            ("n", "Scored forecasts (n)"),
            ("rel_rmsfe", "Relative RMSFE to AR"),
            ("rel_mae", "Relative MAE to AR"),
            ("dm_p", "Diebold-Mariano p-value vs AR"),
            ("rmsfe", "RMSFE (transformed units)"),
            ("bias", "Mean error (outturn minus forecast)"),
            ("wql", "Weighted quantile loss"),
            ("coverage80", "80% interval coverage"),
        ]:
            out += ["", f"**{label}**", "", md_table(_headline_frame(hs, econ, target, metric))]
        if not mcs.empty:
            mg = mcs[(mcs["econ"] == econ) & (mcs["target"] == target)]
            if not mg.empty:
                mg = mg.assign(row=mg["model"] + " / " + mg["variant"])
                w = mg.pivot_table(
                    index="row", columns="horizon", values="in_mcs90", aggfunc="first"
                )
                w.columns = [f"h{int(c)}" for c in w.columns]
                out += [
                    "",
                    "**Model confidence set (90%) membership**",
                    "",
                    md_table(w.reset_index().rename(columns={"row": "model / variant"})),
                ]
    return out


def _view(
    s: pd.DataFrame, fixed: dict, free: str, values: list[str], metric: str = "rel_rmsfe"
) -> pd.DataFrame:
    """One metric, rows = econ/target/model/variant/horizon, columns = the free dimension."""
    g = s.copy()
    for k, v in fixed.items():
        g = g[g[k].astype(str) == v]
    g = g[g[free].astype(str).isin(values)]
    if g.empty:
        return pd.DataFrame()
    w = g.pivot_table(
        index=["econ", "target", "horizon", "model", "variant"],
        columns=free,
        values=metric,
        aggfunc="first",
    )
    w.columns = [f"{metric}:{c}" for c in w.columns]
    n = g.pivot_table(
        index=["econ", "target", "horizon", "model", "variant"],
        columns=free,
        values="n",
        aggfunc="first",
    )
    n.columns = [f"n:{c}" for c in n.columns]
    return w.join(n).reset_index()


def section_views(d: Path) -> list[str]:
    s = _read(d, "scores")
    out = ["## 5. Views by plan question (relative RMSFE to AR unless stated)", ""]
    if s.empty:
        return [*out, "_(no scores.csv)_"]
    base = {k: v for k, v in HEADLINE.items()}
    s = s[s["variant"].isin(HEADLINE_VARIANTS)]
    views = [
        (
            "### 5.1 Q1: real-time versus revised input (first-release outturn)",
            {k: v for k, v in base.items() if k != "input_mode"},
            "input_mode",
            ["realtime", "revised"],
        ),
        (
            "### 5.1b Q1: real-time versus revised input, revised outturn",
            {**{k: v for k, v in base.items() if k != "input_mode"}, "outturn": "revised_12m"},
            "input_mode",
            ["realtime", "revised"],
        ),
        (
            "### 5.2 Outturn definition (real-time input)",
            {k: v for k, v in base.items() if k != "outturn"},
            "outturn",
            ["first_release", "revised_12m"],
        ),
        (
            "### 5.3 Q2: before and after the weights date",
            {k: v for k, v in base.items() if k != "split"},
            "split",
            ["pre", "post"],
        ),
        (
            "### 5.3b Q2: before and after the stated training cutoff (models with a cutoff)",
            {k: v for k, v in base.items() if k != "split"},
            "split",
            ["pre_cutoff", "post_cutoff"],
        ),
        (
            "### 5.4 Full sample versus ex-COVID",
            {k: v for k, v in base.items() if k != "sample"},
            "sample",
            ["full", "ex_covid"],
        ),
        (
            "### 5.5 Primary window versus the pre-registered extension (all origins)",
            {k: v for k, v in base.items() if k != "window"},
            "window",
            ["primary", "all"],
        ),
    ]
    for title, fixed, free, values in views:
        out += ["", title, "", md_table(_view(s, fixed, free, values), max_rows=400)]
    cum = _read(d, "cumulative_levels")
    out += ["", "### 5.6 Levels variant (foundation models only), cumulative h-step change", ""]
    if cum.empty:
        out.append("_(no cumulative_levels.csv)_")
    else:
        c = cum.copy()
        for k in ("input_mode", "outturn", "sample", "window"):
            if k in c.columns:
                c = c[c[k].astype(str) == HEADLINE[k]]
        out.append(
            md_table(
                c[
                    [
                        "econ",
                        "target",
                        "horizon",
                        "model",
                        "variant",
                        "n",
                        "rmsfe",
                        "mae",
                        "bias",
                        "wql",
                        "coverage80",
                    ]
                ].sort_values(["econ", "target", "horizon", "model"]),
                max_rows=400,
            )
        )
    return out


def section_bias(d: Path) -> list[str]:
    out = ["## 6. Q4: forecast error on forecast revision (fixed-event sequences)", ""]
    b = _read(d, "bias_fixed_event")
    if b.empty:
        out.append("_(no bias_fixed_event.csv)_")
    else:
        out.append(
            "Slope `beta` of the error (outturn minus forecast) on the revision from the previous "
            "origin for the same target period; HAC standard errors. `per_target` rows are per "
            "(econ, target); `pooled` rows standardise by target and pool across an economy's "
            "targets (`beta_std`)."
        )
        hb = b[b["input_mode"].astype(str) == "realtime"] if "input_mode" in b else b
        for lvl, g in hb.groupby("level"):
            out += ["", f"**{lvl}**", ""]
            cols = [c for c in g.columns if c not in ("level",) and g[c].notna().any()]
            out.append(md_table(g[cols].sort_values(cols[:4]), max_rows=400))
    sp = _read(d, "bias_spf_fixed_event")
    out += ["", "## 7. Q4: ECB SPF respondents and matched model runs", ""]
    if sp.empty:
        out.append("_(no bias_spf_fixed_event.csv; run `ffcast spf`)_")
    else:
        out.append(
            "Same regression on the ECB Survey of Professional Forecasters: individual "
            "respondents pooled with forecaster fixed effects (`spf_individual_fe`), the "
            "consensus mean, each model and the cross-model mean, on the same rounds and "
            "calendar-year targets (`docs/backtest.md`, SPF)."
        )
        out += ["", md_table(sp.sort_values(["variable", "outturn", "who"]), max_rows=400)]
    return out


# ------------------------------------------------------------------ driver


def build_summary(cfg: Config | None = None, root: Path = BACKTEST_ROOT) -> str:
    cfg = cfg or load_config()
    d = root / TABLES
    parts = [
        "# Backtest results summary (private, HUMAN GATE 4)",
        "",
        f"Generated {dt.datetime.now(dt.UTC).isoformat(timespec='seconds')} from the CSVs in "
        f"`{d}` and the run bookkeeping under `{root}`. Tables only; no interpretation. "
        "Forecast-derived: stays under `data/` and is not published.",
        "",
        "Horizons (steps after the target's last in-vintage observation): "
        + ", ".join(f"{k}: {v}" for k, v in cfg.horizons.items())
        + f". Primary window from {cfg.origins.first}; extension from "
        f"{cfg.origins.extension_first}. Foundation-model weights dates and stated training "
        "cutoffs:",
        "",
        md_table(
            pd.DataFrame(
                [
                    (m, f.weights_date, f.training_cutoff or "")
                    for m, f in cfg.foundation_models().items()
                ],
                columns=["model", "weights_date", "training_cutoff"],
            )
        ),
        "",
    ]
    for sec in (
        section_run(root),
        section_coverage(root),
        section_outturns(root),
        section_headline(d),
        section_views(d),
        section_bias(d),
    ):
        parts += [*sec, ""]
    return "\n".join(parts)


def write_summary(cfg: Config | None = None, root: Path = BACKTEST_ROOT) -> Path:
    d = root / TABLES
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SUMMARY.md"
    p.write_text(build_summary(cfg, root), encoding="utf-8")
    return p
