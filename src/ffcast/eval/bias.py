"""Q4 bias regressions (PLAN Phase 4 item 4). Tables only.

Fixed-event sequences: the same target period forecast from successive origins. For each
(econ, target, model, variant, input_mode) and each target period, order the forecasts by
origin; the revision at origin k is f_k - f_{k-1} (consecutive origins with a forecast for that
period) and the error is outturn - f_k. Regress error on revision (OLS with HAC standard
errors, Bartlett kernel, lag = max horizon - 1) per model and target, per model pooled over
targets (with target fixed effects, errors and revisions standardised by target), and for the
cross-model average of the foundation models (`combo_fm`). Under-reaction to news shows as a
positive coefficient (errors predictable from the revision in the same direction), over-reaction
as a negative one (Coibion-Gorodnichenko style regression on forecast revisions).

Point forecast used: the mean when the model reports one, else the median.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, load_config
from .scoring import load_scored_frame
from .store import BACKTEST_ROOT


def _hac_ols(y: np.ndarray, x: np.ndarray, lag: int) -> tuple[float, float, float, int]:
    """Slope, HAC standard error, intercept, n for y = a + b x + e."""
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    # Degenerate regressor (every revision identical, typically all zero): the slope is not
    # identified, so the row carries NaN for slope and standard error rather than failing the
    # whole table (2026-11-18, found on the first full scoring pass; docs/backtest.md).
    if n < 3 or not np.isfinite(x).all() or not np.isfinite(y).all() or np.ptp(x) == 0.0:
        return float("nan"), float("nan"), float(np.mean(y)) if n else float("nan"), n
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    u = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    S = (X * u[:, None]).T @ (X * u[:, None])
    for k in range(1, min(lag, n - 1) + 1):
        w = 1.0 - k / (lag + 1)
        G = (X[k:] * u[k:, None]).T @ (X[:-k] * u[:-k, None])
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    return float(beta[1]), float(np.sqrt(max(V[1, 1], 0.0))), float(beta[0]), n


def _sequences(gp: pd.DataFrame, outturn: str) -> list[tuple[int, float, float, object]]:
    """Fixed-event revisions and errors for one target period: rows of successive origins,
    revision f_k - f_{k-1} between consecutive origins, error from each row's OWN outturn
    (rows whose outturn is missing, for instance because their series id has no outturn, give
    no error row; before 2026-11-18 the first row's outturn was used for every row, which made
    the whole error vector NaN whenever that row lacked one). Returns (k, revision, error,
    origin) tuples."""
    gp = gp.drop_duplicates("origin").sort_values("origin")
    if len(gp) < 2 or gp[outturn].isna().all():
        return []
    f = gp["point"].to_numpy(dtype=float)
    y = gp[outturn].to_numpy(dtype=float)
    org = gp["origin"].to_numpy()
    return [
        (k, f[k] - f[k - 1], y[k] - f[k], org[k])
        for k in range(1, len(gp))
        if np.isfinite(y[k]) and np.isfinite(f[k]) and np.isfinite(f[k - 1])
    ]


def fixed_event_table(
    cfg: Config | None = None, root: Path = BACKTEST_ROOT, outturn: str = "first_release"
) -> pd.DataFrame:
    cfg = cfg or load_config()
    tr, _ = load_scored_frame(cfg, root)
    if tr.empty:
        return pd.DataFrame()
    tr = tr[tr["space"] == "transformed"].copy()
    tr["point"] = tr["mean"].where(tr["mean"].notna(), tr["q0.5"])
    rows = []
    keys = ["econ", "target", "model", "variant", "input_mode"]
    for key, g in tr.groupby(keys):
        seqs = []
        for period, gp in g.groupby("target_period"):
            steps = gp.drop_duplicates("origin").sort_values("origin")["step"].to_numpy()
            for k, rev, err, origin in _sequences(gp, outturn):
                seqs.append(
                    {
                        "period": period,
                        "origin": origin,
                        "step": int(steps[k]),
                        "revision": rev,
                        "error": err,
                    }
                )
        if len(seqs) < 20:
            continue
        s = pd.DataFrame(seqs)
        lag = int(max(cfg.horizons[cfg.targets[key[0]][key[1]].freq])) - 1
        b, se, a, n = _hac_ols(s["error"].to_numpy(), s["revision"].to_numpy(), lag)
        rows.append(
            dict(
                zip(keys, key, strict=True),
                outturn=outturn,
                n=n,
                n_periods=s["period"].nunique(),
                beta=b,
                se_hac=se,
                t=b / se if se > 0 else np.nan,
                alpha=a,
            )
        )
    per = pd.DataFrame(rows)
    # pooled per model across targets of an economy: standardise by target, target fixed effects via demeaning
    pooled = []
    for (econ, model, variant, mode), g in tr.groupby(["econ", "model", "variant", "input_mode"]):
        allseq = []
        for _target, gt in g.groupby("target"):
            seqs = []
            for _period, gp in gt.groupby("target_period"):
                seqs.extend((rev, err) for _k, rev, err, _o in _sequences(gp, outturn))
            if len(seqs) < 20:
                continue
            a = np.asarray(seqs)
            sd_e, sd_r = a[:, 1].std(), a[:, 0].std()
            if sd_e <= 0 or sd_r <= 0:
                continue
            allseq.append(
                np.column_stack(
                    [(a[:, 0] - a[:, 0].mean()) / sd_r, (a[:, 1] - a[:, 1].mean()) / sd_e]
                )
            )
        if not allseq:
            continue
        A = np.vstack(allseq)
        b, se, a0, n = _hac_ols(A[:, 1], A[:, 0], 11)
        pooled.append(
            {
                "econ": econ,
                "model": model,
                "variant": variant,
                "input_mode": mode,
                "outturn": outturn,
                "n": n,
                "n_targets": len(allseq),
                "beta_std": b,
                "se_hac": se,
                "t": b / se if se > 0 else np.nan,
            }
        )
    per["level"] = "per_target"
    pooled_df = pd.DataFrame(pooled)
    pooled_df["level"] = "pooled_std"
    return pd.concat([per, pooled_df], ignore_index=True)


def write_bias_tables(cfg: Config | None = None, root: Path = BACKTEST_ROOT) -> Path:
    cfg = cfg or load_config()
    d = root / "tables"
    d.mkdir(parents=True, exist_ok=True)
    parts = [fixed_event_table(cfg, root, o) for o in ("first_release", "revised_12m")]
    parts = [p for p in parts if not p.empty]
    out = (
        pd.concat(parts, ignore_index=True)
        if parts
        else pd.DataFrame(
            columns=[
                "econ",
                "target",
                "model",
                "variant",
                "input_mode",
                "outturn",
                "n",
                "beta",
                "se_hac",
                "t",
                "level",
            ]
        )
    )
    out.to_csv(d / "bias_fixed_event.csv", index=False)
    return d / "bias_fixed_event.csv"
