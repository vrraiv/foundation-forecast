// Facts on this page come from the configuration (via meta.json) and from docs/model_cards.md
// in the repository. Nothing here is from memory; where the sources say nothing, the page says so.
import { meta } from "../lib/data";
import { cap, FM_NAME, word } from "../lib/labels";
import { REPO_URL } from "../lib/ledger";

interface Card {
  developer: string;
  repoCreated: string; // "Release date (HF repo created)" in docs/model_cards.md
  weightsNote?: string;
  paper?: { id: string; label: string };
  training: string;
  licenceNote?: string;
  output: string;
}
// Source: docs/model_cards.md (table; "Training data and cutoffs"; "Inference settings").
const CARDS: Record<string, Card> = {
  chronos2: {
    developer: "Amazon",
    repoCreated: "2025-10-30",
    paper: { id: "2510.15821", label: "arXiv 2510.15821" },
    training:
      "23 real univariate datasets from the Chronos and GIFT-Eval pretraining corpora (energy, transport, weather, cloud, M4, Wikipedia). Its multivariate ability was trained on synthetic data only. FRED-MD is not listed.",
    output: "Returns the nine quantiles directly.",
  },
  timesfm25: {
    developer: "Google",
    repoCreated: "2025-09-02",
    weightsNote: "refreshed weights",
    training: "GiftEvalPretrain, Wikimedia pageviews (cutoff November 2023) and Google Trends (cutoff end-2022), per the model card.",
    output: "Fixed decile heads.",
  },
  tirex: {
    developer: "NX-AI",
    repoCreated: "2025-05-26",
    paper: { id: "2505.23719", label: "arXiv 2505.23719" },
    training: "Chronos training sets including M4, a GiftEvalPretrain subset and synthetic Gaussian-process data. No FRED-MD, M3 or CIF.",
    licenceNote: "NXAI Community License: research use free, attribution required, commercial licence above EUR 100m revenue.",
    output: "Fixed decile heads.",
  },
  tirex2: {
    developer: "NX-AI",
    repoCreated: "2026-06-16",
    weightsNote: "checkpoint dated 2026-07-02, safetensors file 2026-10-06; the later date is used as the boundary",
    paper: { id: "2607.01204", label: "arXiv 2607.01204" },
    training:
      "The model card is tagged with the Salesforce LOTSA collection, which contains FRED-MD, M3, M4 and CIF. This is not confirmed in the model's documentation.",
    output: "Fixed decile heads.",
  },
  moirai2: {
    developer: "Salesforce",
    repoCreated: "2025-08-06",
    paper: { id: "2511.11698", label: "arXiv 2511.11698" },
    training: "GIFT-Eval pretrain and train splits, Chronos-Mixup (non-leaking subset), KernelSynth, and internal Salesforce data covering about January 2024 to January 2025.",
    licenceNote: "Non-commercial licence.",
    output: "A quantile-output model: returns the nine quantiles directly, with no sampling.",
  },
};

// Source: docs/model_cards.md, "Benchmarks".
const BENCH: { key: string; name: string; text: string }[] = [
  { key: "ar", name: "AR (the reference)", text: "Direct multi-step autoregression. The lag length is chosen by BIC on the one-step regression, up to 12 lags for monthly and 4 for quarterly series. Quantiles are Gaussian, from the residual standard error at each horizon. Every ratio on this site is relative to this model." },
  { key: "naive", name: "Historical mean", text: "The mean of the transformed series over its history, which is a random walk in levels. Gaussian quantiles from the historical standard deviation." },
  { key: "bvar", name: "BVAR", text: "A Bayesian vector autoregression with a Minnesota prior, plus sum-of-coefficients and dummy-initial-observation priors. The prior's tightness is chosen at each forecast date by marginal likelihood over a fixed grid. Six lags for monthly and two for quarterly targets, up to 12 variables. Indicators already published for the period being forecast are conditioned on. Quantiles from 500 posterior-predictive draws." },
  { key: "dfm", name: "Dynamic factor model", text: "A mixed-frequency dynamic factor model (statsmodels DynamicFactorMQ): two factors of order two, idiosyncratic AR(1) terms, estimated by EM on the ragged-edge panel. It also uses indicators published after the target's last value. Gaussian quantiles from the prediction standard errors." },
];

