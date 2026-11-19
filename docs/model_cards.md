# Model cards

Per model: pinned weights, licence, release date, training-data statement, inference settings
and runtime. Pins are what `ffcast.models.weights.ensure_weights` downloads and verifies by
SHA-256 of every file; the whole-snapshot digest is written into every forecast's metadata.
Inference settings are frozen in `configs/default.yaml` (`models.settings`) and described in
`workers/_protocol.md`. All models run zero-shot on CPU, one worker process per model
environment (`envs/<env>/uv.lock`), seed 0, 4 threads, deterministic algorithms where
PyTorch supports them; a rerun of the same request produced byte-identical output for Chronos-2,
TiRex, TiRex-2 and Moirai 2.0 on a synthetic task and for TimesFM 2.5 and Chronos-2 on the
real smoke requests (11 and 22 tasks) on 2026-11-18.

| Model | Hugging Face ID | Revision (sha) | Weight file date | Release date (HF repo created) | Licence | Package (locked) | Variants |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Chronos-2 | `amazon/chronos-2` | `29ec3766d36d6f73f0696f85560a422f50e8498c` | 2025-10-30 | 2025-10-30 | Apache-2.0 | `chronos-forecasting` 2.3.2, torch 2.15.0+cpu, transformers 5.23.0 | univariate, multivariate (joint forecast of target and conditioning variates) |
| TimesFM 2.5 | `google/timesfm-2.5-200m-pytorch` | `1d952420fba87f3c6dee4f240de0f1a0fbc790e3` | 2025-10-01 (refreshed weights) | 2025-09-02 | Apache-2.0 | `timesfm` 3.0.2, torch 2.15.0+cpu | univariate |
| TimesFM 3.0 (added 2026-11-19) | `google/timesfm-3.0-pytorch` | `43046b85ec22d584a13f8098c2ed39c889e129c2` | 2026-08-24 (later commits change README and licence metadata only) | 2026-08-24 | TimesFM Non-Commercial License v1.0 (non-commercial and non-production use; weights may not be redistributed; outputs are not derivatives) | `timesfm` 3.0.2 (class `TimesFM3Forecaster`), torch 2.15.0+cpu, environment `envs/timesfm3` with the same pins as `envs/timesfm` | univariate, multivariate (all variates as joint targets, variate 0 returned) |
| TiRex | `NX-AI/TiRex` | `43ebaaff068c1390785c387b3e5178df3f4c92ca` | 2025-05-26 | 2025-05-26 | NXAI Community License (research use free; attribution; commercial licence above EUR 100m revenue) | `tirex-ts` 1.4.2, torch 2.15.0+cpu | univariate |
| TiRex-2 | `NX-AI/TiRex-2` | `352636173653592b6dceb3fbeee9224ca97952a9` | ckpt 2026-07-02; safetensors 2026-10-06 | 2026-06-16 | Apache-2.0 | `tirex-2` 0.5.0, torch 2.15.0+cpu | univariate, multivariate |
| Moirai 2.0 | `Salesforce/moirai-2.0-R-small` | `30f43ff08c8494f4943ae1521e9d4e94a0fbb389` | 2025-08-06 | 2025-08-06 | CC-BY-NC-4.0 (non-commercial) | `uni2ts` 2.0.0, torch 2.4.1+cpu, gluonts 0.14.4 | univariate |

## Training data and cutoffs

No model publishes a calendar cutoff for its real-data corpus. Statements found (Phase 0,
`docs/probes/models.md`):

- **Chronos-2** (arXiv 2510.15821): 23 real univariate datasets from the Chronos and GIFT-Eval
  pretraining corpora (energy, transport, weather, cloud, M4 daily/hourly/weekly/monthly,
  Wikipedia). Multivariate ability trained on synthetic data only. FRED-MD not listed.
- **TimesFM 2.5** (model card): GiftEvalPretrain, Wikimedia pageviews (cutoff Nov 2023), Google
  Trends (cutoff end-2022).
