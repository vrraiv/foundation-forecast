# STATUS

Last updated: 2026-11-19 afternoon (TimesFM 3.0 added by owner decision, backtested, scored, its tables published in `docs/results_backtest_2026-11-19.md`, then retired by owner decision: five foundation models go forward. Owner decisions the same day: repository visibility, licences, Canadian retail live series = StatCan v1446870183, `combo_fm` unchanged. Owner started Phase 5 the same day; it was built, trialled, approved at HUMAN GATE 5 and **the pre-registration is frozen as ledger line 0; the first live origin is 2026-11-25** (see "HUMAN GATE 5 PASSED" under "Blocked or needing the owner"). Cloud backup is a to-do. Phase 4 done 2026-11-18: 310 origins, all models, scored, Gate 4 passed as a plausibility check). Repository: foundation-forecast (public GitHub
remote; data/ and registry/ are git-ignored and must never be committed).

## Where we are

| Phase | State |
| --- | --- |
| 0 Feasibility | **Done.** Gate 0 passed 2026-11-17 (see below). |
| 1 Repository and environment | **Done.** `uv sync --extra dev` + `uv run just check` passes from a fresh clone (ruff + 4 tests). Package `ffcast` with `data`, `models`, `bench`, `eval`, `registry` subpackages; `configs/default.yaml` + pydantic loader; CLI stubs. |
| 2 Vintage data layer | **Done.** `ffcast data` downloads 28 series (OECD editions, ECB RTD change logs, DBnomics mirror of StatCan 36-10-0431, Eurostat and Valet latest) into `data/raw/<source>/<date>/` with SHA-256 manifests and normalises them into one change-log table (`as_of`, `revised_view`, `first_appearance`). RTD rebuild matches all 122 ECB bulk vintage files. 25 tests pass incl. hypothesis property tests and 6 revision spot checks on real data (real-data tests skip without data). `ffcast quality` writes `docs/data_quality.md`. |
| 3 Models and benchmarks | **Done.** Three-stage smoke test at origin 2024-06-25 (`ffcast smoke`): all benchmarks and all five foundation models of the time (Chronos-2, TimesFM 2.5, TiRex, TiRex-2, Moirai 2.0; 12 model-variant combinations; TimesFM 3.0 was added on 2026-11-19 and smoke-tested separately, 21 tasks, see `docs/model_cards.md`) pass every sane-magnitude and step-1 alignment check on 11 targets (132 checks); step 1 refers to the same target period across models; reruns byte-identical. Realised conditioning sets in `data/smoke/<origin>/panels.json`; runtimes in `docs/model_cards.md`. Canadian core CPI blocked (no public scripted source). |
| 4 Backtest and scoring | **Done. Results published: `docs/results_backtest_2026-11-18.md`. HUMAN GATE 4 passed 2026-11-18 (plausibility check only; the owner reviewed the tables visually, asked for three decompositions, found the tables plausible, and made no design change).** Harness, forecast store, outturns, scoring tables, Q2 splits, Q4 fixed-event regressions and the ECB SPF comparison are built and tested (`docs/backtest.md`); rules fixed in config and committed before the first run. Full run (`ffcast backtest --window all`: 311 origins 2001-01 to 2026-11, both input modes, all models) started 2026-11-18 07:52 local. SPF run and `ffcast score` follow when it ends. A benchmark-only scoring pass (2026-11-18 midday) found the dynamic factor model producing numerically broken forecasts (log-likelihood about -1e54, values up to 1e97) at about 60 origin-target cells, contaminating `combo_bench`. Diagnosed and fixed the same day on numerical validity alone (`em_initialization: false` repairs 52 of 52; validity guard for every model; `docs/backtest.md` Deviations); every benchmark cell is recomputed under `BENCH_CODE_VERSION` 2 with the foundation-model keys unchanged. **State at 15:28 local:** the harness stopped both jobs for machine-wide memory pressure. The model stage had finished (130 of 130 worker files, every worker ok, all five models over 310 origins) but its merge into the store had not run; the benchmark recompute had covered 269 of 310 origins. On those 269 the AR/BVAR/naive values are identical to the first run row for row, the DFM breakdown is gone (47 origins with absurd values -> 0; 53 formerly failing cells now estimate, none the other way; 169 pre-existing input-data failures remain and are recorded), and the validity guard caught 11 multivariate BVAR cells at the 2020-08..11 origins (`docs/backtest.md`, Deviations 2-3 and Run log). Stage 3 now merges one model at a time, and the cache works per (origin, target, input-mode) cell with keyed skips, which was needed for the core CPI second pass to run at all (`docs/backtest.md` Deviations 5). **Restarted 2026-11-18 evening after the owner's reboot, one job at a time:** stage 3 merged all 310 origins into the model store (74,670 model tasks ok, 0 errors, guard tripped on no model response); the benchmark recompute then finished the remaining 41 origins and re-keyed every skipped cell (50 min, 4 processes, nothing re-estimated elsewhere). Against the backup, all 310 origins now show AR/BVAR/naive identical row for row, DFM 57 cells repaired and none broken, 169 input-data errors unchanged, 11 BVAR guard trips. The second model pass ran 18:12-18:59: 4,570 model tasks (core CPI, real-time input, every model at all 310 origins; the two re-keyed trial origins of Chronos-2 and Moirai), all ok, 0 errors, nothing else recomputed; the model store now holds every model with status ok at every estimated cell and 1,704 keyed skips. Benchmark verify passed (`--verify` recomputes benchmarks only, no model: 5 random origins plus, by hand, two of the 41 post-reboot origins, 2024-10 and 2026-03, all identical to the store; recorded as `data/backtest/verify_<stamp>.json`, which the summary reads) and the final store comparison is unchanged (classical benchmarks identical to the backup on all 310 origins). **No job is running.** The owner took both decisions on the evening of 2026-11-18 (guard kept as configured; DFM coverage rule unchanged), so nothing was recomputed. `ffcast score` wrote the four main tables and then failed in the fixed-event regression (two scoring-code defects, fixed with tests, `docs/backtest.md` Deviations 6; no forecast or rule touched); `ffcast spf` ran clean (46 rounds, every worker ok); the bias table and the summary were regenerated at 22:17. **Gate 4 document: the 18 Nov `SUMMARY.md`, since 2026-11-19 kept at `data/backtest/_backup_before_timesfm3_20261119/tables/SUMMARY.md` (hash verified equal to the published `cd9ad787...`); `data/backtest/tables/SUMMARY.md` now holds the 19 Nov version with TimesFM 3.0** (private, 7 sections: bookkeeping, coverage, outturns, headline tables, views by plan question, fixed-event regressions, SPF comparison). Results stay out of this file and the docs until the owner passes Gate 4. The midday benchmark-only tables (broken DFM, pre-fix) were moved out of `data/backtest/tables/` to `data/backtest/_tables_bench_only_broken_dfm_20261118T1152/` so that the Gate 4 path holds only the final run's tables. Results stay under `data/backtest/` until Gate 4. |
| 5 Live registry | **LIVE. HUMAN GATE 5 passed 2026-11-19; pre-registration frozen as ledger line 0; first origin 2026-11-25.** Built and trialled 2026-11-19. `ffcast registry-init / registry-run / registry-verify` (`src/ffcast/registry/`, `docs/registry.md`): data snapshot per origin, two information sets (`realtime` = backtest rule, `live` = everything public at the run), salted commitments, manifest, hash-chained ledger, time-stamp placeholder, verify and byte-for-byte rerun. 32 registry tests incl. 17 tamper cases; 100 tests in all (registry tests force the offline time-stamp placeholder). Trial run for origin 2026-10-26 in a scratch folder: sealed, verified, rerun identical, and its `realtime` rows identical to the backtest store's for that origin (18,720 of 18,720) (`docs/registry.md`, Trial run). `PREREGISTRATION.md` is a DRAFT. **Switched on 2026-11-19 by the owner's instruction** (`registry.enabled: true`, real time-stamping, scheduled task registered, committed locally, not pushed); **no ledger entry exists and none can until the owner approves the pre-registration text and `ffcast registry-init` is run.** |
| 6 LLM forecasters | Deferred by the plan; not started. |
| 7 Public site | **Design stage (started 2026-11-26).** Owner decisions recorded in PLAN.md Phase 7: seven pages, static Vite and React site in `site/`, Cloudflare Worker hosting, per-origin backtest forecasts and outturns published with attribution, TimesFM 3.0 left off, live page without forecast charts. A private mock-up of the Overview and Results pages is with the owner for feedback; nothing is built in the repository or deployed yet. No live error, score or ranking is shown before 12 origins have outturns (PREREGISTRATION §9 as amended). |

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
  **Update 2026-11-19:** Statistics Canada told the owner the 403 on bulk downloads was
  unintended and has been fixed; the owner's plain `requests` call succeeds. Confirmed from this
  machine with plain curl and with Python `requests` 2.34.2 (default headers), same results: the static table zip (`/n1/tbl/csv/18100256-eng.zip`) and the
  WDS full-table link (`getFullTableDownloadCSV/36100431`) both answer; the SDMX data endpoint
  still returns 403 with a Cloudflare challenge (four attempts here; the owner saw the same on another device). The project does not use SDMX. No source in the config has been changed: the manual-zip
  fallback for CPI-XFET can be retired and direct parsing of 36-10-0431 is now feasible, both as
  the recorded source changes already planned.
