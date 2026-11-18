## Known breaks, gaps and caveats (hand-maintained; appended to the generated report)

Sources: Phase 0 probes (`docs/probes/`), the generated sections above, and the pipeline's
`problems.txt`. Policy: breaks are recorded, not patched. Growth rates are computed within
one vintage only, so rebasings and chain-linking changes never enter a model input.

### Canada

- **No scripted access to Statistics Canada** (Cloudflare challenge on every www150 path,
  2026-11-17/18). GDP and household-consumption vintages come from the DBnomics mirror of
  real-time table 36-10-0431 and are labelled `dbnomics`; monthly targets come from OECD
  editions. Live-data pulls for StatCan tables fail and are recorded in `problems.txt`.
- **36-10-0431 history truncation**: the release of 2018-11-30 dropped 1961Q1-1980Q4 (80
  deletes). Chained-dollar base changes appear as whole-vintage ratio shifts at 2018-11-30
  (2007 to 2012 dollars, ratio about 1.067) and 2023-11-30 (2012 to 2017 dollars, about
  1.063); smaller whole-vintage shifts at 2013-05-31, 2015-12-01 and 2019-03-01 are
  comprehensive revisions.
- **OECD editions versus StatCan releases (GDP)**: quarter-on-quarter growth in the OECD
  edition matches the StatCan release exactly from about 2015 onward, but differs at the
  second decimal in 2012-2013 (e.g. 2012Q3 first release: OECD 0.413% versus StatCan 0.432%).
  Cause not established; the two are treated as different sources, never merged.
- **Headline CPI** (`oecd:CA.M.CP.IX._Z`, Valet `V41690973`): unrevised except for
  rebasings (OECD edition ratios at 1999-07, 2004-07, 2009-04, 2013-11, 2018-10; one 0.01
  change in 2007-07). Treated as vintage-free with pseudo-vintages: month m visible at the
  origin of m+1, except reference month January (visible at the origin of m+2) because the
  January CPI was released on 26 Feb 2015 and 27 Feb 2019. Release dates verified: January
  2015-2026; other months only Nov 2025 to Nov 2026. Earlier years are unverified; the OECD
  CPI editions are the fallback/robustness source.
- **Unemployment rate**: annual LFS seasonal-adjustment revision (late January) reaches the
  OECD February edition in most years and the March edition in 2018, 2024 and 2026 (section
  4). Editions 2025-08/09 showed float-representation noise only (no revision).
- **Retail volume**: StatCan real-time tables inactive since 2026-03; OECD editions are the
  only vintage source. 900 deletes reflect the OECD trimming history in some editions.
- **OECD edition 202104 contained March 2021 CPI**, which StatCan released on 2021-04-21.
  This is the latest-in-month evidence for the edition snapshot date and bounds the
  same-month visibility rule (origin on the 25th) to a margin of a few days.

### Euro area

- **RTD vintages are ECB snapshots, 8 a year since 2015**, taken the day before Governing
  Council meetings; the latest vintage at an origin can be 5 to 13 weeks old. Rebuilt
  vintages match all 122 ECB bulk snapshot files for 2001-2014 exactly (section 5).
- **Composition**: `S0` is a moving concept. Enlargements appear as level revisions in the
  vintage where the ECB switched (Euro 12 to 2007, 13 in 2007, 15 in 2008, 16 in 2009, 17 in
  2011, 18 in 2014, 19 in 2015, 20 in 2023, 21 in 2026). OECD euro-area editions splice area
  codes EA18 (to 201501), EA19 (201502-202303) and EA20 (202304 on); `vintage_label` carries
  the code. Note that OECD never introduced EA21: the EA20 code continues in 2026 editions.
- **Methodology breaks in RTD**: ESA 2010 from November 2014; chain-linking from November
  2005 (periods before 1991 deleted at 2005-11); HICP rebased to 2025=100 in the 2026-02-04
  vintage; HICP 1990-1995 observations removed at 2024-04-10 (72 blank Replace rows treated
  as deletes).
- **RTD unemployment gap**: `M.S0.S.L_UNETO.F` has no vintage between 2024-03-06 and
  2025-07-23 (16 months); at origins in that window the resolver hands the target to the OECD
  fallback because the RTD vintage is older than 100 days.
- **Stale RTD keys**: industrial production and retail trade have no vintage after
  2025-10-29. OECD editions are the vintage source for retail; RTD is kept as a cross-check.
- **No vintage source for HICP excluding energy, food, alcohol and tobacco.** Pseudo-vintages
  from Eurostat `prc_hicp_minr` (month m visible at the origin of m+1; January at m+2). Timing
  verified only against the ECB HICP calendar for Nov 2026 to Jan 2028.
- **OECD euro-area CPI editions stopped changing after 202606**: editions 202607-202611 exist
  but repeat the 202606 content (no new months). RTD is the HICP vintage source; the OECD
  series is a cross-check to mid-2026 only.
- **Eurostat latest data**: `prc_hicp_midx`/`manr` frozen at 2025-12; `prc_hicp_minr`
  (ECOICOP v2, `coicop18`) is used. Unemployment needs `geo=EA21` from 2026.

### Both

- OECD index levels are not comparable across editions (`BASE_PER` attribute is stale).
- The "first release" of a period in a snapshot source is the value in the earliest vintage
  containing it, which may already be a revised value when the snapshot cadence is coarser
  than the statistical office's release cycle (RTD: 8 a year; OECD: monthly).
- The real-data tests in `tests/test_real_data.py` ran on the 2026-11-18 download and passed
  (cross-source growth agreement; six revision spot checks, of which two were confirmed against
  the published releases: euro-area unemployment January 2024 first release 6.4%, Canadian
  unemployment February 2024 first release 5.8%; the other four are regression pins read from
  the downloaded vintages).
- Unemployment rates in RTD carry 5-6 decimals until 2025 and 1 decimal from 2026; revisions
  measured on this series must round to one decimal first.
- Euro-area unemployment for early 2024 first appears in RTD only in July 2025 (the 16-month
  gap); Phase 4 must define when a first release is too late to count as a first release.
