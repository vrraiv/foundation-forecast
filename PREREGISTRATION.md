# Pre-registration of the live forecast record

**Status: DRAFT for HUMAN GATE 5. Not frozen, not hashed, not in any ledger.** The owner approves
this text first; only then is it hashed and made the first ledger entry. Items marked
**PROPOSED** are choices the plan left open and the agent filled in; the owner may change any of
them before the freeze. After the freeze nothing in this file changes; later changes go into
`PREREGISTRATION_AMENDMENTS.md` (section 11).

Configuration this text describes (hash of the parsed `configs/default.yaml`, independent of
comments and line endings; `tests/test_registry.py` fails if the two drift apart):

Design hash: `214ffc27b65e76d0a064e7eeaa5939126582d39d1922463c80ef2eb69a2cabdc`

## 1. What is being registered

Research question Q5 of `PLAN.md`: do the backtest results hold up in a genuinely live record?
From the first origin after the freeze, forecasts are made once a month for twelve macroeconomic
targets (six for Canada, six for the euro area) by five open time-series foundation models and
by classical benchmarks, stored privately, and committed to publicly by hash before the outturns
exist. Nothing here is tuned on, or changed in response to, the backtest results published on
2026-11-18 and 2026-11-19.

## 2. Origins and runs

- One origin per month: the 25th, or the next business day (Monday to Friday; holidays are not
  applied). First origin: the first one after this text is frozen.
- A run is made on the origin day. **PROPOSED:** at 18:00 local time (America/Toronto), after
  the day's Statistics Canada (08:30 ET) and Eurostat (11:00 CET) releases.
- **Late runs.** A run made after its origin day is recorded as late, with the number of days,
  in its manifest. In `realtime` mode (section 3) it uses the data as of the intended origin,
  which the vintage dating allows exactly except for pseudo-vintage targets, whose base series
  is the one downloaded on the run day. In `live` mode it necessarily uses what is public on the
  run day. **PROPOSED:** late `realtime` forecasts are scored with the on-time ones; late `live`
  forecasts are reported separately and excluded from the main `live` tables, which, `live`
  being the primary mode, makes an on-time run matter. Evidence for the
  first half of that: the trial run of 2026-11-19 for the origin 2026-10-26, made 24 days late
  from a fresh download, reproduced the backtest's stored `realtime` forecasts for that origin
  exactly, all 18,720 rows, every model and benchmark, pseudo-vintage targets included.
- A missed month is not back-filled once the next origin has passed; the run command refuses an
  overtaken origin. Its absence is visible in the ledger.
- One run per origin. The ledger refuses a second entry for the same origin.

## 3. Information sets

Every run takes one snapshot of the public data (all sources of the backtest, downloaded on the
run day, hashed file by file) and forecasts from it under two rules. Both are stored; they are
separate rows of the same forecast file.

**`realtime`: the backtest rule.** Each series as of the origin: the newest vintage dated
strictly before the origin date, with the backtest's dating conventions (an OECD edition of month
M is dated the 1st of M+1; ECB real-time database snapshots and Statistics Canada real-time
tables carry their own dates; pseudo-vintage targets show month m from the origin of m+1), the
same primary and fallback sources and staleness limits, the same panels. This is the rule under
which every backtest number was produced. It is deliberately conservative: at a given origin it
can be a month or more behind what is public.

What kind of information set this is. Every value in it was public before the origin, and each
series taken alone is exactly one published vintage, so for a univariate model the set is a real
one from an earlier date. Across series the vintages have different ages, because the sources
take their snapshots at different times (measured over the 2015+ backtest origins: OECD editions
are dated 24 to 25 days before the origin, and their content suggests they are cut in the first
half of the edition month, some weeks before that date, though no publication date is recorded;
ECB real-time database snapshots are 1 to about 50 days old, eight a year; Statistics Canada
real-time tables date from their last release; daily market series run to the last business day
before the origin, 1 to 4 days; the Bank of Canada commodity index is 25 to 27 days old; policy
rates are recorded at their dates of change and carried forward). A multivariate
panel is therefore what a forecaster reading those databases on the origin day would have seen,
not the complete public record of any single date. It contains no value that was unknown at the
time; what it can contain is one series updated or revised more recently than another.

**`live`: everything public at the run.** A live snapshot cannot contain anything from after the
run, so the conservative dating is not needed to prevent look-ahead. In this mode

