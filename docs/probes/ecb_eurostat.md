# Probe: euro-area data sources (ECB RTD vintages, Eurostat latest data, ECB SPF)

Probe date: 2026-11-17/18 (UTC). Read-only, public endpoints, no keys. Tools: curl 8.18, Python stdlib (`-I -X utf8`), WebFetch, WebSearch.
Sample files: `<session-scratchpad>/{ecb,eurostat,spf}\` (listed at the end).

Status labels: **confirmed** / **changed-from-plan** / **unavailable** / **not confirmed** (could not verify in this probe; do not assume).

Text in quotation marks was read from raw HTML/CSV/PDF we downloaded. WebFetch results are model summaries and are marked "(WebFetch summary)".

---

## A. ECB Real Time Database (RTD)

### A.1 Identity, status, update cadence

| Item | Finding | Status |
|---|---|---|
| Dataflow | `ECB:RTD(1.0)` "Real Time Database (research database)", DSD `ECB_RTD1`. 278 series keys in total: 267 `REF_AREA=S0`, 6 `US`, 5 `JP`. | confirmed |
| Experimental label | Dataset page text: "The Euro Area Real-Time Database (RTDB) is an experimental dataset that consists of vintages, or snapshots, of time series of several variables, based on series reported in the ECB's Economic Bulletin (EBu), and previously in the ECB's Monthly Bulletin (MoBu)." Also: "the dataset should be used for research purposes only and the time series included should not be treated as reference data." | confirmed |
| Still updated | Page: "Dataset last update 28 October 2026 15:30 CET". Latest `VALID_FROM` seen in data: `2026-10-28T14:30:00Z`. Page also says "It is updated semi-annually, at the beginning of January and July." That text conflicts with the observed per-Governing-Council vintages (8 in 2025, 6 so far in 2026); reported as-is, not reconciled. | confirmed (live), text inconsistent |
| Vintage timing | Page: "The 'freezing' procedure always takes place on a working day ahead of the Governing Council meeting at precise time 3.30 p.m." Observed `VALID_FROM` timestamps are 13:30Z/14:30Z (= 15:30 CET/CEST) on the eve of monetary-policy meetings, e.g. 2025-06-04, 2025-07-23, 2025-09-10, 2025-10-29, 2025-12-17, 2026-02-04, 2026-03-18, 2026-04-29, 2026-06-10, 2026-09-09, 2026-10-28. Frequency: 12 vintages/year 2001-2014 (Monthly Bulletin), 8/year from 2015 (Economic Bulletin; 7 in 2022). | confirmed |
| Vintage convention | Vintages are **ECB internal frozen-database snapshots**, not Eurostat release snapshots. Page: "All indicators in the dataset follow a so called 'policy concept', i.e. they are reported according to the methodology adopted at the time of their publication." Technical doc (`rtdb_docu.pdf`) marks several series "SOURCE: ECB calculations based on Eurostat data" (e.g. seasonally adjusted/ULC series). HICP and national-accounts series point to Eurostat-sourced ECB series via `DOM_SER_IDS`. | changed-from-plan (if the plan assumed "as published by Eurostat") |

Implication for a "20th of month" forecast origin: vintage dates follow the Governing Council calendar, so the most recent vintage at an origin is typically 5-8 weeks old since 2015 and can be older over the summer break. From the HICP history (259 dated vintages): gaps of 91 days (2026-06-10 -> 2026-09-09; no July 2026 vintage) and 98 days (2022-04-13 -> 2022-07-20); next largest 56-57 days. Short years: 11 vintages in 2007 and 2009, 7 in 2022, 6 so far in 2026 (02-04, 03-18, 04-29, 06-10, 09-09, 10-28). There is no Eurostat-release-aligned vintage in RTD.

### A.2 Key structure and how vintages are encoded

Series key: `RTD.{FREQ}.{REF_AREA}.{ADJUSTMENT}.{RT_ECON_CONCEPT}.{RT_DENOM}` (5 dimensions + `TIME_PERIOD`). Vintages are **not** a dimension.

- `FREQ`: A/M/Q. `REF_AREA`: `S0` = "Euro area (moving concept in the Real Time database context)" (also US, JP for a few series).
- `ADJUSTMENT` (CL_ADJUSTMENT): N none, S seasonally adj., W working-day adj., Y seasonally + working-day adj.
- `RT_ECON_CONCEPT` (CL_RT_ECON_CONCEPT, 263 codes; prefixes: C_ financial rates/equity, E_ exchange rates, F_ government finance, G_ national accounts, I_ industrial production/cars, L_ labour, M_ money/credit, O_ retail turnover, P_ prices, T_ trade, X_ BoP, Y_ EC surveys).
- `RT_DENOM` (CL_RT_DENOM): A annual growth rate, E euro, F percentage, I interest rate, M persons, P growth to previous period, X index, Z n/a, etc.
- Attributes include `DOM_SER_IDS` (underlying ECB Data Portal series key), `UNIT_INDEX_BASE`, `TITLE`, `TITLE_COMPL`, `SOURCE_DETAIL`.

**Vintage retrieval** = `includeHistory=true` on the data endpoint. This returns a change log, not snapshots: one row per (TIME_PERIOD, change), with extra columns `ACTION` (`Replace` / `Delete`), `VALID_FROM`, `VALID_TO`. A row appears only when the value for that period changed in that vintage; `VALID_TO` is filled only on `Delete` rows (all `Replace` rows had empty `VALID_TO` in our samples). Rebuilding the vintage as of time *t* therefore requires an as-of join: for each `TIME_PERIOD`, the latest row with `VALID_FROM <= t` (and not deleted). Rebasing shows up as a revision (e.g. HICP Jan-2000 value went 75.13 -> 58.35 in the 2026-02-04 vintage when the index base moved to 2025=100).

Documented ECB example (on the dataset page): `https://data-api.ecb.europa.eu/service/data/RTD/A.S0.N.F_CEC_CGG_D0.F?includeHistory=true&format=csvdata`.

### A.3 Date range

