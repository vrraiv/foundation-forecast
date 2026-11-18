# PLAN: real-time scoring of open foundation models on macro data

Status of this document: design brief written 17 November 2026. Source details (endpoints, table numbers, model IDs) were checked only lightly and must be confirmed in Phase 0. Design choices marked **DEFAULT** are the owner's to change at the Phase 0 gate; after the pre-registration is frozen (Phase 5) they are fixed.

## 1. Research questions

| ID | Question | Output |
| --- | --- | --- |
| Q1 | How much does evaluating on revised data, instead of real-time vintages, flatter foundation models relative to benchmarks? | Relative accuracy on real-time vs revised inputs |
| Q2 | Is accuracy better for periods before a model's training cutoff than after? | Pre/post-cutoff comparison per model |
| Q3 | Do foundation models beat AR, BVAR and factor-model benchmarks for Canada and the euro area in real time? | Relative RMSFE and density scores with significance tests |
| Q4 | Do the models show the forecast biases documented for human forecasters (under-reaction in the consensus, over-reaction individually)? | Error-on-revision regressions, models vs ECB survey forecasters |
| Q5 | Do backtest results hold up in a genuinely live record? | Monthly registry, scored once enough outturns accumulate |

Known context: a US-data study (MACROCAST, arXiv 2606.28670) already covers Q1 and Q3 for FRED-MD. The contribution here is non-US data, Q2 and Q4, and the live record.

## 2. Design decisions

**Economies.** Canada and the euro area.

**Targets (DEFAULT, 6 per economy).**

| Target | Canada | Euro area | Frequency |
| --- | --- | --- | --- |
| Real GDP growth | Expenditure-based GDP | Real GDP | Quarterly |
| Headline inflation | CPI, all items | HICP, all items | Monthly |
| Core inflation | CPI ex food and energy | HICP ex energy, food, alcohol, tobacco | Monthly |
| Unemployment rate | LFS | Eurostat | Monthly |
| Activity | Monthly GDP by industry, all industries | Industrial production ex construction | Monthly |
| Retail sales | Volume | Volume | Monthly |

**Conditioning set.** Up to about 20 further series per economy for the multivariate models, restricted to series with real vintages. Unrevised financial series (policy rate, yields, exchange rate, oil price, equity index) may be added without vintages, using values dated on or before the origin.

**Horizons (DEFAULT).** Monthly targets: 1, 3, 6, 12 months. Quarterly: 1, 2, 4 quarters. Horizons count from the last observed period at the origin, so publication lags are respected.

**Forecast origins.** One per month, on a fixed calendar day (**DEFAULT**: the 20th, or the next business day). The information set is, for each series, the latest vintage published on or before the origin.

**Evaluation window (DEFAULT).** 2015-01 to present for both economies, because Statistics Canada's real-time tables start around January 2015. Extend earlier where vintages allow (euro area from 2001; Canada via the OECD revisions database) as a robustness check. Report all results with and without 2020Q1 to 2021Q2.

**Transformations (DEFAULT).** Primary specification feeds each model the stationary transform (log-difference or difference) and scores in that space. A secondary specification feeds levels and transforms the forecast. Both are recorded as separate model variants.

**Outturn definition.** Score against two "actuals": the first release, and the vintage available 12 months after the first release. Report both.

**Models.**

| Model | Expected Hugging Face ID | Notes |
| --- | --- | --- |
| Chronos-2 | `amazon/chronos-2` | Run univariate and multivariate; Apache 2.0; released Oct 2025 |
| TimesFM 2.5 | `google/timesfm-2.5-200m-pytorch` | Univariate; confirm ID and licence |
| TiRex | `NX-AI/TiRex` | Univariate; confirm ID and licence |
| Moirai 2.0 | `Salesforce/moirai-2.0-R-small` | Univariate; confirm ID and licence |

All run zero-shot, CPU is acceptable. For each, record: weight revision hash, licence, release date, and the best available statement of training-data cutoff and whether the corpus includes macro series. Do not use newer weights under non-commercial licences without asking.

**Benchmarks.** All re-estimated at every origin on that origin's vintage.

- Random walk / historical mean (whichever is standard for the transform).
- AR(p), direct multi-step, p chosen by BIC with p ≤ 12 (monthly) or 4 (quarterly).
- BVAR with Minnesota prior, hyperparameters chosen by marginal likelihood at each origin (Giannone, Lenza and Primiceri approach). Medium-sized: targets plus conditioning set.
- Dynamic factor model handling mixed frequency and ragged edges (`statsmodels` `DynamicFactorMQ` is acceptable).
- Equal-weight combination of the benchmarks, and of the foundation models.