- each target is the national series named in section 4, as downloaded;
- where the national series starts later than the vintage history, earlier periods come from
  the newest vintage of the target's vintage source, rescaled to join at the first national
  period (ratio for log-difference targets, shift for difference targets), so every growth rate
  before the join comes from the vintage source and every one after it from the national
  series. This applies to three targets: Canadian retail (joined at 2017-01), Canadian
  unemployment (1976-01) and euro-area retail (2000-01). The foundation models read the last 512
  observations, which reach back past the joins of Canadian retail and euro-area retail; the
  multivariate panels use the last 240 months, which contain only the Canadian retail join; the
  benchmarks use the whole history;
- each conditioning series is taken at its newest downloaded vintage, including vintages the
  conservative rule would date after the origin;
- a release published on the origin day before the run is in the information set.

Step 1 always refers to the first period after the target's last observation in the information
set used, so the same origin can have different step-1 periods in the two modes. Forecasts are
joined to outturns by target period, never by step alone.

**`live` is the primary mode of the live record (owner decision 2026-11-19).** It is the
information set a forecaster actually has on the run day, and it is coherent as of a single
date, which the backtest rule's mixed vintage ages are not. The cost is accepted and stated: the
comparison with the backtest (Q5) is then not like for like. The live models see more recent
data than the backtest models did at the same origin, so step 1 often refers to a later period
and accuracy at a given step is not expected to be equal. Because the live information set is
the richer one, a live record that does worse than the backtest, relative to the AR benchmark
under the same information, is the stronger signal; one that does better is the weaker one.
`realtime` is stored at every origin as the like-for-like control and reported alongside.

## 4. Targets