| Claim | Finding | Status |
|---|---|---|
| Plan: vintages from Jan 2001; 2015+ via API, earlier as bulk files | Page text agrees ("RTD vintages from 2015 onwards can be extracted using ECB Data Portal web services"; "Vintages as of January 2001 up to December 2014 for all variables can be downloaded in different files by frequencies monthly, quarterly, annual"; "Selected 38 variables containing data vintages prior to January 2001 can be downloaded from this file"). **But the API actually returns history back to `VALID_FROM 2001-01-03` for all seven target keys tested** (ESI `Y_ESIND` from 2002-02-06). Full HICP history: 260 distinct `VALID_FROM` from 2001-01-03 to 2026-10-28, 2,627 rows, 1.0 MB. | changed-from-plan (API covers 2001+) |
| Bulk files | `monthly.zip` 26.98 MB, `quarterly.zip` 5.0 MB, `annual.zip` 0.38 MB (one CSV per vintage month 2001-01 .. 2014-12, e.g. `quarterly_200101.csv`; wide format: row 0 block titles, row 1 `Name:` = original SDW key per column (e.g. `ESA.Q.I2.S.0000.B1QG00.1000.TTTT.Q.U.A` in 2001-01, `MNA.Q.Y.I7.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N` in 2014-12), row 2 `Description:`, row 3 `comments:`, then periods labelled `Q1-2000` with `NA` for missing). `rtdb38.zip` 4.65 MB = 44 `.xls` files (`le38/*.xls`) for the pre-2001 38-variable set (not parsed; binary xls). | confirmed |
| Bulk vs API consistency | GDP Q1-2000 in `quarterly_200101.csv` = 1508045.76 = API row `VALID_FROM 2001-01-03`. In `quarterly_201412.csv` = 2096450.11281 = API row `VALID_FROM 2014-11-05` (no Dec-2014 row because unchanged). | confirmed (one spot check) |

### A.4 Target series: keys, vintages, liveness

Liveness measured with a whole-flow `lastNObservations=1` pull (2026-11-18) and full `includeHistory` pulls.

| Target | RTD key | Underlying (`DOM_SER_IDS`) | Last obs. period | Last vintage | Status |
|---|---|---|---|---|---|
| Real GDP, chain-linked volumes, SA | `RTD.Q.S0.S.G_GDPM_TO_C.E` | `MNA.Q.Y.I10.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N` | 2026-Q2 | 2026-10-28 | confirmed, live; vintages from 2001-01-03 |
| HICP all items (index) | `RTD.M.S0.N.P_C_OV.X` (base now "2025 = 100"); annual rate `RTD.M.S0.N.P_C_OV.A` | `HICP.M.U2.N.000000.4D0.INX` | 2026-09 | 2026-10-28 | confirmed, live; vintages from 2001-01-03 |
| HICP excl. energy, food, alcohol, tobacco (HICPX) | **none**. Closest is `RTD.M.S0.N.P_C_XEFUN.X` = "HICP - All-items excluding energy and unprocessed food" (a different aggregate), and it is **stale**: last obs 2025-05, last vintage 2025-06-04, no 2026 rows in full history (2,478 rows, 249 vintages 2001-01-03 .. 2025-06-04). Live components `P_C_SERV.X` (services) and `P_C_IGXE.X` (non-energy industrial goods) exist but HICPX cannot be rebuilt from them without weights (not in RTD). | | | | unavailable |
| Unemployment rate | `RTD.M.S0.S.L_UNETO.F` (persons: `.M`) | `LFSI.M.I10.S.UNEHRT.TOTAL0.15_74.T` | 2026-08 | 2026-10-28 | confirmed, live; vintages from 2001-01-03 |
| Industrial production excl. construction | `RTD.M.S0.Y.I_XCONS.X` (SA+WDA, base 2021=100); `RTD.M.S0.W.I_XCONS.X` (WDA only) | `STBS.M.I10.Y.PROD.NS0020.4D0.N.IX` | **2025-08** | **2025-10-29** | changed-from-plan: **stale** (no 2026 vintages; full history 47,961 rows, 253 vintages 2001-01-03 .. 2025-10-29) |
| Retail trade volume | `RTD.M.S0.Y.O_RTXMOTVD.X` ("Total Turnover Index, deflated, Retail trade, except of motor vehicles and motorcycles", SA+WDA, base 2021=100) | `STBS.M.I10.Y.TOVV.2G4700.4D0.N.IX` | **2025-08** | **2025-10-29** | changed-from-plan: **stale** (no 2026 vintages; full history 30,719 rows, 248 vintages 2001-01-03 .. 2025-10-29) |
| Household final consumption (candidate) | `RTD.Q.S0.S.G_FCHI_TO_C.E` = "Final consumption of households and NPISHs (private consumption) - Chain linked volumes" | `MNA.Q.Y.I10.W0.S1M.S1.D.P31._Z._Z._T.EUR.LR.N` | 2026-Q2 | 2026-10-28 | confirmed, live; vintages from 2001-01-03; note it includes NPISH |

