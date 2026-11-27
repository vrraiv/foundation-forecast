// The seven pages. Each is pre-rendered to its own path; links between them are ordinary links.
export type PageId = "overview" | "results" | "tables" | "models" | "data" | "appendix" | "live";
export interface Page {
  id: PageId;
  path: string;
  name: string;
  title: string;
  description: string;
  /** Pages that show scores wait for scores.json before they become interactive. */
  scores: boolean;
}
const SITE = "Foundation Forecast";
export const PAGES: Page[] = [
  { id: "overview", path: "/", name: "Overview", title: `${SITE}: time-series foundation models on real-time macro data`, description: "A real-time backtest of pretrained time-series foundation models against standard macro forecasting benchmarks, for Canada and the euro area.", scores: true },
  { id: "results", path: "/results/", name: "Results", title: `Results | ${SITE}`, description: "Accuracy against the AR benchmark, forecasts against first-release outturns through time, calibration, and accuracy before and after each model's weights date.", scores: true },
  { id: "tables", path: "/tables/", name: "Tables", title: `Tables | ${SITE}`, description: "The backtest score tables for every target, horizon, input mode, sample and window, sortable, with sample sizes and tests beside every figure.", scores: true },
  { id: "models", path: "/models/", name: "Models", title: `Models | ${SITE}`, description: "The foundation models and benchmarks in the backtest: who released each model and when, its licence, pinned revision and settings.", scores: false },
  { id: "data", path: "/data/", name: "Data", title: `Data | ${SITE}`, description: "Data sources, real-time vintages, target definitions and the rule for what a forecast may see.", scores: false },
  { id: "appendix", path: "/appendix/", name: "Technical appendix", title: `Technical appendix | ${SITE}`, description: "How forecasts are scored: samples, windows, tests, calibration, deviations, and where each published figure comes from.", scores: false },
  { id: "live", path: "/live/", name: "Live record", title: `Live record | ${SITE}`, description: "Forecasts sealed, time-stamped and published every month before the outcomes are known, and scored only after twelve months.", scores: false },
];
export const GROUPS: { name: string; pages: PageId[] }[] = [
  { name: "Backtest", pages: ["overview", "results", "tables"] },
  { name: "Reference", pages: ["models", "data", "appendix"] },
];
export const pageById = (id: PageId) => PAGES.find((p) => p.id === id)!;
export function pageForPath(pathname: string): Page | undefined {
  const norm = pathname.replace(/index\.html$/, "").replace(/\/?$/, "/");
  return PAGES.find((p) => p.path === norm);
}
