# Backtest harness (Phase 4)

How forecasts are produced, stored and scored. Rules were fixed in `configs/default.yaml`
(`backtest`, `scoring`) and committed before the first full run on 2026-11-18. One change was
made after the run started and before any result was read: the Canadian core CPI target was
redefined as CPI-XFET from an owner-supplied table (owner approval 2026-11-18,
`docs/data_quality_notes.md`); it was computed in a second pass that the cache restricted to that
target, and `run_manifest.json` flags the config change. Results live under `data/backtest/`
(git-ignored, private until HUMAN GATE 4); this document has no numbers.

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

## Deviations after the first full run

Recorded here and in `STATUS.md`, as the config requires. None was chosen by looking at errors
against outturns.

1. **Canadian core CPI** added as CPI-XFET after the run started (owner approval); computed in a
   second pass restricted to that target by the cache.
2. **DFM numerical breakdown (2026-11-18).** A benchmark-only scoring pass showed the dynamic
   factor model with log-likelihoods near -1e54 and forecasts up to 1e97 at 52 of 5,200
   (origin, target, input mode) cells, contaminating `combo_bench`. The fitted transition
   matrices were stationary; the EM iterations from statsmodels' default start ran normally for
   about ten iterations and then diverged numerically (reproduced). Remedies were compared on
   numerical validity only: `em_initialization=False` repaired 52 of 52 and, on a seeded sample of
   30 sane cells, changed the log-likelihood by between -14 and +61 (median -10) relative to the
   default; trimming the panel to the target's span also repaired 52 of 52 but changes the
   estimation sample; a coverage filter alone repaired 10. The estimator setting with the fewest
   new choices was taken: `em_initialization: false` in config. Every benchmark cell was then
   recomputed (`BENCH_CODE_VERSION` 2 in the cache key; foundation-model keys unchanged); the
   AR, BVAR and naive values must be identical to the first run and are checked against the
   backed-up store. Outcome on the 269 of 310 origins recomputed before the run was stopped
   (2001-01 to 2023-05; the rest is pending): AR, BVAR and naive forecasts identical row for row
   (1.09 million rows, zero differences, apart from the guard trips in item 3); DFM origins with
   absurd values 47 -> 0; on the 4,608 DFM cells common to both runs, 53 cells that failed with
   "matrix not positive definite" or "infs or NaNs" now estimate, no cell went the other way, and
   169 cells still fail for input-data reasons that pre-date the fix (constant predictor columns
   92, non-finite input 67, empty panel 10; clustered in 2001, 2009-10 and 2017; `combo_bench`
   is missing wherever a member is). Cause, checked on one cell per cluster by rebuilding the
   panel at the origin: the DFM takes the first `max_vars` monthly columns of the panel without
   the coverage filter the BVAR applies, and at those origins one column has almost no in-vintage
   observations, so standardisation fails or produces non-finite values: the Bank of Canada
   policy-rate series `valet:B114039` (1 to 10 observations, constant, 2009-10), the 10-year
   yield `valet:BD.CDN.10YR.DQ.YLD` (all missing, 2001), the exchange rate `valet:FXUSDCAD`
   (1 observation, 2017). Remedy and decision for the owner: (a) leave these cells as recorded
   errors (current state), or (b) give the DFM the same minimum-coverage rule as the BVAR, which
   is a benchmark-code change (`BENCH_CODE_VERSION` 3, every benchmark cell recomputed, about
   2.5 hours) and also alters the DFM input in cells that currently estimate fine whenever a
   short column is dropped there. Final count on all 310 origins: 190 DFM errors of 5,736 DFM
   cells (3.3%; 21 of them core CPI cells added in the second pass). Mechanism, confirmed from
   the raw Valet downloads: each series starts on a different date (10-year yield 2001-01-02;
   target for the overnight rate 2009-04-21, a changes-only series with 35 observations in all;
   USD/CAD 2017-01-03), the column enters the panel from its first observation, and the DFM fails
   during the first year or so of each series while the column has 0 to 13 in-vintage values.
   That explains 180 of the 190; the other 10 (euro-area HICP, core HICP and retail at the
   2021-09 and 2021-10 origins, empty monthly panel) have a different, untraced cause. A sample
   of 81 origins showed that the BVAR's selection rule would alter the DFM input in about two
   thirds of the cells that estimate fine, so option (b) is a different benchmark, not a repair.
   **Owner's decision (2026-11-18 evening): option (a), the rule is not changed now; the 190
   cells stay recorded errors.**
