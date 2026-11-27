import { useState } from "react";
import { Field, ModelSelect, Seg } from "../components/controls";
import { find, meta, ratio, type Scores } from "../lib/data";
import { cap, DEFAULT_MODEL, ECON_NAME, f2, fp, monthYear, TARGET_NAME, word } from "../lib/labels";
import { needed } from "../lib/ledger";
import { pageById } from "../routes";

const SCALE_MAX = 1.6; // the colour scale runs from 1/1.6 to 1.6 times the AR's error

function Heat({ scores, freq, model, sample }: { scores: Scores; freq: "M" | "Q"; model: string; sample: string }) {
  const hs = meta.horizons[freq];
  return (
    <div className="scroll">
      <table className="heat">
        <thead>
          <tr>
            <th />
            {hs.map((h) => (
              <th key={h} className="colh">
                h = {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {meta.economies.map((e) => [
            <tr key={e}>
              <th className="grp" colSpan={hs.length + 1}>
                {ECON_NAME[e]}
              </th>
            </tr>,
            ...Object.keys(meta.targets[e])
              .filter((t) => meta.targets[e][t].freq === freq)
              .map((t) => (
                <tr key={`${e}-${t}`}>
                  <th className="rowh" scope="row">
                    {TARGET_NAME[t]}
                  </th>
                  {hs.map((h) => {
                    const r = find(scores, { econ: e, target: t, h, mk: model, mode: "realtime", sample });
                    const rel = ratio(r);
                    if (!r || rel == null)
                      return (
                        <td key={h}>
                          <span className="hc na">–</span>
                        </td>
                      );
                    const t01 = Math.max(-1, Math.min(1, Math.log(rel) / Math.log(SCALE_MAX)));
                    const cls = Math.abs(t01) < 0.04 ? "" : t01 < 0 ? " neg" : " pos";
                    const sig = r.dm_p != null && r.dm_p < 0.05;
                    const href = `${pageById("results").path}?econ=${e}&target=${t}&h=${h}&sample=${sample}&model=${encodeURIComponent(model)}`;
                    return (
                      <td key={h}>
                        <a
                          className={`hc${cls}${sig ? " sig" : ""}`}
                          style={{ "--t": Math.abs(t01).toFixed(3) } as React.CSSProperties}
                          href={href}
                          data-tip={`${ECON_NAME[e]}, ${TARGET_NAME[t]}, h = ${h}\nRMSFE relative to AR: ${f2(rel)}\nDiebold-Mariano p: ${fp(r.dm_p)}\nForecasts scored: ${r.n}\nSelect to open in Results`}
                        >
                          {f2(rel)}
                        </a>
                      </td>
                    );
                  })}
                </tr>
              )),
          ])}
        </tbody>
      </table>
    </div>
  );
}

export function Overview({ scores }: { scores: Scores }) {
  const [model, setModel] = useState(DEFAULT_MODEL);
  const [sample, setSample] = useState("full");
  const nFm = Object.keys(meta.foundation_models).length;
  const nBench = meta.benchmarks.filter((b) => !(b in meta.combinations)).length;
  const nTargets = meta.economies.reduce((a, e) => a + Object.keys(meta.targets[e]).length, 0);
  const so = meta.scored_origins;
  const [c0, c1] = meta.covid_window;
  return (
    <div className="page">
      <div className="prose">
        <p className="label">
          A real-time backtest, {so.first.slice(0, 4)} to {so.last.slice(0, 4)}
        </p>
        <h1>Can off-the-shelf foundation models forecast macro data as well as standard benchmarks?</h1>
        <p className="lede">
          {cap(word(nFm))} pretrained time-series models were run zero-shot on Canadian and euro-area data, seeing at each forecast date only
          what had been published by then. They are scored against an autoregression, a historical mean, a Bayesian VAR and a dynamic factor model on
          first-release outturns.
        </p>
      </div>
      <div className="flex flex-wrap gap-x-[22px] gap-y-1.5 text-sm">
        <span>
          <b className="font-semibold">{nFm}</b> foundation models, <b className="font-semibold">{nBench}</b> benchmarks
        </span>
        <span>
          <b className="font-semibold">{nTargets}</b> targets in <b className="font-semibold">{meta.economies.length}</b> economies
        </span>
        <span>
          <b className="font-semibold">{so.n}</b> monthly forecast dates, {monthYear(so.first)} to {monthYear(so.last)}
        </span>
        <span>Real-time data vintages throughout</span>
      </div>
      <section className="panel">
        <header>
          <h2>Forecast error relative to the AR benchmark</h2>
          <p className="text-[13px] text-ink-2">
            Root mean squared forecast error divided by the AR's, real-time inputs, first-release outturns. Below 1 means smaller errors than
            the AR. Horizons count periods ahead of the latest published value.
          </p>
        </header>
        <div className="filters">
          <Field label="Model" htmlFor="ov-model">
            <ModelSelect id="ov-model" value={model} onChange={setModel} />
          </Field>
          <Field label="Sample">
            <Seg
              label="Sample"
              value={sample}
              onChange={setSample}
              options={[
                { value: "full", label: "Full sample" },
                { value: "ex_covid", label: `Excluding ${c0} to ${c1}` },
              ]}
            />
          </Field>
        </div>
        <div className="two">
          <div>
            <p className="label">Monthly targets, months ahead</p>
            <Heat scores={scores} freq="M" model={model} sample={sample} />
          </div>
          <div>
            <p className="label">Quarterly targets, quarters ahead</p>
            <Heat scores={scores} freq="Q" model={model} sample={sample} />
          </div>
        </div>
        <div className="scale">
          <span>{(1 / SCALE_MAX).toFixed(1)} smaller errors</span>
          <i />
          <span>{SCALE_MAX} larger errors</span>
          <span>·</span>
          <span>
            <b className="font-semibold underline decoration-current underline-offset-[3px]">underlined</b> = Diebold-Mariano p below 0.05 against
            the AR
          </span>
        </div>
        <ul className="grid max-w-[78ch] list-disc gap-1.5 pl-[18px] text-[13.5px] text-ink-2">
          <li>
            Full-sample figures at horizon 1 for the activity targets are dominated by 2020. The sample without {c0} to {c1} is the informative
            one for those cells.
          </li>
          <li>
            Quarterly targets have three monthly forecast dates per quarter, so the Diebold-Mariano test overstates significance at short
            horizons.
          </li>
          <li>
            This is not a ranking. A cell rests on at most {so.n} forecasts and differences between models are often within noise; the Results
            page shows the tests.
          </li>
        </ul>
      </section>
      <div className="cards">
        <a className="card" href={pageById("results").path}>
          <b className="font-semibold">Results</b>
          <span className="text-ink-2">Accuracy, forecasts against outturns through time, calibration, and before and after each model's weights date.</span>
        </a>
        <a className="card" href={pageById("models").path}>
          <b className="font-semibold">Models</b>
          <span className="text-ink-2">What each model is, who released it and when, its licence and pinned revision.</span>
        </a>
        <a className="card" href={pageById("data").path}>
          <b className="font-semibold">Data</b>
          <span className="text-ink-2">Sources, real-time vintages, and the rule for what a forecast may see.</span>
        </a>
        <a className="card" href={pageById("live").path}>
          <b className="font-semibold">Live record</b>
          <span className="text-ink-2">Forecasts sealed and time-stamped every month; scored after {word(needed)}.</span>
        </a>
      </div>
    </div>
  );
}
