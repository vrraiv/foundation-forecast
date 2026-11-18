# STATUS

Last updated: 2026-11-18 (Phase 4 full backtest running; StatCan WDS route for Canadian latest data; DFM defect under diagnosis, see Phase 4 row). Repository: foundation-forecast (public GitHub
remote; data/ and registry/ are git-ignored and must never be committed).

## Where we are

| Phase | State |
| --- | --- |
| 0 Feasibility | **Done.** Gate 0 passed 2026-11-17 (see below). |
| 1 Repository and environment | **Done.** `uv sync --extra dev` + `uv run just check` passes from a fresh clone (ruff + 4 tests). Package `ffcast` with `data`, `models`, `bench`, `eval`, `registry` subpackages; `configs/default.yaml` + pydantic loader; CLI stubs. |
| 2 Vintage data layer | **Done.** `ffcast data` downloads 28 series (OECD editions, ECB RTD change logs, DBnomics mirror of StatCan 36-10-0431, Eurostat and Valet latest) into `data/raw/<source>/<date>/` with SHA-256 manifests and normalises them into one change-log table (`as_of`, `revised_view`, `first_appearance`). RTD rebuild matches all 122 ECB bulk vintage files. 25 tests pass incl. hypothesis property tests and 6 revision spot checks on real data (real-data tests skip without data). `ffcast quality` writes `docs/data_quality.md`. |
| 3 Models and benchmarks | **Done.** Three-stage smoke test at origin 2024-06-25 (`ffcast smoke`): all benchmarks and all five foundation models (Chronos-2, TimesFM 2.5, TiRex, TiRex-2, Moirai 2.0; 12 model-variant combinations) pass every sane-magnitude and step-1 alignment check on 11 targets (132 checks); step 1 refers to the same target period across models; reruns byte-identical. Realised conditioning sets in `data/smoke/<origin>/panels.json`; runtimes in `docs/model_cards.md`. Canadian core CPI blocked (no public scripted source). |
| 4 Backtest and scoring | **In progress.** Harness, forecast store, outturns, scoring tables, Q2 splits, Q4 fixed-event regressions and the ECB SPF comparison are built and tested (`docs/backtest.md`); rules fixed in config and committed before the first run. Full run (`ffcast backtest --window all`: 311 origins 2001-01 to 2026-11, both input modes, all models) started 2026-11-18 07:52 local. SPF run and `ffcast score` follow when it ends. A benchmark-only scoring pass (2026-11-18 midday) found the dynamic factor model producing numerically broken forecasts (log-likelihood about -1e54, values up to 1e97) at about 60 origin-target cells, contaminating `combo_bench`; diagnosis is running on numerical validity only, and the remedy, the recompute of the benchmarks and the recorded deviation follow. Results stay under `data/backtest/` until Gate 4. |
| 5 Live registry | Not started |

## Decisions taken by the owner so far (2026-11-17)

- Repository name stays `foundation-forecast`; planning docs committed; pushing to the
  existing GitHub remote is allowed. The remote is **public**, so forecasts, salts and
  data never enter git.
- The "revised" view will be a pinned, content-hashed snapshot (not "latest at run time").
- Origin-day collisions to be checked before fixing the origin day (done; see feasibility).
- The registry rerun test reuses the stored private salt.
- Monthly GDP by industry (Canada) to be replaced by consumer spending (household final
  consumption). Note: this is quarterly, not monthly.

## HUMAN GATE 0 outcome (2026-11-17, owner)

- Targets per economy: real GDP (Q), headline inflation (M), unemployment rate (M), retail
  volume (M), household final consumption (Q). Core inflation kept as a lag-only series,
  excluded from the real-time vs revised comparison. **Approved.**
- Vintage sources: precise-dated where live (StatCan GDP tables, RTD GDP/HICP/unemployment/
  consumption), OECD editions elsewhere, OECD editions for IP and retail in both economies.
  **Approved.**
