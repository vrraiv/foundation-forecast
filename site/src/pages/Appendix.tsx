// Facts on this page come from docs/backtest.md, the reading notes in the published results
// document, and the configuration. Counts come from the export; nothing is typed in by hand.
import { meta } from "../lib/data";
import { monthYear, pct, word } from "../lib/labels";
import { needed, REPO_URL } from "../lib/ledger";
import { pageById } from "../routes";

const doc = (path: string) => `${REPO_URL}/blob/main/${path}`;

export function Appendix() {
  const [c0, c1] = meta.covid_window;
  const so = meta.scored_origins;
  return (
    <div className="page">
      <div className="prose">
        <h1>Technical appendix</h1>
        <p className="lede">How the forecasts are scored, how to read the tables, and where every figure on this site comes from.</p>
      </div>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,460px),1fr))] gap-3">
        <section className="panel">
          <header>
            <h2>What is scored</h2>
          </header>
          <ul className="grid list-disc gap-1.5 pl-[18px] text-[14px]">
            <li>
              Each model gives nine quantiles, 0.1 to 0.9, for every horizon. The point forecast is the median. The {pct(meta.interval.coverage)}{" "}
              interval runs from the 0.1 to the 0.9 quantile.
            </li>
            <li>Forecasts and outturns are in the transformed series: the period-on-period percentage change, or the change in percentage points for unemployment rates.</li>
            <li>A cell is one target, horizon, model, input mode, outturn definition, sample and window. Every statistic is computed per cell.</li>
            <li>
              Horizons are {meta.horizons.M.join(", ")} months and {meta.horizons.Q.join(", ")} quarters after the last published value.
            </li>
          </ul>
        </section>

        <section className="panel">
          <header>
            <h2>Statistics</h2>
          </header>
          <dl className="dl text-[14px]">
            <dt>RMSFE, MAE</dt>
            <dd>Root mean squared and mean absolute forecast error of the median.</dd>
            <dt>Ratio to AR</dt>
            <dd>The model's RMSFE divided by the AR's over the same cell. Below 1 means smaller errors than the AR.</dd>
            <dt>DM p</dt>
            <dd>
              Diebold-Mariano test of equal squared-error loss against the AR, two-sided, with the Harvey-Leybourne-Newbold small-sample
              correction and a Bartlett kernel with horizon minus one lags.
            </dd>
            <dt>Mean error</dt>
            <dd>The mean of outturn minus forecast.</dd>
            <dt>WQL</dt>
            <dd>Weighted quantile loss: the mean pinball loss over the nine quantiles, times two.</dd>
            <dt>80% cover</dt>
            <dd>The share of outturns inside the 80% interval. A calibrated model scores 80%.</dd>
            <dt>Calibration histogram</dt>
            <dd>Where each outturn fell within the forecast distribution, in ten bins. A calibrated model has 10% in each.</dd>
            <dt>90% MCS</dt>
            <dd>
              Model confidence set of Hansen, Lunde and Nason at 90%, with the T-max statistic and a moving-block bootstrap, over the models with
              complete common forecast dates in the cell.
            </dd>
          </dl>
        </section>

        <section className="panel">
          <header>
            <h2>Samples, windows and splits</h2>
          </header>
          <dl className="dl text-[14px]">
            <dt>Primary window</dt>
            <dd>
              Forecast dates from {monthYear(so.first)} to {monthYear(so.last)}: {so.n} monthly dates. This is the window on the Overview and
              Results pages.
            </dd>
            <dt>Extension</dt>
            <dd>
              Forecast dates from {monthYear(meta.extension_first_origin)}, where the vintage holds at least ten years of history. Shown on the
              Tables page.
            </dd>
            <dt>Excluding the pandemic</dt>
            <dd>
              Target periods from {c0} to {c1} are left out. The exclusion applies to scoring only; models were estimated on all data.
            </dd>
            <dt>Real-time and revised inputs</dt>
            <dd>
              Real-time: every series as it stood at the forecast date. Revised: the latest vintage of the same series, cut to the periods that
              were visible at the forecast date.
            </dd>
            <dt>Before and after the weights date</dt>
            <dd>Each foundation model is scored separately over forecast dates before and after its weights were published.</dd>
          </dl>
        </section>

        <section className="panel">
          <header>
            <h2>Reading the results</h2>
          </header>
          <ul className="grid list-disc gap-1.5 pl-[18px] text-[14px]">
            <li>
              Full-sample figures at horizon 1 for the activity targets are dominated by 2020. The multivariate benchmarks do far better than the
              AR there because monthly indicators for the period were already published at the forecast date. Outside {c0} to {c1} they are at or
              above the AR.
            </li>
            <li>
              Quarterly targets have three monthly forecast dates per quarter. Their n is about three times the number of quarters, and the
              Diebold-Mariano test overstates significance at short horizons.
            </li>
            <li>The split at the weights date leaves few forecast dates after it. The TiRex-2 figures after its date rest on a single forecast date.</li>
            <li>The model confidence set keeps nearly every model in nearly every cell. That is low power, not evidence that the models are equally good.</li>
            <li>No ranking is given. A cell rests on at most {so.n} forecasts and many differences are within noise.</li>
          </ul>
        </section>

        <section className="panel">
          <header>
            <h2>What this site leaves out</h2>
          </header>
          <ul className="grid list-disc gap-1.5 pl-[18px] text-[14px]">
            <li>
              The comparison with the ECB's Survey of Professional Forecasters and the regressions of forecast errors on forecast revisions.
              They are in sections 6 and 7 of <a href={doc(meta.source.summary)}>the published results document</a>, with the method in{" "}
              <a href={doc("docs/spf_rounds.md")}>docs/spf_rounds.md</a>.
            </li>
            <li>The levels variant, in which foundation models forecast the level of a series. Its tables are in section 5.6 of the same document.</li>
            <li>
              Departures from the plan after the first full run are listed, with reasons, in <a href={doc("docs/backtest.md")}>docs/backtest.md</a>.
            </li>
          </ul>
        </section>

        <section className="panel">
          <header>
            <h2>Where the figures come from</h2>
          </header>
          <ul className="grid list-disc gap-1.5 pl-[18px] text-[14px]">
            <li>
              Every score on this site is read from <a href={`${REPO_URL}/tree/main/site/public/data`}>exported files in the repository</a>. The
              browser filters, sorts and formats them. It computes no statistic.
            </li>
            <li>
              The export refuses to run unless the tables it reads hash to the published summary, SHA-256{" "}
              <code title={meta.source.summary_sha256}>{meta.source.summary_sha256.slice(0, 12)}…</code>.
            </li>
            <li>
              A test checks the export against the published results document: every figure in its headline tables, and the first 400 rows
              of each of its views, which is all the document prints. A second test recomputes the sample size, RMSFE, MAE and mean error of
              every score in the main window from the exported forecasts and outturns.
            </li>
            <li>
              The <a href={pageById("live").path}>live record</a> page is built from the public ledger alone. No live forecast is scored before{" "}
              {word(needed)} forecast dates have outturns.
            </li>
          </ul>
        </section>
      </div>

      <p className="max-w-[78ch] text-[13.5px] text-ink-2">
        The design brief is <a href={doc("PLAN.md")}>PLAN.md</a>; the backtest's rules, deviations and run log are in{" "}
        <a href={doc("docs/backtest.md")}>docs/backtest.md</a>; the code is in <a href={REPO_URL}>the repository</a>.
      </p>
    </div>
  );
}