- Models: four planned plus TiRex-2, plus TimesFM 3.0 from 2026-11-19. **Licence review by the
  owner 2026-11-19: Moirai 2.0 (CC-BY-NC-4.0), TiRex (NXAI Community License), TiRex-2
  (Apache-2.0) and TimesFM 3.0 (TimesFM Non-Commercial License v1.0) reviewed; the project's use
  is non-commercial and covered.** **TimesFM 3.0 added by owner decision 2026-11-19**, after the
  Gate 4 results had been seen: a recorded design change, not a response to any result
  (`docs/backtest.md` Deviations 7). It runs univariate and multivariate as its own model
  `timesfm3` in its own environment; `timesfm25` and every other stored forecast are untouched.
  `combo_fm` keeps its five members until the owner decides otherwise. **Run, SPF and scoring
  done 2026-11-19 11:58:** 310 origins, 22,410 tasks ok, 2 validity-guard trips; every other
  model's forecasts, scores, calibration tables and SPF points identical to the backup; only the
  model-confidence-set p-values move, because the model set changed. The regenerated
  `data/backtest/tables/SUMMARY.md` (19 Nov, with `timesfm3`) is **private: the owner's
  disclosure approval of 2026-11-18 covers the 18 Nov summary only**, which is preserved in
  `data/backtest/_backup_before_timesfm3_20261119/tables/` and published unchanged in
  `docs/results_backtest_2026-11-18.md`. **Owner decisions later on 2026-11-19: the 19 Nov tables
  are disclosed (`docs/results_backtest_2026-11-19.md`, verbatim copy, SHA-256 `51f62eb0...`);
  `combo_fm` keeps its original five members; TimesFM 3.0 is retired from all further work**
  (use probably within the licence, which excludes "production deployment", but not clearly so,
  and TimesFM 2.5 already represents the family). Retired means: `models.retired` in the config,
  not run by default, never in the live registry or the pre-registration's model list; its pinned
  entry, environment and stored results stay so the published tables remain reproducible.