Liveness of the whole S0 block (last observation period per series from `rtd_last1_all.csv`, pulled 2026-11-18): **174 monthly S0 series: 88 end at 2026-07 or later (live); 86 end at 2025-08 or earlier (stale), 79 of them between 2024-11 and 2025-08.** So about half of the monthly series stopped being updated in the year to Aug 2025. Breakdown of stale last periods: 18 end 2025-08 (IP block, retail deflated turnover, PPI), 16 end 2025-05 (`P_C_XEFUN` and 15 EC-survey sub-questions), 7 end 2025-04 (`Y`-adjusted money/credit, base money), 17 end 2025-03 (monthly BoP `X_*`, IP sub-indices `I_DCOGO/I_INDTO/I_NCOGO/I_XCOEN`, nominal retail `O_RTXMOTV`, PPI durable goods), 13 end 2025-02 (trade unit-value indices `T_*_U`), 8 end 2024-11 (benchmark yields `C_U202Y..C_U210Y`, oil `P_OILBR`, raw-material prices `P_R_*`), 7 earlier (`C_EONIA` 2021-12, Libor series, two retail sub-sectors, `W`-adjusted car registrations). Quarterly: 74 of 79 end 2026-Q2/Q3; 5 stale (`G_TLSP_TO_U` 2024-Q4; labour-cost indices `L_H_CONST/L_H_SERV/L_H_XCONS` and `Y.L_H_WXAFG` 2025-Q1). Annual: 14 series, last 2024 (6) or 2025 (8). **The cause is not stated anywhere we found; treat as unknown.** `updatedAfter=2026-01-01` flagged 190 series incl. `P_C_XEFUN.X` as updated, yet its `includeHistory` shows no 2026 observation changes, so `updatedAfter` is not a reliable liveness indicator (probably attribute-level updates). No live substitute exists in RTD for IP, retail or PPI: the only `I_*`/`O_RT*`/`P_P_*` key with a 2026 observation is `RTD.M.S0.Y.I_NCARS.Q` (car registrations).

### A.5 Candidate conditioning set in RTD (from the last-observation table, `rtd_last1_all.csv`)

Live monthly S0 series (last obs 2026-07 or later; `RTD.M.S0.` prefix omitted):
- Prices: `N.P_C_OV.X` / `N.P_C_OV.A` HICP total; components `N.P_C_SERV.X`, `N.P_C_GOOD.X`, `N.P_C_IGXE.X` (non-energy industrial goods), `N.P_C_NRGY.X`, `N.P_C_FOOD.X`, `N.P_C_FOODPR.X`, `N.P_C_FOODUN.X`, `N.P_C_HOUS.X`, `N.P_C_TRAN.X`, `N.P_C_COMM.X`, `N.P_C_RECR.X`, `N.P_C_MISC.X` (all 2026-09).
- Labour: `S.L_UNETO.F/.M` (total unemployment rate / persons), `S.L_FMU25.F/.M` (15-24), `S.L_FMO25.F/.M` (25-74), `S.L_FETOT.F/.M`, `S.L_MATOT.F/.M` (2026-08).
- Money/credit (adjustment `N`): `N.M_M1_V_NC.E`, `N.M_M2_V_NC.E`, `N.M_M3_V_NC.E`, `N.M_LOAN_U_NG.E`, `N.M_LOANSEC_U_NG.E`; `Y.M_M3BM_V_NC.A` M3 annual growth (2026-09).
- Surveys (headline only): `S.Y_ESIND.F` ESI, `S.Y_CSCCI.F` consumer (2026-10), `S.Y_ISICI.F` industry, `S.Y_SSSCI.F` services, `S.Y_RSRCI.F` retail, `S.Y_COCCI.F` construction confidence (2026-09).
- Financial: `N.C_EUR1M/3M/6M/1Y.E` Euribor; `N.C_DJESB.X`, `N.C_DJE50.X` and 10 Euro Stoxx sector indices; `N.C_SP500.X`, `N.C_NIKKE.X`; `N.E_EN00_NGR/BGR.X` NEER, `N.E_ERC0_NGR/BGR.X`, `N.E_ERP0_NGR.X` REER (2026-09).
- Trade/BoP: `N.T_XTTT.X`, `N.T_MTTT.X`, `S.T_XTTT.E`, `S.T_MTTT.E` extra-EA trade values (2026-08); BEC/SITC breakdowns `S.T_X*/T_M*.E` and volume indices `*_V.X` (2026-07); `N.X_KA1C_A1.E`, `N.X_KA1D_A1.E` capital account (2026-08).
- Other: `Y.I_NCARS.Q` new car registrations (2026-09).

Live quarterly S0 series (2026-Q2; `RTD.Q.S0.` prefix omitted): `S.G_GDPM_TO_C.E/.D.X/.U.E`, `S.G_FCHI_TO_C.E/.D.X/.U.E`, `S.G_FCGG_TO_*`, `S.G_GFCF_TO_*`, `S.G_XGS_TO_*`, `S.G_MGS_TO_*`, `S.G_CIAXDV_TO_U.E`, `S.G_DDIS_TO_D.X`, `S.G_TLSP_TO_O.E`, gross value added by branch `S.G_GVAD_*_O/U.E`; employment `S.L_TEMP_TO.M`, `N.L_TEMP_TO.M`, `N.L_EMP_TO.M`, `N.L_SEMP_TO.M`, branch employment `N.L_TEMP_*.M`; `S.L_ULC_TO.X` and branch ULC; labour cost index `W.L_H_WXAFG.X`, `W.L_HW_WXAFG.X`, `W.L_HC_WXAFG.X`; `S.Y_ISLCU.F` capacity utilisation (2026-Q3); `N.E_ERU1_NGR.X` ULC-deflated REER; `N.P_CO_RESB.X` construction prices.

Stale (last obs between 2024-11 and 2025-08; usable for backtests up to their last vintage only): all industrial production `W./Y.I_*` incl. `I_XCONS`, `I_MANUF`, `I_INDTO`, MIG breakdowns; retail `Y.O_RTXMOTVD.X`, `Y.O_RTXMOTV.X`, `Y.O_RTFOBETD.X`, `Y.O_RTNONFOD.X`; PPI `N.P_P_*_DS.X`; `N.P_C_XEFUN.X`; benchmark yields `N.C_U202Y..C_U210Y.E`; oil `N.P_OILBR.E`; raw materials `N.P_R_TO.E`, `N.P_R_XNRGY.E`; monthly BoP `N.X_XA1*/XG1*/XI1*/XS1*/XT1*.E`; trade unit values `*_U.X`; `Y`-adjusted money/credit `Y.M_M1/M2/M3_V_NC.E`, `Y.M_LOAN*_U_NG.E`, `N.M_M3BM_C_WN.E`; EC-survey sub-questions `S.Y_CS*12.F`, `S.Y_IS*.F`, `S.Y_RS*.F`, `S.Y_SS*.F`, `S.Y_CO*.F` (other than the confidence indicators above). Earlier still: `C_EONIA` (2021-12), Libor series, `W.I_NCARS.Q`, two retail sub-sectors.

