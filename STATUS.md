# STATUS

Last updated: 2026-11-17 (end of Phase 0). Repository: foundation-forecast (public GitHub
remote; data/ and registry/ are git-ignored and must never be committed).

## Where we are

| Phase | State |
| --- | --- |
| 0 Feasibility | **Done, awaiting HUMAN GATE 0.** `docs/feasibility.md` written; every PLAN.md section-3 row marked. |
| 1 Repository and environment | Not started |
| 2 Vintage data layer | Not started |
| 3 Models and benchmarks | Not started |
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

## Decisions taken by the agent (owner may overturn)

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
8. **Canadian headline CPI is unrevised** (verified across 33 OECD editions), as assumed.

## Blocked or needing the owner

- HUMAN GATE 0 decisions: see `docs/feasibility.md` section 5.
- StatCan access route (browser test by the owner, or accept mirror + OECD).
- Chrome extension was not connected in this session, so the agent could not run the
  browser test itself. Internet Archive downloads were denied by the session's permission
  classifier and were not retried.
- Items still open from the first response: OpenTimestamps stub in the dry run, GPU use,
  quarterly frequency of the consumer-spending target.

## Environment facts

Windows 11, 24 cores, 32 GB RAM, RTX 3080 (unused), about 379 GB free. uv 0.11.7.
Python 3.12.13 (uv-managed). WSL Ubuntu available with make, python 3.14, 15 GB RAM.