- Repository visibility and gate strictness: **owner decision 2026-11-19.** The owner revised PLAN.md
  Gate 5 themselves (commit c53a6d5): a public repository, and even a deployed public site with
  everything the project does, needs no prior authorisation. What the owner must clear first is
  advertising the project on social media or in other public venues. The original gate text was
  agent-generated and stricter than the owner intended.
- OpenTimestamps stubbed in the dry run and no GPU use: **approved.**
- Consumer spending: quarterly; StatCan table 36-10-0107 (household final consumption
  expenditure), released on about the 28th of the second month after the quarter.

## Decisions taken by the agent (owner may overturn)

- Phase 5 (2026-11-19), all in `docs/registry.md` or marked PROPOSED in `PREREGISTRATION.md`:
  two information sets per run instead of one; `live` targets are the national `latest`
  series, joined to the vintage history by rescaling at the first national period; the
  registry's snapshot goes under `registry/`, never into `data/normalised`; ledger line =
  hash of the private manifest, manifest holds salted commitments (the salt also covers the
  status file); `combo_fm` is formed at scoring, not stored; a run refuses to seal an incomplete
  snapshot without an explicit flag; downloads are retried three times (this also changes
  `ffcast data`, behaviour on success unchanged); `registry.enabled` and the time-stamping mode
  are excluded from the design hash; amendments go into `PREREGISTRATION_AMENDMENTS.md`, whose
  hash enters every later manifest; three small extensions of backtest code for reuse
  (`fm_request` extracted, `stage3` takes a manifest, a `live` series id), backtest tests
  unchanged and passing.

- TimesFM 3.0 (2026-11-19, taken after the Gate 4 results had been seen; the owner asked only
  for the model to be included): (a) it runs univariate and multivariate, as Chronos-2 and
  TiRex-2 do, because the model supports several variates; (b) in the multivariate variant all
  variates enter as joint targets and variate 0 is returned, as for TiRex-2, not as past-only
  covariates; (c) inference options are the package defaults (no symmetric averaging, no
  z-normalisation, no positivity clamp), where TimesFM 2.5 runs with its flip-invariance and
  normalisation flags on; (d) it is not a member of `combo_fm`. All fixed before its first
  forecast. Dropping the multivariate variant only removes rows; changing (b) or (c) means
  rerunning this model (about 1.7 hours).