- Window: 2015-01 to present primary; 2001-01 to 2014-12 pre-registered extension where
  in-vintage history is at least 10 years. **Approved.**
- Origin: 25th or next business day, information set strictly before the origin date.
  **Approved.**
- OECD edition visibility rule: **decided 2026-11-18: `conservative`** (edition M dated the 1st
  of M+1, first used at the origin of M+1). The content evidence (edition 202104 contains March
  2021 CPI, released 21 April 2021) bounds the edition cut date from below and says nothing
  about publication, so the owner declined to rest the same-month rule on a margin of at most
  three days. `same_month_eve` stays available as a variant. The OECD staleness limit moved from
  45 to 60 days by the fixed principle "tolerate one missing edition" (ages at origins are 24-26
  days normally, 52-57 with one edition missing, 85-87 with two; `configs/default.yaml`). Under
  the new dating, compared with the old one (sweep of 311 origins 2001-2026): the resolved
  source is unchanged at every origin for the RTD- and pseudo-vintage targets; for the
  OECD-sourced targets the same source resolves but one edition later, so the newest observed
  period is one month older at most origins (CA unemployment 120 of 143 origins since 2015, CA
  retail 128 of 139, EA retail 119 of 143); around missing editions the "no source" origins move
  by one month (CA retail 3 origins, EA retail 1) and for the pre-2012 Canadian GDP/consumption
  fallback (OECD quarterly editions, sparse before 2012) 42 origins swap between "fallback" and
  "no source". Smoke at 2024-06-25: step 1 moved from 2024-04 to 2024-02 for CA retail (edition
  202405 is missing, so the June origin sees edition 202404) and from 2024-05 to 2024-04 for EA
  unemployment (OECD fallback period).
- Canadian data route: **owner decision 2026-11-18: StatCan as the source whenever feasible.**
  The WDS JSON REST API (`/t1/wds/rest/`) answers an identified client from this machine, while
  the static full-table zips and the SDMX service are challenged by Cloudflare (owner's
  observation, confirmed; `docs/probes/statcan.md` 1.6-1.7). New source `statcan_wds` fetches
  single vectors; the Canadian `latest` series now come from StatCan vectors (GDP, consumption,
  unemployment rate, retail volume, CPI-XFET with the owner zip as fallback) and agree exactly with
  the vintage sources where the definitions coincide. Headline CPI stays on Valet until the running
  backtest ends (its pseudo-vintage base enters the cache key); switching it to
  `statcan:18100004:v41690973` is the planned source change afterwards. The real-time GDP zip
  36-10-0431 also downloaded once (17:12 UTC); the DBnomics mirror remains the vintage source of
  record for the backtest, and direct parsing is the second planned change. Earlier routes
  (community MCP servers, `cansim`, GitHub Actions runner with retries, 36 attempts) all 403; the
  owner's browser-identified client fails on 13 and 18 Nov too, so the User-Agent is not the
  explanation. **Resolved for latest data; vintage-source switches pending the run.**
- Models: four planned plus TiRex-2; TimesFM 3.0 excluded. Owner reviewing Moirai and TiRex
  licences. **Approved subject to licence review.**
- Repository visibility and gate strictness: owner will revise PLAN.md gates. **Pending.**
- OpenTimestamps stubbed in the dry run and no GPU use: **approved.**
- Consumer spending: quarterly; StatCan table 36-10-0107 (household final consumption
  expenditure), released on about the 28th of the second month after the quarter.

## Decisions taken by the agent (owner may overturn)

- Phase 2: every source is reduced to one change-log table (R/D rows dated by vintage), so
  `as_of` has a single semantics; full-snapshot sources are diffed into it with a 1e-9
  relative tolerance (OECD CSVs carry float noise such as 5.09999999999999).