**Scoring.**

- Point: RMSFE and MAE relative to AR. Diebold-Mariano with the Harvey-Leybourne-Newbold small-sample correction. Model confidence set across models.
- Density: quantile forecasts at 0.1 to 0.9, weighted quantile loss / CRPS approximation, coverage of the 80% interval, PIT histograms.
- Always report the number of forecast-outturn pairs behind each statistic.

## 3. Data sources to confirm

| Need | Expected source | What was found on a light check |
| --- | --- | --- |
| Canada vintages | Statistics Canada real-time data tables | 19 series, vintages from about Jan 2015; GDP expenditure vintages (table 36-10-0431) from Nov 2012; monthly GDP by industry vintages exist. Check which targets are covered |
| Euro area vintages | ECB Real Time Database (dataset `RTD` on the ECB Data Portal) | Vintages from Jan 2001; 2015 onward via API, earlier as bulk files; labelled experimental; confirm it is still updated |
| Cross-check and gap-filling for both | OECD short-term statistics revisions dataset (`DSD_STES_REVISIONS@DF_STES_REVISIONS`) | Monthly snapshots of key indicators; confirm coverage, API access and update status |
| Latest data for live runs | Statistics Canada Web Data Service; Eurostat API; ECB Data Portal API | Not checked |
| Human forecasts (euro area) | ECB Survey of Professional Forecasters, individual-level CSV per round | Public, with a dataset description PDF; inflation, GDP growth, unemployment |
| Human forecasts (Canada) | None known that is public and individual-level | Expect a gap; do not use paid sources |

Canadian headline CPI is not revised (not seasonally adjusted); treat it as vintage-free but keep its publication lag. Seasonally adjusted series are revised.

## 4. Phases

### Phase 0: feasibility probe (no build)

1. Confirm each source in section 3: reachable without login, licence or terms allow research use and redistribution of derived results, date range, update cadence, one sample pull.
2. For every DEFAULT target, state which source supplies vintages, from when, and with what gaps. Propose substitutions where a target has no vintages.
3. Confirm each model ID resolves, its licence, size, and that it runs on CPU on a toy series.
4. Write `docs/feasibility.md` with a coverage table and a recommended final target list and evaluation window.

Done when: `docs/feasibility.md` exists and every row of section 3 is marked confirmed, changed or unavailable.

**HUMAN GATE 0.** Owner approves targets, window, origins day and any substitutions.

### Phase 1: repository and environment

- Python 3.11+, `uv` with a committed lockfile, `pytest`, `ruff`. CPU-only `torch`.
- Layout: `src/` (packages `data`, `models`, `bench`, `eval`, `registry`), `tests/`, `configs/`, `docs/`, `data/` (git-ignored), `registry/` (git-ignored, private).
- One config file defines targets, horizons, origins and model variants. No magic constants in code.
- `Makefile` or `justfile` targets: `data`, `backtest`, `score`, `registry-run`, `test`.

Done when: fresh clone plus `uv sync` plus `make test` passes on an empty test suite with CI-style checks runnable locally.

### Phase 2: vintage data layer

1. Downloaders per source that save raw responses unmodified under `data/raw/<source>/<download-date>/` with a SHA-256 manifest.
2. A normalised long table: `series_id, ref_period, value, vintage_date, source`. `vintage_date` is the publication date, not the reference date.
3. `as_of(series_ids, origin_date)` returns, per series, the latest vintage with `vintage_date <= origin_date`. This is the only function models and benchmarks may use to get data.
4. A parallel "revised" view: the latest vintage truncated to the same reference periods visible at the origin. Needed for Q1.
5. A release calendar per series (publication lags), derived from the vintages.
6. Data-quality report: gaps in vintages, rebasing and definitional breaks, changes in euro-area composition, seasonal-adjustment changes.

Tests (required):
- Property test: for random origins, no returned observation has `vintage_date > origin`.
- Changing data dated after an origin never changes that origin's `as_of` output.
- Known revision spot-checks: at least three hand-verified cases per economy where first release and later value differ.

Done when: tests pass and `docs/data_quality.md` lists every known break.

### Phase 3: models and benchmarks

