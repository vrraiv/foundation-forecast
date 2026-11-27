// Pre-rendering: scripts/prerender.mjs calls render() once per page at build time.
import { renderToString } from "react-dom/server";
import { App } from "./App";
import { parseScores, type ScoreFile } from "./lib/data";
import { PAGES, type PageId } from "./routes";

export { PAGES };
export function render(page: PageId | null, scoreFile: ScoreFile): string {
  return renderToString(<App page={page} scores={parseScores(scoreFile)} />);
}