- Phase 2: OECD edition M is dated the 1st of M+1 (`oecd_edition_rule: conservative`, owner
  decision 2026-11-18; the `same_month_eve` dating used until then is a variant).
  Evidence: in 334 Canadian editions only edition 202104 contained the previous month's CPI
  (released 2021-04-21); unemployment for M-1 (released first Friday) is present in 109
  editions. The conservative rule remains a config switch. Owner confirmation still pending.
- Phase 2: an edition that is empty or whose newest observation is more than 12 months old
  would be dropped as a broken vintage; none occurred in the downloaded data.
- Phase 2: ECB "Replace" rows with an empty value are treated as deletes dated VALID_FROM.
- Phase 2: DBnomics rows are labelled `dbnomics`, never `statcan`; the two providers are never
  merged into one history.
- Phase 2 follow-up: a primary vintage source is used only if its latest vintage is at most
  `max_staleness_days` old (RTD 100 days), otherwise the fallback; this moves euro-area
  unemployment to OECD editions for origins from 2024-07 to 2025-07 (RTD gap).
- Phase 2 follow-up: Canadian headline CPI and euro-area core HICP get pseudo-vintages (month m
  visible at the origin of m+1) from the latest Valet / Eurostat snapshot; Canadian core CPI is
  blocked.
- Phase 3: one uv project per model under `envs/`; workers never import `ffcast` and receive
  only `as_of` output (process-boundary enforcement of the no-look-ahead rule); workers get a
  minimal, fixed environment, not the parent's. TiRex is loaded from the pinned checkpoint file
  through its model registry because `tirex.load_model` accepts only Hugging Face ids.
- Phase 3: conditioning variables for multivariate models are selected by a coverage/staleness
  rule in `Panel.multivariate`; the BVAR drops the gappiest column until a balanced sample of
  10 observations per parameter exists; DFM limited to 12 monthly variables and 100 EM
  iterations after measuring 35-40 s per fit with 22 variables.

- Windows, not WSL, for the toolchain: all five models install and run on Windows CPU;
  Windows has 32 GB RAM vs 15 GB in WSL. Task runner will be a `justfile` (neither
  `make` nor `just` is installed on Windows; `just` will be added as a dev dependency).
