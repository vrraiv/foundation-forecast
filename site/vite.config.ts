import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, type Plugin } from "vite";

const here = dirname(fileURLToPath(import.meta.url));

/** The public ledger, read at build time. The live page and the masthead count come from this
 *  file alone, so a new ledger line shows up on the next build with nothing else to regenerate. */
function ledger(): Plugin {
  const id = "virtual:ledger";
  const file = resolve(here, "../ledger/ledger.jsonl");
  return {
    name: "ffcast-ledger",
    resolveId: (source) => (source === id ? "\0" + id : undefined),
    load(source) {
      if (source !== "\0" + id) return;
      this.addWatchFile(file);
      const lines = readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
      return `export default ${JSON.stringify(lines)};`;
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), ledger()],
  build: { target: "es2022" },
});