- **TimesFM 3.0** (model card): GiftEvalPretrain excluding the datasets that overlap with
  fev-bench, Wikipedia pageviews (cutoff Nov 2023), Google Trends top queries (cutoff end-2022),
  synthetic and augmented data. No statement on macro series.
- **TiRex** (arXiv 2505.23719): Chronos training sets incl. M4 daily/hourly/monthly/weekly,
  GiftEvalPretrain subset, synthetic Gaussian-process data. No FRED-MD, M3 or CIF.
- **TiRex-2** (model card tag): `Salesforce/lotsa_data`, which contains FRED-MD, M3, M4 and CIF.
  Not confirmed in the documentation site; paper arXiv 2607.01204.
- **Moirai 2.0** (arXiv 2511.11698): GIFT-Eval pretrain and train splits, Chronos-Mixup
  (non-leaking subset), KernelSynth, internal Salesforce data covering about Jan 2024 to
  Jan 2025.

For the pre/post-release split (Q2) the boundary is the weight file date above; TiRex-2's
boundary is ambiguous between 2026-07-02 and 2026-10-06 and both are recorded.

## Inference settings (frozen 2026-11-18)

- Context: the last 512 observations of the transformed, within-vintage history.
- Quantiles 0.1 to 0.9. Chronos-2 and Moirai 2.0 return these levels directly (Moirai 2.0 is a
  quantile-output model, so no sampling is involved); TimesFM 2.5, TiRex and TiRex-2 have fixed
  decile heads. Quantile crossing is removed by sorting (recorded as `rearranged`).
- TimesFM flags: `normalize_inputs`, `use_continuous_quantile_head`, `force_flip_invariance`,
  `fix_quantile_crossing` on; `infer_is_positive` off; `max_horizon` 12.
- TimesFM 3.0 (settings fixed 2026-11-19 before any forecast was made): the package defaults,
  `use_symmetric_averaging`, `make_positive` and `use_znorm` off, `sort_quantiles` on,
  `padding_mode` none; fixed decile heads; the point forecast is the median head, so no mean is
  stored. Smoke at 2024-06-25: 21 tasks (12 univariate, 9 multivariate), all sane, step 1 aligned
  with TimesFM 2.5 on every target. Rerun check on 40 real backtest tasks (1 to 11 variates):
  two runs identical in every value.
- TiRex-2 and TiRex run with `torch.compile` disabled (no MSVC on Windows).
- Multivariate variants receive the target plus the conditioning variables selected by the
  rule in `ffcast.models.panel.Panel.multivariate` (coverage at least 80% of the last 240
  months or 80 quarters, not more than 12 periods stale, at most 12 variables), as a balanced
  panel ending at the target's last observation: conditioning columns whose last observation
  is earlier than the target's are dropped for that origin (no values are invented at the
  ragged edge), interior gaps are carried forward, and only the BVAR and the factor model use
  observations published after the target's last value. Transforms and aggregations per
  conditioning series are fixed in `configs/default.yaml`. The realised variable lists per
  target (`multivariate_vars` for the BVAR, `balanced_fm_vars` for the foundation models; the
  factor model takes the first 12 monthly series in config order plus the quarterly block)
  are written to `panels.json` next to each run.
- Workers refuse to start when the system has less than 4 GB of commit charge available
  (`min_free_commit_mb`), because weight loading then fails unpredictably on Windows.

## Benchmarks (same interface, main environment)

- **naive**: historical mean of the transformed series with Gaussian quantiles.
- **ar**: direct multi-step AR(p), p by BIC on the one-step regression, p at most 12 (monthly)
  or 4 (quarterly); Gaussian quantiles from the residual standard error per horizon.
