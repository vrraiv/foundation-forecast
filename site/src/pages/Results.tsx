import { useEffect, useState } from "react";
import { Field, ModelSelect, Seg } from "../components/controls";
import { Axis, type Dot, OriginsChart, PitChart, ratioTip, Track } from "../components/plots";
import { find, freqOf, hasMode, meta, ratio, type Scores, type SeriesFile } from "../lib/data";
import { DEFAULT_MODEL, ECON_NAME, f2, fp, MODEL_GROUP, MODEL_NAME, MODELS, monthYear, pct, periodWord, TARGET_NAME, targetsOf, unitOf, unitSuffix } from "../lib/labels";

interface Sel {
  econ: string;
  target: string;
  h: number;
  mode: string;
  sample: string;
  model: string;
}
const DEFAULT: Sel = { econ: "CA", target: "cpi", h: 1, mode: "realtime", sample: "full", model: DEFAULT_MODEL };

/** Keep a selection valid as its parts change (a target that the economy lacks, a horizon the
 *  frequency lacks, an input mode or model with no scores). */
function settle(s: Sel, scores: Scores): Sel {
  const out = { ...s };
  if (!meta.economies.includes(out.econ)) out.econ = DEFAULT.econ;
  const ts = targetsOf(out.econ);
  if (!ts.includes(out.target)) out.target = ts.includes("cpi") ? "cpi" : ts.includes("hicp") ? "hicp" : ts[0];
  const hs = meta.horizons[freqOf(out.econ, out.target)];
  if (!hs.includes(out.h)) out.h = hs[0];
  if (!["full", "ex_covid"].includes(out.sample)) out.sample = "full";
  if (!hasMode(scores, out.econ, out.target, out.mode)) out.mode = "realtime";
  if (!find(scores, { ...out, mk: out.model })) out.model = DEFAULT_MODEL;
  return out;
}

function fromUrl(): Partial<Sel> {
  if (typeof window === "undefined") return {};
  const q = new URLSearchParams(window.location.search);
  const out: Partial<Sel> = {};
  for (const k of ["econ", "target", "mode", "sample", "model"] as const) {
    const v = q.get(k);
    if (v) out[k] = v;
  }
  if (q.get("h")) out.h = Number(q.get("h"));
  return out;
}