3. **Validity guard.** `backtest.validity` (config): a forecast is a numerical failure when a
   quantile or mean is non-finite, the estimator's log-likelihood is below -1e10, or the largest
   absolute quantile or mean exceeds 50 standard deviations of the model's own input history in
   the space it forecast in. Failures are stored as status `error` with the reason, counted in
   the summary, and never as values; the guard runs before the benchmark combination and on every
   foundation-model response. The guard is applied when rows are stored and is not part of the
   cache key. What it caught in the recomputed benchmarks (269 origins): zero DFM cells (the
   initialisation fix removed the breakdown it was written for) and 11 multivariate BVAR cells at
   the origins of 2020-08 to 2020-11 (Canadian CPI, core CPI, retail, unemployment, consumption;
   euro-area consumption), where the pandemic shock passing through the VAR produced forecasts
   far outside the rule (the magnitudes are in the private meta store, not here). Those cells
   were `ok` in the first run and are now `error`, so BVAR's own-sample statistics exclude them;
   the relative statistics against AR are computed on common origins, the model confidence set
   drops every origin where any member is missing (so these errors and the DFM errors shrink that
   sample for every model), and the ex-COVID sample loses only the horizons from those origins
   that reach beyond 2021-06. The threshold is not changed after seeing this (that would be
   tuning on the sample); whether the magnitude rule should apply to every model or the guard be
   limited to non-finite values and the log-likelihood floor was put to the owner before scoring.
   Evidence given to the owner: the 11 tripped values lie 80 to 550 history standard deviations
   out, far beyond any realised 2020 move, while values of 40 to 78 percent per period from the
   AR, the BVAR and foundation-model tail quantiles at the same pandemic origins passed, because
   the history standard deviation at those origins includes the COVID collapse; so the guard is a
   numerical-failure filter, not a plausibility filter, and moving the threshold either way now
   would be a post-hoc choice made with the magnitudes in view. **Owner's decision (2026-11-18
   evening): keep the guard as configured for every model.** The owner noted that a design with
   the COVID observations in mind might have been chosen beforehand; the ex-COVID slice is the
   pre-registered answer, and a pre-2020-origin view would be a subsample of this run, not a new
   run.
4. **Cache key.** The live-data source (`latest`) was removed from a target's key on 2026-11-18
   because the backtest never reads it; this re-keyed every cell, so the two trial origins of
   Chronos-2 and Moirai are recomputed in the second pass.
5. **Cache bookkeeping per cell (2026-11-18 evening, no effect on any value).** The done-check
   used to work per (model, origin) and only verified the keys of cells present in the store, so
   a target absent from the store was taken as done: Canadian core CPI was skipped as `blocked`
   at every origin when the model stage started, and the planned second pass would have computed
   nothing for it. Now the unit is the (origin, econ, target, input mode) cell; skipped cells
   carry a skip key (target definition and data hashes) so that a stale skip is re-evaluated;
   stage 1 writes the cell list (`todo.json`) and stage 3 and the benchmark writer replace only
   those cells, keeping every other model's and cell's rows. On the stored benchmarks this
   re-evaluates only keyless skipped cells (panel built, nothing estimated) plus the 41 origins
   not yet recomputed; on the model store after the merge it adds the core CPI tasks and
   re-evaluates the skips, with no model re-run.

## Run log

- 2026-11-18 07:52 full run started; 12:24 benchmark store backed up; 13:02 benchmark recompute
  (`BENCH_CODE_VERSION` 2) started alongside the model stage.
- 2026-11-18 15:28 both jobs stopped by the Claude Code harness for machine-wide memory pressure.
  The model stage had completed all 130 worker files (all five models, 310 origins, every worker
  `ok`) but the merge into the store (stage 3) had not run; the recompute had rewritten 269 of
  310 benchmark origins. Nothing was lost: worker responses sit in
  `data/backtest/work/20261118T075221/responses/`, and the cache skips the recomputed origins.
  Stage 3 was then changed to merge one model at a time (bounded memory). Restart sequence,
  awaiting the owner: (1) stage 3 on that workdir, before any other `backtest` call, since stage
  1 would otherwise see an empty model store and redo the seven-hour model stage; (2) the
  remaining 41 benchmark origins with `--skip-fm` and nothing running alongside; (3) the second
  pass (core CPI and the two re-keyed trial origins), then verify, score, SPF.