- **bvar**: Minnesota normal-inverse-Wishart prior with sum-of-coefficients and dummy-initial-
  observation priors via dummy observations; (lambda, mu, delta) chosen on a fixed grid by
  marginal likelihood at each origin; lags 6 (monthly) or 2 (quarterly); up to 12 variables
  (estimation on the balanced part of the panel, at least 72 months or 32 quarters, dropping the
  gappiest conditioning columns only if that minimum is not met); ragged-edge periods simulated
  conditionally on the variables already observed (shock conditioning); posterior-predictive
  quantiles from 500 seeded draws; step 1 always refers to the first period after the target's
  last observation. Limiting cases tested (tight prior shrinks lags to zero, loose prior
  reproduces OLS).
- **dfm**: statsmodels `DynamicFactorMQ`, 2 factors, factor order 2, idiosyncratic AR(1), EM with
  at most 100 iterations, the first 12 monthly conditioning variables (config order; the Kalman
  filter handles missing values) plus the whole quarterly block; predictions for the periods
  after the target's last observation use the smoothed information set (indicators observed
  after the target count); Gaussian quantiles from the prediction standard errors.
- **combo_bench**, **combo_fm**: equal-weight averages of quantiles.

## Smoke test and runtime

See `data/smoke/smoke_<origin>.csv` (git-ignored) and the runtime table below, generated by
`ffcast smoke --origin 2024-06-25`.

<!-- RUNTIME TABLE START -->
Origin 2024-06-25, 11 targets (Canadian core CPI blocked), Windows 11, 24 cores, 4 threads per worker; three-stage run (`ffcast smoke`, 2026-11-18, data built under the `conservative` OECD rule). Runtimes are per task (one target, all horizons); worker wall time includes process start and weight loading, once per origin and model.

| model | variant | tasks | mean s/task | max s/task | worker wall s | checks |
| --- | --- | --- | --- | --- | --- | --- |
| naive | uni | 11 | 0.056 | 0.617 | - | all sane, step 1 aligned |
| ar | uni | 11 | 0.010 | 0.025 | - | all sane, step 1 aligned |
| bvar | multi | 11 | 0.499 | 0.690 | - | all sane, step 1 aligned |
| dfm | multi | 11 | 6.295 | 12.820 | - | all sane, step 1 aligned |
| combo_bench | multi | 11 | 0.000 | 0.000 | - | all sane, step 1 aligned |
| chronos2 | multi | 9 | 0.130 | 0.197 | 9.47 | all sane, step 1 aligned |
| chronos2 | univa | 11 | 0.058 | 0.073 | (same worker) | all sane, step 1 aligned |
| timesfm25 | univa | 11 | 0.187 | 0.205 | 7.92 | all sane, step 1 aligned |
| tirex | univa | 11 | 0.435 | 0.455 | 11.04 | all sane, step 1 aligned |
| tirex2 | multi | 9 | 0.479 | 0.699 | 12.97 | all sane, step 1 aligned |
| tirex2 | univa | 11 | 0.141 | 0.148 | (same worker) | all sane, step 1 aligned |
| moirai2 | univa | 11 | 0.017 | 0.022 | 6.41 | all sane, step 1 aligned |

Sane-magnitude and step-1 alignment checks: 128 passed, 0 failed (the only failing row is the blocked Canadian core CPI target). Every model's step-1 forecast refers to the same target period for every target (for the foundation models this holds by construction, since the period comes from the shared panel; for the benchmarks it is read from each model's own output). Note: the multivariate task count is lower than in the same-month run because at this origin OECD edition 202405 is missing, so the Canadian unemployment panel keeps 4 instead of 6 conditioning variables. An earlier version of this table (commit 332625a) reported only the last model per variant because the smoke metadata was keyed without the model name; fixed and covered by `tests/test_smoke.py`.

Projected backtest cost per origin (11 targets, two input modes): benchmarks about 4 minutes (dominated by the factor model), foundation models about 1 minute including worker start-up; about 130 monthly origins in the primary window.
<!-- RUNTIME TABLE END -->
