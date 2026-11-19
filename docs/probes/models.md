# Phase 0 probe: foundation models

Probed 2026-11-17 on Windows 11, Python 3.12.13 (uv), CPU-only torch. Each model was
installed in its own virtualenv and run on a 120-point synthetic monthly series,
12-step horizon. Toy outputs were sane (quantile paths tracking the sine component).

## Planned models

| Model | HF ID | Revision (sha) | Licence | Weights | Created on HF | Package / torch | Load / predict (CPU) | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chronos-2 | `amazon/chronos-2` | `29ec3766d36d6f73f0696f85560a422f50e8498c` | Apache-2.0 | 478 MB safetensors | 2025-10-30 (last modified 2026-06-05) | `chronos-forecasting` 2.3.2, torch 2.15.0+cpu, transformers 5.23 | 4.4 s / 0.07 s | confirmed |
| TimesFM 2.5 | `google/timesfm-2.5-200m-pytorch` | `1d952420fba87f3c6dee4f240de0f1a0fbc790e3` | Apache-2.0 | 925 MB safetensors | 2025-09-02 | `timesfm` 3.0.2 (class `TimesFM_2p5_200M_torch`), torch 2.15.0+cpu | 29 s / 0.23 s | confirmed |
| TiRex | `NX-AI/TiRex` | `43ebaaff068c1390785c387b3e5178df3f4c92ca` | NXAI Community License (Llama-3-style; free for research; commercial licence needed only for >EUR 100m revenue entities embedding it in a product; attribution "Built with technology from NXAI" required when distributing) | 141 MB ckpt (+142 MB onnx) | 2025-05-26 (last modified 2026-11-13) | `git+https://github.com/NX-AI/tirex` (the PyPI package named `tirex` is an unrelated dimensionality-reduction library), torch 2.15.0+cpu, CPU via `TIREX_NO_CUDA=1` | 6.1 s / 0.5 s | changed: licence is not OSI; install source differs |
| Moirai 2.0 | `Salesforce/moirai-2.0-R-small` | `30f43ff08c8494f4943ae1521e9d4e94a0fbb389` | CC-BY-NC-4.0 (non-commercial) | 46 MB safetensors | 2025-08-06 | `uni2ts` 2.0.0, which pins torch<2.5 (got 2.4.1+cpu), numpy~=1.26, gluonts 0.14 | 19 s / 0.06 s | confirmed, but non-commercial licence flagged |

Notes
- `lastModified` for Chronos-2 and TiRex is later than creation; files may have been
  updated since release. The pinned sha above is what was probed.
- Moirai's `uni2ts` cannot share an environment with the other three (torch 2.4 vs 2.15,
  numpy 1.26 vs 2.x). One environment per model behind the common interface is required,
  as the plan anticipated.
- Default quantile outputs: Chronos-2 arbitrary levels; TimesFM 10 (mean + 0.1..0.9);
  TiRex 9 (0.1..0.9); Moirai sample-based via gluonts (any level).
- Chronos-2 is the only planned model with native multivariate/covariate input.

## Newer weights found (not in plan)

| Model | HF ID | Revision | Licence | Created | Note |
| --- | --- | --- | --- | --- | --- |
| TiRex-2 | `NX-AI/TiRex-2` | `352636173653592b6dceb3fbeee9224ca97952a9` | Apache-2.0 | 2026-06-16 | Multivariate with past/future covariates; 38M (+44M multivariate) params; package `tirex-2` (installed from GitHub). Runs on CPU; on Windows `torch.compile` must be disabled (`TORCH_COMPILE_DISABLE=1` or `load_model(..., compile=False)`) because no MSVC `cl` is present. Load 0.7 s, predict 0.27 s for 2 targets. Candidate to ADD: it is the only second multivariate model and its licence is more permissive than TiRex-1. Decontaminated variants exist (`TiRex-2-gifteval-zs`, `TiRex-2-fevbench`). |
| TimesFM 3.0 | `google/timesfm-3.0-pytorch` | `43046b85ec22d584a13f8098c2ed39c889e129c2` | "timesfm-non-commercial-license-v1.0" | 2026-08-24 | Non-commercial. Per plan rule, NOT used unless owner asks. **Owner asked 2026-11-19 (licence reviewed, use is non-commercial): added as `timesfm3`, see `docs/model_cards.md`.** |
| Chronos-2 small / synth | `autogluon/chronos-2-small`, `autogluon/chronos-2-synth` | - | Apache-2.0 | 2025-11/12 | Ablation checkpoints; not needed. |

## Training data and cutoffs (best available statements)

No model publishes a calendar cutoff for its real-data corpus. What is documented:

- **Chronos-2** (arXiv 2510.15821, Table 6): 23 real univariate datasets from the Chronos
  and GIFT-Eval pretraining corpora (energy, transport, weather, cloud ops, M4 daily/hourly/
  weekly/monthly, Wiki). Multivariate ability trained entirely on synthetic data. FRED-MD is
  NOT listed as pretraining data, although `monash_fred_md` exists in the public
  `autogluon/chronos_datasets` collection. Macro exposure: M4 monthly (which contains
  macro/finance series ending by 2017-2018).
- **TimesFM 2.5** (model card): GiftEvalPretrain, Wikimedia pageviews (cutoff Nov 2023),
  Google Trends (cutoff end-2022). Only model with explicit (partial) cutoffs.
- **TiRex** (arXiv 2505.23719, Tables 5-6): Chronos training datasets incl. M4 daily/hourly/
  monthly/weekly, GiftEvalPretrain subset, synthetic GP data. No FRED-MD, M3, CIF. No dates.
- **Moirai 2.0** (arXiv 2511.11698): GIFT-Eval Pretrain, GIFT-Eval train splits,
  Chronos-Mixup (non-leaking subset), KernelSynth, internal Salesforce CloudOps data
  covering about Jan 2024 to Jan 2025. No FRED-MD or M3 mentioned.
- **TiRex-2** (model card): LOTSA (`Salesforce/lotsa_data`), which DOES contain `fred_md`,
  M4 monthly/quarterly, M3, CIF 2016 and tourism. Macro exposure is therefore highest for
  TiRex-2. Needs confirmation from its documentation in Phase 3.

Implication for Q2: with no stated cutoffs, the pre/post split must use model release
dates (HF creation dates above) as the conservative boundary, with the TimesFM data
cutoffs as a secondary variant. Record this in the pre-registration.

## Environment conclusions

- Windows + CPU works for all five models. No WSL needed so far.
- `uv pip install` of several venvs in parallel hit a hardlink race on this machine;
  use `--link-mode=copy` or install sequentially.
- Toy scripts are in the session scratchpad; the production wrappers will be written in
  Phase 3 with these call signatures as the starting point.