| Economy | Target | Freq | Transform | Source under the backtest rule (`realtime`) | National series (`live`) |
|---|---|---|---|---|---|
| CA | gdp: Real GDP, expenditure-based | Q | log_diff | StatCan real-time table 36-10-0431 (DBnomics mirror); fallback OECD editions B1GQ_Q | `statcan:36100104:v62305752` |
| CA | cpi: CPI all items, NSA | M | log_diff | pseudo-vintages of `valet:V41690973` (the Bank of Canada's mirror of the national series, identical values); fallback OECD editions CP | `statcan:18100004:v41690973` |
| CA | cpi_core: CPI excluding food, energy and indirect taxes (CPI-XFET), NSA | M | log_diff | pseudo-vintages of `statcan:18100256:v1675033092` | `statcan:18100256:v1675033092` |
| CA | unemp: Unemployment rate, LFS, SA | M | diff | OECD editions UNEMP | `statcan:14100287:v2062815` |
| CA | retail: Retail sales volume | M | log_diff | OECD editions TOVM, activity G47 | `statcan:20100067:v1446870183` |
| CA | consumption: Household final consumption expenditure, volume | Q | log_diff | StatCan real-time table 36-10-0431 (DBnomics mirror); fallback OECD editions P3_S1M_Q | `statcan:36100107:v61989012` |
| EA | gdp: Real GDP, chain-linked volumes, SA | Q | log_diff | ECB RTD `Q.S0.S.G_GDPM_TO_C.E`; fallback OECD editions B1GQ_Q | `eurostat:namq_10_gdp[geo=EA21.na_item=B1GQ.s_adj=SCA.unit=CLV_I15]` |
| EA | hicp: HICP all items | M | log_diff | ECB RTD `M.S0.N.P_C_OV.X`; fallback OECD editions CP | `eurostat:prc_hicp_minr[coicop18=TOTAL.geo=EA.unit=I25]` |
| EA | hicp_core: HICP excluding energy, food, alcohol and tobacco | M | log_diff | pseudo-vintages of the national series | `eurostat:prc_hicp_minr[coicop18=TOT_X_NRG_FOOD.geo=EA.unit=I25]` |
| EA | unemp: Unemployment rate, SA | M | diff | ECB RTD `M.S0.S.L_UNETO.F`; fallback OECD editions UNEMP | `eurostat:une_rt_m[age=TOTAL.geo=EA21.s_adj=SA.sex=T.unit=PC_ACT]` |
| EA | retail: Retail trade volume ex motor vehicles | M | log_diff | OECD editions TOVM, activity G47 | `eurostat:sts_trtu_m[geo=EA21.indic_bt=VOL_SLS.nace_r2=G47.s_adj=SCA.unit=I21]` |
| EA | consumption: Household and NPISH final consumption, chain-linked volumes | Q | log_diff | ECB RTD `Q.S0.S.G_FCHI_TO_C.E`; fallback OECD editions P3_S1M_Q | `eurostat:namq_10_gdp[geo=EA21.na_item=P31_S14_S15.s_adj=SCA.unit=CLV_I15]` |

Canadian retail: the national series is Statistics Canada's retail sales at 2017 constant
prices, the series the OECD volume index copies (owner decision 2026-11-19; monthly log growth
equal to within 0.0001 over 116 common months). The Canadian core measure is CPI-XFET, not the
plan's CPI excluding food and energy, which has no public scripted source.

Conditioning sets for the multivariate variants: the 14 Canadian and 28 euro-area series listed
in the configuration, selected per origin by the fixed coverage and staleness rule of
`docs/model_cards.md`.

If a download fails on the run day (after three attempts), nothing is sealed and the run is
repeated; files already downloaded that day are reused. **PROPOSED:** if a source stays
unavailable for the whole origin day, the run is sealed without it rather than made late: the
series that depend on it are missing from the snapshot, the targets that cannot be built are
skipped for that origin, and the failed downloads are listed in the manifest. Nothing is filled
in, interpolated or substituted.

## 5. Horizons and variants

- Monthly targets: steps 1 to 12 are stored; horizons 1, 3, 6, 12 are scored. Quarterly targets:
  steps 1 to 4 stored; horizons 1, 2, 4 scored.
- Quantiles 0.1 to 0.9; the median is the point forecast where a model reports no mean.
- Primary specification: stationary inputs (log-difference or difference), scored in that
  space. Secondary: levels inputs, foundation models only, mapped to the step-1 transform and to
  the cumulative h-step change as in the backtest.
- A target with fewer than 120 monthly or 40 quarterly observations in the information set is
  skipped at that origin.
- A forecast that trips the numerical-validity guard (non-finite, or beyond 50 standard
  deviations of its own input history) is stored as an error, never as values.

## 6. Models

Five foundation models, zero-shot, on CPU, pinned by weight revision and lockfile:

| Key | Hugging Face ID | Revision | Weights date | Licence | Variants |
|---|---|---|---|---|---|
| chronos2 | `amazon/chronos-2` | `29ec3766d36d6f73f0696f85560a422f50e8498c` | 2025-10-30 | Apache-2.0 | univariate, multivariate |
| timesfm25 | `google/timesfm-2.5-200m-pytorch` | `1d952420fba87f3c6dee4f240de0f1a0fbc790e3` | 2025-10-01 | Apache-2.0 | univariate |
| tirex | `NX-AI/TiRex` | `43ebaaff068c1390785c387b3e5178df3f4c92ca` | 2025-05-26 | NXAI Community | univariate |
| tirex2 | `NX-AI/TiRex-2` | `352636173653592b6dceb3fbeee9224ca97952a9` | 2026-10-06 | Apache-2.0 | univariate, multivariate |
| moirai2 | `Salesforce/moirai-2.0-R-small` | `30f43ff08c8494f4943ae1521e9d4e94a0fbb389` | 2025-08-06 | CC-BY-NC-4.0 | univariate |

Benchmarks, re-estimated at every origin on that origin's information set, with the rules of
the configuration: naive (random walk or mean), direct AR (lag by BIC), Minnesota BVAR
(hyperparameters by marginal likelihood on a fixed grid), mixed-frequency dynamic factor model.
Combinations: `combo_bench` (equal weight of AR, BVAR, DFM) and `combo_fm` (equal weight of the
five foundation models' univariate forecasts), each only where every member exists. `combo_fm`
is formed at scoring from the stored member forecasts, as in the backtest; `combo_bench` is
stored with the other forecasts.

Every live origin postdates every model's weights, so the whole live record is out of sample for
all five models in the sense of Q2.

Not in the live record: TimesFM 3.0. It was added to the backtest on 2026-11-19 after the Gate 4
results had been seen, its backtest tables were published the same day, and the owner then
retired it (`docs/backtest.md`, Deviations 7). No model is added to or removed from the live
record after the freeze; a newer model would start a separate record under its own
pre-registration.

## 7. What is stored and what is public

Per origin, privately: the data snapshot (raw downloads and normalised tables), the forecast
file, a status file (one row per model, target and mode: ok, skipped or error), a random 256-bit
salt, copies of the configuration and lockfiles used, and a manifest. The manifest holds the
origin, the run time (UTC), whether the run was late, the code commit, the design hash, the hash
of this text, salted SHA-256 commitments to the forecast and status files, the digest of the
snapshot, the hashes of the pinned files and the digest of each model's weights.

Publicly: one ledger line per origin with the origin date, the time the line was appended (UTC),
the SHA-256 of the manifest, and the hash of the previous line. The first line is the hash of this text. Each line
is time-stamped independently with OpenTimestamps (owner approval 2026-11-19; only the line's
hash is sent to the public calendar servers). No forecast value, score or data value is
public, and the salt prevents confirming a guessed forecast file from its hash.

The forecast file is reproducible byte for byte from the stored snapshot, the pinned
configuration, lockfiles and weights; `ffcast registry-verify` checks every ledger line against
the private files and can rerun any origin.

## 8. Outturns

- **`realtime` mode:** as in the backtest. First release: the value in the first vintage of the
  target's vintage source that contains the period, transformed inside that vintage. Revised:
  the vintage visible 12 months after that. A first release that appears later than the series'
  median first-release lag plus the source's staleness limit is flagged late, excluded from
  first-release scoring and counted.
- **`live` mode (PROPOSED):** the registry's own monthly snapshots are the vintages. First
  release: the value of the period in the first snapshot of the national series that contains
  it, transformed inside that snapshot. Revised: the value in the snapshot taken 12 origins
  later. Because snapshots are monthly, a first release can already include a revision made
  within the same month; this is accepted and stated in every table.
- Unemployment rates are rounded to one decimal before revisions are measured.
- Primary outturn for accuracy: first release. The revised outturn is reported alongside.

## 9. Scoring

- **No scoring before the record is long enough (PROPOSED, the plan's default):** the live
  record is first scored when at least 12 monthly origins have first-release outturns at horizon
  1 for every monthly target. Until then no score, error or ranking is computed from the live
  forecasts, by anyone, for any purpose; the forecast files are opened only by `registry-verify`.
- After that, **PROPOSED:** scoring is repeated at most once every 12 origins, each time on all
  origins to date, and every scoring is reported, including unfavourable ones.
- Statistics, per target, horizon, model, variant and mode: the backtest's set and code (RMSFE,
  MAE, bias, relative RMSFE and MAE to the AR, Diebold-Mariano against the AR with the
  Harvey-Leybourne-Newbold correction, weighted quantile loss, 80% interval coverage, PIT
  histogram, model confidence set at 90%).
- The comparison with the backtest (Q5) is made on relative RMSFE to the AR of the same mode,
  stationary variants, first-release outturns, per target and horizon and pooled across targets
  after standardising by target. The primary comparison sets the `live` record against the
  backtest's real-time results; the `realtime` record against the same backtest results is the
  like-for-like control, and the difference between the two live modes shows how much of any
  gap is due to the information set. With 12 origins the sampling error is large and is
  reported; no claim of confirmation or refutation is made from a single year without it.
- The 2020-01 to 2021-06 exclusion window of the backtest does not apply to the live record. No
  period of the live record is excluded after the fact.

## 10. Design changes since Gate 0

The design freeze was planned for this document, not for Gate 0. Changes made between Gate 0
(2026-11-17, commit 4dde5f0) and this text, each decided by the owner or recorded as a deviation
before or independently of the results it could affect (`docs/backtest.md`, Deviations 1 to 7,
and `STATUS.md`): the origin day (25th, strict information set); the OECD edition dating rule
(conservative); consumer spending in place of monthly GDP by industry and industrial production;
the Canadian core CPI definition (CPI-XFET); TiRex-2 added as a fifth model at Gate 0; the
live-data sources (Statistics Canada vectors); the numerical-validity guard and the dynamic
factor model's initialisation, both fixed on numerical validity alone after the first run; the
Canadian retail national series; TimesFM 3.0 added and retired. HUMAN GATE 4 was a plausibility
check; no design choice was changed in response to the backtest tables.

## 11. Amendments

After the freeze this file is never edited. If something must change (a source disappears, a
series is redefined by its publisher, a defect is found), the change is written, dated and
justified in `PREREGISTRATION_AMENDMENTS.md` before the first run it affects, and the hash of
that file enters every later manifest, so the ledger shows from which origin an amendment
applies. Forecasts already made are never recomputed or replaced.

## 12. Owner's checks before the first public ledger line

The owner approves, in this order: this text; the repository arrangements for the ledger;
enabling the schedule. Public promotion of the project (social media, public venues) needs the
owner's separate clearance and is not implied by any of these.
