// The exported backtest (site/public/data, written by `ffcast site-export`). The browser looks
// rows up, filters, sorts and formats them. It computes no score.
import metaJson from "../../public/data/meta.json";

export interface Meta {
  source: { summary: string; summary_sha256: string };
  economies: string[];
  targets: Record<string, Record<string, { name: string; freq: "M" | "Q"; transform: "log_diff" | "diff" }>>;
  horizons: Record<"M" | "Q", number[]>;
  first_origin: string;
  scored_origins: { first: string; last: string; n: number };
  extension_first_origin: string;
  covid_window: [string, string];
  interval: { coverage: number; lower: string; upper: string };
  foundation_models: Record<
    string,
    { hf_id: string; revision: string; licence: string; weights_date: string; training_cutoff: string | null; variants: string[] }
  >;
  benchmarks: string[];
  combinations: Record<string, string[]>;
  live_first_scoring_min_origins: number;
}
export const meta = metaJson as unknown as Meta;

export interface Row {
  econ: string;
  target: string;
  h: number;
  model: string;
  variant: string;
  mode: string;
  outturn: string;
  sample: string;
  window: string;
  split: string;
  n: number;
  rmsfe: number | null;
  mae: number | null;
  bias: number | null;
  wql: number | null;
  cov80: number | null;
  rel_rmsfe: number | null;
  rel_mae: number | null;
  dm_p: number | null;
  mcs: boolean | null;
  pit?: number[] | null;
}
export interface ScoreFile {
  cols: string[];
  rows: unknown[][];
}
export interface Scores {
  rows: Row[];
  index: Map<string, Row>;
}

/** A row is identified by all ten dimensions; `mk` is "model|variant". */
export interface Query {
  econ: string;
  target: string;
  h: number;
  mk: string;
  mode: string;
  sample: string;
  outturn?: string;
  window?: string;
  split?: string;
}
const keyOf = (q: Required<Query>) => [q.econ, q.target, q.h, q.mk, q.mode, q.outturn, q.sample, q.window, q.split].join("/");

export function parseScores(...files: ScoreFile[]): Scores {
  const rows: Row[] = [];
  const index = new Map<string, Row>();
  for (const f of files) {
    for (const raw of f.rows) {
      const r = Object.fromEntries(f.cols.map((c, i) => [c, raw[i]])) as unknown as Row;
      rows.push(r);
      index.set(keyOf({ ...r, mk: `${r.model}|${r.variant}` }), r);
    }
  }
  return { rows, index };
}

export function find(s: Scores, q: Query): Row | undefined {
  return s.index.get(keyOf({ outturn: "first_release", window: "primary", split: "all", ...q }));
}

/** The ratio shown for a row: the AR itself is 1 by definition (its own ratio is not stored). */
export const ratio = (r: Row | undefined): number | null => (!r ? null : r.model === "ar" ? 1 : r.rel_rmsfe);

export type Triple = [(number | null)[], (number | null)[], (number | null)[]];
export interface Cell {
  origin: string[];
  period: string[];
  y: number[];
  m: Record<string, Triple>;
}
export type SeriesFile = Record<string, Cell>;

export function inCovid(period: string): boolean {
  const [lo, hi] = meta.covid_window;
  const q = /^(\d{4})-Q(\d)$/.exec(period);
  if (!q) return period >= lo && period <= hi;
  const idx = (y: number, m: number) => y * 4 + Math.floor((m - 1) / 3);
  const v = +q[1] * 4 + (+q[2] - 1);
  return v >= idx(+lo.slice(0, 4), +lo.slice(5, 7)) && v <= idx(+hi.slice(0, 4), +hi.slice(5, 7));
}

export const freqOf = (econ: string, target: string) => meta.targets[econ][target].freq;
export const hasMode = (s: Scores, econ: string, target: string, mode: string) =>
  !!find(s, { econ, target, h: meta.horizons[freqOf(econ, target)][0], mk: "ar|univariate", mode, sample: "full" });
