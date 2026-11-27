import "@fontsource/ibm-plex-sans/latin-400.css";
import "@fontsource/ibm-plex-sans/latin-500.css";
import "@fontsource/ibm-plex-sans/latin-600.css";
import "@fontsource/ibm-plex-sans-condensed/latin-500.css";
import "@fontsource/ibm-plex-sans-condensed/latin-600.css";
import "@fontsource/ibm-plex-mono/latin-400.css";
import "@fontsource/ibm-plex-mono/latin-500.css";
import "./styles/app.css";
import { createRoot, hydrateRoot } from "react-dom/client";
import { App } from "./App";
import { parseScores, type ScoreFile, type Scores } from "./lib/data";
import { pageForPath } from "./routes";

async function start() {
  const root = document.getElementById("root")!;
  const page = pageForPath(window.location.pathname);
  let scores: Scores | null = null;
  if (page?.scores) {
    const r = await fetch("/data/scores.json");
    if (!r.ok) throw new Error(`scores.json: ${r.status}`);
    scores = parseScores((await r.json()) as ScoreFile);
  }
  const app = <App page={page?.id ?? null} scores={scores} />;
  // The pre-rendered page shows the default selection. With a selection in the address, or in
  // development (nothing pre-rendered), render from scratch instead of adopting that markup.
  if (root.hasChildNodes() && !window.location.search) hydrateRoot(root, app);
  else {
    root.textContent = "";
    createRoot(root).render(app);
  }
}
start().catch((e) => {
  console.error(e);
  const main = document.querySelector("main .inner");
  if (main && !main.querySelector("[data-load-error]")) main.insertAdjacentHTML("afterbegin", '<p data-load-error class="tag">The data for this page did not load. Reload to try again.</p>');
});
