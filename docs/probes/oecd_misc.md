# Probe: OECD STES revisions dataset, Canadian forecaster microdata, MACROCAST citation

Date of probe: 2026-11-17. Read-only; public sources only; no packages installed. Tools: curl, WebFetch, WebSearch.
Scratch files (API responses, CSV samples, ~11 MB total): `<session-scratchpad>/oecd\`

Evidence tags used below: **[primary]** = read directly from the API / source page; **[snippet]** = seen only in search-result summaries, not verified against the source.

---

## 1. OECD "Short-term economic statistics revisions" (`DSD_STES_REVISIONS@DF_STES_REVISIONS`)

### 1.1 Existence and identity [primary]

- Dataflow exists: `OECD.SDD.STES,DSD_STES_REVISIONS@DF_STES_REVISIONS,4.0` (isFinal=true). English name "Short-term economic statistics revisions".
- Description (from the dataflow metadata): "Access monthly data snapshots of published short term economic statistics and observe the revisions made to key economic variables. ... Revisions to time series published in subsequent editions of the Main Economic Indicators publication may be due to practices employed both by the national statistical institutes providing the data and the OECD." I.e. this is the successor to the old MEI Original Release Data and Revisions Database.
- Annotations of note: `NonProductionDataflow = true`; `ReleaseVersion = A`; `sdmx_metrics obs_count = 78,973,716` (~79M observations in the full flow). I did not confirm whether the dataflow is listed in the OECD Data Explorer UI (search found only a third-party mirror, baselight.app, and no official DE page) [snippet]. The `NonProductionDataflow` flag is reported as-is; I did not find documentation of what it means operationally.
- Only revision-type dataflow in the whole OECD catalogue by name search (8.9 MB `dataflow/all` listing grepped for vintage/real-time/revision/snapshot in English names): this one. **Trap:** the per-country `DSD_REV_OECD@DF_REVCAN`, `DF_REVISL`, etc. are *tax-revenue* datasets (agency OECD.CTP.TPS), not revisions. **No separate OECD Canada-specific or euro-area real-time dataset was found** by this name search of the SDMX dataflow catalogue.

### 1.2 Structure [primary]

Key dimensions (in order), 6 + time:

| pos | dimension | codelist | notes |
|---|---|---|---|
| 1 | REF_AREA | CL_AREA | 469 codes incl. CAN, EA11/EA18/EA19/EA20, USA, G7, OECD |
| 2 | FREQ | CL_FREQ | M, Q present |
| 3 | MEASURE | CL_MEASURE_REV | 22 codes, see below |
| 4 | UNIT_MEASURE | CL_UNIT_MEASURE | XDC (national currency), IX (index), PT_LF (% of labour force) |
| 5 | ACTIVITY | CL_ACTIVITY_ISIC4 | `_T`, `_Z`, `BTE`/`C` (industry), `G47` (retail) |
| 6 | **EDITION** | CL_EDITION | **the vintage**: `YYYYMM`, codelist spans 199902..202812 (359 codes, pre-populated ahead) |
| – | TIME_PERIOD | – | `YYYY-MM` or `YYYY-Qn` |

Attributes: OBS_STATUS, UNIT_MULT, DECIMALS, BASE_PER.

MEASURE codes relevant to the plan: `B1GQ_Q` GDP volume (Q, XDC); `P3_S1M_Q` household + NPISH final consumption volume (Q, XDC); `CP` consumer prices (M, IX); `UNEMP` unemployment rate (M, PT_LF); `PRVM` production volume = industrial production (M, IX, activity BTE and C); `TOVM` retail trade volume (M, IX, G47). Others: B1GQ_V, B1GQ_D, P3_S13_Q, P51G_Q, P6_Q, P7_Q, EMP, H_EARN, ULC, MABM (M3), CA, IM, EX, LI_AA, LI_TR, RS.

How vintages are encoded: one observation per (series, EDITION, TIME_PERIOD). The EDITION is the publication month of the snapshot; there is **no explicit publication date / release timestamp** attribute. There is no "first release" flag; you derive the revision triangle by pivoting TIME_PERIOD x EDITION.

Query grammar (verified):
```
https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES_REVISIONS@DF_STES_REVISIONS,4.0/{REF_AREA}.{FREQ}.{MEASURE}.{UNIT}.{ACTIVITY}.{EDITION}?startPeriod=...&endPeriod=...&format=csvfile
https://sdmx.oecd.org/public/rest/availableconstraint/OECD.SDD.STES,DSD_STES_REVISIONS@DF_STES_REVISIONS,4.0/CAN.....?references=none&mode=exact
```
`format=csvfilewithlabels` works but label columns contain quoted commas ("Gross domestic product, volume"); use `format=csvfile` or a real CSV parser. Empty positions = wildcard.

### 1.3 Coverage and vintage ranges [primary, from `availableconstraint`]

**Canada (CAN)** - all six target measures have **334 editions, 199902 -> 202611** (every monthly edition from Feb 1999 to Nov 2026):

| measure | freq | unit | activity | editions | time span in data |
|---|---|---|---|---|---|
| B1GQ_Q GDP vol | Q | XDC | _T | 199902-202611 (334) | 1961Q1-2026Q3 |
| P3_S1M_Q HH consumption vol | Q | XDC | _T | 199902-202611 (334) | 1961Q1-2026Q2 |
| CP CPI | M | IX | _Z | 199902-202611 (334) | 1949-01 to 2026-09 |
| UNEMP | M | PT_LF | _T | 199902-202611 (334) | 1956-01 to 2026-10 |
| PRVM IP | M | IX | BTE, C | 199902-202611 (334) | 1961-01 to 2026-08 |
| TOVM retail vol | M | IX | G47 | 199902-202611 (334) | 1961-01 to 2026-08 |

The plan's hope of Canadian vintages before 2015 is met: vintages start **February 1999**. (The earliest CPI vintage, edition 199902, contains CPI 1990-01..1998-12.) USA has the same 334-edition coverage.

**Euro area** - coverage exists but is a **splice across four composition codes**, with no single code spanning the sample:

| code | editions | measures |
|---|---|---|
| EA11 | 199905-200102 (22) | B1GQ_Q, B1GQ_V, B1GQ_D, CP, UNEMP, PRVM, TOVM, P3_S1M_Q, ... (no EMP, no H_EARN) |
| EA18 | 200103-201501 (167) | all six target measures (verified per measure) |
| EA19 | 201502-202303 (98) | all six target measures (verified per measure) |
| EA20 | 202304-202611 (44) | all six target measures (verified per measure) |
| EA / EA17 / EU15 | 1999-2008 | CLI measures only (LI_*, RS) |
| EA12, EA13, EA15, EA16, EU27_2020, EU28 | none | - |
| EU | 201507-202611 | EMP, EX, IM, UNEMP only |

Caveats: EA11 coverage was checked at area level only (the measure list above comes from the area-wide constraint), not per measure as for EA18/EA19/EA20. The "EA18" label on 2001-2014 editions is retroactive (EA18 did not exist in 2001); whether each edition's aggregate reflects the composition at the time or a fixed composition is not documented in the metadata I could reach. Treat the breaks at 200103, 201502 and 202304 as potential level/definition breaks. Euro-area vintages begin May 1999 (EA11, area-level check only) or March 2001 (EA18, verified per measure).

### 1.4 Is it maintained? [primary]

Yes. The most recent edition `202611` (November 2026) exists and carries data through 2026-10 (UNEMP) / 2026-09 (CPI) as of 2026-11-17. There is no explicit "last updated" timestamp in the SDMX structure; the reference-metadata endpoint (`/public/rest/metadata/dataflow/...`) returned HTTP 403. Editions appear monthly without gaps for CAN (334 editions for 334 months Feb 1999-Nov 2026).

### 1.5 Sample pulls and what the data look like [primary]

Files in the scratch dir:
- `sample_CAN_B1GQ_Q.csv` - CAN quarterly GDP volume, all editions, startPeriod 2023-Q1, `csvfilewithlabels` (96 KB, 326 rows, 42 editions 202306..202611).
- `sample_CAN_B1GQ_Q_nolabels.csv` - same, 2024-Q3..Q4, `csvfile`.
- `sample_CAN_CP_ed199902.csv` - CAN CPI, edition 199902 only (108 obs, 1990-01..1998-12).
- `sample_CAN_UNEMP_ed202611.csv` - CAN unemployment, edition 202611, 2026-01..2026-10.
- `chk_CP_199510.csv`, `chk_GDP_2010Q1.csv` - one fixed period across all editions (base-year check).
- `chk_UNEMP_recent.csv`, `chk_CP_recent.csv` - 2024-01 onward, all editions (timing check).
- `df.xml` (full structure, 1.8 MB), `allflows.xml` (all OECD dataflows, 8.9 MB), `avail_*.xml` (availability constraints).

CSV columns (`csvfile`): `DATAFLOW,REF_AREA,FREQ,MEASURE,UNIT_MEASURE,ACTIVITY,EDITION,TIME_PERIOD,OBS_VALUE,OBS_STATUS,UNIT_MULT,DECIMALS,BASE_PER`.

Example revision path, CAN GDP volume level for 2024-Q4 (CAD): ed 202502 = 607.31bn; 202503-202505 = 611.10bn; 202506-202511 = 610.70bn; 202512 onward = 621.07bn (annual/comprehensive revision in Dec 2025 edition).

**Usability caveats found (important for modelling):**
1. **Levels are not comparable across editions; BASE_PER is unreliable.** CAN CPI for 1995-10 reads 111.94 in 1999 editions, 100.18 (2000-2004), 91.96 (2005-2009), 81.98 (2010-2013), 75.3 (2014-2018), 69.29 (2019-2026) - each vintage keeps its own original index base, yet `BASE_PER` is reported as `2015` for every edition. GDP volume levels similarly jump at chain-reference-year changes (328bn -> 393bn -> 430bn -> 457bn for 2010-Q1) with `BASE_PER` empty. Work in growth rates / log-differences within each vintage; do not compare levels across editions.
2. **Edition timing is approximate and not uniform across series.** Latest observation per edition (CAN): CPI edition `202611` -> 2026-09, `202610` -> 2026-08 (month M-2, consistent with a snapshot taken before the mid-month CPI release). UNEMP `202611` -> 2026-10 (month M-1). GDP: each quarter first appears in the edition two months after quarter end (2022-Q1 -> 202205, ..., 2024-Q4 -> 202502, 2026-Q3 -> 202611), with one 3-month exception (2025-Q4 -> 202603). Statistics Canada normally publishes quarterly GDP about two months after quarter end, near month-end (release calendar not checked in this probe), so the GDP snapshot appears to be taken later in the month than the CPI snapshot. There are also stale repeats (CPI editions 202508 and 202509 both end at 2025-05; UNEMP 202501 and 202502 both end at 2024-12). Conclusion: the EDITION is "data as published by the OECD in that month", not a precise information set; snapshot timing differs by source dataset. For strict real-time exercises align against national release calendars, or accept +-1 month uncertainty.
3. The labels CSV quotes commas in names; prefer `format=csvfile`.
4. Full flow is ~79M observations; pull by (area, measure) with edition/time filters. Each CAN measure x all editions is roughly 334 editions x up to ~900 periods; sizes are manageable (tens of MB per series at most).

### 1.6 Terms of use [primary]

OECD Terms and Conditions, https://www.oecd.org/en/about/terms-conditions.html ("Last updated on 1 July 2024"; page fetched successfully with curl + browser-like headers after a 403 on the default UA; WebFetch returned 403; the old `t4.oecd.org/termsandconditions` redirects to the homepage). Data clause, quoted:
> "Except where additional restrictions apply as stated above, you can extract from, download, copy, adapt, print, distribute, share and embed Data for any purpose, even for commercial use. You must give appropriate credit to the OECD by using the citation associated with the relevant Data, or, if no specific citation is available, you must cite the source information using the following format: OECD (year), (dataset name),(data source) DOI or URL (accessed on (date)). When sharing or licensing work created using the Data, you agree to include the same acknowledgment requirement in any sub-licenses that you grant, along with the requirement that any further sub-licensees do the same."

Also: OECD written content published from 1 July 2024 is CC BY 4.0. Restriction: the user is responsible for checking dataset metadata for third-party ownership or additional restrictions; the dataset-level reference metadata endpoint returned 403 for me, so I could not confirm the absence of dataset-specific restrictions for this flow. Research use and redistribution of derived results: allowed under the general terms with attribution, and any redistributed data/derived data must carry the same acknowledgment requirement downstream.

---

## 2. Public individual-level professional forecaster data for Canada

**Conclusion: none found among the sources checked.** Every public Canadian source I could read publishes only averages or quantiles; the one named candidate I could not read (Conference Board of Canada "Survey of Forecasters", paywalled per search snippets, page unreachable due to an expired TLS certificate) remains unverified. Respondent-level panels are known to exist only in paid sources (Consensus Economics, Bloomberg) which the plan excludes. Details:

| source | what is public | individual-level? | notes |
|---|---|---|---|
| Finance Canada, Department of Finance Private Sector Survey (quarterly-ish; e.g. Mar 2026 page) [primary] | Averages of private-sector forecasts: real GDP growth, unemployment rate, employment growth, CPI, CPIX, GDP inflation, 3m T-bill, 10y bond, USD/CAD, US GDP/CPI/rates, WTI, Henry Hub; annual horizons (2026-2030 in Mar 2026 edition) | **No.** Tables titled "Average Private Sector Economic Forecasts"; no downloadable data file; forecasters not named on recent pages | The June 2014 backgrounder [primary] named 14 participants (BMO, CDPQ, CFIB, CIBC, Conference Board, Desjardins, Deutsche Bank Canada, IHS Global Insight, Laurentian, National Bank, RBC, Scotiabank, TD, U of Toronto PEAP); that list is from 2014. Open Canada portal has briefing-note summaries, not raw responses [snippet]. |
| Bank of Canada, Market Participants Survey (quarterly; editions seen back to Q2 2023 in search results, start date not checked) [primary, Q3-2025 page] | 25th pct / median / 75th pct of ~25-30 financial-market participants for GDP growth, CPI, policy rate path, neutral rate, yields, oil, CAD; average probabilities over ranges | **No.** "Individual responses are not shown." | Respondents are market participants, not a forecaster panel; short history. |
| Bank of Canada, Business Outlook Survey / Canadian Survey of Consumer Expectations | firms / households | n/a | not forecasters; excluded by the task. |
| Bank of Canada, Staff Economic Projections database (Champagne, Poulin-Bellisle, Sekkel; SWP 2018-52; JAE 2020) [primary page] | Bank staff forecast vintages for 22 variables, 1970Q4/1982Q2-2019Q4 (released annually with a 5-year lag), CSV/JSON/XML via Valet API | Single institution, not a panel | The working paper's title/abstract describe "a new database of real-time data and forecasts"; the download page itself lists forecast vintages, and I did not confirm that real-time *data* vintages are in the download. No private-sector forecaster data included. |
| Conference Board of Canada, "Survey of Forecasters" [snippet only; page fetch failed: TLS certificate expired] | Quarterly survey of Canada's forecasting organisations; headline results in press items | Unknown; product appears paywalled (~CAD 320 per edition per search snippet) | Not verified. |
| C.D. Howe Institute [snippet] | Commentary, Business Cycle Council statements | No forecast panel data found | - |
| ECB SPF [primary] | Euro-area HICP, GDP, unemployment; anonymised **individual** microdata downloadable (SPF_individual_forecasts_by_round.zip, SPF_microdata_by_variable.zip) | Yes, but **euro area only; no Canada** | Useful for the euro-area leg of the project, not Canada. |
| Philadelphia Fed SPF | US only | yes | not Canada. |
| Academic: Siklos (2013 JIE; 2012 IJF), Yetman (BIS WP 523) [snippet] | Use Consensus Economics individual data for Canada | Underlying data proprietary | Confirms that the Canadian individual-level literature relies on Consensus Economics. |
| Consensus Economics, Bloomberg, FocusEconomics | - | yes | paid; excluded. |

Public **mean/consensus-type** Canadian series usable for a mean-forecast comparison:
1. Finance Canada private-sector survey averages (annual-horizon GDP, CPI, unemployment; archive pages seen back to 2014; published several times a year) [primary]. Would need scraping of HTML tables across editions.
2. Bank of Canada Market Participants Survey medians (quarterly; editions seen from Q2 2023) [primary].
3. Bank of Canada Staff Economic Projections database (single institution, vintages to 2019Q4) [primary].
4. Not checked in this probe but worth a look as single-institution public forecast records: Bank of Canada Monetary Policy Report projections, IMF WEO and OECD Economic Outlook historical forecasts for Canada.

---

## 3. MACROCAST citation check

### 3.1 arXiv 2606.28670 resolves [primary, arXiv API + abs page + HTML full text]

- **Title:** MACROCAST: A Vintage-Consistent Time Series Foundation Model for Real-Time Macroeconomic Forecasting
- **Authors:** Andrea Carriero, Davide Pettenuzzo, Shubhranshu Shekhar
- **Submitted:** 27 June 2026 (v1; only version as of today). Categories econ.EM (primary), cs.AI, cs.LG.
- **Abstract (gist):** introduces a lightweight TSFM pretrained on synthetic series, then fine-tuned on synthetic series drawn from BVAR/DFM/ARIMA models estimated on vintage-specific ALFRED data, so no revised or future values enter training. Evaluated on FRED-MD in a real-time out-of-sample exercise; beats AR(1) on ~80% of series-horizon pairs, matches or surpasses Chronos-2, outperforms BVAR and DFM.
- **Full-text details:** US-only (FRED-MD/ALFRED), 123 series (14 of 137 dropped), out-of-sample Aug 1999-Dec 2024 (Jan-Jun 2020 targets dropped), horizons h=0..12. Competitors: AR(1), BVAR, DFM, Chronos-2 and Moirai2-Small (zero-shot, public weights). TimesFM is only cited, not run. Actuals = the FRED-MD vintage released about six months after the target date. Model weights public: https://huggingface.co/shubhranshu/MacroCast (Apache-2.0; one checkpoint per fine-tuning vintage, manifest.json, forecast.py); backbone vendored from TempoPFN (automl/TempoPFN).

**Does it match the plan's description?** Partly. The ID, FRED-MD, real-time vintages and TSFM comparison are right. But the plan describes it as "a US-data study evaluating time-series foundation models on FRED-MD with real-time vs revised data". The paper is primarily a **new model proposal** (vintage-consistent TSFM), and it evaluates **only with real-time vintages**; the full HTML text (both halves read) contains no real-time-vs-revised counterfactual, no evaluation against latest-vintage actuals, no non-US data, no TimesFM run, and no code/weights link (weights are on Hugging Face but the paper text does not link them). The plan's wording should be corrected to: "Carriero, Pettenuzzo and Shekhar (2026) propose MACROCAST, a vintage-consistent TSFM, and benchmark it against Chronos-2, Moirai2-Small, AR(1), BVAR and DFM on real-time FRED-MD vintages (US only), scoring against six-month-delayed actuals."

The companion/earlier paper is arXiv 2407.00890, "Macroeconomic Forecasting with Large Language Models" (same authors; v1 Jul 2024, v5 17 Aug 2026), a zero-shot evaluation of time-series language models on FRED-MD, finding them broadly comparable to or slightly worse than BVAR/factor models [primary abs page; vintage treatment not stated on the page].

### 3.2 Landscape: 2025-2026 TSFM-on-macro papers, especially real-time and non-US

| paper | verified? | data / country | real-time vintages? | models | note |
|---|---|---|---|---|---|
| Carriero, Pettenuzzo, Shekhar, MACROCAST, arXiv 2606.28670 (Jun 2026) | primary | US FRED-MD, 123 series | yes (ALFRED; 6-month-delayed actuals) | MacroCast, Chronos-2, Moirai2-Small, AR, BVAR, DFM | closest prior to the plan; US only |
| Carriero, Pettenuzzo, Shekhar, arXiv 2407.00890 (v5 Aug 2026) | primary (abs) | US FRED-MD | not stated on abs page | time-series LMs vs BVAR/DFM | zero-shot evaluation |
| Dass, Racheter, Scheufele, Stucki, Vollmer, Winter (SNB), "Real-Time Macroeconomic Forecasting with Time Series Foundation Models", slides at BoE CCBS event, June 2026 | snippet only (PDF saved but could not be rendered: no poppler; WebFetch could not extract text) | Swiss / daily FX (EUR/CHF, USD/CHF, EUR/USD) and macro | claims a real-time design; flags look-ahead bias | Chronos-2, TimesFM, TimeGPT, RW, BVAR | no working paper found; nearest non-US real-time TSFM study |
| Larsen and Thorsrud, "Zero-Shot Conditional Forecasting and the Information Content of Central Bank Paths", CESifo WP 12972 (2026) | primary (abs) | Norway (Norges Bank), replications Sweden, New Zealand | not stated | Chronos-2 (multivariate, zero-shot) vs hard-conditioned VAR | non-US; conditional forecasting angle. A BI Norwegian Business School CAMP WP 05/2026 with a matching description surfaced in search [snippet]; probably the same paper, not confirmed. |
| Jetwiriyanon, Susnjak, Ranathunga, "Generalisation Bounds of Zero-Shot Economic Forecasting using TSFMs", arXiv 2506.15705 (v2 Aug 2025; also MLKE 7(4):135) | primary (abs); country from snippet | New Zealand (RBNZ forecasts as benchmark) | mentions vintage revisions as a problem; not a vintage design | Chronos, Moirai, TimeGPT | non-US |
| Koyuncu, Kwon, Lombardi, Perez-Cruz, Shin, "Introducing BISTRO", BIS WP 1337 (Mar 2026) | primary (abs) | BIS multi-country macro repository (countries not listed on page) | not mentioned | BISTRO (own TSFM) vs econometric benchmarks; snippet mentions AR(1), MOIRAI | code: github.com/bis-med-it/bistro |
| Ebrahim, Ali, El-Kotory, "Foundation or Formula? ... TimesFM-3 ...", arXiv 2610.00589 (30 Sep 2026) | primary (abs) | simulated series, M4, 101 macro series post-training-cutoff (geography not stated on abs page; a snippet says FRED-MD Aug 2026 vintage) | single vintage | TimesFM-3, TiRex, Chronos-2 (per snippet), AutoARIMA, ETS | not a real-time study |
| arXiv 2607.14279, "From Vector Autoregressions to AI-based Time Series Forecasting: A Review" (2026) | snippet | review | - | Chronos, TimesFM, Moirai | survey; stresses post-cutoff evaluation |
| arXiv 2509.07036 | snippet | US unemployment, Chronos zero-shot | - | Chronos | causal-analysis framing |

Gap statement supported by this probe: I found **no 2025-2026 paper evaluating off-the-shelf TSFMs on real-time vintages for Canada or the euro area**. Non-US work exists for Switzerland (slides only), Norway/Sweden/NZ (conditional forecasting), and New Zealand (zero-shot, no vintage design). ECB/Bundesbank/Banque de France/Bank of England/Bank of Canada working papers on TSFMs did not surface in searches (one BoC 2026 staff analytical paper on "non-traditional data and AI" surfaced, contents unverified).

---

## 4. URL log

| URL | result |
|---|---|
| https://sdmx.oecd.org/public/rest/dataflow/OECD.SDD.STES/DSD_STES_REVISIONS@DF_STES_REVISIONS/latest?references=all | 200, 1.8 MB structure |
| https://sdmx.oecd.org/public/rest/dataflow/all/all/latest | 200, 8.9 MB |
| https://sdmx.oecd.org/public/rest/availableconstraint/OECD.SDD.STES,DSD_STES_REVISIONS@DF_STES_REVISIONS,4.0/CAN.......?references=none&mode=exact | 403 "Not enough key values in query, expecting 6 got 8" (wrong key length) |
| .../availableconstraint/.../{CAN,EA20,EA19,EA18,EA11,EA,EA12,EA13,EA15,EA16,EA17,EU,EU15,EU27_2020,EU28,USA,OECD,G7}.....?references=none&mode=exact | 200 each |
| .../availableconstraint/.../{CAN,EA18,EA19,EA20}..{B1GQ_Q,CP,UNEMP,PRVM,TOVM,P3_S1M_Q}... | 200 each (first EA20 pass showed zeros without HTTP codes captured; re-run with codes gave 44 editions each - treat the first pass as transient) |
| https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES_REVISIONS@DF_STES_REVISIONS,4.0/CAN.Q.B1GQ_Q...?startPeriod=2023-Q1&format=csvfilewithlabels | 200, 96 KB |
| .../data/.../CAN.M.CP...199902?format=csvfilewithlabels | 200 |
| .../data/.../CAN.M.UNEMP...202611?format=csvfilewithlabels&startPeriod=2026-01 | 200 |
| .../data/.../CAN.Q.B1GQ_Q...?startPeriod=2024-Q3&endPeriod=2024-Q4&format=csvfile | 200 |
| .../data/.../CAN.M.CP...?startPeriod=1995-10&endPeriod=1995-10&format=csvfile | 200 |
| .../data/.../CAN.Q.B1GQ_Q...?startPeriod=2010-Q1&endPeriod=2010-Q1&format=csvfile | 200 |
| .../data/.../CAN.M.{UNEMP,CP}...?startPeriod=2024-01&format=csvfile | 200 |
| https://sdmx.oecd.org/public/rest/metadata/dataflow/OECD.SDD.STES/DSD_STES_REVISIONS@DF_STES_REVISIONS/4.0?detail=full | 403 |
| https://www.oecd.org/en/about/terms-conditions.html | WebFetch 403; curl default UA 403; curl with browser headers 200 (text quoted above) |
| https://t4.oecd.org/termsandconditions | 301 -> https://www.oecd.org/ (not useful) |
| https://web.archive.org/web/2026/https://www.oecd.org/en/about/terms-conditions.html | blocked by tool ("unable to fetch from web.archive.org") |
| https://social-science-data-editors.github.io/reference/information/OECD.html | 200 (summary of OECD terms, snapshot 2023-10-08) |
| https://arxiv.org/abs/2606.28670 ; https://export.arxiv.org/api/query?id_list=2606.28670 ; https://arxiv.org/html/2606.28670v1 | 200 each (HTML read in full, two passes) |
| .../data/.../CAN.Q.B1GQ_Q...?startPeriod=2022-Q1&format=csvfile | 200 (first-appearance-by-quarter check) |
| https://huggingface.co/shubhranshu/MacroCast | 200 |
| https://arxiv.org/abs/2407.00890 ; https://arxiv.org/abs/2610.00589 ; https://arxiv.org/abs/2506.15705 | 200 each |
| https://econpapers.repec.org/RePEc:ces:ceswps:_12972 | 200 |
| https://www.bis.org/publ/work1337.htm | 200 |
| https://www.bankofengland.co.uk/-/media/boe/files/events/2026/y-stucki-slides.pdf | downloaded (1.6 MB) but text not extractable (no pdftotext/poppler; WebFetch saw binary only) |
| https://www.canada.ca/en/department-finance/services/publications/private-sector-survey/2026/03.html | 200 |
| https://www.canada.ca/en/news/archive/2014/06/results-department-finances-june-2014-survey-private-sector-economists.html | 200 |
| https://www.bankofcanada.ca/2025/11/market-participants-survey-third-quarter-of-2025/ | 200 |
| https://www.bankofcanada.ca/2018/10/staff-working-paper-2018-52/ ; https://www.bankofcanada.ca/rates/staff-economic-projections/ | 200 each |
| https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/index.en.html ; .../all_data.en.html | 200 each |
| https://www.conferenceboard.ca/product/survey-of-forecasters-october-2020/ | WebFetch failed: "certificate has expired"; not retried insecurely |
| WebSearch queries (10+) on Canadian forecaster data, OECD revisions, TSFM macro papers | returned the snippets cited above |