Not in RTD: PMI, any HICP excluding energy, food, alcohol and tobacco, Eurostat flash estimates as separate series.

### A.6 Sample pull

`https://data-api.ecb.europa.eu/service/data/RTD/M.S0.N.P_C_OV.X?format=csvdata&startPeriod=2025-01&endPeriod=2025-03` -> HTTP 200, 1,463 bytes, 3 data rows. Columns: `KEY,FREQ,REF_AREA,ADJUSTMENT,RT_ECON_CONCEPT,RT_DENOM,TIME_PERIOD,OBS_VALUE,OBS_STATUS,OBS_CONF,OBS_PRE_BREAK,OBS_COM,TIME_FORMAT,COLLECTION,COMPILING_ORG,DISS_ORG,DOM_SER_IDS,PUBL_MU,PUBL_PUBLIC,UNIT_INDEX_BASE,UNIT_PRICE_BASE,AGG_EQUN,COMPILATION,COVERAGE,DECIMALS,SOURCE_AGENCY,SOURCE_DETAIL,TITLE,TITLE_COMPL,UNIT,UNIT_MULT`. With `includeHistory=true` three more columns are appended: `ACTION,VALID_FROM,VALID_TO`.
Example history row (GDP 2025-Q1): first vintage `2025-06-04T13:30:00Z` value 3260736.18, then 10 further `Replace` rows up to `2026-10-28T14:30:00Z` value 3318714.44.
Whole-flow pulls are small: `RTD?format=csvdata&detail=serieskeysonly` 12 KB; `RTD?format=csvdata&lastNObservations=1` 129 KB (2 s). Full single-series history: HICP 1.0 MB, IP 25 MB (the API's revision log for IP is large because every vintage revises many periods).

### A.7 Licence / terms

- ECB Disclaimer & Copyright (linked from the Data Portal footer): `https://www.ecb.europa.eu/services/disclaimer/html/index.en.html`. (WebFetch summary) copyright ECB; users "may make free use of the information obtained directly from it"; ECB must be cited as source; "any changes made by the user, such as seasonal adjustment or calculating growth rates, must be stated explicitly"; authored documents (working papers) need written permission to reprint.
- ESCB statistics reuse policy: `https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html`. (WebFetch summary) free reuse "irrespective of any subsequent commercial or non-commercial use", cite source, do not modify statistics or metadata, third-party data excluded without originator's permission, confidential data excluded.
- RTD-specific: dataset page says it "should be used for research purposes only". The `rtdb_docu.pdf` notes several market series are "Data provided by the financial market provider DataStream" (third-party; excluded from free reuse).
- Research use: **confirmed**. Redistribution of derived results (forecasts, transformed series): **not explicitly stated** on either page; the "modifications must be stated explicitly" clause implies derived use is contemplated, but we found no sentence granting redistribution of derivatives. Raw RTD market series from DataStream should not be redistributed.

### A.8 Caveats

- Euro-area composition: `S0` is a "moving concept" - each vintage carries the composition the ECB used at the time. The bulk files make this explicit via the original keys (2001-01: `ESA.Q.I2...` = "Euro 12"; 2014-12: `MNA.Q.Y.I7...` = "Euro area 18 (fixed composition)"); current `DOM_SER_IDS` use `I10` = "Euro area 21 (fixed composition) as of 1 January 2026" for GDP/unemployment/IP/retail and `U2` (changing composition) for HICP and M3. `rtdb_docu.pdf` gives per-series composition timelines, e.g. "February 2014 to January 2015: Euro 18; April 2011 to January 2014: Euro 17; February 2009 to March 2011: Euro 16; July 2008 to January 2009: Euro 15; June 2007 to June 2008: Euro 13; August 2002 to May 2007: Euro 12; March 2001 to July 2002: Euro area changing composition". Each enlargement is therefore expected to appear as a level revision in the vintage log (not directly observed in this probe; the 2026-02-04 HICP revision coincides with both the EA21 switch and the 2025=100 rebasing).
- "Policy concept" revisions: ESA 2010 from November 2014 (page: "as of November 2014, real-time data refer to the new standard on the European System of Accounts ESA 2010"); chain-linking from November 2005; HICP rebased to 2025=100 in the 2026-02-04 vintage; STS base 2021=100.
- Page: "the quality of early vintages might be in some cases lower due to the lack of good electronic sources available at that time."
- Data are "raw series (mainly indexes, levels and absolute values) instead of derived values (annual percentage changes)"; growth rates must be computed by the user (except `P_C_OV.A`).
- Help page lists no rate limit or size limit; one wildcard key query (`RTD/..P_C_OV.?...`) was rejected with HTTP 400 "Your access has been blocked due to security concerns" (WAF), cause undetermined; key-less whole-flow queries worked. `data.ecb.europa.eu` HTML pages returned 503 to WebFetch but 200 to curl with a browser User-Agent.

---

## B. Latest data

### B.1 Eurostat JSON API (no key needed - all calls below returned HTTP 200 with plain curl)

Base: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?...&format=JSON&lang=EN`. Response is JSON-stat 2.0 (`value` dict indexed by flattened position, `dimension`, `updated` timestamp).

| Target | Dataset / filters that returned data | Notes | Status |
|---|---|---|---|
| Real GDP | `namq_10_gdp?geo=EA21&na_item=B1GQ&unit=CLV_I15&s_adj=SCA` (also `EA20` works for history) | `updated 2026-11-17T23:00`, 2026-Q3 = 117.461 (flash). `geo` codes present: EA21 "(from 2026)", EA20 "(2023-2025)", EA19, EA12 - fixed compositions, no changing-composition code. | confirmed |
| Household consumption | `namq_10_gdp?na_item=P31_S14_S15&unit=CLV_I15&s_adj=SCA&geo=EA21` (also `namq_10_fcs` by durability) | 2026-Q3 not yet published (flash has no components). | confirmed |
| HICP all items | **`prc_hicp_minr`** ("Harmonised index of consumer prices (HICP) - ECOICOP ver.2 - indices and rates of change, monthly data"): `geo=EA&coicop18=TOTAL&unit=I25` (2025=100), `unit=I15`, `unit=RCH_A` (annual rate), `RCH_M`, `RCH_MV12MAVR`. `updated 2026-11-04T11:00`, 2026-10 = 104.77 (I25), 4.0% (RCH_A); history back to 1996-01. | `prc_hicp_midx` / `prc_hicp_manr` are frozen: titles now read "(1996-2025)", last period 2025-12, last update 2026-02-06. The dimension is `coicop18`, not `coicop` (the latter returns HTTP 400 "INVALID_QUERY_DIMENSION"). `geo=EA` = "Euro area (EA11-1999, ..., EA20-2023, EA21-2026)" changing composition. | changed-from-plan |
| HICP excl. energy, food, alcohol, tobacco | `prc_hicp_minr?geo=EA&coicop18=TOT_X_NRG_FOOD&unit=I25&unit=RCH_A` ("Overall index excluding energy, food, alcohol and tobacco"); also `TOT_X_NRG_FOOD_NP` (ex energy & unprocessed food) | Pulled: `updated 2026-11-04T11:00`; index `I25` first non-null 1999-12 (65.29), last 2026-10 (103.64), 323 obs; annual rate `RCH_A` first non-null 2000-12, 2026-10 = 2.5. **Eurostat is the only source found for this target** (latest data only, no vintages). | confirmed |
| Unemployment rate | `une_rt_m?geo=EA21&age=TOTAL&sex=T&unit=PC_ACT&s_adj=SA` | `updated 2026-11-05T23:00`; 2026-06..09 = 6.4, 6.5, 6.5, 6.5; 2026-10 slot present but empty. `geo=EA20` returns no data for 2026. | confirmed |
| Industrial production excl. construction | `sts_inpr_m?geo=EA21&nace_r2=B-D&s_adj=SCA&unit=I21` (EA20 also present) | `updated 2026-11-16T11:00`; 2026-09 = 97.5 (EA21). `indic_bt` has a single code `PRD` "Production (volume)". | confirmed |
| Retail trade volume | `sts_trtu_m?geo=EA21&nace_r2=G47&indic_bt=VOL_SLS&s_adj=SCA&unit=I21` | `indic_bt` codes are `VOL_SLS` / `NETTUR` (not `TOVV`). `updated 2026-11-17T11:00`; 2026-09 = 103.9. | confirmed |

Catalogue: `https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en` (2.0 MB tab-separated; gives last update and last period per dataset). Related survey datasets listed there: `ei_bssi_m_r2`, `ei_bsin_m_r2`, `ei_bsco_m` (EC surveys, updated 29.10.2026).

Eurostat licence: `https://ec.europa.eu/eurostat/web/main/help/copyright-notice` (WebFetch summary): reuse for commercial or non-commercial purposes permitted with source acknowledgement, no written licence needed, under Commission Decision 2011/833/EU; exceptions for third-party material, logos, non-EU-country data, some trade data; modifications must be stated. **confirmed**.

### B.2 ECB Data Portal API for unrevised financial series

- Policy rates: `FM/B.U2.EUR.4F.KR.MRR_FR.LEV` (MRO, "date of changes" series; 2025-06-11 = 2.15), `FM/B.U2.EUR.4F.KR.DFR.LEV` (deposit facility; 2026-09-16 = 2.50). HTTP 200, csvdata. **confirmed**
- Exchange rate: `EXR/D.USD.EUR.SP00.A` (2026-11-13 = 1.1052). HTTP 200. **confirmed**
- API docs: `https://data.ecb.europa.eu/help/api/data` (parameters `startPeriod`, `endPeriod`, `updatedAfter`, `firstNObservations`, `lastNObservations`, `detail` = full|dataonly|serieskeysonly|nodata, `includeHistory`, `format` = csvdata|jsondata|structurespecificdata|genericdata; OR operator `+` and wildcards in keys). No rate limit stated.

### B.3 Release timing (one month observed; not the plan's "typical" days)

Sources: Eurostat euro-indicators news list (`https://ec.europa.eu/eurostat/news/euro-indicators`, WebFetch summary - release titles and dates; the reference periods in the table were inferred by the WebFetch model from the release summaries, not read from raw HTML), the ECB statistical calendar for seasonally adjusted HICP (`https://www.ecb.europa.eu/press/calendars/statscal/ges/html/sthicp.en.html`, WebFetch summary - scheduled dates), and raw corroboration from Eurostat API `updated` fields and the statistics-update RSS.

| Release | Reference period | Date | Kind | Raw corroboration |
|---|---|---|---|---|
| Unemployment | Sep 2026 | 30 Oct 2026 | observed (news list) | none in raw data (`une_rt_m` `updated` 2026-11-05T23:00 is a later update) |
| GDP preliminary flash (t+30) | 2026-Q3 | 30 Oct 2026 | observed (news list) | none (RSS window starts 11 Nov) |
| HICP flash | Oct 2026 | 4 Nov 2026 (15:00 per ECB calendar) | observed (news list) + scheduled | `prc_hicp_minr` `updated` 2026-11-04T11:00 |
| Retail trade volume | Sep 2026 | 6 Nov 2026 | observed (news list) | `sts_trtu_m` RSS updates 13, 14, 17 Nov are later revisions |
| GDP flash + employment (t+45) | 2026-Q3 | 13 Nov 2026 | observed (news list) | RSS `NAMQ_10_GDP` 2026-11-13 11:00 |
| Industrial production | Sep 2026 | 16 Nov 2026 | observed (news list) | RSS `STS_INPR_M` 2026-11-16 11:00 |
| HICP full | Oct 2026 | 18 Nov 2026 (12:00) | **scheduled** (ECB calendar; probe ran before release) | none |

Relative to the 20th: in this month unemployment, retail, HICP flash, GDP flash and IP all landed before the 20th; full HICP is scheduled for the 17th-19th in most months but the ECB calendar shows 24 Feb 2027 and 20 May 2027, i.e. on/after the 20th in some months. The ECB HICP calendar lists flash/full dates through Jan 2028 (flash on the 1st-6th, full on the 17th-24th). One month of observations is not a calendar; treat the "typical day" pattern as **not confirmed** beyond these data points. GDP t+65 release and the regular retail/IP/unemployment calendars: **not confirmed** (the Eurostat release-calendar pages `https://ec.europa.eu/eurostat/web/main/news/release-calendar` and `.../euro-indicators/release-calendar` render their table dynamically and returned no entries to WebFetch; the "iCalendar" link `https://ec.europa.eu/eurostat/subscribe/ics.format` returned an HTML help page, not an `.ics`; `.../catalogue/releasecalendar` and `.../rss/en/euroindicators.rss` are 404). Machine-readable alternative that works: `https://ec.europa.eu/eurostat/api/dissemination/catalogue/rss/en/statistics-update.rss` (dataset-update log, ~1 week deep; e.g. `STS_INPR_M` 2026-11-16 11:00, `NAMQ_10_GDP` 2026-11-13 11:00) plus the `updated` field in every JSON response.

---

## C. ECB Survey of Professional Forecasters (SPF)

| Item | Finding | Status |
|---|---|---|
| Landing pages | `https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/index.en.html` (200); data page `.../html/all_data.en.html` (200); background `.../html/about_the_survey.en.html` (200); release list `.../html/all-releases.en.html` (200). | confirmed |
| Individual-level microdata | `https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_individual_forecasts_by_round.zip` (HTTP 200, 1.64 MB) contains 112 files `1999Q1.csv` .. `2026Q4.csv` (one per round). Also `.../SPF_microdata_by_variable.zip` (not downloaded). **Per-round CSVs are only available inside the zip**: `.../shared/files/2026Q4.csv` and `.../shared/files/SPF_individual_forecasts_by_round/2026Q4.csv` both 404. | confirmed (zip only) |
| Dataset description | `https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_dataset_description.pdf` (HTTP 200, 345 KB). | confirmed |
| Aggregates | `https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/data_aggregates_publication.xlsx` (965 KB; sheets `HICP|HICPX|RGDP|UNEM` x `A_YEAR_0/1/2_AHEAD`, `A_YEAR_LONG_TERM`, `M_/Q_YEAR_1/2_AHEAD`; columns mean, median, N, implied mean of aggregate distribution, disagreement, uncertainty, bins). Also in the ECB Data Portal: dataflow `ECB:SPF` "Survey of Professional Forecasters", 506,458 series, key `SPF.{FREQ}.{REF_AREA=U2}.{FCT_TOPIC: HICP,CORE,RGDP,UNEM,ASSU}.{FCT_BREAKDOWN: POINT or bin}.{FCT_HORIZON: P12M, P24M, ...}.{SURVEY_FREQ=Q}.{FCT_SOURCE}` where `FCT_SOURCE` = `001`..`1xx` individual forecaster IDs plus `AVG, ECB, NUM, PFC, VAR` aggregates. | confirmed |
| Variables | PDF: "forecasts for three main economic indicators" HICP inflation (y/y % change of Eurostat HICP; `HICP`/`HICPX` since core was added), real GDP growth (`RGDP`), unemployment rate (`UNEM`, Eurostat definition), plus assumptions `ASSU`: ECB policy rate `IR` ("since 2024 Q4 for deposit facility rate (DFR), prior to this, main refinancing operations (MRO) rate"), labour costs `LAB`, oil `OIL` (Brent USD), `USD` exchange rate. | confirmed |
| Horizons | PDF: "1) a forecast for the current calendar year 2) a forecast for the next calendar year 3) a forecast for the calendar year after next 4) a longer term forecast (four calendar years ahead in the Q1 and Q2 rounds and five calendar years ahead in the Q3 and Q4 rounds) 5) a rolling horizon forecast for the month (for HICP inflation and the unemployment rate) and quarter (for GDP growth) one year ahead of the latest available observation" 6) the same two years ahead. "This is the forecast horizon structure used since the 2001 Q2 SPF round" (Annex 1 documents earlier structures). Rolling horizons: "set 1- and 2-years ahead of the period (month or quarter) for which the latest official release of a given macroeconomic indicator is available". | confirmed |
| CSV structure (2026Q4.csv, 1,318 lines; 1999Q1.csv, 1,201 lines) | Multi-block text file, not a flat table. Verified from `2026Q4.csv`: line 0 `INFLATION EXPECTATIONS; YEAR-ON-YEAR CHANGE IN HICP`, line 1 header `TARGET_PERIOD,FCT_SOURCE,POINT,TN0_8,FN0_7TN0_3,FN0_2T0_2,F0_3T0_7,F0_8T1_2,F1_3T1_7,F1_8T2_2,F2_3T2_7,F2_8T3_2,F3_3T3_7,F3_8T4_2,F4_3T4_7,F4_8`; line 266 `CORE INFLATION EXPECTATIONS; YEAR-ON-YEAR CHANGE IN CORE` (same bins); line 488 `GROWTH EXPECTATIONS; YEAR-ON-YEAR CHANGE IN REAL GDP` (bins `TN1_0,FN1_0TN0_6,...,F3_5T3_9,F4_0`); line 762 `EXPECTED UNEMPLOYMENT RATE; PERCENTAGE OF LABOUR FORCE` (bins `T4_0,F4_0T4_4,...,F10_5T10_9,F11_0`); line 987 `ASSUMPTIONS`, line 988 header `TARGET_PERIOD,FCT_SOURCE,IR,OIL,USD,LAB`. Bins are round-specific (1999Q1 HICP header: `T0_0,F0_0T0_4,F0_5T0_9,...,F3_0T3_4,F3_5`); the PDF (Annex 5) decodes them: "TN4_0 denotes < -4.0 % and T4_0 denotes <4.0 %", "FN0_5TN0_1 denotes from -0.5 to -0.1 %", "F0_0T0_4 denotes from 0.0 to 0.4 %", "F3_5 denotes >= 3.5 %". PDF: "Each file contains four tables two for inflation (HICP/HICPX) and one for GDP and unemployment. The tables are stored on the same worksheet one below the other, each separated by one blank row." `TARGET_PERIOD` formats seen: `yyyy` (2026, 2027, 2028, 2031 = long term), `yyyyQq` (2027Q1-Q3, 2028Q2), `yyyyMmm` (2027Aug, 2027Sep, 2028Aug, 2028Sep). `FCT_SOURCE` = "forecaster ID ... remains the same for a specific forecaster over all forecast rounds (only the subset of forecasters that were actually responding in a particular round is reported)". Empty cells are missing. | confirmed |
| Date range | 1999Q1 .. 2026Q4 (112 rounds); latest published 30 Oct 2026; next provisionally 5 Feb 2027 (index page, WebFetch summary). | confirmed |
| Survey deadline dates | Given per round in the report footnote. 2026Q4 HTML `.../html/ecb.spf2026q4.en.html`: "The survey was conducted between 2 and 7 October 2026, with 52 responses received." 2016Q1 PDF `.../pdf/ecb.spf2016q1.en.pdf`: "The survey was conducted between 5 and 11 January 2016. The total number of responses was 57". Round pages: `.../html/ecb.spf{YYYY}q{N}.en.html` (2019+; 2015q1 HTML is 404), PDFs `.../pdf/ecb.spf{YYYY}q{N}.en.pdf` (2015-2018 PDF only per all-releases page; all-releases lists quarterly rounds from 2015Q1). No consolidated machine-readable list of survey windows found in the zip, the aggregates xlsx, or the dataset-description PDF (0 hits for "deadline"). Our crude PDF text extractor found the sentence in the 2016Q1 PDF but 0 hits for "conducted" in the 2026Q4 PDF (the HTML page has it), so PDF scraping needs a proper PDF library. Only two rounds were checked. Pre-2015 survey windows: **not confirmed** (older round tables exist at `.../html/table_3_{YYYY}q{N}.en.html` back to 1999Q1 but were not checked for dates). | confirmed for 2 rounds (2016Q1 PDF, 2026Q4 HTML); other rounds not checked; pre-2015 not confirmed |
| Licence | Same ECB Disclaimer & Copyright as A.7; about page states "the full, anonymised microdata are published each quarter" (WebFetch summary). No SPF-specific licence text found. | confirmed (general ECB terms) |