- 2026-11-18 evening: the owner suspects a vendor utility leaking memory, will reboot, close
  Chrome and Steam, and restart the agent session before the jobs restart (another Claude session
  stays running). Runbook for the next session, one job at a time, from the repo root:

  ```
  uv run python -m ffcast.eval.backtest stage3 "{\"workdir\": \"C:\projects\foundation-forecast\data\backtest\work\20261118T075221\", \"note\": \"2026-11-18: core CPI (CPI-XFET) added after launch (owner approval); DFM em_initialization=false and validity guard after the DFM numerical breakdown; benchmarks recomputed under BENCH_CODE_VERSION 2\"}"
  uv run ffcast backtest --window all --skip-fm --processes 4
  uv run ffcast backtest --window all
  uv run ffcast backtest --window all --verify 5
  uv run python scripts/compare_bench_stores.py data/backtest/_backup_bench_20261118T122416
  uv run ffcast score
  uv run ffcast spf
  ```

  Expected: step 1 writes 310 model-store origins (every worker was ok) and reports the
  foundation-model error count; step 2 reports 41 origins fully to do and keyless skips at the
  rest, and estimates nothing new at the 269; step 3 adds the core CPI tasks for every model plus
  the two re-keyed trial origins of Chronos-2 and Moirai, nothing else; step 5 must show zero
  differing AR/BVAR/naive rows against the backup on all 310 origins (the writer now rewrites
  every file). The guard-scope and DFM-coverage decisions (STATUS, "Blocked or needing the
  owner") come before step 6.
- 2026-11-18 evening, after the owner's reboot (21 GB free), one job at a time. Step 1: 310
  origins merged, 74,670 model tasks ok, 0 errors, guard tripped on no model response, note in
  the run manifest. Step 2 (4 processes, 50 min): 2,563 cells to do over 310 origins (the 41
  not yet recomputed in full, keyless skipped cells at the other 269), no model work; afterwards
  the 1,704 skipped benchmark cells all carry a skip key. Step 5 run early on all 310 origins:
  zero differing AR/BVAR/naive rows against the backup (429,192 / 428,472 / 429,192 rows
  compared); DFM 57 error -> ok and 0 ok -> error on 5,426 common cells, 169 input-data errors
  unchanged; guard trips BVAR 11; rows only in the current store are the core CPI benchmark
  cells, rows only in the backup are the 11 guard-tripped BVAR cells. Step 3 started 18:12.
- 2026-11-18 18:59 step 3 done (47 min, stage 1 12 min): work list exactly as predicted, 4,570
  model tasks, all ok, 0 errors: core CPI real-time at all 310 origins for every model (two
  variants for Chronos-2 and TiRex-2), plus the two re-keyed trial origins 2024-05-27 and
  2024-06-25 for Chronos-2 and Moirai (230 tasks); the other listed cells were the 1,704 keyless
  skips from the first run, re-keyed with no model call. Model store afterwards: every model
  row ok, no keyless row. Step 4 (`--verify 5`) started 19:02 with step 5 (read-only) alongside.
- 2026-11-18 19:09 step 4 passed (benchmarks only; `--verify` runs no model): origins 2002-09-25,
  2012-01-25, 2017-06-26, 2018-12-25 and 2022-10-25 recomputed from scratch, identical to the
  store (`verify_20261118T190908.json`). Since none of the five fell among the 41 origins
  recomputed after the reboot, 2024-10-25 and 2026-03-25 were verified by hand too, identical
  (`verify_20261118T191840.json`). The midday benchmark-only tables (pre-fix DFM) were moved to
  `_tables_bench_only_broken_dfm_20261118T1152/` so `tables/` holds only the final run's output.
  Step 5 on the final store: unchanged from the 18:12 run (zero differing AR/BVAR/naive rows on
  all 310 origins). Steps 6 and 7 wait for the owner's guard-scope and DFM-coverage decisions.

## Private summary

`ffcast score` also writes `data/backtest/tables/SUMMARY.md` (`ffcast.eval.summary`): run
bookkeeping (config hashes, weights digests, verify result), coverage and skip reasons, outturn
counts, the headline slice (real-time input, first-release outturn, full sample, primary window,
stationary variants, configured horizons: relative RMSFE and MAE to AR, Diebold-Mariano p-values,
weighted quantile loss, coverage, model-confidence-set membership), one view per plan question
(real-time versus revised, outturn definition, pre/post weights date and training cutoff,
ex-COVID, extension window, levels variant), and the Q4 regressions including the SPF table when
present. The slices were fixed and committed before any foundation-model result existed. Tables
only, no interpretation; the file stays under `data/`.

## Not covered

Canadian core CPI has pseudo-vintages only (unrevised by convention), so it has no `revised`
input mode and is excluded from Q1. Canada has no public individual-level survey, so the survey
comparison is euro area only (PLAN section 5).
