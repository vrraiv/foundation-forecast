import { useEffect, useMemo, useState } from "react";
import { Field, Seg } from "../components/controls";
import { find, freqOf, hasMode, meta, parseScores, ratio, type Row, type ScoreFile, type Scores } from "../lib/data";
import { ECON_NAME, f3, fp, MODELS, monthYear, pct, periodWord, TARGET_NAME, targetsOf } from "../lib/labels";
import { REPO_URL } from "../lib/ledger";

interface Col {
  id: string;
  label: string;
  tip: string;
  value: (r: Row) => number | null;
  text: (r: Row) => string;
}
const COLS: Col[] = [
  { id: "n", label: "n", tip: "Forecasts scored", value: (r) => r.n, text: (r) => String(r.n) },
  { id: "rmsfe", label: "RMSFE", tip: "Root mean squared forecast error, in the units of the transformed series", value: (r) => r.rmsfe, text: (r) => f3(r.rmsfe) },
  { id: "rel", label: "Ratio to AR", tip: "RMSFE divided by the AR's in the same cell; below 1 means smaller errors", value: (r) => ratio(r), text: (r) => f3(ratio(r)) },
  { id: "dm", label: "DM p", tip: "Diebold-Mariano test against the AR on squared errors, two-sided, with the Harvey-Leybourne-Newbold correction", value: (r) => r.dm_p, text: (r) => (r.model === "ar" ? "–" : fp(r.dm_p)) },
  { id: "mae", label: "MAE", tip: "Mean absolute error", value: (r) => r.mae, text: (r) => f3(r.mae) },
  { id: "relmae", label: "MAE ratio", tip: "MAE divided by the AR's in the same cell", value: (r) => (r.model === "ar" ? 1 : r.rel_mae), text: (r) => f3(r.model === "ar" ? 1 : r.rel_mae) },
  { id: "bias", label: "Mean error", tip: "Mean of outturn minus forecast", value: (r) => r.bias, text: (r) => f3(r.bias) },
  { id: "wql", label: "WQL", tip: "Weighted quantile loss: mean pinball loss over the nine quantiles, times two", value: (r) => r.wql, text: (r) => f3(r.wql) },
  { id: "cov", label: "80% cover", tip: "Share of outturns inside the 80% interval", value: (r) => r.cov80, text: (r) => pct(r.cov80) },
];

interface Sel {
  econ: string;
  target: string;
  mode: string;
  outturn: string;
  sample: string;
  window: string;
  split: string;
}
const SPLITS = [
  { value: "all", label: "All forecast dates" },
  { value: "pre", label: "Before the weights date" },
  { value: "post", label: "After the weights date" },
  { value: "pre_cutoff", label: "Before the stated training cutoff" },
  { value: "post_cutoff", label: "After the stated training cutoff" },
];

function HorizonTable({ scores, s, h }: { scores: Scores; s: Sel; h: number }) {
  const [sort, setSort] = useState<{ id: string; dir: 1 | -1 } | null>(null);
  const rows = useMemo(() => {
    const found = MODELS.map((m) => ({ m, r: find(scores, { ...s, h, mk: m.key }) })).filter((x): x is { m: (typeof MODELS)[number]; r: Row } => !!x.r);
    if (!sort) return found;
    const col = COLS.find((c) => c.id === sort.id)!;
    return [...found].sort((a, b) => {
      const va = col.value(a.r);
      const vb = col.value(b.r);
      if (va == null || vb == null) return va == null ? (vb == null ? 0 : 1) : -1; // missing values last
      return (va - vb) * sort.dir;
    });
  }, [scores, s, h, sort]);
  if (!rows.length) return <p className="text-[13.5px] text-ink-2">No scores for this selection at this horizon.</p>;
  const click = (id: string) => setSort((cur) => (cur?.id !== id ? { id, dir: 1 } : cur.dir === 1 ? { id, dir: -1 } : null));
  return (
    <>
      <div className="scroll">
        <label className="only-stacked early items-center gap-2 pb-1 text-[13px] text-ink-2">
          Order
          <select
            value={sort ? `${sort.id}:${sort.dir}` : ""}
            onChange={(e) => {
              const [id, dir] = e.target.value.split(":");
              setSort(id ? { id, dir: dir === "-1" ? -1 : 1 } : null);
            }}
          >
            <option value="">Fixed order</option>
            {COLS.map((c) => [
              <option key={`${c.id}:1`} value={`${c.id}:1`}>
                {c.label}, smallest first
              </option>,
              <option key={`${c.id}:-1`} value={`${c.id}:-1`}>
                {c.label}, largest first
              </option>,
            ])}
          </select>
        </label>
        <table className="dt stack early">
          <thead>
            <tr>
              <th scope="col">Model</th>
              {COLS.map((c) => (
                <th key={c.id} scope="col" aria-sort={sort?.id === c.id ? (sort.dir === 1 ? "ascending" : "descending") : "none"}>
                  <button type="button" data-tip={c.tip} data-sorted={sort?.id === c.id || undefined} onClick={() => click(c.id)}>
                    {c.label}
                    {sort?.id === c.id ? (sort.dir === 1 ? " ↑" : " ↓") : ""}
                  </button>
                </th>
              ))}
              <th scope="col" className="l" data-tip="Member of the 90% model confidence set for this cell">
                In 90% MCS
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ m, r }, i) => [
              !sort && (i === 0 || rows[i - 1].m.group !== m.group) && (
                <tr className="grp" key={`g-${m.group}`}>
                  <td colSpan={COLS.length + 2}>{m.group === "fm" ? "Foundation models, zero-shot" : "Benchmarks"}</td>
                </tr>
              ),
              <tr key={m.key}>
                <td>{m.name}</td>
                {COLS.map((c) => (
                  <td key={c.id} className="n" data-l={c.label}>
                    {c.text(r)}
                  </td>
                ))}
                <td className="l" data-l="In 90% MCS">
                  {r.mcs == null ? "–" : r.mcs ? "Yes" : "No"}
                </td>
              </tr>,
            ])}
          </tbody>
        </table>
      </div>
      {sort && (
        <p className="text-[12.5px] text-ink-2">
          Sorted by {COLS.find((c) => c.id === sort.id)!.label}. An order within one cell is not a ranking of models: read it with n and the
          test beside it.{" "}
          <button type="button" className="cursor-pointer underline decoration-hl underline-offset-[3px]" onClick={() => setSort(null)}>
            Restore the fixed order
          </button>
        </p>
      )}
    </>
  );
}