export function Models() {
  const fms = meta.foundation_models;
  const n = Object.keys(fms).length;
  return (
    <div className="page">
      <div className="prose">
        <h1>Models</h1>
        <p className="lede">
          {cap(word(n))} openly released time-series foundation models, used exactly as published, against {word(BENCH.length)} standard
          benchmarks estimated afresh at every forecast date.
        </p>
        <p>
          A foundation model here is a neural network pretrained on a large collection of time series and then applied to a new series without
          any training on it (zero-shot). Nothing was fitted, tuned or selected on the macro data: each model receives the history available at
          the forecast date and returns a forecast distribution.
        </p>
      </div>

      <section className="grid gap-3">
        <h2>Foundation models</h2>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,460px),1fr))] gap-3">
          {Object.entries(fms).map(([key, m]) => {
            const c = CARDS[key];
            return (
              <article className="panel" key={key}>
                <header>
                  <h3 className="text-[17px]">{FM_NAME[key]}</h3>
                  <span className="text-[13px] text-ink-2">{c.developer}</span>
                </header>
                <dl className="dl">
                  <dt>Repository</dt>
                  <dd>
                    <a href={`https://huggingface.co/${m.hf_id}`}>{m.hf_id}</a> on Hugging Face, created {c.repoCreated}
                  </dd>
                  {c.paper && (
                    <>
                      <dt>Paper</dt>
                      <dd>
                        <a href={`https://arxiv.org/abs/${c.paper.id}`}>{c.paper.label}</a>
                      </dd>
                    </>
                  )}
                  <dt>Weights used</dt>
                  <dd>
                    dated {m.weights_date}
                    {c.weightsNote ? ` (${c.weightsNote})` : ""}; revision <code>{m.revision.slice(0, 12)}</code>
                  </dd>
                  <dt>Licence</dt>
                  <dd>
                    {m.licence}
                    {c.licenceNote ? `. ${c.licenceNote}` : ""}
                  </dd>
                  <dt>Run as</dt>
                  <dd>
                    {m.variants.join(" and ")}. {c.output}
                  </dd>
                  <dt>Stated training data</dt>
                  <dd>{c.training}</dd>
                  <dt>Stated cutoff</dt>
                  <dd>{m.training_cutoff ? `${m.training_cutoff} (from the model card)` : "None stated"}</dd>
                </dl>
              </article>
            );
          })}
        </div>
        <div className="prose text-[14px] text-ink-2">
          <p>
            No model publishes a calendar cutoff for all of its training data. The weights date is therefore the boundary used on the Results
            page: a forecast made after it cannot have been in that model's training data. The foundation-model average is the equal-weight
            mean of the {word(meta.combinations.combo_fm.length)} univariate forecasts, where all exist.
          </p>
        </div>
      </section>

      <section className="panel">
        <header>
          <h2>How the foundation models are run</h2>
        </header>
        <ul className="grid max-w-[78ch] list-disc gap-1.5 pl-[18px] text-[14px]">
          <li>Input: the last 512 observations of the transformed series (growth rate or difference) as it stood at the forecast date.</li>
          <li>Output: quantiles from 0.1 to 0.9. The median is the point forecast and the 0.1 to 0.9 range is the 80% interval.</li>
          <li>On CPU, with a fixed seed, at each model's pinned revision; the weights are verified by hash before every run.</li>
          <li>
            Multivariate variants also receive up to 12 other series for the same economy, chosen by a fixed coverage rule. No value is invented
            at the ragged edge: a series that ends before the target does is dropped for that date.
          </li>
          <li>Settings were frozen on 2026-11-18, before the first full run.</li>
        </ul>
      </section>

      <section className="grid gap-3">
        <h2>Benchmarks</h2>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,460px),1fr))] gap-3">
          {BENCH.map((b) => (
            <article className="panel" key={b.key}>
              <h3 className="text-[16px]">{b.name}</h3>
              <p className="text-[14px]">{b.text}</p>
            </article>
          ))}
        </div>
        <p className="max-w-[78ch] text-[14px] text-ink-2">
          The benchmark average is the equal-weight mean of the {meta.combinations.combo_bench.length === 3 ? "AR, BVAR and factor-model" : "benchmark"} forecasts. All
          benchmarks use every observation in the vintage, with no pandemic dummies or sample splits.
        </p>
      </section>

      <p className="max-w-[78ch] text-[13.5px] text-ink-2">
        Sources for this page: <a href={`${REPO_URL}/blob/main/docs/model_cards.md`}>the model cards</a> and{" "}
        <a href={`${REPO_URL}/blob/main/configs/default.yaml`}>the configuration file</a> in the repository, which also hold the package versions
        and every setting.
      </p>
    </div>
  );
}
