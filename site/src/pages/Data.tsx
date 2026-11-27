// Facts on this page come from configs/default.yaml and docs/data_quality.md in the repository.
import { meta } from "../lib/data";
import { ECON_NAME, longDate, TARGET_NAME } from "../lib/labels";
import { REPO_URL } from "../lib/ledger";

type Kind = "statcan" | "oecd" | "rtd" | "pseudo";
const KIND: Record<Kind, string> = {
  statcan: "Statistics Canada real-time table",
  oecd: "OECD monthly editions",
  rtd: "ECB Real Time Database",
  pseudo: "Publication-lag rule (no archived vintages)",
};
// Source: the `vintages` entry of each target in configs/default.yaml, and the caveats in docs/data_quality.md.
const VINTAGES: Record<string, Record<string, { kind: Kind; note: string }>> = {
  CA: {
    gdp: { kind: "statcan", note: "Real-time table 36-10-0431, read through the DBnomics mirror." },
    consumption: { kind: "statcan", note: "Real-time table 36-10-0431, read through the DBnomics mirror." },
    cpi: { kind: "pseudo", note: "Not revised except by rebasing. A month is taken as public at the next month's forecast date; January one month later still." },
    cpi_core: { kind: "pseudo", note: "CPI excluding food, energy and indirect taxes (table 18-10-0256). Same timing rule as headline CPI." },
    unemp: { kind: "oecd", note: "Annual seasonal-adjustment revisions arrive with the February or March edition." },
    retail: { kind: "oecd", note: "The OECD volume index copies Statistics Canada's constant-price retail sales." },
  },
  EA: {
    gdp: { kind: "rtd", note: "OECD editions are the fallback when the latest snapshot is too old." },
    consumption: { kind: "rtd", note: "Household and non-profit consumption. OECD editions are the fallback." },
    hicp: { kind: "rtd", note: "OECD editions are the fallback." },
    hicp_core: { kind: "pseudo", note: "No vintage source exists. Eurostat's latest values with the timing rule; the small revisions to HICP are ignored." },
    unemp: { kind: "rtd", note: "The database has no vintage between March 2024 and July 2025; OECD editions fill that gap." },
    retail: { kind: "oecd", note: "The ECB series stopped updating in October 2025." },
  },
};
const TRANSFORM = { log_diff: "% change on the previous period (log difference)", diff: "change on the previous period, percentage points" };