1. A common interface: `forecast(history, horizon, quantiles) -> quantile forecasts`, with a multivariate variant.
2. Wrappers for each foundation model, weights pinned by revision. Deterministic settings; record seeds where sampling is involved.
3. Benchmarks as specified in section 2.
4. `docs/model_cards.md`: per model, the pins, licence, release date and training-data information.
5. Smoke test: every model and benchmark produces forecasts for one origin for every target, with sane magnitudes.

Done when: smoke test passes and runtime per origin is recorded.

### Phase 4: backtest harness and scoring

1. Loop over origins, targets, horizons, model variants and the two input modes (real-time, revised). Cache per-origin results; a rerun must reproduce cached values exactly.
2. Store forecasts in parquet: `origin, target, horizon, model, variant, input_mode, quantile, value`, plus the realised outturns under both definitions.
3. Scoring module per section 2, producing tables only. No interpretation, no charts beyond diagnostics.
4. Bias regressions for Q4 (do not interpret, just produce):
   - Build fixed-event forecast sequences: the same target period forecast from successive origins.
   - Per model and target: regress forecast error on the forecast revision. Also for the cross-model average.
   - Read the ECB survey dataset description and construct model forecasts that match the survey's target definitions (year-on-year rates at the survey's rolling and calendar-year horizons, at the survey's deadline dates) so the same regressions can be run on individual survey respondents.
5. Q2 split: tag each origin as before or after each model's release date and stated training cutoff.

Done when: a full backtest runs end to end from a clean clone and `make score` regenerates every table.

**HUMAN GATE 4.** Owner reviews a results summary before anything further. Do not start tuning in response to results.

### Phase 5: live registry

Purpose: a forecast record that can later be proven to have existed at each date, without publishing the forecasts.

1. `registry-run` for a given origin: pull latest public data, snapshot it, run all pinned models and benchmarks, write the forecast parquet.
2. Write a manifest per run: origin date, UTC timestamp, SHA-256 of the forecast file, of the data snapshot, of the lockfile and of each model's weights, plus the code commit hash. Add a random salt to the forecast-file hash input and store the salt privately.
3. Append the manifest hash (not the manifest contents that reveal values) to a ledger file. Chain each entry to the previous entry's hash.
4. Timestamp each ledger entry independently with OpenTimestamps, and keep the proof files.
5. A `verify` command that, given the private files, checks every ledger entry and proof.
6. Write `PREREGISTRATION.md`: targets, horizons, models, variants, benchmarks, scoring rules, outturn definitions, and the rule for when and how the live record will first be scored (**DEFAULT**: not before 12 monthly origins have outturns). Hash it and make it the first ledger entry.
7. Backups: propose a private, encrypted backup for `registry/`.
8. Scheduling: propose, do not enable. Options to lay out with trade-offs: a local scheduled job, or a scheduled workflow in a private repository. Include failure alerts and a rule for late runs (a run made after its origin date is recorded as late and uses data as of the intended origin where vintages allow, otherwise is flagged).

Tests: tampering with any stored forecast, snapshot or manifest makes `verify` fail; a rerun of a past origin reproduces the same forecast hash.

**HUMAN GATE 5.** Owner approves, in this order: the pre-registration text; creation of any remote repository (private for code and forecasts, public for the ledger only); enabling the schedule. Before the first public ledger entry, the owner confirms their own employer's outside-activity rules allow it. That check is the owner's, not the agent's.

### Phase 6 (deferred, do not start): LLM forecasters

Text-model forecasts need API keys, cost controls and look-ahead diagnostics (fake-date tests, recall probes). Leave an interface stub and a note only.

## 5. Risks the agent should surface, not solve

- Canada's vintage history is short (about a decade), so tests will have low power. Report sample sizes prominently.
- The post-release sample for Q2 is very short for models released in 2025. The live registry is what fixes this.
- Real-time databases have breaks and gaps. Prefer dropping a series to patching it.
- Foundation-model packages may conflict on `torch` versions. If one environment cannot hold them all, use one environment per model behind the common interface and say so.
- No public individual-level human forecasts for Canada: Q4's human comparison is euro area only unless a public source turns up.

## 6. Deliverables at the end of setup

`docs/feasibility.md`, `docs/data_quality.md`, `docs/model_cards.md`, `PREREGISTRATION.md` (draft), `STATUS.md`, a passing test suite, a reproducible backtest, and a registry that has completed one dry run with `verify` passing.