- Phase 2: every source is reduced to one change-log table (R/D rows dated by vintage), so
  `as_of` has a single semantics; full-snapshot sources are diffed into it with a 1e-9
  relative tolerance (OECD CSVs carry float noise such as 5.09999999999999).
- Phase 2: OECD edition M is dated the 1st of M+1 (`oecd_edition_rule: conservative`, owner
  decision 2026-11-18; the `same_month_eve` dating used until then is a variant).
  Evidence: in 334 Canadian editions only edition 202104 contained the previous month's CPI
  (released 2021-04-21); unemployment for M-1 (released first Friday) is present in 109
  editions. The conservative rule remains a config switch.
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

## To do

- **Publish each origin after its run (Amendment 1).** `uv run ffcast registry-publish <origin> --release`
  stages byte-identical copies under `registry/public/<origin>/`, refuses unless the origin is in
  the ledger, matches its commitments and has a real time-stamp proof, then creates the GitHub
  release `registry-<origin>`. Check with `python scripts/verify_published.py ledger/ledger.jsonl
  <downloaded assets>`. Done for 2026-11-25 on 2026-11-26 (release `registry-2026-11-25`,
  downloaded back and verified). Since 2026-11-26 (owner) the scheduled job publishes automatically:
  at every start, once the ledger is pushed, `ffcast registry-publish-pending` releases any sealed
  origin whose ledger line is on the remote and has no release yet (failure: PUBLISH FAILED,
  exit 7, retried the next day). It uses the `gh` login in the owner's Windows credential store,
  so the pre-December rehearsal (step 4 below) must also show that `gh` works from the task,
  particularly if the task is switched to "run whether user is logged on or not". The published `.ots` proofs are pending attestations; upgraded proofs can be added
  to a release later as extra assets without replacing anything.

Before the December origin:

- **The 2026-12-25 origin may run unattended.** The machine is expected to stay on but that
  cannot be guaranteed. Checked 2026-11-19: desktop on mains, sleep and hibernate never, wake
  timers on, so an undisturbed machine will run. The weak point is a restart (Windows Update or
  a power cut): the scheduled task runs only while the owner is logged in (logon type
  Interactive), so after a restart nothing runs until someone logs in. To do beforehand, each
  the owner's choice:
  1. Let the task run whether or not the owner is logged on (Task Scheduler, task properties,
     "Run whether user is logged on or not"; Windows asks for the account password and stores
     it; the agent must not handle that password). Then a restart does not stop the run.
  2. Pause Windows Update over the December origin (Settings, Windows Update, Pause; up to five
     weeks), so no update restarts the machine in the window.
  3. Optional: firmware setting to power on again after a power cut.
  4. Rehearse once beforehand: restart the machine, do not log in, and after 18:00 check
     that `registry/job.log` has that day's line. On an ordinary day the job only logs "nothing
     due", so the rehearsal costs nothing and tests the whole unattended path, including whether
     the job can still reach the settings in the user profile and push with stored credentials.
  5. Leave the repository clean and pushed.
  6. Do not count on a Claude session for remote repair. On 2026-11-21 the owner's Claude login
     on this machine expired while remote-control sessions about two days old were active;
     logins last about four weeks, so log in afresh shortly before the December origin. A
     session can still become unreachable for other reasons (restart, network), so remote
     repair remains a bonus, not a safeguard. The job itself uses no Claude login (it runs uv,
     git and restic only). The logins the job does use are the GitHub one stored by Git
     Credential Manager (ledger push) and the OneDrive sign-in (upload of the backup). If either
     lapses the forecasts are still made, sealed and time-stamped on time; the push is retried
     at every daily start, and the GitHub check reports a missing line from the 27th. The
     rehearsal in step 4 tests the push path only if a commit is waiting, so also confirm
     `git push` works without a prompt.
  If the run is missed anyway: the job retries at every later start, the GitHub check opens an
  issue from the 27th (mailed to the owner), and a run made later by hand is recorded as late.
  Under the frozen pre-registration a late `live` forecast, `live` being the primary mode, is
  reported separately and left out of the main tables, so a late December run costs that origin
  from the primary sample but not from the record. The origin is lost only if nothing runs
  before 2027-01-25. Decided 2026-11-25: the origin is kept at 25 December and the risk of a
  late run accepted (no amendment, no cloud fallback).

