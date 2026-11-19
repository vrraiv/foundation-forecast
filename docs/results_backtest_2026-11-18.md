# Backtest results, first full run (2026-11-18): public copy of the Gate 4 summary

Verbatim copy of `data/backtest/tables/SUMMARY.md` as generated on 2026-11-19T03:08 UTC by
`ffcast.eval.summary` from the scored tables of the first full backtest (310 origins, 2001-01 to
2026-10, both input modes, every model). SHA-256 of the file as stored (bytes): `cd9ad7875bc1dc98cd6e22fa76188be678393010ba1aec47d47970361cbedcef`. Disclosure of
everything in the summary was approved by the owner on 2026-11-18 after HUMAN GATE 4, which was a
plausibility check only: the owner reviewed the tables, asked for three cells to be decomposed, and
made no design change. The underlying forecasts and the CSV tables stay private under `data/`.

Reading notes established at Gate 4 (facts about the tables, not interpretation of the models):

- Full-sample statistics at horizon 1 for the activity targets are dominated by 2020. For
  Canadian retail at horizon 1 the AR's squared error comes 95% from target periods in
  2020-01..2021-06; for Canadian consumption 97%. The multivariate benchmarks (BVAR, DFM) are far
  better than the AR there because step 1 refers to a period for which monthly indicators were
  already published at the origin (retail is released about two months after the reference month).
  Outside the COVID window they are at or above the AR. The `ex_covid` columns are the informative
  ones for those cells.
- Quarterly targets have three monthly origins per quarter, so their `n` is about three times the
  number of quarters and the Diebold-Mariano statistics (HAC lag from the horizon) overstate
  significance at short horizons.
- The pre/post weights-date split has 1 to 14 post-date observations per cell; the TiRex-2
  post-date figures rest on a single observation.
- The model confidence set keeps nearly every model in nearly every cell (the AR in 89% of the
  headline cells): low power rather than parity.
- In the fixed-event (Q4) table the `univariate_levels` rows are uninformative: those variants have
  step-1 rows only, the two forecasts of a sequence are usually identical, and where they are not
  the revision variance is near zero, so slopes and standard errors are either NaN or enormous with
  t-ratios near zero. The negative slopes of the stationary variants hold for every model including
  the AR.
- The DFM has 190 cells with status `error` (3.3% of its cells): 180 are the first year of each Bank
  of Canada conditioning series (10-year yield from 2001, overnight target from 2009, USD/CAD from
  2017), 10 are an untraced empty euro-area panel at the 2021-09 and 2021-10 origins. The
  validity guard removed 11 multivariate BVAR cells at the 2020-08..11 origins. Both are recorded
  in `docs/backtest.md` (Deviations 2, 3 and 6) with the owner's decisions to leave the rules as
  configured.
- The "revised vintage date 2026-12-02" in the bookkeeping is the newest vintage plus one day; the
  November 2026 OECD edition is dated 2026-12-01 under the conservative edition rule. No origin can
  see it.

---

# Backtest results summary (private, HUMAN GATE 4)

Generated 2026-11-19T03:15:50+00:00 from the CSVs in `C:\projects\foundation-forecast\data\backtest\tables` and the run bookkeeping under `C:\projects\foundation-forecast\data\backtest`. Tables only; no interpretation. Forecast-derived: stays under `data/` and is not published.

Horizons (steps after the target's last in-vintage observation): M: [1, 3, 6, 12], Q: [1, 2, 4]. Primary window from 2015-01-25; extension from 2001-01-25. Foundation-model weights dates and stated training cutoffs:

| model | weights_date | training_cutoff |
|---|---|---|
| chronos2 | 2025-10-30 |  |
| timesfm25 | 2025-10-01 | 2023-11 |
| tirex | 2025-05-26 |  |
| tirex2 | 2026-10-06 |  |
| moirai2 | 2025-08-06 | 2025-01 |

## 1. Run bookkeeping

| item | value |
|---|---|
| first written (UTC) | 2026-11-18T12:42:20+00:00 |
| last written (UTC) | 2026-11-18T23:59:06+00:00 |
| config sha256 at first run | 6deba43a701f7c4d5cedc0e0843a42fa39a0d3adf1b62321e1485398594c00ad |
| config sha256 now | fe0f186593d69263d7bdfd802675d7ab5f6485b9376fb535531ce746c9545a73 |
| config changed since first run | yes |
| config-change note | 2026-11-18: core CPI (CPI-XFET) added after launch (owner approval); DFM em_initialization=false and validity guard after the DFM numerical breakdown (docs/backtest.md, Deviations); benchmarks recomputed under BENCH_CODE_VERSION 2 |
| data manifest sha256 | 6872f15906e208d9622a011962b762c61dfa130c6c7123f2c3bd0b765d393274 |
| series in data manifest | 76 |
| revised vintage date (`revised` mode) | 2026-12-02 |
| last stage-3 workdir | C:\projects\foundation-forecast\data\backtest\work\20261118T181144 |

Weights digests used by the foundation-model stage:

| model | weights digest |
|---|---|
| chronos2 | d71ef15c17e03df7c4b2937e33766c2d6949e2891df54ec08dce362fdaccea2a |
| moirai2 | bd398c136b69f9c86aaa49045f5eef9b331a790df47a0b90560803b35da7b2f8 |
| timesfm25 | ee8dbe310024bc0a785b423f123982839fcce0e28abf3634b9726a78955a1bf7 |
| tirex | b8f6e81ce66a5fdd4bf2ec4d8b58b1a42edceeb04a0ca022f1dac389ec84906c |
| tirex2 | fe17a7e73a2393f0c16561ccb620b12fa3258eefcccfe20ccb38df4c55319f16 |

### Verify (`ffcast backtest --verify N`)

Latest: `verify_20261118T191840.json`; origins recomputed: 2; mismatching origins: 0.

## 2. Coverage

Origins with stored rows: 310 (2001-01-25 to 2026-10-26). Meta rows: 111328.

### Status by model, variant and input mode

| model | variant | input_mode | error | ok | skipped |
|---|---|---|---|---|---|
| - | - | realtime | 0 | 0 | 684 |
| - | - | revised | 0 | 0 | 2724 |
| ar | univariate | realtime | 0 | 3378 | 0 |
| ar | univariate | revised | 0 | 2358 | 0 |
| bvar | multivariate | realtime | 9 | 3369 | 0 |
| bvar | multivariate | revised | 2 | 2356 | 0 |
| chronos2 | multivariate | realtime | 0 | 3225 | 0 |
| chronos2 | multivariate | revised | 0 | 2245 | 0 |
| chronos2 | multivariate_levels | realtime | 0 | 3225 | 0 |
| chronos2 | multivariate_levels | revised | 0 | 2245 | 0 |
| chronos2 | univariate | realtime | 0 | 3378 | 0 |
| chronos2 | univariate | revised | 0 | 2358 | 0 |
| chronos2 | univariate_levels | realtime | 0 | 3378 | 0 |
| chronos2 | univariate_levels | revised | 0 | 2358 | 0 |
| combo_bench | multivariate | realtime | 126 | 3252 | 0 |
| combo_bench | multivariate | revised | 75 | 2283 | 0 |
| dfm | multivariate | realtime | 117 | 3261 | 0 |
| dfm | multivariate | revised | 73 | 2285 | 0 |
| moirai2 | univariate | realtime | 0 | 3378 | 0 |
| moirai2 | univariate | revised | 0 | 2358 | 0 |
| moirai2 | univariate_levels | realtime | 0 | 3378 | 0 |
| moirai2 | univariate_levels | revised | 0 | 2358 | 0 |
| naive | univariate | realtime | 0 | 3378 | 0 |
| naive | univariate | revised | 0 | 2358 | 0 |
| timesfm25 | univariate | realtime | 0 | 3378 | 0 |
| timesfm25 | univariate | revised | 0 | 2358 | 0 |
| timesfm25 | univariate_levels | realtime | 0 | 3378 | 0 |
| timesfm25 | univariate_levels | revised | 0 | 2358 | 0 |
| tirex | univariate | realtime | 0 | 3378 | 0 |
| tirex | univariate | revised | 0 | 2358 | 0 |
| tirex | univariate_levels | realtime | 0 | 3378 | 0 |
| tirex | univariate_levels | revised | 0 | 2358 | 0 |
| tirex2 | multivariate | realtime | 0 | 3225 | 0 |
| tirex2 | multivariate | revised | 0 | 2245 | 0 |
| tirex2 | multivariate_levels | realtime | 0 | 3225 | 0 |
| tirex2 | multivariate_levels | revised | 0 | 2245 | 0 |
| tirex2 | univariate | realtime | 0 | 3378 | 0 |
| tirex2 | univariate | revised | 0 | 2358 | 0 |
| tirex2 | univariate_levels | realtime | 0 | 3378 | 0 |
| tirex2 | univariate_levels | revised | 0 | 2358 | 0 |

### Status by economy and target (all models)

| econ | target | error | ok | skipped |
|---|---|---|---|---|
| CA | consumption | 64 | 9672 | 168 |
| CA | cpi | 38 | 4902 | 720 |
| CA | cpi_core | 44 | 5846 | 620 |
| CA | gdp | 60 | 9676 | 168 |
| CA | retail | 82 | 11508 | 20 |
| CA | unemp | 88 | 11692 | 0 |
| EA | consumption | 6 | 10501 | 134 |
| EA | gdp | 0 | 10499 | 134 |
| EA | hicp | 8 | 10594 | 124 |
| EA | hicp_core | 4 | 3674 | 836 |
| EA | retail | 8 | 9834 | 204 |
| EA | unemp | 0 | 9120 | 280 |

### Skip and error reasons

| status | reason | rows |
|---|---|---|
| skipped | exclude_from_qN: pseudo-vintage target has no revised mode | 1860 |
| skipped | in-vintage history N < N | 1148 |
| skipped | no resolvable vintage at origin | 400 |
| error | missing member: dfm | 190 |
| error | Constant variable(s) found in observed variables, but constants cannot | 104 |
| error | data contains non-finite values (inf, NaN). You should drop these valu | 76 |
| error | missing member: bvar | 11 |
| error | zero-size array to reduction operation maximum which has no identity | 10 |
| error | numerical failure: |forecast| N exceeds N x history sd N.N | 8 |
| error | numerical failure: |forecast| N.N exceeds N x history sd N.N | 2 |
| error | numerical failure: |forecast| N.Ne+N exceeds N x history sd N.N | 1 |

### Runtime (seconds per task, ok rows)

| model | count | median | mean | max |
|---|---|---|---|---|
| ar | 5736 | 0.009 | 0.012 | 0.134 |
| bvar | 5725 | 0.688 | 0.585 | 1.762 |
| chronos2 | 22412 | 0.060 | 0.078 | 0.311 |
| combo_bench | 5535 | 0 | 0 | 0 |
| dfm | 5546 | 7.116 | 7.882 | 21.421 |
| moirai2 | 11472 | 0.013 | 0.013 | 0.080 |
| naive | 5736 | 0.001 | 0.002 | 3.214 |
| timesfm25 | 11472 | 0.183 | 0.184 | 0.266 |
| tirex | 11472 | 0.534 | 0.529 | 0.648 |
| tirex2 | 22412 | 0.214 | 0.369 | 1.306 |

## 3. Outturns

| econ | target | periods | first_release_available | late | revised_12m_available | lag_limit_days | median_lag_days |
|---|---|---|---|---|---|---|---|
| CA | consumption | 110 | 106 | 0 | 106 | 191 | 62.500 |
| CA | cpi | 271 | 260 | 0 | 260 | 69 | 24 |
| CA | cpi_core | 321 | 310 | 0 | 310 | 69 | 24 |
| CA | gdp | 110 | 106 | 0 | 106 | 191 | 62.500 |
| CA | retail | 321 | 308 | 3 | 311 | 153 | 93 |
| CA | unemp | 321 | 311 | 0 | 311 | 122 | 62 |
| EA | consumption | 113 | 108 | 0 | 108 | 153 | 69 |
| EA | gdp | 109 | 104 | 0 | 104 | 152 | 66 |
| EA | hicp | 321 | 310 | 0 | 308 | 132 | 32 |
| EA | hicp_core | 213 | 202 | 0 | 202 | 69 | 24 |
| EA | retail | 270 | 259 | 1 | 260 | 136.500 | 63 |
| EA | unemp | 329 | 305 | 12 | 315 | 122 | 40 |

Late first releases are kept in the table but excluded from first-release scoring (`docs/backtest.md`, Outturns).

## 4. Headline tables

Slice: input_mode = `realtime`, outturn = `first_release`, sample = `full`, window = `primary`, split = `all`, variants `univariate`, `multivariate`, configured horizons. Relative RMSFE and MAE are ratios to the direct AR of the same cell (below 1 means a smaller error than AR; no ranking implied). `dm_p` is the two-sided HLN-corrected Diebold-Mariano p-value against AR on squared errors. `in_mcs90` is membership of the 90% model confidence set over models with complete common origins in the cell.

### CA / consumption


**Scored forecasts (n)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 140 | 137 | 131 |
| bvar / multivariate | 138 | 135 | 129 |
| chronos2 / multivariate | 94 | 92 | 88 |
| chronos2 / univariate | 140 | 137 | 131 |
| combo_bench / multivariate | 135 | 132 | 126 |
| combo_fm / univariate | 140 | 137 | 131 |
| dfm / multivariate | 137 | 134 | 128 |
| moirai2 / univariate | 140 | 137 | 131 |
| naive / univariate | 140 | 137 | 131 |
| timesfm25 / univariate | 140 | 137 | 131 |
| tirex / univariate | 140 | 137 | 131 |
| tirex2 / multivariate | 94 | 92 | 88 |
| tirex2 / univariate | 140 | 137 | 131 |

**Relative RMSFE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 1.049 | 1.150 | 1.239 |
| chronos2 / multivariate | 1.138 | 1.045 | 1.009 |
| chronos2 / univariate | 1.323 | 1.208 | 1.118 |
| combo_bench / multivariate | 0.862 | 1.010 | 1.014 |
| combo_fm / univariate | 1.016 | 1.010 | 1.007 |
| dfm / multivariate | 0.569 | 0.967 | 1.001 |
| moirai2 / univariate | 1.036 | 1.002 | 1.005 |
| naive / univariate | 0.815 | 0.981 | 1.004 |
| timesfm25 / univariate | 0.961 | 1.000 | 1.000 |
| tirex / univariate | 0.959 | 0.983 | 1.001 |
| tirex2 / multivariate | 0.934 | 0.993 | 1.000 |
| tirex2 / univariate | 0.846 | 0.987 | 0.994 |

**Relative MAE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 1.119 | 1.149 | 1.113 |
| chronos2 / multivariate | 1.049 | 1.066 | 1.028 |
| chronos2 / univariate | 1.171 | 1.224 | 1.183 |
| combo_bench / multivariate | 0.929 | 1.045 | 0.999 |
| combo_fm / univariate | 1.010 | 1.041 | 1.036 |
| dfm / multivariate | 0.735 | 0.997 | 0.978 |
| moirai2 / univariate | 1.048 | 1.033 | 1.028 |
| naive / univariate | 0.879 | 0.974 | 0.996 |
| timesfm25 / univariate | 0.997 | 1.036 | 1.017 |
| tirex / univariate | 1.038 | 0.979 | 1.005 |
| tirex2 / multivariate | 0.904 | 0.986 | 0.988 |
| tirex2 / univariate | 0.841 | 0.946 | 0.957 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.660 | 0.271 | 0.337 |
| chronos2 / multivariate | 0.188 | 0.364 | 0.561 |
| chronos2 / univariate | 0.096 | 0.182 | 0.269 |
| combo_bench / multivariate | 0.089 | 0.572 | 0.432 |
| combo_fm / univariate | 0.355 | 0.424 | 0.534 |
| dfm / multivariate | 0.025 | 0.115 | 0.817 |
| moirai2 / univariate | 0.108 | 0.806 | 0.667 |
| naive / univariate | 0.091 | 0.221 | 0.588 |
| timesfm25 / univariate | 0.046 | 0.961 | 0.998 |
| tirex / univariate | 0.145 | 0.058 | 0.906 |
| tirex2 / multivariate | 0.035 | 0.164 | 0.984 |
| tirex2 / univariate | 0.043 | 0.093 | 0.497 |

**RMSFE (transformed units)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 3.518 | 2.952 | 2.946 |
| bvar / multivariate | 2.926 | 3.399 | 3.674 |
| chronos2 / multivariate | 4.000 | 3.076 | 2.973 |
| chronos2 / univariate | 4.653 | 3.567 | 3.295 |
| combo_bench / multivariate | 2.432 | 3.019 | 3.041 |
| combo_fm / univariate | 3.573 | 2.982 | 2.967 |
| dfm / multivariate | 2.023 | 2.886 | 2.984 |
| moirai2 / univariate | 3.647 | 2.959 | 2.959 |
| naive / univariate | 2.868 | 2.895 | 2.958 |
| timesfm25 / univariate | 3.381 | 2.953 | 2.946 |
| tirex / univariate | 3.375 | 2.903 | 2.948 |
| tirex2 / multivariate | 3.284 | 2.923 | 2.946 |
| tirex2 / univariate | 2.977 | 2.913 | 2.929 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | -0.024 | -0.131 | -0.230 |
| bvar / multivariate | -0.365 | -0.257 | -0.339 |
| chronos2 / multivariate | 0.067 | 0.025 | -0.033 |
| chronos2 / univariate | 0.147 | 0.119 | 0.053 |
| combo_bench / multivariate | -0.350 | -0.249 | -0.285 |
| combo_fm / univariate | -0.030 | -0.068 | -0.099 |
| dfm / multivariate | -0.278 | -0.291 | -0.253 |
| moirai2 / univariate | -0.072 | -0.108 | -0.135 |
| naive / univariate | -0.259 | -0.255 | -0.250 |
| timesfm25 / univariate | -0.078 | -0.102 | -0.146 |
| tirex / univariate | -0.125 | -0.164 | -0.161 |
| tirex2 / multivariate | -0.003 | -0.105 | -0.097 |
| tirex2 / univariate | -0.022 | -0.086 | -0.105 |

**Weighted quantile loss**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 1.154 | 1.061 | 1.045 |
| bvar / multivariate | 1.055 | 1.249 | 1.242 |
| chronos2 / multivariate | 1.159 | 1.093 | 1.078 |
| chronos2 / univariate | 1.198 | 1.164 | 1.170 |
| combo_bench / multivariate | 0.864 | 1.106 | 1.101 |
| combo_fm / univariate | 1.085 | 1.044 | 1.048 |
| dfm / multivariate | 0.808 | 1.035 | 1.059 |
| moirai2 / univariate | 1.116 | 1.030 | 1.045 |
| naive / univariate | 1.010 | 1.031 | 1.059 |
| timesfm25 / univariate | 1.090 | 1.037 | 1.027 |
| tirex / univariate | 1.121 | 1.055 | 1.078 |
| tirex2 / multivariate | 1.036 | 1.030 | 1.036 |
| tirex2 / univariate | 0.976 | 1.000 | 0.991 |

**80% interval coverage**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 0.871 | 0.876 | 0.908 |
| bvar / multivariate | 0.877 | 0.874 | 0.876 |
| chronos2 / multivariate | 0.745 | 0.739 | 0.773 |
| chronos2 / univariate | 0.679 | 0.679 | 0.679 |
| combo_bench / multivariate | 0.919 | 0.902 | 0.913 |
| combo_fm / univariate | 0.743 | 0.788 | 0.771 |
| dfm / multivariate | 0.883 | 0.903 | 0.906 |
| moirai2 / univariate | 0.786 | 0.781 | 0.771 |
| naive / univariate | 0.914 | 0.912 | 0.908 |
| timesfm25 / univariate | 0.786 | 0.803 | 0.817 |
| tirex / univariate | 0.764 | 0.810 | 0.748 |
| tirex2 / multivariate | 0.702 | 0.717 | 0.761 |
| tirex2 / univariate | 0.721 | 0.788 | 0.725 |

**Model confidence set (90%) membership**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | yes | yes | yes |
| bvar / multivariate | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |
| chronos2 / univariate | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |
| combo_bench / multivariate | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes |
| dfm / multivariate | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes |
| moirai2 / univariate_levels | yes |  |  |
| naive / univariate | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |
| tirex / univariate | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |
| tirex2 / multivariate | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |
| tirex2 / univariate | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |

### CA / cpi


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 142 | 140 | 137 | 131 |
| bvar / multivariate | 141 | 139 | 136 | 130 |
| chronos2 / multivariate | 142 | 140 | 137 | 131 |
| chronos2 / univariate | 142 | 140 | 137 | 131 |
| combo_bench / multivariate | 138 | 136 | 133 | 127 |
| combo_fm / univariate | 142 | 140 | 137 | 131 |
| dfm / multivariate | 139 | 137 | 134 | 128 |
| moirai2 / univariate | 142 | 140 | 137 | 131 |
| naive / univariate | 142 | 140 | 137 | 131 |
| timesfm25 / univariate | 142 | 140 | 137 | 131 |
| tirex / univariate | 142 | 140 | 137 | 131 |
| tirex2 / multivariate | 142 | 140 | 137 | 131 |
| tirex2 / univariate | 142 | 140 | 137 | 131 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.976 | 1.003 | 1.014 | 1.107 |
| chronos2 / multivariate | 0.844 | 0.846 | 0.895 | 0.917 |
| chronos2 / univariate | 0.862 | 0.822 | 0.862 | 0.891 |
| combo_bench / multivariate | 0.975 | 1.000 | 1.007 | 1.060 |
| combo_fm / univariate | 0.856 | 0.818 | 0.851 | 0.874 |
| dfm / multivariate | 0.988 | 1.001 | 1.011 | 1.103 |
| moirai2 / univariate | 0.863 | 0.840 | 0.870 | 0.892 |
| naive / univariate | 1.012 | 0.998 | 1.010 | 1.104 |
| timesfm25 / univariate | 0.878 | 0.814 | 0.846 | 0.874 |
| tirex / univariate | 0.886 | 0.829 | 0.852 | 0.884 |
| tirex2 / multivariate | 0.856 | 0.843 | 0.883 | 0.902 |
| tirex2 / univariate | 0.854 | 0.831 | 0.872 | 0.888 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.963 | 1.001 | 1.021 | 1.152 |
| chronos2 / multivariate | 0.823 | 0.815 | 0.863 | 0.881 |
| chronos2 / univariate | 0.846 | 0.782 | 0.836 | 0.862 |
| combo_bench / multivariate | 0.976 | 0.997 | 1.013 | 1.096 |
| combo_fm / univariate | 0.851 | 0.788 | 0.827 | 0.847 |
| dfm / multivariate | 1.002 | 0.999 | 1.023 | 1.155 |
| moirai2 / univariate | 0.865 | 0.808 | 0.843 | 0.861 |
| naive / univariate | 1.027 | 0.995 | 1.019 | 1.154 |
| timesfm25 / univariate | 0.858 | 0.782 | 0.826 | 0.846 |
| tirex / univariate | 0.886 | 0.789 | 0.815 | 0.865 |
| tirex2 / multivariate | 0.841 | 0.808 | 0.857 | 0.884 |
| tirex2 / univariate | 0.841 | 0.806 | 0.852 | 0.870 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.445 | 0.712 | 0.043 | 0.004 |
| chronos2 / multivariate | 0.000 | 0.030 | 0.101 | 0.014 |
| chronos2 / univariate | 0.000 | 0.005 | 0.010 | 0.008 |
| combo_bench / multivariate | 0.113 | 0.967 | 0.137 | 0.018 |
| combo_fm / univariate | 0.000 | 0.001 | 0.004 | 0.001 |
| dfm / multivariate | 0.369 | 0.850 | 0.160 | 0.006 |
| moirai2 / univariate | 0.001 | 0.002 | 0.007 | 0.006 |
| naive / univariate | 0.554 | 0.571 | 0.216 | 0.003 |
| timesfm25 / univariate | 0.000 | 0.000 | 0.004 | 0.000 |
| tirex / univariate | 0.001 | 0.005 | 0.005 | 0.010 |
| tirex2 / multivariate | 0.000 | 0.001 | 0.007 | 0.003 |
| tirex2 / univariate | 0.000 | 0.003 | 0.010 | 0.002 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.377 | 0.410 | 0.387 | 0.363 |
| bvar / multivariate | 0.368 | 0.412 | 0.392 | 0.400 |
| chronos2 / multivariate | 0.318 | 0.347 | 0.346 | 0.333 |
| chronos2 / univariate | 0.325 | 0.337 | 0.333 | 0.324 |
| combo_bench / multivariate | 0.361 | 0.415 | 0.392 | 0.381 |
| combo_fm / univariate | 0.323 | 0.336 | 0.329 | 0.318 |
| dfm / multivariate | 0.365 | 0.415 | 0.394 | 0.398 |
| moirai2 / univariate | 0.326 | 0.345 | 0.337 | 0.324 |
| naive / univariate | 0.382 | 0.409 | 0.391 | 0.401 |
| timesfm25 / univariate | 0.331 | 0.334 | 0.327 | 0.317 |
| tirex / univariate | 0.334 | 0.340 | 0.330 | 0.321 |
| tirex2 / multivariate | 0.323 | 0.346 | 0.342 | 0.328 |
| tirex2 / univariate | 0.322 | 0.341 | 0.337 | 0.323 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.041 | 0.079 | 0.043 | 0.008 |
| bvar / multivariate | 0.047 | 0.084 | 0.037 | 0.007 |
| chronos2 / multivariate | 0.037 | 0.010 | 0.014 | -0.004 |
| chronos2 / univariate | 0.026 | 0.027 | 0.018 | 0.003 |
| combo_bench / multivariate | 0.035 | 0.083 | 0.044 | 0.010 |
| combo_fm / univariate | 0.030 | 0.034 | 0.017 | 0.008 |
| dfm / multivariate | 0.029 | 0.082 | 0.047 | 0.013 |
| moirai2 / univariate | 0.026 | 0.036 | 0.024 | 0.006 |
| naive / univariate | 0.041 | 0.078 | 0.042 | 0.008 |
| timesfm25 / univariate | 0.041 | 0.049 | 0.023 | 0.021 |
| tirex / univariate | 0.035 | 0.026 | 0.009 | 0.005 |
| tirex2 / multivariate | 0.030 | 0.045 | 0.024 | 0.001 |
| tirex2 / univariate | 0.022 | 0.032 | 0.009 | 0.003 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.232 | 0.251 | 0.236 | 0.220 |
| bvar / multivariate | 0.224 | 0.251 | 0.238 | 0.246 |
| chronos2 / multivariate | 0.193 | 0.210 | 0.206 | 0.199 |
| chronos2 / univariate | 0.198 | 0.202 | 0.201 | 0.193 |
| combo_bench / multivariate | 0.221 | 0.255 | 0.239 | 0.232 |
| combo_fm / univariate | 0.196 | 0.200 | 0.197 | 0.189 |
| dfm / multivariate | 0.225 | 0.256 | 0.242 | 0.246 |
| moirai2 / univariate | 0.198 | 0.203 | 0.200 | 0.192 |
| naive / univariate | 0.234 | 0.251 | 0.239 | 0.248 |
| timesfm25 / univariate | 0.199 | 0.199 | 0.197 | 0.190 |
| tirex / univariate | 0.205 | 0.204 | 0.197 | 0.193 |
| tirex2 / multivariate | 0.194 | 0.204 | 0.203 | 0.195 |
| tirex2 / univariate | 0.196 | 0.203 | 0.201 | 0.193 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.754 | 0.729 | 0.752 | 0.794 |
| bvar / multivariate | 0.787 | 0.748 | 0.765 | 0.769 |
| chronos2 / multivariate | 0.768 | 0.750 | 0.781 | 0.794 |
| chronos2 / univariate | 0.810 | 0.836 | 0.810 | 0.809 |
| combo_bench / multivariate | 0.783 | 0.728 | 0.737 | 0.780 |
| combo_fm / univariate | 0.817 | 0.829 | 0.810 | 0.824 |
| dfm / multivariate | 0.748 | 0.708 | 0.724 | 0.734 |
| moirai2 / univariate | 0.782 | 0.829 | 0.818 | 0.824 |
| naive / univariate | 0.768 | 0.729 | 0.745 | 0.725 |
| timesfm25 / univariate | 0.824 | 0.836 | 0.832 | 0.840 |
| tirex / univariate | 0.803 | 0.800 | 0.796 | 0.817 |
| tirex2 / multivariate | 0.796 | 0.814 | 0.810 | 0.817 |
| tirex2 / univariate | 0.754 | 0.771 | 0.788 | 0.817 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | no | no | no | no |
| bvar / multivariate | yes | no | no | no |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | no |  |  |  |
| chronos2 / univariate | yes | yes | yes | yes |
| chronos2 / univariate_levels | no |  |  |  |
| combo_bench / multivariate | yes | no | no | no |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | no | no | no | no |
| moirai2 / univariate | yes | yes | yes | yes |
| moirai2 / univariate_levels | no |  |  |  |
| naive / univariate | no | no | no | no |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | no |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

### CA / cpi_core


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 142 | 140 | 137 | 131 |
| bvar / multivariate | 141 | 139 | 136 | 130 |
| chronos2 / multivariate | 142 | 140 | 137 | 131 |
| chronos2 / univariate | 142 | 140 | 137 | 131 |
| combo_bench / multivariate | 138 | 136 | 133 | 127 |
| combo_fm / univariate | 142 | 140 | 137 | 131 |
| dfm / multivariate | 139 | 137 | 134 | 128 |
| moirai2 / univariate | 142 | 140 | 137 | 131 |
| naive / univariate | 142 | 140 | 137 | 131 |
| timesfm25 / univariate | 142 | 140 | 137 | 131 |
| tirex / univariate | 142 | 140 | 137 | 131 |
| tirex2 / multivariate | 142 | 140 | 137 | 131 |
| tirex2 / univariate | 142 | 140 | 137 | 131 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 1.223 | 1.289 | 1.255 | 1.326 |
| chronos2 / multivariate | 0.999 | 1.021 | 1.059 | 1.047 |
| chronos2 / univariate | 1.030 | 1.046 | 1.040 | 0.995 |
| combo_bench / multivariate | 1.066 | 1.129 | 1.102 | 1.135 |
| combo_fm / univariate | 0.967 | 0.974 | 0.963 | 0.960 |
| dfm / multivariate | 1.179 | 1.271 | 1.237 | 1.282 |
| moirai2 / univariate | 1.002 | 0.999 | 0.968 | 0.990 |
| naive / univariate | 1.172 | 1.268 | 1.237 | 1.316 |
| timesfm25 / univariate | 0.976 | 0.961 | 0.960 | 0.958 |
| tirex / univariate | 0.959 | 0.983 | 0.970 | 0.952 |
| tirex2 / multivariate | 0.950 | 0.960 | 0.992 | 0.975 |
| tirex2 / univariate | 0.948 | 0.950 | 0.957 | 0.965 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 1.227 | 1.318 | 1.266 | 1.350 |
| chronos2 / multivariate | 1.000 | 1.047 | 1.055 | 1.027 |
| chronos2 / univariate | 1.034 | 1.046 | 1.065 | 0.954 |
| combo_bench / multivariate | 1.085 | 1.155 | 1.114 | 1.154 |
| combo_fm / univariate | 0.976 | 0.967 | 0.971 | 0.916 |
| dfm / multivariate | 1.225 | 1.307 | 1.263 | 1.324 |
| moirai2 / univariate | 0.997 | 0.980 | 0.950 | 0.959 |
| naive / univariate | 1.208 | 1.303 | 1.265 | 1.351 |
| timesfm25 / univariate | 0.985 | 0.958 | 0.969 | 0.916 |
| tirex / univariate | 0.980 | 0.977 | 0.976 | 0.920 |
| tirex2 / multivariate | 0.963 | 0.966 | 1.005 | 0.930 |
| tirex2 / univariate | 0.953 | 0.938 | 0.960 | 0.915 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.000 | 0.000 | 0.001 | 0.000 |
| chronos2 / multivariate | 0.984 | 0.700 | 0.262 | 0.312 |
| chronos2 / univariate | 0.459 | 0.230 | 0.353 | 0.894 |
| combo_bench / multivariate | 0.108 | 0.003 | 0.062 | 0.026 |
| combo_fm / univariate | 0.242 | 0.368 | 0.229 | 0.198 |
| dfm / multivariate | 0.003 | 0.000 | 0.003 | 0.002 |
| moirai2 / univariate | 0.955 | 0.980 | 0.364 | 0.780 |
| naive / univariate | 0.003 | 0.000 | 0.002 | 0.000 |
| timesfm25 / univariate | 0.428 | 0.214 | 0.271 | 0.258 |
| tirex / univariate | 0.153 | 0.549 | 0.313 | 0.093 |
| tirex2 / multivariate | 0.135 | 0.152 | 0.833 | 0.489 |
| tirex2 / univariate | 0.069 | 0.050 | 0.118 | 0.276 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.256 | 0.254 | 0.249 | 0.254 |
| bvar / multivariate | 0.314 | 0.328 | 0.313 | 0.335 |
| chronos2 / multivariate | 0.255 | 0.259 | 0.264 | 0.266 |
| chronos2 / univariate | 0.263 | 0.265 | 0.259 | 0.252 |
| combo_bench / multivariate | 0.272 | 0.290 | 0.277 | 0.286 |
| combo_fm / univariate | 0.247 | 0.247 | 0.240 | 0.243 |
| dfm / multivariate | 0.299 | 0.325 | 0.311 | 0.324 |
| moirai2 / univariate | 0.256 | 0.253 | 0.241 | 0.251 |
| naive / univariate | 0.300 | 0.322 | 0.308 | 0.334 |
| timesfm25 / univariate | 0.249 | 0.244 | 0.239 | 0.243 |
| tirex / univariate | 0.245 | 0.249 | 0.242 | 0.242 |
| tirex2 / multivariate | 0.243 | 0.243 | 0.247 | 0.247 |
| tirex2 / univariate | 0.242 | 0.241 | 0.238 | 0.245 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | -0.007 | 0.015 | 0.000 | 0.008 |
| bvar / multivariate | 0.050 | 0.079 | 0.047 | 0.029 |
| chronos2 / multivariate | 0.036 | 0.017 | 0.015 | 0.022 |
| chronos2 / univariate | 0.006 | -0.004 | 0.008 | -0.003 |
| combo_bench / multivariate | 0.008 | 0.044 | 0.020 | 0.011 |
| combo_fm / univariate | 0.007 | 0.002 | -0.001 | 0.002 |
| dfm / multivariate | -0.007 | 0.041 | 0.014 | -0.005 |
| moirai2 / univariate | 0.003 | -0.009 | -0.004 | -0.000 |
| naive / univariate | -0.002 | 0.041 | 0.011 | -0.011 |
| timesfm25 / univariate | -0.001 | -0.001 | -0.011 | -0.002 |
| tirex / univariate | 0.015 | 0.020 | 0.008 | 0.016 |
| tirex2 / multivariate | 0.025 | 0.019 | -0.002 | -0.008 |
| tirex2 / univariate | 0.011 | 0.007 | -0.009 | -0.001 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.159 | 0.158 | 0.153 | 0.158 |
| bvar / multivariate | 0.196 | 0.207 | 0.195 | 0.213 |
| chronos2 / multivariate | 0.158 | 0.163 | 0.164 | 0.166 |
| chronos2 / univariate | 0.165 | 0.165 | 0.161 | 0.154 |
| combo_bench / multivariate | 0.169 | 0.182 | 0.173 | 0.180 |
| combo_fm / univariate | 0.153 | 0.152 | 0.147 | 0.148 |
| dfm / multivariate | 0.189 | 0.207 | 0.196 | 0.206 |
| moirai2 / univariate | 0.159 | 0.155 | 0.147 | 0.154 |
| naive / univariate | 0.188 | 0.204 | 0.194 | 0.213 |
| timesfm25 / univariate | 0.154 | 0.150 | 0.147 | 0.148 |
| tirex / univariate | 0.152 | 0.154 | 0.148 | 0.148 |
| tirex2 / multivariate | 0.152 | 0.151 | 0.153 | 0.151 |
| tirex2 / univariate | 0.151 | 0.149 | 0.146 | 0.148 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.718 | 0.721 | 0.715 | 0.718 |
| bvar / multivariate | 0.709 | 0.712 | 0.750 | 0.731 |
| chronos2 / multivariate | 0.690 | 0.700 | 0.752 | 0.695 |
| chronos2 / univariate | 0.711 | 0.736 | 0.759 | 0.779 |
| combo_bench / multivariate | 0.761 | 0.728 | 0.752 | 0.724 |
| combo_fm / univariate | 0.739 | 0.771 | 0.796 | 0.794 |
| dfm / multivariate | 0.734 | 0.701 | 0.731 | 0.719 |
| moirai2 / univariate | 0.704 | 0.779 | 0.774 | 0.771 |
| naive / univariate | 0.746 | 0.707 | 0.737 | 0.695 |
| timesfm25 / univariate | 0.761 | 0.764 | 0.781 | 0.802 |
| tirex / univariate | 0.732 | 0.764 | 0.825 | 0.786 |
| tirex2 / multivariate | 0.718 | 0.779 | 0.788 | 0.802 |
| tirex2 / univariate | 0.718 | 0.743 | 0.781 | 0.779 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | yes | yes | yes | yes |
| bvar / multivariate | no | no | no | no |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | no |  |  |  |
| chronos2 / univariate | yes | no | no | yes |
| chronos2 / univariate_levels | no |  |  |  |
| combo_bench / multivariate | no | no | no | no |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | no | no | no | no |
| moirai2 / univariate | yes | yes | yes | yes |
| moirai2 / univariate_levels | no |  |  |  |
| naive / univariate | no | no | no | no |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | no |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

### CA / gdp


**Scored forecasts (n)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 140 | 137 | 131 |
| bvar / multivariate | 140 | 137 | 131 |
| chronos2 / multivariate | 94 | 92 | 88 |
| chronos2 / univariate | 140 | 137 | 131 |
| combo_bench / multivariate | 137 | 134 | 128 |
| combo_fm / univariate | 140 | 137 | 131 |
| dfm / multivariate | 137 | 134 | 128 |
| moirai2 / univariate | 140 | 137 | 131 |
| naive / univariate | 140 | 137 | 131 |
| timesfm25 / univariate | 140 | 137 | 131 |
| tirex / univariate | 140 | 137 | 131 |
| tirex2 / multivariate | 94 | 92 | 88 |
| tirex2 / univariate | 140 | 137 | 131 |

**Relative RMSFE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 1.119 | 1.164 | 1.121 |
| chronos2 / multivariate | 1.070 | 1.038 | 1.003 |
| chronos2 / univariate | 1.324 | 1.351 | 1.212 |
| combo_bench / multivariate | 0.806 | 1.003 | 1.009 |
| combo_fm / univariate | 0.996 | 1.023 | 1.004 |
| dfm / multivariate | 0.407 | 0.928 | 1.000 |
| moirai2 / univariate | 0.972 | 0.999 | 0.994 |
| naive / univariate | 0.795 | 0.946 | 1.000 |
| timesfm25 / univariate | 0.931 | 1.005 | 0.996 |
| tirex / univariate | 0.957 | 0.962 | 0.992 |
| tirex2 / multivariate | 0.945 | 0.967 | 0.995 |
| tirex2 / univariate | 0.846 | 0.951 | 0.992 |

**Relative MAE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 1.081 | 1.103 | 1.134 |
| chronos2 / multivariate | 0.996 | 1.033 | 1.056 |
| chronos2 / univariate | 1.107 | 1.206 | 1.260 |
| combo_bench / multivariate | 0.842 | 0.988 | 1.019 |
| combo_fm / univariate | 0.952 | 1.002 | 1.033 |
| dfm / multivariate | 0.563 | 0.941 | 1.017 |
| moirai2 / univariate | 0.936 | 0.973 | 0.996 |
| naive / univariate | 0.876 | 0.924 | 1.017 |
| timesfm25 / univariate | 0.952 | 1.026 | 1.025 |
| tirex / univariate | 0.973 | 0.945 | 0.989 |
| tirex2 / multivariate | 0.947 | 0.949 | 1.003 |
| tirex2 / univariate | 0.882 | 0.903 | 0.987 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.224 | 0.278 | 0.333 |
| chronos2 / multivariate | 0.181 | 0.375 | 0.844 |
| chronos2 / univariate | 0.097 | 0.186 | 0.268 |
| combo_bench / multivariate | 0.026 | 0.900 | 0.531 |
| combo_fm / univariate | 0.203 | 0.371 | 0.794 |
| dfm / multivariate | 0.022 | 0.076 | 0.938 |
| moirai2 / univariate | 0.081 | 0.879 | 0.465 |
| naive / univariate | 0.158 | 0.154 | 0.928 |
| timesfm25 / univariate | 0.071 | 0.688 | 0.791 |
| tirex / univariate | 0.063 | 0.079 | 0.449 |
| tirex2 / multivariate | 0.158 | 0.071 | 0.564 |
| tirex2 / univariate | 0.072 | 0.050 | 0.465 |

**RMSFE (transformed units)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 2.931 | 2.485 | 2.397 |
| bvar / multivariate | 3.281 | 2.893 | 2.688 |
| chronos2 / multivariate | 3.129 | 2.571 | 2.395 |
| chronos2 / univariate | 3.881 | 3.359 | 2.906 |
| combo_bench / multivariate | 2.389 | 2.520 | 2.446 |
| combo_fm / univariate | 2.920 | 2.542 | 2.407 |
| dfm / multivariate | 1.206 | 2.332 | 2.425 |
| moirai2 / univariate | 2.849 | 2.482 | 2.382 |
| naive / univariate | 2.329 | 2.351 | 2.398 |
| timesfm25 / univariate | 2.728 | 2.497 | 2.388 |
| tirex / univariate | 2.804 | 2.392 | 2.378 |
| tirex2 / multivariate | 2.764 | 2.396 | 2.375 |
| tirex2 / univariate | 2.480 | 2.363 | 2.377 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | -0.138 | -0.275 | -0.314 |
| bvar / multivariate | 0.041 | -0.027 | 0.024 |
| chronos2 / multivariate | -0.008 | -0.103 | -0.136 |
| chronos2 / univariate | 0.083 | 0.058 | 0.024 |
| combo_bench / multivariate | -0.140 | -0.247 | -0.219 |
| combo_fm / univariate | -0.077 | -0.145 | -0.168 |
| dfm / multivariate | -0.318 | -0.418 | -0.370 |
| moirai2 / univariate | -0.105 | -0.167 | -0.189 |
| naive / univariate | -0.385 | -0.385 | -0.368 |
| timesfm25 / univariate | -0.141 | -0.206 | -0.229 |
| tirex / univariate | -0.111 | -0.233 | -0.249 |
| tirex2 / multivariate | -0.066 | -0.176 | -0.214 |
| tirex2 / univariate | -0.109 | -0.175 | -0.196 |

**Weighted quantile loss**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 0.982 | 0.950 | 0.882 |
| bvar / multivariate | 1.094 | 1.081 | 1.026 |
| chronos2 / multivariate | 0.927 | 0.947 | 0.919 |
| chronos2 / univariate | 1.016 | 1.063 | 1.033 |
| combo_bench / multivariate | 0.855 | 0.965 | 0.928 |
| combo_fm / univariate | 0.886 | 0.912 | 0.889 |
| dfm / multivariate | 0.526 | 0.877 | 0.892 |
| moirai2 / univariate | 0.866 | 0.871 | 0.861 |
| naive / univariate | 0.855 | 0.869 | 0.887 |
| timesfm25 / univariate | 0.883 | 0.927 | 0.874 |
| tirex / univariate | 0.882 | 0.892 | 0.886 |
| tirex2 / multivariate | 0.885 | 0.871 | 0.850 |
| tirex2 / univariate | 0.822 | 0.839 | 0.843 |

**80% interval coverage**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 0.914 | 0.912 | 0.885 |
| bvar / multivariate | 0.893 | 0.854 | 0.847 |
| chronos2 / multivariate | 0.809 | 0.804 | 0.773 |
| chronos2 / univariate | 0.807 | 0.803 | 0.840 |
| combo_bench / multivariate | 0.876 | 0.888 | 0.883 |
| combo_fm / univariate | 0.829 | 0.869 | 0.817 |
| dfm / multivariate | 0.883 | 0.873 | 0.883 |
| moirai2 / univariate | 0.850 | 0.891 | 0.840 |
| naive / univariate | 0.914 | 0.891 | 0.885 |
| timesfm25 / univariate | 0.807 | 0.810 | 0.817 |
| tirex / univariate | 0.786 | 0.847 | 0.794 |
| tirex2 / multivariate | 0.702 | 0.761 | 0.773 |
| tirex2 / univariate | 0.764 | 0.832 | 0.863 |

**Model confidence set (90%) membership**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | yes | yes | yes |
| bvar / multivariate | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |
| chronos2 / univariate | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |
| combo_bench / multivariate | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes |
| dfm / multivariate | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes |
| moirai2 / univariate_levels | yes |  |  |
| naive / univariate | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |
| tirex / univariate | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |
| tirex2 / multivariate | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |
| tirex2 / univariate | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |

### CA / retail


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 140 | 139 | 136 | 131 |
| bvar / multivariate | 139 | 138 | 135 | 130 |
| chronos2 / multivariate | 140 | 139 | 136 | 131 |
| chronos2 / univariate | 140 | 139 | 136 | 131 |
| combo_bench / multivariate | 136 | 135 | 132 | 127 |
| combo_fm / univariate | 140 | 139 | 136 | 131 |
| dfm / multivariate | 137 | 136 | 133 | 128 |
| moirai2 / univariate | 140 | 139 | 136 | 131 |
| naive / univariate | 140 | 139 | 136 | 131 |
| timesfm25 / univariate | 140 | 139 | 136 | 131 |
| tirex / univariate | 140 | 139 | 136 | 131 |
| tirex2 / multivariate | 140 | 139 | 136 | 131 |
| tirex2 / univariate | 140 | 139 | 136 | 131 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.567 | 0.976 | 0.971 | 0.995 |
| chronos2 / multivariate | 1.161 | 1.124 | 1.062 | 1.005 |
| chronos2 / univariate | 1.222 | 1.164 | 1.130 | 1.074 |
| combo_bench / multivariate | 0.717 | 0.976 | 0.973 | 0.994 |
| combo_fm / univariate | 1.034 | 0.998 | 0.971 | 0.970 |
| dfm / multivariate | 0.725 | 0.974 | 0.956 | 0.981 |
| moirai2 / univariate | 1.041 | 0.994 | 0.961 | 0.975 |
| naive / univariate | 0.908 | 0.980 | 0.955 | 0.981 |
| timesfm25 / univariate | 0.959 | 0.980 | 0.959 | 0.978 |
| tirex / univariate | 0.981 | 0.978 | 0.964 | 0.986 |
| tirex2 / multivariate | 0.954 | 0.981 | 0.956 | 0.981 |
| tirex2 / univariate | 1.023 | 0.983 | 0.957 | 0.982 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.741 | 1.043 | 1.004 | 0.977 |
| chronos2 / multivariate | 0.934 | 1.066 | 1.018 | 0.988 |
| chronos2 / univariate | 0.975 | 1.086 | 1.050 | 1.027 |
| combo_bench / multivariate | 0.788 | 0.996 | 0.976 | 0.974 |
| combo_fm / univariate | 0.920 | 0.993 | 0.959 | 0.935 |
| dfm / multivariate | 0.806 | 1.021 | 0.922 | 0.957 |
| moirai2 / univariate | 0.915 | 0.992 | 0.943 | 0.958 |
| naive / univariate | 0.859 | 0.951 | 0.913 | 0.958 |
| timesfm25 / univariate | 0.904 | 0.968 | 0.930 | 0.959 |
| tirex / univariate | 0.931 | 0.971 | 0.954 | 0.985 |
| tirex2 / multivariate | 0.861 | 0.959 | 0.918 | 0.957 |
| tirex2 / univariate | 0.897 | 0.971 | 0.925 | 0.960 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.080 | 0.391 | 0.400 | 0.381 |
| chronos2 / multivariate | 0.579 | 0.381 | 0.467 | 0.701 |
| chronos2 / univariate | 0.503 | 0.372 | 0.387 | 0.384 |
| combo_bench / multivariate | 0.053 | 0.127 | 0.330 | 0.136 |
| combo_fm / univariate | 0.813 | 0.950 | 0.369 | 0.223 |
| dfm / multivariate | 0.063 | 0.217 | 0.297 | 0.134 |
| moirai2 / univariate | 0.795 | 0.762 | 0.322 | 0.209 |
| naive / univariate | 0.178 | 0.198 | 0.289 | 0.136 |
| timesfm25 / univariate | 0.605 | 0.193 | 0.272 | 0.169 |
| tirex / univariate | 0.833 | 0.176 | 0.338 | 0.189 |
| tirex2 / multivariate | 0.572 | 0.230 | 0.295 | 0.135 |
| tirex2 / univariate | 0.846 | 0.300 | 0.298 | 0.156 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 3.929 | 3.657 | 3.782 | 3.747 |
| bvar / multivariate | 2.115 | 3.583 | 3.670 | 3.650 |
| chronos2 / multivariate | 4.561 | 4.112 | 4.016 | 3.767 |
| chronos2 / univariate | 4.803 | 4.257 | 4.274 | 4.026 |
| combo_bench / multivariate | 2.700 | 3.617 | 3.716 | 3.688 |
| combo_fm / univariate | 4.063 | 3.651 | 3.671 | 3.636 |
| dfm / multivariate | 2.879 | 3.599 | 3.655 | 3.717 |
| moirai2 / univariate | 4.093 | 3.635 | 3.635 | 3.653 |
| naive / univariate | 3.568 | 3.583 | 3.610 | 3.677 |
| timesfm25 / univariate | 3.768 | 3.583 | 3.626 | 3.663 |
| tirex / univariate | 3.853 | 3.578 | 3.647 | 3.693 |
| tirex2 / multivariate | 3.750 | 3.588 | 3.616 | 3.677 |
| tirex2 / univariate | 4.021 | 3.596 | 3.620 | 3.680 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | -0.000 | -0.161 | -0.081 | -0.099 |
| bvar / multivariate | -0.315 | 0.007 | -0.122 | 0.005 |
| chronos2 / multivariate | -0.002 | 0.006 | 0.051 | 0.031 |
| chronos2 / univariate | 0.019 | 0.062 | 0.099 | 0.115 |
| combo_bench / multivariate | -0.254 | -0.105 | -0.120 | -0.025 |
| combo_fm / univariate | -0.091 | -0.071 | -0.039 | -0.037 |
| dfm / multivariate | -0.234 | -0.169 | -0.095 | -0.093 |
| moirai2 / univariate | -0.149 | -0.107 | -0.055 | -0.071 |
| naive / univariate | -0.129 | -0.128 | -0.089 | -0.087 |
| timesfm25 / univariate | -0.134 | -0.131 | -0.090 | -0.092 |
| tirex / univariate | -0.125 | -0.068 | -0.070 | -0.053 |
| tirex2 / multivariate | -0.133 | -0.141 | -0.097 | -0.092 |
| tirex2 / univariate | -0.067 | -0.112 | -0.080 | -0.086 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 1.426 | 1.320 | 1.367 | 1.346 |
| bvar / multivariate | 0.885 | 1.288 | 1.325 | 1.308 |
| chronos2 / multivariate | 1.215 | 1.328 | 1.278 | 1.243 |
| chronos2 / univariate | 1.294 | 1.388 | 1.365 | 1.326 |
| combo_bench / multivariate | 1.003 | 1.285 | 1.319 | 1.287 |
| combo_fm / univariate | 1.221 | 1.255 | 1.229 | 1.204 |
| dfm / multivariate | 1.112 | 1.291 | 1.261 | 1.295 |
| moirai2 / univariate | 1.242 | 1.246 | 1.215 | 1.208 |
| naive / univariate | 1.245 | 1.262 | 1.258 | 1.300 |
| timesfm25 / univariate | 1.221 | 1.221 | 1.204 | 1.207 |
| tirex / univariate | 1.216 | 1.254 | 1.246 | 1.275 |
| tirex2 / multivariate | 1.197 | 1.232 | 1.201 | 1.228 |
| tirex2 / univariate | 1.231 | 1.245 | 1.209 | 1.219 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.893 | 0.906 | 0.890 | 0.885 |
| bvar / multivariate | 0.820 | 0.870 | 0.881 | 0.869 |
| chronos2 / multivariate | 0.807 | 0.770 | 0.824 | 0.824 |
| chronos2 / univariate | 0.771 | 0.763 | 0.794 | 0.817 |
| combo_bench / multivariate | 0.875 | 0.889 | 0.902 | 0.882 |
| combo_fm / univariate | 0.771 | 0.741 | 0.824 | 0.817 |
| dfm / multivariate | 0.898 | 0.897 | 0.902 | 0.891 |
| moirai2 / univariate | 0.800 | 0.806 | 0.824 | 0.832 |
| naive / univariate | 0.907 | 0.906 | 0.904 | 0.893 |
| timesfm25 / univariate | 0.750 | 0.755 | 0.787 | 0.786 |
| tirex / univariate | 0.764 | 0.813 | 0.860 | 0.840 |
| tirex2 / multivariate | 0.800 | 0.734 | 0.801 | 0.794 |
| tirex2 / univariate | 0.743 | 0.719 | 0.765 | 0.779 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | yes | yes | yes | yes |
| bvar / multivariate | yes | yes | no | yes |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |  |
| chronos2 / univariate | yes | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |  |
| combo_bench / multivariate | yes | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | yes | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes | yes |
| moirai2 / univariate_levels | yes |  |  |  |
| naive / univariate | yes | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

### CA / unemp


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 142 | 141 | 138 | 132 |
| bvar / multivariate | 141 | 140 | 137 | 131 |
| chronos2 / multivariate | 142 | 141 | 138 | 132 |
| chronos2 / univariate | 142 | 141 | 138 | 132 |
| combo_bench / multivariate | 138 | 137 | 134 | 128 |
| combo_fm / univariate | 142 | 141 | 138 | 132 |
| dfm / multivariate | 139 | 138 | 135 | 129 |
| moirai2 / univariate | 142 | 141 | 138 | 132 |
| naive / univariate | 142 | 141 | 138 | 132 |
| timesfm25 / univariate | 142 | 141 | 138 | 132 |
| tirex / univariate | 142 | 141 | 138 | 132 |
| tirex2 / multivariate | 142 | 141 | 138 | 132 |
| tirex2 / univariate | 142 | 141 | 138 | 132 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.970 | 1.022 | 1.008 | 0.990 |
| chronos2 / multivariate | 1.339 | 1.305 | 1.117 | 0.980 |
| chronos2 / univariate | 1.100 | 1.082 | 1.007 | 0.983 |
| combo_bench / multivariate | 0.971 | 0.998 | 1.003 | 0.991 |
| combo_fm / univariate | 0.987 | 1.004 | 1.001 | 0.984 |
| dfm / multivariate | 1.006 | 0.979 | 1.001 | 0.987 |
| moirai2 / univariate | 0.929 | 0.983 | 1.019 | 0.997 |
| naive / univariate | 0.942 | 0.965 | 0.999 | 0.987 |
| timesfm25 / univariate | 0.979 | 1.008 | 1.005 | 0.992 |
| tirex / univariate | 1.007 | 0.987 | 1.002 | 0.984 |
| tirex2 / multivariate | 1.097 | 1.025 | 1.000 | 0.987 |
| tirex2 / univariate | 0.999 | 0.998 | 0.998 | 0.987 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 1.018 | 1.110 | 1.021 | 0.983 |
| chronos2 / multivariate | 1.099 | 1.099 | 1.089 | 0.953 |
| chronos2 / univariate | 1.004 | 1.014 | 1.050 | 0.959 |
| combo_bench / multivariate | 0.992 | 1.025 | 1.001 | 0.980 |
| combo_fm / univariate | 0.966 | 0.959 | 1.017 | 0.960 |
| dfm / multivariate | 1.024 | 0.982 | 0.990 | 0.960 |
| moirai2 / univariate | 0.923 | 0.951 | 1.019 | 0.990 |
| naive / univariate | 0.943 | 0.949 | 0.977 | 0.961 |
| timesfm25 / univariate | 0.983 | 0.987 | 1.057 | 1.007 |
| tirex / univariate | 0.984 | 0.941 | 1.009 | 0.958 |
| tirex2 / multivariate | 1.008 | 0.967 | 0.993 | 0.979 |
| tirex2 / univariate | 0.993 | 0.957 | 1.002 | 0.985 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.395 | 0.112 | 0.102 | 0.485 |
| chronos2 / multivariate | 0.345 | 0.344 | 0.335 | 0.341 |
| chronos2 / univariate | 0.417 | 0.371 | 0.631 | 0.522 |
| combo_bench / multivariate | 0.154 | 0.815 | 0.328 | 0.407 |
| combo_fm / univariate | 0.733 | 0.845 | 0.941 | 0.480 |
| dfm / multivariate | 0.949 | 0.212 | 0.697 | 0.352 |
| moirai2 / univariate | 0.052 | 0.484 | 0.475 | 0.832 |
| naive / univariate | 0.019 | 0.197 | 0.884 | 0.345 |
| timesfm25 / univariate | 0.521 | 0.749 | 0.682 | 0.729 |
| tirex / univariate | 0.894 | 0.284 | 0.821 | 0.481 |
| tirex2 / multivariate | 0.460 | 0.581 | 0.945 | 0.434 |
| tirex2 / univariate | 0.972 | 0.910 | 0.799 | 0.465 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.466 | 0.582 | 0.547 | 0.594 |
| bvar / multivariate | 0.434 | 0.594 | 0.552 | 0.590 |
| chronos2 / multivariate | 0.624 | 0.760 | 0.611 | 0.582 |
| chronos2 / univariate | 0.512 | 0.630 | 0.551 | 0.584 |
| combo_bench / multivariate | 0.439 | 0.585 | 0.555 | 0.596 |
| combo_fm / univariate | 0.460 | 0.585 | 0.547 | 0.584 |
| dfm / multivariate | 0.473 | 0.576 | 0.553 | 0.591 |
| moirai2 / univariate | 0.433 | 0.572 | 0.557 | 0.592 |
| naive / univariate | 0.439 | 0.562 | 0.547 | 0.586 |
| timesfm25 / univariate | 0.456 | 0.587 | 0.549 | 0.589 |
| tirex / univariate | 0.469 | 0.575 | 0.548 | 0.584 |
| tirex2 / multivariate | 0.511 | 0.597 | 0.547 | 0.586 |
| tirex2 / univariate | 0.465 | 0.581 | 0.546 | 0.586 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | -0.055 | 0.020 | -0.033 | 0.006 |
| bvar / multivariate | -0.034 | 0.016 | -0.037 | 0.005 |
| chronos2 / multivariate | -0.079 | 0.006 | -0.039 | 0.014 |
| chronos2 / univariate | -0.053 | 0.025 | -0.028 | 0.009 |
| combo_bench / multivariate | -0.046 | 0.021 | -0.034 | 0.009 |
| combo_fm / univariate | -0.026 | 0.055 | -0.002 | 0.037 |
| dfm / multivariate | -0.066 | 0.017 | -0.038 | 0.008 |
| moirai2 / univariate | -0.010 | 0.071 | 0.013 | 0.054 |
| naive / univariate | -0.047 | 0.023 | -0.035 | 0.002 |
| timesfm25 / univariate | -0.008 | 0.074 | 0.019 | 0.058 |
| tirex / univariate | -0.025 | 0.060 | 0.002 | 0.039 |
| tirex2 / multivariate | -0.045 | 0.041 | -0.014 | 0.024 |
| tirex2 / univariate | -0.036 | 0.044 | -0.014 | 0.023 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.219 | 0.223 | 0.206 | 0.231 |
| bvar / multivariate | 0.207 | 0.239 | 0.215 | 0.237 |
| chronos2 / multivariate | 0.231 | 0.239 | 0.214 | 0.221 |
| chronos2 / univariate | 0.210 | 0.227 | 0.213 | 0.235 |
| combo_bench / multivariate | 0.209 | 0.226 | 0.210 | 0.230 |
| combo_fm / univariate | 0.202 | 0.213 | 0.203 | 0.223 |
| dfm / multivariate | 0.224 | 0.221 | 0.207 | 0.223 |
| moirai2 / univariate | 0.195 | 0.209 | 0.201 | 0.223 |
| naive / univariate | 0.208 | 0.214 | 0.204 | 0.223 |
| timesfm25 / univariate | 0.205 | 0.215 | 0.206 | 0.227 |
| tirex / univariate | 0.207 | 0.213 | 0.203 | 0.226 |
| tirex2 / multivariate | 0.213 | 0.217 | 0.207 | 0.226 |
| tirex2 / univariate | 0.209 | 0.214 | 0.207 | 0.226 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.824 | 0.837 | 0.841 | 0.833 |
| bvar / multivariate | 0.787 | 0.807 | 0.839 | 0.824 |
| chronos2 / multivariate | 0.634 | 0.652 | 0.710 | 0.727 |
| chronos2 / univariate | 0.683 | 0.660 | 0.717 | 0.674 |
| combo_bench / multivariate | 0.826 | 0.839 | 0.858 | 0.844 |
| combo_fm / univariate | 0.725 | 0.709 | 0.746 | 0.727 |
| dfm / multivariate | 0.784 | 0.833 | 0.830 | 0.845 |
| moirai2 / univariate | 0.768 | 0.745 | 0.761 | 0.780 |
| naive / univariate | 0.831 | 0.823 | 0.848 | 0.841 |
| timesfm25 / univariate | 0.697 | 0.730 | 0.732 | 0.735 |
| tirex / univariate | 0.732 | 0.723 | 0.761 | 0.727 |
| tirex2 / multivariate | 0.683 | 0.709 | 0.746 | 0.720 |
| tirex2 / univariate | 0.711 | 0.702 | 0.725 | 0.742 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | yes | yes | yes | yes |
| bvar / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |  |
| chronos2 / univariate | yes | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |  |
| combo_bench / multivariate | yes | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | yes | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes | yes |
| moirai2 / univariate_levels | yes |  |  |  |
| naive / univariate | yes | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

### EA / consumption


**Scored forecasts (n)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 133 | 130 | 124 |
| bvar / multivariate | 130 | 127 | 124 |
| chronos2 / multivariate | 133 | 130 | 124 |
| chronos2 / univariate | 133 | 130 | 124 |
| combo_bench / multivariate | 130 | 127 | 124 |
| combo_fm / univariate | 133 | 130 | 124 |
| dfm / multivariate | 133 | 130 | 124 |
| moirai2 / univariate | 133 | 130 | 124 |
| naive / univariate | 133 | 130 | 124 |
| timesfm25 / univariate | 133 | 130 | 124 |
| tirex / univariate | 133 | 130 | 124 |
| tirex2 / multivariate | 133 | 130 | 124 |
| tirex2 / univariate | 133 | 130 | 124 |

**Relative RMSFE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.570 | 0.717 | 0.913 |
| chronos2 / multivariate | 0.643 | 0.782 | 0.911 |
| chronos2 / univariate | 0.700 | 0.869 | 0.908 |
| combo_bench / multivariate | 0.628 | 0.727 | 0.916 |
| combo_fm / univariate | 0.600 | 0.736 | 0.906 |
| dfm / multivariate | 0.466 | 0.663 | 0.915 |
| moirai2 / univariate | 0.579 | 0.714 | 0.912 |
| naive / univariate | 0.420 | 0.679 | 0.916 |
| timesfm25 / univariate | 0.504 | 0.721 | 0.912 |
| tirex / univariate | 0.670 | 0.771 | 0.911 |
| tirex2 / multivariate | 0.572 | 0.697 | 0.907 |
| tirex2 / univariate | 0.573 | 0.695 | 0.907 |

**Relative MAE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.678 | 0.892 | 0.915 |
| chronos2 / multivariate | 0.679 | 0.915 | 0.880 |
| chronos2 / univariate | 0.705 | 1.011 | 0.878 |
| combo_bench / multivariate | 0.759 | 0.871 | 0.909 |
| combo_fm / univariate | 0.664 | 0.891 | 0.877 |
| dfm / multivariate | 0.650 | 0.785 | 0.906 |
| moirai2 / univariate | 0.661 | 0.859 | 0.906 |
| naive / univariate | 0.527 | 0.764 | 0.911 |
| timesfm25 / univariate | 0.601 | 0.843 | 0.922 |
| tirex / univariate | 0.711 | 0.961 | 0.912 |
| tirex2 / multivariate | 0.644 | 0.798 | 0.874 |
| tirex2 / univariate | 0.647 | 0.802 | 0.871 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.180 | 0.315 | 0.318 |
| chronos2 / multivariate | 0.027 | 0.391 | 0.318 |
| chronos2 / univariate | 0.020 | 0.586 | 0.309 |
| combo_bench / multivariate | 0.166 | 0.291 | 0.304 |
| combo_fm / univariate | 0.032 | 0.309 | 0.307 |
| dfm / multivariate | 0.043 | 0.233 | 0.327 |
| moirai2 / univariate | 0.034 | 0.284 | 0.324 |
| naive / univariate | 0.043 | 0.248 | 0.333 |
| timesfm25 / univariate | 0.040 | 0.274 | 0.329 |
| tirex / univariate | 0.032 | 0.361 | 0.321 |
| tirex2 / multivariate | 0.036 | 0.258 | 0.306 |
| tirex2 / univariate | 0.036 | 0.260 | 0.305 |

**RMSFE (transformed units)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 6.617 | 4.536 | 3.398 |
| bvar / multivariate | 1.871 | 3.219 | 3.103 |
| chronos2 / multivariate | 4.257 | 3.547 | 3.094 |
| chronos2 / univariate | 4.629 | 3.942 | 3.085 |
| combo_bench / multivariate | 2.061 | 3.267 | 3.112 |
| combo_fm / univariate | 3.968 | 3.339 | 3.078 |
| dfm / multivariate | 3.084 | 3.005 | 3.108 |
| moirai2 / univariate | 3.833 | 3.238 | 3.098 |
| naive / univariate | 2.781 | 3.080 | 3.112 |
| timesfm25 / univariate | 3.337 | 3.269 | 3.097 |
| tirex / univariate | 4.434 | 3.496 | 3.095 |
| tirex2 / multivariate | 3.787 | 3.162 | 3.081 |
| tirex2 / univariate | 3.789 | 3.154 | 3.080 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 0.496 | 0.135 | -0.173 |
| bvar / multivariate | -0.451 | -0.189 | -0.273 |
| chronos2 / multivariate | 0.129 | -0.075 | -0.310 |
| chronos2 / univariate | 0.252 | 0.055 | -0.242 |
| combo_bench / multivariate | -0.418 | -0.141 | -0.245 |
| combo_fm / univariate | 0.045 | -0.192 | -0.310 |
| dfm / multivariate | -0.079 | -0.275 | -0.289 |
| moirai2 / univariate | -0.031 | -0.249 | -0.348 |
| naive / univariate | -0.180 | -0.383 | -0.332 |
| timesfm25 / univariate | -0.102 | -0.375 | -0.355 |
| tirex / univariate | 0.094 | -0.117 | -0.289 |
| tirex2 / multivariate | 0.006 | -0.281 | -0.329 |
| tirex2 / univariate | 0.012 | -0.276 | -0.317 |

**Weighted quantile loss**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 1.852 | 1.505 | 1.314 |
| bvar / multivariate | 0.621 | 1.179 | 1.202 |
| chronos2 / multivariate | 1.015 | 1.144 | 1.082 |
| chronos2 / univariate | 1.125 | 1.287 | 1.125 |
| combo_bench / multivariate | 0.737 | 1.186 | 1.195 |
| combo_fm / univariate | 1.054 | 1.160 | 1.082 |
| dfm / multivariate | 1.133 | 1.117 | 1.174 |
| moirai2 / univariate | 1.059 | 1.120 | 1.094 |
| naive / univariate | 0.997 | 1.148 | 1.209 |
| timesfm25 / univariate | 1.024 | 1.150 | 1.098 |
| tirex / univariate | 1.091 | 1.220 | 1.125 |
| tirex2 / multivariate | 1.048 | 1.111 | 1.063 |
| tirex2 / univariate | 1.047 | 1.119 | 1.065 |

**80% interval coverage**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 0.895 | 0.877 | 0.863 |
| bvar / multivariate | 0.938 | 0.906 | 0.871 |
| chronos2 / multivariate | 0.865 | 0.885 | 0.895 |
| chronos2 / univariate | 0.857 | 0.854 | 0.895 |
| combo_bench / multivariate | 0.915 | 0.898 | 0.871 |
| combo_fm / univariate | 0.880 | 0.885 | 0.895 |
| dfm / multivariate | 0.872 | 0.846 | 0.871 |
| moirai2 / univariate | 0.842 | 0.846 | 0.863 |
| naive / univariate | 0.917 | 0.877 | 0.871 |
| timesfm25 / univariate | 0.835 | 0.854 | 0.879 |
| tirex / univariate | 0.910 | 0.931 | 0.895 |
| tirex2 / multivariate | 0.857 | 0.862 | 0.895 |
| tirex2 / univariate | 0.865 | 0.838 | 0.895 |

**Model confidence set (90%) membership**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | yes | yes | yes |
| bvar / multivariate | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |
| chronos2 / univariate | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |
| combo_bench / multivariate | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes |
| dfm / multivariate | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes |
| moirai2 / univariate_levels | yes |  |  |
| naive / univariate | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |
| tirex / univariate | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |
| tirex2 / multivariate | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |
| tirex2 / univariate | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |

### EA / gdp


**Scored forecasts (n)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 133 | 129 | 124 |
| bvar / multivariate | 133 | 129 | 124 |
| chronos2 / multivariate | 132 | 128 | 123 |
| chronos2 / univariate | 133 | 129 | 124 |
| combo_bench / multivariate | 133 | 129 | 124 |
| combo_fm / univariate | 133 | 129 | 124 |
| dfm / multivariate | 133 | 129 | 124 |
| moirai2 / univariate | 133 | 129 | 124 |
| naive / univariate | 133 | 129 | 124 |
| timesfm25 / univariate | 133 | 129 | 124 |
| tirex / univariate | 133 | 129 | 124 |
| tirex2 / multivariate | 132 | 128 | 123 |
| tirex2 / univariate | 133 | 129 | 124 |

**Relative RMSFE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.411 | 1.025 | 1.006 |
| chronos2 / multivariate | 0.642 | 0.919 | 1.006 |
| chronos2 / univariate | 0.840 | 1.099 | 1.003 |
| combo_bench / multivariate | 0.610 | 0.940 | 1.002 |
| combo_fm / univariate | 0.707 | 0.927 | 1.002 |
| dfm / multivariate | 0.496 | 0.916 | 1.002 |
| moirai2 / univariate | 0.687 | 0.907 | 1.003 |
| naive / univariate | 0.567 | 0.867 | 1.002 |
| timesfm25 / univariate | 0.625 | 0.919 | 1.009 |
| tirex / univariate | 0.795 | 0.936 | 1.001 |
| tirex2 / multivariate | 0.617 | 0.886 | 1.002 |
| tirex2 / univariate | 0.619 | 0.883 | 1.003 |

**Relative MAE to AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.625 | 1.097 | 1.025 |
| chronos2 / multivariate | 0.766 | 0.892 | 1.059 |
| chronos2 / univariate | 0.896 | 1.104 | 1.058 |
| combo_bench / multivariate | 0.739 | 0.863 | 0.999 |
| combo_fm / univariate | 0.816 | 0.935 | 1.042 |
| dfm / multivariate | 0.756 | 0.860 | 1.031 |
| moirai2 / univariate | 0.804 | 0.899 | 1.079 |
| naive / univariate | 0.691 | 0.796 | 1.012 |
| timesfm25 / univariate | 0.769 | 0.902 | 1.091 |
| tirex / univariate | 0.881 | 0.954 | 1.035 |
| tirex2 / multivariate | 0.744 | 0.829 | 1.043 |
| tirex2 / univariate | 0.746 | 0.828 | 1.043 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| bvar / multivariate | 0.071 | 0.381 | 0.060 |
| chronos2 / multivariate | 0.093 | 0.060 | 0.012 |
| chronos2 / univariate | 0.082 | 0.285 | 0.138 |
| combo_bench / multivariate | 0.071 | 0.187 | 0.186 |
| combo_fm / univariate | 0.102 | 0.043 | 0.079 |
| dfm / multivariate | 0.079 | 0.227 | 0.240 |
| moirai2 / univariate | 0.107 | 0.040 | 0.280 |
| naive / univariate | 0.117 | 0.040 | 0.231 |
| timesfm25 / univariate | 0.108 | 0.065 | 0.019 |
| tirex / univariate | 0.109 | 0.055 | 0.651 |
| tirex2 / multivariate | 0.106 | 0.041 | 0.026 |
| tirex2 / univariate | 0.109 | 0.040 | 0.003 |

**RMSFE (transformed units)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 5.087 | 3.091 | 2.769 |
| bvar / multivariate | 2.093 | 3.168 | 2.786 |
| chronos2 / multivariate | 3.278 | 2.853 | 2.796 |
| chronos2 / univariate | 4.275 | 3.398 | 2.778 |
| combo_bench / multivariate | 3.103 | 2.904 | 2.774 |
| combo_fm / univariate | 3.595 | 2.866 | 2.774 |
| dfm / multivariate | 2.524 | 2.831 | 2.775 |
| moirai2 / univariate | 3.496 | 2.803 | 2.776 |
| naive / univariate | 2.886 | 2.681 | 2.774 |
| timesfm25 / univariate | 3.177 | 2.840 | 2.795 |
| tirex / univariate | 4.046 | 2.894 | 2.772 |
| tirex2 / multivariate | 3.149 | 2.748 | 2.787 |
| tirex2 / univariate | 3.147 | 2.728 | 2.777 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 0.306 | 0.296 | -0.208 |
| bvar / multivariate | -0.169 | 0.028 | -0.159 |
| chronos2 / multivariate | -0.084 | 0.106 | -0.260 |
| chronos2 / univariate | 0.142 | 0.357 | -0.210 |
| combo_bench / multivariate | 0.036 | 0.133 | -0.185 |
| combo_fm / univariate | -0.044 | 0.143 | -0.230 |
| dfm / multivariate | -0.029 | 0.076 | -0.188 |
| moirai2 / univariate | -0.085 | 0.109 | -0.242 |
| naive / univariate | -0.242 | 0.027 | -0.213 |
| timesfm25 / univariate | -0.172 | 0.011 | -0.294 |
| tirex / univariate | 0.056 | 0.188 | -0.171 |
| tirex2 / multivariate | -0.154 | 0.062 | -0.237 |
| tirex2 / univariate | -0.163 | 0.051 | -0.234 |

**Weighted quantile loss**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 1.352 | 1.146 | 0.979 |
| bvar / multivariate | 0.732 | 1.155 | 1.001 |
| chronos2 / multivariate | 0.889 | 0.919 | 0.887 |
| chronos2 / univariate | 0.965 | 1.028 | 0.885 |
| combo_bench / multivariate | 0.934 | 0.987 | 0.966 |
| combo_fm / univariate | 0.929 | 0.919 | 0.869 |
| dfm / multivariate | 0.925 | 0.932 | 0.937 |
| moirai2 / univariate | 0.923 | 0.892 | 0.885 |
| naive / univariate | 0.979 | 0.945 | 0.982 |
| timesfm25 / univariate | 0.923 | 0.905 | 0.881 |
| tirex / univariate | 0.971 | 0.952 | 0.887 |
| tirex2 / multivariate | 0.891 | 0.857 | 0.863 |
| tirex2 / univariate | 0.893 | 0.853 | 0.858 |

**80% interval coverage**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | 0.925 | 0.899 | 0.911 |
| bvar / multivariate | 0.887 | 0.907 | 0.911 |
| chronos2 / multivariate | 0.871 | 0.898 | 0.902 |
| chronos2 / univariate | 0.902 | 0.891 | 0.911 |
| combo_bench / multivariate | 0.932 | 0.930 | 0.911 |
| combo_fm / univariate | 0.902 | 0.907 | 0.911 |
| dfm / multivariate | 0.805 | 0.899 | 0.903 |
| moirai2 / univariate | 0.895 | 0.884 | 0.911 |
| naive / univariate | 0.932 | 0.930 | 0.911 |
| timesfm25 / univariate | 0.872 | 0.876 | 0.895 |
| tirex / univariate | 0.880 | 0.930 | 0.903 |
| tirex2 / multivariate | 0.841 | 0.883 | 0.902 |
| tirex2 / univariate | 0.857 | 0.891 | 0.903 |

**Model confidence set (90%) membership**

| model / variant | h1 | h2 | h4 |
|---|---|---|---|
| ar / univariate | yes | yes | yes |
| bvar / multivariate | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |
| chronos2 / univariate | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |
| combo_bench / multivariate | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes |
| dfm / multivariate | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes |
| moirai2 / univariate_levels | yes |  |  |
| naive / univariate | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |
| tirex / univariate | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |
| tirex2 / multivariate | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |
| tirex2 / univariate | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |

### EA / hicp


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 142 | 140 | 136 | 131 |
| bvar / multivariate | 142 | 140 | 136 | 131 |
| chronos2 / multivariate | 142 | 140 | 136 | 131 |
| chronos2 / univariate | 142 | 140 | 136 | 131 |
| combo_bench / multivariate | 140 | 138 | 134 | 129 |
| combo_fm / univariate | 142 | 140 | 136 | 131 |
| dfm / multivariate | 140 | 138 | 134 | 129 |
| moirai2 / univariate | 142 | 140 | 136 | 131 |
| naive / univariate | 142 | 140 | 136 | 131 |
| timesfm25 / univariate | 142 | 140 | 136 | 131 |
| tirex / univariate | 142 | 140 | 136 | 131 |
| tirex2 / multivariate | 142 | 140 | 136 | 131 |
| tirex2 / univariate | 142 | 140 | 136 | 131 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.803 | 0.851 | 0.986 | 1.034 |
| chronos2 / multivariate | 0.894 | 0.933 | 0.934 | 0.989 |
| chronos2 / univariate | 0.926 | 0.973 | 0.983 | 1.148 |
| combo_bench / multivariate | 0.908 | 0.862 | 0.961 | 0.986 |
| combo_fm / univariate | 0.926 | 0.950 | 0.989 | 1.138 |
| dfm / multivariate | 1.420 | 1.161 | 1.262 | 1.246 |
| moirai2 / univariate | 0.937 | 0.987 | 1.030 | 1.156 |
| naive / univariate | 1.486 | 1.118 | 1.259 | 1.248 |
| timesfm25 / univariate | 0.940 | 0.931 | 0.997 | 1.119 |
| tirex / univariate | 1.024 | 0.985 | 1.016 | 1.161 |
| tirex2 / multivariate | 0.964 | 0.990 | 1.026 | 1.205 |
| tirex2 / univariate | 0.980 | 1.001 | 1.043 | 1.249 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.838 | 0.962 | 1.011 | 1.042 |
| chronos2 / multivariate | 0.841 | 0.855 | 0.844 | 0.916 |
| chronos2 / univariate | 0.893 | 0.952 | 0.896 | 0.966 |
| combo_bench / multivariate | 0.931 | 0.952 | 0.956 | 0.934 |
| combo_fm / univariate | 0.884 | 0.885 | 0.876 | 0.924 |
| dfm / multivariate | 1.493 | 1.211 | 1.197 | 1.175 |
| moirai2 / univariate | 0.914 | 0.944 | 0.947 | 1.000 |
| naive / univariate | 1.536 | 1.171 | 1.198 | 1.179 |
| timesfm25 / univariate | 0.903 | 0.866 | 0.867 | 0.925 |
| tirex / univariate | 0.971 | 0.919 | 0.908 | 0.927 |
| tirex2 / multivariate | 0.960 | 0.933 | 0.911 | 0.961 |
| tirex2 / univariate | 0.966 | 0.946 | 0.928 | 0.991 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.030 | 0.298 | 0.822 | 0.512 |
| chronos2 / multivariate | 0.032 | 0.196 | 0.132 | 0.878 |
| chronos2 / univariate | 0.412 | 0.518 | 0.832 | 0.431 |
| combo_bench / multivariate | 0.216 | 0.190 | 0.530 | 0.812 |
| combo_fm / univariate | 0.358 | 0.321 | 0.898 | 0.527 |
| dfm / multivariate | 0.001 | 0.234 | 0.015 | 0.033 |
| moirai2 / univariate | 0.382 | 0.807 | 0.696 | 0.381 |
| naive / univariate | 0.000 | 0.360 | 0.016 | 0.028 |
| timesfm25 / univariate | 0.385 | 0.133 | 0.972 | 0.573 |
| tirex / univariate | 0.793 | 0.829 | 0.863 | 0.500 |
| tirex2 / multivariate | 0.597 | 0.868 | 0.754 | 0.386 |
| tirex2 / univariate | 0.778 | 0.982 | 0.628 | 0.345 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.410 | 0.378 | 0.358 | 0.390 |
| bvar / multivariate | 0.329 | 0.322 | 0.353 | 0.404 |
| chronos2 / multivariate | 0.367 | 0.353 | 0.334 | 0.386 |
| chronos2 / univariate | 0.380 | 0.368 | 0.352 | 0.448 |
| combo_bench / multivariate | 0.369 | 0.327 | 0.338 | 0.386 |
| combo_fm / univariate | 0.380 | 0.359 | 0.354 | 0.444 |
| dfm / multivariate | 0.577 | 0.440 | 0.444 | 0.488 |
| moirai2 / univariate | 0.385 | 0.373 | 0.369 | 0.451 |
| naive / univariate | 0.610 | 0.423 | 0.450 | 0.487 |
| timesfm25 / univariate | 0.386 | 0.352 | 0.357 | 0.437 |
| tirex / univariate | 0.420 | 0.373 | 0.364 | 0.453 |
| tirex2 / multivariate | 0.395 | 0.374 | 0.367 | 0.470 |
| tirex2 / univariate | 0.402 | 0.379 | 0.373 | 0.487 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.004 | 0.045 | 0.024 | 0.058 |
| bvar / multivariate | -0.011 | -0.002 | 0.041 | 0.064 |
| chronos2 / multivariate | 0.012 | 0.024 | -0.013 | -0.013 |
| chronos2 / univariate | 0.038 | 0.038 | 0.048 | 0.043 |
| combo_bench / multivariate | -0.009 | 0.070 | 0.068 | 0.100 |
| combo_fm / univariate | 0.042 | 0.046 | 0.039 | 0.062 |
| dfm / multivariate | -0.015 | 0.176 | 0.156 | 0.185 |
| moirai2 / univariate | 0.037 | 0.032 | 0.033 | 0.037 |
| naive / univariate | 0.019 | 0.159 | 0.160 | 0.186 |
| timesfm25 / univariate | 0.042 | 0.057 | 0.042 | 0.064 |
| tirex / univariate | 0.029 | 0.054 | 0.036 | 0.075 |
| tirex2 / multivariate | 0.047 | 0.035 | 0.016 | 0.072 |
| tirex2 / univariate | 0.067 | 0.049 | 0.034 | 0.092 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.232 | 0.221 | 0.211 | 0.225 |
| bvar / multivariate | 0.190 | 0.202 | 0.209 | 0.230 |
| chronos2 / multivariate | 0.194 | 0.192 | 0.183 | 0.203 |
| chronos2 / univariate | 0.202 | 0.208 | 0.188 | 0.222 |
| combo_bench / multivariate | 0.211 | 0.202 | 0.194 | 0.209 |
| combo_fm / univariate | 0.200 | 0.195 | 0.184 | 0.212 |
| dfm / multivariate | 0.341 | 0.267 | 0.255 | 0.271 |
| moirai2 / univariate | 0.207 | 0.209 | 0.199 | 0.225 |
| naive / univariate | 0.363 | 0.258 | 0.258 | 0.270 |
| timesfm25 / univariate | 0.206 | 0.194 | 0.187 | 0.213 |
| tirex / univariate | 0.219 | 0.201 | 0.188 | 0.214 |
| tirex2 / multivariate | 0.214 | 0.207 | 0.190 | 0.223 |
| tirex2 / univariate | 0.218 | 0.208 | 0.192 | 0.229 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.669 | 0.664 | 0.706 | 0.710 |
| bvar / multivariate | 0.796 | 0.736 | 0.787 | 0.740 |
| chronos2 / multivariate | 0.697 | 0.671 | 0.728 | 0.695 |
| chronos2 / univariate | 0.718 | 0.736 | 0.772 | 0.740 |
| combo_bench / multivariate | 0.800 | 0.761 | 0.843 | 0.829 |
| combo_fm / univariate | 0.754 | 0.786 | 0.816 | 0.809 |
| dfm / multivariate | 0.686 | 0.804 | 0.828 | 0.814 |
| moirai2 / univariate | 0.754 | 0.764 | 0.816 | 0.817 |
| naive / univariate | 0.704 | 0.800 | 0.816 | 0.824 |
| timesfm25 / univariate | 0.761 | 0.793 | 0.831 | 0.855 |
| tirex / univariate | 0.768 | 0.800 | 0.853 | 0.847 |
| tirex2 / multivariate | 0.725 | 0.729 | 0.750 | 0.733 |
| tirex2 / univariate | 0.711 | 0.736 | 0.765 | 0.740 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | yes | yes | yes | yes |
| bvar / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | no |  |  |  |
| chronos2 / univariate | yes | yes | yes | yes |
| chronos2 / univariate_levels | no |  |  |  |
| combo_bench / multivariate | yes | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | no | yes | no | no |
| moirai2 / univariate | yes | yes | yes | yes |
| moirai2 / univariate_levels | no |  |  |  |
| naive / univariate | no | yes | no | no |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | no |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | no |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

### EA / hicp_core


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 142 | 140 | 137 | 131 |
| bvar / multivariate | 142 | 140 | 137 | 131 |
| chronos2 / multivariate | 102 | 101 | 100 | 96 |
| chronos2 / univariate | 142 | 140 | 137 | 131 |
| combo_bench / multivariate | 140 | 138 | 135 | 129 |
| combo_fm / univariate | 142 | 140 | 137 | 131 |
| dfm / multivariate | 140 | 138 | 135 | 129 |
| moirai2 / univariate | 142 | 140 | 137 | 131 |
| naive / univariate | 142 | 140 | 137 | 131 |
| timesfm25 / univariate | 142 | 140 | 137 | 131 |
| tirex / univariate | 142 | 140 | 137 | 131 |
| tirex2 / multivariate | 102 | 101 | 100 | 96 |
| tirex2 / univariate | 142 | 140 | 137 | 131 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 1.401 | 1.430 | 1.500 | 1.524 |
| chronos2 / multivariate | 0.795 | 0.849 | 0.835 | 0.914 |
| chronos2 / univariate | 0.879 | 0.951 | 0.872 | 0.942 |
| combo_bench / multivariate | 1.377 | 1.340 | 1.292 | 1.235 |
| combo_fm / univariate | 0.841 | 0.863 | 0.845 | 0.924 |
| dfm / multivariate | 2.847 | 2.784 | 2.258 | 2.030 |
| moirai2 / univariate | 0.875 | 0.927 | 0.912 | 1.027 |
| naive / univariate | 2.760 | 2.684 | 2.264 | 2.032 |
| timesfm25 / univariate | 0.859 | 0.870 | 0.858 | 0.953 |
| tirex / univariate | 0.938 | 0.946 | 0.922 | 0.968 |
| tirex2 / multivariate | 0.873 | 0.863 | 0.857 | 0.882 |
| tirex2 / univariate | 0.865 | 0.851 | 0.837 | 0.916 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 1.673 | 1.668 | 1.686 | 1.696 |
| chronos2 / multivariate | 0.837 | 0.851 | 0.820 | 0.863 |
| chronos2 / univariate | 0.914 | 1.000 | 0.869 | 0.914 |
| combo_bench / multivariate | 1.571 | 1.475 | 1.414 | 1.336 |
| combo_fm / univariate | 0.844 | 0.879 | 0.846 | 0.904 |
| dfm / multivariate | 3.046 | 2.891 | 2.264 | 2.094 |
| moirai2 / univariate | 0.962 | 0.965 | 0.917 | 1.030 |
| naive / univariate | 2.917 | 2.795 | 2.258 | 2.098 |
| timesfm25 / univariate | 0.889 | 0.909 | 0.879 | 0.939 |
| tirex / univariate | 0.968 | 0.970 | 0.939 | 0.948 |
| tirex2 / multivariate | 0.874 | 0.855 | 0.854 | 0.886 |
| tirex2 / univariate | 0.880 | 0.870 | 0.835 | 0.910 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.000 | 0.000 | 0.000 | 0.000 |
| chronos2 / multivariate | 0.001 | 0.017 | 0.033 | 0.425 |
| chronos2 / univariate | 0.010 | 0.388 | 0.026 | 0.442 |
| combo_bench / multivariate | 0.002 | 0.008 | 0.027 | 0.003 |
| combo_fm / univariate | 0.000 | 0.011 | 0.004 | 0.226 |
| dfm / multivariate | 0.000 | 0.000 | 0.000 | 0.000 |
| moirai2 / univariate | 0.016 | 0.224 | 0.118 | 0.721 |
| naive / univariate | 0.000 | 0.000 | 0.000 | 0.000 |
| timesfm25 / univariate | 0.001 | 0.022 | 0.022 | 0.501 |
| tirex / univariate | 0.123 | 0.292 | 0.091 | 0.599 |
| tirex2 / multivariate | 0.010 | 0.031 | 0.073 | 0.134 |
| tirex2 / univariate | 0.002 | 0.024 | 0.011 | 0.182 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.281 | 0.257 | 0.273 | 0.244 |
| bvar / multivariate | 0.393 | 0.367 | 0.409 | 0.372 |
| chronos2 / multivariate | 0.215 | 0.233 | 0.218 | 0.223 |
| chronos2 / univariate | 0.247 | 0.245 | 0.238 | 0.230 |
| combo_bench / multivariate | 0.387 | 0.342 | 0.350 | 0.298 |
| combo_fm / univariate | 0.236 | 0.222 | 0.230 | 0.226 |
| dfm / multivariate | 0.800 | 0.711 | 0.612 | 0.490 |
| moirai2 / univariate | 0.246 | 0.238 | 0.249 | 0.251 |
| naive / univariate | 0.775 | 0.690 | 0.617 | 0.496 |
| timesfm25 / univariate | 0.241 | 0.224 | 0.234 | 0.233 |
| tirex / univariate | 0.263 | 0.243 | 0.251 | 0.237 |
| tirex2 / multivariate | 0.236 | 0.237 | 0.224 | 0.215 |
| tirex2 / univariate | 0.243 | 0.219 | 0.228 | 0.224 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.004 | -0.009 | -0.008 | 0.052 |
| bvar / multivariate | 0.007 | 0.028 | 0.024 | 0.114 |
| chronos2 / multivariate | 0.009 | -0.016 | -0.008 | -0.013 |
| chronos2 / univariate | -0.004 | -0.025 | -0.000 | -0.005 |
| combo_bench / multivariate | -0.046 | 0.030 | 0.026 | 0.114 |
| combo_fm / univariate | 0.011 | 0.002 | 0.004 | 0.010 |
| dfm / multivariate | -0.147 | 0.075 | 0.072 | 0.183 |
| moirai2 / univariate | 0.009 | 0.007 | -0.022 | -0.014 |
| naive / univariate | -0.105 | 0.098 | 0.096 | 0.195 |
| timesfm25 / univariate | 0.017 | -0.007 | 0.001 | -0.001 |
| tirex / univariate | 0.029 | 0.011 | 0.024 | 0.021 |
| tirex2 / multivariate | 0.007 | 0.023 | 0.007 | 0.034 |
| tirex2 / univariate | 0.003 | 0.024 | 0.019 | 0.051 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.163 | 0.149 | 0.160 | 0.149 |
| bvar / multivariate | 0.254 | 0.231 | 0.256 | 0.235 |
| chronos2 / multivariate | 0.126 | 0.137 | 0.130 | 0.127 |
| chronos2 / univariate | 0.148 | 0.147 | 0.140 | 0.135 |
| combo_bench / multivariate | 0.239 | 0.212 | 0.215 | 0.189 |
| combo_fm / univariate | 0.137 | 0.130 | 0.133 | 0.133 |
| dfm / multivariate | 0.482 | 0.432 | 0.362 | 0.305 |
| moirai2 / univariate | 0.150 | 0.142 | 0.147 | 0.154 |
| naive / univariate | 0.467 | 0.418 | 0.364 | 0.305 |
| timesfm25 / univariate | 0.141 | 0.132 | 0.137 | 0.138 |
| tirex / univariate | 0.151 | 0.143 | 0.147 | 0.139 |
| tirex2 / multivariate | 0.132 | 0.138 | 0.135 | 0.127 |
| tirex2 / univariate | 0.141 | 0.129 | 0.134 | 0.134 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.683 | 0.671 | 0.664 | 0.672 |
| bvar / multivariate | 0.627 | 0.771 | 0.723 | 0.802 |
| chronos2 / multivariate | 0.755 | 0.713 | 0.710 | 0.812 |
| chronos2 / univariate | 0.725 | 0.743 | 0.715 | 0.794 |
| combo_bench / multivariate | 0.786 | 0.841 | 0.859 | 0.899 |
| combo_fm / univariate | 0.746 | 0.807 | 0.774 | 0.802 |
| dfm / multivariate | 0.700 | 0.739 | 0.815 | 0.899 |
| moirai2 / univariate | 0.697 | 0.764 | 0.715 | 0.679 |
| naive / univariate | 0.704 | 0.743 | 0.796 | 0.870 |
| timesfm25 / univariate | 0.768 | 0.793 | 0.715 | 0.786 |
| tirex / univariate | 0.718 | 0.743 | 0.759 | 0.779 |
| tirex2 / multivariate | 0.794 | 0.752 | 0.690 | 0.740 |
| tirex2 / univariate | 0.732 | 0.771 | 0.745 | 0.771 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | no | yes | yes | yes |
| bvar / multivariate | no | no | no | no |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | no |  |  |  |
| chronos2 / univariate | yes | yes | yes | yes |
| chronos2 / univariate_levels | no |  |  |  |
| combo_bench / multivariate | no | no | no | no |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | no | no | no | no |
| moirai2 / univariate | yes | yes | yes | no |
| moirai2 / univariate_levels | no |  |  |  |
| naive / univariate | no | no | no | no |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | no |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | no |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

### EA / retail


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 142 | 141 | 138 | 132 |
| bvar / multivariate | 142 | 141 | 138 | 132 |
| chronos2 / multivariate | 142 | 141 | 138 | 132 |
| chronos2 / univariate | 142 | 141 | 138 | 132 |
| combo_bench / multivariate | 140 | 139 | 136 | 130 |
| combo_fm / univariate | 142 | 141 | 138 | 132 |
| dfm / multivariate | 140 | 139 | 136 | 130 |
| moirai2 / univariate | 142 | 141 | 138 | 132 |
| naive / univariate | 142 | 141 | 138 | 132 |
| timesfm25 / univariate | 142 | 141 | 138 | 132 |
| tirex / univariate | 142 | 141 | 138 | 132 |
| tirex2 / multivariate | 142 | 141 | 138 | 132 |
| tirex2 / univariate | 142 | 141 | 138 | 132 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.548 | 1.092 | 0.948 | 0.959 |
| chronos2 / multivariate | 0.891 | 1.116 | 1.057 | 0.976 |
| chronos2 / univariate | 1.111 | 1.277 | 1.178 | 1.134 |
| combo_bench / multivariate | 0.712 | 1.020 | 0.952 | 0.965 |
| combo_fm / univariate | 1.033 | 1.116 | 1.052 | 0.973 |
| dfm / multivariate | 0.727 | 1.036 | 0.938 | 0.956 |
| moirai2 / univariate | 1.051 | 1.140 | 1.105 | 1.015 |
| naive / univariate | 0.768 | 1.010 | 0.931 | 0.954 |
| timesfm25 / univariate | 0.987 | 1.057 | 0.981 | 0.943 |
| tirex / univariate | 1.035 | 1.110 | 1.075 | 0.960 |
| tirex2 / multivariate | 0.852 | 1.011 | 0.937 | 0.954 |
| tirex2 / univariate | 1.012 | 1.065 | 0.989 | 0.944 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.764 | 1.187 | 0.913 | 0.921 |
| chronos2 / multivariate | 0.860 | 1.113 | 0.984 | 0.914 |
| chronos2 / univariate | 0.943 | 1.218 | 1.068 | 1.043 |
| combo_bench / multivariate | 0.798 | 1.024 | 0.920 | 0.925 |
| combo_fm / univariate | 0.924 | 1.126 | 0.980 | 0.919 |
| dfm / multivariate | 0.802 | 1.052 | 0.883 | 0.901 |
| moirai2 / univariate | 0.947 | 1.143 | 1.011 | 0.952 |
| naive / univariate | 0.827 | 1.000 | 0.876 | 0.892 |
| timesfm25 / univariate | 0.917 | 1.079 | 0.941 | 0.867 |
| tirex / univariate | 0.930 | 1.139 | 1.005 | 0.907 |
| tirex2 / multivariate | 0.849 | 1.001 | 0.887 | 0.889 |
| tirex2 / univariate | 0.923 | 1.085 | 0.947 | 0.856 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.035 | 0.010 | 0.145 | 0.214 |
| chronos2 / multivariate | 0.209 | 0.220 | 0.595 | 0.293 |
| chronos2 / univariate | 0.597 | 0.204 | 0.412 | 0.377 |
| combo_bench / multivariate | 0.021 | 0.224 | 0.101 | 0.193 |
| combo_fm / univariate | 0.840 | 0.178 | 0.607 | 0.292 |
| dfm / multivariate | 0.037 | 0.204 | 0.097 | 0.205 |
| moirai2 / univariate | 0.785 | 0.208 | 0.488 | 0.711 |
| naive / univariate | 0.036 | 0.747 | 0.077 | 0.189 |
| timesfm25 / univariate | 0.917 | 0.197 | 0.654 | 0.208 |
| tirex / univariate | 0.821 | 0.169 | 0.521 | 0.226 |
| tirex2 / multivariate | 0.115 | 0.723 | 0.086 | 0.205 |
| tirex2 / univariate | 0.931 | 0.227 | 0.837 | 0.213 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 3.582 | 2.397 | 2.594 | 2.611 |
| bvar / multivariate | 1.962 | 2.618 | 2.459 | 2.504 |
| chronos2 / multivariate | 3.191 | 2.675 | 2.742 | 2.548 |
| chronos2 / univariate | 3.978 | 3.060 | 3.056 | 2.960 |
| combo_bench / multivariate | 2.560 | 2.460 | 2.457 | 2.531 |
| combo_fm / univariate | 3.699 | 2.675 | 2.729 | 2.541 |
| dfm / multivariate | 2.614 | 2.499 | 2.423 | 2.507 |
| moirai2 / univariate | 3.764 | 2.733 | 2.865 | 2.651 |
| naive / univariate | 2.751 | 2.420 | 2.416 | 2.490 |
| timesfm25 / univariate | 3.535 | 2.532 | 2.545 | 2.461 |
| tirex / univariate | 3.707 | 2.659 | 2.788 | 2.506 |
| tirex2 / multivariate | 3.052 | 2.423 | 2.430 | 2.490 |
| tirex2 / univariate | 3.624 | 2.551 | 2.566 | 2.465 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.068 | -0.090 | -0.148 | -0.317 |
| bvar / multivariate | -0.140 | -0.019 | -0.209 | -0.237 |
| chronos2 / multivariate | 0.028 | 0.058 | -0.054 | -0.140 |
| chronos2 / univariate | 0.175 | 0.151 | 0.052 | -0.008 |
| combo_bench / multivariate | -0.000 | -0.050 | -0.141 | -0.260 |
| combo_fm / univariate | 0.108 | 0.063 | -0.041 | -0.140 |
| dfm / multivariate | 0.080 | -0.058 | -0.125 | -0.245 |
| moirai2 / univariate | 0.144 | 0.079 | 0.011 | -0.086 |
| naive / univariate | 0.048 | -0.069 | -0.157 | -0.252 |
| timesfm25 / univariate | 0.102 | 0.005 | -0.120 | -0.244 |
| tirex / univariate | 0.020 | 0.091 | -0.041 | -0.122 |
| tirex2 / multivariate | 0.020 | -0.086 | -0.171 | -0.278 |
| tirex2 / univariate | 0.099 | -0.009 | -0.110 | -0.243 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 1.255 | 0.953 | 1.107 | 1.152 |
| bvar / multivariate | 0.866 | 1.102 | 1.038 | 1.094 |
| chronos2 / multivariate | 0.995 | 0.953 | 1.011 | 1.021 |
| chronos2 / univariate | 1.084 | 1.080 | 1.135 | 1.166 |
| combo_bench / multivariate | 0.961 | 0.983 | 1.018 | 1.094 |
| combo_fm / univariate | 1.044 | 0.983 | 1.027 | 1.021 |
| dfm / multivariate | 0.977 | 1.013 | 0.998 | 1.072 |
| moirai2 / univariate | 1.095 | 1.011 | 1.064 | 1.038 |
| naive / univariate | 1.042 | 0.970 | 0.994 | 1.057 |
| timesfm25 / univariate | 1.094 | 0.970 | 0.997 | 0.981 |
| tirex / univariate | 1.043 | 0.985 | 1.052 | 1.043 |
| tirex2 / multivariate | 1.009 | 0.931 | 0.967 | 0.997 |
| tirex2 / univariate | 1.064 | 0.961 | 1.003 | 0.999 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.817 | 0.809 | 0.783 | 0.758 |
| bvar / multivariate | 0.754 | 0.773 | 0.812 | 0.780 |
| chronos2 / multivariate | 0.831 | 0.801 | 0.790 | 0.780 |
| chronos2 / univariate | 0.803 | 0.794 | 0.783 | 0.742 |
| combo_bench / multivariate | 0.821 | 0.791 | 0.824 | 0.777 |
| combo_fm / univariate | 0.817 | 0.794 | 0.797 | 0.803 |
| dfm / multivariate | 0.829 | 0.777 | 0.801 | 0.777 |
| moirai2 / univariate | 0.796 | 0.787 | 0.790 | 0.765 |
| naive / univariate | 0.838 | 0.823 | 0.812 | 0.780 |
| timesfm25 / univariate | 0.796 | 0.787 | 0.768 | 0.788 |
| tirex / univariate | 0.845 | 0.809 | 0.833 | 0.818 |
| tirex2 / multivariate | 0.789 | 0.809 | 0.768 | 0.780 |
| tirex2 / univariate | 0.746 | 0.780 | 0.761 | 0.780 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | yes | yes | yes | yes |
| bvar / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |  |
| chronos2 / univariate | yes | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |  |
| combo_bench / multivariate | yes | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | yes | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes | yes |
| moirai2 / univariate_levels | yes |  |  |  |
| naive / univariate | yes | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

### EA / unemp


**Scored forecasts (n)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 133 | 131 | 126 | 114 |
| bvar / multivariate | 133 | 131 | 126 | 114 |
| chronos2 / multivariate | 133 | 131 | 126 | 114 |
| chronos2 / univariate | 133 | 131 | 126 | 114 |
| combo_bench / multivariate | 133 | 131 | 126 | 114 |
| combo_fm / univariate | 133 | 131 | 126 | 114 |
| dfm / multivariate | 133 | 131 | 126 | 114 |
| moirai2 / univariate | 133 | 131 | 126 | 114 |
| naive / univariate | 133 | 131 | 126 | 114 |
| timesfm25 / univariate | 133 | 131 | 126 | 114 |
| tirex / univariate | 133 | 131 | 126 | 114 |
| tirex2 / multivariate | 133 | 131 | 126 | 114 |
| tirex2 / univariate | 133 | 131 | 126 | 114 |

**Relative RMSFE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 1.051 | 0.883 | 1.026 | 0.993 |
| chronos2 / multivariate | 0.965 | 0.998 | 1.006 | 0.999 |
| chronos2 / univariate | 0.949 | 0.981 | 1.010 | 1.076 |
| combo_bench / multivariate | 1.001 | 0.916 | 0.992 | 0.977 |
| combo_fm / univariate | 0.947 | 0.946 | 0.942 | 0.991 |
| dfm / multivariate | 1.067 | 0.961 | 1.021 | 0.967 |
| moirai2 / univariate | 0.968 | 0.955 | 0.940 | 0.987 |
| naive / univariate | 1.075 | 1.009 | 0.973 | 0.945 |
| timesfm25 / univariate | 0.951 | 0.924 | 0.922 | 0.987 |
| tirex / univariate | 0.948 | 0.946 | 0.930 | 0.972 |
| tirex2 / multivariate | 0.938 | 0.952 | 0.952 | 0.990 |
| tirex2 / univariate | 0.935 | 0.946 | 0.930 | 0.969 |

**Relative MAE to AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 1.013 | 0.919 | 0.964 | 1.020 |
| chronos2 / multivariate | 0.930 | 0.985 | 1.060 | 1.068 |
| chronos2 / univariate | 0.979 | 0.967 | 1.036 | 1.111 |
| combo_bench / multivariate | 0.982 | 0.927 | 0.947 | 0.968 |
| combo_fm / univariate | 0.975 | 0.960 | 0.994 | 1.069 |
| dfm / multivariate | 1.066 | 0.963 | 0.950 | 0.957 |
| moirai2 / univariate | 0.991 | 0.967 | 0.998 | 1.056 |
| naive / univariate | 0.980 | 0.999 | 0.917 | 0.940 |
| timesfm25 / univariate | 0.977 | 0.940 | 0.991 | 1.072 |
| tirex / univariate | 0.975 | 0.956 | 0.984 | 1.056 |
| tirex2 / multivariate | 0.952 | 0.970 | 0.999 | 1.077 |
| tirex2 / univariate | 0.955 | 0.971 | 0.982 | 1.063 |

**Diebold-Mariano p-value vs AR**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| bvar / multivariate | 0.269 | 0.088 | 0.722 | 0.821 |
| chronos2 / multivariate | 0.248 | 0.969 | 0.921 | 0.987 |
| chronos2 / univariate | 0.053 | 0.639 | 0.749 | 0.185 |
| combo_bench / multivariate | 0.960 | 0.076 | 0.825 | 0.328 |
| combo_fm / univariate | 0.052 | 0.123 | 0.320 | 0.871 |
| dfm / multivariate | 0.038 | 0.540 | 0.697 | 0.490 |
| moirai2 / univariate | 0.234 | 0.238 | 0.349 | 0.847 |
| naive / univariate | 0.158 | 0.912 | 0.752 | 0.364 |
| timesfm25 / univariate | 0.120 | 0.094 | 0.328 | 0.860 |
| tirex / univariate | 0.083 | 0.147 | 0.264 | 0.620 |
| tirex2 / multivariate | 0.016 | 0.078 | 0.356 | 0.843 |
| tirex2 / univariate | 0.019 | 0.091 | 0.285 | 0.641 |

**RMSFE (transformed units)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.083 | 0.091 | 0.089 | 0.096 |
| bvar / multivariate | 0.087 | 0.080 | 0.092 | 0.096 |
| chronos2 / multivariate | 0.080 | 0.091 | 0.090 | 0.096 |
| chronos2 / univariate | 0.079 | 0.089 | 0.090 | 0.104 |
| combo_bench / multivariate | 0.083 | 0.083 | 0.089 | 0.094 |
| combo_fm / univariate | 0.079 | 0.086 | 0.084 | 0.096 |
| dfm / multivariate | 0.089 | 0.088 | 0.091 | 0.093 |
| moirai2 / univariate | 0.080 | 0.087 | 0.084 | 0.095 |
| naive / univariate | 0.089 | 0.092 | 0.087 | 0.091 |
| timesfm25 / univariate | 0.079 | 0.084 | 0.082 | 0.095 |
| tirex / univariate | 0.079 | 0.086 | 0.083 | 0.094 |
| tirex2 / multivariate | 0.078 | 0.087 | 0.085 | 0.096 |
| tirex2 / univariate | 0.078 | 0.086 | 0.083 | 0.094 |

**Mean error (outturn minus forecast)**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | -0.013 | -0.023 | -0.019 | -0.036 |
| bvar / multivariate | -0.013 | -0.022 | -0.026 | -0.039 |
| chronos2 / multivariate | -0.001 | -0.006 | -0.002 | -0.004 |
| chronos2 / univariate | -0.003 | -0.008 | -0.003 | -0.012 |
| combo_bench / multivariate | -0.016 | -0.027 | -0.026 | -0.039 |
| combo_fm / univariate | -0.002 | -0.005 | 0.002 | -0.005 |
| dfm / multivariate | -0.021 | -0.038 | -0.035 | -0.042 |
| moirai2 / univariate | -0.001 | -0.004 | 0.004 | -0.003 |
| naive / univariate | -0.033 | -0.038 | -0.031 | -0.039 |
| timesfm25 / univariate | 0.000 | -0.002 | 0.006 | 0.003 |
| tirex / univariate | -0.001 | -0.005 | 0.001 | -0.008 |
| tirex2 / multivariate | -0.004 | -0.008 | -0.001 | -0.008 |
| tirex2 / univariate | -0.003 | -0.007 | 0.001 | -0.006 |

**Weighted quantile loss**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.052 | 0.053 | 0.052 | 0.058 |
| bvar / multivariate | 0.055 | 0.049 | 0.052 | 0.058 |
| chronos2 / multivariate | 0.050 | 0.054 | 0.055 | 0.059 |
| chronos2 / univariate | 0.051 | 0.051 | 0.053 | 0.061 |
| combo_bench / multivariate | 0.052 | 0.050 | 0.052 | 0.057 |
| combo_fm / univariate | 0.050 | 0.050 | 0.050 | 0.058 |
| dfm / multivariate | 0.057 | 0.054 | 0.055 | 0.057 |
| moirai2 / univariate | 0.052 | 0.051 | 0.050 | 0.058 |
| naive / univariate | 0.055 | 0.056 | 0.052 | 0.056 |
| timesfm25 / univariate | 0.050 | 0.049 | 0.050 | 0.058 |
| tirex / univariate | 0.050 | 0.050 | 0.049 | 0.057 |
| tirex2 / multivariate | 0.050 | 0.051 | 0.051 | 0.058 |
| tirex2 / univariate | 0.050 | 0.051 | 0.050 | 0.057 |

**80% interval coverage**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | 0.647 | 0.847 | 0.825 | 0.860 |
| bvar / multivariate | 0.564 | 0.756 | 0.817 | 0.825 |
| chronos2 / multivariate | 0.564 | 0.641 | 0.675 | 0.728 |
| chronos2 / univariate | 0.564 | 0.718 | 0.730 | 0.772 |
| combo_bench / multivariate | 0.602 | 0.779 | 0.810 | 0.816 |
| combo_fm / univariate | 0.594 | 0.740 | 0.802 | 0.816 |
| dfm / multivariate | 0.594 | 0.710 | 0.722 | 0.649 |
| moirai2 / univariate | 0.564 | 0.710 | 0.778 | 0.763 |
| naive / univariate | 0.872 | 0.878 | 0.913 | 0.868 |
| timesfm25 / univariate | 0.617 | 0.794 | 0.833 | 0.754 |
| tirex / univariate | 0.609 | 0.771 | 0.841 | 0.833 |
| tirex2 / multivariate | 0.549 | 0.710 | 0.786 | 0.798 |
| tirex2 / univariate | 0.571 | 0.710 | 0.786 | 0.825 |

**Model confidence set (90%) membership**

| model / variant | h1 | h3 | h6 | h12 |
|---|---|---|---|---|
| ar / univariate | yes | yes | yes | yes |
| bvar / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate | yes | yes | yes | yes |
| chronos2 / multivariate_levels | yes |  |  |  |
| chronos2 / univariate | yes | yes | yes | yes |
| chronos2 / univariate_levels | yes |  |  |  |
| combo_bench / multivariate | yes | yes | yes | yes |
| combo_fm / univariate | yes | yes | yes | yes |
| dfm / multivariate | yes | yes | yes | yes |
| moirai2 / univariate | yes | yes | yes | yes |
| moirai2 / univariate_levels | no |  |  |  |
| naive / univariate | yes | yes | yes | yes |
| timesfm25 / univariate | yes | yes | yes | yes |
| timesfm25 / univariate_levels | yes |  |  |  |
| tirex / univariate | yes | yes | yes | yes |
| tirex / univariate_levels | yes |  |  |  |
| tirex2 / multivariate | yes | yes | yes | yes |
| tirex2 / multivariate_levels | yes |  |  |  |
| tirex2 / univariate | yes | yes | yes | yes |
| tirex2 / univariate_levels | yes |  |  |  |

## 5. Views by plan question (relative RMSFE to AR unless stated)


### 5.1 Q1: real-time versus revised input (first-release outturn)

| econ | target | horizon | model | variant | rel_rmsfe:realtime | rel_rmsfe:revised | n:realtime | n:revised |
|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | bvar | multivariate | 1.049 | 1.261 | 138 | 140 |
| CA | consumption | 1 | chronos2 | multivariate | 1.138 | 1.115 | 94 | 94 |
| CA | consumption | 1 | chronos2 | univariate | 1.323 | 1.367 | 140 | 140 |
| CA | consumption | 1 | combo_bench | multivariate | 0.862 | 0.900 | 135 | 137 |
| CA | consumption | 1 | combo_fm | univariate | 1.016 | 1.014 | 140 | 140 |
| CA | consumption | 1 | dfm | multivariate | 0.569 | 0.551 | 137 | 137 |
| CA | consumption | 1 | moirai2 | univariate | 1.036 | 1.054 | 140 | 140 |
| CA | consumption | 1 | naive | univariate | 0.815 | 0.823 | 140 | 140 |
| CA | consumption | 1 | timesfm25 | univariate | 0.961 | 0.945 | 140 | 140 |
| CA | consumption | 1 | tirex | univariate | 0.959 | 0.923 | 140 | 140 |
| CA | consumption | 1 | tirex2 | multivariate | 0.934 | 0.924 | 94 | 94 |
| CA | consumption | 1 | tirex2 | univariate | 0.846 | 0.845 | 140 | 140 |
| CA | consumption | 2 | bvar | multivariate | 1.150 | 1.266 | 135 | 137 |
| CA | consumption | 2 | chronos2 | multivariate | 1.045 | 1.017 | 92 | 92 |
| CA | consumption | 2 | chronos2 | univariate | 1.208 | 1.205 | 137 | 137 |
| CA | consumption | 2 | combo_bench | multivariate | 1.010 | 1.027 | 132 | 134 |
| CA | consumption | 2 | combo_fm | univariate | 1.010 | 1.007 | 137 | 137 |
| CA | consumption | 2 | dfm | multivariate | 0.967 | 0.965 | 134 | 134 |
| CA | consumption | 2 | moirai2 | univariate | 1.002 | 1.002 | 137 | 137 |
| CA | consumption | 2 | naive | univariate | 0.981 | 0.982 | 137 | 137 |
| CA | consumption | 2 | timesfm25 | univariate | 1.000 | 0.995 | 137 | 137 |
| CA | consumption | 2 | tirex | univariate | 0.983 | 0.985 | 137 | 137 |
| CA | consumption | 2 | tirex2 | multivariate | 0.993 | 0.992 | 92 | 92 |
| CA | consumption | 2 | tirex2 | univariate | 0.987 | 0.987 | 137 | 137 |
| CA | consumption | 4 | bvar | multivariate | 1.239 | 1.324 | 129 | 131 |
| CA | consumption | 4 | chronos2 | multivariate | 1.009 | 1.005 | 88 | 88 |
| CA | consumption | 4 | chronos2 | univariate | 1.118 | 1.115 | 131 | 131 |
| CA | consumption | 4 | combo_bench | multivariate | 1.014 | 1.034 | 126 | 128 |
| CA | consumption | 4 | combo_fm | univariate | 1.007 | 1.007 | 131 | 131 |
| CA | consumption | 4 | dfm | multivariate | 1.001 | 1.002 | 128 | 128 |
| CA | consumption | 4 | moirai2 | univariate | 1.005 | 1.005 | 131 | 131 |
| CA | consumption | 4 | naive | univariate | 1.004 | 1.004 | 131 | 131 |
| CA | consumption | 4 | timesfm25 | univariate | 1.000 | 1.000 | 131 | 131 |
| CA | consumption | 4 | tirex | univariate | 1.001 | 1.002 | 131 | 131 |
| CA | consumption | 4 | tirex2 | multivariate | 1.000 | 1.000 | 88 | 88 |
| CA | consumption | 4 | tirex2 | univariate | 0.994 | 0.995 | 131 | 131 |
| CA | cpi | 1 | bvar | multivariate | 0.976 |  | 141 |  |
| CA | cpi | 1 | chronos2 | multivariate | 0.844 |  | 142 |  |
| CA | cpi | 1 | chronos2 | univariate | 0.862 |  | 142 |  |
| CA | cpi | 1 | combo_bench | multivariate | 0.975 |  | 138 |  |
| CA | cpi | 1 | combo_fm | univariate | 0.856 |  | 142 |  |
| CA | cpi | 1 | dfm | multivariate | 0.988 |  | 139 |  |
| CA | cpi | 1 | moirai2 | univariate | 0.863 |  | 142 |  |
| CA | cpi | 1 | naive | univariate | 1.012 |  | 142 |  |
| CA | cpi | 1 | timesfm25 | univariate | 0.878 |  | 142 |  |
| CA | cpi | 1 | tirex | univariate | 0.886 |  | 142 |  |
| CA | cpi | 1 | tirex2 | multivariate | 0.856 |  | 142 |  |
| CA | cpi | 1 | tirex2 | univariate | 0.854 |  | 142 |  |
| CA | cpi | 3 | bvar | multivariate | 1.003 |  | 139 |  |
| CA | cpi | 3 | chronos2 | multivariate | 0.846 |  | 140 |  |
| CA | cpi | 3 | chronos2 | univariate | 0.822 |  | 140 |  |
| CA | cpi | 3 | combo_bench | multivariate | 1.000 |  | 136 |  |
| CA | cpi | 3 | combo_fm | univariate | 0.818 |  | 140 |  |
| CA | cpi | 3 | dfm | multivariate | 1.001 |  | 137 |  |
| CA | cpi | 3 | moirai2 | univariate | 0.840 |  | 140 |  |
| CA | cpi | 3 | naive | univariate | 0.998 |  | 140 |  |
| CA | cpi | 3 | timesfm25 | univariate | 0.814 |  | 140 |  |
| CA | cpi | 3 | tirex | univariate | 0.829 |  | 140 |  |
| CA | cpi | 3 | tirex2 | multivariate | 0.843 |  | 140 |  |
| CA | cpi | 3 | tirex2 | univariate | 0.831 |  | 140 |  |
| CA | cpi | 6 | bvar | multivariate | 1.014 |  | 136 |  |
| CA | cpi | 6 | chronos2 | multivariate | 0.895 |  | 137 |  |
| CA | cpi | 6 | chronos2 | univariate | 0.862 |  | 137 |  |
| CA | cpi | 6 | combo_bench | multivariate | 1.007 |  | 133 |  |
| CA | cpi | 6 | combo_fm | univariate | 0.851 |  | 137 |  |
| CA | cpi | 6 | dfm | multivariate | 1.011 |  | 134 |  |
| CA | cpi | 6 | moirai2 | univariate | 0.870 |  | 137 |  |
| CA | cpi | 6 | naive | univariate | 1.010 |  | 137 |  |
| CA | cpi | 6 | timesfm25 | univariate | 0.846 |  | 137 |  |
| CA | cpi | 6 | tirex | univariate | 0.852 |  | 137 |  |
| CA | cpi | 6 | tirex2 | multivariate | 0.883 |  | 137 |  |
| CA | cpi | 6 | tirex2 | univariate | 0.872 |  | 137 |  |
| CA | cpi | 12 | bvar | multivariate | 1.107 |  | 130 |  |
| CA | cpi | 12 | chronos2 | multivariate | 0.917 |  | 131 |  |
| CA | cpi | 12 | chronos2 | univariate | 0.891 |  | 131 |  |
| CA | cpi | 12 | combo_bench | multivariate | 1.060 |  | 127 |  |
| CA | cpi | 12 | combo_fm | univariate | 0.874 |  | 131 |  |
| CA | cpi | 12 | dfm | multivariate | 1.103 |  | 128 |  |
| CA | cpi | 12 | moirai2 | univariate | 0.892 |  | 131 |  |
| CA | cpi | 12 | naive | univariate | 1.104 |  | 131 |  |
| CA | cpi | 12 | timesfm25 | univariate | 0.874 |  | 131 |  |
| CA | cpi | 12 | tirex | univariate | 0.884 |  | 131 |  |
| CA | cpi | 12 | tirex2 | multivariate | 0.902 |  | 131 |  |
| CA | cpi | 12 | tirex2 | univariate | 0.888 |  | 131 |  |
| CA | cpi_core | 1 | bvar | multivariate | 1.223 |  | 141 |  |
| CA | cpi_core | 1 | chronos2 | multivariate | 0.999 |  | 142 |  |
| CA | cpi_core | 1 | chronos2 | univariate | 1.030 |  | 142 |  |
| CA | cpi_core | 1 | combo_bench | multivariate | 1.066 |  | 138 |  |
| CA | cpi_core | 1 | combo_fm | univariate | 0.967 |  | 142 |  |
| CA | cpi_core | 1 | dfm | multivariate | 1.179 |  | 139 |  |
| CA | cpi_core | 1 | moirai2 | univariate | 1.002 |  | 142 |  |
| CA | cpi_core | 1 | naive | univariate | 1.172 |  | 142 |  |
| CA | cpi_core | 1 | timesfm25 | univariate | 0.976 |  | 142 |  |
| CA | cpi_core | 1 | tirex | univariate | 0.959 |  | 142 |  |
| CA | cpi_core | 1 | tirex2 | multivariate | 0.950 |  | 142 |  |
| CA | cpi_core | 1 | tirex2 | univariate | 0.948 |  | 142 |  |
| CA | cpi_core | 3 | bvar | multivariate | 1.289 |  | 139 |  |
| CA | cpi_core | 3 | chronos2 | multivariate | 1.021 |  | 140 |  |
| CA | cpi_core | 3 | chronos2 | univariate | 1.046 |  | 140 |  |
| CA | cpi_core | 3 | combo_bench | multivariate | 1.129 |  | 136 |  |
| CA | cpi_core | 3 | combo_fm | univariate | 0.974 |  | 140 |  |
| CA | cpi_core | 3 | dfm | multivariate | 1.271 |  | 137 |  |
| CA | cpi_core | 3 | moirai2 | univariate | 0.999 |  | 140 |  |
| CA | cpi_core | 3 | naive | univariate | 1.268 |  | 140 |  |
| CA | cpi_core | 3 | timesfm25 | univariate | 0.961 |  | 140 |  |
| CA | cpi_core | 3 | tirex | univariate | 0.983 |  | 140 |  |
| CA | cpi_core | 3 | tirex2 | multivariate | 0.960 |  | 140 |  |
| CA | cpi_core | 3 | tirex2 | univariate | 0.950 |  | 140 |  |
| CA | cpi_core | 6 | bvar | multivariate | 1.255 |  | 136 |  |
| CA | cpi_core | 6 | chronos2 | multivariate | 1.059 |  | 137 |  |
| CA | cpi_core | 6 | chronos2 | univariate | 1.040 |  | 137 |  |
| CA | cpi_core | 6 | combo_bench | multivariate | 1.102 |  | 133 |  |
| CA | cpi_core | 6 | combo_fm | univariate | 0.963 |  | 137 |  |
| CA | cpi_core | 6 | dfm | multivariate | 1.237 |  | 134 |  |
| CA | cpi_core | 6 | moirai2 | univariate | 0.968 |  | 137 |  |
| CA | cpi_core | 6 | naive | univariate | 1.237 |  | 137 |  |
| CA | cpi_core | 6 | timesfm25 | univariate | 0.960 |  | 137 |  |
| CA | cpi_core | 6 | tirex | univariate | 0.970 |  | 137 |  |
| CA | cpi_core | 6 | tirex2 | multivariate | 0.992 |  | 137 |  |
| CA | cpi_core | 6 | tirex2 | univariate | 0.957 |  | 137 |  |
| CA | cpi_core | 12 | bvar | multivariate | 1.326 |  | 130 |  |
| CA | cpi_core | 12 | chronos2 | multivariate | 1.047 |  | 131 |  |
| CA | cpi_core | 12 | chronos2 | univariate | 0.995 |  | 131 |  |
| CA | cpi_core | 12 | combo_bench | multivariate | 1.135 |  | 127 |  |
| CA | cpi_core | 12 | combo_fm | univariate | 0.960 |  | 131 |  |
| CA | cpi_core | 12 | dfm | multivariate | 1.282 |  | 128 |  |
| CA | cpi_core | 12 | moirai2 | univariate | 0.990 |  | 131 |  |
| CA | cpi_core | 12 | naive | univariate | 1.316 |  | 131 |  |
| CA | cpi_core | 12 | timesfm25 | univariate | 0.958 |  | 131 |  |
| CA | cpi_core | 12 | tirex | univariate | 0.952 |  | 131 |  |
| CA | cpi_core | 12 | tirex2 | multivariate | 0.975 |  | 131 |  |
| CA | cpi_core | 12 | tirex2 | univariate | 0.965 |  | 131 |  |
| CA | gdp | 1 | bvar | multivariate | 1.119 | 0.994 | 140 | 140 |
| CA | gdp | 1 | chronos2 | multivariate | 1.070 | 1.016 | 94 | 94 |
| CA | gdp | 1 | chronos2 | univariate | 1.324 | 1.304 | 140 | 140 |
| CA | gdp | 1 | combo_bench | multivariate | 0.806 | 0.767 | 137 | 137 |
| CA | gdp | 1 | combo_fm | univariate | 0.996 | 1.003 | 140 | 140 |
| CA | gdp | 1 | dfm | multivariate | 0.407 | 0.399 | 137 | 137 |
| CA | gdp | 1 | moirai2 | univariate | 0.972 | 0.983 | 140 | 140 |
| CA | gdp | 1 | naive | univariate | 0.795 | 0.812 | 140 | 140 |
| CA | gdp | 1 | timesfm25 | univariate | 0.931 | 0.943 | 140 | 140 |
| CA | gdp | 1 | tirex | univariate | 0.957 | 0.968 | 140 | 140 |
| CA | gdp | 1 | tirex2 | multivariate | 0.945 | 0.948 | 94 | 94 |
| CA | gdp | 1 | tirex2 | univariate | 0.846 | 0.861 | 140 | 140 |
| CA | gdp | 2 | bvar | multivariate | 1.164 | 1.011 | 137 | 137 |
| CA | gdp | 2 | chronos2 | multivariate | 1.038 | 0.993 | 92 | 92 |
| CA | gdp | 2 | chronos2 | univariate | 1.351 | 1.294 | 137 | 137 |
| CA | gdp | 2 | combo_bench | multivariate | 1.003 | 0.973 | 134 | 134 |
| CA | gdp | 2 | combo_fm | univariate | 1.023 | 1.021 | 137 | 137 |
| CA | gdp | 2 | dfm | multivariate | 0.928 | 0.935 | 134 | 134 |
| CA | gdp | 2 | moirai2 | univariate | 0.999 | 1.002 | 137 | 137 |
| CA | gdp | 2 | naive | univariate | 0.946 | 0.952 | 137 | 137 |
| CA | gdp | 2 | timesfm25 | univariate | 1.005 | 1.007 | 137 | 137 |
| CA | gdp | 2 | tirex | univariate | 0.962 | 0.971 | 137 | 137 |
| CA | gdp | 2 | tirex2 | multivariate | 0.967 | 0.973 | 92 | 92 |
| CA | gdp | 2 | tirex2 | univariate | 0.951 | 0.960 | 137 | 137 |
| CA | gdp | 4 | bvar | multivariate | 1.121 | 0.990 | 131 | 131 |
| CA | gdp | 4 | chronos2 | multivariate | 1.003 | 1.000 | 88 | 88 |
| CA | gdp | 4 | chronos2 | univariate | 1.212 | 1.123 | 131 | 131 |
| CA | gdp | 4 | combo_bench | multivariate | 1.009 | 0.993 | 128 | 128 |
| CA | gdp | 4 | combo_fm | univariate | 1.004 | 1.002 | 131 | 131 |
| CA | gdp | 4 | dfm | multivariate | 1.000 | 0.999 | 128 | 128 |
| CA | gdp | 4 | moirai2 | univariate | 0.994 | 0.997 | 131 | 131 |
| CA | gdp | 4 | naive | univariate | 1.000 | 0.999 | 131 | 131 |
| CA | gdp | 4 | timesfm25 | univariate | 0.996 | 1.000 | 131 | 131 |
| CA | gdp | 4 | tirex | univariate | 0.992 | 0.997 | 131 | 131 |
| CA | gdp | 4 | tirex2 | multivariate | 0.995 | 0.997 | 88 | 88 |
| CA | gdp | 4 | tirex2 | univariate | 0.992 | 0.995 | 131 | 131 |
| CA | retail | 1 | bvar | multivariate | 0.567 | 0.537 | 139 | 139 |
| CA | retail | 1 | chronos2 | multivariate | 1.161 | 0.927 | 140 | 140 |
| CA | retail | 1 | chronos2 | univariate | 1.222 | 1.047 | 140 | 140 |
| CA | retail | 1 | combo_bench | multivariate | 0.717 | 0.682 | 136 | 136 |
| CA | retail | 1 | combo_fm | univariate | 1.034 | 0.886 | 140 | 140 |
| CA | retail | 1 | dfm | multivariate | 0.725 | 0.637 | 137 | 137 |
| CA | retail | 1 | moirai2 | univariate | 1.041 | 0.898 | 140 | 140 |
| CA | retail | 1 | naive | univariate | 0.908 | 0.791 | 140 | 140 |
| CA | retail | 1 | timesfm25 | univariate | 0.959 | 0.841 | 140 | 140 |
| CA | retail | 1 | tirex | univariate | 0.981 | 0.886 | 140 | 140 |
| CA | retail | 1 | tirex2 | multivariate | 0.954 | 0.823 | 140 | 140 |
| CA | retail | 1 | tirex2 | univariate | 1.023 | 0.827 | 140 | 140 |
| CA | retail | 3 | bvar | multivariate | 0.976 | 0.857 | 138 | 138 |
| CA | retail | 3 | chronos2 | multivariate | 1.124 | 0.922 | 139 | 139 |
| CA | retail | 3 | chronos2 | univariate | 1.164 | 1.025 | 139 | 139 |
| CA | retail | 3 | combo_bench | multivariate | 0.976 | 0.875 | 135 | 135 |
| CA | retail | 3 | combo_fm | univariate | 0.998 | 0.888 | 139 | 139 |
| CA | retail | 3 | dfm | multivariate | 0.974 | 0.868 | 136 | 136 |
| CA | retail | 3 | moirai2 | univariate | 0.994 | 0.883 | 139 | 139 |
| CA | retail | 3 | naive | univariate | 0.980 | 0.870 | 139 | 139 |
| CA | retail | 3 | timesfm25 | univariate | 0.980 | 0.878 | 139 | 139 |
| CA | retail | 3 | tirex | univariate | 0.978 | 0.881 | 139 | 139 |
| CA | retail | 3 | tirex2 | multivariate | 0.981 | 0.871 | 139 | 139 |
| CA | retail | 3 | tirex2 | univariate | 0.983 | 0.872 | 139 | 139 |
| CA | retail | 6 | bvar | multivariate | 0.971 | 0.939 | 135 | 135 |
| CA | retail | 6 | chronos2 | multivariate | 1.062 | 0.964 | 136 | 136 |
| CA | retail | 6 | chronos2 | univariate | 1.130 | 1.091 | 136 | 136 |
| CA | retail | 6 | combo_bench | multivariate | 0.973 | 0.949 | 132 | 132 |
| CA | retail | 6 | combo_fm | univariate | 0.971 | 0.945 | 136 | 136 |
| CA | retail | 6 | dfm | multivariate | 0.956 | 0.926 | 133 | 133 |
| CA | retail | 6 | moirai2 | univariate | 0.961 | 0.932 | 136 | 136 |
| CA | retail | 6 | naive | univariate | 0.955 | 0.925 | 136 | 136 |
| CA | retail | 6 | timesfm25 | univariate | 0.959 | 0.947 | 136 | 136 |
| CA | retail | 6 | tirex | univariate | 0.964 | 0.944 | 136 | 136 |
| CA | retail | 6 | tirex2 | multivariate | 0.956 | 0.926 | 136 | 136 |
| CA | retail | 6 | tirex2 | univariate | 0.957 | 0.926 | 136 | 136 |
| CA | retail | 12 | bvar | multivariate | 0.995 | 0.984 | 130 | 130 |
| CA | retail | 12 | chronos2 | multivariate | 1.005 | 0.973 | 131 | 131 |
| CA | retail | 12 | chronos2 | univariate | 1.074 | 1.064 | 131 | 131 |
| CA | retail | 12 | combo_bench | multivariate | 0.994 | 0.985 | 127 | 127 |
| CA | retail | 12 | combo_fm | univariate | 0.970 | 0.967 | 131 | 131 |
| CA | retail | 12 | dfm | multivariate | 0.981 | 0.980 | 128 | 128 |
| CA | retail | 12 | moirai2 | univariate | 0.975 | 0.973 | 131 | 131 |
| CA | retail | 12 | naive | univariate | 0.981 | 0.980 | 131 | 131 |
| CA | retail | 12 | timesfm25 | univariate | 0.978 | 0.979 | 131 | 131 |
| CA | retail | 12 | tirex | univariate | 0.986 | 0.975 | 131 | 131 |
| CA | retail | 12 | tirex2 | multivariate | 0.981 | 0.980 | 131 | 131 |
| CA | retail | 12 | tirex2 | univariate | 0.982 | 0.981 | 131 | 131 |
| CA | unemp | 1 | bvar | multivariate | 0.970 | 0.981 | 141 | 141 |
| CA | unemp | 1 | chronos2 | multivariate | 1.339 | 1.300 | 142 | 142 |
| CA | unemp | 1 | chronos2 | univariate | 1.100 | 1.103 | 142 | 142 |
| CA | unemp | 1 | combo_bench | multivariate | 0.971 | 0.964 | 138 | 138 |
| CA | unemp | 1 | combo_fm | univariate | 0.987 | 0.987 | 142 | 142 |
| CA | unemp | 1 | dfm | multivariate | 1.006 | 0.975 | 139 | 139 |
| CA | unemp | 1 | moirai2 | univariate | 0.929 | 0.914 | 142 | 142 |
| CA | unemp | 1 | naive | univariate | 0.942 | 0.938 | 142 | 142 |
| CA | unemp | 1 | timesfm25 | univariate | 0.979 | 0.965 | 142 | 142 |
| CA | unemp | 1 | tirex | univariate | 1.007 | 1.000 | 142 | 142 |
| CA | unemp | 1 | tirex2 | multivariate | 1.097 | 1.087 | 142 | 142 |
| CA | unemp | 1 | tirex2 | univariate | 0.999 | 1.041 | 142 | 142 |
| CA | unemp | 3 | bvar | multivariate | 1.022 | 1.020 | 140 | 140 |
| CA | unemp | 3 | chronos2 | multivariate | 1.305 | 1.305 | 141 | 141 |
| CA | unemp | 3 | chronos2 | univariate | 1.082 | 1.124 | 141 | 141 |
| CA | unemp | 3 | combo_bench | multivariate | 0.998 | 0.996 | 137 | 137 |
| CA | unemp | 3 | combo_fm | univariate | 1.004 | 1.022 | 141 | 141 |
| CA | unemp | 3 | dfm | multivariate | 0.979 | 0.977 | 138 | 138 |
| CA | unemp | 3 | moirai2 | univariate | 0.983 | 1.007 | 141 | 141 |
| CA | unemp | 3 | naive | univariate | 0.965 | 0.962 | 141 | 141 |
| CA | unemp | 3 | timesfm25 | univariate | 1.008 | 1.032 | 141 | 141 |
| CA | unemp | 3 | tirex | univariate | 0.987 | 0.986 | 141 | 141 |
| CA | unemp | 3 | tirex2 | multivariate | 1.025 | 1.016 | 141 | 141 |
| CA | unemp | 3 | tirex2 | univariate | 0.998 | 1.015 | 141 | 141 |
| CA | unemp | 6 | bvar | multivariate | 1.008 | 1.010 | 137 | 137 |
| CA | unemp | 6 | chronos2 | multivariate | 1.117 | 1.157 | 138 | 138 |
| CA | unemp | 6 | chronos2 | univariate | 1.007 | 1.023 | 138 | 138 |
| CA | unemp | 6 | combo_bench | multivariate | 1.003 | 1.006 | 134 | 134 |
| CA | unemp | 6 | combo_fm | univariate | 1.001 | 1.010 | 138 | 138 |
| CA | unemp | 6 | dfm | multivariate | 1.001 | 1.009 | 135 | 135 |
| CA | unemp | 6 | moirai2 | univariate | 1.019 | 1.042 | 138 | 138 |
| CA | unemp | 6 | naive | univariate | 0.999 | 1.002 | 138 | 138 |
| CA | unemp | 6 | timesfm25 | univariate | 1.005 | 1.018 | 138 | 138 |
| CA | unemp | 6 | tirex | univariate | 1.002 | 1.012 | 138 | 138 |
| CA | unemp | 6 | tirex2 | multivariate | 1.000 | 1.000 | 138 | 138 |
| CA | unemp | 6 | tirex2 | univariate | 0.998 | 1.000 | 138 | 138 |
| CA | unemp | 12 | bvar | multivariate | 0.990 | 0.991 | 131 | 131 |
| CA | unemp | 12 | chronos2 | multivariate | 0.980 | 0.977 | 132 | 132 |
| CA | unemp | 12 | chronos2 | univariate | 0.983 | 0.991 | 132 | 132 |
| CA | unemp | 12 | combo_bench | multivariate | 0.991 | 0.993 | 128 | 128 |
| CA | unemp | 12 | combo_fm | univariate | 0.984 | 0.990 | 132 | 132 |
| CA | unemp | 12 | dfm | multivariate | 0.987 | 0.991 | 129 | 129 |
| CA | unemp | 12 | moirai2 | univariate | 0.997 | 1.021 | 132 | 132 |
| CA | unemp | 12 | naive | univariate | 0.987 | 0.988 | 132 | 132 |
| CA | unemp | 12 | timesfm25 | univariate | 0.992 | 1.000 | 132 | 132 |
| CA | unemp | 12 | tirex | univariate | 0.984 | 0.987 | 132 | 132 |
| CA | unemp | 12 | tirex2 | multivariate | 0.987 | 0.990 | 132 | 132 |
| CA | unemp | 12 | tirex2 | univariate | 0.987 | 0.990 | 132 | 132 |
| EA | consumption | 1 | bvar | multivariate | 0.570 | 0.479 | 130 | 133 |
| EA | consumption | 1 | chronos2 | multivariate | 0.643 | 0.637 | 133 | 133 |
| EA | consumption | 1 | chronos2 | univariate | 0.700 | 0.679 | 133 | 133 |
| EA | consumption | 1 | combo_bench | multivariate | 0.628 | 0.597 | 130 | 133 |
| EA | consumption | 1 | combo_fm | univariate | 0.600 | 0.595 | 133 | 133 |
| EA | consumption | 1 | dfm | multivariate | 0.466 | 0.387 | 133 | 133 |
| EA | consumption | 1 | moirai2 | univariate | 0.579 | 0.562 | 133 | 133 |
| EA | consumption | 1 | naive | univariate | 0.420 | 0.416 | 133 | 133 |
| EA | consumption | 1 | timesfm25 | univariate | 0.504 | 0.506 | 133 | 133 |
| EA | consumption | 1 | tirex | univariate | 0.670 | 0.670 | 133 | 133 |
| EA | consumption | 1 | tirex2 | multivariate | 0.572 | 0.581 | 133 | 133 |
| EA | consumption | 1 | tirex2 | univariate | 0.573 | 0.579 | 133 | 133 |
| EA | consumption | 2 | bvar | multivariate | 0.717 | 0.738 | 127 | 130 |
| EA | consumption | 2 | chronos2 | multivariate | 0.782 | 0.836 | 130 | 130 |
| EA | consumption | 2 | chronos2 | univariate | 0.869 | 0.880 | 130 | 130 |
| EA | consumption | 2 | combo_bench | multivariate | 0.727 | 0.744 | 127 | 130 |
| EA | consumption | 2 | combo_fm | univariate | 0.736 | 0.778 | 130 | 130 |
| EA | consumption | 2 | dfm | multivariate | 0.663 | 0.707 | 130 | 130 |
| EA | consumption | 2 | moirai2 | univariate | 0.714 | 0.756 | 130 | 130 |
| EA | consumption | 2 | naive | univariate | 0.679 | 0.722 | 130 | 130 |
| EA | consumption | 2 | timesfm25 | univariate | 0.721 | 0.762 | 130 | 130 |
| EA | consumption | 2 | tirex | univariate | 0.771 | 0.829 | 130 | 130 |
| EA | consumption | 2 | tirex2 | multivariate | 0.697 | 0.750 | 130 | 130 |
| EA | consumption | 2 | tirex2 | univariate | 0.695 | 0.741 | 130 | 130 |
| EA | consumption | 4 | bvar | multivariate | 0.913 | 0.964 | 124 | 124 |
| EA | consumption | 4 | chronos2 | multivariate | 0.911 | 0.969 | 124 | 124 |
| EA | consumption | 4 | chronos2 | univariate | 0.908 | 0.963 | 124 | 124 |
| EA | consumption | 4 | combo_bench | multivariate | 0.916 | 0.959 | 124 | 124 |
| EA | consumption | 4 | combo_fm | univariate | 0.906 | 0.964 | 124 | 124 |
| EA | consumption | 4 | dfm | multivariate | 0.915 | 0.969 | 124 | 124 |
| EA | consumption | 4 | moirai2 | univariate | 0.912 | 0.969 | 124 | 124 |
| EA | consumption | 4 | naive | univariate | 0.916 | 0.971 | 124 | 124 |
| EA | consumption | 4 | timesfm25 | univariate | 0.912 | 0.971 | 124 | 124 |
| EA | consumption | 4 | tirex | univariate | 0.911 | 0.965 | 124 | 124 |
| EA | consumption | 4 | tirex2 | multivariate | 0.907 | 0.964 | 124 | 124 |
| EA | consumption | 4 | tirex2 | univariate | 0.907 | 0.965 | 124 | 124 |
| EA | gdp | 1 | bvar | multivariate | 0.411 | 0.313 | 133 | 133 |
| EA | gdp | 1 | chronos2 | multivariate | 0.642 | 0.689 | 132 | 132 |
| EA | gdp | 1 | chronos2 | univariate | 0.840 | 0.878 | 133 | 133 |
| EA | gdp | 1 | combo_bench | multivariate | 0.610 | 0.563 | 133 | 133 |
| EA | gdp | 1 | combo_fm | univariate | 0.707 | 0.741 | 133 | 133 |
| EA | gdp | 1 | dfm | multivariate | 0.496 | 0.461 | 133 | 133 |
| EA | gdp | 1 | moirai2 | univariate | 0.687 | 0.718 | 133 | 133 |
| EA | gdp | 1 | naive | univariate | 0.567 | 0.610 | 133 | 133 |
| EA | gdp | 1 | timesfm25 | univariate | 0.625 | 0.666 | 133 | 133 |
| EA | gdp | 1 | tirex | univariate | 0.795 | 0.816 | 133 | 133 |
| EA | gdp | 1 | tirex2 | multivariate | 0.617 | 0.652 | 132 | 132 |
| EA | gdp | 1 | tirex2 | univariate | 0.619 | 0.655 | 133 | 133 |
| EA | gdp | 2 | bvar | multivariate | 1.025 | 1.112 | 129 | 129 |
| EA | gdp | 2 | chronos2 | multivariate | 0.919 | 0.911 | 128 | 128 |
| EA | gdp | 2 | chronos2 | univariate | 1.099 | 1.078 | 129 | 129 |
| EA | gdp | 2 | combo_bench | multivariate | 0.940 | 0.959 | 129 | 129 |
| EA | gdp | 2 | combo_fm | univariate | 0.927 | 0.935 | 129 | 129 |
| EA | gdp | 2 | dfm | multivariate | 0.916 | 0.947 | 129 | 129 |
| EA | gdp | 2 | moirai2 | univariate | 0.907 | 0.917 | 129 | 129 |
| EA | gdp | 2 | naive | univariate | 0.867 | 0.881 | 129 | 129 |
| EA | gdp | 2 | timesfm25 | univariate | 0.919 | 0.927 | 129 | 129 |
| EA | gdp | 2 | tirex | univariate | 0.936 | 0.941 | 129 | 129 |
| EA | gdp | 2 | tirex2 | multivariate | 0.886 | 0.903 | 128 | 128 |
| EA | gdp | 2 | tirex2 | univariate | 0.883 | 0.902 | 129 | 129 |
| EA | gdp | 4 | bvar | multivariate | 1.006 | 1.007 | 124 | 124 |
| EA | gdp | 4 | chronos2 | multivariate | 1.006 | 1.010 | 123 | 123 |
| EA | gdp | 4 | chronos2 | univariate | 1.003 | 1.008 | 124 | 124 |
| EA | gdp | 4 | combo_bench | multivariate | 1.002 | 1.001 | 124 | 124 |
| EA | gdp | 4 | combo_fm | univariate | 1.002 | 1.005 | 124 | 124 |
| EA | gdp | 4 | dfm | multivariate | 1.002 | 1.001 | 124 | 124 |
| EA | gdp | 4 | moirai2 | univariate | 1.003 | 1.005 | 124 | 124 |
| EA | gdp | 4 | naive | univariate | 1.002 | 1.000 | 124 | 124 |
| EA | gdp | 4 | timesfm25 | univariate | 1.009 | 1.010 | 124 | 124 |
| EA | gdp | 4 | tirex | univariate | 1.001 | 1.002 | 124 | 124 |
| EA | gdp | 4 | tirex2 | multivariate | 1.002 | 1.006 | 123 | 123 |
| EA | gdp | 4 | tirex2 | univariate | 1.003 | 1.006 | 124 | 124 |
| EA | hicp | 1 | bvar | multivariate | 0.803 | 0.817 | 142 | 142 |
| EA | hicp | 1 | chronos2 | multivariate | 0.894 | 0.890 | 142 | 142 |
| EA | hicp | 1 | chronos2 | univariate | 0.926 | 0.929 | 142 | 142 |
| EA | hicp | 1 | combo_bench | multivariate | 0.908 | 0.902 | 140 | 140 |
| EA | hicp | 1 | combo_fm | univariate | 0.926 | 0.921 | 142 | 142 |
| EA | hicp | 1 | dfm | multivariate | 1.420 | 1.402 | 140 | 140 |
| EA | hicp | 1 | moirai2 | univariate | 0.937 | 0.929 | 142 | 142 |
| EA | hicp | 1 | naive | univariate | 1.486 | 1.482 | 142 | 142 |
| EA | hicp | 1 | timesfm25 | univariate | 0.940 | 0.938 | 142 | 142 |
| EA | hicp | 1 | tirex | univariate | 1.024 | 1.014 | 142 | 142 |
| EA | hicp | 1 | tirex2 | multivariate | 0.964 | 0.957 | 142 | 142 |
| EA | hicp | 1 | tirex2 | univariate | 0.980 | 0.976 | 142 | 142 |
| EA | hicp | 3 | bvar | multivariate | 0.851 | 0.851 | 140 | 140 |
| EA | hicp | 3 | chronos2 | multivariate | 0.933 | 0.924 | 140 | 140 |
| EA | hicp | 3 | chronos2 | univariate | 0.973 | 0.971 | 140 | 140 |
| EA | hicp | 3 | combo_bench | multivariate | 0.862 | 0.859 | 138 | 138 |
| EA | hicp | 3 | combo_fm | univariate | 0.950 | 0.949 | 140 | 140 |
| EA | hicp | 3 | dfm | multivariate | 1.161 | 1.170 | 138 | 138 |
| EA | hicp | 3 | moirai2 | univariate | 0.987 | 0.986 | 140 | 140 |
| EA | hicp | 3 | naive | univariate | 1.118 | 1.118 | 140 | 140 |
| EA | hicp | 3 | timesfm25 | univariate | 0.931 | 0.941 | 140 | 140 |
| EA | hicp | 3 | tirex | univariate | 0.985 | 0.980 | 140 | 140 |
| EA | hicp | 3 | tirex2 | multivariate | 0.990 | 0.985 | 140 | 140 |
| EA | hicp | 3 | tirex2 | univariate | 1.001 | 0.996 | 140 | 140 |
| EA | hicp | 6 | bvar | multivariate | 0.986 | 0.987 | 136 | 136 |
| EA | hicp | 6 | chronos2 | multivariate | 0.934 | 0.931 | 136 | 136 |
| EA | hicp | 6 | chronos2 | univariate | 0.983 | 0.985 | 136 | 136 |
| EA | hicp | 6 | combo_bench | multivariate | 0.961 | 0.953 | 134 | 134 |
| EA | hicp | 6 | combo_fm | univariate | 0.989 | 0.989 | 136 | 136 |
| EA | hicp | 6 | dfm | multivariate | 1.262 | 1.262 | 134 | 134 |
| EA | hicp | 6 | moirai2 | univariate | 1.030 | 1.036 | 136 | 136 |
| EA | hicp | 6 | naive | univariate | 1.259 | 1.260 | 136 | 136 |
| EA | hicp | 6 | timesfm25 | univariate | 0.997 | 0.989 | 136 | 136 |
| EA | hicp | 6 | tirex | univariate | 1.016 | 1.014 | 136 | 136 |
| EA | hicp | 6 | tirex2 | multivariate | 1.026 | 1.021 | 136 | 136 |
| EA | hicp | 6 | tirex2 | univariate | 1.043 | 1.041 | 136 | 136 |
| EA | hicp | 12 | bvar | multivariate | 1.034 | 1.041 | 131 | 131 |
| EA | hicp | 12 | chronos2 | multivariate | 0.989 | 0.975 | 131 | 131 |
| EA | hicp | 12 | chronos2 | univariate | 1.148 | 1.149 | 131 | 131 |
| EA | hicp | 12 | combo_bench | multivariate | 0.986 | 0.983 | 129 | 129 |
| EA | hicp | 12 | combo_fm | univariate | 1.138 | 1.137 | 131 | 131 |
| EA | hicp | 12 | dfm | multivariate | 1.246 | 1.254 | 129 | 129 |
| EA | hicp | 12 | moirai2 | univariate | 1.156 | 1.161 | 131 | 131 |
| EA | hicp | 12 | naive | univariate | 1.248 | 1.255 | 131 | 131 |
| EA | hicp | 12 | timesfm25 | univariate | 1.119 | 1.115 | 131 | 131 |
| EA | hicp | 12 | tirex | univariate | 1.161 | 1.157 | 131 | 131 |
| EA | hicp | 12 | tirex2 | multivariate | 1.205 | 1.203 | 131 | 131 |
| EA | hicp | 12 | tirex2 | univariate | 1.249 | 1.246 | 131 | 131 |
| EA | hicp_core | 1 | bvar | multivariate | 1.401 |  | 142 |  |
| EA | hicp_core | 1 | chronos2 | multivariate | 0.795 |  | 102 |  |
| EA | hicp_core | 1 | chronos2 | univariate | 0.879 |  | 142 |  |
| EA | hicp_core | 1 | combo_bench | multivariate | 1.377 |  | 140 |  |
| EA | hicp_core | 1 | combo_fm | univariate | 0.841 |  | 142 |  |
| EA | hicp_core | 1 | dfm | multivariate | 2.847 |  | 140 |  |
| EA | hicp_core | 1 | moirai2 | univariate | 0.875 |  | 142 |  |
| EA | hicp_core | 1 | naive | univariate | 2.760 |  | 142 |  |
| EA | hicp_core | 1 | timesfm25 | univariate | 0.859 |  | 142 |  |
| EA | hicp_core | 1 | tirex | univariate | 0.938 |  | 142 |  |
| EA | hicp_core | 1 | tirex2 | multivariate | 0.873 |  | 102 |  |
| EA | hicp_core | 1 | tirex2 | univariate | 0.865 |  | 142 |  |
| EA | hicp_core | 3 | bvar | multivariate | 1.430 |  | 140 |  |
| EA | hicp_core | 3 | chronos2 | multivariate | 0.849 |  | 101 |  |
| EA | hicp_core | 3 | chronos2 | univariate | 0.951 |  | 140 |  |
| EA | hicp_core | 3 | combo_bench | multivariate | 1.340 |  | 138 |  |

_128 more rows in the CSV_

### 5.1b Q1: real-time versus revised input, revised outturn

| econ | target | horizon | model | variant | rel_rmsfe:realtime | rel_rmsfe:revised | n:realtime | n:revised |
|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | bvar | multivariate | 1.035 | 1.244 | 138 | 140 |
| CA | consumption | 1 | chronos2 | multivariate | 1.126 | 1.105 | 94 | 94 |
| CA | consumption | 1 | chronos2 | univariate | 1.303 | 1.346 | 140 | 140 |
| CA | consumption | 1 | combo_bench | multivariate | 0.866 | 0.900 | 135 | 137 |
| CA | consumption | 1 | combo_fm | univariate | 1.011 | 1.010 | 140 | 140 |
| CA | consumption | 1 | dfm | multivariate | 0.587 | 0.569 | 137 | 137 |
| CA | consumption | 1 | moirai2 | univariate | 1.030 | 1.048 | 140 | 140 |
| CA | consumption | 1 | naive | univariate | 0.824 | 0.832 | 140 | 140 |
| CA | consumption | 1 | timesfm25 | univariate | 0.959 | 0.945 | 140 | 140 |
| CA | consumption | 1 | tirex | univariate | 0.957 | 0.923 | 140 | 140 |
| CA | consumption | 1 | tirex2 | multivariate | 0.934 | 0.925 | 94 | 94 |
| CA | consumption | 1 | tirex2 | univariate | 0.854 | 0.853 | 140 | 140 |
| CA | consumption | 2 | bvar | multivariate | 1.147 | 1.260 | 135 | 137 |
| CA | consumption | 2 | chronos2 | multivariate | 1.047 | 1.019 | 92 | 92 |
| CA | consumption | 2 | chronos2 | univariate | 1.204 | 1.201 | 137 | 137 |
| CA | consumption | 2 | combo_bench | multivariate | 1.012 | 1.029 | 132 | 134 |
| CA | consumption | 2 | combo_fm | univariate | 1.013 | 1.010 | 137 | 137 |
| CA | consumption | 2 | dfm | multivariate | 0.967 | 0.965 | 134 | 134 |
| CA | consumption | 2 | moirai2 | univariate | 1.005 | 1.005 | 137 | 137 |
| CA | consumption | 2 | naive | univariate | 0.979 | 0.981 | 137 | 137 |
| CA | consumption | 2 | timesfm25 | univariate | 1.003 | 0.999 | 137 | 137 |
| CA | consumption | 2 | tirex | univariate | 0.985 | 0.986 | 137 | 137 |
| CA | consumption | 2 | tirex2 | multivariate | 0.995 | 0.993 | 92 | 92 |
| CA | consumption | 2 | tirex2 | univariate | 0.988 | 0.988 | 137 | 137 |
| CA | consumption | 4 | bvar | multivariate | 1.214 | 1.294 | 129 | 131 |
| CA | consumption | 4 | chronos2 | multivariate | 1.010 | 1.006 | 88 | 88 |
| CA | consumption | 4 | chronos2 | univariate | 1.107 | 1.103 | 131 | 131 |
| CA | consumption | 4 | combo_bench | multivariate | 1.009 | 1.029 | 126 | 128 |
| CA | consumption | 4 | combo_fm | univariate | 1.006 | 1.006 | 131 | 131 |
| CA | consumption | 4 | dfm | multivariate | 1.004 | 1.004 | 128 | 128 |
| CA | consumption | 4 | moirai2 | univariate | 1.004 | 1.005 | 131 | 131 |
| CA | consumption | 4 | naive | univariate | 1.007 | 1.007 | 131 | 131 |
| CA | consumption | 4 | timesfm25 | univariate | 1.000 | 1.000 | 131 | 131 |
| CA | consumption | 4 | tirex | univariate | 1.001 | 1.002 | 131 | 131 |
| CA | consumption | 4 | tirex2 | multivariate | 1.002 | 1.002 | 88 | 88 |
| CA | consumption | 4 | tirex2 | univariate | 0.996 | 0.997 | 131 | 131 |
| CA | cpi | 1 | bvar | multivariate | 0.976 |  | 141 |  |
| CA | cpi | 1 | chronos2 | multivariate | 0.844 |  | 142 |  |
| CA | cpi | 1 | chronos2 | univariate | 0.862 |  | 142 |  |
| CA | cpi | 1 | combo_bench | multivariate | 0.975 |  | 138 |  |
| CA | cpi | 1 | combo_fm | univariate | 0.856 |  | 142 |  |
| CA | cpi | 1 | dfm | multivariate | 0.988 |  | 139 |  |
| CA | cpi | 1 | moirai2 | univariate | 0.863 |  | 142 |  |
| CA | cpi | 1 | naive | univariate | 1.012 |  | 142 |  |
| CA | cpi | 1 | timesfm25 | univariate | 0.878 |  | 142 |  |
| CA | cpi | 1 | tirex | univariate | 0.886 |  | 142 |  |
| CA | cpi | 1 | tirex2 | multivariate | 0.856 |  | 142 |  |
| CA | cpi | 1 | tirex2 | univariate | 0.854 |  | 142 |  |
| CA | cpi | 3 | bvar | multivariate | 1.003 |  | 139 |  |
| CA | cpi | 3 | chronos2 | multivariate | 0.846 |  | 140 |  |
| CA | cpi | 3 | chronos2 | univariate | 0.822 |  | 140 |  |
| CA | cpi | 3 | combo_bench | multivariate | 1.000 |  | 136 |  |
| CA | cpi | 3 | combo_fm | univariate | 0.818 |  | 140 |  |
| CA | cpi | 3 | dfm | multivariate | 1.001 |  | 137 |  |
| CA | cpi | 3 | moirai2 | univariate | 0.840 |  | 140 |  |
| CA | cpi | 3 | naive | univariate | 0.998 |  | 140 |  |
| CA | cpi | 3 | timesfm25 | univariate | 0.814 |  | 140 |  |
| CA | cpi | 3 | tirex | univariate | 0.829 |  | 140 |  |
| CA | cpi | 3 | tirex2 | multivariate | 0.843 |  | 140 |  |
| CA | cpi | 3 | tirex2 | univariate | 0.831 |  | 140 |  |
| CA | cpi | 6 | bvar | multivariate | 1.014 |  | 136 |  |
| CA | cpi | 6 | chronos2 | multivariate | 0.895 |  | 137 |  |
| CA | cpi | 6 | chronos2 | univariate | 0.862 |  | 137 |  |
| CA | cpi | 6 | combo_bench | multivariate | 1.007 |  | 133 |  |
| CA | cpi | 6 | combo_fm | univariate | 0.851 |  | 137 |  |
| CA | cpi | 6 | dfm | multivariate | 1.011 |  | 134 |  |
| CA | cpi | 6 | moirai2 | univariate | 0.870 |  | 137 |  |
| CA | cpi | 6 | naive | univariate | 1.010 |  | 137 |  |
| CA | cpi | 6 | timesfm25 | univariate | 0.846 |  | 137 |  |
| CA | cpi | 6 | tirex | univariate | 0.852 |  | 137 |  |
| CA | cpi | 6 | tirex2 | multivariate | 0.883 |  | 137 |  |
| CA | cpi | 6 | tirex2 | univariate | 0.872 |  | 137 |  |
| CA | cpi | 12 | bvar | multivariate | 1.107 |  | 130 |  |
| CA | cpi | 12 | chronos2 | multivariate | 0.917 |  | 131 |  |
| CA | cpi | 12 | chronos2 | univariate | 0.891 |  | 131 |  |
| CA | cpi | 12 | combo_bench | multivariate | 1.060 |  | 127 |  |
| CA | cpi | 12 | combo_fm | univariate | 0.874 |  | 131 |  |
| CA | cpi | 12 | dfm | multivariate | 1.103 |  | 128 |  |
| CA | cpi | 12 | moirai2 | univariate | 0.892 |  | 131 |  |
| CA | cpi | 12 | naive | univariate | 1.104 |  | 131 |  |
| CA | cpi | 12 | timesfm25 | univariate | 0.874 |  | 131 |  |
| CA | cpi | 12 | tirex | univariate | 0.884 |  | 131 |  |
| CA | cpi | 12 | tirex2 | multivariate | 0.902 |  | 131 |  |
| CA | cpi | 12 | tirex2 | univariate | 0.888 |  | 131 |  |
| CA | cpi_core | 1 | bvar | multivariate | 1.223 |  | 141 |  |
| CA | cpi_core | 1 | chronos2 | multivariate | 0.999 |  | 142 |  |
| CA | cpi_core | 1 | chronos2 | univariate | 1.030 |  | 142 |  |
| CA | cpi_core | 1 | combo_bench | multivariate | 1.066 |  | 138 |  |
| CA | cpi_core | 1 | combo_fm | univariate | 0.967 |  | 142 |  |
| CA | cpi_core | 1 | dfm | multivariate | 1.179 |  | 139 |  |
| CA | cpi_core | 1 | moirai2 | univariate | 1.002 |  | 142 |  |
| CA | cpi_core | 1 | naive | univariate | 1.172 |  | 142 |  |
| CA | cpi_core | 1 | timesfm25 | univariate | 0.976 |  | 142 |  |
| CA | cpi_core | 1 | tirex | univariate | 0.959 |  | 142 |  |
| CA | cpi_core | 1 | tirex2 | multivariate | 0.950 |  | 142 |  |
| CA | cpi_core | 1 | tirex2 | univariate | 0.948 |  | 142 |  |
| CA | cpi_core | 3 | bvar | multivariate | 1.289 |  | 139 |  |
| CA | cpi_core | 3 | chronos2 | multivariate | 1.021 |  | 140 |  |
| CA | cpi_core | 3 | chronos2 | univariate | 1.046 |  | 140 |  |
| CA | cpi_core | 3 | combo_bench | multivariate | 1.129 |  | 136 |  |
| CA | cpi_core | 3 | combo_fm | univariate | 0.974 |  | 140 |  |
| CA | cpi_core | 3 | dfm | multivariate | 1.271 |  | 137 |  |
| CA | cpi_core | 3 | moirai2 | univariate | 0.999 |  | 140 |  |
| CA | cpi_core | 3 | naive | univariate | 1.268 |  | 140 |  |
| CA | cpi_core | 3 | timesfm25 | univariate | 0.961 |  | 140 |  |
| CA | cpi_core | 3 | tirex | univariate | 0.983 |  | 140 |  |
| CA | cpi_core | 3 | tirex2 | multivariate | 0.960 |  | 140 |  |
| CA | cpi_core | 3 | tirex2 | univariate | 0.950 |  | 140 |  |
| CA | cpi_core | 6 | bvar | multivariate | 1.255 |  | 136 |  |
| CA | cpi_core | 6 | chronos2 | multivariate | 1.059 |  | 137 |  |
| CA | cpi_core | 6 | chronos2 | univariate | 1.040 |  | 137 |  |
| CA | cpi_core | 6 | combo_bench | multivariate | 1.102 |  | 133 |  |
| CA | cpi_core | 6 | combo_fm | univariate | 0.963 |  | 137 |  |
| CA | cpi_core | 6 | dfm | multivariate | 1.237 |  | 134 |  |
| CA | cpi_core | 6 | moirai2 | univariate | 0.968 |  | 137 |  |
| CA | cpi_core | 6 | naive | univariate | 1.237 |  | 137 |  |
| CA | cpi_core | 6 | timesfm25 | univariate | 0.960 |  | 137 |  |
| CA | cpi_core | 6 | tirex | univariate | 0.970 |  | 137 |  |
| CA | cpi_core | 6 | tirex2 | multivariate | 0.992 |  | 137 |  |
| CA | cpi_core | 6 | tirex2 | univariate | 0.957 |  | 137 |  |
| CA | cpi_core | 12 | bvar | multivariate | 1.326 |  | 130 |  |
| CA | cpi_core | 12 | chronos2 | multivariate | 1.047 |  | 131 |  |
| CA | cpi_core | 12 | chronos2 | univariate | 0.995 |  | 131 |  |
| CA | cpi_core | 12 | combo_bench | multivariate | 1.135 |  | 127 |  |
| CA | cpi_core | 12 | combo_fm | univariate | 0.960 |  | 131 |  |
| CA | cpi_core | 12 | dfm | multivariate | 1.282 |  | 128 |  |
| CA | cpi_core | 12 | moirai2 | univariate | 0.990 |  | 131 |  |
| CA | cpi_core | 12 | naive | univariate | 1.316 |  | 131 |  |
| CA | cpi_core | 12 | timesfm25 | univariate | 0.958 |  | 131 |  |
| CA | cpi_core | 12 | tirex | univariate | 0.952 |  | 131 |  |
| CA | cpi_core | 12 | tirex2 | multivariate | 0.975 |  | 131 |  |
| CA | cpi_core | 12 | tirex2 | univariate | 0.965 |  | 131 |  |
| CA | gdp | 1 | bvar | multivariate | 1.121 | 0.994 | 140 | 140 |
| CA | gdp | 1 | chronos2 | multivariate | 1.072 | 1.018 | 94 | 94 |
| CA | gdp | 1 | chronos2 | univariate | 1.329 | 1.309 | 140 | 140 |
| CA | gdp | 1 | combo_bench | multivariate | 0.805 | 0.765 | 137 | 137 |
| CA | gdp | 1 | combo_fm | univariate | 0.998 | 1.005 | 140 | 140 |
| CA | gdp | 1 | dfm | multivariate | 0.400 | 0.391 | 137 | 137 |
| CA | gdp | 1 | moirai2 | univariate | 0.974 | 0.985 | 140 | 140 |
| CA | gdp | 1 | naive | univariate | 0.788 | 0.806 | 140 | 140 |
| CA | gdp | 1 | timesfm25 | univariate | 0.933 | 0.945 | 140 | 140 |
| CA | gdp | 1 | tirex | univariate | 0.959 | 0.970 | 140 | 140 |
| CA | gdp | 1 | tirex2 | multivariate | 0.945 | 0.949 | 94 | 94 |
| CA | gdp | 1 | tirex2 | univariate | 0.845 | 0.860 | 140 | 140 |
| CA | gdp | 2 | bvar | multivariate | 1.167 | 1.013 | 137 | 137 |
| CA | gdp | 2 | chronos2 | multivariate | 1.037 | 0.992 | 92 | 92 |
| CA | gdp | 2 | chronos2 | univariate | 1.356 | 1.297 | 137 | 137 |
| CA | gdp | 2 | combo_bench | multivariate | 1.003 | 0.974 | 134 | 134 |
| CA | gdp | 2 | combo_fm | univariate | 1.025 | 1.022 | 137 | 137 |
| CA | gdp | 2 | dfm | multivariate | 0.929 | 0.934 | 134 | 134 |
| CA | gdp | 2 | moirai2 | univariate | 1.000 | 1.004 | 137 | 137 |
| CA | gdp | 2 | naive | univariate | 0.945 | 0.951 | 137 | 137 |
| CA | gdp | 2 | timesfm25 | univariate | 1.010 | 1.011 | 137 | 137 |
| CA | gdp | 2 | tirex | univariate | 0.965 | 0.973 | 137 | 137 |
| CA | gdp | 2 | tirex2 | multivariate | 0.966 | 0.971 | 92 | 92 |
| CA | gdp | 2 | tirex2 | univariate | 0.951 | 0.960 | 137 | 137 |
| CA | gdp | 4 | bvar | multivariate | 1.116 | 0.991 | 131 | 131 |
| CA | gdp | 4 | chronos2 | multivariate | 1.001 | 1.000 | 88 | 88 |
| CA | gdp | 4 | chronos2 | univariate | 1.202 | 1.112 | 131 | 131 |
| CA | gdp | 4 | combo_bench | multivariate | 1.007 | 0.995 | 128 | 128 |
| CA | gdp | 4 | combo_fm | univariate | 1.002 | 1.000 | 131 | 131 |
| CA | gdp | 4 | dfm | multivariate | 1.004 | 1.002 | 128 | 128 |
| CA | gdp | 4 | moirai2 | univariate | 0.994 | 0.997 | 131 | 131 |
| CA | gdp | 4 | naive | univariate | 1.004 | 1.002 | 131 | 131 |
| CA | gdp | 4 | timesfm25 | univariate | 0.997 | 1.001 | 131 | 131 |
| CA | gdp | 4 | tirex | univariate | 0.995 | 0.999 | 131 | 131 |
| CA | gdp | 4 | tirex2 | multivariate | 0.997 | 0.999 | 88 | 88 |
| CA | gdp | 4 | tirex2 | univariate | 0.995 | 0.998 | 131 | 131 |
| CA | retail | 1 | bvar | multivariate | 0.575 | 0.535 | 139 | 139 |
| CA | retail | 1 | chronos2 | multivariate | 1.188 | 0.928 | 140 | 140 |
| CA | retail | 1 | chronos2 | univariate | 1.250 | 1.053 | 140 | 140 |
| CA | retail | 1 | combo_bench | multivariate | 0.719 | 0.680 | 136 | 136 |
| CA | retail | 1 | combo_fm | univariate | 1.055 | 0.888 | 140 | 140 |
| CA | retail | 1 | dfm | multivariate | 0.738 | 0.640 | 137 | 137 |
| CA | retail | 1 | moirai2 | univariate | 1.065 | 0.901 | 140 | 140 |
| CA | retail | 1 | naive | univariate | 0.914 | 0.782 | 140 | 140 |
| CA | retail | 1 | timesfm25 | univariate | 0.974 | 0.837 | 140 | 140 |
| CA | retail | 1 | tirex | univariate | 0.998 | 0.888 | 140 | 140 |
| CA | retail | 1 | tirex2 | multivariate | 0.965 | 0.814 | 140 | 140 |
| CA | retail | 1 | tirex2 | univariate | 1.038 | 0.818 | 140 | 140 |
| CA | retail | 3 | bvar | multivariate | 0.968 | 0.837 | 138 | 138 |
| CA | retail | 3 | chronos2 | multivariate | 1.103 | 0.905 | 139 | 139 |
| CA | retail | 3 | chronos2 | univariate | 1.142 | 0.999 | 139 | 139 |
| CA | retail | 3 | combo_bench | multivariate | 0.972 | 0.869 | 135 | 135 |
| CA | retail | 3 | combo_fm | univariate | 0.991 | 0.875 | 139 | 139 |
| CA | retail | 3 | dfm | multivariate | 0.970 | 0.860 | 136 | 136 |
| CA | retail | 3 | moirai2 | univariate | 0.987 | 0.872 | 139 | 139 |
| CA | retail | 3 | naive | univariate | 0.977 | 0.862 | 139 | 139 |
| CA | retail | 3 | timesfm25 | univariate | 0.975 | 0.865 | 139 | 139 |
| CA | retail | 3 | tirex | univariate | 0.974 | 0.870 | 139 | 139 |
| CA | retail | 3 | tirex2 | multivariate | 0.977 | 0.862 | 139 | 139 |
| CA | retail | 3 | tirex2 | univariate | 0.978 | 0.863 | 139 | 139 |
| CA | retail | 6 | bvar | multivariate | 0.963 | 0.931 | 135 | 135 |
| CA | retail | 6 | chronos2 | multivariate | 1.050 | 0.956 | 136 | 136 |
| CA | retail | 6 | chronos2 | univariate | 1.116 | 1.078 | 136 | 136 |
| CA | retail | 6 | combo_bench | multivariate | 0.967 | 0.944 | 132 | 132 |
| CA | retail | 6 | combo_fm | univariate | 0.962 | 0.938 | 136 | 136 |
| CA | retail | 6 | dfm | multivariate | 0.945 | 0.916 | 133 | 133 |
| CA | retail | 6 | moirai2 | univariate | 0.952 | 0.923 | 136 | 136 |
| CA | retail | 6 | naive | univariate | 0.944 | 0.915 | 136 | 136 |
| CA | retail | 6 | timesfm25 | univariate | 0.950 | 0.941 | 136 | 136 |
| CA | retail | 6 | tirex | univariate | 0.954 | 0.935 | 136 | 136 |
| CA | retail | 6 | tirex2 | multivariate | 0.946 | 0.916 | 136 | 136 |
| CA | retail | 6 | tirex2 | univariate | 0.948 | 0.916 | 136 | 136 |
| CA | retail | 12 | bvar | multivariate | 0.995 | 0.985 | 130 | 130 |
| CA | retail | 12 | chronos2 | multivariate | 1.009 | 0.976 | 131 | 131 |
| CA | retail | 12 | chronos2 | univariate | 1.075 | 1.065 | 131 | 131 |
| CA | retail | 12 | combo_bench | multivariate | 0.994 | 0.985 | 127 | 127 |
| CA | retail | 12 | combo_fm | univariate | 0.974 | 0.971 | 131 | 131 |
| CA | retail | 12 | dfm | multivariate | 0.982 | 0.981 | 128 | 128 |
| CA | retail | 12 | moirai2 | univariate | 0.978 | 0.975 | 131 | 131 |
| CA | retail | 12 | naive | univariate | 0.983 | 0.981 | 131 | 131 |
| CA | retail | 12 | timesfm25 | univariate | 0.980 | 0.981 | 131 | 131 |
| CA | retail | 12 | tirex | univariate | 0.987 | 0.977 | 131 | 131 |
| CA | retail | 12 | tirex2 | multivariate | 0.983 | 0.981 | 131 | 131 |
| CA | retail | 12 | tirex2 | univariate | 0.984 | 0.982 | 131 | 131 |
| CA | unemp | 1 | bvar | multivariate | 0.964 | 0.973 | 141 | 141 |
| CA | unemp | 1 | chronos2 | multivariate | 1.372 | 1.327 | 142 | 142 |
| CA | unemp | 1 | chronos2 | univariate | 1.116 | 1.123 | 142 | 142 |
| CA | unemp | 1 | combo_bench | multivariate | 0.971 | 0.962 | 138 | 138 |
| CA | unemp | 1 | combo_fm | univariate | 0.992 | 0.994 | 142 | 142 |
| CA | unemp | 1 | dfm | multivariate | 1.019 | 0.986 | 139 | 139 |
| CA | unemp | 1 | moirai2 | univariate | 0.928 | 0.914 | 142 | 142 |
| CA | unemp | 1 | naive | univariate | 0.930 | 0.922 | 142 | 142 |
| CA | unemp | 1 | timesfm25 | univariate | 0.984 | 0.972 | 142 | 142 |
| CA | unemp | 1 | tirex | univariate | 1.015 | 1.007 | 142 | 142 |
| CA | unemp | 1 | tirex2 | multivariate | 1.112 | 1.102 | 142 | 142 |
| CA | unemp | 1 | tirex2 | univariate | 1.000 | 1.049 | 142 | 142 |
| CA | unemp | 3 | bvar | multivariate | 1.022 | 1.019 | 140 | 140 |
| CA | unemp | 3 | chronos2 | multivariate | 1.320 | 1.319 | 141 | 141 |
| CA | unemp | 3 | chronos2 | univariate | 1.088 | 1.131 | 141 | 141 |
| CA | unemp | 3 | combo_bench | multivariate | 0.998 | 0.996 | 137 | 137 |
| CA | unemp | 3 | combo_fm | univariate | 1.005 | 1.024 | 141 | 141 |
| CA | unemp | 3 | dfm | multivariate | 0.980 | 0.979 | 138 | 138 |
| CA | unemp | 3 | moirai2 | univariate | 0.978 | 1.002 | 141 | 141 |
| CA | unemp | 3 | naive | univariate | 0.962 | 0.959 | 141 | 141 |
| CA | unemp | 3 | timesfm25 | univariate | 1.009 | 1.034 | 141 | 141 |
| CA | unemp | 3 | tirex | univariate | 0.987 | 0.985 | 141 | 141 |
| CA | unemp | 3 | tirex2 | multivariate | 1.028 | 1.018 | 141 | 141 |
| CA | unemp | 3 | tirex2 | univariate | 0.999 | 1.019 | 141 | 141 |
| CA | unemp | 6 | bvar | multivariate | 1.007 | 1.009 | 137 | 137 |
| CA | unemp | 6 | chronos2 | multivariate | 1.127 | 1.168 | 138 | 138 |
| CA | unemp | 6 | chronos2 | univariate | 1.008 | 1.026 | 138 | 138 |
| CA | unemp | 6 | combo_bench | multivariate | 1.002 | 1.005 | 134 | 134 |
| CA | unemp | 6 | combo_fm | univariate | 1.000 | 1.011 | 138 | 138 |
| CA | unemp | 6 | dfm | multivariate | 1.001 | 1.009 | 135 | 135 |
| CA | unemp | 6 | moirai2 | univariate | 1.018 | 1.043 | 138 | 138 |
| CA | unemp | 6 | naive | univariate | 0.998 | 1.002 | 138 | 138 |
| CA | unemp | 6 | timesfm25 | univariate | 1.004 | 1.020 | 138 | 138 |
| CA | unemp | 6 | tirex | univariate | 1.001 | 1.011 | 138 | 138 |
| CA | unemp | 6 | tirex2 | multivariate | 1.000 | 1.001 | 138 | 138 |
| CA | unemp | 6 | tirex2 | univariate | 0.998 | 1.002 | 138 | 138 |
| CA | unemp | 12 | bvar | multivariate | 0.991 | 0.992 | 131 | 131 |
| CA | unemp | 12 | chronos2 | multivariate | 0.984 | 0.979 | 132 | 132 |
| CA | unemp | 12 | chronos2 | univariate | 0.987 | 0.998 | 132 | 132 |
| CA | unemp | 12 | combo_bench | multivariate | 0.992 | 0.993 | 128 | 128 |
| CA | unemp | 12 | combo_fm | univariate | 0.989 | 0.996 | 132 | 132 |
| CA | unemp | 12 | dfm | multivariate | 0.989 | 0.992 | 129 | 129 |
| CA | unemp | 12 | moirai2 | univariate | 1.006 | 1.033 | 132 | 132 |
| CA | unemp | 12 | naive | univariate | 0.988 | 0.989 | 132 | 132 |
| CA | unemp | 12 | timesfm25 | univariate | 0.998 | 1.008 | 132 | 132 |
| CA | unemp | 12 | tirex | univariate | 0.988 | 0.991 | 132 | 132 |
| CA | unemp | 12 | tirex2 | multivariate | 0.990 | 0.992 | 132 | 132 |
| CA | unemp | 12 | tirex2 | univariate | 0.990 | 0.993 | 132 | 132 |
| EA | consumption | 1 | bvar | multivariate | 0.340 | 0.450 | 131 | 134 |
| EA | consumption | 1 | chronos2 | multivariate | 0.634 | 0.625 | 134 | 134 |
| EA | consumption | 1 | chronos2 | univariate | 0.707 | 0.675 | 134 | 134 |
| EA | consumption | 1 | combo_bench | multivariate | 0.486 | 0.582 | 131 | 134 |
| EA | consumption | 1 | combo_fm | univariate | 0.585 | 0.578 | 134 | 134 |
| EA | consumption | 1 | dfm | multivariate | 0.426 | 0.360 | 134 | 134 |
| EA | consumption | 1 | moirai2 | univariate | 0.558 | 0.539 | 134 | 134 |
| EA | consumption | 1 | naive | univariate | 0.356 | 0.350 | 134 | 134 |
| EA | consumption | 1 | timesfm25 | univariate | 0.476 | 0.474 | 134 | 134 |
| EA | consumption | 1 | tirex | univariate | 0.657 | 0.660 | 134 | 134 |
| EA | consumption | 1 | tirex2 | multivariate | 0.545 | 0.559 | 134 | 134 |
| EA | consumption | 1 | tirex2 | univariate | 0.545 | 0.554 | 134 | 134 |
| EA | consumption | 2 | bvar | multivariate | 0.535 | 0.632 | 126 | 129 |
| EA | consumption | 2 | chronos2 | multivariate | 0.631 | 0.762 | 129 | 129 |
| EA | consumption | 2 | chronos2 | univariate | 0.750 | 0.832 | 129 | 129 |
| EA | consumption | 2 | combo_bench | multivariate | 0.554 | 0.631 | 126 | 129 |
| EA | consumption | 2 | combo_fm | univariate | 0.575 | 0.677 | 129 | 129 |
| EA | consumption | 2 | dfm | multivariate | 0.480 | 0.574 | 129 | 129 |
| EA | consumption | 2 | moirai2 | univariate | 0.537 | 0.636 | 129 | 129 |
| EA | consumption | 2 | naive | univariate | 0.477 | 0.570 | 129 | 129 |
| EA | consumption | 2 | timesfm25 | univariate | 0.560 | 0.658 | 129 | 129 |
| EA | consumption | 2 | tirex | univariate | 0.626 | 0.763 | 129 | 129 |
| EA | consumption | 2 | tirex2 | multivariate | 0.517 | 0.629 | 129 | 129 |
| EA | consumption | 2 | tirex2 | univariate | 0.515 | 0.616 | 129 | 129 |
| EA | consumption | 4 | bvar | multivariate | 0.853 | 1.393 | 121 | 124 |
| EA | consumption | 4 | chronos2 | multivariate | 1.039 | 1.198 | 124 | 124 |
| EA | consumption | 4 | chronos2 | univariate | 1.235 | 1.304 | 124 | 124 |
| EA | consumption | 4 | combo_bench | multivariate | 0.860 | 1.012 | 121 | 124 |
| EA | consumption | 4 | combo_fm | univariate | 0.909 | 0.983 | 124 | 124 |
| EA | consumption | 4 | dfm | multivariate | 0.785 | 0.851 | 124 | 124 |
| EA | consumption | 4 | moirai2 | univariate | 0.892 | 0.945 | 124 | 124 |
| EA | consumption | 4 | naive | univariate | 0.781 | 0.852 | 124 | 124 |
| EA | consumption | 4 | timesfm25 | univariate | 0.791 | 0.867 | 124 | 124 |
| EA | consumption | 4 | tirex | univariate | 0.966 | 1.039 | 124 | 124 |
| EA | consumption | 4 | tirex2 | multivariate | 0.808 | 0.900 | 124 | 124 |
| EA | consumption | 4 | tirex2 | univariate | 0.808 | 0.891 | 124 | 124 |
| EA | gdp | 1 | bvar | multivariate | 0.325 | 0.217 | 132 | 132 |
| EA | gdp | 1 | chronos2 | multivariate | 0.557 | 0.598 | 131 | 131 |
| EA | gdp | 1 | chronos2 | univariate | 0.817 | 0.858 | 132 | 132 |
| EA | gdp | 1 | combo_bench | multivariate | 0.561 | 0.513 | 132 | 132 |
| EA | gdp | 1 | combo_fm | univariate | 0.634 | 0.666 | 132 | 132 |
| EA | gdp | 1 | dfm | multivariate | 0.427 | 0.386 | 132 | 132 |
| EA | gdp | 1 | moirai2 | univariate | 0.600 | 0.626 | 132 | 132 |
| EA | gdp | 1 | naive | univariate | 0.389 | 0.424 | 132 | 132 |
| EA | gdp | 1 | timesfm25 | univariate | 0.519 | 0.554 | 132 | 132 |
| EA | gdp | 1 | tirex | univariate | 0.751 | 0.772 | 132 | 132 |
| EA | gdp | 1 | tirex2 | multivariate | 0.497 | 0.530 | 131 | 131 |
| EA | gdp | 1 | tirex2 | univariate | 0.493 | 0.531 | 132 | 132 |
| EA | gdp | 2 | bvar | multivariate | 1.015 | 1.129 | 130 | 130 |
| EA | gdp | 2 | chronos2 | multivariate | 0.883 | 0.869 | 129 | 129 |
| EA | gdp | 2 | chronos2 | univariate | 1.132 | 1.100 | 130 | 130 |
| EA | gdp | 2 | combo_bench | multivariate | 0.907 | 0.931 | 130 | 130 |
| EA | gdp | 2 | combo_fm | univariate | 0.900 | 0.904 | 130 | 130 |
| EA | gdp | 2 | dfm | multivariate | 0.871 | 0.907 | 130 | 130 |
| EA | gdp | 2 | moirai2 | univariate | 0.871 | 0.878 | 130 | 130 |
| EA | gdp | 2 | naive | univariate | 0.806 | 0.820 | 130 | 130 |
| EA | gdp | 2 | timesfm25 | univariate | 0.884 | 0.889 | 130 | 130 |
| EA | gdp | 2 | tirex | univariate | 0.915 | 0.914 | 130 | 130 |
| EA | gdp | 2 | tirex2 | multivariate | 0.839 | 0.857 | 129 | 129 |
| EA | gdp | 2 | tirex2 | univariate | 0.834 | 0.855 | 130 | 130 |
| EA | gdp | 4 | bvar | multivariate | 1.004 | 1.090 | 124 | 124 |
| EA | gdp | 4 | chronos2 | multivariate | 0.981 | 1.034 | 123 | 123 |
| EA | gdp | 4 | chronos2 | univariate | 1.252 | 1.205 | 124 | 124 |
| EA | gdp | 4 | combo_bench | multivariate | 0.939 | 0.983 | 124 | 124 |
| EA | gdp | 4 | combo_fm | univariate | 1.002 | 1.036 | 124 | 124 |
| EA | gdp | 4 | dfm | multivariate | 0.949 | 0.994 | 124 | 124 |
| EA | gdp | 4 | moirai2 | univariate | 0.991 | 1.029 | 124 | 124 |
| EA | gdp | 4 | naive | univariate | 0.946 | 0.991 | 124 | 124 |
| EA | gdp | 4 | timesfm25 | univariate | 0.968 | 1.009 | 124 | 124 |
| EA | gdp | 4 | tirex | univariate | 0.983 | 1.027 | 124 | 124 |
| EA | gdp | 4 | tirex2 | multivariate | 0.954 | 1.000 | 123 | 123 |
| EA | gdp | 4 | tirex2 | univariate | 0.953 | 0.999 | 124 | 124 |
| EA | hicp | 1 | bvar | multivariate | 0.806 | 0.820 | 141 | 141 |
| EA | hicp | 1 | chronos2 | multivariate | 0.891 | 0.887 | 141 | 141 |
| EA | hicp | 1 | chronos2 | univariate | 0.923 | 0.926 | 141 | 141 |
| EA | hicp | 1 | combo_bench | multivariate | 0.909 | 0.903 | 139 | 139 |
| EA | hicp | 1 | combo_fm | univariate | 0.924 | 0.919 | 141 | 141 |
| EA | hicp | 1 | dfm | multivariate | 1.417 | 1.400 | 139 | 139 |
| EA | hicp | 1 | moirai2 | univariate | 0.935 | 0.927 | 141 | 141 |
| EA | hicp | 1 | naive | univariate | 1.483 | 1.481 | 141 | 141 |
| EA | hicp | 1 | timesfm25 | univariate | 0.937 | 0.935 | 141 | 141 |
| EA | hicp | 1 | tirex | univariate | 1.019 | 1.011 | 141 | 141 |
| EA | hicp | 1 | tirex2 | multivariate | 0.961 | 0.955 | 141 | 141 |
| EA | hicp | 1 | tirex2 | univariate | 0.977 | 0.974 | 141 | 141 |
| EA | hicp | 3 | bvar | multivariate | 0.842 | 0.844 | 138 | 138 |
| EA | hicp | 3 | chronos2 | multivariate | 0.928 | 0.920 | 138 | 138 |
| EA | hicp | 3 | chronos2 | univariate | 0.967 | 0.969 | 138 | 138 |
| EA | hicp | 3 | combo_bench | multivariate | 0.861 | 0.860 | 136 | 136 |
| EA | hicp | 3 | combo_fm | univariate | 0.946 | 0.946 | 138 | 138 |
| EA | hicp | 3 | dfm | multivariate | 1.145 | 1.158 | 136 | 136 |
| EA | hicp | 3 | moirai2 | univariate | 0.981 | 0.981 | 138 | 138 |
| EA | hicp | 3 | naive | univariate | 1.104 | 1.109 | 138 | 138 |
| EA | hicp | 3 | timesfm25 | univariate | 0.926 | 0.936 | 138 | 138 |
| EA | hicp | 3 | tirex | univariate | 0.980 | 0.977 | 138 | 138 |
| EA | hicp | 3 | tirex2 | multivariate | 0.986 | 0.981 | 138 | 138 |
| EA | hicp | 3 | tirex2 | univariate | 0.995 | 0.991 | 138 | 138 |
| EA | hicp | 6 | bvar | multivariate | 0.978 | 0.986 | 134 | 134 |
| EA | hicp | 6 | chronos2 | multivariate | 0.929 | 0.927 | 134 | 134 |
| EA | hicp | 6 | chronos2 | univariate | 0.974 | 0.982 | 134 | 134 |
| EA | hicp | 6 | combo_bench | multivariate | 0.960 | 0.957 | 132 | 132 |
| EA | hicp | 6 | combo_fm | univariate | 0.979 | 0.981 | 134 | 134 |
| EA | hicp | 6 | dfm | multivariate | 1.247 | 1.257 | 132 | 132 |
| EA | hicp | 6 | moirai2 | univariate | 1.017 | 1.025 | 134 | 134 |
| EA | hicp | 6 | naive | univariate | 1.241 | 1.254 | 134 | 134 |
| EA | hicp | 6 | timesfm25 | univariate | 0.985 | 0.978 | 134 | 134 |
| EA | hicp | 6 | tirex | univariate | 1.004 | 1.004 | 134 | 134 |
| EA | hicp | 6 | tirex2 | multivariate | 1.017 | 1.015 | 134 | 134 |
| EA | hicp | 6 | tirex2 | univariate | 1.033 | 1.034 | 134 | 134 |
| EA | hicp | 12 | bvar | multivariate | 1.034 | 1.046 | 130 | 130 |
| EA | hicp | 12 | chronos2 | multivariate | 0.988 | 0.976 | 130 | 130 |
| EA | hicp | 12 | chronos2 | univariate | 1.143 | 1.148 | 130 | 130 |
| EA | hicp | 12 | combo_bench | multivariate | 0.986 | 0.986 | 128 | 128 |
| EA | hicp | 12 | combo_fm | univariate | 1.132 | 1.133 | 130 | 130 |
| EA | hicp | 12 | dfm | multivariate | 1.241 | 1.256 | 128 | 128 |
| EA | hicp | 12 | moirai2 | univariate | 1.149 | 1.156 | 130 | 130 |
| EA | hicp | 12 | naive | univariate | 1.243 | 1.256 | 130 | 130 |
| EA | hicp | 12 | timesfm25 | univariate | 1.111 | 1.108 | 130 | 130 |
| EA | hicp | 12 | tirex | univariate | 1.155 | 1.153 | 130 | 130 |
| EA | hicp | 12 | tirex2 | multivariate | 1.198 | 1.198 | 130 | 130 |
| EA | hicp | 12 | tirex2 | univariate | 1.242 | 1.241 | 130 | 130 |
| EA | hicp_core | 1 | bvar | multivariate | 1.401 |  | 142 |  |
| EA | hicp_core | 1 | chronos2 | multivariate | 0.795 |  | 102 |  |
| EA | hicp_core | 1 | chronos2 | univariate | 0.879 |  | 142 |  |
| EA | hicp_core | 1 | combo_bench | multivariate | 1.377 |  | 140 |  |
| EA | hicp_core | 1 | combo_fm | univariate | 0.841 |  | 142 |  |
| EA | hicp_core | 1 | dfm | multivariate | 2.847 |  | 140 |  |
| EA | hicp_core | 1 | moirai2 | univariate | 0.875 |  | 142 |  |
| EA | hicp_core | 1 | naive | univariate | 2.760 |  | 142 |  |
| EA | hicp_core | 1 | timesfm25 | univariate | 0.859 |  | 142 |  |
| EA | hicp_core | 1 | tirex | univariate | 0.938 |  | 142 |  |
| EA | hicp_core | 1 | tirex2 | multivariate | 0.873 |  | 102 |  |
| EA | hicp_core | 1 | tirex2 | univariate | 0.865 |  | 142 |  |
| EA | hicp_core | 3 | bvar | multivariate | 1.430 |  | 140 |  |
| EA | hicp_core | 3 | chronos2 | multivariate | 0.849 |  | 101 |  |
| EA | hicp_core | 3 | chronos2 | univariate | 0.951 |  | 140 |  |
| EA | hicp_core | 3 | combo_bench | multivariate | 1.340 |  | 138 |  |

_128 more rows in the CSV_

### 5.2 Outturn definition (real-time input)

| econ | target | horizon | model | variant | rel_rmsfe:first_release | rel_rmsfe:revised_12m | n:first_release | n:revised_12m |
|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | bvar | multivariate | 1.049 | 1.035 | 138 | 138 |
| CA | consumption | 1 | chronos2 | multivariate | 1.138 | 1.126 | 94 | 94 |
| CA | consumption | 1 | chronos2 | univariate | 1.323 | 1.303 | 140 | 140 |
| CA | consumption | 1 | combo_bench | multivariate | 0.862 | 0.866 | 135 | 135 |
| CA | consumption | 1 | combo_fm | univariate | 1.016 | 1.011 | 140 | 140 |
| CA | consumption | 1 | dfm | multivariate | 0.569 | 0.587 | 137 | 137 |
| CA | consumption | 1 | moirai2 | univariate | 1.036 | 1.030 | 140 | 140 |
| CA | consumption | 1 | naive | univariate | 0.815 | 0.824 | 140 | 140 |
| CA | consumption | 1 | timesfm25 | univariate | 0.961 | 0.959 | 140 | 140 |
| CA | consumption | 1 | tirex | univariate | 0.959 | 0.957 | 140 | 140 |
| CA | consumption | 1 | tirex2 | multivariate | 0.934 | 0.934 | 94 | 94 |
| CA | consumption | 1 | tirex2 | univariate | 0.846 | 0.854 | 140 | 140 |
| CA | consumption | 2 | bvar | multivariate | 1.150 | 1.147 | 135 | 135 |
| CA | consumption | 2 | chronos2 | multivariate | 1.045 | 1.047 | 92 | 92 |
| CA | consumption | 2 | chronos2 | univariate | 1.208 | 1.204 | 137 | 137 |
| CA | consumption | 2 | combo_bench | multivariate | 1.010 | 1.012 | 132 | 132 |
| CA | consumption | 2 | combo_fm | univariate | 1.010 | 1.013 | 137 | 137 |
| CA | consumption | 2 | dfm | multivariate | 0.967 | 0.967 | 134 | 134 |
| CA | consumption | 2 | moirai2 | univariate | 1.002 | 1.005 | 137 | 137 |
| CA | consumption | 2 | naive | univariate | 0.981 | 0.979 | 137 | 137 |
| CA | consumption | 2 | timesfm25 | univariate | 1.000 | 1.003 | 137 | 137 |
| CA | consumption | 2 | tirex | univariate | 0.983 | 0.985 | 137 | 137 |
| CA | consumption | 2 | tirex2 | multivariate | 0.993 | 0.995 | 92 | 92 |
| CA | consumption | 2 | tirex2 | univariate | 0.987 | 0.988 | 137 | 137 |
| CA | consumption | 4 | bvar | multivariate | 1.239 | 1.214 | 129 | 129 |
| CA | consumption | 4 | chronos2 | multivariate | 1.009 | 1.010 | 88 | 88 |
| CA | consumption | 4 | chronos2 | univariate | 1.118 | 1.107 | 131 | 131 |
| CA | consumption | 4 | combo_bench | multivariate | 1.014 | 1.009 | 126 | 126 |
| CA | consumption | 4 | combo_fm | univariate | 1.007 | 1.006 | 131 | 131 |
| CA | consumption | 4 | dfm | multivariate | 1.001 | 1.004 | 128 | 128 |
| CA | consumption | 4 | moirai2 | univariate | 1.005 | 1.004 | 131 | 131 |
| CA | consumption | 4 | naive | univariate | 1.004 | 1.007 | 131 | 131 |
| CA | consumption | 4 | timesfm25 | univariate | 1.000 | 1.000 | 131 | 131 |
| CA | consumption | 4 | tirex | univariate | 1.001 | 1.001 | 131 | 131 |
| CA | consumption | 4 | tirex2 | multivariate | 1.000 | 1.002 | 88 | 88 |
| CA | consumption | 4 | tirex2 | univariate | 0.994 | 0.996 | 131 | 131 |
| CA | cpi | 1 | bvar | multivariate | 0.976 | 0.976 | 141 | 141 |
| CA | cpi | 1 | chronos2 | multivariate | 0.844 | 0.844 | 142 | 142 |
| CA | cpi | 1 | chronos2 | univariate | 0.862 | 0.862 | 142 | 142 |
| CA | cpi | 1 | combo_bench | multivariate | 0.975 | 0.975 | 138 | 138 |
| CA | cpi | 1 | combo_fm | univariate | 0.856 | 0.856 | 142 | 142 |
| CA | cpi | 1 | dfm | multivariate | 0.988 | 0.988 | 139 | 139 |
| CA | cpi | 1 | moirai2 | univariate | 0.863 | 0.863 | 142 | 142 |
| CA | cpi | 1 | naive | univariate | 1.012 | 1.012 | 142 | 142 |
| CA | cpi | 1 | timesfm25 | univariate | 0.878 | 0.878 | 142 | 142 |
| CA | cpi | 1 | tirex | univariate | 0.886 | 0.886 | 142 | 142 |
| CA | cpi | 1 | tirex2 | multivariate | 0.856 | 0.856 | 142 | 142 |
| CA | cpi | 1 | tirex2 | univariate | 0.854 | 0.854 | 142 | 142 |
| CA | cpi | 3 | bvar | multivariate | 1.003 | 1.003 | 139 | 139 |
| CA | cpi | 3 | chronos2 | multivariate | 0.846 | 0.846 | 140 | 140 |
| CA | cpi | 3 | chronos2 | univariate | 0.822 | 0.822 | 140 | 140 |
| CA | cpi | 3 | combo_bench | multivariate | 1.000 | 1.000 | 136 | 136 |
| CA | cpi | 3 | combo_fm | univariate | 0.818 | 0.818 | 140 | 140 |
| CA | cpi | 3 | dfm | multivariate | 1.001 | 1.001 | 137 | 137 |
| CA | cpi | 3 | moirai2 | univariate | 0.840 | 0.840 | 140 | 140 |
| CA | cpi | 3 | naive | univariate | 0.998 | 0.998 | 140 | 140 |
| CA | cpi | 3 | timesfm25 | univariate | 0.814 | 0.814 | 140 | 140 |
| CA | cpi | 3 | tirex | univariate | 0.829 | 0.829 | 140 | 140 |
| CA | cpi | 3 | tirex2 | multivariate | 0.843 | 0.843 | 140 | 140 |
| CA | cpi | 3 | tirex2 | univariate | 0.831 | 0.831 | 140 | 140 |
| CA | cpi | 6 | bvar | multivariate | 1.014 | 1.014 | 136 | 136 |
| CA | cpi | 6 | chronos2 | multivariate | 0.895 | 0.895 | 137 | 137 |
| CA | cpi | 6 | chronos2 | univariate | 0.862 | 0.862 | 137 | 137 |
| CA | cpi | 6 | combo_bench | multivariate | 1.007 | 1.007 | 133 | 133 |
| CA | cpi | 6 | combo_fm | univariate | 0.851 | 0.851 | 137 | 137 |
| CA | cpi | 6 | dfm | multivariate | 1.011 | 1.011 | 134 | 134 |
| CA | cpi | 6 | moirai2 | univariate | 0.870 | 0.870 | 137 | 137 |
| CA | cpi | 6 | naive | univariate | 1.010 | 1.010 | 137 | 137 |
| CA | cpi | 6 | timesfm25 | univariate | 0.846 | 0.846 | 137 | 137 |
| CA | cpi | 6 | tirex | univariate | 0.852 | 0.852 | 137 | 137 |
| CA | cpi | 6 | tirex2 | multivariate | 0.883 | 0.883 | 137 | 137 |
| CA | cpi | 6 | tirex2 | univariate | 0.872 | 0.872 | 137 | 137 |
| CA | cpi | 12 | bvar | multivariate | 1.107 | 1.107 | 130 | 130 |
| CA | cpi | 12 | chronos2 | multivariate | 0.917 | 0.917 | 131 | 131 |
| CA | cpi | 12 | chronos2 | univariate | 0.891 | 0.891 | 131 | 131 |
| CA | cpi | 12 | combo_bench | multivariate | 1.060 | 1.060 | 127 | 127 |
| CA | cpi | 12 | combo_fm | univariate | 0.874 | 0.874 | 131 | 131 |
| CA | cpi | 12 | dfm | multivariate | 1.103 | 1.103 | 128 | 128 |
| CA | cpi | 12 | moirai2 | univariate | 0.892 | 0.892 | 131 | 131 |
| CA | cpi | 12 | naive | univariate | 1.104 | 1.104 | 131 | 131 |
| CA | cpi | 12 | timesfm25 | univariate | 0.874 | 0.874 | 131 | 131 |
| CA | cpi | 12 | tirex | univariate | 0.884 | 0.884 | 131 | 131 |
| CA | cpi | 12 | tirex2 | multivariate | 0.902 | 0.902 | 131 | 131 |
| CA | cpi | 12 | tirex2 | univariate | 0.888 | 0.888 | 131 | 131 |
| CA | cpi_core | 1 | bvar | multivariate | 1.223 | 1.223 | 141 | 141 |
| CA | cpi_core | 1 | chronos2 | multivariate | 0.999 | 0.999 | 142 | 142 |
| CA | cpi_core | 1 | chronos2 | univariate | 1.030 | 1.030 | 142 | 142 |
| CA | cpi_core | 1 | combo_bench | multivariate | 1.066 | 1.066 | 138 | 138 |
| CA | cpi_core | 1 | combo_fm | univariate | 0.967 | 0.967 | 142 | 142 |
| CA | cpi_core | 1 | dfm | multivariate | 1.179 | 1.179 | 139 | 139 |
| CA | cpi_core | 1 | moirai2 | univariate | 1.002 | 1.002 | 142 | 142 |
| CA | cpi_core | 1 | naive | univariate | 1.172 | 1.172 | 142 | 142 |
| CA | cpi_core | 1 | timesfm25 | univariate | 0.976 | 0.976 | 142 | 142 |
| CA | cpi_core | 1 | tirex | univariate | 0.959 | 0.959 | 142 | 142 |
| CA | cpi_core | 1 | tirex2 | multivariate | 0.950 | 0.950 | 142 | 142 |
| CA | cpi_core | 1 | tirex2 | univariate | 0.948 | 0.948 | 142 | 142 |
| CA | cpi_core | 3 | bvar | multivariate | 1.289 | 1.289 | 139 | 139 |
| CA | cpi_core | 3 | chronos2 | multivariate | 1.021 | 1.021 | 140 | 140 |
| CA | cpi_core | 3 | chronos2 | univariate | 1.046 | 1.046 | 140 | 140 |
| CA | cpi_core | 3 | combo_bench | multivariate | 1.129 | 1.129 | 136 | 136 |
| CA | cpi_core | 3 | combo_fm | univariate | 0.974 | 0.974 | 140 | 140 |
| CA | cpi_core | 3 | dfm | multivariate | 1.271 | 1.271 | 137 | 137 |
| CA | cpi_core | 3 | moirai2 | univariate | 0.999 | 0.999 | 140 | 140 |
| CA | cpi_core | 3 | naive | univariate | 1.268 | 1.268 | 140 | 140 |
| CA | cpi_core | 3 | timesfm25 | univariate | 0.961 | 0.961 | 140 | 140 |
| CA | cpi_core | 3 | tirex | univariate | 0.983 | 0.983 | 140 | 140 |
| CA | cpi_core | 3 | tirex2 | multivariate | 0.960 | 0.960 | 140 | 140 |
| CA | cpi_core | 3 | tirex2 | univariate | 0.950 | 0.950 | 140 | 140 |
| CA | cpi_core | 6 | bvar | multivariate | 1.255 | 1.255 | 136 | 136 |
| CA | cpi_core | 6 | chronos2 | multivariate | 1.059 | 1.059 | 137 | 137 |
| CA | cpi_core | 6 | chronos2 | univariate | 1.040 | 1.040 | 137 | 137 |
| CA | cpi_core | 6 | combo_bench | multivariate | 1.102 | 1.102 | 133 | 133 |
| CA | cpi_core | 6 | combo_fm | univariate | 0.963 | 0.963 | 137 | 137 |
| CA | cpi_core | 6 | dfm | multivariate | 1.237 | 1.237 | 134 | 134 |
| CA | cpi_core | 6 | moirai2 | univariate | 0.968 | 0.968 | 137 | 137 |
| CA | cpi_core | 6 | naive | univariate | 1.237 | 1.237 | 137 | 137 |
| CA | cpi_core | 6 | timesfm25 | univariate | 0.960 | 0.960 | 137 | 137 |
| CA | cpi_core | 6 | tirex | univariate | 0.970 | 0.970 | 137 | 137 |
| CA | cpi_core | 6 | tirex2 | multivariate | 0.992 | 0.992 | 137 | 137 |
| CA | cpi_core | 6 | tirex2 | univariate | 0.957 | 0.957 | 137 | 137 |
| CA | cpi_core | 12 | bvar | multivariate | 1.326 | 1.326 | 130 | 130 |
| CA | cpi_core | 12 | chronos2 | multivariate | 1.047 | 1.047 | 131 | 131 |
| CA | cpi_core | 12 | chronos2 | univariate | 0.995 | 0.995 | 131 | 131 |
| CA | cpi_core | 12 | combo_bench | multivariate | 1.135 | 1.135 | 127 | 127 |
| CA | cpi_core | 12 | combo_fm | univariate | 0.960 | 0.960 | 131 | 131 |
| CA | cpi_core | 12 | dfm | multivariate | 1.282 | 1.282 | 128 | 128 |
| CA | cpi_core | 12 | moirai2 | univariate | 0.990 | 0.990 | 131 | 131 |
| CA | cpi_core | 12 | naive | univariate | 1.316 | 1.316 | 131 | 131 |
| CA | cpi_core | 12 | timesfm25 | univariate | 0.958 | 0.958 | 131 | 131 |
| CA | cpi_core | 12 | tirex | univariate | 0.952 | 0.952 | 131 | 131 |
| CA | cpi_core | 12 | tirex2 | multivariate | 0.975 | 0.975 | 131 | 131 |
| CA | cpi_core | 12 | tirex2 | univariate | 0.965 | 0.965 | 131 | 131 |
| CA | gdp | 1 | bvar | multivariate | 1.119 | 1.121 | 140 | 140 |
| CA | gdp | 1 | chronos2 | multivariate | 1.070 | 1.072 | 94 | 94 |
| CA | gdp | 1 | chronos2 | univariate | 1.324 | 1.329 | 140 | 140 |
| CA | gdp | 1 | combo_bench | multivariate | 0.806 | 0.805 | 137 | 137 |
| CA | gdp | 1 | combo_fm | univariate | 0.996 | 0.998 | 140 | 140 |
| CA | gdp | 1 | dfm | multivariate | 0.407 | 0.400 | 137 | 137 |
| CA | gdp | 1 | moirai2 | univariate | 0.972 | 0.974 | 140 | 140 |
| CA | gdp | 1 | naive | univariate | 0.795 | 0.788 | 140 | 140 |
| CA | gdp | 1 | timesfm25 | univariate | 0.931 | 0.933 | 140 | 140 |
| CA | gdp | 1 | tirex | univariate | 0.957 | 0.959 | 140 | 140 |
| CA | gdp | 1 | tirex2 | multivariate | 0.945 | 0.945 | 94 | 94 |
| CA | gdp | 1 | tirex2 | univariate | 0.846 | 0.845 | 140 | 140 |
| CA | gdp | 2 | bvar | multivariate | 1.164 | 1.167 | 137 | 137 |
| CA | gdp | 2 | chronos2 | multivariate | 1.038 | 1.037 | 92 | 92 |
| CA | gdp | 2 | chronos2 | univariate | 1.351 | 1.356 | 137 | 137 |
| CA | gdp | 2 | combo_bench | multivariate | 1.003 | 1.003 | 134 | 134 |
| CA | gdp | 2 | combo_fm | univariate | 1.023 | 1.025 | 137 | 137 |
| CA | gdp | 2 | dfm | multivariate | 0.928 | 0.929 | 134 | 134 |
| CA | gdp | 2 | moirai2 | univariate | 0.999 | 1.000 | 137 | 137 |
| CA | gdp | 2 | naive | univariate | 0.946 | 0.945 | 137 | 137 |
| CA | gdp | 2 | timesfm25 | univariate | 1.005 | 1.010 | 137 | 137 |
| CA | gdp | 2 | tirex | univariate | 0.962 | 0.965 | 137 | 137 |
| CA | gdp | 2 | tirex2 | multivariate | 0.967 | 0.966 | 92 | 92 |
| CA | gdp | 2 | tirex2 | univariate | 0.951 | 0.951 | 137 | 137 |
| CA | gdp | 4 | bvar | multivariate | 1.121 | 1.116 | 131 | 131 |
| CA | gdp | 4 | chronos2 | multivariate | 1.003 | 1.001 | 88 | 88 |
| CA | gdp | 4 | chronos2 | univariate | 1.212 | 1.202 | 131 | 131 |
| CA | gdp | 4 | combo_bench | multivariate | 1.009 | 1.007 | 128 | 128 |
| CA | gdp | 4 | combo_fm | univariate | 1.004 | 1.002 | 131 | 131 |
| CA | gdp | 4 | dfm | multivariate | 1.000 | 1.004 | 128 | 128 |
| CA | gdp | 4 | moirai2 | univariate | 0.994 | 0.994 | 131 | 131 |
| CA | gdp | 4 | naive | univariate | 1.000 | 1.004 | 131 | 131 |
| CA | gdp | 4 | timesfm25 | univariate | 0.996 | 0.997 | 131 | 131 |
| CA | gdp | 4 | tirex | univariate | 0.992 | 0.995 | 131 | 131 |
| CA | gdp | 4 | tirex2 | multivariate | 0.995 | 0.997 | 88 | 88 |
| CA | gdp | 4 | tirex2 | univariate | 0.992 | 0.995 | 131 | 131 |
| CA | retail | 1 | bvar | multivariate | 0.567 | 0.575 | 139 | 139 |
| CA | retail | 1 | chronos2 | multivariate | 1.161 | 1.188 | 140 | 140 |
| CA | retail | 1 | chronos2 | univariate | 1.222 | 1.250 | 140 | 140 |
| CA | retail | 1 | combo_bench | multivariate | 0.717 | 0.719 | 136 | 136 |
| CA | retail | 1 | combo_fm | univariate | 1.034 | 1.055 | 140 | 140 |
| CA | retail | 1 | dfm | multivariate | 0.725 | 0.738 | 137 | 137 |
| CA | retail | 1 | moirai2 | univariate | 1.041 | 1.065 | 140 | 140 |
| CA | retail | 1 | naive | univariate | 0.908 | 0.914 | 140 | 140 |
| CA | retail | 1 | timesfm25 | univariate | 0.959 | 0.974 | 140 | 140 |
| CA | retail | 1 | tirex | univariate | 0.981 | 0.998 | 140 | 140 |
| CA | retail | 1 | tirex2 | multivariate | 0.954 | 0.965 | 140 | 140 |
| CA | retail | 1 | tirex2 | univariate | 1.023 | 1.038 | 140 | 140 |
| CA | retail | 3 | bvar | multivariate | 0.976 | 0.968 | 138 | 138 |
| CA | retail | 3 | chronos2 | multivariate | 1.124 | 1.103 | 139 | 139 |
| CA | retail | 3 | chronos2 | univariate | 1.164 | 1.142 | 139 | 139 |
| CA | retail | 3 | combo_bench | multivariate | 0.976 | 0.972 | 135 | 135 |
| CA | retail | 3 | combo_fm | univariate | 0.998 | 0.991 | 139 | 139 |
| CA | retail | 3 | dfm | multivariate | 0.974 | 0.970 | 136 | 136 |
| CA | retail | 3 | moirai2 | univariate | 0.994 | 0.987 | 139 | 139 |
| CA | retail | 3 | naive | univariate | 0.980 | 0.977 | 139 | 139 |
| CA | retail | 3 | timesfm25 | univariate | 0.980 | 0.975 | 139 | 139 |
| CA | retail | 3 | tirex | univariate | 0.978 | 0.974 | 139 | 139 |
| CA | retail | 3 | tirex2 | multivariate | 0.981 | 0.977 | 139 | 139 |
| CA | retail | 3 | tirex2 | univariate | 0.983 | 0.978 | 139 | 139 |
| CA | retail | 6 | bvar | multivariate | 0.971 | 0.963 | 135 | 135 |
| CA | retail | 6 | chronos2 | multivariate | 1.062 | 1.050 | 136 | 136 |
| CA | retail | 6 | chronos2 | univariate | 1.130 | 1.116 | 136 | 136 |
| CA | retail | 6 | combo_bench | multivariate | 0.973 | 0.967 | 132 | 132 |
| CA | retail | 6 | combo_fm | univariate | 0.971 | 0.962 | 136 | 136 |
| CA | retail | 6 | dfm | multivariate | 0.956 | 0.945 | 133 | 133 |
| CA | retail | 6 | moirai2 | univariate | 0.961 | 0.952 | 136 | 136 |
| CA | retail | 6 | naive | univariate | 0.955 | 0.944 | 136 | 136 |
| CA | retail | 6 | timesfm25 | univariate | 0.959 | 0.950 | 136 | 136 |
| CA | retail | 6 | tirex | univariate | 0.964 | 0.954 | 136 | 136 |
| CA | retail | 6 | tirex2 | multivariate | 0.956 | 0.946 | 136 | 136 |
| CA | retail | 6 | tirex2 | univariate | 0.957 | 0.948 | 136 | 136 |
| CA | retail | 12 | bvar | multivariate | 0.995 | 0.995 | 130 | 130 |
| CA | retail | 12 | chronos2 | multivariate | 1.005 | 1.009 | 131 | 131 |
| CA | retail | 12 | chronos2 | univariate | 1.074 | 1.075 | 131 | 131 |
| CA | retail | 12 | combo_bench | multivariate | 0.994 | 0.994 | 127 | 127 |
| CA | retail | 12 | combo_fm | univariate | 0.970 | 0.974 | 131 | 131 |
| CA | retail | 12 | dfm | multivariate | 0.981 | 0.982 | 128 | 128 |
| CA | retail | 12 | moirai2 | univariate | 0.975 | 0.978 | 131 | 131 |
| CA | retail | 12 | naive | univariate | 0.981 | 0.983 | 131 | 131 |
| CA | retail | 12 | timesfm25 | univariate | 0.978 | 0.980 | 131 | 131 |
| CA | retail | 12 | tirex | univariate | 0.986 | 0.987 | 131 | 131 |
| CA | retail | 12 | tirex2 | multivariate | 0.981 | 0.983 | 131 | 131 |
| CA | retail | 12 | tirex2 | univariate | 0.982 | 0.984 | 131 | 131 |
| CA | unemp | 1 | bvar | multivariate | 0.970 | 0.964 | 141 | 141 |
| CA | unemp | 1 | chronos2 | multivariate | 1.339 | 1.372 | 142 | 142 |
| CA | unemp | 1 | chronos2 | univariate | 1.100 | 1.116 | 142 | 142 |
| CA | unemp | 1 | combo_bench | multivariate | 0.971 | 0.971 | 138 | 138 |
| CA | unemp | 1 | combo_fm | univariate | 0.987 | 0.992 | 142 | 142 |
| CA | unemp | 1 | dfm | multivariate | 1.006 | 1.019 | 139 | 139 |
| CA | unemp | 1 | moirai2 | univariate | 0.929 | 0.928 | 142 | 142 |
| CA | unemp | 1 | naive | univariate | 0.942 | 0.930 | 142 | 142 |
| CA | unemp | 1 | timesfm25 | univariate | 0.979 | 0.984 | 142 | 142 |
| CA | unemp | 1 | tirex | univariate | 1.007 | 1.015 | 142 | 142 |
| CA | unemp | 1 | tirex2 | multivariate | 1.097 | 1.112 | 142 | 142 |
| CA | unemp | 1 | tirex2 | univariate | 0.999 | 1.000 | 142 | 142 |
| CA | unemp | 3 | bvar | multivariate | 1.022 | 1.022 | 140 | 140 |
| CA | unemp | 3 | chronos2 | multivariate | 1.305 | 1.320 | 141 | 141 |
| CA | unemp | 3 | chronos2 | univariate | 1.082 | 1.088 | 141 | 141 |
| CA | unemp | 3 | combo_bench | multivariate | 0.998 | 0.998 | 137 | 137 |
| CA | unemp | 3 | combo_fm | univariate | 1.004 | 1.005 | 141 | 141 |
| CA | unemp | 3 | dfm | multivariate | 0.979 | 0.980 | 138 | 138 |
| CA | unemp | 3 | moirai2 | univariate | 0.983 | 0.978 | 141 | 141 |
| CA | unemp | 3 | naive | univariate | 0.965 | 0.962 | 141 | 141 |
| CA | unemp | 3 | timesfm25 | univariate | 1.008 | 1.009 | 141 | 141 |
| CA | unemp | 3 | tirex | univariate | 0.987 | 0.987 | 141 | 141 |
| CA | unemp | 3 | tirex2 | multivariate | 1.025 | 1.028 | 141 | 141 |
| CA | unemp | 3 | tirex2 | univariate | 0.998 | 0.999 | 141 | 141 |
| CA | unemp | 6 | bvar | multivariate | 1.008 | 1.007 | 137 | 137 |
| CA | unemp | 6 | chronos2 | multivariate | 1.117 | 1.127 | 138 | 138 |
| CA | unemp | 6 | chronos2 | univariate | 1.007 | 1.008 | 138 | 138 |
| CA | unemp | 6 | combo_bench | multivariate | 1.003 | 1.002 | 134 | 134 |
| CA | unemp | 6 | combo_fm | univariate | 1.001 | 1.000 | 138 | 138 |
| CA | unemp | 6 | dfm | multivariate | 1.001 | 1.001 | 135 | 135 |
| CA | unemp | 6 | moirai2 | univariate | 1.019 | 1.018 | 138 | 138 |
| CA | unemp | 6 | naive | univariate | 0.999 | 0.998 | 138 | 138 |
| CA | unemp | 6 | timesfm25 | univariate | 1.005 | 1.004 | 138 | 138 |
| CA | unemp | 6 | tirex | univariate | 1.002 | 1.001 | 138 | 138 |
| CA | unemp | 6 | tirex2 | multivariate | 1.000 | 1.000 | 138 | 138 |
| CA | unemp | 6 | tirex2 | univariate | 0.998 | 0.998 | 138 | 138 |
| CA | unemp | 12 | bvar | multivariate | 0.990 | 0.991 | 131 | 131 |
| CA | unemp | 12 | chronos2 | multivariate | 0.980 | 0.984 | 132 | 132 |
| CA | unemp | 12 | chronos2 | univariate | 0.983 | 0.987 | 132 | 132 |
| CA | unemp | 12 | combo_bench | multivariate | 0.991 | 0.992 | 128 | 128 |
| CA | unemp | 12 | combo_fm | univariate | 0.984 | 0.989 | 132 | 132 |
| CA | unemp | 12 | dfm | multivariate | 0.987 | 0.989 | 129 | 129 |
| CA | unemp | 12 | moirai2 | univariate | 0.997 | 1.006 | 132 | 132 |
| CA | unemp | 12 | naive | univariate | 0.987 | 0.988 | 132 | 132 |
| CA | unemp | 12 | timesfm25 | univariate | 0.992 | 0.998 | 132 | 132 |
| CA | unemp | 12 | tirex | univariate | 0.984 | 0.988 | 132 | 132 |
| CA | unemp | 12 | tirex2 | multivariate | 0.987 | 0.990 | 132 | 132 |
| CA | unemp | 12 | tirex2 | univariate | 0.987 | 0.990 | 132 | 132 |
| EA | consumption | 1 | bvar | multivariate | 0.570 | 0.340 | 130 | 131 |
| EA | consumption | 1 | chronos2 | multivariate | 0.643 | 0.634 | 133 | 134 |
| EA | consumption | 1 | chronos2 | univariate | 0.700 | 0.707 | 133 | 134 |
| EA | consumption | 1 | combo_bench | multivariate | 0.628 | 0.486 | 130 | 131 |
| EA | consumption | 1 | combo_fm | univariate | 0.600 | 0.585 | 133 | 134 |
| EA | consumption | 1 | dfm | multivariate | 0.466 | 0.426 | 133 | 134 |
| EA | consumption | 1 | moirai2 | univariate | 0.579 | 0.558 | 133 | 134 |
| EA | consumption | 1 | naive | univariate | 0.420 | 0.356 | 133 | 134 |
| EA | consumption | 1 | timesfm25 | univariate | 0.504 | 0.476 | 133 | 134 |
| EA | consumption | 1 | tirex | univariate | 0.670 | 0.657 | 133 | 134 |
| EA | consumption | 1 | tirex2 | multivariate | 0.572 | 0.545 | 133 | 134 |
| EA | consumption | 1 | tirex2 | univariate | 0.573 | 0.545 | 133 | 134 |
| EA | consumption | 2 | bvar | multivariate | 0.717 | 0.535 | 127 | 126 |
| EA | consumption | 2 | chronos2 | multivariate | 0.782 | 0.631 | 130 | 129 |
| EA | consumption | 2 | chronos2 | univariate | 0.869 | 0.750 | 130 | 129 |
| EA | consumption | 2 | combo_bench | multivariate | 0.727 | 0.554 | 127 | 126 |
| EA | consumption | 2 | combo_fm | univariate | 0.736 | 0.575 | 130 | 129 |
| EA | consumption | 2 | dfm | multivariate | 0.663 | 0.480 | 130 | 129 |
| EA | consumption | 2 | moirai2 | univariate | 0.714 | 0.537 | 130 | 129 |
| EA | consumption | 2 | naive | univariate | 0.679 | 0.477 | 130 | 129 |
| EA | consumption | 2 | timesfm25 | univariate | 0.721 | 0.560 | 130 | 129 |
| EA | consumption | 2 | tirex | univariate | 0.771 | 0.626 | 130 | 129 |
| EA | consumption | 2 | tirex2 | multivariate | 0.697 | 0.517 | 130 | 129 |
| EA | consumption | 2 | tirex2 | univariate | 0.695 | 0.515 | 130 | 129 |
| EA | consumption | 4 | bvar | multivariate | 0.913 | 0.853 | 124 | 121 |
| EA | consumption | 4 | chronos2 | multivariate | 0.911 | 1.039 | 124 | 124 |
| EA | consumption | 4 | chronos2 | univariate | 0.908 | 1.235 | 124 | 124 |
| EA | consumption | 4 | combo_bench | multivariate | 0.916 | 0.860 | 124 | 121 |
| EA | consumption | 4 | combo_fm | univariate | 0.906 | 0.909 | 124 | 124 |
| EA | consumption | 4 | dfm | multivariate | 0.915 | 0.785 | 124 | 124 |
| EA | consumption | 4 | moirai2 | univariate | 0.912 | 0.892 | 124 | 124 |
| EA | consumption | 4 | naive | univariate | 0.916 | 0.781 | 124 | 124 |
| EA | consumption | 4 | timesfm25 | univariate | 0.912 | 0.791 | 124 | 124 |
| EA | consumption | 4 | tirex | univariate | 0.911 | 0.966 | 124 | 124 |
| EA | consumption | 4 | tirex2 | multivariate | 0.907 | 0.808 | 124 | 124 |
| EA | consumption | 4 | tirex2 | univariate | 0.907 | 0.808 | 124 | 124 |
| EA | gdp | 1 | bvar | multivariate | 0.411 | 0.325 | 133 | 132 |
| EA | gdp | 1 | chronos2 | multivariate | 0.642 | 0.557 | 132 | 131 |
| EA | gdp | 1 | chronos2 | univariate | 0.840 | 0.817 | 133 | 132 |
| EA | gdp | 1 | combo_bench | multivariate | 0.610 | 0.561 | 133 | 132 |
| EA | gdp | 1 | combo_fm | univariate | 0.707 | 0.634 | 133 | 132 |
| EA | gdp | 1 | dfm | multivariate | 0.496 | 0.427 | 133 | 132 |
| EA | gdp | 1 | moirai2 | univariate | 0.687 | 0.600 | 133 | 132 |
| EA | gdp | 1 | naive | univariate | 0.567 | 0.389 | 133 | 132 |
| EA | gdp | 1 | timesfm25 | univariate | 0.625 | 0.519 | 133 | 132 |
| EA | gdp | 1 | tirex | univariate | 0.795 | 0.751 | 133 | 132 |
| EA | gdp | 1 | tirex2 | multivariate | 0.617 | 0.497 | 132 | 131 |
| EA | gdp | 1 | tirex2 | univariate | 0.619 | 0.493 | 133 | 132 |
| EA | gdp | 2 | bvar | multivariate | 1.025 | 1.015 | 129 | 130 |
| EA | gdp | 2 | chronos2 | multivariate | 0.919 | 0.883 | 128 | 129 |
| EA | gdp | 2 | chronos2 | univariate | 1.099 | 1.132 | 129 | 130 |
| EA | gdp | 2 | combo_bench | multivariate | 0.940 | 0.907 | 129 | 130 |
| EA | gdp | 2 | combo_fm | univariate | 0.927 | 0.900 | 129 | 130 |
| EA | gdp | 2 | dfm | multivariate | 0.916 | 0.871 | 129 | 130 |
| EA | gdp | 2 | moirai2 | univariate | 0.907 | 0.871 | 129 | 130 |
| EA | gdp | 2 | naive | univariate | 0.867 | 0.806 | 129 | 130 |
| EA | gdp | 2 | timesfm25 | univariate | 0.919 | 0.884 | 129 | 130 |
| EA | gdp | 2 | tirex | univariate | 0.936 | 0.915 | 129 | 130 |
| EA | gdp | 2 | tirex2 | multivariate | 0.886 | 0.839 | 128 | 129 |
| EA | gdp | 2 | tirex2 | univariate | 0.883 | 0.834 | 129 | 130 |
| EA | gdp | 4 | bvar | multivariate | 1.006 | 1.004 | 124 | 124 |
| EA | gdp | 4 | chronos2 | multivariate | 1.006 | 0.981 | 123 | 123 |
| EA | gdp | 4 | chronos2 | univariate | 1.003 | 1.252 | 124 | 124 |
| EA | gdp | 4 | combo_bench | multivariate | 1.002 | 0.939 | 124 | 124 |
| EA | gdp | 4 | combo_fm | univariate | 1.002 | 1.002 | 124 | 124 |
| EA | gdp | 4 | dfm | multivariate | 1.002 | 0.949 | 124 | 124 |
| EA | gdp | 4 | moirai2 | univariate | 1.003 | 0.991 | 124 | 124 |
| EA | gdp | 4 | naive | univariate | 1.002 | 0.946 | 124 | 124 |
| EA | gdp | 4 | timesfm25 | univariate | 1.009 | 0.968 | 124 | 124 |
| EA | gdp | 4 | tirex | univariate | 1.001 | 0.983 | 124 | 124 |
| EA | gdp | 4 | tirex2 | multivariate | 1.002 | 0.954 | 123 | 123 |
| EA | gdp | 4 | tirex2 | univariate | 1.003 | 0.953 | 124 | 124 |
| EA | hicp | 1 | bvar | multivariate | 0.803 | 0.806 | 142 | 141 |
| EA | hicp | 1 | chronos2 | multivariate | 0.894 | 0.891 | 142 | 141 |
| EA | hicp | 1 | chronos2 | univariate | 0.926 | 0.923 | 142 | 141 |
| EA | hicp | 1 | combo_bench | multivariate | 0.908 | 0.909 | 140 | 139 |
| EA | hicp | 1 | combo_fm | univariate | 0.926 | 0.924 | 142 | 141 |
| EA | hicp | 1 | dfm | multivariate | 1.420 | 1.417 | 140 | 139 |
| EA | hicp | 1 | moirai2 | univariate | 0.937 | 0.935 | 142 | 141 |
| EA | hicp | 1 | naive | univariate | 1.486 | 1.483 | 142 | 141 |
| EA | hicp | 1 | timesfm25 | univariate | 0.940 | 0.937 | 142 | 141 |
| EA | hicp | 1 | tirex | univariate | 1.024 | 1.019 | 142 | 141 |
| EA | hicp | 1 | tirex2 | multivariate | 0.964 | 0.961 | 142 | 141 |
| EA | hicp | 1 | tirex2 | univariate | 0.980 | 0.977 | 142 | 141 |
| EA | hicp | 3 | bvar | multivariate | 0.851 | 0.842 | 140 | 138 |
| EA | hicp | 3 | chronos2 | multivariate | 0.933 | 0.928 | 140 | 138 |
| EA | hicp | 3 | chronos2 | univariate | 0.973 | 0.967 | 140 | 138 |
| EA | hicp | 3 | combo_bench | multivariate | 0.862 | 0.861 | 138 | 136 |
| EA | hicp | 3 | combo_fm | univariate | 0.950 | 0.946 | 140 | 138 |
| EA | hicp | 3 | dfm | multivariate | 1.161 | 1.145 | 138 | 136 |
| EA | hicp | 3 | moirai2 | univariate | 0.987 | 0.981 | 140 | 138 |
| EA | hicp | 3 | naive | univariate | 1.118 | 1.104 | 140 | 138 |
| EA | hicp | 3 | timesfm25 | univariate | 0.931 | 0.926 | 140 | 138 |
| EA | hicp | 3 | tirex | univariate | 0.985 | 0.980 | 140 | 138 |
| EA | hicp | 3 | tirex2 | multivariate | 0.990 | 0.986 | 140 | 138 |
| EA | hicp | 3 | tirex2 | univariate | 1.001 | 0.995 | 140 | 138 |
| EA | hicp | 6 | bvar | multivariate | 0.986 | 0.978 | 136 | 134 |
| EA | hicp | 6 | chronos2 | multivariate | 0.934 | 0.929 | 136 | 134 |
| EA | hicp | 6 | chronos2 | univariate | 0.983 | 0.974 | 136 | 134 |
| EA | hicp | 6 | combo_bench | multivariate | 0.961 | 0.960 | 134 | 132 |
| EA | hicp | 6 | combo_fm | univariate | 0.989 | 0.979 | 136 | 134 |
| EA | hicp | 6 | dfm | multivariate | 1.262 | 1.247 | 134 | 132 |
| EA | hicp | 6 | moirai2 | univariate | 1.030 | 1.017 | 136 | 134 |
| EA | hicp | 6 | naive | univariate | 1.259 | 1.241 | 136 | 134 |
| EA | hicp | 6 | timesfm25 | univariate | 0.997 | 0.985 | 136 | 134 |
| EA | hicp | 6 | tirex | univariate | 1.016 | 1.004 | 136 | 134 |
| EA | hicp | 6 | tirex2 | multivariate | 1.026 | 1.017 | 136 | 134 |
| EA | hicp | 6 | tirex2 | univariate | 1.043 | 1.033 | 136 | 134 |
| EA | hicp | 12 | bvar | multivariate | 1.034 | 1.034 | 131 | 130 |
| EA | hicp | 12 | chronos2 | multivariate | 0.989 | 0.988 | 131 | 130 |
| EA | hicp | 12 | chronos2 | univariate | 1.148 | 1.143 | 131 | 130 |
| EA | hicp | 12 | combo_bench | multivariate | 0.986 | 0.986 | 129 | 128 |
| EA | hicp | 12 | combo_fm | univariate | 1.138 | 1.132 | 131 | 130 |
| EA | hicp | 12 | dfm | multivariate | 1.246 | 1.241 | 129 | 128 |
| EA | hicp | 12 | moirai2 | univariate | 1.156 | 1.149 | 131 | 130 |
| EA | hicp | 12 | naive | univariate | 1.248 | 1.243 | 131 | 130 |
| EA | hicp | 12 | timesfm25 | univariate | 1.119 | 1.111 | 131 | 130 |
| EA | hicp | 12 | tirex | univariate | 1.161 | 1.155 | 131 | 130 |
| EA | hicp | 12 | tirex2 | multivariate | 1.205 | 1.198 | 131 | 130 |
| EA | hicp | 12 | tirex2 | univariate | 1.249 | 1.242 | 131 | 130 |
| EA | hicp_core | 1 | bvar | multivariate | 1.401 | 1.401 | 142 | 142 |
| EA | hicp_core | 1 | chronos2 | multivariate | 0.795 | 0.795 | 102 | 102 |
| EA | hicp_core | 1 | chronos2 | univariate | 0.879 | 0.879 | 142 | 142 |
| EA | hicp_core | 1 | combo_bench | multivariate | 1.377 | 1.377 | 140 | 140 |
| EA | hicp_core | 1 | combo_fm | univariate | 0.841 | 0.841 | 142 | 142 |
| EA | hicp_core | 1 | dfm | multivariate | 2.847 | 2.847 | 140 | 140 |
| EA | hicp_core | 1 | moirai2 | univariate | 0.875 | 0.875 | 142 | 142 |
| EA | hicp_core | 1 | naive | univariate | 2.760 | 2.760 | 142 | 142 |
| EA | hicp_core | 1 | timesfm25 | univariate | 0.859 | 0.859 | 142 | 142 |
| EA | hicp_core | 1 | tirex | univariate | 0.938 | 0.938 | 142 | 142 |
| EA | hicp_core | 1 | tirex2 | multivariate | 0.873 | 0.873 | 102 | 102 |
| EA | hicp_core | 1 | tirex2 | univariate | 0.865 | 0.865 | 142 | 142 |
| EA | hicp_core | 3 | bvar | multivariate | 1.430 | 1.430 | 140 | 140 |
| EA | hicp_core | 3 | chronos2 | multivariate | 0.849 | 0.849 | 101 | 101 |
| EA | hicp_core | 3 | chronos2 | univariate | 0.951 | 0.951 | 140 | 140 |
| EA | hicp_core | 3 | combo_bench | multivariate | 1.340 | 1.340 | 138 | 138 |

_128 more rows in the CSV_

### 5.3 Q2: before and after the weights date

| econ | target | horizon | model | variant | rel_rmsfe:post | rel_rmsfe:pre | n:post | n:pre |
|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | chronos2 | multivariate | 0.668 | 1.139 | 7 | 87 |
| CA | consumption | 1 | chronos2 | univariate | 0.652 | 1.323 | 10 | 130 |
| CA | consumption | 1 | moirai2 | univariate | 0.873 | 1.037 | 13 | 127 |
| CA | consumption | 1 | timesfm25 | univariate | 0.815 | 0.961 | 11 | 129 |
| CA | consumption | 1 | tirex | univariate | 0.963 | 0.959 | 16 | 124 |
| CA | consumption | 1 | tirex2 | multivariate |  | 0.934 |  | 94 |
| CA | consumption | 1 | tirex2 | univariate |  | 0.846 |  | 140 |
| CA | consumption | 2 | chronos2 | multivariate | 0.767 | 1.045 | 5 | 87 |
| CA | consumption | 2 | chronos2 | univariate | 0.913 | 1.208 | 7 | 130 |
| CA | consumption | 2 | moirai2 | univariate | 0.916 | 1.002 | 10 | 127 |
| CA | consumption | 2 | timesfm25 | univariate | 0.848 | 1.000 | 8 | 129 |
| CA | consumption | 2 | tirex | univariate | 0.939 | 0.984 | 13 | 124 |
| CA | consumption | 2 | tirex2 | multivariate |  | 0.993 |  | 92 |
| CA | consumption | 2 | tirex2 | univariate |  | 0.987 |  | 137 |
| CA | consumption | 4 | chronos2 | multivariate | 8.298 | 1.009 | 1 | 87 |
| CA | consumption | 4 | chronos2 | univariate | 4.245 | 1.118 | 1 | 130 |
| CA | consumption | 4 | moirai2 | univariate | 1.159 | 1.004 | 4 | 127 |
| CA | consumption | 4 | timesfm25 | univariate | 4.001 | 1.000 | 2 | 129 |
| CA | consumption | 4 | tirex | univariate | 0.916 | 1.001 | 7 | 124 |
| CA | consumption | 4 | tirex2 | multivariate |  | 1.000 |  | 88 |
| CA | consumption | 4 | tirex2 | univariate |  | 0.994 |  | 131 |
| CA | cpi | 1 | chronos2 | multivariate | 0.747 | 0.854 | 12 | 130 |
| CA | cpi | 1 | chronos2 | univariate | 0.719 | 0.876 | 12 | 130 |
| CA | cpi | 1 | moirai2 | univariate | 0.812 | 0.869 | 15 | 127 |
| CA | cpi | 1 | timesfm25 | univariate | 0.762 | 0.889 | 13 | 129 |
| CA | cpi | 1 | tirex | univariate | 0.800 | 0.897 | 18 | 124 |
| CA | cpi | 1 | tirex2 | multivariate | 1.169 | 0.856 | 1 | 141 |
| CA | cpi | 1 | tirex2 | univariate | 1.518 | 0.854 | 1 | 141 |
| CA | cpi | 3 | chronos2 | multivariate | 0.685 | 0.861 | 10 | 130 |
| CA | cpi | 3 | chronos2 | univariate | 0.681 | 0.836 | 10 | 130 |
| CA | cpi | 3 | moirai2 | univariate | 0.643 | 0.860 | 13 | 127 |
| CA | cpi | 3 | timesfm25 | univariate | 0.642 | 0.831 | 11 | 129 |
| CA | cpi | 3 | tirex | univariate | 0.700 | 0.844 | 16 | 124 |
| CA | cpi | 3 | tirex2 | multivariate |  | 0.843 |  | 140 |
| CA | cpi | 3 | tirex2 | univariate |  | 0.831 |  | 140 |
| CA | cpi | 6 | chronos2 | multivariate | 0.657 | 0.909 | 7 | 130 |
| CA | cpi | 6 | chronos2 | univariate | 0.738 | 0.870 | 7 | 130 |
| CA | cpi | 6 | moirai2 | univariate | 0.764 | 0.880 | 10 | 127 |
| CA | cpi | 6 | timesfm25 | univariate | 0.705 | 0.859 | 8 | 129 |
| CA | cpi | 6 | tirex | univariate | 0.773 | 0.861 | 13 | 124 |
| CA | cpi | 6 | tirex2 | multivariate |  | 0.883 |  | 137 |
| CA | cpi | 6 | tirex2 | univariate |  | 0.872 |  | 137 |
| CA | cpi | 12 | chronos2 | multivariate | 0.491 | 0.917 | 1 | 130 |
| CA | cpi | 12 | chronos2 | univariate | 4.841 | 0.890 | 1 | 130 |
| CA | cpi | 12 | moirai2 | univariate | 0.821 | 0.892 | 4 | 127 |
| CA | cpi | 12 | timesfm25 | univariate | 2.712 | 0.873 | 2 | 129 |
| CA | cpi | 12 | tirex | univariate | 0.957 | 0.880 | 7 | 124 |
| CA | cpi | 12 | tirex2 | multivariate |  | 0.902 |  | 131 |
| CA | cpi | 12 | tirex2 | univariate |  | 0.888 |  | 131 |
| CA | cpi_core | 1 | chronos2 | multivariate | 0.975 | 1.002 | 12 | 130 |
| CA | cpi_core | 1 | chronos2 | univariate | 0.967 | 1.038 | 12 | 130 |
| CA | cpi_core | 1 | moirai2 | univariate | 1.018 | 0.999 | 15 | 127 |
| CA | cpi_core | 1 | timesfm25 | univariate | 0.914 | 0.984 | 13 | 129 |
| CA | cpi_core | 1 | tirex | univariate | 0.871 | 0.971 | 18 | 124 |
| CA | cpi_core | 1 | tirex2 | multivariate | 1.108 | 0.950 | 1 | 141 |
| CA | cpi_core | 1 | tirex2 | univariate | 2.049 | 0.947 | 1 | 141 |
| CA | cpi_core | 3 | chronos2 | multivariate | 1.039 | 1.019 | 10 | 130 |
| CA | cpi_core | 3 | chronos2 | univariate | 1.031 | 1.047 | 10 | 130 |
| CA | cpi_core | 3 | moirai2 | univariate | 1.014 | 0.998 | 13 | 127 |
| CA | cpi_core | 3 | timesfm25 | univariate | 0.985 | 0.959 | 11 | 129 |
| CA | cpi_core | 3 | tirex | univariate | 0.920 | 0.989 | 16 | 124 |
| CA | cpi_core | 3 | tirex2 | multivariate |  | 0.960 |  | 140 |
| CA | cpi_core | 3 | tirex2 | univariate |  | 0.950 |  | 140 |
| CA | cpi_core | 6 | chronos2 | multivariate | 1.086 | 1.058 | 7 | 130 |
| CA | cpi_core | 6 | chronos2 | univariate | 1.042 | 1.040 | 7 | 130 |
| CA | cpi_core | 6 | moirai2 | univariate | 0.893 | 0.973 | 10 | 127 |
| CA | cpi_core | 6 | timesfm25 | univariate | 1.057 | 0.957 | 8 | 129 |
| CA | cpi_core | 6 | tirex | univariate | 0.994 | 0.968 | 13 | 124 |
| CA | cpi_core | 6 | tirex2 | multivariate |  | 0.992 |  | 137 |
| CA | cpi_core | 6 | tirex2 | univariate |  | 0.957 |  | 137 |
| CA | cpi_core | 12 | chronos2 | multivariate | 1.836 | 1.047 | 1 | 130 |
| CA | cpi_core | 12 | chronos2 | univariate | 1.426 | 0.995 | 1 | 130 |
| CA | cpi_core | 12 | moirai2 | univariate | 1.113 | 0.989 | 4 | 127 |
| CA | cpi_core | 12 | timesfm25 | univariate | 1.246 | 0.957 | 2 | 129 |
| CA | cpi_core | 12 | tirex | univariate | 0.855 | 0.956 | 7 | 124 |
| CA | cpi_core | 12 | tirex2 | multivariate |  | 0.975 |  | 131 |
| CA | cpi_core | 12 | tirex2 | univariate |  | 0.965 |  | 131 |
| CA | gdp | 1 | chronos2 | multivariate | 0.839 | 1.070 | 7 | 87 |
| CA | gdp | 1 | chronos2 | univariate | 0.882 | 1.325 | 10 | 130 |
| CA | gdp | 1 | moirai2 | univariate | 0.887 | 0.972 | 13 | 127 |
| CA | gdp | 1 | timesfm25 | univariate | 0.957 | 0.931 | 11 | 129 |
| CA | gdp | 1 | tirex | univariate | 0.902 | 0.957 | 16 | 124 |
| CA | gdp | 1 | tirex2 | multivariate |  | 0.945 |  | 94 |
| CA | gdp | 1 | tirex2 | univariate |  | 0.846 |  | 140 |
| CA | gdp | 2 | chronos2 | multivariate | 0.850 | 1.038 | 5 | 87 |
| CA | gdp | 2 | chronos2 | univariate | 0.868 | 1.353 | 7 | 130 |
| CA | gdp | 2 | moirai2 | univariate | 0.834 | 0.999 | 10 | 127 |
| CA | gdp | 2 | timesfm25 | univariate | 0.854 | 1.005 | 8 | 129 |
| CA | gdp | 2 | tirex | univariate | 0.825 | 0.963 | 13 | 124 |
| CA | gdp | 2 | tirex2 | multivariate |  | 0.967 |  | 92 |
| CA | gdp | 2 | tirex2 | univariate |  | 0.951 |  | 137 |
| CA | gdp | 4 | chronos2 | multivariate | 1.374 | 1.003 | 1 | 87 |
| CA | gdp | 4 | chronos2 | univariate | 1.668 | 1.212 | 1 | 130 |
| CA | gdp | 4 | moirai2 | univariate | 1.079 | 0.994 | 4 | 127 |
| CA | gdp | 4 | timesfm25 | univariate | 1.853 | 0.996 | 2 | 129 |
| CA | gdp | 4 | tirex | univariate | 0.915 | 0.992 | 7 | 124 |
| CA | gdp | 4 | tirex2 | multivariate |  | 0.995 |  | 88 |
| CA | gdp | 4 | tirex2 | univariate |  | 0.992 |  | 131 |
| CA | retail | 1 | chronos2 | multivariate | 0.764 | 1.163 | 12 | 128 |
| CA | retail | 1 | chronos2 | univariate | 0.849 | 1.224 | 12 | 128 |
| CA | retail | 1 | moirai2 | univariate | 0.821 | 1.043 | 15 | 125 |
| CA | retail | 1 | timesfm25 | univariate | 0.856 | 0.960 | 13 | 127 |
| CA | retail | 1 | tirex | univariate | 0.929 | 0.981 | 18 | 122 |
| CA | retail | 1 | tirex2 | multivariate | 0.425 | 0.955 | 1 | 139 |
| CA | retail | 1 | tirex2 | univariate | 0.843 | 1.023 | 1 | 139 |
| CA | retail | 3 | chronos2 | multivariate | 0.922 | 1.126 | 11 | 128 |
| CA | retail | 3 | chronos2 | univariate | 0.927 | 1.165 | 11 | 128 |
| CA | retail | 3 | moirai2 | univariate | 0.982 | 0.994 | 14 | 125 |
| CA | retail | 3 | timesfm25 | univariate | 0.954 | 0.980 | 12 | 127 |
| CA | retail | 3 | tirex | univariate | 0.990 | 0.978 | 17 | 122 |
| CA | retail | 3 | tirex2 | multivariate |  | 0.981 |  | 139 |
| CA | retail | 3 | tirex2 | univariate |  | 0.983 |  | 139 |
| CA | retail | 6 | chronos2 | multivariate | 1.031 | 1.062 | 8 | 128 |
| CA | retail | 6 | chronos2 | univariate | 1.030 | 1.130 | 8 | 128 |
| CA | retail | 6 | moirai2 | univariate | 1.039 | 0.961 | 11 | 125 |
| CA | retail | 6 | timesfm25 | univariate | 1.011 | 0.959 | 9 | 127 |
| CA | retail | 6 | tirex | univariate | 0.989 | 0.964 | 14 | 122 |
| CA | retail | 6 | tirex2 | multivariate |  | 0.956 |  | 136 |
| CA | retail | 6 | tirex2 | univariate |  | 0.957 |  | 136 |
| CA | retail | 12 | chronos2 | multivariate | 0.912 | 1.005 | 3 | 128 |
| CA | retail | 12 | chronos2 | univariate | 0.916 | 1.075 | 3 | 128 |
| CA | retail | 12 | moirai2 | univariate | 0.925 | 0.975 | 6 | 125 |
| CA | retail | 12 | timesfm25 | univariate | 0.939 | 0.978 | 4 | 127 |
| CA | retail | 12 | tirex | univariate | 0.976 | 0.986 | 9 | 122 |
| CA | retail | 12 | tirex2 | multivariate |  | 0.981 |  | 131 |
| CA | retail | 12 | tirex2 | univariate |  | 0.982 |  | 131 |
| CA | unemp | 1 | chronos2 | multivariate | 0.779 | 1.351 | 12 | 130 |
| CA | unemp | 1 | chronos2 | univariate | 0.742 | 1.108 | 12 | 130 |
| CA | unemp | 1 | moirai2 | univariate | 0.821 | 0.932 | 15 | 127 |
| CA | unemp | 1 | timesfm25 | univariate | 0.815 | 0.983 | 13 | 129 |
| CA | unemp | 1 | tirex | univariate | 0.837 | 1.012 | 18 | 124 |
| CA | unemp | 1 | tirex2 | multivariate | 1.216 | 1.097 | 1 | 141 |
| CA | unemp | 1 | tirex2 | univariate | 0.799 | 0.999 | 1 | 141 |
| CA | unemp | 3 | chronos2 | multivariate | 1.091 | 1.307 | 11 | 130 |
| CA | unemp | 3 | chronos2 | univariate | 1.053 | 1.082 | 11 | 130 |
| CA | unemp | 3 | moirai2 | univariate | 1.062 | 0.982 | 14 | 127 |
| CA | unemp | 3 | timesfm25 | univariate | 1.113 | 1.007 | 12 | 129 |
| CA | unemp | 3 | tirex | univariate | 1.053 | 0.986 | 17 | 124 |
| CA | unemp | 3 | tirex2 | multivariate |  | 1.025 |  | 141 |
| CA | unemp | 3 | tirex2 | univariate |  | 0.998 |  | 141 |
| CA | unemp | 6 | chronos2 | multivariate | 0.989 | 1.118 | 8 | 130 |
| CA | unemp | 6 | chronos2 | univariate | 0.971 | 1.007 | 8 | 130 |
| CA | unemp | 6 | moirai2 | univariate | 1.023 | 1.019 | 11 | 127 |
| CA | unemp | 6 | timesfm25 | univariate | 0.936 | 1.005 | 9 | 129 |
| CA | unemp | 6 | tirex | univariate | 1.026 | 1.002 | 14 | 124 |
| CA | unemp | 6 | tirex2 | multivariate |  | 1.000 |  | 138 |
| CA | unemp | 6 | tirex2 | univariate |  | 0.998 |  | 138 |
| CA | unemp | 12 | chronos2 | multivariate | 1.289 | 0.980 | 2 | 130 |
| CA | unemp | 12 | chronos2 | univariate | 0.920 | 0.983 | 2 | 130 |
| CA | unemp | 12 | moirai2 | univariate | 1.102 | 0.997 | 5 | 127 |
| CA | unemp | 12 | timesfm25 | univariate | 1.092 | 0.992 | 3 | 129 |
| CA | unemp | 12 | tirex | univariate | 1.082 | 0.984 | 8 | 124 |
| CA | unemp | 12 | tirex2 | multivariate |  | 0.987 |  | 132 |
| CA | unemp | 12 | tirex2 | univariate |  | 0.987 |  | 132 |
| EA | consumption | 1 | chronos2 | multivariate | 2.087 | 0.643 | 10 | 123 |
| EA | consumption | 1 | chronos2 | univariate | 1.749 | 0.700 | 10 | 123 |
| EA | consumption | 1 | moirai2 | univariate | 1.168 | 0.579 | 13 | 120 |
| EA | consumption | 1 | timesfm25 | univariate | 1.068 | 0.504 | 11 | 122 |
| EA | consumption | 1 | tirex | univariate | 1.233 | 0.670 | 16 | 117 |
| EA | consumption | 1 | tirex2 | multivariate |  | 0.572 |  | 133 |
| EA | consumption | 1 | tirex2 | univariate |  | 0.573 |  | 133 |
| EA | consumption | 2 | chronos2 | multivariate | 0.979 | 0.782 | 7 | 123 |
| EA | consumption | 2 | chronos2 | univariate | 0.730 | 0.869 | 7 | 123 |
| EA | consumption | 2 | moirai2 | univariate | 0.814 | 0.714 | 10 | 120 |
| EA | consumption | 2 | timesfm25 | univariate | 1.067 | 0.721 | 8 | 122 |
| EA | consumption | 2 | tirex | univariate | 0.946 | 0.771 | 13 | 117 |
| EA | consumption | 2 | tirex2 | multivariate |  | 0.697 |  | 130 |
| EA | consumption | 2 | tirex2 | univariate |  | 0.695 |  | 130 |
| EA | consumption | 4 | chronos2 | multivariate | 2.751 | 0.911 | 1 | 123 |
| EA | consumption | 4 | chronos2 | univariate | 1.375 | 0.908 | 1 | 123 |
| EA | consumption | 4 | moirai2 | univariate | 1.411 | 0.912 | 4 | 120 |
| EA | consumption | 4 | timesfm25 | univariate | 1.614 | 0.912 | 2 | 122 |
| EA | consumption | 4 | tirex | univariate | 1.095 | 0.911 | 7 | 117 |
| EA | consumption | 4 | tirex2 | multivariate |  | 0.907 |  | 124 |
| EA | consumption | 4 | tirex2 | univariate |  | 0.907 |  | 124 |
| EA | gdp | 1 | chronos2 | multivariate | 2.126 | 0.642 | 10 | 122 |
| EA | gdp | 1 | chronos2 | univariate | 2.024 | 0.840 | 10 | 123 |
| EA | gdp | 1 | moirai2 | univariate | 1.785 | 0.687 | 13 | 120 |
| EA | gdp | 1 | timesfm25 | univariate | 1.878 | 0.624 | 11 | 122 |
| EA | gdp | 1 | tirex | univariate | 1.704 | 0.795 | 16 | 117 |
| EA | gdp | 1 | tirex2 | multivariate |  | 0.617 |  | 132 |
| EA | gdp | 1 | tirex2 | univariate |  | 0.619 |  | 133 |
| EA | gdp | 2 | chronos2 | multivariate | 1.117 | 0.919 | 6 | 122 |
| EA | gdp | 2 | chronos2 | univariate | 1.239 | 1.099 | 6 | 123 |
| EA | gdp | 2 | moirai2 | univariate | 1.210 | 0.907 | 9 | 120 |
| EA | gdp | 2 | timesfm25 | univariate | 1.254 | 0.919 | 7 | 122 |
| EA | gdp | 2 | tirex | univariate | 1.115 | 0.936 | 12 | 117 |
| EA | gdp | 2 | tirex2 | multivariate |  | 0.886 |  | 128 |
| EA | gdp | 2 | tirex2 | univariate |  | 0.883 |  | 129 |
| EA | gdp | 4 | chronos2 | multivariate | 1.281 | 1.006 | 1 | 122 |
| EA | gdp | 4 | chronos2 | univariate | 1.371 | 1.003 | 1 | 123 |
| EA | gdp | 4 | moirai2 | univariate | 1.318 | 1.003 | 4 | 120 |
| EA | gdp | 4 | timesfm25 | univariate | 1.406 | 1.009 | 2 | 122 |
| EA | gdp | 4 | tirex | univariate | 1.296 | 1.001 | 7 | 117 |
| EA | gdp | 4 | tirex2 | multivariate |  | 1.002 |  | 123 |
| EA | gdp | 4 | tirex2 | univariate |  | 1.003 |  | 124 |
| EA | hicp | 1 | chronos2 | multivariate | 0.794 | 0.903 | 12 | 130 |
| EA | hicp | 1 | chronos2 | univariate | 0.767 | 0.940 | 12 | 130 |
| EA | hicp | 1 | moirai2 | univariate | 0.651 | 0.960 | 15 | 127 |
| EA | hicp | 1 | timesfm25 | univariate | 0.726 | 0.958 | 13 | 129 |
| EA | hicp | 1 | tirex | univariate | 0.802 | 1.043 | 18 | 124 |
| EA | hicp | 1 | tirex2 | multivariate | 1.223 | 0.963 | 1 | 141 |
| EA | hicp | 1 | tirex2 | univariate | 1.165 | 0.979 | 1 | 141 |
| EA | hicp | 3 | chronos2 | multivariate | 0.794 | 0.940 | 10 | 130 |
| EA | hicp | 3 | chronos2 | univariate | 0.869 | 0.978 | 10 | 130 |
| EA | hicp | 3 | moirai2 | univariate | 0.743 | 0.999 | 13 | 127 |
| EA | hicp | 3 | timesfm25 | univariate | 0.727 | 0.940 | 11 | 129 |
| EA | hicp | 3 | tirex | univariate | 0.859 | 0.992 | 16 | 124 |
| EA | hicp | 3 | tirex2 | multivariate |  | 0.990 |  | 140 |
| EA | hicp | 3 | tirex2 | univariate |  | 1.001 |  | 140 |
| EA | hicp | 6 | chronos2 | multivariate | 0.780 | 0.943 | 6 | 130 |
| EA | hicp | 6 | chronos2 | univariate | 0.904 | 0.987 | 6 | 130 |
| EA | hicp | 6 | moirai2 | univariate | 1.046 | 1.029 | 9 | 127 |
| EA | hicp | 6 | timesfm25 | univariate | 0.869 | 1.004 | 7 | 129 |
| EA | hicp | 6 | tirex | univariate | 0.828 | 1.028 | 12 | 124 |
| EA | hicp | 6 | tirex2 | multivariate |  | 1.026 |  | 136 |
| EA | hicp | 6 | tirex2 | univariate |  | 1.043 |  | 136 |
| EA | hicp | 12 | chronos2 | multivariate | 0.998 | 0.989 | 1 | 130 |
| EA | hicp | 12 | chronos2 | univariate | 1.000 | 1.149 | 1 | 130 |
| EA | hicp | 12 | moirai2 | univariate | 0.965 | 1.160 | 4 | 127 |
| EA | hicp | 12 | timesfm25 | univariate | 0.899 | 1.121 | 2 | 129 |
| EA | hicp | 12 | tirex | univariate | 0.960 | 1.173 | 7 | 124 |
| EA | hicp | 12 | tirex2 | multivariate |  | 1.205 |  | 131 |
| EA | hicp | 12 | tirex2 | univariate |  | 1.249 |  | 131 |
| EA | hicp_core | 1 | chronos2 | multivariate | 0.776 | 0.795 | 7 | 95 |
| EA | hicp_core | 1 | chronos2 | univariate | 0.942 | 0.877 | 12 | 130 |
| EA | hicp_core | 1 | moirai2 | univariate | 1.016 | 0.871 | 15 | 127 |
| EA | hicp_core | 1 | timesfm25 | univariate | 0.887 | 0.858 | 13 | 129 |
| EA | hicp_core | 1 | tirex | univariate | 0.903 | 0.940 | 18 | 124 |
| EA | hicp_core | 1 | tirex2 | multivariate |  | 0.873 |  | 102 |
| EA | hicp_core | 1 | tirex2 | univariate | 4.133 | 0.864 | 1 | 141 |
| EA | hicp_core | 3 | chronos2 | multivariate | 0.629 | 0.857 | 6 | 95 |
| EA | hicp_core | 3 | chronos2 | univariate | 0.811 | 0.957 | 10 | 130 |
| EA | hicp_core | 3 | moirai2 | univariate | 0.556 | 0.939 | 13 | 127 |
| EA | hicp_core | 3 | timesfm25 | univariate | 0.914 | 0.868 | 11 | 129 |
| EA | hicp_core | 3 | tirex | univariate | 0.792 | 0.952 | 16 | 124 |
| EA | hicp_core | 3 | tirex2 | multivariate |  | 0.863 |  | 101 |
| EA | hicp_core | 3 | tirex2 | univariate |  | 0.851 |  | 140 |
| EA | hicp_core | 6 | chronos2 | multivariate | 0.548 | 0.843 | 5 | 95 |
| EA | hicp_core | 6 | chronos2 | univariate | 0.545 | 0.879 | 7 | 130 |
| EA | hicp_core | 6 | moirai2 | univariate | 0.694 | 0.919 | 10 | 127 |
| EA | hicp_core | 6 | timesfm25 | univariate | 0.645 | 0.863 | 8 | 129 |
| EA | hicp_core | 6 | tirex | univariate | 0.840 | 0.925 | 13 | 124 |
| EA | hicp_core | 6 | tirex2 | multivariate |  | 0.857 |  | 100 |
| EA | hicp_core | 6 | tirex2 | univariate |  | 0.837 |  | 137 |
| EA | hicp_core | 12 | chronos2 | multivariate | 0.496 | 0.915 | 1 | 95 |
| EA | hicp_core | 12 | chronos2 | univariate | 0.045 | 0.942 | 1 | 130 |
| EA | hicp_core | 12 | moirai2 | univariate | 0.690 | 1.029 | 4 | 127 |
| EA | hicp_core | 12 | timesfm25 | univariate | 0.648 | 0.953 | 2 | 129 |
| EA | hicp_core | 12 | tirex | univariate | 0.640 | 0.976 | 7 | 124 |
| EA | hicp_core | 12 | tirex2 | multivariate |  | 0.882 |  | 96 |
| EA | hicp_core | 12 | tirex2 | univariate |  | 0.916 |  | 131 |
| EA | retail | 1 | chronos2 | multivariate | 1.256 | 0.891 | 12 | 130 |
| EA | retail | 1 | chronos2 | univariate | 1.140 | 1.110 | 12 | 130 |
| EA | retail | 1 | moirai2 | univariate | 1.391 | 1.050 | 15 | 127 |
| EA | retail | 1 | timesfm25 | univariate | 1.225 | 0.987 | 13 | 129 |
| EA | retail | 1 | tirex | univariate | 1.133 | 1.035 | 18 | 124 |
| EA | retail | 1 | tirex2 | multivariate | 0.874 | 0.852 | 1 | 141 |
| EA | retail | 1 | tirex2 | univariate | 1.573 | 1.012 | 1 | 141 |
| EA | retail | 3 | chronos2 | multivariate | 1.187 | 1.116 | 11 | 130 |
| EA | retail | 3 | chronos2 | univariate | 1.099 | 1.277 | 11 | 130 |
| EA | retail | 3 | moirai2 | univariate | 1.170 | 1.140 | 14 | 127 |
| EA | retail | 3 | timesfm25 | univariate | 1.171 | 1.056 | 12 | 129 |
| EA | retail | 3 | tirex | univariate | 1.148 | 1.109 | 17 | 124 |
| EA | retail | 3 | tirex2 | multivariate |  | 1.011 |  | 141 |
| EA | retail | 3 | tirex2 | univariate |  | 1.065 |  | 141 |
| EA | retail | 6 | chronos2 | multivariate | 1.087 | 1.057 | 8 | 130 |
| EA | retail | 6 | chronos2 | univariate | 1.035 | 1.178 | 8 | 130 |
| EA | retail | 6 | moirai2 | univariate | 1.019 | 1.105 | 11 | 127 |
| EA | retail | 6 | timesfm25 | univariate | 1.024 | 0.981 | 9 | 129 |
| EA | retail | 6 | tirex | univariate | 0.997 | 1.075 | 14 | 124 |
| EA | retail | 6 | tirex2 | multivariate |  | 0.937 |  | 138 |
| EA | retail | 6 | tirex2 | univariate |  | 0.989 |  | 138 |
| EA | retail | 12 | chronos2 | multivariate | 1.025 | 0.976 | 2 | 130 |
| EA | retail | 12 | chronos2 | univariate | 0.983 | 1.134 | 2 | 130 |
| EA | retail | 12 | moirai2 | univariate | 0.973 | 1.015 | 5 | 127 |
| EA | retail | 12 | timesfm25 | univariate | 0.974 | 0.943 | 3 | 129 |
| EA | retail | 12 | tirex | univariate | 0.966 | 0.960 | 8 | 124 |
| EA | retail | 12 | tirex2 | multivariate |  | 0.954 |  | 132 |
| EA | retail | 12 | tirex2 | univariate |  | 0.944 |  | 132 |
| EA | unemp | 1 | chronos2 | multivariate | 0.940 | 0.968 | 12 | 121 |
| EA | unemp | 1 | chronos2 | univariate | 0.959 | 0.948 | 12 | 121 |
| EA | unemp | 1 | moirai2 | univariate | 0.952 | 0.971 | 15 | 118 |
| EA | unemp | 1 | timesfm25 | univariate | 0.905 | 0.959 | 13 | 120 |
| EA | unemp | 1 | tirex | univariate | 0.913 | 0.957 | 18 | 115 |
| EA | unemp | 1 | tirex2 | multivariate | 0.819 | 0.938 | 1 | 132 |
| EA | unemp | 1 | tirex2 | univariate | 0.570 | 0.936 | 1 | 132 |
| EA | unemp | 3 | chronos2 | multivariate | 0.887 | 1.003 | 10 | 121 |
| EA | unemp | 3 | chronos2 | univariate | 0.931 | 0.983 | 10 | 121 |
| EA | unemp | 3 | moirai2 | univariate | 0.924 | 0.957 | 13 | 118 |
| EA | unemp | 3 | timesfm25 | univariate | 0.912 | 0.925 | 11 | 120 |
| EA | unemp | 3 | tirex | univariate | 0.950 | 0.945 | 16 | 115 |
| EA | unemp | 3 | tirex2 | multivariate |  | 0.952 |  | 131 |
| EA | unemp | 3 | tirex2 | univariate |  | 0.946 |  | 131 |
| EA | unemp | 6 | chronos2 | multivariate | 1.275 | 0.995 | 7 | 119 |
| EA | unemp | 6 | chronos2 | univariate | 0.925 | 1.013 | 7 | 119 |
| EA | unemp | 6 | moirai2 | univariate | 1.027 | 0.936 | 10 | 116 |
| EA | unemp | 6 | timesfm25 | univariate | 0.915 | 0.922 | 8 | 118 |
| EA | unemp | 6 | tirex | univariate | 1.027 | 0.922 | 13 | 113 |
| EA | unemp | 6 | tirex2 | multivariate |  | 0.952 |  | 126 |
| EA | unemp | 6 | tirex2 | univariate |  | 0.930 |  | 126 |
| EA | unemp | 12 | chronos2 | multivariate | 2.891 | 0.998 | 1 | 113 |
| EA | unemp | 12 | chronos2 | univariate | 1.812 | 1.076 | 1 | 113 |
| EA | unemp | 12 | moirai2 | univariate | 1.195 | 0.985 | 4 | 110 |
| EA | unemp | 12 | timesfm25 | univariate | 2.493 | 0.986 | 2 | 112 |
| EA | unemp | 12 | tirex | univariate | 1.094 | 0.967 | 7 | 107 |
| EA | unemp | 12 | tirex2 | multivariate |  | 0.990 |  | 114 |
| EA | unemp | 12 | tirex2 | univariate |  | 0.969 |  | 114 |

### 5.3b Q2: before and after the stated training cutoff (models with a cutoff)

| econ | target | horizon | model | variant | rel_rmsfe:post_cutoff | rel_rmsfe:pre_cutoff | n:post_cutoff | n:pre_cutoff |
|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | moirai2 | univariate | 0.993 | 1.037 | 20 | 120 |
| CA | consumption | 1 | timesfm25 | univariate | 0.925 | 0.961 | 34 | 106 |
| CA | consumption | 2 | moirai2 | univariate | 0.911 | 1.003 | 17 | 120 |
| CA | consumption | 2 | timesfm25 | univariate | 0.959 | 1.001 | 31 | 106 |
| CA | consumption | 4 | moirai2 | univariate | 0.860 | 1.005 | 11 | 120 |
| CA | consumption | 4 | timesfm25 | univariate | 1.042 | 1.000 | 25 | 106 |
| CA | cpi | 1 | moirai2 | univariate | 0.860 | 0.864 | 22 | 120 |
| CA | cpi | 1 | timesfm25 | univariate | 0.790 | 0.898 | 36 | 106 |
| CA | cpi | 3 | moirai2 | univariate | 0.642 | 0.863 | 20 | 120 |
| CA | cpi | 3 | timesfm25 | univariate | 0.665 | 0.851 | 34 | 106 |
| CA | cpi | 6 | moirai2 | univariate | 0.728 | 0.886 | 17 | 120 |
| CA | cpi | 6 | timesfm25 | univariate | 0.717 | 0.879 | 31 | 106 |
| CA | cpi | 12 | moirai2 | univariate | 0.740 | 0.905 | 11 | 120 |
| CA | cpi | 12 | timesfm25 | univariate | 0.744 | 0.897 | 25 | 106 |
| CA | cpi_core | 1 | moirai2 | univariate | 1.039 | 0.994 | 22 | 120 |
| CA | cpi_core | 1 | timesfm25 | univariate | 0.956 | 0.983 | 36 | 106 |
| CA | cpi_core | 3 | moirai2 | univariate | 1.064 | 0.988 | 20 | 120 |
| CA | cpi_core | 3 | timesfm25 | univariate | 0.985 | 0.952 | 34 | 106 |
| CA | cpi_core | 6 | moirai2 | univariate | 0.965 | 0.968 | 17 | 120 |
| CA | cpi_core | 6 | timesfm25 | univariate | 0.992 | 0.950 | 31 | 106 |
| CA | cpi_core | 12 | moirai2 | univariate | 0.957 | 0.991 | 11 | 120 |
| CA | cpi_core | 12 | timesfm25 | univariate | 0.972 | 0.956 | 25 | 106 |
| CA | gdp | 1 | moirai2 | univariate | 0.887 | 0.973 | 20 | 120 |
| CA | gdp | 1 | timesfm25 | univariate | 0.829 | 0.932 | 34 | 106 |
| CA | gdp | 2 | moirai2 | univariate | 0.856 | 1.000 | 17 | 120 |
| CA | gdp | 2 | timesfm25 | univariate | 0.808 | 1.007 | 31 | 106 |
| CA | gdp | 4 | moirai2 | univariate | 0.923 | 0.994 | 11 | 120 |
| CA | gdp | 4 | timesfm25 | univariate | 0.866 | 0.997 | 25 | 106 |
| CA | retail | 1 | moirai2 | univariate | 0.894 | 1.043 | 22 | 118 |
| CA | retail | 1 | timesfm25 | univariate | 0.950 | 0.959 | 36 | 104 |
| CA | retail | 3 | moirai2 | univariate | 0.991 | 0.994 | 21 | 118 |
| CA | retail | 3 | timesfm25 | univariate | 1.000 | 0.980 | 35 | 104 |
| CA | retail | 6 | moirai2 | univariate | 0.995 | 0.961 | 18 | 118 |
| CA | retail | 6 | timesfm25 | univariate | 1.025 | 0.958 | 32 | 104 |
| CA | retail | 12 | moirai2 | univariate | 0.925 | 0.975 | 13 | 118 |
| CA | retail | 12 | timesfm25 | univariate | 0.961 | 0.978 | 27 | 104 |
| CA | unemp | 1 | moirai2 | univariate | 0.873 | 0.931 | 22 | 120 |
| CA | unemp | 1 | timesfm25 | univariate | 0.886 | 0.982 | 36 | 106 |
| CA | unemp | 3 | moirai2 | univariate | 1.041 | 0.982 | 21 | 120 |
| CA | unemp | 3 | timesfm25 | univariate | 1.011 | 1.008 | 35 | 106 |
| CA | unemp | 6 | moirai2 | univariate | 1.041 | 1.019 | 18 | 120 |
| CA | unemp | 6 | timesfm25 | univariate | 1.011 | 1.004 | 32 | 106 |
| CA | unemp | 12 | moirai2 | univariate | 1.074 | 0.996 | 12 | 120 |
| CA | unemp | 12 | timesfm25 | univariate | 1.021 | 0.991 | 26 | 106 |
| EA | consumption | 1 | moirai2 | univariate | 1.050 | 0.579 | 20 | 113 |
| EA | consumption | 1 | timesfm25 | univariate | 1.026 | 0.504 | 34 | 99 |
| EA | consumption | 2 | moirai2 | univariate | 1.002 | 0.714 | 17 | 113 |
| EA | consumption | 2 | timesfm25 | univariate | 1.149 | 0.720 | 31 | 99 |
| EA | consumption | 4 | moirai2 | univariate | 0.908 | 0.912 | 11 | 113 |
| EA | consumption | 4 | timesfm25 | univariate | 1.085 | 0.911 | 25 | 99 |
| EA | gdp | 1 | moirai2 | univariate | 1.512 | 0.687 | 20 | 113 |
| EA | gdp | 1 | timesfm25 | univariate | 1.135 | 0.624 | 34 | 99 |
| EA | gdp | 2 | moirai2 | univariate | 1.034 | 0.907 | 16 | 113 |
| EA | gdp | 2 | timesfm25 | univariate | 0.947 | 0.919 | 30 | 99 |
| EA | gdp | 4 | moirai2 | univariate | 1.226 | 1.003 | 11 | 113 |
| EA | gdp | 4 | timesfm25 | univariate | 0.989 | 1.009 | 25 | 99 |
| EA | hicp | 1 | moirai2 | univariate | 0.726 | 0.956 | 22 | 120 |
| EA | hicp | 1 | timesfm25 | univariate | 0.765 | 0.971 | 36 | 106 |
| EA | hicp | 3 | moirai2 | univariate | 0.847 | 0.995 | 20 | 120 |
| EA | hicp | 3 | timesfm25 | univariate | 0.897 | 0.935 | 34 | 106 |
| EA | hicp | 6 | moirai2 | univariate | 1.082 | 1.026 | 16 | 120 |
| EA | hicp | 6 | timesfm25 | univariate | 1.030 | 0.992 | 30 | 106 |
| EA | hicp | 12 | moirai2 | univariate | 0.965 | 1.175 | 11 | 120 |
| EA | hicp | 12 | timesfm25 | univariate | 1.001 | 1.133 | 25 | 106 |
| EA | hicp_core | 1 | moirai2 | univariate | 0.941 | 0.871 | 22 | 120 |
| EA | hicp_core | 1 | timesfm25 | univariate | 1.015 | 0.837 | 36 | 106 |
| EA | hicp_core | 3 | moirai2 | univariate | 0.653 | 0.942 | 20 | 120 |
| EA | hicp_core | 3 | timesfm25 | univariate | 1.134 | 0.842 | 34 | 106 |
| EA | hicp_core | 6 | moirai2 | univariate | 0.848 | 0.915 | 17 | 120 |
| EA | hicp_core | 6 | timesfm25 | univariate | 1.153 | 0.828 | 31 | 106 |
| EA | hicp_core | 12 | moirai2 | univariate | 0.565 | 1.042 | 11 | 120 |
| EA | hicp_core | 12 | timesfm25 | univariate | 0.966 | 0.951 | 25 | 106 |
| EA | retail | 1 | moirai2 | univariate | 1.457 | 1.050 | 22 | 120 |
| EA | retail | 1 | timesfm25 | univariate | 0.894 | 0.987 | 36 | 106 |
| EA | retail | 3 | moirai2 | univariate | 1.197 | 1.140 | 21 | 120 |
| EA | retail | 3 | timesfm25 | univariate | 0.958 | 1.057 | 35 | 106 |
| EA | retail | 6 | moirai2 | univariate | 1.000 | 1.105 | 18 | 120 |
| EA | retail | 6 | timesfm25 | univariate | 0.961 | 0.981 | 32 | 106 |
| EA | retail | 12 | moirai2 | univariate | 0.969 | 1.015 | 12 | 120 |
| EA | retail | 12 | timesfm25 | univariate | 0.999 | 0.942 | 26 | 106 |
| EA | unemp | 1 | moirai2 | univariate | 0.968 | 0.968 | 22 | 111 |
| EA | unemp | 1 | timesfm25 | univariate | 0.905 | 0.970 | 33 | 100 |
| EA | unemp | 3 | moirai2 | univariate | 0.944 | 0.957 | 20 | 111 |
| EA | unemp | 3 | timesfm25 | univariate | 0.947 | 0.920 | 29 | 102 |
| EA | unemp | 6 | moirai2 | univariate | 1.035 | 0.929 | 17 | 109 |
| EA | unemp | 6 | timesfm25 | univariate | 1.024 | 0.908 | 24 | 102 |
| EA | unemp | 12 | moirai2 | univariate | 0.990 | 0.987 | 11 | 103 |
| EA | unemp | 12 | timesfm25 | univariate | 1.031 | 0.981 | 18 | 96 |

### 5.4 Full sample versus ex-COVID

| econ | target | horizon | model | variant | rel_rmsfe:ex_covid | rel_rmsfe:full | n:ex_covid | n:full |
|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | bvar | multivariate | 1.004 | 1.049 | 122 | 138 |
| CA | consumption | 1 | chronos2 | multivariate | 1.051 | 1.138 | 81 | 94 |
| CA | consumption | 1 | chronos2 | univariate | 1.079 | 1.323 | 122 | 140 |
| CA | consumption | 1 | combo_bench | multivariate | 0.935 | 0.862 | 119 | 135 |
| CA | consumption | 1 | combo_fm | univariate | 1.103 | 1.016 | 122 | 140 |
| CA | consumption | 1 | dfm | multivariate | 0.939 | 0.569 | 119 | 137 |
| CA | consumption | 1 | moirai2 | univariate | 1.091 | 1.036 | 122 | 140 |
| CA | consumption | 1 | naive | univariate | 1.049 | 0.815 | 122 | 140 |
| CA | consumption | 1 | timesfm25 | univariate | 1.161 | 0.961 | 122 | 140 |
| CA | consumption | 1 | tirex | univariate | 1.241 | 0.959 | 122 | 140 |
| CA | consumption | 1 | tirex2 | multivariate | 1.044 | 0.934 | 81 | 94 |
| CA | consumption | 1 | tirex2 | univariate | 1.001 | 0.846 | 122 | 140 |
| CA | consumption | 2 | bvar | multivariate | 1.091 | 1.150 | 119 | 135 |
| CA | consumption | 2 | chronos2 | multivariate | 0.994 | 1.045 | 79 | 92 |
| CA | consumption | 2 | chronos2 | univariate | 0.991 | 1.208 | 119 | 137 |
| CA | consumption | 2 | combo_bench | multivariate | 1.009 | 1.010 | 116 | 132 |
| CA | consumption | 2 | combo_fm | univariate | 0.999 | 1.010 | 119 | 137 |
| CA | consumption | 2 | dfm | multivariate | 1.022 | 0.967 | 116 | 134 |
| CA | consumption | 2 | moirai2 | univariate | 0.991 | 1.002 | 119 | 137 |
| CA | consumption | 2 | naive | univariate | 1.013 | 0.981 | 119 | 137 |
| CA | consumption | 2 | timesfm25 | univariate | 1.016 | 1.000 | 119 | 137 |
| CA | consumption | 2 | tirex | univariate | 1.026 | 0.983 | 119 | 137 |
| CA | consumption | 2 | tirex2 | multivariate | 1.013 | 0.993 | 79 | 92 |
| CA | consumption | 2 | tirex2 | univariate | 1.005 | 0.987 | 119 | 137 |
| CA | consumption | 4 | bvar | multivariate | 3.651 | 1.239 | 113 | 129 |
| CA | consumption | 4 | chronos2 | multivariate | 1.167 | 1.009 | 76 | 88 |
| CA | consumption | 4 | chronos2 | univariate | 1.125 | 1.118 | 113 | 131 |
| CA | consumption | 4 | combo_bench | multivariate | 1.313 | 1.014 | 110 | 126 |
| CA | consumption | 4 | combo_fm | univariate | 1.095 | 1.007 | 113 | 131 |
| CA | consumption | 4 | dfm | multivariate | 1.080 | 1.001 | 110 | 128 |
| CA | consumption | 4 | moirai2 | univariate | 1.128 | 1.005 | 113 | 131 |
| CA | consumption | 4 | naive | univariate | 1.125 | 1.004 | 113 | 131 |
| CA | consumption | 4 | timesfm25 | univariate | 1.079 | 1.000 | 113 | 131 |
| CA | consumption | 4 | tirex | univariate | 1.147 | 1.001 | 113 | 131 |
| CA | consumption | 4 | tirex2 | multivariate | 1.120 | 1.000 | 76 | 88 |
| CA | consumption | 4 | tirex2 | univariate | 1.030 | 0.994 | 113 | 131 |
| CA | cpi | 1 | bvar | multivariate | 1.001 | 0.976 | 124 | 141 |
| CA | cpi | 1 | chronos2 | multivariate | 0.812 | 0.844 | 124 | 142 |
| CA | cpi | 1 | chronos2 | univariate | 0.829 | 0.862 | 124 | 142 |
| CA | cpi | 1 | combo_bench | multivariate | 0.993 | 0.975 | 121 | 138 |
| CA | cpi | 1 | combo_fm | univariate | 0.826 | 0.856 | 124 | 142 |
| CA | cpi | 1 | dfm | multivariate | 0.997 | 0.988 | 121 | 139 |
| CA | cpi | 1 | moirai2 | univariate | 0.834 | 0.863 | 124 | 142 |
| CA | cpi | 1 | naive | univariate | 1.013 | 1.012 | 124 | 142 |
| CA | cpi | 1 | timesfm25 | univariate | 0.847 | 0.878 | 124 | 142 |
| CA | cpi | 1 | tirex | univariate | 0.868 | 0.886 | 124 | 142 |
| CA | cpi | 1 | tirex2 | multivariate | 0.824 | 0.856 | 124 | 142 |
| CA | cpi | 1 | tirex2 | univariate | 0.818 | 0.854 | 124 | 142 |
| CA | cpi | 3 | bvar | multivariate | 0.998 | 1.003 | 122 | 139 |
| CA | cpi | 3 | chronos2 | multivariate | 0.785 | 0.846 | 122 | 140 |
| CA | cpi | 3 | chronos2 | univariate | 0.782 | 0.822 | 122 | 140 |
| CA | cpi | 3 | combo_bench | multivariate | 0.998 | 1.000 | 119 | 136 |
| CA | cpi | 3 | combo_fm | univariate | 0.780 | 0.818 | 122 | 140 |
| CA | cpi | 3 | dfm | multivariate | 1.000 | 1.001 | 119 | 137 |
| CA | cpi | 3 | moirai2 | univariate | 0.803 | 0.840 | 122 | 140 |
| CA | cpi | 3 | naive | univariate | 0.997 | 0.998 | 122 | 140 |
| CA | cpi | 3 | timesfm25 | univariate | 0.776 | 0.814 | 122 | 140 |
| CA | cpi | 3 | tirex | univariate | 0.791 | 0.829 | 122 | 140 |
| CA | cpi | 3 | tirex2 | multivariate | 0.811 | 0.843 | 122 | 140 |
| CA | cpi | 3 | tirex2 | univariate | 0.795 | 0.831 | 122 | 140 |
| CA | cpi | 6 | bvar | multivariate | 1.014 | 1.014 | 118 | 136 |
| CA | cpi | 6 | chronos2 | multivariate | 0.824 | 0.895 | 118 | 137 |
| CA | cpi | 6 | chronos2 | univariate | 0.819 | 0.862 | 118 | 137 |
| CA | cpi | 6 | combo_bench | multivariate | 1.007 | 1.007 | 115 | 133 |
| CA | cpi | 6 | combo_fm | univariate | 0.813 | 0.851 | 118 | 137 |
| CA | cpi | 6 | dfm | multivariate | 1.010 | 1.011 | 115 | 134 |
| CA | cpi | 6 | moirai2 | univariate | 0.828 | 0.870 | 118 | 137 |
| CA | cpi | 6 | naive | univariate | 1.009 | 1.010 | 118 | 137 |
| CA | cpi | 6 | timesfm25 | univariate | 0.804 | 0.846 | 118 | 137 |
| CA | cpi | 6 | tirex | univariate | 0.825 | 0.852 | 118 | 137 |
| CA | cpi | 6 | tirex2 | multivariate | 0.853 | 0.883 | 118 | 137 |
| CA | cpi | 6 | tirex2 | univariate | 0.837 | 0.872 | 118 | 137 |
| CA | cpi | 12 | bvar | multivariate | 1.153 | 1.107 | 113 | 130 |
| CA | cpi | 12 | chronos2 | multivariate | 0.918 | 0.917 | 114 | 131 |
| CA | cpi | 12 | chronos2 | univariate | 0.881 | 0.891 | 114 | 131 |
| CA | cpi | 12 | combo_bench | multivariate | 1.093 | 1.060 | 110 | 127 |
| CA | cpi | 12 | combo_fm | univariate | 0.864 | 0.874 | 114 | 131 |
| CA | cpi | 12 | dfm | multivariate | 1.148 | 1.103 | 111 | 128 |
| CA | cpi | 12 | moirai2 | univariate | 0.882 | 0.892 | 114 | 131 |
| CA | cpi | 12 | naive | univariate | 1.147 | 1.104 | 114 | 131 |
| CA | cpi | 12 | timesfm25 | univariate | 0.864 | 0.874 | 114 | 131 |
| CA | cpi | 12 | tirex | univariate | 0.878 | 0.884 | 114 | 131 |
| CA | cpi | 12 | tirex2 | multivariate | 0.901 | 0.902 | 114 | 131 |
| CA | cpi | 12 | tirex2 | univariate | 0.883 | 0.888 | 114 | 131 |
| CA | cpi_core | 1 | bvar | multivariate | 1.307 | 1.223 | 124 | 141 |
| CA | cpi_core | 1 | chronos2 | multivariate | 0.989 | 0.999 | 124 | 142 |
| CA | cpi_core | 1 | chronos2 | univariate | 1.051 | 1.030 | 124 | 142 |
| CA | cpi_core | 1 | combo_bench | multivariate | 1.116 | 1.066 | 121 | 138 |
| CA | cpi_core | 1 | combo_fm | univariate | 0.972 | 0.967 | 124 | 142 |
| CA | cpi_core | 1 | dfm | multivariate | 1.243 | 1.179 | 121 | 139 |
| CA | cpi_core | 1 | moirai2 | univariate | 1.004 | 1.002 | 124 | 142 |
| CA | cpi_core | 1 | naive | univariate | 1.235 | 1.172 | 124 | 142 |
| CA | cpi_core | 1 | timesfm25 | univariate | 0.989 | 0.976 | 124 | 142 |
| CA | cpi_core | 1 | tirex | univariate | 0.959 | 0.959 | 124 | 142 |
| CA | cpi_core | 1 | tirex2 | multivariate | 0.949 | 0.950 | 124 | 142 |
| CA | cpi_core | 1 | tirex2 | univariate | 0.942 | 0.948 | 124 | 142 |
| CA | cpi_core | 3 | bvar | multivariate | 1.324 | 1.289 | 122 | 139 |
| CA | cpi_core | 3 | chronos2 | multivariate | 1.000 | 1.021 | 122 | 140 |
| CA | cpi_core | 3 | chronos2 | univariate | 1.054 | 1.046 | 122 | 140 |
| CA | cpi_core | 3 | combo_bench | multivariate | 1.156 | 1.129 | 119 | 136 |
| CA | cpi_core | 3 | combo_fm | univariate | 0.979 | 0.974 | 122 | 140 |
| CA | cpi_core | 3 | dfm | multivariate | 1.307 | 1.271 | 119 | 137 |
| CA | cpi_core | 3 | moirai2 | univariate | 1.012 | 0.999 | 122 | 140 |
| CA | cpi_core | 3 | naive | univariate | 1.303 | 1.268 | 122 | 140 |
| CA | cpi_core | 3 | timesfm25 | univariate | 0.965 | 0.961 | 122 | 140 |
| CA | cpi_core | 3 | tirex | univariate | 0.987 | 0.983 | 122 | 140 |
| CA | cpi_core | 3 | tirex2 | multivariate | 0.956 | 0.960 | 122 | 140 |
| CA | cpi_core | 3 | tirex2 | univariate | 0.948 | 0.950 | 122 | 140 |
| CA | cpi_core | 6 | bvar | multivariate | 1.330 | 1.255 | 118 | 136 |
| CA | cpi_core | 6 | chronos2 | multivariate | 1.064 | 1.059 | 118 | 137 |
| CA | cpi_core | 6 | chronos2 | univariate | 1.063 | 1.040 | 118 | 137 |
| CA | cpi_core | 6 | combo_bench | multivariate | 1.154 | 1.102 | 115 | 133 |
| CA | cpi_core | 6 | combo_fm | univariate | 0.980 | 0.963 | 118 | 137 |
| CA | cpi_core | 6 | dfm | multivariate | 1.314 | 1.237 | 115 | 134 |
| CA | cpi_core | 6 | moirai2 | univariate | 0.988 | 0.968 | 118 | 137 |
| CA | cpi_core | 6 | naive | univariate | 1.315 | 1.237 | 118 | 137 |
| CA | cpi_core | 6 | timesfm25 | univariate | 0.986 | 0.960 | 118 | 137 |
| CA | cpi_core | 6 | tirex | univariate | 0.984 | 0.970 | 118 | 137 |
| CA | cpi_core | 6 | tirex2 | multivariate | 1.016 | 0.992 | 118 | 137 |
| CA | cpi_core | 6 | tirex2 | univariate | 0.968 | 0.957 | 118 | 137 |
| CA | cpi_core | 12 | bvar | multivariate | 1.434 | 1.326 | 113 | 130 |
| CA | cpi_core | 12 | chronos2 | multivariate | 1.080 | 1.047 | 114 | 131 |
| CA | cpi_core | 12 | chronos2 | univariate | 1.012 | 0.995 | 114 | 131 |
| CA | cpi_core | 12 | combo_bench | multivariate | 1.202 | 1.135 | 110 | 127 |
| CA | cpi_core | 12 | combo_fm | univariate | 0.973 | 0.960 | 114 | 131 |
| CA | cpi_core | 12 | dfm | multivariate | 1.375 | 1.282 | 111 | 128 |
| CA | cpi_core | 12 | moirai2 | univariate | 1.005 | 0.990 | 114 | 131 |
| CA | cpi_core | 12 | naive | univariate | 1.414 | 1.316 | 114 | 131 |
| CA | cpi_core | 12 | timesfm25 | univariate | 0.980 | 0.958 | 114 | 131 |
| CA | cpi_core | 12 | tirex | univariate | 0.966 | 0.952 | 114 | 131 |
| CA | cpi_core | 12 | tirex2 | multivariate | 0.985 | 0.975 | 114 | 131 |
| CA | cpi_core | 12 | tirex2 | univariate | 0.976 | 0.965 | 114 | 131 |
| CA | gdp | 1 | bvar | multivariate | 0.909 | 1.119 | 122 | 140 |
| CA | gdp | 1 | chronos2 | multivariate | 0.940 | 1.070 | 81 | 94 |
| CA | gdp | 1 | chronos2 | univariate | 0.931 | 1.324 | 122 | 140 |
| CA | gdp | 1 | combo_bench | multivariate | 0.845 | 0.806 | 119 | 137 |
| CA | gdp | 1 | combo_fm | univariate | 0.924 | 0.996 | 122 | 140 |
| CA | gdp | 1 | dfm | multivariate | 0.895 | 0.407 | 119 | 137 |
| CA | gdp | 1 | moirai2 | univariate | 0.910 | 0.972 | 122 | 140 |
| CA | gdp | 1 | naive | univariate | 1.026 | 0.795 | 122 | 140 |
| CA | gdp | 1 | timesfm25 | univariate | 0.918 | 0.931 | 122 | 140 |
| CA | gdp | 1 | tirex | univariate | 0.979 | 0.957 | 122 | 140 |
| CA | gdp | 1 | tirex2 | multivariate | 0.945 | 0.945 | 81 | 94 |
| CA | gdp | 1 | tirex2 | univariate | 0.920 | 0.846 | 122 | 140 |
| CA | gdp | 2 | bvar | multivariate | 0.939 | 1.164 | 119 | 137 |
| CA | gdp | 2 | chronos2 | multivariate | 0.969 | 1.038 | 79 | 92 |
| CA | gdp | 2 | chronos2 | univariate | 0.923 | 1.351 | 119 | 137 |
| CA | gdp | 2 | combo_bench | multivariate | 0.924 | 1.003 | 116 | 134 |
| CA | gdp | 2 | combo_fm | univariate | 0.907 | 1.023 | 119 | 137 |
| CA | gdp | 2 | dfm | multivariate | 1.028 | 0.928 | 116 | 134 |
| CA | gdp | 2 | moirai2 | univariate | 0.891 | 0.999 | 119 | 137 |
| CA | gdp | 2 | naive | univariate | 1.025 | 0.946 | 119 | 137 |
| CA | gdp | 2 | timesfm25 | univariate | 0.920 | 1.005 | 119 | 137 |
| CA | gdp | 2 | tirex | univariate | 0.937 | 0.962 | 119 | 137 |
| CA | gdp | 2 | tirex2 | multivariate | 0.952 | 0.967 | 79 | 92 |
| CA | gdp | 2 | tirex2 | univariate | 0.896 | 0.951 | 119 | 137 |
| CA | gdp | 4 | bvar | multivariate | 0.900 | 1.121 | 113 | 131 |
| CA | gdp | 4 | chronos2 | multivariate | 1.036 | 1.003 | 76 | 88 |
| CA | gdp | 4 | chronos2 | univariate | 0.998 | 1.212 | 113 | 131 |
| CA | gdp | 4 | combo_bench | multivariate | 0.945 | 1.009 | 110 | 128 |
| CA | gdp | 4 | combo_fm | univariate | 0.944 | 1.004 | 113 | 131 |
| CA | gdp | 4 | dfm | multivariate | 1.053 | 1.000 | 110 | 128 |
| CA | gdp | 4 | moirai2 | univariate | 0.941 | 0.994 | 113 | 131 |
| CA | gdp | 4 | naive | univariate | 1.060 | 1.000 | 113 | 131 |
| CA | gdp | 4 | timesfm25 | univariate | 1.094 | 0.996 | 113 | 131 |
| CA | gdp | 4 | tirex | univariate | 0.970 | 0.992 | 113 | 131 |
| CA | gdp | 4 | tirex2 | multivariate | 1.033 | 0.995 | 76 | 88 |
| CA | gdp | 4 | tirex2 | univariate | 0.954 | 0.992 | 113 | 131 |
| CA | retail | 1 | bvar | multivariate | 1.187 | 0.567 | 122 | 139 |
| CA | retail | 1 | chronos2 | multivariate | 0.951 | 1.161 | 122 | 140 |
| CA | retail | 1 | chronos2 | univariate | 1.008 | 1.222 | 122 | 140 |
| CA | retail | 1 | combo_bench | multivariate | 1.035 | 0.717 | 119 | 136 |
| CA | retail | 1 | combo_fm | univariate | 0.987 | 1.034 | 122 | 140 |
| CA | retail | 1 | dfm | multivariate | 1.128 | 0.725 | 119 | 137 |
| CA | retail | 1 | moirai2 | univariate | 0.988 | 1.041 | 122 | 140 |
| CA | retail | 1 | naive | univariate | 1.009 | 0.908 | 122 | 140 |
| CA | retail | 1 | timesfm25 | univariate | 0.997 | 0.959 | 122 | 140 |
| CA | retail | 1 | tirex | univariate | 1.024 | 0.981 | 122 | 140 |
| CA | retail | 1 | tirex2 | multivariate | 0.957 | 0.954 | 122 | 140 |
| CA | retail | 1 | tirex2 | univariate | 0.960 | 1.023 | 122 | 140 |
| CA | retail | 3 | bvar | multivariate | 1.197 | 0.976 | 121 | 138 |
| CA | retail | 3 | chronos2 | multivariate | 0.989 | 1.124 | 121 | 139 |
| CA | retail | 3 | chronos2 | univariate | 0.984 | 1.164 | 121 | 139 |
| CA | retail | 3 | combo_bench | multivariate | 1.050 | 0.976 | 118 | 135 |
| CA | retail | 3 | combo_fm | univariate | 0.993 | 0.998 | 121 | 139 |
| CA | retail | 3 | dfm | multivariate | 1.111 | 0.974 | 118 | 136 |
| CA | retail | 3 | moirai2 | univariate | 0.994 | 0.994 | 121 | 139 |
| CA | retail | 3 | naive | univariate | 0.983 | 0.980 | 121 | 139 |
| CA | retail | 3 | timesfm25 | univariate | 0.993 | 0.980 | 121 | 139 |
| CA | retail | 3 | tirex | univariate | 1.017 | 0.978 | 121 | 139 |
| CA | retail | 3 | tirex2 | multivariate | 0.998 | 0.981 | 121 | 139 |
| CA | retail | 3 | tirex2 | univariate | 0.998 | 0.983 | 121 | 139 |
| CA | retail | 6 | bvar | multivariate | 1.059 | 0.971 | 118 | 135 |
| CA | retail | 6 | chronos2 | multivariate | 0.960 | 1.062 | 118 | 136 |
| CA | retail | 6 | chronos2 | univariate | 0.965 | 1.130 | 118 | 136 |
| CA | retail | 6 | combo_bench | multivariate | 0.998 | 0.973 | 115 | 132 |
| CA | retail | 6 | combo_fm | univariate | 0.977 | 0.971 | 118 | 136 |
| CA | retail | 6 | dfm | multivariate | 0.977 | 0.956 | 115 | 133 |
| CA | retail | 6 | moirai2 | univariate | 0.971 | 0.961 | 118 | 136 |
| CA | retail | 6 | naive | univariate | 0.963 | 0.955 | 118 | 136 |
| CA | retail | 6 | timesfm25 | univariate | 0.977 | 0.959 | 118 | 136 |
| CA | retail | 6 | tirex | univariate | 1.018 | 0.964 | 118 | 136 |
| CA | retail | 6 | tirex2 | multivariate | 0.970 | 0.956 | 118 | 136 |
| CA | retail | 6 | tirex2 | univariate | 0.972 | 0.957 | 118 | 136 |
| CA | retail | 12 | bvar | multivariate | 0.863 | 0.995 | 113 | 130 |
| CA | retail | 12 | chronos2 | multivariate | 0.860 | 1.005 | 113 | 131 |
| CA | retail | 12 | chronos2 | univariate | 0.856 | 1.074 | 113 | 131 |
| CA | retail | 12 | combo_bench | multivariate | 0.887 | 0.994 | 110 | 127 |
| CA | retail | 12 | combo_fm | univariate | 0.868 | 0.970 | 113 | 131 |
| CA | retail | 12 | dfm | multivariate | 0.854 | 0.981 | 110 | 128 |
| CA | retail | 12 | moirai2 | univariate | 0.869 | 0.975 | 113 | 131 |
| CA | retail | 12 | naive | univariate | 0.857 | 0.981 | 113 | 131 |
| CA | retail | 12 | timesfm25 | univariate | 0.874 | 0.978 | 113 | 131 |
| CA | retail | 12 | tirex | univariate | 0.899 | 0.986 | 113 | 131 |
| CA | retail | 12 | tirex2 | multivariate | 0.858 | 0.981 | 113 | 131 |
| CA | retail | 12 | tirex2 | univariate | 0.858 | 0.982 | 113 | 131 |
| CA | unemp | 1 | bvar | multivariate | 0.983 | 0.970 | 124 | 141 |
| CA | unemp | 1 | chronos2 | multivariate | 0.896 | 1.339 | 124 | 142 |
| CA | unemp | 1 | chronos2 | univariate | 0.918 | 1.100 | 124 | 142 |
| CA | unemp | 1 | combo_bench | multivariate | 0.951 | 0.971 | 121 | 138 |
| CA | unemp | 1 | combo_fm | univariate | 0.905 | 0.987 | 124 | 142 |
| CA | unemp | 1 | dfm | multivariate | 0.984 | 1.006 | 121 | 139 |
| CA | unemp | 1 | moirai2 | univariate | 0.894 | 0.929 | 124 | 142 |
| CA | unemp | 1 | naive | univariate | 0.943 | 0.942 | 124 | 142 |
| CA | unemp | 1 | timesfm25 | univariate | 0.919 | 0.979 | 124 | 142 |
| CA | unemp | 1 | tirex | univariate | 0.916 | 1.007 | 124 | 142 |
| CA | unemp | 1 | tirex2 | multivariate | 0.906 | 1.097 | 124 | 142 |
| CA | unemp | 1 | tirex2 | univariate | 0.910 | 0.999 | 124 | 142 |
| CA | unemp | 3 | bvar | multivariate | 1.191 | 1.022 | 123 | 140 |
| CA | unemp | 3 | chronos2 | multivariate | 0.969 | 1.305 | 123 | 141 |
| CA | unemp | 3 | chronos2 | univariate | 0.970 | 1.082 | 123 | 141 |
| CA | unemp | 3 | combo_bench | multivariate | 1.051 | 0.998 | 120 | 137 |
| CA | unemp | 3 | combo_fm | univariate | 0.935 | 1.004 | 123 | 141 |
| CA | unemp | 3 | dfm | multivariate | 1.016 | 0.979 | 120 | 138 |
| CA | unemp | 3 | moirai2 | univariate | 0.926 | 0.983 | 123 | 141 |
| CA | unemp | 3 | naive | univariate | 0.995 | 0.965 | 123 | 141 |
| CA | unemp | 3 | timesfm25 | univariate | 0.962 | 1.008 | 123 | 141 |
| CA | unemp | 3 | tirex | univariate | 0.933 | 0.987 | 123 | 141 |
| CA | unemp | 3 | tirex2 | multivariate | 0.936 | 1.025 | 123 | 141 |
| CA | unemp | 3 | tirex2 | univariate | 0.928 | 0.998 | 123 | 141 |
| CA | unemp | 6 | bvar | multivariate | 1.036 | 1.008 | 121 | 137 |
| CA | unemp | 6 | chronos2 | multivariate | 0.990 | 1.117 | 121 | 138 |
| CA | unemp | 6 | chronos2 | univariate | 1.033 | 1.007 | 121 | 138 |
| CA | unemp | 6 | combo_bench | multivariate | 1.008 | 1.003 | 118 | 134 |
| CA | unemp | 6 | combo_fm | univariate | 0.980 | 1.001 | 121 | 138 |
| CA | unemp | 6 | dfm | multivariate | 1.001 | 1.001 | 118 | 135 |
| CA | unemp | 6 | moirai2 | univariate | 0.974 | 1.019 | 121 | 138 |
| CA | unemp | 6 | naive | univariate | 1.000 | 0.999 | 121 | 138 |
| CA | unemp | 6 | timesfm25 | univariate | 1.015 | 1.005 | 121 | 138 |
| CA | unemp | 6 | tirex | univariate | 0.974 | 1.002 | 121 | 138 |
| CA | unemp | 6 | tirex2 | multivariate | 0.970 | 1.000 | 121 | 138 |
| CA | unemp | 6 | tirex2 | univariate | 0.968 | 0.998 | 121 | 138 |
| CA | unemp | 12 | bvar | multivariate | 0.959 | 0.990 | 114 | 131 |
| CA | unemp | 12 | chronos2 | multivariate | 0.939 | 0.980 | 114 | 132 |
| CA | unemp | 12 | chronos2 | univariate | 0.953 | 0.983 | 114 | 132 |
| CA | unemp | 12 | combo_bench | multivariate | 0.964 | 0.991 | 111 | 128 |
| CA | unemp | 12 | combo_fm | univariate | 0.926 | 0.984 | 114 | 132 |
| CA | unemp | 12 | dfm | multivariate | 0.939 | 0.987 | 111 | 129 |
| CA | unemp | 12 | moirai2 | univariate | 1.026 | 0.997 | 114 | 132 |
| CA | unemp | 12 | naive | univariate | 0.942 | 0.987 | 114 | 132 |
| CA | unemp | 12 | timesfm25 | univariate | 0.997 | 0.992 | 114 | 132 |
| CA | unemp | 12 | tirex | univariate | 0.917 | 0.984 | 114 | 132 |
| CA | unemp | 12 | tirex2 | multivariate | 0.955 | 0.987 | 114 | 132 |
| CA | unemp | 12 | tirex2 | univariate | 0.974 | 0.987 | 114 | 132 |
| EA | consumption | 1 | bvar | multivariate | 0.901 | 0.570 | 120 | 130 |
| EA | consumption | 1 | chronos2 | multivariate | 0.906 | 0.643 | 120 | 133 |
| EA | consumption | 1 | chronos2 | univariate | 0.987 | 0.700 | 120 | 133 |
| EA | consumption | 1 | combo_bench | multivariate | 0.723 | 0.628 | 120 | 130 |
| EA | consumption | 1 | combo_fm | univariate | 1.060 | 0.600 | 120 | 133 |
| EA | consumption | 1 | dfm | multivariate | 1.074 | 0.466 | 120 | 133 |
| EA | consumption | 1 | moirai2 | univariate | 1.101 | 0.579 | 120 | 133 |
| EA | consumption | 1 | naive | univariate | 0.833 | 0.420 | 120 | 133 |
| EA | consumption | 1 | timesfm25 | univariate | 1.191 | 0.504 | 120 | 133 |
| EA | consumption | 1 | tirex | univariate | 1.211 | 0.670 | 120 | 133 |
| EA | consumption | 1 | tirex2 | multivariate | 0.971 | 0.572 | 120 | 133 |
| EA | consumption | 1 | tirex2 | univariate | 0.996 | 0.573 | 120 | 133 |
| EA | consumption | 2 | bvar | multivariate | 1.394 | 0.717 | 117 | 127 |
| EA | consumption | 2 | chronos2 | multivariate | 1.003 | 0.782 | 117 | 130 |
| EA | consumption | 2 | chronos2 | univariate | 1.114 | 0.869 | 117 | 130 |
| EA | consumption | 2 | combo_bench | multivariate | 1.051 | 0.727 | 117 | 127 |
| EA | consumption | 2 | combo_fm | univariate | 1.276 | 0.736 | 117 | 130 |
| EA | consumption | 2 | dfm | multivariate | 1.077 | 0.663 | 117 | 130 |
| EA | consumption | 2 | moirai2 | univariate | 1.272 | 0.714 | 117 | 130 |
| EA | consumption | 2 | naive | univariate | 0.911 | 0.679 | 117 | 130 |
| EA | consumption | 2 | timesfm25 | univariate | 1.402 | 0.721 | 117 | 130 |
| EA | consumption | 2 | tirex | univariate | 1.430 | 0.771 | 117 | 130 |
| EA | consumption | 2 | tirex2 | multivariate | 1.154 | 0.697 | 117 | 130 |
| EA | consumption | 2 | tirex2 | univariate | 1.200 | 0.695 | 117 | 130 |
| EA | consumption | 4 | bvar | multivariate | 0.367 | 0.913 | 109 | 124 |
| EA | consumption | 4 | chronos2 | multivariate | 0.309 | 0.911 | 109 | 124 |
| EA | consumption | 4 | chronos2 | univariate | 0.286 | 0.908 | 109 | 124 |
| EA | consumption | 4 | combo_bench | multivariate | 0.385 | 0.916 | 109 | 124 |
| EA | consumption | 4 | combo_fm | univariate | 0.247 | 0.906 | 109 | 124 |
| EA | consumption | 4 | dfm | multivariate | 0.317 | 0.915 | 109 | 124 |
| EA | consumption | 4 | moirai2 | univariate | 0.314 | 0.912 | 109 | 124 |
| EA | consumption | 4 | naive | univariate | 0.321 | 0.916 | 109 | 124 |
| EA | consumption | 4 | timesfm25 | univariate | 0.296 | 0.912 | 109 | 124 |
| EA | consumption | 4 | tirex | univariate | 0.315 | 0.911 | 109 | 124 |
| EA | consumption | 4 | tirex2 | multivariate | 0.229 | 0.907 | 109 | 124 |
| EA | consumption | 4 | tirex2 | univariate | 0.229 | 0.907 | 109 | 124 |
| EA | gdp | 1 | bvar | multivariate | 1.809 | 0.411 | 120 | 133 |
| EA | gdp | 1 | chronos2 | multivariate | 0.934 | 0.642 | 119 | 132 |
| EA | gdp | 1 | chronos2 | univariate | 0.918 | 0.840 | 120 | 133 |
| EA | gdp | 1 | combo_bench | multivariate | 1.079 | 0.610 | 120 | 133 |
| EA | gdp | 1 | combo_fm | univariate | 0.926 | 0.707 | 120 | 133 |
| EA | gdp | 1 | dfm | multivariate | 1.964 | 0.496 | 120 | 133 |
| EA | gdp | 1 | moirai2 | univariate | 0.900 | 0.687 | 120 | 133 |
| EA | gdp | 1 | naive | univariate | 0.880 | 0.567 | 120 | 133 |
| EA | gdp | 1 | timesfm25 | univariate | 0.992 | 0.625 | 120 | 133 |
| EA | gdp | 1 | tirex | univariate | 1.019 | 0.795 | 120 | 133 |
| EA | gdp | 1 | tirex2 | multivariate | 0.952 | 0.617 | 119 | 132 |
| EA | gdp | 1 | tirex2 | univariate | 0.958 | 0.619 | 120 | 133 |
| EA | gdp | 2 | bvar | multivariate | 1.966 | 1.025 | 116 | 129 |
| EA | gdp | 2 | chronos2 | multivariate | 1.055 | 0.919 | 115 | 128 |
| EA | gdp | 2 | chronos2 | univariate | 1.077 | 1.099 | 116 | 129 |
| EA | gdp | 2 | combo_bench | multivariate | 1.209 | 0.940 | 116 | 129 |
| EA | gdp | 2 | combo_fm | univariate | 1.181 | 0.927 | 116 | 129 |
| EA | gdp | 2 | dfm | multivariate | 1.361 | 0.916 | 116 | 129 |
| EA | gdp | 2 | moirai2 | univariate | 1.177 | 0.907 | 116 | 129 |
| EA | gdp | 2 | naive | univariate | 1.015 | 0.867 | 116 | 129 |
| EA | gdp | 2 | timesfm25 | univariate | 1.236 | 0.919 | 116 | 129 |
| EA | gdp | 2 | tirex | univariate | 1.308 | 0.936 | 116 | 129 |
| EA | gdp | 2 | tirex2 | multivariate | 1.190 | 0.886 | 115 | 128 |
| EA | gdp | 2 | tirex2 | univariate | 1.181 | 0.883 | 116 | 129 |
| EA | gdp | 4 | bvar | multivariate | 1.437 | 1.006 | 109 | 124 |
| EA | gdp | 4 | chronos2 | multivariate | 1.329 | 1.006 | 108 | 123 |
| EA | gdp | 4 | chronos2 | univariate | 1.337 | 1.003 | 109 | 124 |
| EA | gdp | 4 | combo_bench | multivariate | 1.150 | 1.002 | 109 | 124 |
| EA | gdp | 4 | combo_fm | univariate | 1.206 | 1.002 | 109 | 124 |
| EA | gdp | 4 | dfm | multivariate | 1.253 | 1.002 | 109 | 124 |
| EA | gdp | 4 | moirai2 | univariate | 1.458 | 1.003 | 109 | 124 |
| EA | gdp | 4 | naive | univariate | 1.159 | 1.002 | 109 | 124 |
| EA | gdp | 4 | timesfm25 | univariate | 1.815 | 1.009 | 109 | 124 |
| EA | gdp | 4 | tirex | univariate | 1.252 | 1.001 | 109 | 124 |
| EA | gdp | 4 | tirex2 | multivariate | 1.256 | 1.002 | 108 | 123 |
| EA | gdp | 4 | tirex2 | univariate | 1.258 | 1.003 | 109 | 124 |
| EA | hicp | 1 | bvar | multivariate | 0.839 | 0.803 | 124 | 142 |
| EA | hicp | 1 | chronos2 | multivariate | 0.846 | 0.894 | 124 | 142 |
| EA | hicp | 1 | chronos2 | univariate | 0.908 | 0.926 | 124 | 142 |
| EA | hicp | 1 | combo_bench | multivariate | 0.947 | 0.908 | 122 | 140 |
| EA | hicp | 1 | combo_fm | univariate | 0.902 | 0.926 | 124 | 142 |
| EA | hicp | 1 | dfm | multivariate | 1.486 | 1.420 | 122 | 140 |
| EA | hicp | 1 | moirai2 | univariate | 0.917 | 0.937 | 124 | 142 |
| EA | hicp | 1 | naive | univariate | 1.556 | 1.486 | 124 | 142 |
| EA | hicp | 1 | timesfm25 | univariate | 0.902 | 0.940 | 124 | 142 |
| EA | hicp | 1 | tirex | univariate | 1.007 | 1.024 | 124 | 142 |
| EA | hicp | 1 | tirex2 | multivariate | 0.949 | 0.964 | 124 | 142 |
| EA | hicp | 1 | tirex2 | univariate | 0.971 | 0.980 | 124 | 142 |
| EA | hicp | 3 | bvar | multivariate | 0.945 | 0.851 | 122 | 140 |
| EA | hicp | 3 | chronos2 | multivariate | 0.828 | 0.933 | 122 | 140 |
| EA | hicp | 3 | chronos2 | univariate | 0.930 | 0.973 | 122 | 140 |
| EA | hicp | 3 | combo_bench | multivariate | 0.958 | 0.862 | 120 | 138 |
| EA | hicp | 3 | combo_fm | univariate | 0.869 | 0.950 | 122 | 140 |
| EA | hicp | 3 | dfm | multivariate | 1.337 | 1.161 | 120 | 138 |
| EA | hicp | 3 | moirai2 | univariate | 0.926 | 0.987 | 122 | 140 |
| EA | hicp | 3 | naive | univariate | 1.279 | 1.118 | 122 | 140 |
| EA | hicp | 3 | timesfm25 | univariate | 0.848 | 0.931 | 122 | 140 |
| EA | hicp | 3 | tirex | univariate | 0.870 | 0.985 | 122 | 140 |
| EA | hicp | 3 | tirex2 | multivariate | 0.930 | 0.990 | 122 | 140 |
| EA | hicp | 3 | tirex2 | univariate | 0.953 | 1.001 | 122 | 140 |
| EA | hicp | 6 | bvar | multivariate | 0.982 | 0.986 | 118 | 136 |
| EA | hicp | 6 | chronos2 | multivariate | 0.932 | 0.934 | 118 | 136 |
| EA | hicp | 6 | chronos2 | univariate | 0.990 | 0.983 | 118 | 136 |
| EA | hicp | 6 | combo_bench | multivariate | 0.965 | 0.961 | 116 | 134 |
| EA | hicp | 6 | combo_fm | univariate | 0.990 | 0.989 | 118 | 136 |
| EA | hicp | 6 | dfm | multivariate | 1.267 | 1.262 | 116 | 134 |
| EA | hicp | 6 | moirai2 | univariate | 1.028 | 1.030 | 118 | 136 |
| EA | hicp | 6 | naive | univariate | 1.262 | 1.259 | 118 | 136 |
| EA | hicp | 6 | timesfm25 | univariate | 1.001 | 0.997 | 118 | 136 |
| EA | hicp | 6 | tirex | univariate | 1.011 | 1.016 | 118 | 136 |
| EA | hicp | 6 | tirex2 | multivariate | 1.027 | 1.026 | 118 | 136 |
| EA | hicp | 6 | tirex2 | univariate | 1.046 | 1.043 | 118 | 136 |
| EA | hicp | 12 | bvar | multivariate | 1.016 | 1.034 | 113 | 131 |
| EA | hicp | 12 | chronos2 | multivariate | 0.991 | 0.989 | 113 | 131 |
| EA | hicp | 12 | chronos2 | univariate | 1.161 | 1.148 | 113 | 131 |
| EA | hicp | 12 | combo_bench | multivariate | 0.992 | 0.986 | 111 | 129 |
| EA | hicp | 12 | combo_fm | univariate | 1.151 | 1.138 | 113 | 131 |
| EA | hicp | 12 | dfm | multivariate | 1.262 | 1.246 | 111 | 129 |
| EA | hicp | 12 | moirai2 | univariate | 1.163 | 1.156 | 113 | 131 |
| EA | hicp | 12 | naive | univariate | 1.265 | 1.248 | 113 | 131 |
| EA | hicp | 12 | timesfm25 | univariate | 1.132 | 1.119 | 113 | 131 |
| EA | hicp | 12 | tirex | univariate | 1.174 | 1.161 | 113 | 131 |
| EA | hicp | 12 | tirex2 | multivariate | 1.220 | 1.205 | 113 | 131 |
| EA | hicp | 12 | tirex2 | univariate | 1.268 | 1.249 | 113 | 131 |
| EA | hicp_core | 1 | bvar | multivariate | 1.559 | 1.401 | 124 | 142 |
| EA | hicp_core | 1 | chronos2 | multivariate | 0.776 | 0.795 | 88 | 102 |
| EA | hicp_core | 1 | chronos2 | univariate | 0.874 | 0.879 | 124 | 142 |
| EA | hicp_core | 1 | combo_bench | multivariate | 1.533 | 1.377 | 122 | 140 |
| EA | hicp_core | 1 | combo_fm | univariate | 0.803 | 0.841 | 124 | 142 |
| EA | hicp_core | 1 | dfm | multivariate | 3.158 | 2.847 | 122 | 140 |
| EA | hicp_core | 1 | moirai2 | univariate | 0.856 | 0.875 | 124 | 142 |
| EA | hicp_core | 1 | naive | univariate | 3.096 | 2.760 | 124 | 142 |
| EA | hicp_core | 1 | timesfm25 | univariate | 0.837 | 0.859 | 124 | 142 |
| EA | hicp_core | 1 | tirex | univariate | 0.905 | 0.938 | 124 | 142 |
| EA | hicp_core | 1 | tirex2 | multivariate | 0.816 | 0.873 | 88 | 102 |
| EA | hicp_core | 1 | tirex2 | univariate | 0.815 | 0.865 | 124 | 142 |
| EA | hicp_core | 3 | bvar | multivariate | 1.511 | 1.430 | 122 | 140 |
| EA | hicp_core | 3 | chronos2 | multivariate | 0.809 | 0.849 | 87 | 101 |
| EA | hicp_core | 3 | chronos2 | univariate | 0.955 | 0.951 | 122 | 140 |
| EA | hicp_core | 3 | combo_bench | multivariate | 1.460 | 1.340 | 120 | 138 |

_128 more rows in the CSV_

### 5.5 Primary window versus the pre-registered extension (all origins)

| econ | target | horizon | model | variant | rel_rmsfe:all | rel_rmsfe:primary | n:all | n:primary |
|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | bvar | multivariate | 1.047 | 1.049 | 264 | 138 |
| CA | consumption | 1 | chronos2 | multivariate | 1.135 | 1.138 | 211 | 94 |
| CA | consumption | 1 | chronos2 | univariate | 1.318 | 1.323 | 266 | 140 |
| CA | consumption | 1 | combo_bench | multivariate | 0.864 | 0.862 | 249 | 135 |
| CA | consumption | 1 | combo_fm | univariate | 1.015 | 1.016 | 266 | 140 |
| CA | consumption | 1 | dfm | multivariate | 0.576 | 0.569 | 251 | 137 |
| CA | consumption | 1 | moirai2 | univariate | 1.036 | 1.036 | 266 | 140 |
| CA | consumption | 1 | naive | univariate | 0.818 | 0.815 | 266 | 140 |
| CA | consumption | 1 | timesfm25 | univariate | 0.961 | 0.961 | 266 | 140 |
| CA | consumption | 1 | tirex | univariate | 0.960 | 0.959 | 266 | 140 |
| CA | consumption | 1 | tirex2 | multivariate | 0.935 | 0.934 | 211 | 94 |
| CA | consumption | 1 | tirex2 | univariate | 0.848 | 0.846 | 266 | 140 |
| CA | consumption | 2 | bvar | multivariate | 1.145 | 1.150 | 261 | 135 |
| CA | consumption | 2 | chronos2 | multivariate | 1.044 | 1.045 | 209 | 92 |
| CA | consumption | 2 | chronos2 | univariate | 1.204 | 1.208 | 263 | 137 |
| CA | consumption | 2 | combo_bench | multivariate | 1.008 | 1.010 | 246 | 132 |
| CA | consumption | 2 | combo_fm | univariate | 1.010 | 1.010 | 263 | 137 |
| CA | consumption | 2 | dfm | multivariate | 0.967 | 0.967 | 248 | 134 |
| CA | consumption | 2 | moirai2 | univariate | 1.002 | 1.002 | 263 | 137 |
| CA | consumption | 2 | naive | univariate | 0.981 | 0.981 | 263 | 137 |
| CA | consumption | 2 | timesfm25 | univariate | 1.000 | 1.000 | 263 | 137 |
| CA | consumption | 2 | tirex | univariate | 0.985 | 0.983 | 263 | 137 |
| CA | consumption | 2 | tirex2 | multivariate | 0.994 | 0.993 | 209 | 92 |
| CA | consumption | 2 | tirex2 | univariate | 0.987 | 0.987 | 263 | 137 |
| CA | consumption | 4 | bvar | multivariate | 1.232 | 1.239 | 255 | 129 |
| CA | consumption | 4 | chronos2 | multivariate | 1.007 | 1.009 | 205 | 88 |
| CA | consumption | 4 | chronos2 | univariate | 1.116 | 1.118 | 257 | 131 |
| CA | consumption | 4 | combo_bench | multivariate | 1.012 | 1.014 | 240 | 126 |
| CA | consumption | 4 | combo_fm | univariate | 1.007 | 1.007 | 257 | 131 |
| CA | consumption | 4 | dfm | multivariate | 1.000 | 1.001 | 242 | 128 |
| CA | consumption | 4 | moirai2 | univariate | 1.004 | 1.005 | 257 | 131 |
| CA | consumption | 4 | naive | univariate | 1.003 | 1.004 | 257 | 131 |
| CA | consumption | 4 | timesfm25 | univariate | 0.999 | 1.000 | 257 | 131 |
| CA | consumption | 4 | tirex | univariate | 1.001 | 1.001 | 257 | 131 |
| CA | consumption | 4 | tirex2 | multivariate | 1.001 | 1.000 | 205 | 88 |
| CA | consumption | 4 | tirex2 | univariate | 0.994 | 0.994 | 257 | 131 |
| CA | cpi | 1 | bvar | multivariate | 0.964 | 0.976 | 259 | 141 |
| CA | cpi | 1 | chronos2 | multivariate | 0.880 | 0.844 | 260 | 142 |
| CA | cpi | 1 | chronos2 | univariate | 0.899 | 0.862 | 260 | 142 |
| CA | cpi | 1 | combo_bench | multivariate | 0.979 | 0.975 | 241 | 138 |
| CA | cpi | 1 | combo_fm | univariate | 0.890 | 0.856 | 260 | 142 |
| CA | cpi | 1 | dfm | multivariate | 1.011 | 0.988 | 242 | 139 |
| CA | cpi | 1 | moirai2 | univariate | 0.890 | 0.863 | 260 | 142 |
| CA | cpi | 1 | naive | univariate | 1.020 | 1.012 | 260 | 142 |
| CA | cpi | 1 | timesfm25 | univariate | 0.902 | 0.878 | 260 | 142 |
| CA | cpi | 1 | tirex | univariate | 0.914 | 0.886 | 260 | 142 |
| CA | cpi | 1 | tirex2 | multivariate | 0.900 | 0.856 | 260 | 142 |
| CA | cpi | 1 | tirex2 | univariate | 0.897 | 0.854 | 260 | 142 |
| CA | cpi | 3 | bvar | multivariate | 1.000 | 1.003 | 257 | 139 |
| CA | cpi | 3 | chronos2 | multivariate | 0.861 | 0.846 | 258 | 140 |
| CA | cpi | 3 | chronos2 | univariate | 0.854 | 0.822 | 258 | 140 |
| CA | cpi | 3 | combo_bench | multivariate | 0.999 | 1.000 | 239 | 136 |
| CA | cpi | 3 | combo_fm | univariate | 0.853 | 0.818 | 258 | 140 |
| CA | cpi | 3 | dfm | multivariate | 1.002 | 1.001 | 240 | 137 |
| CA | cpi | 3 | moirai2 | univariate | 0.860 | 0.840 | 258 | 140 |
| CA | cpi | 3 | naive | univariate | 1.000 | 0.998 | 258 | 140 |
| CA | cpi | 3 | timesfm25 | univariate | 0.843 | 0.814 | 258 | 140 |
| CA | cpi | 3 | tirex | univariate | 0.872 | 0.829 | 258 | 140 |
| CA | cpi | 3 | tirex2 | multivariate | 0.882 | 0.843 | 258 | 140 |
| CA | cpi | 3 | tirex2 | univariate | 0.876 | 0.831 | 258 | 140 |
| CA | cpi | 6 | bvar | multivariate | 1.005 | 1.014 | 254 | 136 |
| CA | cpi | 6 | chronos2 | multivariate | 0.889 | 0.895 | 255 | 137 |
| CA | cpi | 6 | chronos2 | univariate | 0.872 | 0.862 | 255 | 137 |
| CA | cpi | 6 | combo_bench | multivariate | 1.002 | 1.007 | 236 | 133 |
| CA | cpi | 6 | combo_fm | univariate | 0.872 | 0.851 | 255 | 137 |
| CA | cpi | 6 | dfm | multivariate | 1.005 | 1.011 | 237 | 134 |
| CA | cpi | 6 | moirai2 | univariate | 0.876 | 0.870 | 255 | 137 |
| CA | cpi | 6 | naive | univariate | 1.002 | 1.010 | 255 | 137 |
| CA | cpi | 6 | timesfm25 | univariate | 0.865 | 0.846 | 255 | 137 |
| CA | cpi | 6 | tirex | univariate | 0.884 | 0.852 | 255 | 137 |
| CA | cpi | 6 | tirex2 | multivariate | 0.906 | 0.883 | 255 | 137 |
| CA | cpi | 6 | tirex2 | univariate | 0.899 | 0.872 | 255 | 137 |
| CA | cpi | 12 | bvar | multivariate | 1.085 | 1.107 | 248 | 130 |
| CA | cpi | 12 | chronos2 | multivariate | 0.912 | 0.917 | 249 | 131 |
| CA | cpi | 12 | chronos2 | univariate | 0.901 | 0.891 | 249 | 131 |
| CA | cpi | 12 | combo_bench | multivariate | 1.051 | 1.060 | 230 | 127 |
| CA | cpi | 12 | combo_fm | univariate | 0.894 | 0.874 | 249 | 131 |
| CA | cpi | 12 | dfm | multivariate | 1.081 | 1.103 | 231 | 128 |
| CA | cpi | 12 | moirai2 | univariate | 0.892 | 0.892 | 249 | 131 |
| CA | cpi | 12 | naive | univariate | 1.078 | 1.104 | 249 | 131 |
| CA | cpi | 12 | timesfm25 | univariate | 0.888 | 0.874 | 249 | 131 |
| CA | cpi | 12 | tirex | univariate | 0.918 | 0.884 | 249 | 131 |
| CA | cpi | 12 | tirex2 | multivariate | 0.931 | 0.902 | 249 | 131 |
| CA | cpi | 12 | tirex2 | univariate | 0.915 | 0.888 | 249 | 131 |
| CA | cpi_core | 1 | bvar | multivariate | 1.220 | 1.223 | 309 | 141 |
| CA | cpi_core | 1 | chronos2 | multivariate | 0.979 | 0.999 | 310 | 142 |
| CA | cpi_core | 1 | chronos2 | univariate | 0.990 | 1.030 | 310 | 142 |
| CA | cpi_core | 1 | combo_bench | multivariate | 1.096 | 1.066 | 288 | 138 |
| CA | cpi_core | 1 | combo_fm | univariate | 0.944 | 0.967 | 310 | 142 |
| CA | cpi_core | 1 | dfm | multivariate | 1.225 | 1.179 | 289 | 139 |
| CA | cpi_core | 1 | moirai2 | univariate | 0.956 | 1.002 | 310 | 142 |
| CA | cpi_core | 1 | naive | univariate | 1.220 | 1.172 | 310 | 142 |
| CA | cpi_core | 1 | timesfm25 | univariate | 0.954 | 0.976 | 310 | 142 |
| CA | cpi_core | 1 | tirex | univariate | 0.953 | 0.959 | 310 | 142 |
| CA | cpi_core | 1 | tirex2 | multivariate | 0.941 | 0.950 | 310 | 142 |
| CA | cpi_core | 1 | tirex2 | univariate | 0.938 | 0.948 | 310 | 142 |
| CA | cpi_core | 3 | bvar | multivariate | 1.253 | 1.289 | 307 | 139 |
| CA | cpi_core | 3 | chronos2 | multivariate | 0.970 | 1.021 | 308 | 140 |
| CA | cpi_core | 3 | chronos2 | univariate | 0.982 | 1.046 | 308 | 140 |
| CA | cpi_core | 3 | combo_bench | multivariate | 1.117 | 1.129 | 286 | 136 |
| CA | cpi_core | 3 | combo_fm | univariate | 0.941 | 0.974 | 308 | 140 |
| CA | cpi_core | 3 | dfm | multivariate | 1.254 | 1.271 | 287 | 137 |
| CA | cpi_core | 3 | moirai2 | univariate | 0.965 | 0.999 | 308 | 140 |
| CA | cpi_core | 3 | naive | univariate | 1.254 | 1.268 | 308 | 140 |
| CA | cpi_core | 3 | timesfm25 | univariate | 0.941 | 0.961 | 308 | 140 |
| CA | cpi_core | 3 | tirex | univariate | 0.947 | 0.983 | 308 | 140 |
| CA | cpi_core | 3 | tirex2 | multivariate | 0.943 | 0.960 | 308 | 140 |
| CA | cpi_core | 3 | tirex2 | univariate | 0.936 | 0.950 | 308 | 140 |
| CA | cpi_core | 6 | bvar | multivariate | 1.267 | 1.255 | 304 | 136 |
| CA | cpi_core | 6 | chronos2 | multivariate | 0.997 | 1.059 | 305 | 137 |
| CA | cpi_core | 6 | chronos2 | univariate | 0.979 | 1.040 | 305 | 137 |
| CA | cpi_core | 6 | combo_bench | multivariate | 1.123 | 1.102 | 283 | 133 |
| CA | cpi_core | 6 | combo_fm | univariate | 0.934 | 0.963 | 305 | 137 |
| CA | cpi_core | 6 | dfm | multivariate | 1.270 | 1.237 | 284 | 134 |
| CA | cpi_core | 6 | moirai2 | univariate | 0.927 | 0.968 | 305 | 137 |
| CA | cpi_core | 6 | naive | univariate | 1.270 | 1.237 | 305 | 137 |
| CA | cpi_core | 6 | timesfm25 | univariate | 0.937 | 0.960 | 305 | 137 |
| CA | cpi_core | 6 | tirex | univariate | 0.948 | 0.970 | 305 | 137 |
| CA | cpi_core | 6 | tirex2 | multivariate | 0.980 | 0.992 | 305 | 137 |
| CA | cpi_core | 6 | tirex2 | univariate | 0.953 | 0.957 | 305 | 137 |
| CA | cpi_core | 12 | bvar | multivariate | 1.355 | 1.326 | 298 | 130 |
| CA | cpi_core | 12 | chronos2 | multivariate | 0.995 | 1.047 | 299 | 131 |
| CA | cpi_core | 12 | chronos2 | univariate | 0.967 | 0.995 | 299 | 131 |
| CA | cpi_core | 12 | combo_bench | multivariate | 1.182 | 1.135 | 277 | 127 |
| CA | cpi_core | 12 | combo_fm | univariate | 0.947 | 0.960 | 299 | 131 |
| CA | cpi_core | 12 | dfm | multivariate | 1.362 | 1.282 | 278 | 128 |
| CA | cpi_core | 12 | moirai2 | univariate | 0.956 | 0.990 | 299 | 131 |
| CA | cpi_core | 12 | naive | univariate | 1.363 | 1.316 | 299 | 131 |
| CA | cpi_core | 12 | timesfm25 | univariate | 0.962 | 0.958 | 299 | 131 |
| CA | cpi_core | 12 | tirex | univariate | 0.951 | 0.952 | 299 | 131 |
| CA | cpi_core | 12 | tirex2 | multivariate | 0.995 | 0.975 | 299 | 131 |
| CA | cpi_core | 12 | tirex2 | univariate | 0.962 | 0.965 | 299 | 131 |
| CA | gdp | 1 | bvar | multivariate | 1.114 | 1.119 | 266 | 140 |
| CA | gdp | 1 | chronos2 | multivariate | 1.064 | 1.070 | 211 | 94 |
| CA | gdp | 1 | chronos2 | univariate | 1.315 | 1.324 | 266 | 140 |
| CA | gdp | 1 | combo_bench | multivariate | 0.808 | 0.806 | 251 | 137 |
| CA | gdp | 1 | combo_fm | univariate | 0.994 | 0.996 | 266 | 140 |
| CA | gdp | 1 | dfm | multivariate | 0.420 | 0.407 | 251 | 137 |
| CA | gdp | 1 | moirai2 | univariate | 0.972 | 0.972 | 266 | 140 |
| CA | gdp | 1 | naive | univariate | 0.807 | 0.795 | 266 | 140 |
| CA | gdp | 1 | timesfm25 | univariate | 0.931 | 0.931 | 266 | 140 |
| CA | gdp | 1 | tirex | univariate | 0.956 | 0.957 | 266 | 140 |
| CA | gdp | 1 | tirex2 | multivariate | 0.944 | 0.945 | 211 | 94 |
| CA | gdp | 1 | tirex2 | univariate | 0.848 | 0.846 | 266 | 140 |
| CA | gdp | 2 | bvar | multivariate | 1.151 | 1.164 | 263 | 137 |
| CA | gdp | 2 | chronos2 | multivariate | 1.032 | 1.038 | 209 | 92 |
| CA | gdp | 2 | chronos2 | univariate | 1.334 | 1.351 | 263 | 137 |
| CA | gdp | 2 | combo_bench | multivariate | 0.999 | 1.003 | 248 | 134 |
| CA | gdp | 2 | combo_fm | univariate | 1.020 | 1.023 | 263 | 137 |
| CA | gdp | 2 | dfm | multivariate | 0.928 | 0.928 | 248 | 134 |
| CA | gdp | 2 | moirai2 | univariate | 0.999 | 0.999 | 263 | 137 |
| CA | gdp | 2 | naive | univariate | 0.950 | 0.946 | 263 | 137 |
| CA | gdp | 2 | timesfm25 | univariate | 1.002 | 1.005 | 263 | 137 |
| CA | gdp | 2 | tirex | univariate | 0.962 | 0.962 | 263 | 137 |
| CA | gdp | 2 | tirex2 | multivariate | 0.967 | 0.967 | 209 | 92 |
| CA | gdp | 2 | tirex2 | univariate | 0.951 | 0.951 | 263 | 137 |
| CA | gdp | 4 | bvar | multivariate | 1.110 | 1.121 | 257 | 131 |
| CA | gdp | 4 | chronos2 | multivariate | 1.001 | 1.003 | 205 | 88 |
| CA | gdp | 4 | chronos2 | univariate | 1.199 | 1.212 | 257 | 131 |
| CA | gdp | 4 | combo_bench | multivariate | 1.006 | 1.009 | 242 | 128 |
| CA | gdp | 4 | combo_fm | univariate | 1.000 | 1.004 | 257 | 131 |
| CA | gdp | 4 | dfm | multivariate | 1.002 | 1.000 | 242 | 128 |
| CA | gdp | 4 | moirai2 | univariate | 0.992 | 0.994 | 257 | 131 |
| CA | gdp | 4 | naive | univariate | 1.002 | 1.000 | 257 | 131 |
| CA | gdp | 4 | timesfm25 | univariate | 0.993 | 0.996 | 257 | 131 |
| CA | gdp | 4 | tirex | univariate | 0.990 | 0.992 | 257 | 131 |
| CA | gdp | 4 | tirex2 | multivariate | 0.992 | 0.995 | 205 | 88 |
| CA | gdp | 4 | tirex2 | univariate | 0.989 | 0.992 | 257 | 131 |
| CA | retail | 1 | bvar | multivariate | 0.619 | 0.567 | 300 | 139 |
| CA | retail | 1 | chronos2 | multivariate | 1.151 | 1.161 | 301 | 140 |
| CA | retail | 1 | chronos2 | univariate | 1.210 | 1.222 | 301 | 140 |
| CA | retail | 1 | combo_bench | multivariate | 0.740 | 0.717 | 279 | 136 |
| CA | retail | 1 | combo_fm | univariate | 1.032 | 1.034 | 301 | 140 |
| CA | retail | 1 | dfm | multivariate | 0.744 | 0.725 | 280 | 137 |
| CA | retail | 1 | moirai2 | univariate | 1.040 | 1.041 | 301 | 140 |
| CA | retail | 1 | naive | univariate | 0.915 | 0.908 | 301 | 140 |
| CA | retail | 1 | timesfm25 | univariate | 0.964 | 0.959 | 301 | 140 |
| CA | retail | 1 | tirex | univariate | 0.983 | 0.981 | 301 | 140 |
| CA | retail | 1 | tirex2 | multivariate | 0.958 | 0.954 | 301 | 140 |
| CA | retail | 1 | tirex2 | univariate | 1.022 | 1.023 | 301 | 140 |
| CA | retail | 3 | bvar | multivariate | 0.980 | 0.976 | 302 | 138 |
| CA | retail | 3 | chronos2 | multivariate | 1.115 | 1.124 | 303 | 139 |
| CA | retail | 3 | chronos2 | univariate | 1.152 | 1.164 | 303 | 139 |
| CA | retail | 3 | combo_bench | multivariate | 0.977 | 0.976 | 281 | 135 |
| CA | retail | 3 | combo_fm | univariate | 0.999 | 0.998 | 303 | 139 |
| CA | retail | 3 | dfm | multivariate | 0.975 | 0.974 | 282 | 136 |
| CA | retail | 3 | moirai2 | univariate | 0.995 | 0.994 | 303 | 139 |
| CA | retail | 3 | naive | univariate | 0.981 | 0.980 | 303 | 139 |
| CA | retail | 3 | timesfm25 | univariate | 0.984 | 0.980 | 303 | 139 |
| CA | retail | 3 | tirex | univariate | 0.981 | 0.978 | 303 | 139 |
| CA | retail | 3 | tirex2 | multivariate | 0.983 | 0.981 | 303 | 139 |
| CA | retail | 3 | tirex2 | univariate | 0.984 | 0.983 | 303 | 139 |
| CA | retail | 6 | bvar | multivariate | 0.974 | 0.971 | 299 | 135 |
| CA | retail | 6 | chronos2 | multivariate | 1.057 | 1.062 | 300 | 136 |
| CA | retail | 6 | chronos2 | univariate | 1.120 | 1.130 | 300 | 136 |
| CA | retail | 6 | combo_bench | multivariate | 0.974 | 0.973 | 278 | 132 |
| CA | retail | 6 | combo_fm | univariate | 0.973 | 0.971 | 300 | 136 |
| CA | retail | 6 | dfm | multivariate | 0.959 | 0.956 | 279 | 133 |
| CA | retail | 6 | moirai2 | univariate | 0.964 | 0.961 | 300 | 136 |
| CA | retail | 6 | naive | univariate | 0.958 | 0.955 | 300 | 136 |
| CA | retail | 6 | timesfm25 | univariate | 0.963 | 0.959 | 300 | 136 |
| CA | retail | 6 | tirex | univariate | 0.968 | 0.964 | 300 | 136 |
| CA | retail | 6 | tirex2 | multivariate | 0.959 | 0.956 | 300 | 136 |
| CA | retail | 6 | tirex2 | univariate | 0.960 | 0.957 | 300 | 136 |
| CA | retail | 12 | bvar | multivariate | 0.994 | 0.995 | 295 | 130 |
| CA | retail | 12 | chronos2 | multivariate | 1.003 | 1.005 | 296 | 131 |
| CA | retail | 12 | chronos2 | univariate | 1.067 | 1.074 | 296 | 131 |
| CA | retail | 12 | combo_bench | multivariate | 0.993 | 0.994 | 274 | 127 |
| CA | retail | 12 | combo_fm | univariate | 0.971 | 0.970 | 296 | 131 |
| CA | retail | 12 | dfm | multivariate | 0.981 | 0.981 | 275 | 128 |
| CA | retail | 12 | moirai2 | univariate | 0.975 | 0.975 | 296 | 131 |
| CA | retail | 12 | naive | univariate | 0.981 | 0.981 | 296 | 131 |
| CA | retail | 12 | timesfm25 | univariate | 0.978 | 0.978 | 296 | 131 |
| CA | retail | 12 | tirex | univariate | 0.985 | 0.986 | 296 | 131 |
| CA | retail | 12 | tirex2 | multivariate | 0.982 | 0.981 | 296 | 131 |
| CA | retail | 12 | tirex2 | univariate | 0.982 | 0.982 | 296 | 131 |
| CA | unemp | 1 | bvar | multivariate | 0.972 | 0.970 | 309 | 141 |
| CA | unemp | 1 | chronos2 | multivariate | 1.302 | 1.339 | 310 | 142 |
| CA | unemp | 1 | chronos2 | univariate | 1.088 | 1.100 | 310 | 142 |
| CA | unemp | 1 | combo_bench | multivariate | 0.976 | 0.971 | 288 | 138 |
| CA | unemp | 1 | combo_fm | univariate | 0.987 | 0.987 | 310 | 142 |
| CA | unemp | 1 | dfm | multivariate | 1.015 | 1.006 | 289 | 139 |
| CA | unemp | 1 | moirai2 | univariate | 0.937 | 0.929 | 310 | 142 |
| CA | unemp | 1 | naive | univariate | 0.948 | 0.942 | 310 | 142 |
| CA | unemp | 1 | timesfm25 | univariate | 0.980 | 0.979 | 310 | 142 |
| CA | unemp | 1 | tirex | univariate | 1.004 | 1.007 | 310 | 142 |
| CA | unemp | 1 | tirex2 | multivariate | 1.086 | 1.097 | 310 | 142 |
| CA | unemp | 1 | tirex2 | univariate | 0.999 | 0.999 | 310 | 142 |
| CA | unemp | 3 | bvar | multivariate | 1.019 | 1.022 | 308 | 140 |
| CA | unemp | 3 | chronos2 | multivariate | 1.286 | 1.305 | 309 | 141 |
| CA | unemp | 3 | chronos2 | univariate | 1.075 | 1.082 | 309 | 141 |
| CA | unemp | 3 | combo_bench | multivariate | 0.996 | 0.998 | 287 | 137 |
| CA | unemp | 3 | combo_fm | univariate | 1.004 | 1.004 | 309 | 141 |
| CA | unemp | 3 | dfm | multivariate | 0.978 | 0.979 | 288 | 138 |
| CA | unemp | 3 | moirai2 | univariate | 0.983 | 0.983 | 309 | 141 |
| CA | unemp | 3 | naive | univariate | 0.967 | 0.965 | 309 | 141 |
| CA | unemp | 3 | timesfm25 | univariate | 1.008 | 1.008 | 309 | 141 |
| CA | unemp | 3 | tirex | univariate | 0.988 | 0.987 | 309 | 141 |
| CA | unemp | 3 | tirex2 | multivariate | 1.023 | 1.025 | 309 | 141 |
| CA | unemp | 3 | tirex2 | univariate | 0.998 | 0.998 | 309 | 141 |
| CA | unemp | 6 | bvar | multivariate | 1.007 | 1.008 | 305 | 137 |
| CA | unemp | 6 | chronos2 | multivariate | 1.110 | 1.117 | 306 | 138 |
| CA | unemp | 6 | chronos2 | univariate | 1.008 | 1.007 | 306 | 138 |
| CA | unemp | 6 | combo_bench | multivariate | 1.002 | 1.003 | 284 | 134 |
| CA | unemp | 6 | combo_fm | univariate | 1.002 | 1.001 | 306 | 138 |
| CA | unemp | 6 | dfm | multivariate | 1.002 | 1.001 | 285 | 135 |
| CA | unemp | 6 | moirai2 | univariate | 1.018 | 1.019 | 306 | 138 |
| CA | unemp | 6 | naive | univariate | 0.998 | 0.999 | 306 | 138 |
| CA | unemp | 6 | timesfm25 | univariate | 1.006 | 1.005 | 306 | 138 |
| CA | unemp | 6 | tirex | univariate | 1.004 | 1.002 | 306 | 138 |
| CA | unemp | 6 | tirex2 | multivariate | 1.003 | 1.000 | 306 | 138 |
| CA | unemp | 6 | tirex2 | univariate | 1.000 | 0.998 | 306 | 138 |
| CA | unemp | 12 | bvar | multivariate | 0.991 | 0.990 | 299 | 131 |
| CA | unemp | 12 | chronos2 | multivariate | 0.985 | 0.980 | 300 | 132 |
| CA | unemp | 12 | chronos2 | univariate | 0.987 | 0.983 | 300 | 132 |
| CA | unemp | 12 | combo_bench | multivariate | 0.992 | 0.991 | 278 | 128 |
| CA | unemp | 12 | combo_fm | univariate | 0.988 | 0.984 | 300 | 132 |
| CA | unemp | 12 | dfm | multivariate | 0.988 | 0.987 | 279 | 129 |
| CA | unemp | 12 | moirai2 | univariate | 1.001 | 0.997 | 300 | 132 |
| CA | unemp | 12 | naive | univariate | 0.988 | 0.987 | 300 | 132 |
| CA | unemp | 12 | timesfm25 | univariate | 0.996 | 0.992 | 300 | 132 |
| CA | unemp | 12 | tirex | univariate | 0.988 | 0.984 | 300 | 132 |
| CA | unemp | 12 | tirex2 | multivariate | 0.990 | 0.987 | 300 | 132 |
| CA | unemp | 12 | tirex2 | univariate | 0.990 | 0.987 | 300 | 132 |
| EA | consumption | 1 | bvar | multivariate | 0.580 | 0.570 | 292 | 130 |
| EA | consumption | 1 | chronos2 | multivariate | 0.645 | 0.643 | 295 | 133 |
| EA | consumption | 1 | chronos2 | univariate | 0.701 | 0.700 | 295 | 133 |
| EA | consumption | 1 | combo_bench | multivariate | 0.634 | 0.628 | 292 | 130 |
| EA | consumption | 1 | combo_fm | univariate | 0.601 | 0.600 | 295 | 133 |
| EA | consumption | 1 | dfm | multivariate | 0.469 | 0.466 | 295 | 133 |
| EA | consumption | 1 | moirai2 | univariate | 0.581 | 0.579 | 295 | 133 |
| EA | consumption | 1 | naive | univariate | 0.425 | 0.420 | 295 | 133 |
| EA | consumption | 1 | timesfm25 | univariate | 0.506 | 0.504 | 295 | 133 |
| EA | consumption | 1 | tirex | univariate | 0.671 | 0.670 | 295 | 133 |
| EA | consumption | 1 | tirex2 | multivariate | 0.574 | 0.572 | 295 | 133 |
| EA | consumption | 1 | tirex2 | univariate | 0.574 | 0.573 | 295 | 133 |
| EA | consumption | 2 | bvar | multivariate | 0.720 | 0.717 | 289 | 127 |
| EA | consumption | 2 | chronos2 | multivariate | 0.784 | 0.782 | 292 | 130 |
| EA | consumption | 2 | chronos2 | univariate | 0.870 | 0.869 | 292 | 130 |
| EA | consumption | 2 | combo_bench | multivariate | 0.729 | 0.727 | 289 | 127 |
| EA | consumption | 2 | combo_fm | univariate | 0.738 | 0.736 | 292 | 130 |
| EA | consumption | 2 | dfm | multivariate | 0.667 | 0.663 | 292 | 130 |
| EA | consumption | 2 | moirai2 | univariate | 0.717 | 0.714 | 292 | 130 |
| EA | consumption | 2 | naive | univariate | 0.684 | 0.679 | 292 | 130 |
| EA | consumption | 2 | timesfm25 | univariate | 0.723 | 0.721 | 292 | 130 |
| EA | consumption | 2 | tirex | univariate | 0.772 | 0.771 | 292 | 130 |
| EA | consumption | 2 | tirex2 | multivariate | 0.700 | 0.697 | 292 | 130 |
| EA | consumption | 2 | tirex2 | univariate | 0.698 | 0.695 | 292 | 130 |
| EA | consumption | 4 | bvar | multivariate | 0.915 | 0.913 | 286 | 124 |
| EA | consumption | 4 | chronos2 | multivariate | 0.912 | 0.911 | 286 | 124 |
| EA | consumption | 4 | chronos2 | univariate | 0.911 | 0.908 | 286 | 124 |
| EA | consumption | 4 | combo_bench | multivariate | 0.917 | 0.916 | 286 | 124 |
| EA | consumption | 4 | combo_fm | univariate | 0.907 | 0.906 | 286 | 124 |
| EA | consumption | 4 | dfm | multivariate | 0.917 | 0.915 | 286 | 124 |
| EA | consumption | 4 | moirai2 | univariate | 0.913 | 0.912 | 286 | 124 |
| EA | consumption | 4 | naive | univariate | 0.919 | 0.916 | 286 | 124 |
| EA | consumption | 4 | timesfm25 | univariate | 0.913 | 0.912 | 286 | 124 |
| EA | consumption | 4 | tirex | univariate | 0.912 | 0.911 | 286 | 124 |
| EA | consumption | 4 | tirex2 | multivariate | 0.908 | 0.907 | 286 | 124 |
| EA | consumption | 4 | tirex2 | univariate | 0.908 | 0.907 | 286 | 124 |
| EA | gdp | 1 | bvar | multivariate | 0.421 | 0.411 | 295 | 133 |
| EA | gdp | 1 | chronos2 | multivariate | 0.650 | 0.642 | 294 | 132 |
| EA | gdp | 1 | chronos2 | univariate | 0.842 | 0.840 | 295 | 133 |
| EA | gdp | 1 | combo_bench | multivariate | 0.614 | 0.610 | 295 | 133 |
| EA | gdp | 1 | combo_fm | univariate | 0.710 | 0.707 | 295 | 133 |
| EA | gdp | 1 | dfm | multivariate | 0.502 | 0.496 | 295 | 133 |
| EA | gdp | 1 | moirai2 | univariate | 0.692 | 0.687 | 295 | 133 |
| EA | gdp | 1 | naive | univariate | 0.578 | 0.567 | 295 | 133 |
| EA | gdp | 1 | timesfm25 | univariate | 0.629 | 0.625 | 295 | 133 |
| EA | gdp | 1 | tirex | univariate | 0.798 | 0.795 | 295 | 133 |
| EA | gdp | 1 | tirex2 | multivariate | 0.623 | 0.617 | 294 | 132 |
| EA | gdp | 1 | tirex2 | univariate | 0.625 | 0.619 | 295 | 133 |
| EA | gdp | 2 | bvar | multivariate | 1.018 | 1.025 | 291 | 129 |
| EA | gdp | 2 | chronos2 | multivariate | 0.926 | 0.919 | 290 | 128 |
| EA | gdp | 2 | chronos2 | univariate | 1.095 | 1.099 | 291 | 129 |
| EA | gdp | 2 | combo_bench | multivariate | 0.933 | 0.940 | 291 | 129 |
| EA | gdp | 2 | combo_fm | univariate | 0.929 | 0.927 | 291 | 129 |
| EA | gdp | 2 | dfm | multivariate | 0.907 | 0.916 | 291 | 129 |
| EA | gdp | 2 | moirai2 | univariate | 0.911 | 0.907 | 291 | 129 |
| EA | gdp | 2 | naive | univariate | 0.869 | 0.867 | 291 | 129 |
| EA | gdp | 2 | timesfm25 | univariate | 0.916 | 0.919 | 291 | 129 |
| EA | gdp | 2 | tirex | univariate | 0.941 | 0.936 | 291 | 129 |
| EA | gdp | 2 | tirex2 | multivariate | 0.889 | 0.886 | 290 | 128 |
| EA | gdp | 2 | tirex2 | univariate | 0.885 | 0.883 | 291 | 129 |
| EA | gdp | 4 | bvar | multivariate | 1.011 | 1.006 | 286 | 124 |
| EA | gdp | 4 | chronos2 | multivariate | 1.016 | 1.006 | 285 | 123 |
| EA | gdp | 4 | chronos2 | univariate | 1.017 | 1.003 | 286 | 124 |
| EA | gdp | 4 | combo_bench | multivariate | 1.001 | 1.002 | 286 | 124 |
| EA | gdp | 4 | combo_fm | univariate | 1.010 | 1.002 | 286 | 124 |
| EA | gdp | 4 | dfm | multivariate | 1.001 | 1.002 | 286 | 124 |
| EA | gdp | 4 | moirai2 | univariate | 1.016 | 1.003 | 286 | 124 |
| EA | gdp | 4 | naive | univariate | 1.002 | 1.002 | 286 | 124 |
| EA | gdp | 4 | timesfm25 | univariate | 1.012 | 1.009 | 286 | 124 |
| EA | gdp | 4 | tirex | univariate | 1.016 | 1.001 | 286 | 124 |
| EA | gdp | 4 | tirex2 | multivariate | 1.005 | 1.002 | 285 | 123 |
| EA | gdp | 4 | tirex2 | univariate | 1.006 | 1.003 | 286 | 124 |
| EA | hicp | 1 | bvar | multivariate | 0.824 | 0.803 | 310 | 142 |
| EA | hicp | 1 | chronos2 | multivariate | 0.839 | 0.894 | 310 | 142 |
| EA | hicp | 1 | chronos2 | univariate | 0.881 | 0.926 | 310 | 142 |
| EA | hicp | 1 | combo_bench | multivariate | 0.954 | 0.908 | 308 | 140 |
| EA | hicp | 1 | combo_fm | univariate | 0.888 | 0.926 | 310 | 142 |
| EA | hicp | 1 | dfm | multivariate | 1.468 | 1.420 | 308 | 140 |
| EA | hicp | 1 | moirai2 | univariate | 0.906 | 0.937 | 310 | 142 |
| EA | hicp | 1 | naive | univariate | 1.475 | 1.486 | 310 | 142 |
| EA | hicp | 1 | timesfm25 | univariate | 0.908 | 0.940 | 310 | 142 |
| EA | hicp | 1 | tirex | univariate | 0.965 | 1.024 | 310 | 142 |
| EA | hicp | 1 | tirex2 | multivariate | 0.913 | 0.964 | 310 | 142 |
| EA | hicp | 1 | tirex2 | univariate | 0.931 | 0.980 | 310 | 142 |
| EA | hicp | 3 | bvar | multivariate | 0.885 | 0.851 | 308 | 140 |
| EA | hicp | 3 | chronos2 | multivariate | 0.862 | 0.933 | 308 | 140 |
| EA | hicp | 3 | chronos2 | univariate | 0.909 | 0.973 | 308 | 140 |
| EA | hicp | 3 | combo_bench | multivariate | 0.947 | 0.862 | 306 | 138 |
| EA | hicp | 3 | combo_fm | univariate | 0.898 | 0.950 | 308 | 140 |
| EA | hicp | 3 | dfm | multivariate | 1.312 | 1.161 | 306 | 138 |
| EA | hicp | 3 | moirai2 | univariate | 0.921 | 0.987 | 308 | 140 |
| EA | hicp | 3 | naive | univariate | 1.274 | 1.118 | 308 | 140 |
| EA | hicp | 3 | timesfm25 | univariate | 0.912 | 0.931 | 308 | 140 |
| EA | hicp | 3 | tirex | univariate | 0.930 | 0.985 | 308 | 140 |
| EA | hicp | 3 | tirex2 | multivariate | 0.928 | 0.990 | 308 | 140 |
| EA | hicp | 3 | tirex2 | univariate | 0.936 | 1.001 | 308 | 140 |
| EA | hicp | 6 | bvar | multivariate | 0.976 | 0.986 | 304 | 136 |
| EA | hicp | 6 | chronos2 | multivariate | 0.878 | 0.934 | 304 | 136 |
| EA | hicp | 6 | chronos2 | univariate | 0.924 | 0.983 | 304 | 136 |
| EA | hicp | 6 | combo_bench | multivariate | 1.014 | 0.961 | 302 | 134 |
| EA | hicp | 6 | combo_fm | univariate | 0.930 | 0.989 | 304 | 136 |
| EA | hicp | 6 | dfm | multivariate | 1.376 | 1.262 | 302 | 134 |
| EA | hicp | 6 | moirai2 | univariate | 0.958 | 1.030 | 304 | 136 |
| EA | hicp | 6 | naive | univariate | 1.390 | 1.259 | 304 | 136 |
| EA | hicp | 6 | timesfm25 | univariate | 0.948 | 0.997 | 304 | 136 |
| EA | hicp | 6 | tirex | univariate | 0.954 | 1.016 | 304 | 136 |
| EA | hicp | 6 | tirex2 | multivariate | 0.960 | 1.026 | 304 | 136 |
| EA | hicp | 6 | tirex2 | univariate | 0.971 | 1.043 | 304 | 136 |
| EA | hicp | 12 | bvar | multivariate | 1.060 | 1.034 | 299 | 131 |
| EA | hicp | 12 | chronos2 | multivariate | 0.944 | 0.989 | 299 | 131 |
| EA | hicp | 12 | chronos2 | univariate | 1.076 | 1.148 | 299 | 131 |
| EA | hicp | 12 | combo_bench | multivariate | 1.051 | 0.986 | 297 | 129 |
| EA | hicp | 12 | combo_fm | univariate | 1.071 | 1.138 | 299 | 131 |
| EA | hicp | 12 | dfm | multivariate | 1.413 | 1.246 | 297 | 129 |
| EA | hicp | 12 | moirai2 | univariate | 1.094 | 1.156 | 299 | 131 |
| EA | hicp | 12 | naive | univariate | 1.424 | 1.248 | 299 | 131 |
| EA | hicp | 12 | timesfm25 | univariate | 1.061 | 1.119 | 299 | 131 |
| EA | hicp | 12 | tirex | univariate | 1.093 | 1.161 | 299 | 131 |
| EA | hicp | 12 | tirex2 | multivariate | 1.120 | 1.205 | 299 | 131 |
| EA | hicp | 12 | tirex2 | univariate | 1.156 | 1.249 | 299 | 131 |
| EA | hicp_core | 1 | bvar | multivariate | 1.480 | 1.401 | 202 | 142 |
| EA | hicp_core | 1 | chronos2 | multivariate | 0.853 | 0.795 | 162 | 102 |
| EA | hicp_core | 1 | chronos2 | univariate | 0.899 | 0.879 | 202 | 142 |
| EA | hicp_core | 1 | combo_bench | multivariate | 1.536 | 1.377 | 200 | 140 |
| EA | hicp_core | 1 | combo_fm | univariate | 0.861 | 0.841 | 202 | 142 |
| EA | hicp_core | 1 | dfm | multivariate | 3.290 | 2.847 | 200 | 140 |
| EA | hicp_core | 1 | moirai2 | univariate | 0.929 | 0.875 | 202 | 142 |
| EA | hicp_core | 1 | naive | univariate | 3.186 | 2.760 | 202 | 142 |
| EA | hicp_core | 1 | timesfm25 | univariate | 0.867 | 0.859 | 202 | 142 |
| EA | hicp_core | 1 | tirex | univariate | 0.950 | 0.938 | 202 | 142 |
| EA | hicp_core | 1 | tirex2 | multivariate | 0.910 | 0.873 | 162 | 102 |
| EA | hicp_core | 1 | tirex2 | univariate | 0.887 | 0.865 | 202 | 142 |
| EA | hicp_core | 3 | bvar | multivariate | 1.572 | 1.430 | 200 | 140 |
| EA | hicp_core | 3 | chronos2 | multivariate | 0.923 | 0.849 | 161 | 101 |
| EA | hicp_core | 3 | chronos2 | univariate | 0.992 | 0.951 | 200 | 140 |
| EA | hicp_core | 3 | combo_bench | multivariate | 1.529 | 1.340 | 198 | 138 |

_128 more rows in the CSV_

### 5.6 Levels variant (foundation models only), cumulative h-step change

| econ | target | horizon | model | variant | n | rmsfe | mae | bias | wql | coverage80 |
|---|---|---|---|---|---|---|---|---|---|---|
| CA | consumption | 1 | chronos2 | multivariate_levels | 94 | 3.509 | 1.407 | -0.372 | 1.163 | 0.830 |
| CA | consumption | 1 | chronos2 | univariate_levels | 140 | 3.495 | 1.416 | -0.448 | 1.171 | 0.850 |
| CA | consumption | 1 | moirai2 | univariate_levels | 140 | 2.777 | 1.428 | -1.031 | 1.188 | 0.529 |
| CA | consumption | 1 | timesfm25 | univariate_levels | 140 | 3.098 | 1.322 | -0.132 | 1.171 | 0.871 |
| CA | consumption | 1 | tirex | univariate_levels | 140 | 3.559 | 1.253 | 0.319 | 1.058 | 0.807 |
| CA | consumption | 1 | tirex2 | multivariate_levels | 94 | 3.421 | 1.121 | 0.099 | 1.048 | 0.787 |
| CA | consumption | 1 | tirex2 | univariate_levels | 140 | 3.042 | 1.048 | 0.044 | 0.978 | 0.829 |
| CA | consumption | 2 | chronos2 | multivariate_levels | 92 | 4.068 | 1.671 | -0.402 | 1.396 | 0.804 |
| CA | consumption | 2 | chronos2 | univariate_levels | 137 | 4.266 | 1.629 | -0.146 | 1.379 | 0.891 |
| CA | consumption | 2 | moirai2 | univariate_levels | 137 | 3.252 | 1.584 | -1.153 | 1.375 | 0.679 |
| CA | consumption | 2 | timesfm25 | univariate_levels | 137 | 3.411 | 1.546 | 0.151 | 1.397 | 0.847 |
| CA | consumption | 2 | tirex | univariate_levels | 137 | 3.929 | 1.595 | 0.037 | 1.390 | 0.825 |
| CA | consumption | 2 | tirex2 | multivariate_levels | 92 | 4.234 | 1.517 | 0.092 | 1.419 | 0.761 |
| CA | consumption | 2 | tirex2 | univariate_levels | 137 | 3.671 | 1.423 | 0.031 | 1.318 | 0.745 |
| CA | consumption | 4 | chronos2 | multivariate_levels | 88 | 4.605 | 2.131 | -0.232 | 1.835 | 0.773 |
| CA | consumption | 4 | chronos2 | univariate_levels | 131 | 5.371 | 2.482 | 0.369 | 2.138 | 0.702 |
| CA | consumption | 4 | moirai2 | univariate_levels | 131 | 3.750 | 1.977 | -1.160 | 1.795 | 0.679 |
| CA | consumption | 4 | timesfm25 | univariate_levels | 131 | 3.507 | 1.940 | 0.146 | 1.690 | 0.817 |
| CA | consumption | 4 | tirex | univariate_levels | 131 | 4.583 | 2.272 | 0.069 | 2.084 | 0.748 |
| CA | consumption | 4 | tirex2 | multivariate_levels | 88 | 5.032 | 2.321 | 0.045 | 2.102 | 0.727 |
| CA | consumption | 4 | tirex2 | univariate_levels | 131 | 4.286 | 2.200 | -0.053 | 1.976 | 0.634 |
| CA | cpi | 1 | chronos2 | multivariate_levels | 142 | 0.400 | 0.305 | -0.005 | 0.243 | 0.887 |
| CA | cpi | 1 | chronos2 | univariate_levels | 142 | 0.541 | 0.390 | -0.174 | 0.303 | 0.894 |
| CA | cpi | 1 | moirai2 | univariate_levels | 142 | 0.562 | 0.464 | -0.393 | 0.368 | 0.556 |
| CA | cpi | 1 | timesfm25 | univariate_levels | 142 | 0.374 | 0.305 | 0.040 | 0.251 | 0.901 |
| CA | cpi | 1 | tirex | univariate_levels | 142 | 0.350 | 0.273 | 0.055 | 0.210 | 0.789 |
| CA | cpi | 1 | tirex2 | multivariate_levels | 142 | 0.328 | 0.258 | 0.028 | 0.200 | 0.845 |
| CA | cpi | 1 | tirex2 | univariate_levels | 142 | 0.322 | 0.251 | 0.035 | 0.197 | 0.859 |
| CA | cpi | 3 | chronos2 | multivariate_levels | 140 | 0.696 | 0.520 | 0.197 | 0.422 | 0.764 |
| CA | cpi | 3 | chronos2 | univariate_levels | 140 | 0.758 | 0.570 | -0.007 | 0.447 | 0.814 |
| CA | cpi | 3 | moirai2 | univariate_levels | 140 | 0.721 | 0.572 | -0.166 | 0.441 | 0.679 |
| CA | cpi | 3 | timesfm25 | univariate_levels | 140 | 0.813 | 0.613 | 0.402 | 0.493 | 0.879 |
| CA | cpi | 3 | tirex | univariate_levels | 140 | 0.643 | 0.471 | 0.192 | 0.361 | 0.843 |
| CA | cpi | 3 | tirex2 | multivariate_levels | 140 | 0.661 | 0.456 | 0.090 | 0.366 | 0.864 |
| CA | cpi | 3 | tirex2 | univariate_levels | 140 | 0.599 | 0.440 | 0.118 | 0.347 | 0.879 |
| CA | cpi | 6 | chronos2 | multivariate_levels | 137 | 1.163 | 0.811 | 0.390 | 0.665 | 0.737 |
| CA | cpi | 6 | chronos2 | univariate_levels | 137 | 1.253 | 0.919 | 0.167 | 0.721 | 0.737 |
| CA | cpi | 6 | moirai2 | univariate_levels | 137 | 1.116 | 0.809 | 0.159 | 0.650 | 0.723 |
| CA | cpi | 6 | timesfm25 | univariate_levels | 137 | 1.320 | 0.927 | 0.704 | 0.766 | 0.869 |
| CA | cpi | 6 | tirex | univariate_levels | 137 | 1.084 | 0.724 | 0.419 | 0.601 | 0.774 |
| CA | cpi | 6 | tirex2 | multivariate_levels | 137 | 1.218 | 0.781 | 0.173 | 0.647 | 0.818 |
| CA | cpi | 6 | tirex2 | univariate_levels | 137 | 1.051 | 0.701 | 0.228 | 0.585 | 0.832 |
| CA | cpi | 12 | chronos2 | multivariate_levels | 131 | 1.885 | 1.296 | 0.485 | 1.093 | 0.748 |
| CA | cpi | 12 | chronos2 | univariate_levels | 131 | 2.088 | 1.469 | 0.185 | 1.190 | 0.695 |
| CA | cpi | 12 | moirai2 | univariate_levels | 131 | 1.865 | 1.199 | 0.853 | 1.019 | 0.771 |
| CA | cpi | 12 | timesfm25 | univariate_levels | 131 | 2.061 | 1.383 | 1.129 | 1.175 | 0.832 |
| CA | cpi | 12 | tirex | univariate_levels | 131 | 1.889 | 1.232 | 0.927 | 1.054 | 0.802 |
| CA | cpi | 12 | tirex2 | multivariate_levels | 131 | 2.258 | 1.395 | 0.288 | 1.180 | 0.779 |
| CA | cpi | 12 | tirex2 | univariate_levels | 131 | 1.812 | 1.180 | 0.467 | 1.003 | 0.794 |
| CA | cpi_core | 1 | chronos2 | multivariate_levels | 142 | 0.354 | 0.292 | -0.057 | 0.222 | 0.796 |
| CA | cpi_core | 1 | chronos2 | univariate_levels | 142 | 0.438 | 0.340 | -0.197 | 0.258 | 0.937 |
| CA | cpi_core | 1 | moirai2 | univariate_levels | 142 | 0.546 | 0.453 | -0.426 | 0.372 | 0.472 |
| CA | cpi_core | 1 | timesfm25 | univariate_levels | 142 | 0.351 | 0.283 | -0.137 | 0.246 | 0.937 |
| CA | cpi_core | 1 | tirex | univariate_levels | 142 | 0.268 | 0.217 | 0.052 | 0.166 | 0.894 |
| CA | cpi_core | 1 | tirex2 | multivariate_levels | 142 | 0.244 | 0.197 | 0.030 | 0.152 | 0.852 |
| CA | cpi_core | 1 | tirex2 | univariate_levels | 142 | 0.242 | 0.193 | 0.027 | 0.150 | 0.852 |
| CA | cpi_core | 3 | chronos2 | multivariate_levels | 140 | 0.509 | 0.415 | 0.091 | 0.324 | 0.750 |
| CA | cpi_core | 3 | chronos2 | univariate_levels | 140 | 0.567 | 0.446 | -0.030 | 0.352 | 0.786 |
| CA | cpi_core | 3 | moirai2 | univariate_levels | 140 | 0.598 | 0.494 | -0.266 | 0.384 | 0.529 |
| CA | cpi_core | 3 | timesfm25 | univariate_levels | 140 | 0.509 | 0.395 | 0.171 | 0.340 | 0.979 |
| CA | cpi_core | 3 | tirex | univariate_levels | 140 | 0.451 | 0.340 | 0.074 | 0.270 | 0.807 |
| CA | cpi_core | 3 | tirex2 | multivariate_levels | 140 | 0.427 | 0.334 | 0.057 | 0.260 | 0.864 |
| CA | cpi_core | 3 | tirex2 | univariate_levels | 140 | 0.425 | 0.326 | 0.054 | 0.256 | 0.886 |
| CA | cpi_core | 6 | chronos2 | multivariate_levels | 137 | 0.766 | 0.584 | 0.183 | 0.454 | 0.803 |
| CA | cpi_core | 6 | chronos2 | univariate_levels | 137 | 0.860 | 0.684 | 0.181 | 0.517 | 0.766 |
| CA | cpi_core | 6 | moirai2 | univariate_levels | 137 | 0.745 | 0.569 | -0.025 | 0.456 | 0.620 |
| CA | cpi_core | 6 | timesfm25 | univariate_levels | 137 | 0.748 | 0.543 | 0.173 | 0.477 | 0.971 |
| CA | cpi_core | 6 | tirex | univariate_levels | 137 | 0.684 | 0.490 | 0.129 | 0.392 | 0.803 |
| CA | cpi_core | 6 | tirex2 | multivariate_levels | 137 | 0.694 | 0.509 | 0.092 | 0.403 | 0.869 |
| CA | cpi_core | 6 | tirex2 | univariate_levels | 137 | 0.672 | 0.478 | 0.107 | 0.385 | 0.883 |
| CA | cpi_core | 12 | chronos2 | multivariate_levels | 131 | 1.302 | 0.950 | 0.220 | 0.770 | 0.725 |
| CA | cpi_core | 12 | chronos2 | univariate_levels | 131 | 1.416 | 1.083 | 0.275 | 0.858 | 0.626 |
| CA | cpi_core | 12 | moirai2 | univariate_levels | 131 | 1.206 | 0.777 | 0.494 | 0.657 | 0.733 |
| CA | cpi_core | 12 | timesfm25 | univariate_levels | 131 | 1.281 | 0.850 | 0.333 | 0.753 | 0.870 |
| CA | cpi_core | 12 | tirex | univariate_levels | 131 | 1.194 | 0.792 | 0.390 | 0.672 | 0.779 |
| CA | cpi_core | 12 | tirex2 | multivariate_levels | 131 | 1.261 | 0.889 | 0.183 | 0.721 | 0.779 |
| CA | cpi_core | 12 | tirex2 | univariate_levels | 131 | 1.162 | 0.772 | 0.239 | 0.651 | 0.832 |
| CA | gdp | 1 | chronos2 | multivariate_levels | 94 | 2.471 | 1.170 | -0.617 | 0.953 | 0.809 |
| CA | gdp | 1 | chronos2 | univariate_levels | 140 | 3.370 | 1.448 | -0.585 | 1.153 | 0.829 |
| CA | gdp | 1 | moirai2 | univariate_levels | 140 | 2.398 | 1.297 | -1.221 | 1.088 | 0.571 |
| CA | gdp | 1 | timesfm25 | univariate_levels | 140 | 3.020 | 1.125 | -0.109 | 0.992 | 0.914 |
| CA | gdp | 1 | tirex | univariate_levels | 140 | 2.801 | 1.057 | 0.078 | 0.886 | 0.807 |
| CA | gdp | 1 | tirex2 | multivariate_levels | 94 | 2.856 | 1.038 | 0.002 | 0.889 | 0.851 |
| CA | gdp | 1 | tirex2 | univariate_levels | 140 | 2.589 | 0.968 | -0.039 | 0.838 | 0.786 |
| CA | gdp | 2 | chronos2 | multivariate_levels | 92 | 3.112 | 1.453 | -0.639 | 1.212 | 0.804 |
| CA | gdp | 2 | chronos2 | univariate_levels | 137 | 3.755 | 1.606 | -0.544 | 1.312 | 0.847 |
| CA | gdp | 2 | moirai2 | univariate_levels | 137 | 2.866 | 1.544 | -1.379 | 1.289 | 0.803 |
| CA | gdp | 2 | timesfm25 | univariate_levels | 137 | 3.757 | 1.477 | 0.172 | 1.299 | 0.934 |
| CA | gdp | 2 | tirex | univariate_levels | 137 | 3.348 | 1.391 | -0.193 | 1.174 | 0.869 |
| CA | gdp | 2 | tirex2 | multivariate_levels | 92 | 3.784 | 1.500 | -0.127 | 1.296 | 0.804 |
| CA | gdp | 2 | tirex2 | univariate_levels | 137 | 3.375 | 1.370 | -0.160 | 1.195 | 0.803 |
| CA | gdp | 4 | chronos2 | multivariate_levels | 88 | 3.435 | 1.726 | -0.544 | 1.516 | 0.864 |
| CA | gdp | 4 | chronos2 | univariate_levels | 131 | 3.624 | 1.746 | -0.381 | 1.541 | 0.817 |
| CA | gdp | 4 | moirai2 | univariate_levels | 131 | 3.186 | 1.721 | -1.313 | 1.487 | 0.885 |
| CA | gdp | 4 | timesfm25 | univariate_levels | 131 | 3.684 | 1.691 | -0.355 | 1.530 | 0.931 |
| CA | gdp | 4 | tirex | univariate_levels | 131 | 3.730 | 1.802 | -0.154 | 1.584 | 0.863 |
| CA | gdp | 4 | tirex2 | multivariate_levels | 88 | 4.511 | 1.996 | -0.384 | 1.763 | 0.750 |
| CA | gdp | 4 | tirex2 | univariate_levels | 131 | 3.935 | 1.818 | -0.358 | 1.621 | 0.794 |
| CA | retail | 1 | chronos2 | multivariate_levels | 140 | 3.704 | 1.378 | -0.311 | 1.142 | 0.807 |
| CA | retail | 1 | chronos2 | univariate_levels | 140 | 3.858 | 1.466 | -0.344 | 1.188 | 0.836 |
| CA | retail | 1 | moirai2 | univariate_levels | 140 | 3.551 | 1.503 | -0.844 | 1.235 | 0.557 |
| CA | retail | 1 | timesfm25 | univariate_levels | 140 | 3.207 | 1.223 | -0.219 | 1.046 | 0.843 |
| CA | retail | 1 | tirex | univariate_levels | 140 | 3.586 | 1.333 | 0.008 | 1.110 | 0.807 |
| CA | retail | 1 | tirex2 | multivariate_levels | 140 | 3.783 | 1.353 | -0.072 | 1.238 | 0.864 |
| CA | retail | 1 | tirex2 | univariate_levels | 140 | 3.656 | 1.331 | -0.068 | 1.170 | 0.836 |
| CA | retail | 3 | chronos2 | multivariate_levels | 139 | 5.855 | 1.999 | -0.124 | 1.721 | 0.806 |
| CA | retail | 3 | chronos2 | univariate_levels | 139 | 5.812 | 2.015 | -0.267 | 1.686 | 0.835 |
| CA | retail | 3 | moirai2 | univariate_levels | 139 | 4.890 | 1.904 | -0.767 | 1.594 | 0.662 |
| CA | retail | 3 | timesfm25 | univariate_levels | 139 | 4.495 | 1.766 | -0.056 | 1.522 | 0.914 |
| CA | retail | 3 | tirex | univariate_levels | 139 | 5.559 | 1.926 | 0.041 | 1.637 | 0.835 |
| CA | retail | 3 | tirex2 | multivariate_levels | 139 | 5.949 | 2.023 | -0.106 |  | 0.892 |
| CA | retail | 3 | tirex2 | univariate_levels | 139 | 5.568 | 1.970 | -0.091 | 1.789 | 0.899 |
| CA | retail | 6 | chronos2 | multivariate_levels | 136 | 6.180 | 2.231 | 0.081 | 1.934 | 0.824 |
| CA | retail | 6 | chronos2 | univariate_levels | 136 | 5.959 | 2.232 | -0.047 | 1.863 | 0.772 |
| CA | retail | 6 | moirai2 | univariate_levels | 136 | 4.628 | 2.024 | -0.625 | 1.675 | 0.838 |
| CA | retail | 6 | timesfm25 | univariate_levels | 136 | 4.713 | 2.085 | -0.055 | 1.806 | 0.912 |
| CA | retail | 6 | tirex | univariate_levels | 136 | 5.783 | 2.185 | -0.026 | 1.814 | 0.868 |
| CA | retail | 6 | tirex2 | multivariate_levels | 136 | 6.378 | 2.344 | -0.184 |  | 0.926 |
| CA | retail | 6 | tirex2 | univariate_levels | 136 | 5.863 | 2.256 | -0.130 | 2.075 | 0.926 |
| CA | retail | 12 | chronos2 | multivariate_levels | 131 | 6.210 | 2.553 | 0.061 | 2.202 | 0.809 |
| CA | retail | 12 | chronos2 | univariate_levels | 131 | 6.044 | 2.596 | -0.158 | 2.122 | 0.763 |
| CA | retail | 12 | moirai2 | univariate_levels | 131 | 4.708 | 2.154 | -0.161 | 1.914 | 0.863 |
| CA | retail | 12 | timesfm25 | univariate_levels | 131 | 4.871 | 2.292 | 0.230 | 1.956 | 0.924 |
| CA | retail | 12 | tirex | univariate_levels | 131 | 5.744 | 2.494 | 0.157 | 2.065 | 0.901 |
| CA | retail | 12 | tirex2 | multivariate_levels | 131 | 6.409 | 2.522 | -0.242 |  | 0.924 |
| CA | retail | 12 | tirex2 | univariate_levels | 131 | 5.922 | 2.485 | -0.119 | 2.372 | 0.924 |
| CA | unemp | 1 | chronos2 | multivariate_levels | 142 | 0.402 | 0.230 | -0.032 | 0.185 | 0.739 |
| CA | unemp | 1 | chronos2 | univariate_levels | 142 | 0.425 | 0.240 | -0.045 | 0.200 | 0.648 |
| CA | unemp | 1 | moirai2 | univariate_levels | 142 | 0.408 | 0.228 | -0.003 | 0.185 | 0.676 |
| CA | unemp | 1 | timesfm25 | univariate_levels | 142 | 0.440 | 0.244 | -0.007 | 0.195 | 0.725 |
| CA | unemp | 1 | tirex | univariate_levels | 142 | 0.423 | 0.229 | -0.035 | 0.191 | 0.704 |
| CA | unemp | 1 | tirex2 | multivariate_levels | 142 | 0.397 | 0.217 | -0.006 | 0.184 | 0.718 |
| CA | unemp | 1 | tirex2 | univariate_levels | 142 | 0.444 | 0.233 | -0.032 | 0.199 | 0.768 |
| CA | unemp | 3 | chronos2 | multivariate_levels | 141 | 1.291 | 0.493 | 0.042 | 0.438 | 0.723 |
| CA | unemp | 3 | chronos2 | univariate_levels | 141 | 1.339 | 0.523 | 0.018 | 0.450 | 0.716 |
| CA | unemp | 3 | moirai2 | univariate_levels | 141 | 1.288 | 0.493 | 0.072 | 0.416 | 0.752 |
| CA | unemp | 3 | timesfm25 | univariate_levels | 141 | 1.277 | 0.507 | 0.086 | 0.433 | 0.688 |
| CA | unemp | 3 | tirex | univariate_levels | 141 | 1.304 | 0.498 | 0.025 | 0.424 | 0.794 |
| CA | unemp | 3 | tirex2 | multivariate_levels | 141 | 1.263 | 0.475 | 0.077 | 0.413 | 0.787 |
| CA | unemp | 3 | tirex2 | univariate_levels | 141 | 1.331 | 0.511 | 0.053 | 0.441 | 0.766 |
| CA | unemp | 6 | chronos2 | multivariate_levels | 138 | 1.570 | 0.752 | 0.036 | 0.666 | 0.681 |
| CA | unemp | 6 | chronos2 | univariate_levels | 138 | 1.609 | 0.762 | 0.014 | 0.654 | 0.688 |
| CA | unemp | 6 | moirai2 | univariate_levels | 138 | 1.510 | 0.711 | 0.081 | 0.608 | 0.768 |
| CA | unemp | 6 | timesfm25 | univariate_levels | 138 | 1.462 | 0.711 | 0.144 | 0.606 | 0.703 |
| CA | unemp | 6 | tirex | univariate_levels | 138 | 1.536 | 0.721 | -0.005 | 0.616 | 0.717 |
| CA | unemp | 6 | tirex2 | multivariate_levels | 138 | 1.499 | 0.695 | 0.073 | 0.595 | 0.754 |
| CA | unemp | 6 | tirex2 | univariate_levels | 138 | 1.571 | 0.725 | 0.058 | 0.620 | 0.804 |
| CA | unemp | 12 | chronos2 | multivariate_levels | 132 | 1.931 | 1.145 | 0.081 | 1.006 | 0.621 |
| CA | unemp | 12 | chronos2 | univariate_levels | 132 | 1.944 | 1.176 | 0.014 | 0.974 | 0.689 |
| CA | unemp | 12 | moirai2 | univariate_levels | 132 | 1.853 | 1.118 | 0.159 | 0.927 | 0.742 |
| CA | unemp | 12 | timesfm25 | univariate_levels | 132 | 1.672 | 1.046 | 0.323 | 0.875 | 0.591 |
| CA | unemp | 12 | tirex | univariate_levels | 132 | 1.861 | 1.149 | -0.052 | 0.963 | 0.674 |
| CA | unemp | 12 | tirex2 | multivariate_levels | 132 | 1.763 | 1.064 | 0.158 | 0.906 | 0.659 |
| CA | unemp | 12 | tirex2 | univariate_levels | 132 | 1.830 | 1.087 | 0.137 | 0.916 | 0.727 |
| EA | consumption | 1 | chronos2 | multivariate_levels | 133 | 3.099 | 1.197 | -0.291 | 1.026 | 0.797 |
| EA | consumption | 1 | chronos2 | univariate_levels | 133 | 3.316 | 1.223 | -0.235 | 1.031 | 0.910 |
| EA | consumption | 1 | moirai2 | univariate_levels | 133 | 3.221 | 1.269 | 0.131 | 1.051 | 0.774 |
| EA | consumption | 1 | timesfm25 | univariate_levels | 133 | 3.445 | 1.192 | -0.119 | 1.003 | 0.752 |
| EA | consumption | 1 | tirex | univariate_levels | 133 | 3.305 | 1.085 | -0.054 | 0.922 | 0.902 |
| EA | consumption | 1 | tirex2 | multivariate_levels | 133 | 2.906 | 1.100 | -0.058 | 0.940 | 0.842 |
| EA | consumption | 1 | tirex2 | univariate_levels | 133 | 3.281 | 1.142 | -0.033 | 0.986 | 0.865 |
| EA | consumption | 2 | chronos2 | multivariate_levels | 130 | 4.040 | 1.564 | -0.299 | 1.402 | 0.800 |
| EA | consumption | 2 | chronos2 | univariate_levels | 130 | 4.278 | 1.611 | -0.197 | 1.449 | 0.846 |
| EA | consumption | 2 | moirai2 | univariate_levels | 130 | 3.944 | 1.774 | 0.136 | 1.503 | 0.685 |
| EA | consumption | 2 | timesfm25 | univariate_levels | 130 | 4.626 | 1.816 | -0.064 | 1.583 | 0.869 |
| EA | consumption | 2 | tirex | univariate_levels | 130 | 4.445 | 1.697 | -0.178 | 1.460 | 0.900 |
| EA | consumption | 2 | tirex2 | multivariate_levels | 130 | 4.011 | 1.628 | -0.011 | 1.401 | 0.792 |
| EA | consumption | 2 | tirex2 | univariate_levels | 130 | 4.520 | 1.807 | 0.066 | 1.585 | 0.815 |
| EA | consumption | 4 | chronos2 | multivariate_levels | 124 | 3.620 | 1.753 | -0.439 | 1.568 | 0.815 |
| EA | consumption | 4 | chronos2 | univariate_levels | 124 | 3.784 | 1.865 | -0.286 | 1.642 | 0.847 |
| EA | consumption | 4 | moirai2 | univariate_levels | 124 | 3.745 | 2.201 | 0.111 | 1.933 | 0.556 |
| EA | consumption | 4 | timesfm25 | univariate_levels | 124 | 3.991 | 1.980 | -0.223 | 1.793 | 0.806 |
| EA | consumption | 4 | tirex | univariate_levels | 124 | 3.909 | 1.889 | -0.456 | 1.709 | 0.871 |
| EA | consumption | 4 | tirex2 | multivariate_levels | 124 | 3.901 | 2.051 | -0.138 | 1.776 | 0.685 |
| EA | consumption | 4 | tirex2 | univariate_levels | 124 | 4.197 | 2.144 | -0.162 | 1.890 | 0.718 |
| EA | gdp | 1 | chronos2 | multivariate_levels | 132 | 2.792 | 1.016 | -0.305 | 0.879 | 0.909 |
| EA | gdp | 1 | chronos2 | univariate_levels | 133 | 3.097 | 1.103 | -0.300 | 0.958 | 0.902 |
| EA | gdp | 1 | moirai2 | univariate_levels | 133 | 3.127 | 1.167 | 0.151 | 0.983 | 0.857 |
| EA | gdp | 1 | timesfm25 | univariate_levels | 133 | 3.438 | 1.144 | -0.165 | 0.995 | 0.677 |
| EA | gdp | 1 | tirex | univariate_levels | 133 | 3.445 | 1.036 | -0.009 | 0.924 | 0.917 |
| EA | gdp | 1 | tirex2 | multivariate_levels | 132 | 2.964 | 0.981 | -0.001 | 0.891 | 0.886 |
| EA | gdp | 1 | tirex2 | univariate_levels | 133 | 3.218 | 0.969 | -0.135 | 0.905 | 0.902 |
| EA | gdp | 2 | chronos2 | multivariate_levels | 128 | 2.975 | 1.183 | 0.036 | 1.014 | 0.867 |
| EA | gdp | 2 | chronos2 | univariate_levels | 129 | 3.250 | 1.249 | 0.022 | 1.074 | 0.899 |
| EA | gdp | 2 | moirai2 | univariate_levels | 129 | 3.099 | 1.471 | 0.568 | 1.176 | 0.698 |
| EA | gdp | 2 | timesfm25 | univariate_levels | 129 | 4.117 | 1.413 | 0.430 | 1.265 | 0.915 |
| EA | gdp | 2 | tirex | univariate_levels | 129 | 3.892 | 1.287 | 0.252 | 1.139 | 0.915 |
| EA | gdp | 2 | tirex2 | multivariate_levels | 128 | 3.123 | 1.140 | 0.281 | 1.027 | 0.883 |
| EA | gdp | 2 | tirex2 | univariate_levels | 129 | 3.459 | 1.143 | 0.035 | 1.055 | 0.915 |
| EA | gdp | 4 | chronos2 | multivariate_levels | 123 | 3.121 | 1.622 | -0.072 | 1.387 | 0.837 |
| EA | gdp | 4 | chronos2 | univariate_levels | 124 | 3.230 | 1.723 | -0.171 | 1.438 | 0.847 |
| EA | gdp | 4 | moirai2 | univariate_levels | 124 | 3.290 | 2.075 | 0.564 | 1.748 | 0.565 |
| EA | gdp | 4 | timesfm25 | univariate_levels | 124 | 3.481 | 1.906 | 0.313 | 1.659 | 0.734 |
| EA | gdp | 4 | tirex | univariate_levels | 124 | 3.236 | 1.620 | -0.055 | 1.441 | 0.839 |
| EA | gdp | 4 | tirex2 | multivariate_levels | 123 | 3.482 | 1.831 | 0.082 | 1.580 | 0.789 |
| EA | gdp | 4 | tirex2 | univariate_levels | 124 | 3.279 | 1.545 | -0.608 | 1.361 | 0.766 |
| EA | hicp | 1 | chronos2 | multivariate_levels | 141 | 0.555 | 0.378 | 0.146 | 0.320 | 0.837 |
| EA | hicp | 1 | chronos2 | univariate_levels | 141 | 0.700 | 0.435 | 0.016 | 0.369 | 0.872 |
| EA | hicp | 1 | moirai2 | univariate_levels | 141 | 0.705 | 0.525 | -0.366 | 0.438 | 0.631 |
| EA | hicp | 1 | timesfm25 | univariate_levels | 141 | 0.498 | 0.345 | 0.055 | 0.286 | 0.801 |
| EA | hicp | 1 | tirex | univariate_levels | 141 | 0.472 | 0.334 | 0.009 | 0.263 | 0.780 |
| EA | hicp | 1 | tirex2 | multivariate_levels | 141 | 0.406 | 0.281 | 0.052 | 0.218 | 0.823 |
| EA | hicp | 1 | tirex2 | univariate_levels | 141 | 0.407 | 0.280 | 0.080 | 0.220 | 0.794 |
| EA | hicp | 3 | chronos2 | multivariate_levels | 139 | 0.913 | 0.607 | 0.333 | 0.526 | 0.763 |
| EA | hicp | 3 | chronos2 | univariate_levels | 139 | 1.032 | 0.691 | 0.210 | 0.578 | 0.856 |
| EA | hicp | 3 | moirai2 | univariate_levels | 139 | 0.830 | 0.651 | -0.095 | 0.509 | 0.626 |
| EA | hicp | 3 | timesfm25 | univariate_levels | 139 | 0.860 | 0.579 | 0.366 | 0.462 | 0.914 |
| EA | hicp | 3 | tirex | univariate_levels | 139 | 0.761 | 0.530 | 0.067 | 0.444 | 0.755 |
| EA | hicp | 3 | tirex2 | multivariate_levels | 139 | 0.757 | 0.524 | 0.114 | 0.429 | 0.791 |
| EA | hicp | 3 | tirex2 | univariate_levels | 139 | 0.749 | 0.515 | 0.187 | 0.427 | 0.784 |
| EA | hicp | 6 | chronos2 | multivariate_levels | 135 | 1.381 | 0.922 | 0.593 | 0.771 | 0.726 |
| EA | hicp | 6 | chronos2 | univariate_levels | 135 | 1.509 | 1.056 | 0.469 | 0.861 | 0.756 |
| EA | hicp | 6 | moirai2 | univariate_levels | 135 | 1.265 | 0.918 | 0.235 | 0.721 | 0.778 |
| EA | hicp | 6 | timesfm25 | univariate_levels | 135 | 1.319 | 0.886 | 0.610 | 0.731 | 0.867 |
| EA | hicp | 6 | tirex | univariate_levels | 135 | 1.161 | 0.835 | 0.267 | 0.697 | 0.726 |
| EA | hicp | 6 | tirex2 | multivariate_levels | 135 | 1.127 | 0.789 | 0.251 | 0.650 | 0.770 |
| EA | hicp | 6 | tirex2 | univariate_levels | 135 | 1.145 | 0.804 | 0.374 | 0.658 | 0.785 |
| EA | hicp | 12 | chronos2 | multivariate_levels | 130 | 2.464 | 1.490 | 0.935 | 1.340 | 0.723 |
| EA | hicp | 12 | chronos2 | univariate_levels | 130 | 2.658 | 1.746 | 0.767 | 1.470 | 0.785 |
| EA | hicp | 12 | moirai2 | univariate_levels | 130 | 2.580 | 1.590 | 1.068 | 1.359 | 0.731 |
| EA | hicp | 12 | timesfm25 | univariate_levels | 130 | 2.473 | 1.497 | 0.996 | 1.313 | 0.862 |
| EA | hicp | 12 | tirex | univariate_levels | 130 | 2.249 | 1.388 | 0.701 | 1.236 | 0.777 |
| EA | hicp | 12 | tirex2 | multivariate_levels | 130 | 2.199 | 1.335 | 0.665 | 1.167 | 0.754 |
| EA | hicp | 12 | tirex2 | univariate_levels | 130 | 2.246 | 1.369 | 0.866 | 1.180 | 0.746 |
| EA | hicp_core | 1 | chronos2 | multivariate_levels | 102 | 0.348 | 0.257 | -0.013 | 0.207 | 0.863 |
| EA | hicp_core | 1 | chronos2 | univariate_levels | 142 | 0.407 | 0.308 | -0.068 | 0.241 | 0.817 |
| EA | hicp_core | 1 | moirai2 | univariate_levels | 142 | 0.545 | 0.397 | -0.241 | 0.337 | 0.803 |
| EA | hicp_core | 1 | timesfm25 | univariate_levels | 142 | 0.308 | 0.234 | -0.061 | 0.242 | 0.951 |
| EA | hicp_core | 1 | tirex | univariate_levels | 142 | 0.290 | 0.218 | 0.094 | 0.169 | 0.838 |
| EA | hicp_core | 1 | tirex2 | multivariate_levels | 102 | 0.236 | 0.166 | 0.003 | 0.136 | 0.843 |
| EA | hicp_core | 1 | tirex2 | univariate_levels | 142 | 0.246 | 0.176 | 0.005 | 0.145 | 0.803 |
| EA | hicp_core | 3 | chronos2 | multivariate_levels | 101 | 0.520 | 0.401 | 0.073 | 0.321 | 0.683 |
| EA | hicp_core | 3 | chronos2 | univariate_levels | 140 | 0.620 | 0.471 | 0.025 | 0.381 | 0.679 |
| EA | hicp_core | 3 | moirai2 | univariate_levels | 140 | 0.680 | 0.527 | -0.016 | 0.409 | 0.779 |
| EA | hicp_core | 3 | timesfm25 | univariate_levels | 140 | 0.541 | 0.418 | 0.177 | 0.368 | 0.936 |
| EA | hicp_core | 3 | tirex | univariate_levels | 140 | 0.454 | 0.343 | 0.142 | 0.272 | 0.743 |
| EA | hicp_core | 3 | tirex2 | multivariate_levels | 101 | 0.398 | 0.298 | 0.018 | 0.250 | 0.792 |
| EA | hicp_core | 3 | tirex2 | univariate_levels | 140 | 0.407 | 0.302 | 0.031 | 0.254 | 0.807 |
| EA | hicp_core | 6 | chronos2 | multivariate_levels | 100 | 0.793 | 0.583 | 0.221 | 0.449 | 0.670 |
| EA | hicp_core | 6 | chronos2 | univariate_levels | 137 | 0.977 | 0.708 | 0.203 | 0.562 | 0.620 |
| EA | hicp_core | 6 | moirai2 | univariate_levels | 137 | 0.949 | 0.728 | 0.029 | 0.567 | 0.781 |
| EA | hicp_core | 6 | timesfm25 | univariate_levels | 137 | 0.755 | 0.560 | 0.277 | 0.499 | 0.956 |
| EA | hicp_core | 6 | tirex | univariate_levels | 137 | 0.749 | 0.540 | 0.255 | 0.435 | 0.701 |
| EA | hicp_core | 6 | tirex2 | multivariate_levels | 100 | 0.644 | 0.496 | 0.083 | 0.393 | 0.760 |
| EA | hicp_core | 6 | tirex2 | univariate_levels | 137 | 0.655 | 0.503 | 0.115 | 0.402 | 0.774 |
| EA | hicp_core | 12 | chronos2 | multivariate_levels | 96 | 1.315 | 0.816 | 0.346 | 0.690 | 0.740 |
| EA | hicp_core | 12 | chronos2 | univariate_levels | 131 | 1.563 | 1.002 | 0.379 | 0.859 | 0.687 |
| EA | hicp_core | 12 | moirai2 | univariate_levels | 131 | 1.605 | 0.879 | 0.658 | 0.822 | 0.794 |
| EA | hicp_core | 12 | timesfm25 | univariate_levels | 131 | 1.343 | 0.870 | 0.366 | 0.779 | 0.863 |
| EA | hicp_core | 12 | tirex | univariate_levels | 131 | 1.426 | 0.919 | 0.455 | 0.755 | 0.725 |
| EA | hicp_core | 12 | tirex2 | multivariate_levels | 96 | 1.251 | 0.830 | 0.229 | 0.699 | 0.771 |
| EA | hicp_core | 12 | tirex2 | univariate_levels | 131 | 1.266 | 0.844 | 0.316 | 0.712 | 0.802 |
| EA | retail | 1 | chronos2 | multivariate_levels | 142 | 2.916 | 1.136 | -0.094 | 0.959 | 0.704 |
| EA | retail | 1 | chronos2 | univariate_levels | 142 | 3.103 | 1.154 | -0.094 | 0.995 | 0.789 |
| EA | retail | 1 | moirai2 | univariate_levels | 142 | 2.697 | 1.095 | -0.062 | 0.928 | 0.732 |
| EA | retail | 1 | timesfm25 | univariate_levels | 142 | 2.573 | 1.006 | -0.121 | 0.866 | 0.866 |
| EA | retail | 1 | tirex | univariate_levels | 142 | 2.905 | 1.107 | -0.006 | 0.944 | 0.739 |
| EA | retail | 1 | tirex2 | multivariate_levels | 142 | 2.544 | 1.032 | -0.143 | 0.882 | 0.817 |
| EA | retail | 1 | tirex2 | univariate_levels | 142 | 2.672 | 1.078 | -0.140 | 0.920 | 0.838 |
| EA | retail | 3 | chronos2 | multivariate_levels | 141 | 4.204 | 1.593 | -0.007 | 1.364 | 0.716 |
| EA | retail | 3 | chronos2 | univariate_levels | 141 | 4.270 | 1.594 | -0.048 | 1.386 | 0.738 |
| EA | retail | 3 | moirai2 | univariate_levels | 141 | 3.919 | 1.599 | 0.026 | 1.305 | 0.745 |
| EA | retail | 3 | timesfm25 | univariate_levels | 141 | 3.382 | 1.376 | -0.018 | 1.176 | 0.837 |
| EA | retail | 3 | tirex | univariate_levels | 141 | 4.134 | 1.632 | -0.038 | 1.325 | 0.773 |
| EA | retail | 3 | tirex2 | multivariate_levels | 141 | 3.717 | 1.510 | -0.068 | 1.222 | 0.823 |
| EA | retail | 3 | tirex2 | univariate_levels | 141 | 3.781 | 1.550 | -0.109 | 1.255 | 0.830 |
| EA | retail | 6 | chronos2 | multivariate_levels | 138 | 4.127 | 1.615 | 0.276 | 1.376 | 0.812 |
| EA | retail | 6 | chronos2 | univariate_levels | 138 | 4.299 | 1.717 | 0.221 | 1.464 | 0.768 |
| EA | retail | 6 | moirai2 | univariate_levels | 138 | 3.780 | 1.674 | 0.423 | 1.374 | 0.761 |
| EA | retail | 6 | timesfm25 | univariate_levels | 138 | 3.313 | 1.491 | 0.331 | 1.235 | 0.855 |
| EA | retail | 6 | tirex | univariate_levels | 138 | 4.031 | 1.689 | 0.170 | 1.336 | 0.804 |
| EA | retail | 6 | tirex2 | multivariate_levels | 138 | 3.468 | 1.501 | 0.249 | 1.198 | 0.833 |
| EA | retail | 6 | tirex2 | univariate_levels | 138 | 3.649 | 1.559 | 0.169 | 1.231 | 0.884 |
| EA | retail | 12 | chronos2 | multivariate_levels | 132 | 3.912 | 2.034 | 0.476 | 1.640 | 0.765 |
| EA | retail | 12 | chronos2 | univariate_levels | 132 | 4.160 | 2.168 | 0.308 | 1.809 | 0.689 |
| EA | retail | 12 | moirai2 | univariate_levels | 132 | 3.604 | 2.299 | 0.964 | 1.789 | 0.621 |
| EA | retail | 12 | timesfm25 | univariate_levels | 132 | 3.101 | 2.078 | 0.643 | 1.564 | 0.818 |
| EA | retail | 12 | tirex | univariate_levels | 132 | 3.760 | 2.151 | 0.375 | 1.666 | 0.803 |
| EA | retail | 12 | tirex2 | multivariate_levels | 132 | 2.994 | 1.912 | 0.559 | 1.491 | 0.841 |
| EA | retail | 12 | tirex2 | univariate_levels | 132 | 3.274 | 1.942 | 0.393 | 1.505 | 0.856 |
| EA | unemp | 1 | chronos2 | multivariate_levels | 132 | 0.087 | 0.066 | 0.007 | 0.053 | 0.750 |
| EA | unemp | 1 | chronos2 | univariate_levels | 132 | 0.085 | 0.067 | 0.013 | 0.056 | 0.538 |
| EA | unemp | 1 | moirai2 | univariate_levels | 132 | 0.090 | 0.073 | -0.025 | 0.058 | 0.621 |
| EA | unemp | 1 | timesfm25 | univariate_levels | 132 | 0.083 | 0.069 | -0.003 | 0.054 | 0.629 |
| EA | unemp | 1 | tirex | univariate_levels | 132 | 0.081 | 0.068 | -0.008 | 0.053 | 0.545 |
| EA | unemp | 1 | tirex2 | multivariate_levels | 132 | 0.079 | 0.066 | -0.012 | 0.051 | 0.803 |
| EA | unemp | 1 | tirex2 | univariate_levels | 132 | 0.079 | 0.066 | -0.008 | 0.050 | 0.902 |
| EA | unemp | 3 | chronos2 | multivariate_levels | 129 | 0.171 | 0.113 | -0.009 | 0.093 | 0.829 |
| EA | unemp | 3 | chronos2 | univariate_levels | 129 | 0.170 | 0.113 | -0.037 | 0.089 | 0.829 |
| EA | unemp | 3 | moirai2 | univariate_levels | 129 | 0.187 | 0.132 | -0.070 | 0.104 | 0.806 |
| EA | unemp | 3 | timesfm25 | univariate_levels | 129 | 0.176 | 0.121 | -0.046 | 0.095 | 0.822 |
| EA | unemp | 3 | tirex | univariate_levels | 129 | 0.176 | 0.120 | -0.039 | 0.093 | 0.783 |
| EA | unemp | 3 | tirex2 | multivariate_levels | 129 | 0.166 | 0.117 | -0.049 | 0.092 | 0.806 |
| EA | unemp | 3 | tirex2 | univariate_levels | 129 | 0.169 | 0.118 | -0.048 | 0.092 | 0.829 |
| EA | unemp | 6 | chronos2 | multivariate_levels | 123 | 0.342 | 0.221 | -0.021 | 0.182 | 0.821 |
| EA | unemp | 6 | chronos2 | univariate_levels | 123 | 0.331 | 0.211 | -0.093 | 0.172 | 0.837 |
| EA | unemp | 6 | moirai2 | univariate_levels | 123 | 0.349 | 0.234 | -0.108 | 0.188 | 0.837 |
| EA | unemp | 6 | timesfm25 | univariate_levels | 123 | 0.331 | 0.224 | -0.111 | 0.179 | 0.862 |
| EA | unemp | 6 | tirex | univariate_levels | 123 | 0.328 | 0.214 | -0.093 | 0.172 | 0.886 |
| EA | unemp | 6 | tirex2 | multivariate_levels | 123 | 0.312 | 0.213 | -0.107 | 0.170 | 0.797 |
| EA | unemp | 6 | tirex2 | univariate_levels | 123 | 0.317 | 0.215 | -0.107 | 0.172 | 0.813 |
| EA | unemp | 12 | chronos2 | multivariate_levels | 110 | 0.609 | 0.463 | -0.144 | 0.373 | 0.736 |
| EA | unemp | 12 | chronos2 | univariate_levels | 110 | 0.592 | 0.445 | -0.291 | 0.350 | 0.755 |
| EA | unemp | 12 | moirai2 | univariate_levels | 110 | 0.632 | 0.484 | -0.289 | 0.374 | 0.836 |
| EA | unemp | 12 | timesfm25 | univariate_levels | 110 | 0.598 | 0.451 | -0.290 | 0.347 | 0.791 |
| EA | unemp | 12 | tirex | univariate_levels | 110 | 0.590 | 0.458 | -0.293 | 0.351 | 0.827 |
| EA | unemp | 12 | tirex2 | multivariate_levels | 110 | 0.572 | 0.450 | -0.281 | 0.350 | 0.791 |
| EA | unemp | 12 | tirex2 | univariate_levels | 110 | 0.580 | 0.451 | -0.277 | 0.351 | 0.745 |

## 6. Q4: forecast error on forecast revision (fixed-event sequences)

Slope `beta` of the error (outturn minus forecast) on the revision from the previous origin for the same target period; HAC standard errors. `per_target` rows are per (econ, target); `pooled` rows standardise by target and pool across an economy's targets (`beta_std`).

**per_target**

| econ | target | model | variant | input_mode | outturn | n | n_periods | beta | se_hac | t | alpha |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CA | consumption | ar | univariate | realtime | first_release | 943 | 103 | -1.413 | 0.621 | -2.276 | -0.136 |
| CA | consumption | ar | univariate | realtime | revised_12m | 943 | 103 | -1.437 | 0.608 | -2.366 | -0.112 |
| CA | consumption | bvar | multivariate | realtime | first_release | 935 | 103 | -0.396 | 0.123 | -3.231 | -0.193 |
| CA | consumption | bvar | multivariate | realtime | revised_12m | 935 | 103 | -0.401 | 0.120 | -3.332 | -0.168 |
| CA | consumption | chronos2 | multivariate | realtime | first_release | 729 | 103 | -1.037 | 0.439 | -2.360 | -0.048 |
| CA | consumption | chronos2 | multivariate | realtime | revised_12m | 729 | 103 | -1.036 | 0.438 | -2.363 | -0.019 |
| CA | consumption | chronos2 | multivariate_levels | realtime | first_release | 108 | 102 | 13.506 | 2.036 | 6.633 | -0.393 |
| CA | consumption | chronos2 | multivariate_levels | realtime | revised_12m | 108 | 102 | 11.599 | 1.967 | 5.897 | -0.367 |
| CA | consumption | chronos2 | univariate | realtime | first_release | 943 | 103 | -0.730 | 0.284 | -2.568 | 0.012 |
| CA | consumption | chronos2 | univariate | realtime | revised_12m | 943 | 103 | -0.731 | 0.283 | -2.581 | 0.036 |
| CA | consumption | chronos2 | univariate_levels | realtime | first_release | 163 | 103 | -0.747 | 0.128 | -5.826 | -0.428 |
| CA | consumption | chronos2 | univariate_levels | realtime | revised_12m | 163 | 103 | -0.740 | 0.130 | -5.704 | -0.409 |
| CA | consumption | combo_bench | multivariate | realtime | first_release | 878 | 100 | -0.444 | 0.115 | -3.848 | -0.205 |
| CA | consumption | combo_bench | multivariate | realtime | revised_12m | 878 | 100 | -0.456 | 0.116 | -3.933 | -0.178 |
| CA | consumption | combo_fm | univariate | realtime | first_release | 943 | 103 | -0.997 | 0.444 | -2.248 | -0.077 |
| CA | consumption | combo_fm | univariate | realtime | revised_12m | 943 | 103 | -0.997 | 0.442 | -2.257 | -0.053 |
| CA | consumption | dfm | multivariate | realtime | first_release | 886 | 100 | 1.672 | 0.767 | 2.179 | -0.177 |
| CA | consumption | dfm | multivariate | realtime | revised_12m | 886 | 100 | 1.756 | 0.846 | 2.076 | -0.150 |
| CA | consumption | moirai2 | univariate | realtime | first_release | 943 | 103 | -1.198 | 0.533 | -2.247 | -0.089 |
| CA | consumption | moirai2 | univariate | realtime | revised_12m | 943 | 103 | -1.195 | 0.532 | -2.246 | -0.065 |
| CA | consumption | moirai2 | univariate_levels | realtime | first_release | 163 | 103 | -0.189 | 0.153 | -1.235 | -0.688 |
| CA | consumption | moirai2 | univariate_levels | realtime | revised_12m | 163 | 103 | -0.181 | 0.161 | -1.127 | -0.669 |
| CA | consumption | naive | univariate | realtime | first_release | 943 | 103 | -0.908 | 1.542 | -0.589 | -0.180 |
| CA | consumption | naive | univariate | realtime | revised_12m | 943 | 103 | -0.866 | 1.527 | -0.567 | -0.156 |
| CA | consumption | timesfm25 | univariate | realtime | first_release | 943 | 103 | -1.128 | 0.554 | -2.035 | -0.098 |
| CA | consumption | timesfm25 | univariate | realtime | revised_12m | 943 | 103 | -1.130 | 0.552 | -2.047 | -0.074 |
| CA | consumption | timesfm25 | univariate_levels | realtime | first_release | 163 | 103 | -0.187 | 0.584 | -0.321 | -0.179 |
| CA | consumption | timesfm25 | univariate_levels | realtime | revised_12m | 163 | 103 | -0.146 | 0.581 | -0.252 | -0.160 |
| CA | consumption | tirex | univariate | realtime | first_release | 943 | 103 | -1.572 | 0.691 | -2.274 | -0.134 |
| CA | consumption | tirex | univariate | realtime | revised_12m | 943 | 103 | -1.563 | 0.693 | -2.255 | -0.110 |
| CA | consumption | tirex | univariate_levels | realtime | first_release | 163 | 103 | 0.418 | 0.333 | 1.256 | 0.208 |
| CA | consumption | tirex | univariate_levels | realtime | revised_12m | 163 | 103 | 0.393 | 0.336 | 1.170 | 0.227 |
| CA | consumption | tirex2 | multivariate | realtime | first_release | 729 | 103 | -1.849 | 0.972 | -1.902 | -0.115 |
| CA | consumption | tirex2 | multivariate | realtime | revised_12m | 729 | 103 | -1.852 | 0.963 | -1.922 | -0.085 |
| CA | consumption | tirex2 | multivariate_levels | realtime | first_release | 108 | 102 | 0.585 | 0.681 | 0.858 | 0.032 |
| CA | consumption | tirex2 | multivariate_levels | realtime | revised_12m | 108 | 102 | -1.135 | 0.767 | -1.479 | 0.059 |
| CA | consumption | tirex2 | univariate | realtime | first_release | 943 | 103 | -2.092 | 1.813 | -1.154 | -0.091 |
| CA | consumption | tirex2 | univariate | realtime | revised_12m | 943 | 103 | -2.221 | 1.791 | -1.240 | -0.068 |
| CA | consumption | tirex2 | univariate_levels | realtime | first_release | 163 | 103 | 13.523 | 23.709 | 0.570 | 0.024 |
| CA | consumption | tirex2 | univariate_levels | realtime | revised_12m | 163 | 103 | 21.885 | 21.396 | 1.023 | 0.044 |
| CA | cpi | ar | univariate | realtime | first_release | 2795 | 259 | -0.590 | 0.058 | -10.199 | 0.020 |
| CA | cpi | ar | univariate | realtime | revised_12m | 2795 | 259 | -0.590 | 0.058 | -10.199 | 0.020 |
| CA | cpi | bvar | multivariate | realtime | first_release | 2783 | 259 | -0.193 | 0.099 | -1.955 | 0.018 |
| CA | cpi | bvar | multivariate | realtime | revised_12m | 2783 | 259 | -0.193 | 0.099 | -1.955 | 0.018 |
| CA | cpi | chronos2 | multivariate | realtime | first_release | 2795 | 259 | -0.374 | 0.079 | -4.742 | -0.001 |
| CA | cpi | chronos2 | multivariate | realtime | revised_12m | 2795 | 259 | -0.374 | 0.079 | -4.742 | -0.001 |
| CA | cpi | chronos2 | multivariate_levels | realtime | first_release | 21 | 21 | 2.617 | 1.247 | 2.099 | -0.052 |
| CA | cpi | chronos2 | multivariate_levels | realtime | revised_12m | 21 | 21 | 2.617 | 1.247 | 2.099 | -0.052 |
| CA | cpi | chronos2 | univariate | realtime | first_release | 2795 | 259 | -0.371 | 0.132 | -2.806 | 0.001 |
| CA | cpi | chronos2 | univariate | realtime | revised_12m | 2795 | 259 | -0.371 | 0.132 | -2.806 | 0.001 |
| CA | cpi | chronos2 | univariate_levels | realtime | first_release | 21 | 21 |  |  |  | -0.117 |
| CA | cpi | chronos2 | univariate_levels | realtime | revised_12m | 21 | 21 |  |  |  | -0.117 |
| CA | cpi | combo_bench | multivariate | realtime | first_release | 2571 | 252 | -0.176 | 0.166 | -1.056 | 0.019 |
| CA | cpi | combo_bench | multivariate | realtime | revised_12m | 2571 | 252 | -0.176 | 0.166 | -1.056 | 0.019 |
| CA | cpi | combo_fm | univariate | realtime | first_release | 2795 | 259 | -0.310 | 0.165 | -1.882 | 0.002 |
| CA | cpi | combo_fm | univariate | realtime | revised_12m | 2795 | 259 | -0.310 | 0.165 | -1.882 | 0.002 |
| CA | cpi | dfm | multivariate | realtime | first_release | 2583 | 252 | 0.159 | 0.354 | 0.449 | 0.020 |
| CA | cpi | dfm | multivariate | realtime | revised_12m | 2583 | 252 | 0.159 | 0.354 | 0.449 | 0.020 |
| CA | cpi | moirai2 | univariate | realtime | first_release | 2795 | 259 | -0.416 | 0.093 | -4.476 | 0.007 |
| CA | cpi | moirai2 | univariate | realtime | revised_12m | 2795 | 259 | -0.416 | 0.093 | -4.476 | 0.007 |
| CA | cpi | moirai2 | univariate_levels | realtime | first_release | 21 | 21 |  |  |  | -0.323 |
| CA | cpi | moirai2 | univariate_levels | realtime | revised_12m | 21 | 21 |  |  |  | -0.323 |
| CA | cpi | naive | univariate | realtime | first_release | 2795 | 259 | -3.368 | 5.229 | -0.644 | 0.020 |
| CA | cpi | naive | univariate | realtime | revised_12m | 2795 | 259 | -3.368 | 5.229 | -0.644 | 0.020 |
| CA | cpi | timesfm25 | univariate | realtime | first_release | 2795 | 259 | -0.354 | 0.191 | -1.857 | 0.009 |
| CA | cpi | timesfm25 | univariate | realtime | revised_12m | 2795 | 259 | -0.354 | 0.191 | -1.857 | 0.009 |
| CA | cpi | timesfm25 | univariate_levels | realtime | first_release | 21 | 21 |  |  |  | 0.153 |
| CA | cpi | timesfm25 | univariate_levels | realtime | revised_12m | 21 | 21 |  |  |  | 0.153 |
| CA | cpi | tirex | univariate | realtime | first_release | 2795 | 259 | -0.480 | 0.054 | -8.932 | -0.009 |
| CA | cpi | tirex | univariate | realtime | revised_12m | 2795 | 259 | -0.480 | 0.054 | -8.932 | -0.009 |
| CA | cpi | tirex | univariate_levels | realtime | first_release | 21 | 21 |  |  |  | 0.111 |
| CA | cpi | tirex | univariate_levels | realtime | revised_12m | 21 | 21 |  |  |  | 0.111 |
| CA | cpi | tirex2 | multivariate | realtime | first_release | 2795 | 259 | -0.336 | 0.105 | -3.202 | -0.002 |
| CA | cpi | tirex2 | multivariate | realtime | revised_12m | 2795 | 259 | -0.336 | 0.105 | -3.202 | -0.002 |
| CA | cpi | tirex2 | multivariate_levels | realtime | first_release | 21 | 21 | -17.485 | 4.861 | -3.597 | 0.097 |
| CA | cpi | tirex2 | multivariate_levels | realtime | revised_12m | 21 | 21 | -17.485 | 4.861 | -3.597 | 0.097 |
| CA | cpi | tirex2 | univariate | realtime | first_release | 2795 | 259 | -0.329 | 0.130 | -2.531 | -0.007 |
| CA | cpi | tirex2 | univariate | realtime | revised_12m | 2795 | 259 | -0.329 | 0.130 | -2.531 | -0.007 |
| CA | cpi | tirex2 | univariate_levels | realtime | first_release | 21 | 21 |  |  |  | 0.058 |
| CA | cpi | tirex2 | univariate_levels | realtime | revised_12m | 21 | 21 |  |  |  | 0.058 |
| CA | cpi_core | ar | univariate | realtime | first_release | 3345 | 310 | -0.554 | 0.124 | -4.479 | -0.006 |
| CA | cpi_core | ar | univariate | realtime | revised_12m | 3345 | 310 | -0.554 | 0.124 | -4.479 | -0.006 |
| CA | cpi_core | bvar | multivariate | realtime | first_release | 3333 | 310 | -0.430 | 0.151 | -2.855 | 0.004 |
| CA | cpi_core | bvar | multivariate | realtime | revised_12m | 3333 | 310 | -0.430 | 0.151 | -2.855 | 0.004 |
| CA | cpi_core | chronos2 | multivariate | realtime | first_release | 3345 | 310 | -0.421 | 0.057 | -7.357 | 0.001 |
| CA | cpi_core | chronos2 | multivariate | realtime | revised_12m | 3345 | 310 | -0.421 | 0.057 | -7.357 | 0.001 |
| CA | cpi_core | chronos2 | multivariate_levels | realtime | first_release | 26 | 26 | 4.469 | 0.950 | 4.706 | -0.331 |
| CA | cpi_core | chronos2 | multivariate_levels | realtime | revised_12m | 26 | 26 | 4.469 | 0.950 | 4.706 | -0.331 |
| CA | cpi_core | chronos2 | univariate | realtime | first_release | 3345 | 310 | -0.559 | 0.103 | -5.407 | -0.009 |
| CA | cpi_core | chronos2 | univariate | realtime | revised_12m | 3345 | 310 | -0.559 | 0.103 | -5.407 | -0.009 |
| CA | cpi_core | chronos2 | univariate_levels | realtime | first_release | 26 | 26 |  |  |  | -0.352 |
| CA | cpi_core | chronos2 | univariate_levels | realtime | revised_12m | 26 | 26 |  |  |  | -0.352 |
| CA | cpi_core | combo_bench | multivariate | realtime | first_release | 3088 | 299 | -0.401 | 0.287 | -1.396 | -0.006 |
| CA | cpi_core | combo_bench | multivariate | realtime | revised_12m | 3088 | 299 | -0.401 | 0.287 | -1.396 | -0.006 |
| CA | cpi_core | combo_fm | univariate | realtime | first_release | 3345 | 310 | -0.428 | 0.129 | -3.310 | -0.006 |
| CA | cpi_core | combo_fm | univariate | realtime | revised_12m | 3345 | 310 | -0.428 | 0.129 | -3.310 | -0.006 |
| CA | cpi_core | dfm | multivariate | realtime | first_release | 3100 | 299 | -0.844 | 0.411 | -2.052 | -0.022 |
| CA | cpi_core | dfm | multivariate | realtime | revised_12m | 3100 | 299 | -0.844 | 0.411 | -2.052 | -0.022 |
| CA | cpi_core | moirai2 | univariate | realtime | first_release | 3345 | 310 | -0.477 | 0.054 | -8.864 | -0.009 |
| CA | cpi_core | moirai2 | univariate | realtime | revised_12m | 3345 | 310 | -0.477 | 0.054 | -8.864 | -0.009 |
| CA | cpi_core | moirai2 | univariate_levels | realtime | first_release | 26 | 26 |  |  |  | -0.621 |
| CA | cpi_core | moirai2 | univariate_levels | realtime | revised_12m | 26 | 26 |  |  |  | -0.621 |
| CA | cpi_core | naive | univariate | realtime | first_release | 3345 | 310 | -0.938 | 6.232 | -0.150 | -0.029 |
| CA | cpi_core | naive | univariate | realtime | revised_12m | 3345 | 310 | -0.938 | 6.232 | -0.150 | -0.029 |
| CA | cpi_core | timesfm25 | univariate | realtime | first_release | 3345 | 310 | -0.366 | 0.085 | -4.318 | -0.004 |
| CA | cpi_core | timesfm25 | univariate | realtime | revised_12m | 3345 | 310 | -0.366 | 0.085 | -4.318 | -0.004 |
| CA | cpi_core | timesfm25 | univariate_levels | realtime | first_release | 26 | 26 |  |  |  | -0.220 |
| CA | cpi_core | timesfm25 | univariate_levels | realtime | revised_12m | 26 | 26 |  |  |  | -0.220 |
| CA | cpi_core | tirex | univariate | realtime | first_release | 3345 | 310 | -0.499 | 0.050 | -9.910 | -0.003 |
| CA | cpi_core | tirex | univariate | realtime | revised_12m | 3345 | 310 | -0.499 | 0.050 | -9.910 | -0.003 |
| CA | cpi_core | tirex | univariate_levels | realtime | first_release | 26 | 26 |  |  |  | -0.047 |
| CA | cpi_core | tirex | univariate_levels | realtime | revised_12m | 26 | 26 |  |  |  | -0.047 |
| CA | cpi_core | tirex2 | multivariate | realtime | first_release | 3345 | 310 | -0.397 | 0.065 | -6.138 | -0.008 |
| CA | cpi_core | tirex2 | multivariate | realtime | revised_12m | 3345 | 310 | -0.397 | 0.065 | -6.138 | -0.008 |
| CA | cpi_core | tirex2 | multivariate_levels | realtime | first_release | 26 | 26 | 26.878 | 10.650 | 2.524 | -0.012 |
| CA | cpi_core | tirex2 | multivariate_levels | realtime | revised_12m | 26 | 26 | 26.878 | 10.650 | 2.524 | -0.012 |
| CA | cpi_core | tirex2 | univariate | realtime | first_release | 3345 | 310 | -0.444 | 0.069 | -6.475 | -0.008 |
| CA | cpi_core | tirex2 | univariate | realtime | revised_12m | 3345 | 310 | -0.444 | 0.069 | -6.475 | -0.008 |
| CA | cpi_core | tirex2 | univariate_levels | realtime | first_release | 26 | 26 |  |  |  | -0.037 |
| CA | cpi_core | tirex2 | univariate_levels | realtime | revised_12m | 26 | 26 |  |  |  | -0.037 |
| CA | gdp | ar | univariate | realtime | first_release | 943 | 103 | -1.162 | 0.548 | -2.121 | -0.259 |
| CA | gdp | ar | univariate | realtime | revised_12m | 943 | 103 | -1.183 | 0.541 | -2.188 | -0.243 |
| CA | gdp | bvar | multivariate | realtime | first_release | 943 | 103 | -0.622 | 0.171 | -3.634 | -0.061 |
| CA | gdp | bvar | multivariate | realtime | revised_12m | 943 | 103 | -0.622 | 0.168 | -3.700 | -0.045 |
| CA | gdp | chronos2 | multivariate | realtime | first_release | 729 | 103 | -1.006 | 0.463 | -2.172 | -0.118 |
| CA | gdp | chronos2 | multivariate | realtime | revised_12m | 729 | 103 | -1.022 | 0.460 | -2.222 | -0.106 |
| CA | gdp | chronos2 | multivariate_levels | realtime | first_release | 108 | 102 | 1.392 | 3.037 | 0.458 | -0.481 |
| CA | gdp | chronos2 | multivariate_levels | realtime | revised_12m | 108 | 102 | 0.283 | 3.856 | 0.073 | -0.469 |
| CA | gdp | chronos2 | univariate | realtime | first_release | 943 | 103 | -0.631 | 0.256 | -2.468 | -0.026 |
| CA | gdp | chronos2 | univariate | realtime | revised_12m | 943 | 103 | -0.639 | 0.252 | -2.530 | -0.009 |
| CA | gdp | chronos2 | univariate_levels | realtime | first_release | 163 | 103 | -0.848 | 0.432 | -1.964 | -0.501 |
| CA | gdp | chronos2 | univariate_levels | realtime | revised_12m | 163 | 103 | -1.074 | 0.445 | -2.415 | -0.483 |
| CA | gdp | combo_bench | multivariate | realtime | first_release | 886 | 100 | -0.548 | 0.291 | -1.884 | -0.214 |
| CA | gdp | combo_bench | multivariate | realtime | revised_12m | 886 | 100 | -0.558 | 0.286 | -1.951 | -0.197 |
| CA | gdp | combo_fm | univariate | realtime | first_release | 943 | 103 | -0.798 | 0.367 | -2.171 | -0.116 |
| CA | gdp | combo_fm | univariate | realtime | revised_12m | 943 | 103 | -0.813 | 0.364 | -2.236 | -0.100 |
| CA | gdp | dfm | multivariate | realtime | first_release | 886 | 100 | 0.894 | 0.431 | 2.075 | -0.295 |
| CA | gdp | dfm | multivariate | realtime | revised_12m | 886 | 100 | 0.863 | 0.417 | 2.070 | -0.278 |
| CA | gdp | moirai2 | univariate | realtime | first_release | 943 | 103 | -0.950 | 0.487 | -1.953 | -0.105 |
| CA | gdp | moirai2 | univariate | realtime | revised_12m | 943 | 103 | -0.972 | 0.483 | -2.015 | -0.089 |
| CA | gdp | moirai2 | univariate_levels | realtime | first_release | 163 | 103 | 0.336 | 0.132 | 2.550 | -0.786 |
| CA | gdp | moirai2 | univariate_levels | realtime | revised_12m | 163 | 103 | 0.258 | 0.132 | 1.945 | -0.768 |
| CA | gdp | naive | univariate | realtime | first_release | 943 | 103 | -0.276 | 0.624 | -0.442 | -0.334 |
| CA | gdp | naive | univariate | realtime | revised_12m | 943 | 103 | -0.603 | 0.617 | -0.977 | -0.318 |
| CA | gdp | timesfm25 | univariate | realtime | first_release | 943 | 103 | -0.797 | 0.387 | -2.057 | -0.163 |
| CA | gdp | timesfm25 | univariate | realtime | revised_12m | 943 | 103 | -0.817 | 0.386 | -2.118 | -0.147 |
| CA | gdp | timesfm25 | univariate_levels | realtime | first_release | 163 | 103 | -0.108 | 0.444 | -0.242 | -0.240 |
| CA | gdp | timesfm25 | univariate_levels | realtime | revised_12m | 163 | 103 | -0.980 | 0.618 | -1.586 | -0.221 |
| CA | gdp | tirex | univariate | realtime | first_release | 943 | 103 | -1.088 | 0.563 | -1.934 | -0.176 |
| CA | gdp | tirex | univariate | realtime | revised_12m | 943 | 103 | -1.116 | 0.557 | -2.003 | -0.160 |
| CA | gdp | tirex | univariate_levels | realtime | first_release | 163 | 103 | -1.729 | 1.251 | -1.382 | 0.029 |
| CA | gdp | tirex | univariate_levels | realtime | revised_12m | 163 | 103 | -3.519 | 3.079 | -1.143 | 0.046 |
| CA | gdp | tirex2 | multivariate | realtime | first_release | 729 | 103 | -1.290 | 0.645 | -2.000 | -0.165 |
| CA | gdp | tirex2 | multivariate | realtime | revised_12m | 729 | 103 | -1.318 | 0.639 | -2.064 | -0.153 |
| CA | gdp | tirex2 | multivariate_levels | realtime | first_release | 108 | 102 | -1.179 | 1.646 | -0.716 | -0.005 |
| CA | gdp | tirex2 | multivariate_levels | realtime | revised_12m | 108 | 102 | -3.117 | 1.395 | -2.235 | 0.008 |
| CA | gdp | tirex2 | univariate | realtime | first_release | 943 | 103 | -1.092 | 0.968 | -1.129 | -0.145 |
| CA | gdp | tirex2 | univariate | realtime | revised_12m | 943 | 103 | -1.147 | 0.958 | -1.197 | -0.129 |
| CA | gdp | tirex2 | univariate_levels | realtime | first_release | 163 | 103 | -0.955 | 1.089 | -0.877 | -0.031 |
| CA | gdp | tirex2 | univariate_levels | realtime | revised_12m | 163 | 103 | -3.599 | 0.884 | -4.072 | -0.012 |
| CA | retail | ar | univariate | realtime | first_release | 3284 | 307 | -0.803 | 0.253 | -3.168 | -0.057 |
| CA | retail | ar | univariate | realtime | revised_12m | 3321 | 310 | -0.797 | 0.257 | -3.102 | 0.005 |
| CA | retail | bvar | multivariate | realtime | first_release | 3272 | 307 | 0.121 | 0.234 | 0.514 | -0.063 |
| CA | retail | bvar | multivariate | realtime | revised_12m | 3309 | 310 | 0.131 | 0.238 | 0.548 | -0.002 |
| CA | retail | chronos2 | multivariate | realtime | first_release | 3284 | 307 | -0.557 | 0.089 | -6.285 | -0.009 |
| CA | retail | chronos2 | multivariate | realtime | revised_12m | 3321 | 310 | -0.567 | 0.097 | -5.863 | 0.053 |
| CA | retail | chronos2 | univariate | realtime | first_release | 3284 | 307 | -0.534 | 0.065 | -8.180 | 0.027 |
| CA | retail | chronos2 | univariate | realtime | revised_12m | 3321 | 310 | -0.540 | 0.071 | -7.646 | 0.088 |
| CA | retail | combo_bench | multivariate | realtime | first_release | 3030 | 298 | 0.815 | 0.559 | 1.457 | -0.073 |
| CA | retail | combo_bench | multivariate | realtime | revised_12m | 3064 | 301 | 0.825 | 0.556 | 1.483 | -0.013 |
| CA | retail | combo_fm | univariate | realtime | first_release | 3284 | 307 | -0.662 | 0.180 | -3.685 | -0.049 |
| CA | retail | combo_fm | univariate | realtime | revised_12m | 3321 | 310 | -0.692 | 0.202 | -3.424 | 0.013 |
| CA | retail | dfm | multivariate | realtime | first_release | 3042 | 298 | 1.050 | 0.766 | 1.372 | -0.078 |
| CA | retail | dfm | multivariate | realtime | revised_12m | 3076 | 301 | 1.077 | 0.755 | 1.426 | -0.016 |
| CA | retail | moirai2 | univariate | realtime | first_release | 3284 | 307 | -0.848 | 0.359 | -2.363 | -0.061 |
| CA | retail | moirai2 | univariate | realtime | revised_12m | 3321 | 310 | -0.920 | 0.403 | -2.285 | 0.001 |
| CA | retail | naive | univariate | realtime | first_release | 3284 | 307 | -25.790 | 17.490 | -1.475 | -0.066 |
| CA | retail | naive | univariate | realtime | revised_12m | 3321 | 310 | -27.544 | 19.337 | -1.424 | -0.004 |
| CA | retail | timesfm25 | univariate | realtime | first_release | 3284 | 307 | -0.940 | 0.397 | -2.367 | -0.081 |
| CA | retail | timesfm25 | univariate | realtime | revised_12m | 3321 | 310 | -1.045 | 0.459 | -2.276 | -0.019 |
| CA | retail | tirex | univariate | realtime | first_release | 3284 | 307 | -0.950 | 0.416 | -2.281 | -0.080 |
| CA | retail | tirex | univariate | realtime | revised_12m | 3321 | 310 | -1.068 | 0.477 | -2.238 | -0.017 |
| CA | retail | tirex2 | multivariate | realtime | first_release | 3284 | 307 | -2.392 | 1.029 | -2.326 | -0.082 |
| CA | retail | tirex2 | multivariate | realtime | revised_12m | 3321 | 310 | -2.715 | 1.211 | -2.243 | -0.019 |
| CA | retail | tirex2 | univariate | realtime | first_release | 3284 | 307 | -1.658 | 0.589 | -2.815 | -0.071 |
| CA | retail | tirex2 | univariate | realtime | revised_12m | 3321 | 310 | -1.840 | 0.681 | -2.703 | -0.009 |
| CA | unemp | ar | univariate | realtime | first_release | 3360 | 311 | -0.554 | 0.114 | -4.883 | -0.001 |
| CA | unemp | ar | univariate | realtime | revised_12m | 3360 | 311 | -0.588 | 0.110 | -5.330 | -0.002 |
| CA | unemp | bvar | multivariate | realtime | first_release | 3348 | 311 | -0.518 | 0.122 | -4.250 | 0.006 |
| CA | unemp | bvar | multivariate | realtime | revised_12m | 3348 | 311 | -0.535 | 0.118 | -4.522 | 0.006 |
| CA | unemp | chronos2 | multivariate | realtime | first_release | 3360 | 311 | -0.556 | 0.081 | -6.828 | 0.002 |
| CA | unemp | chronos2 | multivariate | realtime | revised_12m | 3360 | 311 | -0.557 | 0.082 | -6.772 | 0.001 |
| CA | unemp | chronos2 | multivariate_levels | realtime | first_release | 49 | 49 | -1.727 | 0.328 | -5.262 | -0.042 |
| CA | unemp | chronos2 | multivariate_levels | realtime | revised_12m | 49 | 49 | -0.893 | 0.349 | -2.561 | -0.040 |
| CA | unemp | chronos2 | univariate | realtime | first_release | 3360 | 311 | -0.602 | 0.106 | -5.684 | 0.008 |
| CA | unemp | chronos2 | univariate | realtime | revised_12m | 3360 | 311 | -0.609 | 0.107 | -5.715 | 0.008 |
| CA | unemp | chronos2 | univariate_levels | realtime | first_release | 49 | 49 | -0.355 | 1.236 | -0.287 | -0.080 |
| CA | unemp | chronos2 | univariate_levels | realtime | revised_12m | 49 | 49 | 3.023 | 1.807 | 1.673 | -0.076 |
| CA | unemp | combo_bench | multivariate | realtime | first_release | 3103 | 303 | -0.503 | 0.139 | -3.608 | 0.004 |
| CA | unemp | combo_bench | multivariate | realtime | revised_12m | 3103 | 303 | -0.541 | 0.139 | -3.887 | 0.004 |
| CA | unemp | combo_fm | univariate | realtime | first_release | 3360 | 311 | -0.578 | 0.094 | -6.149 | 0.021 |
| CA | unemp | combo_fm | univariate | realtime | revised_12m | 3360 | 311 | -0.587 | 0.093 | -6.308 | 0.021 |
| CA | unemp | dfm | multivariate | realtime | first_release | 3115 | 303 | -0.594 | 0.171 | -3.484 | -0.003 |
| CA | unemp | dfm | multivariate | realtime | revised_12m | 3115 | 303 | -0.618 | 0.171 | -3.603 | -0.003 |
| CA | unemp | moirai2 | univariate | realtime | first_release | 3360 | 311 | -0.485 | 0.058 | -8.422 | 0.028 |
| CA | unemp | moirai2 | univariate | realtime | revised_12m | 3360 | 311 | -0.486 | 0.054 | -8.958 | 0.027 |
| CA | unemp | moirai2 | univariate_levels | realtime | first_release | 49 | 49 | -0.028 | 2.964 | -0.009 | -0.045 |
| CA | unemp | moirai2 | univariate_levels | realtime | revised_12m | 49 | 49 | -6.348 | 3.016 | -2.104 | -0.042 |
| CA | unemp | naive | univariate | realtime | first_release | 3360 | 311 | -17.991 | 15.153 | -1.187 | -0.003 |
| CA | unemp | naive | univariate | realtime | revised_12m | 3360 | 311 | -17.929 | 14.713 | -1.219 | -0.003 |
| CA | unemp | timesfm25 | univariate | realtime | first_release | 3360 | 311 | -0.559 | 0.087 | -6.402 | 0.030 |
| CA | unemp | timesfm25 | univariate | realtime | revised_12m | 3360 | 311 | -0.566 | 0.085 | -6.663 | 0.030 |
| CA | unemp | timesfm25 | univariate_levels | realtime | first_release | 49 | 49 | -6.488 | 6.179 | -1.050 | -0.090 |
| CA | unemp | timesfm25 | univariate_levels | realtime | revised_12m | 49 | 49 | -8.162 | 7.531 | -1.084 | -0.084 |
| CA | unemp | tirex | univariate | realtime | first_release | 3360 | 311 | -0.618 | 0.098 | -6.317 | 0.020 |
| CA | unemp | tirex | univariate | realtime | revised_12m | 3360 | 311 | -0.631 | 0.098 | -6.432 | 0.020 |
| CA | unemp | tirex | univariate_levels | realtime | first_release | 49 | 49 | -3.079 | 2.015 | -1.528 | -0.067 |
| CA | unemp | tirex | univariate_levels | realtime | revised_12m | 49 | 49 | 0.051 | 1.925 | 0.027 | -0.063 |
| CA | unemp | tirex2 | multivariate | realtime | first_release | 3360 | 311 | -0.638 | 0.123 | -5.196 | 0.013 |
| CA | unemp | tirex2 | multivariate | realtime | revised_12m | 3360 | 311 | -0.650 | 0.125 | -5.204 | 0.012 |
| CA | unemp | tirex2 | multivariate_levels | realtime | first_release | 49 | 49 | -6.390 | 3.306 | -1.933 | -0.043 |
| CA | unemp | tirex2 | multivariate_levels | realtime | revised_12m | 49 | 49 | -2.111 | 3.153 | -0.670 | -0.042 |
| CA | unemp | tirex2 | univariate | realtime | first_release | 3360 | 311 | -0.642 | 0.110 | -5.833 | 0.012 |
| CA | unemp | tirex2 | univariate | realtime | revised_12m | 3360 | 311 | -0.662 | 0.108 | -6.115 | 0.012 |
| CA | unemp | tirex2 | univariate_levels | realtime | first_release | 49 | 49 | -3.430 | 2.803 | -1.224 | -0.079 |
| CA | unemp | tirex2 | univariate_levels | realtime | revised_12m | 49 | 49 | 6.081 | 3.581 | 1.698 | -0.074 |
| EA | consumption | ar | univariate | realtime | first_release | 1064 | 100 | -0.712 | 0.210 | -3.393 | -0.014 |
| EA | consumption | ar | univariate | realtime | revised_12m | 1062 | 100 | -0.657 | 0.163 | -4.023 | 0.180 |
| EA | consumption | bvar | multivariate | realtime | first_release | 1055 | 100 | -0.432 | 0.262 | -1.649 | -0.199 |
| EA | consumption | bvar | multivariate | realtime | revised_12m | 1050 | 100 | -0.517 | 0.243 | -2.128 | -0.018 |
| EA | consumption | chronos2 | multivariate | realtime | first_release | 1064 | 100 | -0.859 | 0.378 | -2.270 | -0.081 |
| EA | consumption | chronos2 | multivariate | realtime | revised_12m | 1062 | 100 | -0.732 | 0.356 | -2.059 | 0.154 |
| EA | consumption | chronos2 | multivariate_levels | realtime | first_release | 195 | 98 | -0.782 | 1.059 | -0.738 | -0.196 |
| EA | consumption | chronos2 | multivariate_levels | realtime | revised_12m | 196 | 98 | -1.599 | 1.067 | -1.499 | -0.059 |
| EA | consumption | chronos2 | univariate | realtime | first_release | 1064 | 100 | -0.753 | 0.293 | -2.565 | 0.024 |
| EA | consumption | chronos2 | univariate | realtime | revised_12m | 1062 | 100 | -0.632 | 0.273 | -2.316 | 0.270 |
| EA | consumption | chronos2 | univariate_levels | realtime | first_release | 195 | 98 | -1.483 | 1.086 | -1.366 | -0.171 |
| EA | consumption | chronos2 | univariate_levels | realtime | revised_12m | 196 | 98 | -1.505 | 1.155 | -1.303 | -0.045 |
| EA | consumption | combo_bench | multivariate | realtime | first_release | 1055 | 100 | -0.584 | 0.186 | -3.135 | -0.197 |
| EA | consumption | combo_bench | multivariate | realtime | revised_12m | 1050 | 100 | -0.595 | 0.137 | -4.331 | -0.016 |
| EA | consumption | combo_fm | univariate | realtime | first_release | 1064 | 100 | -0.836 | 0.309 | -2.701 | -0.073 |
| EA | consumption | combo_fm | univariate | realtime | revised_12m | 1062 | 100 | -0.757 | 0.281 | -2.695 | 0.158 |
| EA | consumption | dfm | multivariate | realtime | first_release | 1064 | 100 | -1.077 | 0.486 | -2.213 | -0.222 |
| EA | consumption | dfm | multivariate | realtime | revised_12m | 1062 | 100 | -1.162 | 0.400 | -2.906 | -0.019 |
| EA | consumption | moirai2 | univariate | realtime | first_release | 1064 | 100 | -0.921 | 0.379 | -2.429 | -0.099 |
| EA | consumption | moirai2 | univariate | realtime | revised_12m | 1062 | 100 | -0.848 | 0.359 | -2.364 | 0.127 |
| EA | consumption | moirai2 | univariate_levels | realtime | first_release | 195 | 98 | -1.334 | 1.318 | -1.012 | 0.141 |
| EA | consumption | moirai2 | univariate_levels | realtime | revised_12m | 196 | 98 | -1.700 | 1.382 | -1.229 | 0.280 |
| EA | consumption | naive | univariate | realtime | first_release | 1064 | 100 | -11.571 | 15.743 | -0.735 | -0.267 |
| EA | consumption | naive | univariate | realtime | revised_12m | 1062 | 100 | -11.934 | 14.278 | -0.836 | -0.057 |
| EA | consumption | timesfm25 | univariate | realtime | first_release | 1064 | 100 | -0.814 | 0.253 | -3.223 | -0.162 |
| EA | consumption | timesfm25 | univariate | realtime | revised_12m | 1062 | 100 | -0.780 | 0.196 | -3.982 | 0.053 |
| EA | consumption | timesfm25 | univariate_levels | realtime | first_release | 195 | 98 | 0.231 | 1.204 | 0.192 | -0.010 |
| EA | consumption | timesfm25 | univariate_levels | realtime | revised_12m | 196 | 98 | 0.446 | 1.326 | 0.336 | 0.124 |
| EA | consumption | tirex | univariate | realtime | first_release | 1064 | 100 | -0.806 | 0.264 | -3.048 | -0.053 |
| EA | consumption | tirex | univariate | realtime | revised_12m | 1062 | 100 | -0.738 | 0.248 | -2.980 | 0.183 |
| EA | consumption | tirex | univariate_levels | realtime | first_release | 195 | 98 | -0.186 | 2.208 | -0.084 | -0.026 |
| EA | consumption | tirex | univariate_levels | realtime | revised_12m | 196 | 98 | 0.569 | 2.108 | 0.270 | 0.125 |
| EA | consumption | tirex2 | multivariate | realtime | first_release | 1064 | 100 | -1.365 | 0.594 | -2.299 | -0.131 |
| EA | consumption | tirex2 | multivariate | realtime | revised_12m | 1062 | 100 | -1.378 | 0.593 | -2.322 | 0.090 |
| EA | consumption | tirex2 | multivariate_levels | realtime | first_release | 195 | 98 | -9.302 | 3.322 | -2.800 | -0.046 |
| EA | consumption | tirex2 | multivariate_levels | realtime | revised_12m | 196 | 98 | -9.896 | 3.454 | -2.865 | 0.098 |
| EA | consumption | tirex2 | univariate | realtime | first_release | 1064 | 100 | -1.383 | 0.581 | -2.381 | -0.122 |
| EA | consumption | tirex2 | univariate | realtime | revised_12m | 1062 | 100 | -1.386 | 0.582 | -2.381 | 0.100 |
| EA | consumption | tirex2 | univariate_levels | realtime | first_release | 195 | 98 | -8.415 | 2.747 | -3.063 | -0.027 |
| EA | consumption | tirex2 | univariate_levels | realtime | revised_12m | 196 | 98 | -8.299 | 2.962 | -2.802 | 0.138 |
| EA | gdp | ar | univariate | realtime | first_release | 1062 | 100 | -1.304 | 0.314 | -4.156 | -0.089 |
| EA | gdp | ar | univariate | realtime | revised_12m | 1060 | 100 | -1.295 | 0.302 | -4.295 | 0.087 |
| EA | gdp | bvar | multivariate | realtime | first_release | 1062 | 100 | -0.260 | 0.267 | -0.974 | -0.152 |
| EA | gdp | bvar | multivariate | realtime | revised_12m | 1060 | 100 | -0.389 | 0.211 | -1.840 | -0.017 |
| EA | gdp | chronos2 | multivariate | realtime | first_release | 1058 | 100 | -0.995 | 0.502 | -1.984 | -0.117 |
| EA | gdp | chronos2 | multivariate | realtime | revised_12m | 1056 | 100 | -1.064 | 0.470 | -2.264 | 0.059 |
| EA | gdp | chronos2 | multivariate_levels | realtime | first_release | 194 | 98 | -2.970 | 2.249 | -1.320 | -0.105 |
| EA | gdp | chronos2 | multivariate_levels | realtime | revised_12m | 193 | 98 | -0.549 | 0.418 | -1.313 | 0.001 |
| EA | gdp | chronos2 | univariate | realtime | first_release | 1062 | 100 | -0.765 | 0.299 | -2.556 | 0.006 |
| EA | gdp | chronos2 | univariate | realtime | revised_12m | 1060 | 100 | -0.711 | 0.279 | -2.547 | 0.199 |
| EA | gdp | chronos2 | univariate_levels | realtime | first_release | 195 | 98 | -5.114 | 2.974 | -1.719 | -0.163 |
| EA | gdp | chronos2 | univariate_levels | realtime | revised_12m | 194 | 98 | -2.963 | 1.446 | -2.049 | 0.042 |
| EA | gdp | combo_bench | multivariate | realtime | first_release | 1062 | 100 | -0.971 | 0.833 | -1.166 | -0.134 |
| EA | gdp | combo_bench | multivariate | realtime | revised_12m | 1060 | 100 | -1.512 | 0.622 | -2.432 | 0.016 |
| EA | gdp | combo_fm | univariate | realtime | first_release | 1062 | 100 | -0.896 | 0.372 | -2.408 | -0.062 |
| EA | gdp | combo_fm | univariate | realtime | revised_12m | 1060 | 100 | -0.879 | 0.342 | -2.573 | 0.118 |
| EA | gdp | dfm | multivariate | realtime | first_release | 1062 | 100 | -0.334 | 0.453 | -0.739 | -0.165 |
| EA | gdp | dfm | multivariate | realtime | revised_12m | 1060 | 100 | -0.646 | 0.394 | -1.640 | -0.013 |
| EA | gdp | moirai2 | univariate | realtime | first_release | 1062 | 100 | -1.008 | 0.475 | -2.122 | -0.056 |
| EA | gdp | moirai2 | univariate | realtime | revised_12m | 1060 | 100 | -1.014 | 0.448 | -2.261 | 0.124 |
| EA | gdp | moirai2 | univariate_levels | realtime | first_release | 195 | 98 | -0.894 | 0.393 | -2.274 | 0.139 |
| EA | gdp | moirai2 | univariate_levels | realtime | revised_12m | 194 | 98 | -1.206 | 0.628 | -1.922 | 0.354 |
| EA | gdp | naive | univariate | realtime | first_release | 1062 | 100 | -7.025 | 11.304 | -0.621 | -0.224 |
| EA | gdp | naive | univariate | realtime | revised_12m | 1060 | 100 | -8.608 | 9.921 | -0.868 | -0.047 |
| EA | gdp | timesfm25 | univariate | realtime | first_release | 1062 | 100 | -0.757 | 0.256 | -2.961 | -0.153 |
| EA | gdp | timesfm25 | univariate | realtime | revised_12m | 1060 | 100 | -0.740 | 0.191 | -3.880 | 0.019 |
| EA | gdp | timesfm25 | univariate_levels | realtime | first_release | 195 | 98 | -15.459 | 10.422 | -1.483 | -0.083 |
| EA | gdp | timesfm25 | univariate_levels | realtime | revised_12m | 194 | 98 | -10.350 | 9.003 | -1.150 | 0.068 |
| EA | gdp | tirex | univariate | realtime | first_release | 1062 | 100 | -0.979 | 0.378 | -2.592 | -0.045 |
| EA | gdp | tirex | univariate | realtime | revised_12m | 1060 | 100 | -1.001 | 0.363 | -2.755 | 0.133 |
| EA | gdp | tirex | univariate_levels | realtime | first_release | 195 | 98 | -2.355 | 1.288 | -1.829 | -0.029 |
| EA | gdp | tirex | univariate_levels | realtime | revised_12m | 194 | 98 | -2.287 | 1.395 | -1.639 | 0.187 |
| EA | gdp | tirex2 | multivariate | realtime | first_release | 1058 | 100 | -1.260 | 0.841 | -1.498 | -0.143 |
| EA | gdp | tirex2 | multivariate | realtime | revised_12m | 1056 | 100 | -1.454 | 0.768 | -1.894 | 0.032 |
| EA | gdp | tirex2 | multivariate_levels | realtime | first_release | 194 | 98 | 1.122 | 3.196 | 0.351 | -0.057 |
| EA | gdp | tirex2 | multivariate_levels | realtime | revised_12m | 193 | 98 | -1.811 | 1.109 | -1.633 | 0.186 |
| EA | gdp | tirex2 | univariate | realtime | first_release | 1062 | 100 | -1.298 | 0.835 | -1.554 | -0.140 |
| EA | gdp | tirex2 | univariate | realtime | revised_12m | 1060 | 100 | -1.449 | 0.780 | -1.857 | 0.035 |
| EA | gdp | tirex2 | univariate_levels | realtime | first_release | 195 | 98 | 3.748 | 3.618 | 1.036 | -0.120 |
| EA | gdp | tirex2 | univariate_levels | realtime | revised_12m | 194 | 98 | 1.573 | 2.273 | 0.692 | 0.120 |
| EA | hicp | ar | univariate | realtime | first_release | 3339 | 309 | -0.740 | 0.142 | -5.222 | 0.005 |
| EA | hicp | ar | univariate | realtime | revised_12m | 3317 | 307 | -0.739 | 0.141 | -5.227 | 0.005 |
| EA | hicp | bvar | multivariate | realtime | first_release | 3339 | 309 | -0.064 | 0.107 | -0.601 | 0.013 |
| EA | hicp | bvar | multivariate | realtime | revised_12m | 3317 | 307 | -0.066 | 0.108 | -0.614 | 0.013 |
| EA | hicp | chronos2 | multivariate | realtime | first_release | 3339 | 309 | -0.480 | 0.138 | -3.490 | -0.002 |
| EA | hicp | chronos2 | multivariate | realtime | revised_12m | 3317 | 307 | -0.477 | 0.137 | -3.471 | -0.003 |
| EA | hicp | chronos2 | multivariate_levels | realtime | first_release | 52 | 50 | 4.974 | 19.144 | 0.260 | 0.065 |
| EA | hicp | chronos2 | multivariate_levels | realtime | revised_12m | 52 | 50 | 4.870 | 19.142 | 0.254 | 0.067 |
| EA | hicp | chronos2 | univariate | realtime | first_release | 3339 | 309 | -0.380 | 0.160 | -2.369 | 0.016 |
| EA | hicp | chronos2 | univariate | realtime | revised_12m | 3317 | 307 | -0.380 | 0.161 | -2.368 | 0.016 |
| EA | hicp | chronos2 | univariate_levels | realtime | first_release | 52 | 50 |  |  |  | -0.112 |
| EA | hicp | chronos2 | univariate_levels | realtime | revised_12m | 52 | 50 |  |  |  | -0.109 |
| EA | hicp | combo_bench | multivariate | realtime | first_release | 3315 | 309 | -0.194 | 0.176 | -1.101 | 0.005 |
| EA | hicp | combo_bench | multivariate | realtime | revised_12m | 3293 | 307 | -0.193 | 0.177 | -1.089 | 0.006 |
| EA | hicp | combo_fm | univariate | realtime | first_release | 3339 | 309 | -0.366 | 0.245 | -1.494 | 0.012 |
| EA | hicp | combo_fm | univariate | realtime | revised_12m | 3317 | 307 | -0.365 | 0.245 | -1.486 | 0.012 |
| EA | hicp | dfm | multivariate | realtime | first_release | 3315 | 309 | -0.580 | 0.095 | -6.113 | 0.007 |
| EA | hicp | dfm | multivariate | realtime | revised_12m | 3293 | 307 | -0.578 | 0.096 | -6.030 | 0.008 |
| EA | hicp | moirai2 | univariate | realtime | first_release | 3339 | 309 | -0.418 | 0.103 | -4.061 | 0.007 |
| EA | hicp | moirai2 | univariate | realtime | revised_12m | 3317 | 307 | -0.416 | 0.103 | -4.033 | 0.006 |
| EA | hicp | moirai2 | univariate_levels | realtime | first_release | 52 | 50 |  |  |  | -0.489 |
| EA | hicp | moirai2 | univariate_levels | realtime | revised_12m | 52 | 50 |  |  |  | -0.487 |
| EA | hicp | naive | univariate | realtime | first_release | 3339 | 309 | -1.258 | 2.254 | -0.558 | 0.003 |
| EA | hicp | naive | univariate | realtime | revised_12m | 3317 | 307 | -1.432 | 2.295 | -0.624 | 0.004 |
| EA | hicp | timesfm25 | univariate | realtime | first_release | 3339 | 309 | -0.424 | 0.189 | -2.243 | 0.014 |
| EA | hicp | timesfm25 | univariate | realtime | revised_12m | 3317 | 307 | -0.423 | 0.189 | -2.236 | 0.013 |
| EA | hicp | timesfm25 | univariate_levels | realtime | first_release | 52 | 50 |  |  |  | -0.030 |
| EA | hicp | timesfm25 | univariate_levels | realtime | revised_12m | 52 | 50 |  |  |  | -0.028 |
| EA | hicp | tirex | univariate | realtime | first_release | 3339 | 309 | -0.500 | 0.128 | -3.901 | 0.012 |
| EA | hicp | tirex | univariate | realtime | revised_12m | 3317 | 307 | -0.499 | 0.128 | -3.899 | 0.011 |
| EA | hicp | tirex | univariate_levels | realtime | first_release | 52 | 50 |  |  |  | -0.097 |
| EA | hicp | tirex | univariate_levels | realtime | revised_12m | 52 | 50 |  |  |  | -0.095 |
| EA | hicp | tirex2 | multivariate | realtime | first_release | 3339 | 309 | -0.423 | 0.148 | -2.856 | 0.012 |
| EA | hicp | tirex2 | multivariate | realtime | revised_12m | 3317 | 307 | -0.431 | 0.147 | -2.936 | 0.011 |
| EA | hicp | tirex2 | multivariate_levels | realtime | first_release | 52 | 50 | 28.569 | 6.462 | 4.421 | -0.002 |
| EA | hicp | tirex2 | multivariate_levels | realtime | revised_12m | 52 | 50 | 28.676 | 6.450 | 4.446 | 0.000 |
| EA | hicp | tirex2 | univariate | realtime | first_release | 3339 | 309 | -0.406 | 0.154 | -2.642 | 0.018 |
| EA | hicp | tirex2 | univariate | realtime | revised_12m | 3317 | 307 | -0.412 | 0.153 | -2.698 | 0.018 |
| EA | hicp | tirex2 | univariate_levels | realtime | first_release | 52 | 50 |  |  |  | 0.016 |
| EA | hicp | tirex2 | univariate_levels | realtime | revised_12m | 52 | 50 |  |  |  | 0.018 |
| EA | hicp_core | ar | univariate | realtime | first_release | 2157 | 202 | -0.554 | 0.253 | -2.185 | 0.003 |
| EA | hicp_core | ar | univariate | realtime | revised_12m | 2157 | 202 | -0.554 | 0.253 | -2.185 | 0.003 |
| EA | hicp_core | bvar | multivariate | realtime | first_release | 2157 | 202 | -0.323 | 0.079 | -4.074 | 0.030 |
| EA | hicp_core | bvar | multivariate | realtime | revised_12m | 2157 | 202 | -0.323 | 0.079 | -4.074 | 0.030 |
| EA | hicp_core | chronos2 | multivariate | realtime | first_release | 1712 | 202 | -0.271 | 0.083 | -3.251 | 0.007 |
| EA | hicp_core | chronos2 | multivariate | realtime | revised_12m | 1712 | 202 | -0.271 | 0.083 | -3.251 | 0.007 |
| EA | hicp_core | chronos2 | univariate | realtime | first_release | 2157 | 202 | -0.364 | 0.059 | -6.138 | 0.004 |
| EA | hicp_core | chronos2 | univariate | realtime | revised_12m | 2157 | 202 | -0.364 | 0.059 | -6.138 | 0.004 |
| EA | hicp_core | combo_bench | multivariate | realtime | first_release | 2133 | 202 | -0.096 | 0.182 | -0.524 | 0.010 |
| EA | hicp_core | combo_bench | multivariate | realtime | revised_12m | 2133 | 202 | -0.096 | 0.182 | -0.524 | 0.010 |
| EA | hicp_core | combo_fm | univariate | realtime | first_release | 2157 | 202 | -0.185 | 0.100 | -1.852 | 0.007 |
| EA | hicp_core | combo_fm | univariate | realtime | revised_12m | 2157 | 202 | -0.185 | 0.100 | -1.852 | 0.007 |
| EA | hicp_core | dfm | multivariate | realtime | first_release | 2133 | 202 | -0.781 | 0.132 | -5.909 | 0.005 |
| EA | hicp_core | dfm | multivariate | realtime | revised_12m | 2133 | 202 | -0.781 | 0.132 | -5.909 | 0.005 |
| EA | hicp_core | moirai2 | univariate | realtime | first_release | 2157 | 202 | -0.441 | 0.033 | -13.553 | -0.006 |
| EA | hicp_core | moirai2 | univariate | realtime | revised_12m | 2157 | 202 | -0.441 | 0.033 | -13.553 | -0.006 |
| EA | hicp_core | naive | univariate | realtime | first_release | 2157 | 202 | -13.214 | 2.926 | -4.517 | 0.025 |
| EA | hicp_core | naive | univariate | realtime | revised_12m | 2157 | 202 | -13.214 | 2.926 | -4.517 | 0.025 |
| EA | hicp_core | timesfm25 | univariate | realtime | first_release | 2157 | 202 | -0.347 | 0.057 | -6.087 | 0.011 |
| EA | hicp_core | timesfm25 | univariate | realtime | revised_12m | 2157 | 202 | -0.347 | 0.057 | -6.087 | 0.011 |
| EA | hicp_core | tirex | univariate | realtime | first_release | 2157 | 202 | -0.445 | 0.053 | -8.474 | 0.018 |
| EA | hicp_core | tirex | univariate | realtime | revised_12m | 2157 | 202 | -0.445 | 0.053 | -8.474 | 0.018 |
| EA | hicp_core | tirex2 | multivariate | realtime | first_release | 1712 | 202 | -0.416 | 0.054 | -7.667 | 0.013 |
| EA | hicp_core | tirex2 | multivariate | realtime | revised_12m | 1712 | 202 | -0.416 | 0.054 | -7.667 | 0.013 |
| EA | hicp_core | tirex2 | univariate | realtime | first_release | 2157 | 202 | -0.454 | 0.040 | -11.281 | 0.017 |
| EA | hicp_core | tirex2 | univariate | realtime | revised_12m | 2157 | 202 | -0.454 | 0.040 | -11.281 | 0.017 |
| EA | retail | ar | univariate | realtime | first_release | 2784 | 258 | -0.914 | 0.189 | -4.833 | -0.135 |
| EA | retail | ar | univariate | realtime | revised_12m | 2797 | 259 | -0.915 | 0.190 | -4.805 | 0.006 |
| EA | retail | bvar | multivariate | realtime | first_release | 2784 | 258 | -0.249 | 0.223 | -1.115 | -0.148 |
| EA | retail | bvar | multivariate | realtime | revised_12m | 2797 | 259 | -0.236 | 0.238 | -0.990 | -0.009 |
| EA | retail | chronos2 | multivariate | realtime | first_release | 2784 | 258 | -0.544 | 0.080 | -6.828 | -0.060 |
| EA | retail | chronos2 | multivariate | realtime | revised_12m | 2797 | 259 | -0.552 | 0.080 | -6.872 | 0.081 |
| EA | retail | chronos2 | multivariate_levels | realtime | first_release | 48 | 47 | -1.426 | 1.165 | -1.223 | 0.322 |
| EA | retail | chronos2 | multivariate_levels | realtime | revised_12m | 51 | 48 | -1.269 | 1.236 | -1.027 | 0.451 |
| EA | retail | chronos2 | univariate | realtime | first_release | 2784 | 258 | -0.551 | 0.124 | -4.433 | -0.023 |
| EA | retail | chronos2 | univariate | realtime | revised_12m | 2797 | 259 | -0.559 | 0.127 | -4.419 | 0.117 |
| EA | retail | chronos2 | univariate_levels | realtime | first_release | 48 | 47 | -1.557 | 1.470 | -1.059 | 0.315 |
| EA | retail | chronos2 | univariate_levels | realtime | revised_12m | 51 | 48 | -1.171 | 1.244 | -0.942 | 0.430 |
| EA | retail | combo_bench | multivariate | realtime | first_release | 2760 | 258 | -0.352 | 0.285 | -1.237 | -0.118 |
| EA | retail | combo_bench | multivariate | realtime | revised_12m | 2773 | 259 | -0.350 | 0.289 | -1.209 | 0.020 |
| EA | retail | combo_fm | univariate | realtime | first_release | 2784 | 258 | -0.600 | 0.145 | -4.138 | -0.049 |
| EA | retail | combo_fm | univariate | realtime | revised_12m | 2797 | 259 | -0.610 | 0.148 | -4.114 | 0.091 |
| EA | retail | dfm | multivariate | realtime | first_release | 2760 | 258 | -0.402 | 0.246 | -1.633 | -0.085 |
| EA | retail | dfm | multivariate | realtime | revised_12m | 2773 | 259 | -0.430 | 0.248 | -1.738 | 0.053 |
| EA | retail | moirai2 | univariate | realtime | first_release | 2784 | 258 | -0.567 | 0.111 | -5.124 | -0.041 |
| EA | retail | moirai2 | univariate | realtime | revised_12m | 2797 | 259 | -0.576 | 0.113 | -5.096 | 0.099 |
| EA | retail | moirai2 | univariate_levels | realtime | first_release | 48 | 47 | -3.388 | 1.759 | -1.926 | 0.378 |
| EA | retail | moirai2 | univariate_levels | realtime | revised_12m | 51 | 48 | -3.353 | 1.850 | -1.812 | 0.493 |
| EA | retail | naive | univariate | realtime | first_release | 2784 | 258 | -9.597 | 11.099 | -0.865 | -0.144 |
| EA | retail | naive | univariate | realtime | revised_12m | 2797 | 259 | -10.002 | 11.333 | -0.883 | -0.004 |
| EA | retail | timesfm25 | univariate | realtime | first_release | 2784 | 258 | -0.767 | 0.257 | -2.988 | -0.092 |
| EA | retail | timesfm25 | univariate | realtime | revised_12m | 2797 | 259 | -0.782 | 0.264 | -2.966 | 0.049 |
| EA | retail | timesfm25 | univariate_levels | realtime | first_release | 48 | 47 | -0.446 | 0.753 | -0.592 | 0.250 |
| EA | retail | timesfm25 | univariate_levels | realtime | revised_12m | 51 | 48 | 0.042 | 0.665 | 0.063 | 0.371 |

_52 more rows in the CSV_

**pooled_std**

| econ | model | variant | input_mode | outturn | n | se_hac | t | n_targets | beta_std |
|---|---|---|---|---|---|---|---|---|---|
| CA | ar | univariate | realtime | first_release | 14670 | 0.016 | -6.527 | 6 | -0.105 |
| CA | ar | univariate | realtime | revised_12m | 14707 | 0.016 | -6.710 | 6 | -0.105 |
| CA | bvar | multivariate | realtime | first_release | 14614 | 0.024 | -2.791 | 6 | -0.068 |
| CA | bvar | multivariate | realtime | revised_12m | 14651 | 0.024 | -2.830 | 6 | -0.068 |
| CA | chronos2 | multivariate | realtime | first_release | 14242 | 0.024 | -8.906 | 6 | -0.214 |
| CA | chronos2 | multivariate | realtime | revised_12m | 14279 | 0.024 | -8.741 | 6 | -0.214 |
| CA | chronos2 | multivariate_levels | realtime | first_release | 312 | 0.048 | 1.915 | 5 | 0.092 |
| CA | chronos2 | multivariate_levels | realtime | revised_12m | 312 | 0.046 | 1.966 | 5 | 0.089 |
| CA | chronos2 | univariate | realtime | first_release | 14670 | 0.023 | -8.251 | 6 | -0.187 |
| CA | chronos2 | univariate | realtime | revised_12m | 14707 | 0.023 | -8.259 | 6 | -0.187 |
| CA | chronos2 | univariate_levels | realtime | first_release | 375 | 0.008 | -2.766 | 3 | -0.022 |
| CA | chronos2 | univariate_levels | realtime | revised_12m | 375 | 0.009 | -2.006 | 3 | -0.018 |
| CA | combo_bench | multivariate | realtime | first_release | 13556 | 0.022 | -0.962 | 6 | -0.022 |
| CA | combo_bench | multivariate | realtime | revised_12m | 13590 | 0.022 | -1.044 | 6 | -0.023 |
| CA | combo_fm | univariate | realtime | first_release | 14670 | 0.018 | -6.310 | 6 | -0.112 |
| CA | combo_fm | univariate | realtime | revised_12m | 14707 | 0.018 | -6.161 | 6 | -0.113 |
| CA | dfm | multivariate | realtime | first_release | 13612 | 0.033 | 0.516 | 6 | 0.017 |
| CA | dfm | multivariate | realtime | revised_12m | 13646 | 0.033 | 0.471 | 6 | 0.016 |
| CA | moirai2 | univariate | realtime | first_release | 14670 | 0.020 | -5.979 | 6 | -0.121 |
| CA | moirai2 | univariate | realtime | revised_12m | 14707 | 0.021 | -5.740 | 6 | -0.123 |
| CA | moirai2 | univariate_levels | realtime | first_release | 375 | 0.012 | 0.505 | 3 | 0.006 |
| CA | moirai2 | univariate_levels | realtime | revised_12m | 375 | 0.012 | -0.028 | 3 | -0.000 |
| CA | naive | univariate | realtime | first_release | 14670 | 0.012 | -1.968 | 6 | -0.023 |
| CA | naive | univariate | realtime | revised_12m | 14707 | 0.012 | -1.986 | 6 | -0.024 |
| CA | timesfm25 | univariate | realtime | first_release | 14670 | 0.015 | -5.903 | 6 | -0.087 |
| CA | timesfm25 | univariate | realtime | revised_12m | 14707 | 0.015 | -5.776 | 6 | -0.089 |
| CA | timesfm25 | univariate_levels | realtime | first_release | 375 | 0.005 | -0.894 | 3 | -0.005 |
| CA | timesfm25 | univariate_levels | realtime | revised_12m | 375 | 0.007 | -1.517 | 3 | -0.011 |
| CA | tirex | univariate | realtime | first_release | 14670 | 0.016 | -7.054 | 6 | -0.113 |
| CA | tirex | univariate | realtime | revised_12m | 14707 | 0.017 | -6.859 | 6 | -0.116 |
| CA | tirex | univariate_levels | realtime | first_release | 375 | 0.006 | -0.705 | 3 | -0.004 |
| CA | tirex | univariate_levels | realtime | revised_12m | 375 | 0.009 | -0.567 | 3 | -0.005 |
| CA | tirex2 | multivariate | realtime | first_release | 14242 | 0.020 | -5.477 | 6 | -0.111 |
| CA | tirex2 | multivariate | realtime | revised_12m | 14279 | 0.022 | -5.291 | 6 | -0.115 |
| CA | tirex2 | multivariate_levels | realtime | first_release | 312 | 0.034 | -0.349 | 5 | -0.012 |
| CA | tirex2 | multivariate_levels | realtime | revised_12m | 312 | 0.029 | -0.426 | 5 | -0.013 |
| CA | tirex2 | univariate | realtime | first_release | 14670 | 0.021 | -4.421 | 6 | -0.094 |
| CA | tirex2 | univariate | realtime | revised_12m | 14707 | 0.023 | -4.239 | 6 | -0.099 |
| CA | tirex2 | univariate_levels | realtime | first_release | 375 | 0.005 | -0.333 | 3 | -0.002 |
| CA | tirex2 | univariate_levels | realtime | revised_12m | 375 | 0.009 | -0.234 | 3 | -0.002 |
| EA | ar | univariate | realtime | first_release | 13353 | 0.027 | -6.420 | 6 | -0.172 |
| EA | ar | univariate | realtime | revised_12m | 13400 | 0.030 | -5.761 | 6 | -0.170 |
| EA | bvar | multivariate | realtime | first_release | 13344 | 0.014 | -4.671 | 6 | -0.067 |
| EA | bvar | multivariate | realtime | revised_12m | 13388 | 0.015 | -4.292 | 6 | -0.066 |
| EA | chronos2 | multivariate | realtime | first_release | 12904 | 0.018 | -7.925 | 6 | -0.146 |
| EA | chronos2 | multivariate | realtime | revised_12m | 12951 | 0.021 | -6.800 | 6 | -0.142 |
| EA | chronos2 | multivariate_levels | realtime | first_release | 543 | 0.068 | -0.815 | 5 | -0.055 |
| EA | chronos2 | multivariate_levels | realtime | revised_12m | 548 | 0.030 | -0.116 | 5 | -0.004 |
| EA | chronos2 | univariate | realtime | first_release | 13353 | 0.021 | -7.009 | 6 | -0.149 |
| EA | chronos2 | univariate | realtime | revised_12m | 13400 | 0.023 | -6.076 | 6 | -0.141 |
| EA | chronos2 | univariate_levels | realtime | first_release | 438 | 0.023 | -2.173 | 3 | -0.050 |
| EA | chronos2 | univariate_levels | realtime | revised_12m | 441 | 0.014 | -2.828 | 3 | -0.040 |
| EA | combo_bench | multivariate | realtime | first_release | 13272 | 0.019 | -2.994 | 6 | -0.057 |
| EA | combo_bench | multivariate | realtime | revised_12m | 13316 | 0.024 | -2.589 | 6 | -0.062 |
| EA | combo_fm | univariate | realtime | first_release | 13353 | 0.021 | -6.061 | 6 | -0.126 |
| EA | combo_fm | univariate | realtime | revised_12m | 13400 | 0.023 | -5.289 | 6 | -0.123 |
| EA | dfm | multivariate | realtime | first_release | 13281 | 0.012 | -6.792 | 6 | -0.079 |
| EA | dfm | multivariate | realtime | revised_12m | 13328 | 0.013 | -5.974 | 6 | -0.076 |
| EA | moirai2 | univariate | realtime | first_release | 13353 | 0.018 | -8.655 | 6 | -0.159 |
| EA | moirai2 | univariate | realtime | revised_12m | 13400 | 0.021 | -7.307 | 6 | -0.154 |
| EA | moirai2 | univariate_levels | realtime | first_release | 438 | 0.016 | -2.034 | 3 | -0.032 |
| EA | moirai2 | univariate_levels | realtime | revised_12m | 441 | 0.020 | -2.239 | 3 | -0.046 |
| EA | naive | univariate | realtime | first_release | 13353 | 0.014 | -0.445 | 6 | -0.006 |
| EA | naive | univariate | realtime | revised_12m | 13400 | 0.017 | -0.453 | 6 | -0.007 |
| EA | timesfm25 | univariate | realtime | first_release | 13353 | 0.018 | -6.559 | 6 | -0.121 |
| EA | timesfm25 | univariate | realtime | revised_12m | 13400 | 0.020 | -6.137 | 6 | -0.123 |
| EA | timesfm25 | univariate_levels | realtime | first_release | 438 | 0.096 | -1.170 | 3 | -0.112 |
| EA | timesfm25 | univariate_levels | realtime | revised_12m | 441 | 0.072 | -1.058 | 3 | -0.077 |
| EA | tirex | univariate | realtime | first_release | 13353 | 0.020 | -8.497 | 6 | -0.168 |
| EA | tirex | univariate | realtime | revised_12m | 13400 | 0.023 | -7.200 | 6 | -0.164 |
| EA | tirex | univariate_levels | realtime | first_release | 438 | 0.014 | -1.331 | 3 | -0.018 |
| EA | tirex | univariate_levels | realtime | revised_12m | 441 | 0.017 | -1.031 | 3 | -0.017 |
| EA | tirex2 | multivariate | realtime | first_release | 12904 | 0.022 | -5.052 | 6 | -0.113 |
| EA | tirex2 | multivariate | realtime | revised_12m | 12951 | 0.026 | -4.476 | 6 | -0.115 |
| EA | tirex2 | multivariate_levels | realtime | first_release | 543 | 0.067 | -0.399 | 5 | -0.027 |
| EA | tirex2 | multivariate_levels | realtime | revised_12m | 548 | 0.078 | -0.586 | 5 | -0.046 |
| EA | tirex2 | univariate | realtime | first_release | 13353 | 0.021 | -6.255 | 6 | -0.133 |
| EA | tirex2 | univariate | realtime | revised_12m | 13400 | 0.024 | -5.449 | 6 | -0.133 |
| EA | tirex2 | univariate_levels | realtime | first_release | 438 | 0.063 | -0.935 | 3 | -0.059 |
| EA | tirex2 | univariate_levels | realtime | revised_12m | 441 | 0.063 | -1.130 | 3 | -0.071 |

## 7. Q4: ECB SPF respondents and matched model runs

Same regression on the ECB Survey of Professional Forecasters: individual respondents pooled with forecaster fixed effects (`spf_individual_fe`), the consensus mean, each model and the cross-model mean, on the same rounds and calendar-year targets (`docs/backtest.md`, SPF).

| who | variable | outturn | n | n_ids | beta | se_hac | t |
|---|---|---|---|---|---|---|---|
| model:ar | CORE | first_release | 84 | 1 | -0.097 | 0.244 | -0.399 |
| model:bvar | CORE | first_release | 84 | 1 | -0.064 | 0.214 | -0.298 |
| model:chronos2 | CORE | first_release | 84 | 1 | -0.128 | 0.281 | -0.454 |
| model:combo_bench | CORE | first_release | 81 | 1 | 0.044 | 0.215 | 0.206 |
| model:combo_fm | CORE | first_release | 84 | 1 | -0.087 | 0.228 | -0.382 |
| model:dfm | CORE | first_release | 81 | 1 | -0.315 | 0.080 | -3.920 |
| model:moirai2 | CORE | first_release | 84 | 1 | -0.247 | 0.183 | -1.355 |
| model:naive | CORE | first_release | 84 | 1 | -0.259 | 0.099 | -2.614 |
| model:timesfm25 | CORE | first_release | 84 | 1 | 0.062 | 0.288 | 0.215 |
| model:tirex | CORE | first_release | 84 | 1 | -0.026 | 0.247 | -0.104 |
| model:tirex2 | CORE | first_release | 84 | 1 | -0.258 | 0.128 | -2.022 |
| spf_consensus | CORE | first_release | 89 | 1 | 1.197 | 0.523 | 2.289 |
| spf_individual_fe | CORE | first_release | 3122 | 75 | 0.125 | 0.050 | 2.484 |
| model:ar | CORE | revised_12m | 84 | 1 | -0.097 | 0.244 | -0.399 |
| model:bvar | CORE | revised_12m | 84 | 1 | -0.064 | 0.214 | -0.298 |
| model:chronos2 | CORE | revised_12m | 84 | 1 | -0.128 | 0.281 | -0.454 |
| model:combo_bench | CORE | revised_12m | 81 | 1 | 0.044 | 0.215 | 0.206 |
| model:combo_fm | CORE | revised_12m | 84 | 1 | -0.087 | 0.228 | -0.382 |
| model:dfm | CORE | revised_12m | 81 | 1 | -0.315 | 0.080 | -3.920 |
| model:moirai2 | CORE | revised_12m | 84 | 1 | -0.247 | 0.183 | -1.355 |
| model:naive | CORE | revised_12m | 84 | 1 | -0.259 | 0.099 | -2.614 |
| model:timesfm25 | CORE | revised_12m | 84 | 1 | 0.062 | 0.288 | 0.215 |
| model:tirex | CORE | revised_12m | 84 | 1 | -0.026 | 0.247 | -0.104 |
| model:tirex2 | CORE | revised_12m | 84 | 1 | -0.258 | 0.128 | -2.022 |
| spf_consensus | CORE | revised_12m | 89 | 1 | 1.197 | 0.523 | 2.289 |
| spf_individual_fe | CORE | revised_12m | 3122 | 75 | 0.125 | 0.050 | 2.484 |
| model:ar | HICP | first_release | 87 | 1 | -0.046 | 0.298 | -0.155 |
| model:bvar | HICP | first_release | 87 | 1 | 0.250 | 0.285 | 0.878 |
| model:chronos2 | HICP | first_release | 87 | 1 | 0.183 | 0.389 | 0.471 |
| model:combo_bench | HICP | first_release | 85 | 1 | 0.330 | 0.329 | 1.002 |
| model:combo_fm | HICP | first_release | 87 | 1 | 0.192 | 0.318 | 0.606 |
| model:dfm | HICP | first_release | 85 | 1 | 0.195 | 0.270 | 0.722 |
| model:moirai2 | HICP | first_release | 87 | 1 | -0.084 | 0.195 | -0.429 |
| model:naive | HICP | first_release | 87 | 1 | 0.366 | 0.280 | 1.304 |
| model:timesfm25 | HICP | first_release | 87 | 1 | 0.131 | 0.324 | 0.403 |
| model:tirex | HICP | first_release | 87 | 1 | 0.064 | 0.281 | 0.228 |
| model:tirex2 | HICP | first_release | 87 | 1 | -0.078 | 0.235 | -0.331 |
| spf_consensus | HICP | first_release | 87 | 1 | 0.665 | 0.399 | 1.667 |
| spf_individual_fe | HICP | first_release | 4348 | 85 | 0.163 | 0.049 | 3.315 |
| model:ar | HICP | revised_12m | 87 | 1 | -0.047 | 0.298 | -0.157 |
| model:bvar | HICP | revised_12m | 87 | 1 | 0.250 | 0.285 | 0.876 |
| model:chronos2 | HICP | revised_12m | 87 | 1 | 0.184 | 0.390 | 0.471 |
| model:combo_bench | HICP | revised_12m | 85 | 1 | 0.329 | 0.329 | 1.000 |
| model:combo_fm | HICP | revised_12m | 87 | 1 | 0.192 | 0.318 | 0.606 |
| model:dfm | HICP | revised_12m | 85 | 1 | 0.194 | 0.270 | 0.720 |
| model:moirai2 | HICP | revised_12m | 87 | 1 | -0.084 | 0.195 | -0.429 |
| model:naive | HICP | revised_12m | 87 | 1 | 0.365 | 0.280 | 1.303 |
| model:timesfm25 | HICP | revised_12m | 87 | 1 | 0.131 | 0.324 | 0.404 |
| model:tirex | HICP | revised_12m | 87 | 1 | 0.064 | 0.281 | 0.228 |
| model:tirex2 | HICP | revised_12m | 87 | 1 | -0.078 | 0.235 | -0.332 |
| spf_consensus | HICP | revised_12m | 87 | 1 | 0.664 | 0.399 | 1.664 |
| spf_individual_fe | HICP | revised_12m | 4348 | 85 | 0.163 | 0.049 | 3.306 |
| model:ar | RGDP | first_release | 140 | 1 | -0.537 | 0.229 | -2.345 |
| model:bvar | RGDP | first_release | 136 | 1 | -0.227 | 0.165 | -1.374 |
| model:chronos2 | RGDP | first_release | 140 | 1 | -0.506 | 0.153 | -3.297 |
| model:combo_bench | RGDP | first_release | 136 | 1 | -0.044 | 0.159 | -0.280 |
| model:combo_fm | RGDP | first_release | 140 | 1 | -0.490 | 0.109 | -4.505 |
| model:dfm | RGDP | first_release | 140 | 1 | -0.346 | 0.108 | -3.190 |
| model:moirai2 | RGDP | first_release | 140 | 1 | -0.489 | 0.132 | -3.706 |
| model:naive | RGDP | first_release | 140 | 1 | -0.336 | 0.144 | -2.335 |
| model:timesfm25 | RGDP | first_release | 140 | 1 | -0.438 | 0.081 | -5.408 |
| model:tirex | RGDP | first_release | 140 | 1 | -0.508 | 0.112 | -4.525 |
| model:tirex2 | RGDP | first_release | 140 | 1 | -0.449 | 0.131 | -3.436 |
| spf_consensus | RGDP | first_release | 145 | 1 | 0.100 | 0.094 | 1.066 |
| spf_individual_fe | RGDP | first_release | 7474 | 87 | -0.132 | 0.021 | -6.229 |
| model:ar | RGDP | revised_12m | 140 | 1 | -0.542 | 0.230 | -2.351 |
| model:bvar | RGDP | revised_12m | 136 | 1 | -0.239 | 0.163 | -1.469 |
| model:chronos2 | RGDP | revised_12m | 140 | 1 | -0.507 | 0.153 | -3.301 |
| model:combo_bench | RGDP | revised_12m | 136 | 1 | -0.063 | 0.158 | -0.397 |
| model:combo_fm | RGDP | revised_12m | 140 | 1 | -0.492 | 0.109 | -4.494 |
| model:dfm | RGDP | revised_12m | 140 | 1 | -0.359 | 0.108 | -3.330 |
| model:moirai2 | RGDP | revised_12m | 140 | 1 | -0.493 | 0.133 | -3.700 |
| model:naive | RGDP | revised_12m | 140 | 1 | -0.355 | 0.144 | -2.466 |
| model:timesfm25 | RGDP | revised_12m | 140 | 1 | -0.438 | 0.081 | -5.390 |
| model:tirex | RGDP | revised_12m | 140 | 1 | -0.510 | 0.113 | -4.504 |
| model:tirex2 | RGDP | revised_12m | 140 | 1 | -0.458 | 0.132 | -3.462 |
| spf_consensus | RGDP | revised_12m | 145 | 1 | 0.076 | 0.100 | 0.765 |
| spf_individual_fe | RGDP | revised_12m | 7474 | 87 | -0.148 | 0.021 | -7.143 |
| model:ar | UNEM | first_release | 130 | 1 | -0.051 | 0.208 | -0.244 |
| model:bvar | UNEM | first_release | 130 | 1 | -0.230 | 0.116 | -1.985 |
| model:chronos2 | UNEM | first_release | 130 | 1 | -0.294 | 0.162 | -1.816 |
| model:combo_bench | UNEM | first_release | 130 | 1 | 0.087 | 0.184 | 0.472 |
| model:combo_fm | UNEM | first_release | 130 | 1 | -0.249 | 0.160 | -1.558 |
| model:dfm | UNEM | first_release | 130 | 1 | 0.421 | 0.201 | 2.092 |
| model:moirai2 | UNEM | first_release | 130 | 1 | -0.175 | 0.143 | -1.223 |
| model:naive | UNEM | first_release | 130 | 1 | 0.841 | 0.474 | 1.773 |
| model:timesfm25 | UNEM | first_release | 130 | 1 | -0.286 | 0.174 | -1.646 |
| model:tirex | UNEM | first_release | 130 | 1 | -0.279 | 0.150 | -1.867 |
| model:tirex2 | UNEM | first_release | 130 | 1 | -0.232 | 0.151 | -1.537 |
| spf_consensus | UNEM | first_release | 133 | 1 | -0.364 | 0.143 | -2.544 |
| spf_individual_fe | UNEM | first_release | 6075 | 82 | -0.422 | 0.020 | -20.840 |
| model:ar | UNEM | revised_12m | 130 | 1 | -0.054 | 0.206 | -0.263 |
| model:bvar | UNEM | revised_12m | 130 | 1 | -0.232 | 0.114 | -2.029 |
| model:chronos2 | UNEM | revised_12m | 130 | 1 | -0.294 | 0.160 | -1.835 |
| model:combo_bench | UNEM | revised_12m | 130 | 1 | 0.082 | 0.181 | 0.454 |
| model:combo_fm | UNEM | revised_12m | 130 | 1 | -0.250 | 0.158 | -1.583 |
| model:dfm | UNEM | revised_12m | 130 | 1 | 0.413 | 0.198 | 2.090 |
| model:moirai2 | UNEM | revised_12m | 130 | 1 | -0.176 | 0.142 | -1.239 |
| model:naive | UNEM | revised_12m | 130 | 1 | 0.829 | 0.466 | 1.779 |
| model:timesfm25 | UNEM | revised_12m | 130 | 1 | -0.287 | 0.172 | -1.665 |
| model:tirex | UNEM | revised_12m | 130 | 1 | -0.280 | 0.148 | -1.894 |
| model:tirex2 | UNEM | revised_12m | 130 | 1 | -0.233 | 0.150 | -1.554 |
| spf_consensus | UNEM | revised_12m | 133 | 1 | -0.361 | 0.139 | -2.591 |
| spf_individual_fe | UNEM | revised_12m | 6075 | 82 | -0.421 | 0.020 | -21.096 |
