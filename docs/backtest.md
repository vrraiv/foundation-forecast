# Backtest harness (Phase 4)

How forecasts are produced, stored and scored. Rules were fixed in `configs/default.yaml`
(`backtest`, `scoring`) and committed before the first full run on 2026-11-18. Results live under
`data/backtest/` (git-ignored, private until HUMAN GATE 4); this document has no numbers.

## Run

`ffcast backtest --window all` runs three stages:

1. **Stage 1 (heavy, parallel over origins).** For every origin (25th or next business day,
   2001-01 to the present), target and input mode, `ffcast.models.panel.build_panel` assembles
   the information set through `as_of` only. The classical benchmarks (naive mean, direct AR by
   BIC, Minnesota BVAR with marginal-likelihood hyperparameters, mixed-frequency factor model,
   equal-weight combination) are estimated on that vintage and written to
   `forecasts/bench/<origin>.parquet`. Foundation-model tasks (history arrays only) are written
   to request files, one per model per 12 origins.
2. **Stage 2 (lean process).** Each request runs in the model's own locked environment
   (`envs/<env>`), offline, seed 0, 4 threads. Workers never import `ffcast`.
3. **Stage 3 (heavy).** Responses become `forecasts/fm/<origin>.parquet`; outturns and the run
   manifest are rebuilt.

Benchmarks run in 6 processes with 4 BLAS threads each (fixed, so results do not depend on
machine load). Files are written atomically. `ffcast backtest --verify N` recomputes the
benchmarks at N stored origins and compares every value exactly.

## Rules

- **Input modes.** `realtime`: every series as of the origin (strict). `revised`: the latest
  pinned vintage of the same resolved series, cut to the reference periods visible in the
  real-time vintage at that origin, transformed within the latest vintage. Pseudo-vintage
  targets (`exclude_from_q1`) have no revised mode.
- **Variants.** `stationary`: models receive the transformed series and are scored in that
  space (primary, every model). `levels`: foundation models only; they receive levels and the
  level quantiles are mapped exactly to the step-1 transform and to the cumulative h-step
  change. Benchmarks have no levels variant.
- **Horizons.** Every step 1..max is stored; tables use the configured horizons (M: 1, 3, 6,
  12; Q: 1, 2, 4). Step h refers to the h-th period after the target's last observation in its
  own vintage (`target_period` column), so publication lags are respected and fixed-event
  sequences join on `target_period`.
- **Minimum history.** A target is skipped at an origin with fewer than 120 monthly or 40
  quarterly in-vintage observations.
- **Combinations** exist only when every member exists at that origin.
- **Outturns.** First release: the value in the first vintage containing the period,
  transformed inside that vintage. Revised: the vintage visible 12 months after that date. A
  first release counts only if it appeared no later than the series' median first-release lag
  plus the source's staleness limit after the period end; later ones are flagged `late`, dropped
  from first-release scoring and counted. Unemployment is rounded to one decimal before revisions
  are measured.
- **Cache.** Every row carries a key hashing the config slice that affects it (target,
  conditioning list, horizons, origin rules, vintage sources, backtest rules, model settings),
  the data-manifest hashes of the series used, and the weights digest. Matching origins are
  skipped on rerun. `run_manifest.json` records the config hash at the first run; a later
  change is flagged there.

## Store

`forecasts/*/<origin>.parquet`: origin, econ, target, freq, model, variant, input_mode, space
(`transformed` | `level`), step, target_period, quantile, value, mean, series_id, source_role,
cache_key. `meta/*/<origin>.parquet`: one row per (origin, econ, target, model, variant,
input_mode) with status (ok, skipped, error), note, last_period, last_level, n_history, n_vars,
runtime. `outturns.parquet`, `cumulative_outturns.parquet`.

## Scoring (`ffcast score`)

Per cell (econ, target, horizon, model, variant, input_mode, outturn, sample full | ex_covid,
window primary | all, split all | pre | post weights date, and pre/post training cutoff where
the model card states one): n, RMSFE, MAE, bias, relative RMSFE and MAE to the AR of the same
cell, Diebold-Mariano against AR with the Harvey-Leybourne-Newbold correction (squared errors,
Bartlett kernel with h-1 lags), weighted quantile loss (mean pinball loss over the nine
quantiles, times two), 80% interval coverage, PIT histogram (ten bins). Model confidence set
(Hansen, Lunde and Nason; T_max statistic; moving-block bootstrap) at 90% per cell group.
`combo_fm` is the equal-weight mean of the five univariate foundation-model forecasts where all
five exist. Tables: `data/backtest/tables/{scores,pit,mcs,cumulative_levels}.csv`.

## Q4 bias regressions

`bias_fixed_event.csv`: per (econ, target, model, variant, input_mode), the error
`outturn - f_k` on the revision `f_k - f_{k-1}` across successive origins for the same target
period (HAC standard errors), and pooled per model across targets after standardising by
target.

`bias_spf_fixed_event.csv` (`ffcast spf`): ECB Survey of Professional Forecasters microdata
(point forecasts per anonymised respondent and round, calendar-year targets). Models are run at
origin = survey end + 1 day for every round whose survey window is printed on the ECB release
page (`docs/spf_rounds.md`; 2015Q1 onward, two rounds skipped), on euro-area HICP, core HICP,
GDP and unemployment, with the horizon reaching December of the year after next; the mean path
(median where the model reports no mean) is converted to the survey definitions (annual-average
inflation and growth, annual-average unemployment rate, rolling year-on-year). Outturns use the
same definitions inside the first vintage containing the last period needed and the vintage 12
months later. Regressions: individual respondents pooled with forecaster fixed effects, the
consensus mean, each model, and the cross-model mean, on the same rounds and targets. TimesFM's
`max_horizon` is raised to the SPF horizon for these runs only (recorded in the request file).

## Not covered

Canadian core CPI (blocked, no data). Canada has no public individual-level survey, so the
survey comparison is euro area only (PLAN section 5).