- **Noted for later, not decided (owner, 2026-11-19):** in two or three years the local storage
  of this project may be moved to cloud-only storage, or the project may be archived after one
  or two years. Sizes, what must stay local, what offloading would require of `registry-verify`,
  and an archiving checklist are in `docs/registry.md`, "Storage outlook and possible futures".
  The owner confirmed on 2026-11-19 that the backup opens with the password from their password
  manager and that the backup folder is kept on this device.

- **Cloud backup of the git-ignored work: DONE 2026-11-19 (owner request of the same day).**
  restic repository in a folder the OneDrive client syncs (a household account, not the
  owner's employer's), encrypted on this machine before anything is written there. Settings
  are project-specific user environment variables, `FFCAST_RESTIC_REPOSITORY` and
  `FFCAST_RESTIC_PASSWORD_FILE` (the file is outside the repository and outside OneDrive,
  readable by the owner's account only); the generic `RESTIC_*` names are not used, so another
  project's repository cannot be touched by accident. `scripts/registry_backup.ps1` backs up
  `registry/` in full and `data/` except `data/models/`, then runs `restic check`; the monthly
  job calls it after every run. `scripts/restic.ps1 <command>` is restic for this repository
  only. First backup: 4,344 files, 2.5 GiB read, 451 MiB stored. Restore test: the trial run and
  `registry/` restored to a scratch folder; `registry-verify` passes on both restored copies
  and the restored trial is identical to the original, file for file (232 files). (Both owner steps below were confirmed done the same evening.) Left for the
  owner: open the repository once with the password typed from the password manager, and mark
  the backup folder "Always keep on this device" in OneDrive. Without the password the backup
  is unreadable.

## Blocked or needing the owner

**Disclosure change, 2026-11-26 (owner).** Direct model outputs may be public in the repository and on the site, and the site may start early. The frozen pre-registration says in §7 that no forecast value is public, so the owner approved **Amendment 1** on 2026-11-26 (`PREREGISTRATION_AMENDMENTS.md`). It also narrows §9 to "the project computes no live score before 12 origins". Owner choices: the 2026-11-25 forecasts are published; the status file is published; the route is one GitHub release per origin (`registry-<origin>`), built by `ffcast registry-publish`. The 2026-12-25 manifest is the first to carry the amendment's hash. Checked: `registry-verify` does not compare `amendments_sha256`, and the file does not enter `design_hash`, so adding it does not disturb the 2026-11-25 origin. Exploration of model capabilities and fine-tuning goes to a separate repository, so that this one's lockfiles, configs and model pins stay as frozen.

- **HUMAN GATE 5 PASSED, 2026-11-19 (evening): the owner approved `PREREGISTRATION.md` and said
  to begin. THE DESIGN IS FROZEN.** Only the status header of the text was changed after the
  owner read it (draft -> approved; commit 92ba6f4). `ffcast registry-init` then wrote ledger
  line 0: pre-registration SHA-256 `68479cfc1edd7792bf341e21428ba64b85a122c6c6e37755147c9cf677066075`,
  entry hash `225d49cd827c86e7fcfe83f71fc6049c0d357ae891e1294400d3246dda20c30a`, recorded
  2026-11-20T01:25:16 UTC, time-stamped by three OpenTimestamps calendars (proof under
  `registry/prereg/proofs/`, pending; it can be upgraded to a Bitcoin attestation later).
  `registry-verify` and the public `scripts/check_ledger.py` both pass. Pushed with the Phase 5
  commits so that the ledger and its check workflow are public before the first origin.
  **From here on:** `PREREGISTRATION.md` and the design part of `configs/default.yaml` do not
  change (a test compares the text's design hash with the config); a necessary change is
  written into `PREREGISTRATION_AMENDMENTS.md` before the first run it affects. No score, error
  or ranking is computed from live forecasts before 12 origins have outturns. A live run needs a
  clean committed tree, so commit or stash other work before the 25th.
  **First live origin: 2026-11-25**, run by the scheduled task at 18:00 local time (about 30
  minutes; the machine must be on and the owner logged in). Afterwards the job verifies,
  commits and pushes the ledger line, and the GitHub workflow checks it.
  Still open, not blocking: the backup (owner: rclone, OneDrive login, restic password; then
  `scripts/registry_backup.ps1`); the two vintage-source switches are off the table until an
  amendment says otherwise.
- **(Earlier the same evening) HUMAN GATE 5, state before approval. One thing was pending: the owner's approval of
  `PREREGISTRATION.md`** (the owner reads it tonight; a copy was sent to them). Until
  `ffcast registry-init` has hashed the approved text into ledger line 0 (the freeze), no live
  run can happen: the scheduled job finds nothing due. Done on the owner's instruction:
  - Canadian headline CPI in the primary `live` mode now comes from StatCan vector 41690973
    (identical to the Bank of Canada mirror on all 382 common months; history from 1914, so no
    join to OECD history is needed for it any more). The pseudo-vintage base of the backtest
    rule stays `valet:V41690973` and the pipeline downloads it separately; the backtest cache
    keys of that target are unchanged (checked). The DBnomics switch is not made.
  - `registry.enabled: true`, `registry.opentimestamps: ots`.
  - Scheduled task "foundation-forecast registry" registered (daily 18:00, start when
    available); see `docs/registry.md`.
  - Phase 5 committed locally. **Not pushed.** Consequences until the owner pushes or says to:
    the GitHub ledger workflow does not exist on the remote, and the job will not push a ledger
    line while other local commits are ahead (it logs "NOT PUSHED ... the owner pushes").
  Open besides the text: the backup (owner sets up rclone and the restic password tonight or
  tomorrow; then `scripts/registry_backup.ps1`).
  **DBnomics timeliness (owner's question):** unknown. DBnomics indexes the provider daily, and
  its copy of table 36-10-0431 was last changed on 2026-09-30, 33 days after the release of
  2026-08-28; that is one observation and an upper bound, not a measured lag. It matters only
  for the `realtime` control mode of Canadian GDP and consumption (if the mirror is stale beyond
  130 days the rule falls back to OECD editions and records it). First real test: the Q3
  release at the end of November against the 2026-12-25 origin. If the mirror proves late, the
  direct StatCan file (already downloaded at every run) becomes the source by amendment.
  After the owner approves the text: `uv run ffcast registry-init`, commit nothing else, and
  the first origin is 2026-11-25 (the job runs it at 18:00 that day).
- **HUMAN GATE 5, further answers (2026-11-19, later):** item 3: **the ledger lives in this
  repository with its own workflow, and needs a fallback** because scheduled GitHub workflows
  are unreliable in the owner's experience. Built, not switched on: the local job
  `scripts/registry_job.ps1` (daily start, acts only when an origin is due, retries by
  construction, pushes the ledger file only), the public check `scripts/check_ledger.py`, and
  `.github/workflows/ledger.yml` (chain and append-only on push; presence check on eight days a
  month; opens an issue on failure); `ffcast registry-status`. Layers and what remains a single
  point of failure are in `docs/registry.md`. Item 2 was explained again to the owner (the two
  switches are plumbing, not a move to OECD data; under the primary `live` mode every Canadian
  target already comes from Statistics Canada except headline CPI, which comes from the Bank of
  Canada's mirror of the same StatCan vector). **Still open:** approval of the pre-registration
  text; item 2; the owner's go-ahead to commit, enable and register the task; rclone and the
  restic password for the backup.
- **HUMAN GATE 5, owner's answers of 2026-11-19 (evening):** (1) **`live`, everything public
  at the run, is the primary mode**; the inconsistency with the backtest is accepted, and doing
  worse than the backtest is then the stronger signal; `realtime` stays as the like-for-like
  control. Draft updated (sections 3 and 9). (4) **Real OpenTimestamps stamping approved**;
  implemented through the client's library (the command-line client fails on Windows), tested
  once on the trial entry's hash, accepted by three calendars. (5) **Schedule option C and the
  restic backup to OneDrive approved** as recommended; neither is set up yet (the job script
  waits for the answer on item 3, the backup for the owner's rclone login and password).
  **Still open:** approval of the pre-registration text as a whole (the owner asked when the
  freeze is: it is the moment `ffcast registry-init` hashes the text into ledger line 0, which
  must come before the first live run, so in practice just before the first origin; the config
  and the text can change freely until then and only by amendment after); item 2 (source
  switches; proposal: neither before the freeze); item 3 (where the public ledger file lives and
  who pushes it; the owner asked for an explanation).
- **HUMAN GATE 5 (reached 2026-11-19).** The owner approves, in this order (PLAN.md as revised
  by the owner): the pre-registration text; creation of any remote repository (public);
  enabling the schedule. For decision, with the agent's proposal in each case:
  1. `PREREGISTRATION.md` (draft). Its PROPOSED items: `realtime` as the primary mode for Q5 and
     `live` alongside (the owner asked on 2026-11-19 whether the backtest rule yields incoherent
     information sets; answer in `docs/backtest.md`, Not covered: no unknown value, but
     multivariate panels mix vintage ages, while `live` is coherent as of the run; this bears on
     which mode is primary); run time 18:00 America/Toronto; treatment of late runs; sealing
     without a source that is down all day; `live` outturns from the registry's own monthly
     snapshots; first scoring after 12 origins with outturns, then at most once every 12.
  2. Whether the two planned Statistics Canada source switches happen before the freeze (they
     change sources the text names): Canadian headline CPI from the Bank of Canada's Valet
     mirror to StatCan vector 41690973 (identical values, verified), and GDP/consumption
     vintages from the DBnomics mirror to direct parsing of 36-10-0431 (feasible since StatCan
     fixed bulk downloads; identity still to be verified). The second changes backtest cache
     keys for two targets and would require recomputing them; the retired TimesFM 3.0 would not
     be rerun (`docs/backtest.md`, Deviations 7). The CPI switch cannot be done for the live
     source alone: the pseudo-vintage base `valet:V41690973` is downloaded only because it is
     the `latest` source, so base and live source must move together, which changes that
     target's cache key and forces its recompute too. Agent's proposal: neither switch before
     the freeze. The text then names the Valet mirror (identical values to the StatCan vector)
     and the DBnomics mirror, as the backtest used them; a later switch would be an amendment.
  3. Where the public ledger lives (this public repository under `ledger/`, or a separate
     ledger-only repository) and whether the scheduled job pushes it or the owner does.
  4. Real OpenTimestamps stamping (sends each ledger line's hash, and nothing else, to public
     calendar servers; needs the `opentimestamps-client` package; never run so far).
  5. Schedule: options A, B, C in `docs/registry.md`; proposal C (Windows Task Scheduler here
     plus a monthly reminder). Backup: restic to OneDrive as proposed there; needs the owner's
     rclone login and password choice.
  6. To switch on after approval: set `registry.enabled: true`, commit, `ffcast registry-init`,
     then the first run. **The next origin is 2026-11-25**; if the text is approved and the
     registry enabled before then, it can be the first live entry, otherwise 2026-12-25.

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
  check kernel pools (RAMMap) before blaming the workers. **Recurred 2026-11-18 15:28:** the
  Claude Code harness stopped both background jobs for critical memory pressure while the session
  was idle; afterwards, with no Python process running, free physical memory was about 10 GB of
  32 GB. The harness behaviour can be disabled by starting Claude Code with
  `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`. Measured at 17:15 with no backtest running:
  22.4 GB of 31.9 GB physical in use, and it is ordinary processes, not a hidden holder (an
  earlier note claiming 20 GB outside any process was wrong; it looked at the top six processes
  only). 422 processes sum to 23.3 GB of working set: 16 Claude processes 3.6 GB (desktop app plus
  three other Claude Code sessions from 15, 16 and 18 Nov), VS Code 2.1 GB, Chrome 2.0 GB, ChatGPT
  1.9 GB, svchost 1.3 GB, OneDrive 0.9 GB, Steam 0.6 GB, and a `courtdelay fetch` job from another
  project; kernel pools 4.7 GB; memory compression 2.2 GB (a sign of pressure). Commit charge
  40 GB of 128 GB, so the 126 GB commit episode has not recurred. Headroom for the restart is
  about 9.5 GB free plus whatever the owner closes; the stopped jobs together had been using
  roughly 5 benchmark processes plus one model worker for hours, and the stop came at the moment
  stage 3 (then an in-memory merge of six million rows) was about to start.

- **Restart (done, 2026-11-18 evening):** the owner rebooted (21 GB of 32 free afterwards, with
  another Claude session's job still running) and approved resuming one job at a time. Runbook
  all seven runbook steps (`docs/backtest.md`, Run log) completed by 22:17; nothing is running,
  so the reboot below can happen whenever the other session's job has finished. (Hardware note closed 2026-11-19: the memory's XMP/D.O.C.P. profile is enabled again,
  all four modules run at 3600 MT/s and Windows sees the full 32 GB.)
- **Validity guard scope:** in the recomputed benchmarks the guard caught no DFM cell but 11
  multivariate BVAR cells at the 2020-08..11 origins (pandemic shock through the VAR; magnitudes
  stay in the private store). Owner to choose before scoring: keep the magnitude rule for every model (current
  config, recommended: the rule was fixed before these cells were seen and the ex-COVID split
  exists), or limit the guard to non-finite values and the log-likelihood floor. **Decided
  2026-11-18 evening: keep the guard as configured** (`docs/backtest.md` Deviations 3 has the
  evidence shown to the owner).
- **DFM input-data failures (169 cells, pre-existing):** caused by predictor columns with almost
  no in-vintage observations at the origin (Bank of Canada policy rate 2009-10, 10-year yield
  2001, exchange rate 2017; `docs/backtest.md` Deviations 2). Owner to choose: leave as recorded
  errors, or give the DFM the BVAR's minimum-coverage rule (`BENCH_CODE_VERSION` 3, full
  benchmark recompute, changes DFM inputs in some healthy cells too). Final count 190 of 5,736
  DFM cells; 180 are the start-up year of each Valet series (yield 2001, overnight target 2009,
  USD/CAD 2017), 10 are an untraced empty euro-area panel at the 2021-09/10 origins. **Decided
  2026-11-18 evening: leave as recorded errors, the rule is not changed now.**
- **HUMAN GATE 4 passed (2026-11-18, plausibility only).** The owner reviewed
  `data/backtest/tables/SUMMARY.md`, had three cells decomposed (BVAR and DFM at horizon 1 on
  Canadian retail and consumption: pandemic nowcast effects, correct; levels-variant fixed-event
  slopes: regressor without variance, uninformative), and found the tables plausible. Standing
  rules from the owner: Gate 4 is a plausibility check only, no design change at this gate, no
  tuning in response to results at Gate 4 or after. **Disclosure approved by the owner
  (2026-11-18): everything in `SUMMARY.md`.** A verbatim copy with Gate 4 reading notes is
  `docs/results_backtest_2026-11-18.md` (SHA-256 of the summary `cd9ad7875bc1dc98cd6e22fa76188be678393010ba1aec47d47970361cbedcef`). The forecasts and
  the CSV tables stay private under `data/`.
- **Design freeze record (owner decision 2026-11-18):** kept as PLAN.md plans it, in
  `PREREGISTRATION.md` at Phase 5; the freeze is not redated to Gate 0. Verification done for
  the record: the Gate 0 commit is 4dde5f0 (PLAN.md unchanged since); the config file was created
  three minutes later (c736472) and elaborated before the first run (dc4bb6c); the
  design-relevant changes since Gate 0 (OECD edition rule, core CPI redefinition, live-data
  sources, validity guard, DFM initialisation; all owner-decided or recorded deviations) are
  listed in `docs/backtest.md` and will be cited in `PREREGISTRATION.md`.
- HUMAN GATE 0 decisions: see `docs/feasibility.md` section 5.
- StatCan: two planned source changes after the running backtest ends, each recorded and each
  forcing a recompute of the affected target only: headline CPI base Valet -> StatCan vector
  41690973 (values identical, verified), and GDP/consumption vintages DBnomics mirror -> direct
  parsing of 36-10-0431 (to be verified identical first). Retail: StatCan's Fisher volume index
  differs from the OECD volume index used for the vintages (definitional; owner to choose the live
  target definition for Phase 5).
  **Finding 2026-11-19:** the OECD series is still published (live value for 2026-08) and is a
  rebased copy of another StatCan series in the same table: 20-10-0067, retail trade [44-45],
  "Retail sales at 2017 constant prices (Unchained Laspeyres Index)", vector v1446870183. Over the
  116 common months (2017-01 to 2026-08) month-on-month log growth differs by at most 0.0001
  (rounding) and the level ratio is constant (OECD rebases to 2015 = 100). The config's live
  vector v1446870181 is the chained Fisher volume index, which is the series that differs. The
  OECD labels the activity G47 "except motor vehicles" but the data match total retail including
  motor vehicle dealers. The OECD dataflow states no source per series (methodology attribute
  "National" only). Choosing v1446870183 as the live source would make the live target the same
  definition as the backtest vintages. **Owner decision 2026-11-19: the live Canadian retail
  series is StatCan v1446870183.** Config switched (`latest` is in no cache key, so nothing is
  recomputed). The vector is in millions of 2017 dollars, the OECD vintages are an index
  (2015 = 100): the target is scored in log differences, where the scale drops out, and any
  level use in the live phase must rescale on the overlap.
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
- Repository visibility: settled 2026-11-19 (see Decisions taken by the owner): public code and a
  public site are allowed; only public promotion needs the owner's prior clearance.

## Environment facts

Windows 11, 24 cores, 32 GB RAM, RTX 3080 (unused), about 379 GB free. uv 0.11.7.
Python 3.12.13 (uv-managed). WSL Ubuntu available with make, python 3.14, 15 GB RAM.