export function Tables({ scores: main }: { scores: Scores }) {
  const [more, setMore] = useState<ScoreFile | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    fetch("/data/scores_more.json")
      .then((r) => (r.ok ? (r.json() as Promise<ScoreFile>) : Promise.reject(new Error(String(r.status)))))
      .then(setMore)
      .catch(() => setFailed(true));
  }, []);
  const scores = useMemo(() => {
    if (!more) return main;
    const extra = parseScores(more);
    return { rows: [...main.rows, ...extra.rows], index: new Map([...main.index, ...extra.index]) };
  }, [main, more]);

  const [s, setS] = useState<Sel>({ econ: "CA", target: "cpi", mode: "realtime", outturn: "first_release", sample: "full", window: "primary", split: "all" });
  const set = (patch: Partial<Sel>) =>
    setS((cur) => {
      const next = { ...cur, ...patch };
      const ts = targetsOf(next.econ);
      if (!ts.includes(next.target)) next.target = ts.includes("cpi") ? "cpi" : ts.includes("hicp") ? "hicp" : ts[0];
      if (!hasMode(main, next.econ, next.target, next.mode)) next.mode = "realtime";
      return next;
    });
  const freq = freqOf(s.econ, s.target);
  const noRevised = !hasMode(main, s.econ, s.target, "revised");
  const [c0, c1] = meta.covid_window;
  const waiting = !more;
  return (
    <div className="page">
      <div className="prose">
        <h1>Tables</h1>
        <p className="text-ink-2">
          The score tables behind the charts, one table per horizon. Rows keep a fixed order, and any column can be sorted. Every figure sits
          beside its sample size and its test against the AR. The site computes no figure of its own: these are the published tables.
        </p>
      </div>
      <div className="filters">
        <Field label="Economy">
          <Seg label="Economy" value={s.econ} onChange={(econ) => set({ econ })} options={meta.economies.map((e) => ({ value: e, label: ECON_NAME[e] }))} />
        </Field>
        <Field label="Target" htmlFor="t-target">
          <select id="t-target" value={s.target} onChange={(e) => set({ target: e.target.value })}>
            {targetsOf(s.econ).map((t) => (
              <option key={t} value={t}>
                {TARGET_NAME[t]} ({meta.targets[s.econ][t].freq === "M" ? "monthly" : "quarterly"})
              </option>
            ))}
          </select>
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
        <Field label="Outturn">
          <Seg
            label="Outturn"
            value={s.outturn}
            onChange={(outturn) => set({ outturn })}
            options={[
              { value: "first_release", label: "First release" },
              { value: "revised_12m", label: "Revised, 12 months on", disabled: waiting },
            ]}
          />
        </Field>
        <Field label="Forecast dates from">
          <Seg
            label="Forecast dates from"
            value={s.window}
            onChange={(window) => set({ window })}
            options={[
              { value: "primary", label: monthYear(meta.first_origin) },
              { value: "all", label: `${monthYear(meta.extension_first_origin)} (extension)`, disabled: waiting },
            ]}
          />
        </Field>
        <Field label="Rows" htmlFor="t-split">
          <select id="t-split" value={s.split} onChange={(e) => set({ split: e.target.value })}>
            {SPLITS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Field>
      </div>
      {failed && <p className="text-[13px] text-ink-2">The tables for the other outturn and window did not load; the main tables below are complete.</p>}
      {s.split !== "all" && (
        <p className="text-[13px] text-ink-2">
          Splits exist for the foundation models only: each is scored over the forecast dates before or after its own weights date (or stated
          training cutoff, where its model card gives one). The ratio is to the AR over the same dates.
        </p>
      )}
      {meta.horizons[freq].map((h, i) => (
        <details className="fold" key={`${s.econ}-${s.target}-${h}`} open={i === 0 || undefined}>
          <summary>
            <h2>
              {h} {periodWord(freq)}
              {h > 1 ? "s" : ""} ahead
            </h2>
            <span className="text-[13px] text-ink-2">
              {ECON_NAME[s.econ]}, {TARGET_NAME[s.target]}
            </span>
          </summary>
          <div className="body">
            <HorizonTable scores={scores} s={s} h={h} />
          </div>
        </details>
      ))}
      <p className="max-w-[78ch] text-[13.5px] text-ink-2">
        The same figures as files: <a href={`${REPO_URL}/tree/main/site/public/data`}>the exported tables</a> and{" "}
        <a href={`${REPO_URL}/blob/main/${meta.source.summary}`}>the published results document</a> they are checked against.
      </p>
    </div>
  );
}
