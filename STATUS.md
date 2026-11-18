# STATUS

Last updated: 2026-11-18 (Phase 3 done; awaiting owner input before Phase 4). Repository: foundation-forecast (public GitHub
remote; data/ and registry/ are git-ignored and must never be committed).

## Where we are

| Phase | State |
| --- | --- |
| 0 Feasibility | **Done.** Gate 0 passed 2026-11-17 (see below). |
| 1 Repository and environment | **Done.** `uv sync --extra dev` + `uv run just check` passes from a fresh clone (ruff + 4 tests). Package `ffcast` with `data`, `models`, `bench`, `eval`, `registry` subpackages; `configs/default.yaml` + pydantic loader; CLI stubs. |
| 2 Vintage data layer | **Done.** `ffcast data` downloads 28 series (OECD editions, ECB RTD change logs, DBnomics mirror of StatCan 36-10-0431, Eurostat and Valet latest) into `data/raw/<source>/<date>/` with SHA-256 manifests and normalises them into one change-log table (`as_of`, `revised_view`, `first_appearance`). RTD rebuild matches all 122 ECB bulk vintage files. 25 tests pass incl. hypothesis property tests and 6 revision spot checks on real data (real-data tests skip without data). `ffcast quality` writes `docs/data_quality.md`. |
| 3 Models and benchmarks | **Done.** Three-stage smoke test at origin 2024-06-25 (`ffcast smoke`): all benchmarks and all five foundation models (Chronos-2, TimesFM 2.5, TiRex, TiRex-2, Moirai 2.0; 12 model-variant combinations) pass every sane-magnitude and step-1 alignment check on 11 targets (132 checks); step 1 refers to the same target period across models; reruns byte-identical. Realised conditioning sets in `data/smoke/<origin>/panels.json`; runtimes in `docs/model_cards.md`. Canadian core CPI blocked (no public scripted source). |
| 4 Backtest and scoring | Not started |
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
- OECD edition visibility rule: owner questioned the conservative rule; agent proposed that
  edition M be treated as visible at the 25th-of-M origin (`same_month_eve`: the edition is
  dated the eve of the origin). This is an assumption about OECD publication timing backed by
  edition content (docs/data_quality.md section 4); there is no published OECD schedule to
  check against. The conservative rule remains a config switch. **Pending owner confirmation.**
- Canadian data route: StatCan loads in the owner's browser after a Cloudflare challenge;
  scripted access still blocked on 2026-11-17 and 2026-11-18 (WDS, SDMX REST and the
  36100107-SDMX.zip all 403). Owner suggested the community MCP servers and the R package
  `cansim`: tested 2026-11-18, all blocked (details in `docs/probes/statcan.md` section 1.5);
  the hosted MCP instance on Render gets the same 403 from its own network, so the block is
  not specific to this machine. Remaining routes: owner-run browser downloads registered with
  `RawStore.register_manual`, or the DBnomics mirror + OECD. **Pending.**
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
- Phase 2: OECD edition M is dated the 24th of M, the eve of the origin (`oecd_edition_rule: same_month_eve`).
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

1. **StatCan is unreachable to scripts.** Every www150.statcan.gc.ca path (WDS API, bulk
   zips) returns a Cloudflare JS challenge to curl, Python and WebFetch from this machine.
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
- StatCan access route (browser test by the owner, or accept mirror + OECD).
- Chrome extension was not connected in this session, so the agent could not run the
  browser test itself. Internet Archive downloads were denied by the session's permission
  classifier and were not retried.
- Decisions needed before Phase 4: (1) Canadian core CPI: supply a StatCan 18-10-0004 extract
  by hand (registered through `RawStore.register_manual`) or drop the target; (2) OECD
  edition rule: the content evidence bounds the edition CUT date (edition 202104 was cut on or
  after 21 April 2021), not the publication date; both rules (`same_month_eve`,
  `conservative`) can be run as variants.
- Repository visibility: planning and probe docs are on a public remote; PLAN.md Gate 5
  expects private code. Owner to decide before Phase 1.

## Environment facts

Windows 11, 24 cores, 32 GB RAM, RTX 3080 (unused), about 379 GB free. uv 0.11.7.
Python 3.12.13 (uv-managed). WSL Ubuntu available with make, python 3.14, 15 GB RAM.