export function Data() {
  return (
    <div className="page">
      <div className="prose">
        <h1>Data</h1>
        <p className="lede">
          Every forecast in the backtest was made from the data as it stood on the forecast date, not from today's revised series, and is scored
          against the value first published.
        </p>
      </div>

      <section className="panel">
        <header>
          <h2>What a forecast may see</h2>
        </header>
        <ul className="grid max-w-[78ch] list-disc gap-1.5 pl-[18px] text-[14px]">
          <li>
            A forecast is made once a month, on the 25th or the next business day. The backtest starts at {longDate(meta.scored_origins.first)}{" "}
            and the last scored date is {longDate(meta.scored_origins.last)}.
          </li>
          <li>It sees only observations whose publication date is strictly before the forecast date.</li>
          <li>Growth rates are computed inside one vintage, so rebasings and chain-linking changes between vintages never reach a model.</li>
          <li>
            Horizons count periods after the target's last published value. Horizon 1 is the first period not yet published, which for most
            series is a month or quarter that has already ended.
          </li>
          <li>A target is skipped on a date with fewer than 120 monthly or 40 quarterly observations in its vintage.</li>
        </ul>
      </section>

      <section className="panel">
        <header>
          <h2>Targets and where their vintages come from</h2>
        </header>
        <div className="scroll">
          <table className="dt wrap stack" style={{ "--stack-grid": "minmax(0, 1fr)" } as React.CSSProperties}>
            <thead>
              <tr>
                <th scope="col">Target</th>
                <th scope="col">Series</th>
                <th scope="col">Forecast as</th>
                <th scope="col">Vintage source</th>
                <th scope="col">Note</th>
              </tr>
            </thead>
            <tbody>
              {meta.economies.map((e) => [
                <tr className="grp" key={e}>
                  <td colSpan={5}>{ECON_NAME[e]}</td>
                </tr>,
                ...Object.entries(meta.targets[e]).map(([t, v]) => (
                  <tr key={`${e}-${t}`}>
                    <td className="font-medium">{TARGET_NAME[t]}</td>
                    <td data-l="Series">
                      {v.name}, {v.freq === "M" ? "monthly" : "quarterly"}
                    </td>
                    <td data-l="Forecast as">{TRANSFORM[v.transform]}</td>
                    <td data-l="Vintage source">{KIND[VINTAGES[e][t].kind]}</td>
                    <td data-l="Note">{VINTAGES[e][t].note}</td>
                  </tr>
                )),
              ])}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid gap-3">
        <h2>Vintage sources</h2>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,460px),1fr))] gap-3">
          <article className="panel">
            <h3 className="text-[16px]">Statistics Canada</h3>
            <p className="text-[14px]">
              Quarterly national accounts come from{" "}
              <a href="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043101">real-time table 36-10-0431</a>, which keeps each release
              as published. Scripted downloads from Statistics Canada's site were blocked when the data were built, so the table is read through the
              DBnomics mirror. Consumer prices
              are read from Statistics Canada tables and from the Bank of Canada's Valet service, which mirrors the same series.
            </p>
            <p className="text-[13px] text-ink-2">
              Used under the <a href="https://www.statcan.gc.ca/en/reference/licence">Statistics Canada Open Licence</a>.
            </p>
          </article>
          <article className="panel">
            <h3 className="text-[16px]">OECD monthly editions</h3>
            <p className="text-[14px]">
              The OECD's short-term statistics revisions database keeps one edition of each series per month. The edition for a month is dated
              the first day of the following month and first used at that month's forecast date. This is the cautious choice: the editions carry
              no publication date, only evidence of when their content was cut.
            </p>
            <p className="text-[13px] text-ink-2">
              Used under the <a href="https://www.oecd.org/en/about/terms-conditions.html">OECD terms and conditions</a>.
            </p>
          </article>
          <article className="panel">
            <h3 className="text-[16px]">ECB Real Time Database</h3>
            <p className="text-[14px]">
              Snapshots of euro-area series taken the day before Governing Council meetings, eight a year since 2015. The latest snapshot on a
              forecast date can be 5 to 13 weeks old; when it is more than 100 days old the OECD edition is used instead. Rebuilt vintages match
              all 122 of the ECB's bulk snapshot files for 2001 to 2014.
            </p>
            <p className="text-[13px] text-ink-2">
              See the ECB's{" "}
              <a href="https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html">
                statistics usage policy
              </a>
              . Latest euro-area values come from Eurostat (
              <a href="https://ec.europa.eu/eurostat/web/main/help/copyright-notice">copyright notice</a>).
            </p>
          </article>
          <article className="panel">
            <h3 className="text-[16px]">Series with no archived vintages</h3>
            <p className="text-[14px]">
              Canadian CPI, Canadian core CPI and euro-area core HICP have no vintage archive. Their real-time path is rebuilt from release
              timing: a month's value is taken as public at the following month's forecast date, and January's one month later, a cautious
              allowance for January figures that have been released late in the following month. For these series the comparison of real-time with revised inputs does not apply.
            </p>
          </article>
        </div>
      </section>

      <section className="panel">
        <header>
          <h2>Outturns</h2>
        </header>
        <ul className="grid max-w-[78ch] list-disc gap-1.5 pl-[18px] text-[14px]">
          <li>The first release of a period is its value in the first vintage that contains it, with the growth rate computed inside that vintage.</li>
          <li>
            A first release that appears much later than usual for its series is flagged as late and left out of first-release scoring, so a gap
            in a vintage archive cannot pass off a revised figure as a first release.
          </li>
          <li>
            Where a source takes snapshots less often than the statistical office publishes, the first value it holds may already be revised.
          </li>
          <li>The revised outturn used in the tables is the value in the vintage visible 12 months after the first release.</li>
        </ul>
      </section>

      <section className="panel">
        <header>
          <h2>Known breaks and gaps</h2>
        </header>
        <ul className="grid max-w-[78ch] list-disc gap-1.5 pl-[18px] text-[14px]">
          <li>Breaks are recorded, not patched. No series is spliced or adjusted by hand.</li>
          <li>The euro area is a moving concept: each enlargement appears as a level revision in the vintage where the source switched.</li>
          <li>Canadian national accounts changed their chained-dollar base in November 2018 and November 2023; these are whole-vintage shifts.</li>
          <li>Canadian core CPI is the measure excluding food, energy and indirect taxes, because the usual core measure has no public scripted source.</li>
          <li>Canada's vintage history is short, about a decade, so tests on Canadian targets have low power.</li>
        </ul>
        <p className="text-[13.5px] text-ink-2">
          The full record, series by series, is in <a href={`${REPO_URL}/blob/main/docs/data_quality.md`}>the data quality report</a>; target and
          source definitions are in <a href={`${REPO_URL}/blob/main/configs/default.yaml`}>the configuration file</a>.
        </p>
      </section>

      <p className="max-w-[78ch] text-[13.5px] text-ink-2">
        The outturn values charted on this site are computed by this project from the sources above. Raw data and vintages are not redistributed
        here; the code that downloads and rebuilds them is in the repository.
      </p>
    </div>
  );
}