const cache = new Map<string, SeriesFile>();
function useSeries(econ: string, target: string) {
  const k = `${econ}_${target}`;
  const [state, setState] = useState<{ key: string; file?: SeriesFile; failed?: boolean }>({ key: k, file: cache.get(k) });
  useEffect(() => {
    if (cache.has(k)) {
      setState({ key: k, file: cache.get(k) });
      return;
    }
    let live = true;
    setState({ key: k });
    fetch(`/data/series_${k}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json() as Promise<SeriesFile>;
      })
      .then((file) => {
        cache.set(k, file);
        if (live) setState({ key: k, file });
      })
      .catch(() => live && setState({ key: k, failed: true }));
    return () => {
      live = false;
    };
  }, [k]);
  return state.key === k ? state : { key: k };
}

function Accuracy({ scores, s, onPick }: { scores: Scores; s: Sel; onPick: (model: string) => void }) {
  return (
    <>
      <div className="pl" style={{ "--cols": "52px 64px 44px 76px 78px" } as React.CSSProperties}>
        <div className="head">
          <span className="hl">Model</span>
          <span className="trk">
            <span className="hl">RMSFE relative to AR (log scale)</span>
            <Axis />
          </span>
          <span className="hl r">Ratio</span>
          <span className="st">
            <span className="hl r">DM p</span>
            <span className="hl r">n</span>
            <span className="hl r">80% cover</span>
            <span className="hl">In 90% MCS</span>
          </span>
        </div>
        {(
          [
            ["fm", "Foundation models, zero-shot"],
            ["bench", "Benchmarks"],
          ] as const
        ).map(([g, label]) => (
          <div key={g} style={{ display: "contents" }}>
            <div className="grp">{label}</div>
            {MODELS.filter((m) => m.group === g).map((m) => {
              const r = find(scores, { ...s, mk: m.key });
              if (!r) return null;
              const isAR = m.key === "ar|univariate";
              const rel = ratio(r);
              const sig = r.dm_p != null && r.dm_p < 0.05;
              const dot: Dot = { rel, stem: !isAR, cls: sig || isAR ? "" : "open", tip: ratioTip(m.name, r, rel, isAR, fp(r.dm_p)) };
              return (
                <div
                  key={m.key}
                  className="row"
                  role="button"
                  tabIndex={0}
                  data-model={m.key}
                  aria-selected={m.key === s.model}
                  onClick={() => onPick(m.key)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onPick(m.key);
                    }
                  }}
                >
                  <span className="nm">{m.name}</span>
                  <span className="trk">
                    <Track dots={[dot]} group={g} />
                  </span>
                  <span className="ratio">{f2(rel)}</span>
                  <span className="st">
                    <span data-l="DM p">{isAR ? "–" : fp(r.dm_p)}</span>
                    <span data-l="n">{r.n}</span>
                    <span data-l="80% cover">{pct(r.cov80)}</span>
                    <span className="l" data-l="in 90% MCS:">
                      {r.mcs == null ? "–" : r.mcs ? "Yes" : "No"}
                    </span>
                  </span>
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div className="key">
        <span className="fmc">
          <i className="sw" />
          foundation model
        </span>
        <span className="benchc">
          <i className="sw" />
          benchmark
        </span>
        <span className="fmc">
          <i className="sw open" />
          hollow: DM p at or above 0.05
        </span>
        <span>diamond: beyond the axis</span>
        <span>Select a row to chart that model below.</span>
      </div>
    </>
  );
}

function BeforeAfter({ scores, s }: { scores: Scores; s: Sel }) {
  return (
    <>
      <div className="pl" style={{ "--cols": "52px 40px 52px 40px" } as React.CSSProperties}>
        <div className="head">
          <span className="hl">Model</span>
          <span className="trk">
            <span className="hl">RMSFE relative to AR (log scale)</span>
            <Axis />
          </span>
          <span className="st">
            <span className="hl r">Before</span>
            <span className="hl r">n</span>
            <span className="hl r">After</span>
            <span className="hl r">n</span>
          </span>
        </div>
        {MODELS.map((m) => {
          const a = find(scores, { ...s, mk: m.key, split: "pre" });
          const b = find(scores, { ...s, mk: m.key, split: "post" });
          if (!a && !b) return null;
          const dots: Dot[] = [];
          if (a) dots.push({ rel: a.rel_rmsfe, cls: "pre", tip: `${m.name}, before the weights date\nratio to AR ${f2(a.rel_rmsfe)}, n = ${a.n}` });
          if (b) dots.push({ rel: b.rel_rmsfe, tip: `${m.name}, after the weights date\nratio to AR ${f2(b.rel_rmsfe)}, n = ${b.n}` });
          const fm = meta.foundation_models[m.key.split("|")[0]];
          return (
            <div key={m.key} className="row">
              <span className="nm">
                {m.name}
                {fm && <small>weights {fm.weights_date}</small>}
              </span>
              <span className="trk">
                <Track dots={dots} group="fm" />
              </span>
              <span className="st">
                <span data-l="ratio before">{f2(a?.rel_rmsfe)}</span>
                <span data-l="n">{a ? a.n : "–"}</span>
                <span data-l="ratio after">{f2(b?.rel_rmsfe)}</span>
                <span data-l="n">{b ? b.n : "–"}</span>
              </span>
            </div>
          );
        })}
      </div>
      <div className="key fmc">
        <span>
          <i className="sw pre" />
          forecast dates before the model's weights were published
        </span>
        <span>
          <i className="sw" />
          after
        </span>
      </div>
    </>
  );
}

export function Results({ scores }: { scores: Scores }) {
  const [raw, setRaw] = useState<Sel>(() => ({ ...DEFAULT, ...fromUrl() }));
  const s = settle(raw, scores);
  const set = (patch: Partial<Sel>) => setRaw(settle({ ...s, ...patch }, scores));
  useEffect(() => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(s)) if (v !== DEFAULT[k as keyof Sel]) q.set(k, String(v));
    const qs = q.toString();
    window.history.replaceState(null, "", qs ? `?${qs}` : window.location.pathname);
  }, [s.econ, s.target, s.h, s.mode, s.sample, s.model]); // eslint-disable-line react-hooks/exhaustive-deps

  const freq = freqOf(s.econ, s.target);
  const per = periodWord(freq);
  const ahead = `${s.h} ${per}${s.h > 1 ? "s" : ""} ahead`;
  const noRevised = !hasMode(scores, s.econ, s.target, "revised");
  const row = find(scores, { ...s, mk: s.model });
  const group = MODEL_GROUP[s.model];
  const series = useSeries(s.econ, s.target);
  const cell = series.file?.[`${s.h}|${s.mode}`];
  const so = meta.scored_origins;
  const [c0, c1] = meta.covid_window;
  const cls = group === "fm" ? "fmc" : "benchc";
  return (
    <div className="page">
      <div className="prose">
        <h1>Results</h1>
        <p className="text-ink-2">
          One selection drives every panel. Scores are against first-release outturns over the forecast dates from {monthYear(so.first)} to{" "}
          {monthYear(so.last)}.
        </p>
      </div>
      <div className="filters">
        <Field label="Economy">
          <Seg label="Economy" value={s.econ} onChange={(econ) => set({ econ })} options={meta.economies.map((e) => ({ value: e, label: ECON_NAME[e] }))} />
        </Field>
        <Field label="Target" htmlFor="f-target">
          <select id="f-target" value={s.target} onChange={(e) => set({ target: e.target.value })}>
            {targetsOf(s.econ).map((t) => (
              <option key={t} value={t}>
                {TARGET_NAME[t]} ({meta.targets[s.econ][t].freq === "M" ? "monthly" : "quarterly"})
              </option>
            ))}
          </select>
        </Field>
        <Field label={`Horizon, ${per}s ahead`}>
          <Seg label="Horizon" value={s.h} onChange={(h) => set({ h })} options={meta.horizons[freq].map((h) => ({ value: h, label: String(h) }))} />
        </Field>
        <Field label="Data the models saw">
          <Seg
            label="Data the models saw"
            value={s.mode}
            onChange={(mode) => set({ mode })}
            options={[
              { value: "realtime", label: "Real-time" },
              { value: "revised", label: "Revised", disabled: noRevised },
            ]}
          />
        </Field>
        <Field label="Sample">
          <Seg
            label="Sample"
            value={s.sample}
            onChange={(sample) => set({ sample })}
            options={[
              { value: "full", label: "Full" },
              { value: "ex_covid", label: `Excl. ${c0} to ${c1}` },
            ]}
          />
        </Field>
      </div>
      {noRevised && (
        <p className="text-[13px] text-ink-2">
          This series has no archived vintages; its real-time path is reconstructed from publication lags, so the revised-data comparison does
          not apply.
        </p>
      )}
      <section className="panel">
        <header>
          <h2>Accuracy</h2>
          <p className="text-[13px] text-ink-2">
            {ECON_NAME[s.econ]}, {TARGET_NAME[s.target]}, {ahead}. Left of the line means smaller errors than the AR.
          </p>
        </header>
        <Accuracy scores={scores} s={s} onPick={(model) => set({ model })} />
      </section>
      <section className="panel">
        <header>
          <h2>Across forecast dates</h2>
          <Field label="Model" htmlFor="f-model">
            <ModelSelect id="f-model" value={s.model} onChange={(model) => set({ model })} only={(k) => !!find(scores, { ...s, mk: k })} />
          </Field>
          <p className="text-[13px] text-ink-2">
            Each point is the forecast made at that date for {ahead}, against the value first published for that period. Units:{" "}
            {unitOf(s.econ, s.target)}.
          </p>
        </header>
        <div className="key">
          <span className="inkc">
            <i className="ln" />
            first-release outturn
          </span>
          <span className={cls}>
            <i className="ln" />
            {MODEL_NAME[s.model]}, median
          </span>
          <span className={cls}>
            <i className="band" />
            {pct(meta.interval.coverage)} interval
          </span>
        </div>
        {cell ? (
          <OriginsChart cell={cell} model={s.model} group={group} exCovid={s.sample === "ex_covid"} unit={unitSuffix(s.econ, s.target)} />
        ) : (
          <p className="chart text-ink-2">{series.failed ? "The forecast file for this target did not load." : series.file ? "No forecasts for this selection." : "Loading forecasts…"}</p>
        )}
      </section>
      <div className="two">
        <section className="panel">
          <header>
            <h2>Accuracy before and after the weights date</h2>
            <p className="text-[13px] text-ink-2">
              RMSFE relative to the AR, computed separately over the forecast dates before and after each model's weights were published. Dates
              after cannot have been in its training data. Left of the line means smaller errors than the AR. Only a few later dates exist so
              far; n is shown.
            </p>
          </header>
          <BeforeAfter scores={scores} s={s} />
        </section>
        <section className="panel">
          <header>
            <h2>Calibration</h2>
            <p className="text-[13px] text-ink-2">
              {MODEL_NAME[s.model]}: the {pct(meta.interval.coverage)} interval contained {row?.cov80 != null ? `${pct(row.cov80)} of ${row.n}` : "–"} outturns.
              Bars show where outturns fell within the forecast distribution; a calibrated model has every bar at the dashed line.
            </p>
          </header>
          <PitChart row={row} group={group} />
        </section>
      </div>
    </div>
  );
}