- Python 3.12 via `uv` (system Python is 3.14, too new for the model packages).
- One virtualenv per foundation model (Moirai's `uni2ts` pins torch<2.5 and numpy 1.26).
- Probe venvs and toy scripts live in the session scratchpad, not the repo.

## Where reality differed from the plan

1. **StatCan file downloads are challenged; the JSON API answers.** From 2026-10 the static
   zips and SDMX paths return a Cloudflare challenge to scripts (intermittently also the API,
   which otherwise answers an identified client; resolved for latest data on 2026-11-18).
   Structure verified only via the DBnomics mirror. Six of the 19 real-time tables are
   inactive (incl. both retail tables), one CPI core table is stale. No vintage table for
   LFS unemployment or CPI ex food and energy.
2. **ECB RTD**: API serves vintages from 2001 (plan said 2015+); vintages are 8 per year
   ECB snapshots, not Eurostat releases; IP and retail keys stale since Oct 2025; no
   HICP-ex-energy-food-alcohol-tobacco key; 86 of 174 monthly keys stopped updating
   between Nov 2024 and Aug 2025.
3. **OECD revisions dataset** is far better than expected: monthly editions for all six
   measures, Canada from Feb 1999 with no gaps; euro area as an EA18/19/20 splice. But no
   core inflation, month-level timing only, and index bases change across editions.
4. **Core inflation has no vintage source in either economy.**
5. **Eurostat** HICP moved to dataset `prc_hicp_minr` (dimension `coicop18`); the datasets
   named in the plan are frozen at 2025-12.
6. **MACROCAST** (arXiv 2606.28670) is a new vintage-consistent model on FRED-MD, not a
   real-time-vs-revised evaluation, and does not include TimesFM. Plan section 1 should be
   reworded.
7. **Models**: TiRex's licence is the NXAI Community License (not OSI); PyPI `tirex` is an
   unrelated package; Moirai 2.0 is CC-BY-NC-4.0; the `timesfm` package is now 3.0.x but
   still ships the 2.5 class. Newer weights exist: TiRex-2 (Apache-2.0, multivariate) and
   TimesFM 3.0 (non-commercial). No model publishes a real-data training cutoff.
8. **Canadian headline CPI is unrevised** in 2024-2026 (33 OECD editions) and spot-checked
   for one month across all editions since 1999, as assumed. Full-history check in Phase 2.
9. **In-vintage history** is long for Canada (40 years in the 2001 edition) but short for the
   euro area (23 quarters of GDP in the March 2001 edition), so 2015 stays the recommended
   primary window with 2001-2014 as a pre-registered extension.
10. **Bank of Canada Valet API** (not in plan) is a working live feed for Canadian CPI and core
    measures; DBnomics does not mirror the regular StatCan CPI, LFS or retail tables.
11. **TiRex-2 weights** changed on 2026-07-02 and files were re-uploaded 2026-10-06, so its
    Q2 boundary is ambiguous; its macro training-data exposure is a model-card tag only.

## Blocked or needing the owner

- **Machine memory (cleared 2026-11-18, cause not identified):** earlier in the day Windows
  reported about 126.7 GB of a 131 GB commit limit in use while all processes together held
  about 29 GB, and the TimesFM worker (925 MB checkpoint) crashed with an access violation at
  load. Between sessions, and without a reboot (last boot 2026-11-15), commit charge fell to
  about 36-38 GB with process commit unchanged at 29 GB; the limit moved to 127.9 GB
  (system-managed pagefile). The drop coincided with the previous Claude Code session
  process crashing, but that process's own commit was small, so the roughly 90 GB was never
  attributable to a visible process and the holder is unknown. TimesFM then ran through the
  orchestrator without incident. The memory pre-flight (workers refuse to start below 2x the
  largest weight file + 600 MB of free commit) stays in place; recurrence cannot be ruled
  out. If it recurs, compare `Get-Process` commit totals with `Win32_OperatingSystem` and
  check kernel pools (RAMMap) before blaming the workers.

- HUMAN GATE 0 decisions: see `docs/feasibility.md` section 5.
- StatCan: two planned source changes after the running backtest ends, each recorded and each
  forcing a recompute of the affected target only: headline CPI base Valet -> StatCan vector
  41690973 (values identical, verified), and GDP/consumption vintages DBnomics mirror -> direct
  parsing of 36-10-0431 (to be verified identical first). Retail: StatCan's Fisher volume index
  differs from the OECD volume index used for the vintages (definitional; owner to choose the live
  target definition for Phase 5).
- Chrome extension was not connected in this session, so the agent could not run the
  browser test itself. Internet Archive downloads were denied by the session's permission
  classifier and were not retried.
- Canadian core CPI: **redefined 2026-11-18 (owner approval)** as CPI-XFET (all-items excluding
  food, energy and the effect of indirect taxes, NSA) from StatCan 18-10-0256, supplied by the
  owner as a browser download (`data/raw/statcan-manual/2026-11-18/18100256-eng.zip`, sha256
  515424b0...), loaded through `latest: {source: statcan_manual, ...}` with pseudo-vintages. The
  original definition (all-items excluding food and energy, 18-10-0004) had no public scripted
  source. Valet STATIC_CPIXFET agrees with the file at every overlapping month and is the live
  cross-check. Live-phase updates: WDS vector 1675033092 (equal to the file at all 514 months),
  with the owner's zip as fallback when the API is challenged. No target is blocked any more.
- Repository visibility: planning and probe docs are on a public remote; PLAN.md Gate 5
  expects private code. Owner to decide before Phase 1.

## Environment facts

Windows 11, 24 cores, 32 GB RAM, RTX 3080 (unused), about 379 GB free. uv 0.11.7.
Python 3.12.13 (uv-managed). WSL Ubuntu available with make, python 3.14, 15 GB RAM.
