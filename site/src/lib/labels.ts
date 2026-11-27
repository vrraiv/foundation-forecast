// Display names. The order of MODELS is fixed and is the order used everywhere a list of models
// appears by default; it is not a ranking.
import { meta } from "./data";

export type Group = "fm" | "bench";
export const MODELS: { key: string; name: string; group: Group }[] = [
  { key: "combo_fm|univariate", name: "Foundation-model average", group: "fm" },
  { key: "chronos2|univariate", name: "Chronos-2", group: "fm" },
  { key: "chronos2|multivariate", name: "Chronos-2, multivariate", group: "fm" },
  { key: "timesfm25|univariate", name: "TimesFM 2.5", group: "fm" },
  { key: "tirex|univariate", name: "TiRex", group: "fm" },
  { key: "tirex2|univariate", name: "TiRex-2", group: "fm" },
  { key: "tirex2|multivariate", name: "TiRex-2, multivariate", group: "fm" },
  { key: "moirai2|univariate", name: "Moirai 2.0", group: "fm" },
  { key: "ar|univariate", name: "AR (reference)", group: "bench" },
  { key: "naive|univariate", name: "Historical mean", group: "bench" },
  { key: "bvar|multivariate", name: "BVAR", group: "bench" },
  { key: "dfm|multivariate", name: "Dynamic factor model", group: "bench" },
  { key: "combo_bench|multivariate", name: "Benchmark average", group: "bench" },
];
export const MODEL_NAME: Record<string, string> = Object.fromEntries(MODELS.map((m) => [m.key, m.name]));
export const MODEL_GROUP: Record<string, Group> = Object.fromEntries(MODELS.map((m) => [m.key, m.group]));
export const FM_NAME: Record<string, string> = { chronos2: "Chronos-2", timesfm25: "TimesFM 2.5", tirex: "TiRex", tirex2: "TiRex-2", moirai2: "Moirai 2.0" };
export const DEFAULT_MODEL = "combo_fm|univariate";

export const ECON_NAME: Record<string, string> = { CA: "Canada", EA: "Euro area" };
export const TARGET_NAME: Record<string, string> = {
  gdp: "Real GDP",
  consumption: "Household consumption",
  cpi: "CPI inflation",
  cpi_core: "Core CPI (CPI-XFET)",
  hicp: "HICP inflation",
  hicp_core: "Core HICP",
  unemp: "Unemployment rate",
  retail: "Retail sales volume",
};
export const targetsOf = (econ: string) => Object.keys(meta.targets[econ]);
export const periodWord = (freq: "M" | "Q") => (freq === "M" ? "month" : "quarter");
export const unitOf = (econ: string, target: string) =>
  meta.targets[econ][target].transform === "diff" ? "percentage-point change on the previous period" : "% change on the previous period";
export const unitSuffix = (econ: string, target: string) => (meta.targets[econ][target].transform === "diff" ? " pp" : "%");

// Formatting only.
export const f2 = (x: number | null | undefined) => (x == null ? "–" : x.toFixed(2));
export const f3 = (x: number | null | undefined) => (x == null ? "–" : x.toFixed(3));
export const fp = (x: number | null | undefined) => (x == null ? "–" : x < 0.001 ? "<0.001" : x.toFixed(3));
export const pct = (x: number | null | undefined) => (x == null ? "–" : (x * 100).toFixed(0) + "%");
const WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"];
export const word = (n: number) => WORDS[n] ?? String(n);
export const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
/** "2015-01-26" or "2020-01" -> "January 2015". */
export const monthYear = (iso: string) => `${MONTHS[+iso.slice(5, 7) - 1]} ${iso.slice(0, 4)}`;
/** "2026-11-25" -> "25 November 2026". */
export const longDate = (iso: string) => `${+iso.slice(8, 10)} ${monthYear(iso)}`;
