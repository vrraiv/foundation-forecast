// Pre-render every page to its own HTML file in dist/, from the client build's index.html and
// the server build's render(). Run by `npm run build` after the two Vite builds.
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const dist = resolve(here, "../dist");
const { render, PAGES } = await import(pathToFileURL(resolve(here, "../dist-ssr/entry-server.js")).href);
const template = readFileSync(join(dist, "index.html"), "utf8");
const scores = JSON.parse(readFileSync(join(dist, "data/scores.json"), "utf8"));
const esc = (s) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");

function page(id, title, description) {
  for (const mark of ["<!--app-title-->", "<!--app-description-->", "<!--app-html-->"]) {
    if (!template.includes(mark)) throw new Error(`index.html lost its ${mark} marker`);
  }
  return template.replace("<!--app-title-->", esc(title)).replace("<!--app-description-->", esc(description)).replace("<!--app-html-->", render(id, scores));
}

for (const p of PAGES) {
  const file = join(dist, p.path, "index.html");
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, page(p.id, p.title, p.description));
  console.log(`pre-rendered ${p.path}`);
}
writeFileSync(join(dist, "404.html"), page(null, "Page not found | Foundation Forecast", "This page does not exist."));
console.log("pre-rendered 404.html");
rmSync(resolve(here, "../dist-ssr"), { recursive: true, force: true });
