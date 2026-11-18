# Model cards

Per model: pinned weights, licence, release date, training-data statement, inference settings
and runtime. Pins are what `ffcast.models.weights.ensure_weights` downloads and verifies by
SHA-256 of every file; the whole-snapshot digest is written into every forecast's metadata.
Inference settings are frozen in `configs/default.yaml` (`models.settings`) and described in
`workers/_protocol.md`. All models run zero-shot on CPU, one worker process per model
environment (`envs/<env>/uv.lock`), seed 0, 4 threads, deterministic algorithms where
PyTorch supports them; a rerun of the same request produces byte-identical output (checked for
every model on a synthetic task on 2026-11-18).

| Model | Hugging Face ID | Revision (sha) | Weight file date | Release date (HF repo created) | Licence | Package (locked) | Variants |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Chronos-2 | `amazon/chronos-2` | `29ec3766d36d6f73f0696f85560a422f50e8498c` | 2025-10-30 | 2025-10-30 | Apache-2.0 | `chronos-forecasting` 2.3.2, torch 2.15.0+cpu, transformers 5.23.0 | univariate, multivariate (joint forecast of target and conditioning variates) |
| TimesFM 2.5 | `google/timesfm-2.5-200m-pytorch` | `1d952420fba87f3c6dee4f240de0f1a0fbc790e3` | 2025-10-01 (refreshed weights) | 2025-09-02 | Apache-2.0 | `timesfm` 3.0.2, torch 2.15.0+cpu | univariate |
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
- TiRex-2 and TiRex run with `torch.compile` disabled (no MSVC on Windows).
- Multivariate variants receive the target plus the conditioning variables selected by the
  rule in `ffcast.models.panel.Panel.multivariate` (coverage at least 80% of the last 240
  months or 80 quarters, not more than 12 periods stale, at most 12 variables), forward-filled
  at the ragged edge, and return the target's quantiles.
- Workers refuse to start when the system has less than 4 GB of commit charge available
  (`min_free_commit_mb`), because weight loading then fails unpredictably on Windows.

## Benchmarks (same interface, main environment)

- **naive**: historical mean of the transformed series with Gaussian quantiles.
- **ar**: direct multi-step AR(p), p by BIC on the one-step regression, p at most 12 (monthly)
  or 4 (quarterly); Gaussian quantiles from the residual standard error per horizon.
- **bvar**: Minnesota normal-inverse-Wishart prior with sum-of-coefficients and dummy-initial-
  observation priors via dummy observations; (lambda, mu, delta) chosen on a fixed grid by
  marginal likelihood at each origin; lags 6 (monthly) or 2 (quarterly); up to 12 variables;
  ragged edge completed by the VAR's own conditional forecast; posterior-predictive quantiles
  from 500 seeded draws. Limiting cases tested (tight prior shrinks lags to zero, loose prior
  reproduces OLS).
- **dfm**: statsmodels `DynamicFactorMQ`, 2 factors, factor order 2, idiosyncratic AR(1), EM with
  at most 100 iterations, up to 12 monthly variables plus the quarterly block; Gaussian
  quantiles from the forecast standard errors.
- **combo_bench**, **combo_fm**: equal-weight averages of quantiles.

## Smoke test and runtime

See `data/smoke/smoke_<origin>.csv` (git-ignored) and the runtime table below, generated by
`ffcast smoke --origin 2024-06-25`.

<!-- RUNTIME TABLE START -->
(pending)
<!-- RUNTIME TABLE END -->