---

## D. URL log

| URL | Result |
|---|---|
| `https://data-api.ecb.europa.eu/service/datastructure/ECB/ECB_RTD1?references=children` | 200, 564 KB SDMX-ML |
| `https://data-api.ecb.europa.eu/service/dataflow/ECB/RTD` | 200 |
| `https://data-api.ecb.europa.eu/service/data/RTD/M.S0.N.P_C_OV.X?format=csvdata&startPeriod=2025-01&endPeriod=2025-03` | 200 (sample) |
| `https://data-api.ecb.europa.eu/service/data/RTD/..P_C_OV.?format=csvdata&detail=serieskeysonly` | **400** WAF block page ("access has been blocked due to security concerns"); cause undetermined |
| `https://data-api.ecb.europa.eu/service/data/RTD?format=csvdata&detail=serieskeysonly` | 200, 278 keys |
| `https://data-api.ecb.europa.eu/service/data/RTD/Q.S0.S.G_GDPM_TO_C.X?...includeHistory=true` | 404 "No Series was returned" (wrong denom; correct key ends `.E`) |
| `https://data-api.ecb.europa.eu/service/data/RTD/Q.S0.S.G_GDPM_TO_C.E?format=csvdata&includeHistory=true&startPeriod=2024-Q1&endPeriod=2025-Q2` | 200, 75 rows, 11 s |
| `.../RTD/M.S0.N.P_C_OV.X?format=csvdata&includeHistory=true` (full) | 200, 1.03 MB, 2,627 rows |
| `.../RTD/M.S0.Y.I_XCONS.X?format=csvdata&includeHistory=true` (full) | 200, 25.1 MB, 47,961 rows (>120 s) |
| `.../RTD/M.S0.Y.O_RTXMOTVD.X?format=csvdata&includeHistory=true` (full) | 200, 16.4 MB, 30,719 rows |
| `.../RTD/M.S0.N.P_C_XEFUN.X?format=csvdata&includeHistory=true` (full) | 200, 1.15 MB, 2,478 rows |
| `.../RTD/{7 target keys}?includeHistory=true&startPeriod=2000-Q1|2000-01&endPeriod=...` | 200 each; earliest `VALID_FROM` 2001-01-03 (ESI 2002-02-06) |
| `https://data-api.ecb.europa.eu/service/data/RTD?format=csvdata&lastNObservations=1` | 200, 129 KB |
| `https://data-api.ecb.europa.eu/service/data/RTD?format=csvdata&updatedAfter=2026-01-01T00%3A00%3A00%2B00%3A00&detail=serieskeysonly` | 200, 190 keys (unreliable as liveness, see A.4) |
| `https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV?format=csvdata&lastNObservations=3` | 200 |
| `https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.DFR.LEV?format=csvdata&lastNObservations=3` | 200 |
| `https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata&lastNObservations=3` | 200 |
| `https://data-api.ecb.europa.eu/service/dataflow/ECB/SPF`; `.../data/SPF?format=csvdata&detail=serieskeysonly` | 200; 200, 32 MB, 506,458 keys |
| `https://data.ecb.europa.eu/data/datasets/RTD` (WebFetch) | **503** |
| `https://data.ecb.europa.eu/data/datasets/RTD/data-information` | WebFetch **503**; curl with browser UA 200 (source of quoted RTD text) |
| `https://data.ecb.europa.eu/help/api/data` | WebFetch 503; curl 200 |
| `https://data.ecb.europa.eu/help/data-examples` | 301 (not followed) |
| `https://data.ecb.europa.eu/legal-notice`, `.../help/terms-of-use` | 404 (guesses) |
| `https://data.ecb.europa.eu/sites/default/files/2023-04/rtdb_docu.pdf` | 200, 474 KB |
| `https://data.ecb.europa.eu/sites/default/files/2024-08/{monthly,quarterly,annual,rtdb38}.zip` | HEAD 200: 26.98 MB / 5.01 MB / 0.38 MB / 4.65 MB; quarterly.zip and rtdb38.zip downloaded |
| `http://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp1145.pdf` (WP 1145, Giannone-Henry-Lalik-Modugno 2010) | linked from page; not fetched |
| `https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html` (vintage dates = GovC decision dates, per page) | linked; not fetched |
| `https://www.ecb.europa.eu/stats/ecb_surveys/rtdb/html/index.en.html` | **404** |
| `https://www.ecb.europa.eu/services/disclaimer/html/index.en.html` | 200 (WebFetch) |
| `https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html` | 200 (WebFetch) |
| `https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/{index,all_data,about_the_survey,all-releases}.en.html` | 200 (WebFetch) |
| `.../html/ecb.spf2026q4.en.html` | 200; `.../html/ecb.spf2015q1.en.html` **404** |
| `.../pdf/ecb.spf2016q1.en.pdf`, `.../pdf/ecb.spf2026q4.en.pdf` | 200 (726 KB, 738 KB) |
| `https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_individual_forecasts_by_round.zip` | 200, 1.64 MB |
| `.../shared/files/SPF_dataset_description.pdf`; `.../shared/files/data_aggregates_publication.xlsx` | 200; 200 |
| `.../shared/files/2026Q4.csv`; `.../shared/files/SPF_individual_forecasts_by_round/2026Q4.csv` | 404; 404 |
| `https://www.ecb.europa.eu/press/calendars/statscal/ges/html/sthicp.en.html`; `.../ges/html/index.en.html` | 200 (WebFetch) |
| `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp?geo=EA20&na_item=B1GQ&unit=CLV_I15&s_adj=SCA&sinceTimePeriod=2024-Q1&format=JSON&lang=EN` | 200 (sample) |
| `.../data/prc_hicp_midx?geo=EA&coicop=CP00&unit=I15...`; `.../prc_hicp_manr?...` | 200 but dataset frozen at 2025-12 |
| `.../data/prc_hicp_minr?geo=EA&coicop=CP00...` | **400** INVALID_QUERY_DIMENSION (dimension is `coicop18`) |
| `.../data/prc_hicp_minr?geo=EA&coicop18=TOTAL&unit=I25&unit=RCH_A&sinceTimePeriod=1996-01...` | 200, 1996-01..2026-10 |
| `.../data/une_rt_m?geo=EA20...` | 200 but empty for 2026; `geo=EA21` 200 with data |
| `.../data/sts_inpr_m?geo=EA20|EA21&nace_r2=B-D&s_adj=SCA&unit=I21` | 200 |
| `.../data/sts_trtu_m?...indic_bt=TOVV` | 200 but empty (wrong code); `indic_bt=VOL_SLS` 200 with data |
| `https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en` | 200, 2.0 MB |
| `https://ec.europa.eu/eurostat/api/dissemination/catalogue/rss/en/statistics-update.rss` | 200, 389 KB, 1,238 items (2026-11-11..17) |
| `https://ec.europa.eu/eurostat/api/dissemination/catalogue/rss/en/euroindicators.rss`; `.../catalogue/releasecalendar?lang=EN` | 404; 404 (guesses) |
| `https://ec.europa.eu/eurostat/web/main/news/release-calendar`; `.../news/euro-indicators/release-calendar` | 200 but table loads dynamically; no dates captured |
| `https://ec.europa.eu/eurostat/subscribe/ics.format`; `.../web/main/subscribe/ics.format` | 200 but `text/html` help page, not `.ics` |
| `https://ec.europa.eu/eurostat/web/euro-indicators`; `https://ec.europa.eu/eurostat/news/euro-indicators` | 200 (WebFetch; source of observed release dates); `.../web/euro-indicators/release-calendar` 404 |
| `https://ec.europa.eu/eurostat/web/main/help/copyright-notice` | 200 (WebFetch); `.../help/faq/copyright` 404 |

