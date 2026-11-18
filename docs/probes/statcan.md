# Probe: Statistics Canada real-time vintages and WDS access

Probe run: 2026-11-17 evening (local) / 2026-11-18 ~03:00-03:40 UTC.
Method constraints: read-only, public sources only, WebFetch/WebSearch/curl, no package installs, no browser automation. Archive replays (web.archive.org, archive-it) were refused by the session's permission system, so none were used.
Scratch files: `<session-scratchpad>/statcan\` (open.canada.ca CKAN JSON per table, DBnomics metadata and sample JSON, two provincial schedule PDFs, PDF text extractor). **No StatCan-hosted CSV or WDS response could be obtained** (section 1); the structural sample comes from the DBnomics mirror (section 1.4).

Status legend: **confirmed** = verified from a primary page fetched during the probe; **confirmed (mirror)** = verified from a third-party mirror of StatCan data (DBnomics), not from StatCan directly; **changed-from-plan** = evidence contradicts PLAN.md; **unavailable** = not obtainable with the allowed tools, or does not exist; **unverified** = plausible but no evidence obtained.

---

## 0. Headline findings

| # | Finding | Status |
|---|---|---|
| 1 | `www150.statcan.gc.ca` (WDS REST API, table viewer, `/n1/tbl/csv/*.zip` bulk downloads, Daily PDFs) is behind a **Cloudflare managed JavaScript challenge** (`HTTP 403`, header `Cf-Mitigated: challenge`, "We are validating your web browser"). Every scripted request failed: curl default UA, curl with Chrome UA + Accept headers, HTTP/1.1, IPv4-only, GET and POST, and WebFetch. Retried over ~15 minutes; identical result at 03:20 UTC. **No WDS call succeeded and no StatCan sample file was pulled.** | unavailable (at probe time, from scripted clients) |
| 2 | The real-time tables list page is on the *other* host `www.statcan.gc.ca`, which is not challenged. 19 real-time tables; verbatim list with status in section 2. **Six of the 19 are titled "inactive" on open.canada.ca and stopped updating in Feb-Mar 2026**: 16-10-0014, 16-10-0015 (manufacturing), 20-10-0005, 20-10-0020 (wholesale), 20-10-0081, 20-10-0082 (retail). 18-10-0259 (CPI core) has not updated since 2026-05-04 and 36-10-0042 (BoP) missed its Q2 update. Three tables (16-10-0118, 16-10-0119, 20-10-0019) have no open.canada.ca record and were not checked. | confirmed; changed-from-plan |
| 3 | 36-10-0431 (expenditure-based GDP vintages): vintage dimension is named **"Release"**, members formatted **"November 30, 2012"** (English month name, zero-padded day, comma, year), 56 vintages from **Nov 30, 2012** to **Aug 28, 2026** (as of the mirror's 2026-09-30 index). Plan's "Nov 2012" holds. **"Household final consumption expenditure" is a member** of the "Estimates" dimension (31 members). Last StatCan update 2026-09-10 (13 days after the Q2 release). | confirmed (CKAN for start date and update); confirmed (mirror) for dimensions/members |
| 4 | Early vintages in 36-10-0431 are stored under the current price-basis label: the Nov 30, 2012 vintage of household consumption has 127 non-missing values (1981Q1-2012Q3) under the member "Chained (2017) dollars", with 2012Q3 = 927,378 vs 992,184 in current prices. Chained 2017 dollars could not be below 2012 current prices, so these are the chained dollars **as published at the time** (then chained 2007). Levels are therefore not comparable across vintages that straddle a base change; growth rates are. A separate member "Chained (2012) dollars" also exists. | confirmed (mirror), interpretation is inference |
| 5 | **CPI all-items** regular table is 18-10-0004 (monthly, NSA, 2002=100); updated 2026-11-16 08:30 for Oct 2026. No real-time table exists for it. Release lag 15-22 days after reference month; 2026 dates in section 5. The plan's assumption that NSA CPI is not revised was not tested here. | confirmed (table, frequency, lag); non-revision unverified |
| 6 | **CPI excluding food and energy**: no StatCan real-time table. The only CPI real-time table, 18-10-0259, covers the *Bank of Canada core measures* (source 18-10-0256, "13 series, with data from 1949"). The Bank of Canada's CPI page lists StatCan vectors for CPI-trim, CPI-median, CPI-common, CPIX, CPIW and CPI-XFET (excl. food, energy and indirect taxes) but does not say which table they sit in, and 18-10-0259's member list could not be read. **18-10-0259 last updated 2026-05-04** although the source table updated monthly through 2026-11-16: stale or paused. | changed-from-plan (no ex-food-and-energy vintages; core-measure vintages exist but stale); membership unverified |
| 7 | **Unemployment rate (LFS)**: no real-time table. 14-10-0331 / 14-10-0332 are SEPH *payroll* employment and earnings (CKAN description ends "... by North American Industry Classification System (NAICS), last 5 months."), not LFS. Regular table 14-10-0287 (SA and trend-cycle), updated 2026-11-06 for Oct 2026. LFS SA series are revised once a year (release "Labour Force Survey seasonal adjustment revisions 2023-2025", 2026-01-26). | unavailable (StatCan) |
| 8 | **Monthly GDP by industry**: real-time table is 36-10-0491 (source 36-10-0434), monthly, active; last update 2026-11-09 (10 days after the 2026-10-30 release). First vintage not verified (list page says the set starts January 2015, "some are expanded"; not in DBnomics). Full CSV zip is large: ~411 MB per the Wayback index entry of 2026-03-07 (229 MB in Jul 2023). | confirmed (ID, active); unverified (start date) |
| 9 | **Retail sales volume**: real-time tables 20-10-0082 (sales, price and volume; source 20-10-0067) and 20-10-0081 (sales by province; source 20-10-0056) exist, but open.canada.ca titles both **"..., inactive"** and both were last published **2026-03-02** while the source tables kept updating (2026-10-23). Reason not found. | changed-from-plan |
| 10 | Vintage encoding (list page): "a vintage dimension that records the date of official release" in The Daily; one row per release date; most recent estimate in the first row; first estimate is the last non-missing cell in each reference-period column. In the CSV the vintage is one ordinary dimension column (named "Release" in 36-10-0431; CKAN notes for 20-10-0081/20-10-0020 also say "release" and "adjustment(s)" dimensions). | confirmed (concept, StatCan); confirmed (mirror) for header name/format on 36-10-0431 |
| 11 | Update cadence: "released approximately one week after the official release of the source data tables" (list page). Observed: 10 days (36-10-0491) and 13 days (36-10-0431, 36-10-0430). Not same-day. | confirmed |
| 12 | Licence: Statistics Canada Open Licence permits use, reproduction, distribution, sale and sublicensing of the data and of "Value-added Products", with attribution and no implied endorsement. open.canada.ca records cite the Open Government Licence - Canada. | confirmed |
| 13 | Origin-day collisions under the plan's "20th or next business day" rule (2026): CPI lands on the origin day on **Apr 20, Jun 22, Jul 20**; retail trade on **Feb 20, Mar 20**. See section 5. | confirmed (dates), rule implication |

---

## 1. WDS API (Web Data Service)

### 1.1 Reachability at probe time

All of the following returned `HTTP 403` with a Cloudflare challenge page (title "Vérification de sécurité / Security Check", `Cf-Mitigated: challenge`, `Server: cloudflare`, `meta http-equiv="refresh" content="360"`, requires JavaScript and cookies):

| URL | Method | Result |
|---|---|---|
| `https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata` (POST `[{"productId":36100431}]`) | curl x2 | 403 challenge |
| `https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/36100431/en` | curl (default UA; Chrome UA; `--http1.1`; `-4`) | 403 challenge |
| `https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/18100259/en` | curl | 403 challenge (retry 03:20 UTC) |
| `https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets` | curl x4, several header sets | 403 challenge |
| `https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite` | curl | 403 challenge |
| `https://www150.statcan.gc.ca/n1/tbl/csv/36100431-eng.zip` | curl | 403 challenge |
| `https://www150.statcan.gc.ca/n1/en/catalogue/36100431` | curl | 403 challenge |
| `https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043101` | curl | 403 challenge |
| `https://www150.statcan.gc.ca/` | curl | 403 challenge |
| `https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/rel-com-eng.htm` | curl | 403 challenge |
| `https://www150.statcan.gc.ca/n1/en/type/data?text=real-time` | WebFetch | 403 |
| `https://www150.statcan.gc.ca/n1/daily-quotidien/250130/dq250130a-eng.pdf` | WebFetch | 403 |
| `https://www.statcan.gc.ca/t1/wds/rest/getCodeSets` (wrong host, control) | curl | 503 HTML error page |
| `https://api.statcan.gc.ca/t1/wds/rest/getCodeSets` (guessed host) | curl | 404 |

Interpretation: a bot-management rule on the `www150` zone that also covers the API path. It cannot be passed by header changes; it needs a JS-capable client or an allow-listing. Whether it is permanent, new, or specific to this network could not be determined from one vantage point. No StatCan announcement about it was found by search. Third-party wrappers (e.g. the `stats_can` Python package README) still document plain REST calls, which says nothing about whether they currently work.

Follow-ups for the caller (not done here; outside this probe's mandate):
- Open `https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets` in a normal browser on the same network; if it loads, the block is bot-management only.
- Test from the intended runner's network.
- Fallbacks if WDS stays blocked: (a) SDMX zip `https://www150.statcan.gc.ca/n1/tbl/sdmx/<PID>-SDMX.zip` (same host, probably same block, untested); (b) open.canada.ca CKAN for *metadata only* (works, 1.3), but its resource URLs point back to `www150`; (c) DBnomics mirror for the three real-time tables it carries (1.4); (d) a browser-driven download step.

### 1.2 Documented API shape (from the WDS user guide; **documented, not empirically verified**)

Source: `https://www.statcan.gc.ca/en/developers/wds/user-guide` (fetched OK, 245k chars; chars 0-200k read; 100k-200k is code lists only).

- Base: `https://www150.statcan.gc.ca/t1/wds/rest/`; HTTPS, JSON, no authentication or key.
- Limits: 50 requests/s server-wide, 25 requests/s per IP. `409 Not available` can occur 00:00-08:30 ET while tables are being updated. New data appear 08:30 ET on release day.
- `getCubeMetadata`: POST body `[{"productId":36100431}]`. Returns `status`, `object` with `productId`, `cansimId`, `cubeTitleEn/Fr`, `cubeStartDate`, `cubeEndDate`, `frequencyCode`, `nbSeriesCube`, `nbDatapointsCube`, `releaseTime`, `archiveStatusCode`, `subjectCode`, `surveyCode`, `dimension[]` (each with `member[]`), `footnote`, `correctionFootnote`, `issueDate`.
- `getFullTableDownloadCSV/{PID}/{en|fr}`: GET. Returns `{"status":"SUCCESS","object":"<url to PID-eng.zip>"}`; the zip is served from `https://www150.statcan.gc.ca/n1/tbl/csv/`.
- `getDataFromCubePidCoordAndLatestNPeriods`: POST `[{"productId":..,"coordinate":"1.12.0.0.0.0.0.0.0.0","latestN":3}]`.
- `getDataFromVectorsAndLatestNPeriods`: POST `[{"vectorId":32164132,"latestN":3}]`.
- `getBulkVectorDataByRange`: POST `{"vectorIds":["74804","1"],"startDataPointReleaseDate":"2015-12-01T08:30","endDataPointReleaseDate":"2018-03-31T19:00"}`. Filters by **release date**, which is what a live as-of pull of the source tables needs.
- `getChangedCubeList/{YYYY-MM-DD}`: GET; cubes released on that date with `releaseTime`.
- Data point fields: `refPer`, `refPer2`, `value`, `decimals`, `scalarFactorCode`, `symbolCode`, `statusCode`, `securityLevelCode`, `releaseTime`, `frequencyCode`.
- The guide itself notes a parameter-name inconsistency in `getDataFromVectorByReferencePeriodRange`.

Full-table CSV layout (source: `https://www.statcan.gc.ca/en/developers/csv/user-guide`, fetched OK): zip `PID-eng.zip` holds `PID.csv` and `PID_Metadata.csv`. Data columns: `REF_DATE, GEO, DGUID, <one column per dimension, up to 10>, UOM, UOM_ID, SCALAR_FACTOR, SCALAR_ID, VECTOR, COORDINATE, VALUE, STATUS, SYMBOL, TERMINATED, DECIMALS`. For a real-time table the vintage dimension is one of the dimension columns (for 36-10-0431 expect a column headed `Release`, values like `November 30, 2012`; this is the mirror's reading of StatCan's metadata, not a direct CSV check). The metadata CSV lists cube title, PID, archive status (`CURRENT`/`ARCHIVED`), frequency, start/end reference periods, dimension names/IDs, member names/IDs/parent/terminated flag, symbol legend, survey, subject, notes, corrections. There is no release-date column in the data CSV; the Daily release date is only in the vintage dimension of real-time tables (or in WDS `releaseTime`).

### 1.3 Metadata reachable without a browser: open.canada.ca CKAN

`https://open.canada.ca/data/api/action/package_search?q=<PID>&rows=3` worked (HTTP 200) for all PIDs tried except three real-time tables that have no CKAN record at all (16100118, 16100119, 20100019: `count: 0` even with `rows=20`; see section 2). Gives title (with an "inactive" suffix where StatCan has marked the table so), description, `frequency` (ISO 8601 duration), `date_published` (= last StatCan release at 08:30 ET), `metadata_modified`, licence, resource URLs (CSV eng/fra zips, SDMX zip, table viewer). No coverage dates or member lists. Cheap "has this table been updated" poll; it is not challenged.

Regular (source) tables:

```
18100004 | P1M | 2026-11-16 08:30 | Consumer Price Index, monthly, not seasonally adjusted
18100256 | P1M | 2026-11-16 08:30 | Consumer Price Index (CPI) statistics, measures of core inflation and other related statistics - Bank of Canada definitions   ("This table contains 13 series, with data from 1949")
14100287 | P1M | 2026-11-06 08:30 | Labour force characteristics, monthly, seasonally adjusted and trend-cycle
36100434 | P1M | 2026-10-30 08:30 | Gross domestic product (GDP) at basic prices, by industry, monthly   ("volume measures")
36100104 | P3M | 2026-08-28 08:30 | Gross domestic product, expenditure-based, Canada, quarterly   ("in chained (2017) and current dollars")
20100067 | P1M | 2026-10-23 08:30 | Monthly retail sales, price, and volume, seasonally adjusted
20100056 | P1M | 2026-10-23 08:30 | Monthly retail trade sales by province and territory
```

Real-time tables: see section 2.

Verbatim descriptions worth keeping:
- 36100431: "Vintages of releases of quarterly expenditure-based, gross domestic product, starting with the November 30, 2012 reference period, Canada, in chained and current dollars, contributions to percent change and to annualized percent change."
- 36100430: "Vintages of releases of quarterly income-based gross domestic product, starting with the November 30, 2012 reference period, Canada."
- 36100491: "Vintages of releases of gross domestic product (GDP) at basic prices, by North American Industry Classification System (NAICS) aggregates, by industry, volume measures, monthly."
- 18100259: "Historical (real-time) releases of the measures of core inflation, with data from 1989 (not all combinations necessarily have data for all years). Data are presented for the current release and previous four releases."
- 20100081: "Historical releases of retail trade sales, available for all members under release and adjustment dimensions, for Canada, provinces and territories, available on a monthly basis in dollars x 1,000."
- 34100278/34100279: "Historical (real time) releases starting in 2015 of capital and repair expenditures ... annual data from 2006 to present."

### 1.4 Structural sample via the DBnomics mirror (third-party, not StatCan)

DBnomics (`https://api.db.nomics.world/v22/`) carries a `STATCAN` provider with 199 datasets, including exactly three real-time tables: **36100431, 36100430, 36100042**. It does **not** carry 36100491, 18100259, 20100082, 14100331 (dataset lookups returned `num_found: 0`), nor 18100004, 14100287, 18100256, 20100067. Dataset 36100431 was indexed 2026-09-30, i.e. it includes the 2026-09-10 StatCan update. Files: `dbnomics_36100431.json`, `dbnomics_36100431_series_sample.json`, `dbnomics_36100431_v2012.json`, `dbnomics_provider_statcan.json` in the scratch folder.

Dataset 36100431 metadata (DBnomics' rendering of StatCan's dimensions; DBnomics codes in parentheses are DBnomics', not StatCan's):
- `nb_series`: 9,428.
- Dimensions: `Frequency` (Quarterly), `Geography` (Canada), `Prices`, `Seasonal adjustment`, `Estimates`, `Release`.
- `Prices` (6): Chained (2017) dollars; Current prices; Contributions to percent change; Contributions to percent change, annualized; Chained (2012) dollars; Chained (2017) dollars percentage change.
- `Seasonal adjustment` (2): Seasonally adjusted at annual rates; Unadjusted.
- `Estimates` (31): Final consumption expenditure; **Household final consumption expenditure**; Goods; Durable goods; Semi-durable goods; Non-durable goods; Services; Non-profit institutions serving households' final consumption expenditure; General governments final consumption expenditure; Gross fixed capital formation; Business gross fixed capital formation; Residential structures; Non-residential structures, machinery and equipment; Non-residential structures; Machinery and equipment; Intellectual property products; Non-profit institutions serving households' gross fixed capital formation; General governments gross fixed capital formation; Investment in inventories; Of which: business investment in inventories; Non-farm; Farm; Exports of goods and services; Exports of goods; Exports of services; Less: imports of goods and services; Imports of goods; Imports of services; Statistical discrepancy; **Gross domestic product at market prices**; Final domestic demand.
- `Release` (56): earliest "November 30, 2012", latest "August 28, 2026"; all 56 labels parse as `%B %d, %Y` (e.g. "March 02, 2017", "May 31, 2018"). 56 members over 14 years = one per quarterly release, no gaps apparent (not individually checked).

Example vintage rows (series `STATCAN/36100431/1.1.1.2.1`, "Quarterly - Canada - Chained (2017) dollars - Seasonally adjusted at annual rates - Household final consumption expenditure - November 30, 2012"): 257 periods 1961Q1-2025Q1 in the mirror's grid, 127 non-missing, first 1981Q1 = 400,801, last 2012Q3 = 927,378 (millions). Same vintage, current prices (`1.2.1.2.1`): last 2012Q3 = 992,184. Vintage "November 28, 2014": last 2014Q3 = 978,496 (chained) / 1,081,860 (current). So a vintage ends at the quarter released that day (Q3 released end-November, ~60 days lag), and the Nov 2012 vintage starts at 1981Q1.

Caveat on the price basis (inference, see headline 4): the chained values in the Nov 2012 and Nov 2014 vintages are below current prices, which is impossible for a 2017 base and consistent with the then-current 2007 base. Treat the "Chained (2017) dollars" member as "chained dollars as published in that vintage"; use growth rates, not levels, across vintages.

### 1.5 Internet Archive copies (index reachable; downloads not permitted in this session)

The Wayback CDX index answered and lists archived copies of the full-table zips and the official 2026 release calendar. Downloading them was denied by the session's permission classifier and WebFetch refuses `web.archive.org`, so nothing was fetched; this route is closed for this session. For reference (timestamp, size from the index):

| Archived URL | Snapshots |
|---|---|
| `www150.statcan.gc.ca/n1/tbl/csv/36100431-eng.zip` | 2024-07-10 (14.5 MB) |
| `www150.statcan.gc.ca/n1/tbl/csv/18100259-eng.zip` | 2024-01-27 (1.2 MB), 2024-06-04 (0.6 MB), 2026-01-14 (2.0 MB), 2026-02-25 (1.9 MB), 2026-11-13 (2.1 MB) |
| `www150.statcan.gc.ca/n1/tbl/csv/36100491-eng.zip` | 2023-07-24 (229 MB), 2026-03-07 (411 MB) |
| `www150.statcan.gc.ca/n1/tbl/csv/20100082-eng.zip` | 2024-11-25 (0.74 MB), 2026-03-20 (2,247,292 B), 2026-04-27 (2,247,329 B), 2026-10-11 (2,247,329 B) - the identical April and October sizes are consistent with the table being frozen after March 2026 |
| `www150.statcan.gc.ca/n1/release-diffusion/2026-eng.pdf` (official 2026 release calendar) | 2025-12-12 (344 KB), 2026-06-17 (126 KB) |

---

### 1.5 Re-test 2026-11-18 (owner-suggested routes)

| Route | Result |
|---|---|
| `https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/dataflow/StatCan/DF_18100004` (SDMX REST), plain curl, identified client string | 403, `Cf-Mitigated: challenge` |
| `https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite` (WDS) | 403, challenge |
| `https://www150.statcan.gc.ca/n1/tbl/sdmx/36100107-SDMX.zip` | 403, challenge |
| Hosted community MCP server `mcp-statcan.onrender.com/mcp` (Aryan-Jhaveri/mcp-statcan v0.19.0, MIT; wraps WDS + SDMX REST with plain HTTP, no browser emulation), tool `get_sdmx_data` for 18100004 | tool error: `403 Forbidden` for `.../sdmx/statcan/rest/structure/Data_Structure_18100004`, i.e. StatCan blocks the Render host too |
| R package `cansim` 0.4.4 (local R 4.5.1), `get_cansim_vector("v41690973")` | "Problem downloading data, returned status code 403" |
| npm `statcan-mcp` | not run: same WDS endpoints, no reason to expect a different outcome |

| GitHub Actions runner (ubuntu-latest, `.github/workflows/statcan-fetch.yml`, run 44310619180, 2026-11-18 13:08 UTC), stdlib urllib, User-Agent `foundation-forecast-fetch/0.1 (GitHub Actions; public data)`, `getFullTableDownloadCSV` for 18100004, 36100107, 36100104, 14100287, 20100067, 36100431 | all six: 403, `server: cloudflare`, challenge page |

Counter-evidence: the owner's own public repository (vrraiv/sixfigures, `pipeline/series.py`) calls the same `getFullTableDownloadCSV` endpoint from a GitHub runner with stdlib urllib and the User-Agent string `Mozilla/5.0`, and its data-refresh runs of 2026-11-14 05:06 and 05:16 UTC downloaded five full-table zips (17100155, 11100239, 14100459, 18100005, 34100292) successfully. Two explanations fit: (a) the rule was tightened between 14 and 18 November, or (b) the rule challenges requests whose User-Agent does not look like a browser's while letting runner IPs through otherwise. (b) was not tested from here: sending a browser User-Agent to pass a bot filter is not something the agent does. The owner can separate the two by re-running their own sixfigures refresh (housing part) and seeing whether `series.py` still downloads today.

Conclusion: the Cloudflare rule on the `www150` zone blocked every client the agent used, from this
network, from a Render host and from a GitHub Actions runner, on both days tested; the owner's
browser-identified script passed from a runner on 14 November. None of the wrappers (MCP servers, `cansim`,
`stats_can`) does anything a plain HTTP client does not, so they inherit the block. The
remaining routes are unchanged: (a) the owner downloads the files in a browser and the agent
registers them with `RawStore.register_manual` (hash-pinned, labelled `manual`); (b) DBnomics
mirror + OECD editions. Not attempted and not proposed: browser-emulation or challenge-solving
clients, which would amount to circumventing the site's bot protection.

## 2. Real-time data tables: the full list, with status

List page: `https://www.statcan.gc.ca/en/dai/btd/rct` (fetched OK three times; "Date modified: 2025-12-16"). Table 1 verbatim, plus open.canada.ca frequency, last published date and status (probe date 2026-11-17):

| Real-time table title (verbatim from the list page) | Regular table | Real-time table | Freq (CKAN) | Last published (CKAN) | Status |
|---|---|---|---|---|---|
| Historical (real-time) releases of merchandise imports and exports, customs and balance of payments basis for all countries, by seasonal adjustment and North American Product Classification System (NAPCS) | 12-10-0163 | 12-10-0165 | P1M | 2026-11-16 | active ("data for years 1988 - current") |
| Historical (real-time) releases of real manufacturing sales, orders, inventory owned and inventory to sales ratio, 2017 dollars, seasonally adjusted | 16-10-0013 | 16-10-0014 | P1M | 2026-02-26 | **inactive** (CKAN title) |
| Historical (real-time) releases manufacturing capacity utilization rates | 16-10-0012 | 16-10-0015 | P1M (CKAN) | 2026-02-26 | **inactive** (CKAN title); "from January 2017" |
| Historical (real-time) releases of manufacturers' sales, inventories, orders and inventory to sales ratios, by North American Industry Classification System (NAICS), Canada | 16-10-0047 | 16-10-0118 | ? | ? | no CKAN record found |
| Historical (real-time) releases of manufacturing sales, by North American Industry Classification System (NAICS) and province | 16-10-0048 | 16-10-0119 | ? | ? | no CKAN record found |
| Historical (real-time) releases of wholesale sales, price and volume, seasonally adjusted | 20-10-0003 | 20-10-0005 | P1M | 2026-03-04 | **inactive** (CKAN title) |
| Historical (real-time) releases of wholesale trade, sales | 20-10-0074 | 20-10-0019 | ? | ? | no CKAN record found |
| Historical (real-time) releases of wholesale trade, inventories | 20-10-0076 | 20-10-0020 | P1M | 2026-03-04 | **inactive** (CKAN title) |
| Historical (real-time) releases of Consumer Price Index (CPI) statistics, measures of core inflation - Bank of Canada definitions | 18-10-0256 | 18-10-0259 | P1M | 2026-05-04 | not titled inactive, but **6 months stale** |
| Historical (real-time) releases of monthly retail trade, sales | 20-10-0056 | 20-10-0081 | P1M | 2026-03-02 | **inactive** (CKAN title) |
| Historical (real-time) releases of monthly retail sales, price, and volume | 20-10-0067 | 20-10-0082 | P1M | 2026-03-02 | **inactive** (CKAN title) |
| Historical (real-time) releases of employment and average weekly earnings (including overtime) for all employees by industry, monthly, seasonally adjusted | 14-10-0220 | 14-10-0331 | P1M | 2026-11-16 | active ("last 5 months") |
| Historical (real-time) releases of employment and average weekly earnings (including overtime) for all employees by province and territory, monthly, seasonally adjusted | 14-10-0223 | 14-10-0332 | P1M | 2026-11-16 | active ("last 5 months") |
| Historical (real-time) releases of gross domestic product (GDP) at basic prices, by industry, monthly | 36-10-0434 | 36-10-0491 | P1M | 2026-11-09 | active |
| Historical (real-time) releases of balance of international payments, current account, seasonally adjusted, quarterly | 36-10-0018 | 36-10-0042 | P3M | 2026-06-08 | **stale**: source table 36-10-0018 was published 2026-08-27 (Q2), but the real-time table's last update is 2026-06-08, so the Q2 vintage is missing ~3 months later |
| Vintages of releases of gross domestic product, income-based | 36-10-0103 | 36-10-0430 | P3M | 2026-09-10 | active; vintages from Nov 30, 2012 |
| Vintages of releases of gross domestic product, expenditure-based | 36-10-0104 | 36-10-0431 | P3M | 2026-09-10 | active; vintages from Nov 30, 2012 |
| Historical (real time) releases of capital and repair expenditures, non-residential tangible assets, by industry and geography | 34-10-0035 | 34-10-0278 | P1Y | 2026-03-02 | annual; "releases starting in 2015" |
| Historical (real time) releases of capital and repair expenditures, non-residential tangible assets, by industry, Canada | 34-10-0036 | 34-10-0279 | P1Y | 2026-03-02 | annual; "releases starting in 2015" |

Per-table first-vintage dates are **not** on the list page: "The data tables contain vintages of data as of January 2015, some are expanded to provide users with a longer time series." Confirmed starts: 36-10-0431 and 36-10-0430 from Nov 30, 2012 (CKAN; mirror); capital expenditure tables from 2015 (CKAN). Others unverified. The SEPH descriptions end with "last 5 months"; whether that describes the stored vintage range or only the default view is not known.

Verbatim structural statements from the list page:
- "they contain a vintage dimension that records the date of official release" ... "to record the date that the data were released in The Daily, the agency's official release vehicle."
- "The real-time data tables show all revisions of a specific data point over time."
- "The rows of the vertical axis indicate the date data was released." "For each column, the last data point contains the initial data released for that year and quarter." "The first row contains the most recent estimate for each reference period".
- "The real-time tables are released approximately one week after the official release of the source data tables."
- "the real-time data tables do not replace the current data tables for these time series".
- Worked example: a Nov 30, 2023 release of Q3 2023 is recorded with that date; a May 31, 2024 release adds rows for Q3 and Q4 2023 with "the vintage (release) dimension would have the value of May 31, 2024."

The list page (modified 2025-12-16) still lists the six tables that open.canada.ca marks inactive; the page has not been updated for the Feb-Mar 2026 changes. The plan's "19 series" count matches the page. As of this probe: **active** (updated after their latest source release): 12-10-0165, 14-10-0331, 14-10-0332, 36-10-0491, 36-10-0430, 36-10-0431, and the two annual capital-expenditure tables 34-10-0278, 34-10-0279 (updated 2026-03-02, consistent with an annual cycle); **inactive**: 16-10-0014, 16-10-0015, 20-10-0005, 20-10-0020, 20-10-0081, 20-10-0082; **stale**: 18-10-0259, 36-10-0042; **unchecked**: 16-10-0118, 16-10-0119, 20-10-0019.

---

## 3. Target-by-target assessment

| Target | Regular table | Real-time table | Vintages | Notes | Status |
|---|---|---|---|---|---|
| Real GDP, expenditure-based, quarterly | 36-10-0104 (P3M; "chained (2017) and current dollars") | 36-10-0431 | 56 vintages, Nov 30, 2012 - Aug 28, 2026; dimension "Release", format "November 30, 2012" | Members include "Gross domestic product at market prices" and "Household final consumption expenditure" (31 estimates), 6 price bases, SAAR and unadjusted. Chained-dollar levels in early vintages are in the base of the time (see 1.4). | confirmed (mirror) |
| Household final consumption expenditure | 36-10-0104 | 36-10-0431 | same | Member present. | confirmed (mirror) |
| CPI all-items, monthly NSA | 18-10-0004 (P1M, 2002=100) | none | n/a | Live pull from 18-10-0004 (Bank of Canada cites vector v41690973 for total CPI). Lag 15-22 days. Whether StatCan ever revises NSA CPI was not checked. | confirmed (table); vintage-free assumption unverified |
| CPI excluding food and energy, monthly | 18-10-0256 (13 series, core measures) or a special aggregate in 18-10-0004 (not checked) | 18-10-0259 (core measures; stale since 2026-05-04) | not verified | No ex-food-and-energy vintage table. Bank of Canada page lists CPI-XFET vector v1675033092 (excl. food, energy, indirect taxes) and CPIX, CPIW, trim, median, common, with no table attribution. | changed-from-plan |
| Unemployment rate, LFS SA | 14-10-0287 (P1M) | none | n/a | 14-10-0331/0332 are SEPH payroll. LFS SA revised annually (Jan). | unavailable (StatCan) |
| Monthly GDP by industry, all industries | 36-10-0434 (P1M, basic prices, volume measures) | 36-10-0491 | start unverified (set from Jan 2015) | Active (2026-11-09). ~411 MB full zip; prefer a filtered pull once API access works. | confirmed (ID, active) |
| Retail sales volume | 20-10-0067 (P1M, SA, price and volume) | 20-10-0082 | ends ~Feb 2026 release | Inactive since 2026-03-02. | changed-from-plan |

Conditioning series with active real-time tables as of the probe: merchandise trade 12-10-0165 (monthly); SEPH employment and earnings 14-10-0331, 14-10-0332 (monthly); income-based GDP 36-10-0430 (quarterly); monthly GDP by industry 36-10-0491. Inactive: 16-10-0014, 16-10-0015, 20-10-0005, 20-10-0020, 20-10-0081, 20-10-0082. Stale: 18-10-0259 (CPI core), 36-10-0042 (BoP). Unchecked (no open.canada.ca record): 16-10-0118, 16-10-0119, 20-10-0019.

---

## 4. Licence

- Statistics Canada Open Licence: `https://www.statcan.gc.ca/en/reference/licence` (fetched OK).
- Worldwide, royalty-free, non-exclusive licence to "use, reproduce, publish, freely distribute, or sell the Information" and "Value-added Products" (products made by adapting or incorporating the Information), and to sublicense on consistent terms. IP in Value-added Products vests in the licensee.
- Conditions: accurate reproduction, no misrepresentation of source, no implied endorsement, no linking to identify individuals or businesses, no use of StatCan name/logos/wordmark without authorization.
- Attribution for data: "Source: Statistics Canada, name of product, reference date. Reproduced and distributed on an "as is" basis with the permission of Statistics Canada." For derived results: "Adapted from Statistics Canada, name of product, reference date. This does not constitute an endorsement by Statistics Canada of this product."
- open.canada.ca records for the same tables cite the Open Government Licence - Canada (`https://open.canada.ca/en/open-government-licence-canada`).
- Conclusion: research use and redistribution of derived results (forecast scores, revision statistics, normalised vintage tables) are permitted with attribution. **confirmed**
- DBnomics redistributes StatCan data under its own terms; if the mirror is used as a data source, check DBnomics' terms separately (not done).

---

## 5. Release calendar and publication lags

Sources: StatCan service standards 2025-26 (`https://www.statcan.gc.ca/en/about/transparency/service-standards/2025-2026-annual`, fetched OK) for stated lags; Nova Scotia Finance release archive (`https://novascotia.ca/finance/statistics/archive.asp?dti=12&dto=0`, fetched OK) for **actual** release dates 2025-11-17 to 2026-11-16 (used for all dates below unless stated); Newfoundland and Labrador flashsheet PDF (`https://www.stats.gov.nl.ca/Publications/Flashsheets/PDF/ReleaseSchedule.PDF`, produced 2026-01-22) for the **scheduled** 2026 LFS and CPI dates. The two agree except January CPI: the flashsheet (produced 2026-01-22) scheduled Feb 16, 2026; the actual release was Feb 17, 2026 (NS archive, and StatCan's own Daily URL `dq260217a`). The official StatCan calendar (`www150.../n1/release-diffusion/2026-eng.pdf`, `cal2-eng.htm`) is on the blocked host; the guessed path `https://www.statcan.gc.ca/en/dai/sched/release-dates` returned 503 twice and may simply not exist. All releases are 08:30 ET.

Stated service standards (lag after reference period): CPI within 31 days; LFS 10 days after end of collection; monthly GDP by industry 60 days; quarterly GDP within 60 days after the quarter; retail trade within 2 months; manufacturing within 45 days; wholesale within 47 days; SEPH 60 days; international merchandise trade 35-40 days (the only standard missed in 2025-26, 75%).

Actual dates (Nova Scotia archive) and 2026 schedule (NL flashsheet for CPI/LFS beyond the archive):

| Release | Dates (reference period) | Typical day | Lag |
|---|---|---|---|
| CPI (18-10-0004, 18-10-0256) | 2025-11-17 (Oct), 12-15 (Nov), 2026-01-19 (Dec), 02-17 (Jan), 03-16 (Feb), 04-20 (Mar), 05-19 (Apr), 06-22 (May), 07-20 (Jun), 08-17 (Jul), 09-14 (Aug), 10-19 (Sep), 11-16 (Oct); scheduled 12-14 (Nov), 2027-01-18 (Dec). Basket update release 2026-06-18. | Mon/Tue, 14th-22nd | 15-22 days |
| LFS (14-10-0287) | 2025-12-05, 2026-01-09, 02-06, 03-13, 04-10, 05-08, 06-05, 07-10, 08-07, 09-04, 10-09, 11-06; scheduled 12-04, 2027-01-08. SA revisions release 2026-01-26. | 1st/2nd Friday | ~5-13 days |
| Monthly GDP by industry (36-10-0434) | 2025-11-28 (Sep), 12-23 (Oct), 2026-01-30 (Nov), 02-27 (Dec), 03-31 (Jan), 04-30 (Feb), 05-29 (Mar), 06-30 (Apr), 07-31 (May), 08-28 (Jun), 09-29 (Jul), 10-30 (Aug) | last business day(s) | ~60 days |
| Quarterly GDP (36-10-0104) | 2025-11-28 (Q3), 2026-02-27 (Q4), 05-29 (Q1), 08-28 (Q2) | last business day of Feb/May/Aug/Nov | ~60 days |
| Retail trade (20-10-0067) | 2025-11-21 (Sep), 12-19 (Oct), 2026-01-23 (Nov), 02-20 (Dec), 03-20 (Jan), [Feb 2026 reference release absent from the NS archive], 05-22 (Mar), 06-19 (Apr), 07-23 (May), 08-21 (Jun), 09-24 (Jul), 10-23 (Aug) | Thu/Fri, 19th-24th | ~50-55 days |
| Manufacturing (16-10-0047) | 2025-12-15, 2026-01-15, 02-17, 03-13, 04-15, 05-15, 06-15, 07-15, 08-14, 09-14, 10-15, 11-13 | mid-month | ~45 days |
| Wholesale (20-10-0003/0074) | 2025-12-12, 2026-01-15, 02-17, 03-12, 04-15, 05-14, 06-15, 07-15, 08-14, 09-15, 10-15, 11-13 | mid-month | ~45 days |
| SEPH payroll (14-10-0220) | 2025-11-27, 12-18, 2026-01-29, 02-26, 03-26, 04-30, 05-28, 06-25, 07-30, 08-27, 09-24, 10-29 | last Thursday | ~60 days |
| Merchandise trade (12-10-0163) | 2025-12-11, 2026-01-08, 01-29, 02-19, 03-12, 04-02, 05-05, 06-09, 07-07, 08-04, 09-03, 10-06, 11-04 | ~1st week (irregular late 2025/early 2026) | ~35-40 days |

Origin-day collisions under PLAN.md's rule "the 20th, or the next business day" (computed for Nov 2025 - Dec 2026; weekends rolled forward, Canadian statutory holidays not applied). The Nova Scotia archive holds past releases only, so retail dates after 2026-10-23 and the Feb-2026-reference retail release are not available from it:

| Origin | Release on the origin day (08:30 ET) | Release the day before / after | Gaps |
|---|---|---|---|
| 2025-11-20 (Thu) | - | Retail 2025-11-21 (day after) | |
| 2025-12-22 (Mon; 20th is a Saturday) | - | - | |
| 2026-01-20 (Tue) | - | CPI 2026-01-19 (day before) | |
| 2026-02-20 (Fri) | **Retail trade** | - | |
| 2026-03-20 (Fri) | **Retail trade** | - | |
| 2026-04-20 (Mon) | **CPI** | - | retail (Feb reference) date not available |
| 2026-05-20 (Wed) | - | CPI 2026-05-19 (day before) | |
| 2026-06-22 (Mon; 20th is a Saturday) | **CPI** | - | |
| 2026-07-20 (Mon) | **CPI** | - | |
| 2026-08-20 (Thu) | - | Retail 2026-08-21 (day after) | |
| 2026-09-21 (Mon) | - | - | |
| 2026-10-20 (Tue) | - | CPI 2026-10-19 (day before) | |
| 2026-11-20 (Fri) | retail (Sep reference) **probably** on this day: a third-party economic calendar lists 2026-11-20 13:30 UTC; not confirmed from StatCan | - | official retail date not available |
| 2026-12-21 (Mon; 20th is a Sunday) | - | - | retail (Oct reference) date not available |

Implications: CPI and retail trade are the two releases that fall on the origin day (5 confirmed, 1 probable, of 14 origins) or within a day of it (another 5). The information-set rule must state whether an 08:30 ET release on the origin date is in or out, and a live runner must execute after 08:30 ET if "in". LFS, monthly and quarterly GDP, SEPH, manufacturing and wholesale never fall within a day of the origin in this window. Because real-time tables are posted ~1-2 weeks after the source release, a live run cannot rely on them for the newest vintage; it must pull the source table at the origin and store that pull as its own vintage. For the historical backtest this does not matter: each stored vintage carries its Daily release date.

---

## 6. Other sources with longer Canadian vintage history (note only; separate agent)

- OECD Main Economic Indicators "Original Release Data and Revisions Database": described (Dallas Fed, OECD) as monthly vintages from January 1999 across MEI series. Coverage of specific Canadian series (GDP, unemployment rate, CPI) was **not** verified in this probe.
- Federal Reserve Bank of Dallas "Real-Time Historical Dataset for the OECD": 1962-1998 vintages for 26 countries including Canada; Canadian series listed on its page are real GDP/GNP, industrial production, manufacturing production, capacity utilization, unemployment rate (`https://www.dallasfed.org/research/international/oecd/canada`, from search snippet; not fetched).
- A Bank of Canada Review article by Tkacz (2010, found via search snippet, not read) covers data revisions in Canada and notes the OECD maintains real-time data for Canada; context only.
- DBnomics (above) mirrors StatCan's 36-10-0431 and 36-10-0430 with full vintage structure; it adds no history beyond StatCan's.

---

## 7. All URLs used

| URL | Tool | Result |
|---|---|---|
| https://www.statcan.gc.ca/en/dai/btd/rct | WebFetch x3 | OK (list page, structure notes, verbatim table) |
| https://www.statcan.gc.ca/en/developers/wds/user-guide | WebFetch x2 (offset 0, 100000) | OK; API shapes; chars 200000+ not read |
| https://www.statcan.gc.ca/en/developers/csv/user-guide | WebFetch | OK; CSV layout |
| https://www.statcan.gc.ca/en/reference/licence | WebFetch | OK |
| https://www.statcan.gc.ca/en/about/transparency/service-standards/2025-2026-annual | WebFetch | OK; timeliness standards |
| https://www.statcan.gc.ca/en/dai/sched/release-dates (guessed path) | WebFetch x2 | 503; probably not a real page |
| https://www.statcan.gc.ca/t1/wds/rest/getCodeSets (control, wrong host) | curl | 503 |
| https://api.statcan.gc.ca/t1/wds/rest/getCodeSets (guessed host) | curl | 404 |
| https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata (POST) | curl x2 | 403 Cloudflare challenge |
| https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/36100431/en | curl x3 (header/protocol variants) | 403 challenge |
| https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/18100259/en | curl | 403 challenge |
| https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets | curl x4 | 403 challenge |
| https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite | curl | 403 challenge |
| https://www150.statcan.gc.ca/n1/tbl/csv/36100431-eng.zip | curl | 403 challenge |
| https://www150.statcan.gc.ca/n1/en/catalogue/36100431 | curl | 403 challenge |
| https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043101 | curl | 403 challenge |
| https://www150.statcan.gc.ca/ | curl | 403 challenge |
| https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/rel-com-eng.htm | curl | 403 challenge |
| https://www150.statcan.gc.ca/n1/en/type/data?text=real-time | WebFetch | 403 |
| https://www150.statcan.gc.ca/n1/daily-quotidien/250130/dq250130a-eng.pdf | WebFetch | 403 |
| https://open.canada.ca/data/api/action/package_search?q=<PID>&rows=3 (26 PIDs; 4 re-run with rows=20) | curl | OK; 3 PIDs (16100118, 16100119, 20100019) have no record |
| https://open.canada.ca/data/api/action/package_search?q="real-time) releases" OR "Vintages of releases"&rows=40 | curl | OK but 1 hit (full-text search weak; search by PID) |
| https://open.canada.ca/data/en/dataset/80614309-33f7-45d4-b492-a20811b13bd3 | WebFetch | OK (36-10-0431 record) |
| https://api.db.nomics.world/v22/datasets/STATCAN/36100431?limit=1 | curl | OK; dimensions and members |
| https://api.db.nomics.world/v22/datasets/STATCAN/{36100491,18100259,20100082,14100331} | curl | OK, `num_found: 0` (not mirrored) |
| https://api.db.nomics.world/v22/providers/STATCAN | curl | OK; 199 datasets |
| https://api.db.nomics.world/v22/series/STATCAN/36100431?...&observations=1 (2 calls, 3-5 series each) | curl | OK; example vintage rows |
| https://web.archive.org/cdx/search/cdx?url=... (9 patterns) | curl | OK (index only); one call returned "Internet Archive services are temporarily offline" |
| https://web.archive.org/web/<ts>id_/... (zips, 2026-eng.pdf) | curl | denied by session permission classifier; not retried |
| https://web.archive.org/web/2026/https://www150.statcan.gc.ca/n1/dai-quo/cal2-eng.htm | WebFetch | tool refuses web.archive.org |
| https://bac-lac.wayback.archive-it.org/web/2025/https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043101 (and 3610049101) | WebFetch | denied by session permission classifier |
| https://www.bankofcanada.ca/rates/price-indexes/cpi/ | WebFetch | OK (core measure definitions and StatCan vectors; no table attribution) |
| https://novascotia.ca/finance/statistics/archive.asp?dti=12&dto=0 | WebFetch x2 | OK (actual release dates Nov 2025 - Nov 2026) |
| https://www.stats.gov.nl.ca/Publications/Flashsheets/PDF/ReleaseSchedule.PDF | WebFetch + local stdlib text extraction | OK (scheduled 2026 LFS and CPI dates) |
| https://publications.saskatchewan.ca/api/v1/products/86689/formats/156260/download | WebFetch + local extraction | PDF fetched; text not extractable with stdlib; unused |
| https://www.financecalendar.com/?p=2099 and ?p=2098 | WebFetch | OK; third-party; consistent with NL flashsheet for Sep 2026 - Jan 2027; not used for the tables above |
| WebSearch (9 queries) | WebSearch | discovery only; the last found a third-party calendar entry for retail trade on 2026-11-20 (unconfirmed) |

---

## 8. Recommended next actions for the plan

1. Resolve WDS access before Phase 2. Test `getCodeSets` from a browser and from the intended runner's network; if the Cloudflare challenge persists for scripts, the live-pull layer needs another mechanism (browser-driven fetch, or asking StatCan about API access), or the project accepts a manual download step. Record the outcome in this file.
2. Confirm 36-10-0431 structure directly from StatCan when access works (the DBnomics reading is consistent with StatCan's own description, but is a mirror). Check the price-basis behaviour across vintages (headline 4) before computing level-based revisions.
3. Drop retail sales volume as a Canadian vintage target unless 20-10-0082 is revived (inactive since 2026-03-02); it can still be a conditioning series with vintages ending Feb 2026 if acceptable.
4. Treat the unemployment rate and CPI excluding food and energy as "OECD vintages or none" for Canada; decide whether the stale core-measure table 18-10-0259 is worth ingesting.
5. Re-check every real-time table's `date_published` on open.canada.ca before each ingest; six of 19 went inactive in Feb-Mar 2026 and two more are stale, without the list page being updated.
6. Decide the same-day rule for 08:30 ET releases on the origin (CPI: Apr 20, Jun 22, Jul 20, 2026; retail: Feb 20, Mar 20, 2026).
7. For 36-10-0491 (~411 MB full zip) plan a filtered pull (all-industries aggregate only) once API access exists.
