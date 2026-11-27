# Public site

A static site that presents the backtest and the live record. Vite, React and Tailwind; every
page is pre-rendered to its own HTML file, and the browser only filters, sorts and draws.

```
npm ci
npm run check      # type-check, and no colour outside src/styles/tokens.css
npm run build      # client build, server build, pre-render to dist/
npm run preview    # serve dist/ locally
npm run dev        # development server (not pre-rendered)
```

Where things come from:

- `public/data/*.json`: the backtest, written by `uv run ffcast site-export` from the private
  store and committed. `tests/test_site_export.py` checks it against the published results
  document. Do not edit these files by hand.
- `../ledger/ledger.jsonl`: read at build time for the live record page and the masthead count.
  A new ledger line appears on the next build.
- `src/styles/tokens.css`: every colour, for both themes.
- `src/pages/Models.tsx`, `Data.tsx`, `Appendix.tsx`, `Live.tsx`: text written from
  `docs/model_cards.md`, `docs/data_quality.md`, `docs/backtest.md`, `configs/default.yaml` and
  the pre-registration. Update the page when the source changes.

`wrangler.jsonc` describes a Cloudflare Worker that serves `dist/` as static files. Nothing is
deployed by this repository's scripts.