## E. Saved samples (scratchpad)

`...\scratchpad\ecb\`: `rtd_datastructure.xml`, `rtd_dataflow.xml`, `rtd_all_keys.csv`, `rtd_hicp_sample.csv` (the A.6 sample), `rtd_gdp_history.csv`, `rtd_hicp_full_history.csv`, `rtd_hicp_2000.csv`, `rtd_last1_all.csv`, `rtd_updated_2026.csv`, `hist_*.csv`, `fullhist_*.csv`, `gdp_2000q1_hist.csv`, `fm_mrr.csv`, `fm_dfr.csv`, `exr_usd.csv`, `rtdb_docu.pdf` (+ `rtdb_docu_text.txt`), `quarterly.zip`, `rtdb38.zip`, `page_data-information.html`, `page_data.html`.
`...\scratchpad\eurostat\`: `namq_gdp_sample.json`, `hicp_minr_tot.json`, `une_ea21.json`, `trtu_vol.json`, `inpr_ea21.json`, `namq_ea21.json`, `toc.txt`, `rss_85b143.xml`, plus the failed probes.
`...\scratchpad\spf\`: `SPF_individual_forecasts_by_round.zip`, extracted `2026Q4.csv`, `1999Q1.csv`, `SPF_dataset_description.pdf` (+ `spf_desc_text.txt`), `data_aggregates_publication.xlsx`, `spf_keys.csv` (32 MB), `ecb.spf2016q1.en.pdf`, `ecb.spf2026q4.en.pdf`.
Total on disk (`du`): ecb 54 MB + eurostat 3.1 MB + spf 37 MB = about 94 MB, dominated by the 32 MB SPF key list, the 25 MB IP history and the 16 MB retail history; everything else is small.
