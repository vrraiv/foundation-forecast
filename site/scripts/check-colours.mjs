// Every colour lives in src/styles/tokens.css. This fails if a raw colour appears anywhere else
// in the site's source, so a new colour cannot slip in beside the tokens.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const allowed = join(root, "src", "styles", "tokens.css");
const raw = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch)\(/g;
const named = /(?:color|background|fill|stroke|border(?:-\w+)?)\s*[:=]\s*["']?\s*(?:white|black|red|blue|green|gr[ae]y|orange|yellow|purple|pink)\b/gi;
const files = [join(root, "index.html")];
(function walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (/\.(tsx?|css|html)$/.test(name)) files.push(p);
  }
})(join(root, "src"));

let bad = 0;
for (const f of files) {
  if (f === allowed) continue;
  readFileSync(f, "utf8").split("\n").forEach((line, i) => {
    const hits = [...line.matchAll(raw), ...line.matchAll(named)].map((m) => m[0]).filter((h) => !/^#\d+$/.test(h) || h.length === 4 || h.length === 7);
    for (const h of hits) {
      if (/&#|href=|id="|#root|#tip/.test(line) && h.startsWith("#") && !/^#[0-9a-fA-F]{6}$/.test(h)) continue;
      console.error(`${relative(root, f)}:${i + 1}: raw colour ${h}`);
      bad++;
    }
  });
}
if (bad) {
  console.error(`${bad} raw colour(s) outside src/styles/tokens.css`);
  process.exit(1);
}
console.log(`colours: ${files.length} files checked, all colours come from tokens.css`);
