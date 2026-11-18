"""Survey windows of the ECB Survey of Professional Forecasters, one per round, read from the
ECB's own round release pages (HTML, or PDF where no HTML page exists). Nothing is assumed: a
round without a parsable "conducted between ... and ..." sentence is listed as skipped.

Output: `data/raw/ecb-spf/<day>/survey_windows.json` (hash-pinned through RawStore) and the
committed summary `docs/spf_rounds.md`.
"""

from __future__ import annotations

import datetime as dt
import io
import json
import re
from pathlib import Path

from ..data.raw import DownloadError, RawStore

BASE = "https://www.ecb.europa.eu"
ALL_RELEASES = (
    f"{BASE}/stats/ecb_surveys/survey_of_professional_forecasters/html/all-releases.en.html"
)
SOURCE = "ecb-spf"

_MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
# Observed phrasings on the ECB round pages:
#   "conducted between 2 and 7 October 2026"      "between 30 June and 4 July 2025"
#   "between 31 of March and 6 April 2016"        "between 7 and 13 of January 2020"
#   "between 4 and 11 January."  (no year)        "conducted over 4-10 April" (dash, no year)
#   "conducted on 1-11 October 2021"
_PAT = re.compile(
    r"(?:conducted|carried out|took place)\s+(?:between|from|over|on)\s+"
    r"(\d{1,2})(?:\s+of)?(?:\s+(" + _MONTHS + r"))?\s*(?:and|to|[–—-])\s*"
    r"(\d{1,2})(?:\s+of)?\s+(" + _MONTHS + r")(?:\s+(\d{4}))?",
    re.I,
)


def round_links(store: RawStore) -> dict[str, dict[str, str]]:
    """{round: {'html': url} | {'pdf': url}} from the all-releases page (HTML preferred)."""
    rf = store.fetch(SOURCE, "all-releases.en.html", ALL_RELEASES)
    html = rf.path.read_text(encoding="utf-8", errors="replace")
    out: dict[str, dict[str, str]] = {}
    for m in re.finditer(
        r'href="(/stats/ecb_surveys/survey_of_professional_forecasters/(html|pdf)/ecb\.spf(\d{4})q([1-4])[^"]*)"',
        html,
    ):
        url, kind, y, q = m.groups()
        out.setdefault(f"{y}Q{q}", {})[kind] = BASE + url
    return out


def _text_of(path: Path, kind: str) -> str:
    if kind == "html":
        t = path.read_text(encoding="utf-8", errors="replace")
        return re.sub(r"<[^>]+>", " ", t)
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(path.read_bytes()))
    return " ".join((p.extract_text() or "") for p in reader.pages[:3])


def parse_window(text: str, round_year: int | None = None) -> tuple[dt.date, dt.date] | None:
    """Survey window from the page text. A sentence without a year takes the round's year
    (every round is conducted inside its own calendar year)."""
    text = re.sub(r"\s+", " ", text.replace("�", "-"))
    m = _PAT.search(text)
    if not m:
        return None
    d1, m1, d2, m2, y = m.groups()
    months = {name: i + 1 for i, name in enumerate(_MONTHS.split("|"))}
    if y is None and round_year is None:
        return None
    year = int(y) if y else int(round_year)
    end = dt.date(year, months[m2.capitalize()], int(d2))
    start_month = months[m1.capitalize()] if m1 else end.month
    start_year = year if start_month <= end.month else year - 1
    start = dt.date(start_year, start_month, int(d1))
    return start, end


def collect(store: RawStore | None = None, first_round: str = "1999Q1") -> dict:
    store = store or RawStore()
    links = round_links(store)
    out = {"source": ALL_RELEASES, "fetched": store.today.isoformat(), "rounds": {}, "skipped": {}}
    # rounds in the microdata zip with no release page linked from all-releases
    zip_path = store.dir_for(SOURCE) / "SPF_individual_forecasts_by_round.zip"
    if zip_path.exists():
        import zipfile

        for n in zipfile.ZipFile(zip_path).namelist():
            rnd = n[:-4]
            if rnd >= first_round and rnd not in links:
                out["skipped"][rnd] = "no release page linked from all-releases"
    for rnd in sorted(links):
        if rnd < first_round:
            continue
        kinds = ["html", "pdf"] if "html" in links[rnd] else ["pdf"]
        found = None
        tried = []
        for kind in kinds:
            url = links[rnd][kind]
            name = f"{rnd}.{kind}"
            try:
                rf = store.fetch(SOURCE, name, url)
            except DownloadError as e:
                tried.append(f"{kind}: {e}")
                continue
            w = parse_window(_text_of(rf.path, kind), int(rnd[:4]))
            if w:
                found = {
                    "start": w[0].isoformat(),
                    "end": w[1].isoformat(),
                    "url": url,
                    "sha256": rf.sha256,
                }
                break
            tried.append(f"{kind}: no survey-window sentence")
        if found:
            out["rounds"][rnd] = found
        else:
            out["skipped"][rnd] = "; ".join(tried) or "no page"
    store.put(
        SOURCE,
        "survey_windows.json",
        json.dumps(out, indent=1).encode("utf-8"),
        None,
        None,
        {"note": "parsed from the ECB round pages listed inside"},
    )
    return out


def write_doc(out: dict, path: Path) -> None:
    lines = [
        "# ECB SPF survey windows",
        "",
        f"Read from the ECB round release pages linked at {ALL_RELEASES} on {out['fetched']} "
        '(sentence of the form "The survey was conducted between D and D Month YYYY"). Rounds without '
        "such a sentence are listed as skipped and are not used for the Q4 survey comparison.",
        "",
        "| round | survey start | survey end | source |",
        "| --- | --- | --- | --- |",
    ]
    for rnd, r in sorted(out["rounds"].items()):
        lines.append(f"| {rnd} | {r['start']} | {r['end']} | {r['url']} |")
    if out["skipped"]:
        lines += ["", "Skipped rounds:", ""]
        for rnd, why in sorted(out["skipped"].items()):
            lines.append(f"- {rnd}: {why}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import sys

    res = collect(first_round=sys.argv[1] if len(sys.argv) > 1 else "1999Q1")
    write_doc(res, Path(__file__).resolve().parents[3] / "docs" / "spf_rounds.md")
    print(len(res["rounds"]), "rounds with windows;", len(res["skipped"]), "skipped")
    for k, v in sorted(res["skipped"].items()):
        print("  skipped", k, v[:100])
