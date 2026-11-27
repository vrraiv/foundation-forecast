// Everything on this page comes from the public ledger (ledger/ledger.jsonl, bundled at build
// time), the configuration, and the pre-registration and its amendment. It shows which forecast
// dates are sealed. It shows no forecast, no outturn and no score.
import { meta } from "../lib/data";
import { cap, longDate, word } from "../lib/labels";
import { needed, preregistration, releaseUrl, REPO_URL, runs, sealed } from "../lib/ledger";

const short = (h: string) => `${h.slice(0, 12)}…`;

export function Live() {
  const nFm = Object.keys(meta.foundation_models).length;
  return (
    <div className="page">
      <div className="prose">
        <h1>Live record</h1>
        <p className="lede">
          Since {runs.length ? longDate(runs[0].origin!).replace(/^\d+ /, "") : "the first run"} the same models forecast every month. Each set of
          forecasts is sealed, time-stamped and published before the outcomes are known.
        </p>
      </div>

      <section className="panel">
        <header>
          <h2>Progress to the first scoring</h2>
          <p className="text-[13px] text-ink-2">
            {sealed} of {needed} monthly forecast dates sealed. The record is first scored once {word(needed)} dates have outturns.
          </p>
        </header>
        <div className="prog" style={{ "--n": needed } as React.CSSProperties} role="img" aria-label={`${sealed} of ${needed} forecast dates sealed`}>
          {Array.from({ length: needed }, (_, i) => (
            <i key={i} className={i < sealed ? "on" : undefined} />
          ))}
        </div>
        <div className="scroll">
          <table className="dt stack" style={{ "--stack-grid": "minmax(0, 1fr)" } as React.CSSProperties}>
            <thead>
              <tr>
                <th scope="col">Forecast date</th>
                <th scope="col" className="l">
                  Sealed (UTC)
                </th>
                <th scope="col" className="l">
                  Ledger line
                </th>
                <th scope="col" className="l">
                  Published files
                </th>
              </tr>
            </thead>
            <tbody>
              {runs.map((e) => (
                <tr key={e.seq}>
                  <td>{longDate(e.origin!)}</td>
                  <td className="l n" data-l="Sealed (UTC)">
                    {e.recorded_utc.replace("T", " ").replace("+00:00", "")}
                  </td>
                  <td className="l" data-l="Ledger line">
                    <code title={e.entry_hash}>{short(e.entry_hash)}</code>
                  </td>
                  <td className="l" data-l="Published files">
                    <a href={releaseUrl(e.origin!)}>registry-{e.origin}</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-[13px] text-ink-2">
          This table is the public ledger as it stood when the site was built. The full file is{" "}
          <a href={`${REPO_URL}/blob/main/ledger/ledger.jsonl`}>ledger/ledger.jsonl</a>.
        </p>
      </section>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,460px),1fr))] gap-3">
        <section className="panel">
          <header>
            <h2>Why keep a live record</h2>
          </header>
          <div className="prose text-[14px]">
            <p>
              A backtest is run after the outcomes are known. Its design can be adjusted, knowingly or not, until the results look right, and a
              reader cannot tell. A forecast sealed before the outcome exists cannot be adjusted afterwards.
            </p>
            <p>
              There is a second reason specific to these models. A pretrained model may have seen the backtest period in its training data, and
              only a handful of backtest dates fall after each model's weights were published. Every live forecast is made after all{" "}
              {word(nFm)} sets of weights were fixed, so the live record is the clean test of whether the backtest's results hold.
            </p>
          </div>
        </section>

        <section className="panel">
          <header>
            <h2>What happens each month</h2>
          </header>
          <ol className="grid list-decimal gap-1.5 pl-[20px] text-[14px]">
            <li>On the 25th, or the next business day, the data available that day are downloaded and stored.</li>
            <li>Every model forecasts every target from that snapshot, at its pinned revision and settings.</li>
            <li>The forecast file is sealed: a manifest records its salted hash, the code version, the data snapshot and the weights.</li>
            <li>One line is added to the public ledger with the hash of the manifest and the hash of the line before it.</li>
            <li>The line is time-stamped with OpenTimestamps, which anchors it to a date independently of this project.</li>
            <li>The sealed files are published as a release in the repository, byte for byte as sealed.</li>
          </ol>
        </section>

        <section className="panel">
          <header>
            <h2>Why nothing is scored yet</h2>
          </header>
          <div className="prose text-[14px]">
            <p>
              The rules were fixed in advance in a pre-registration whose hash is the first line of the ledger. The record is first scored when
              at least {word(needed)} monthly forecast dates have first-release outturns at horizon 1 for every monthly target. Until then the
              project computes, reports and displays no error, score or ranking from the live forecasts.
            </p>
            <p>
              {cap(word(needed))} dates is still a small sample. The first scoring will report its sampling error, every later scoring will be
              reported whether favourable or not, and no period will be excluded after the fact.
            </p>
            <p>
              The forecasts themselves are public, so anyone can compare them with outturns as they arrive. This site does not, until the
              threshold is reached.
            </p>
          </div>
        </section>

        <section className="panel">
          <header>
            <h2>Check it yourself</h2>
          </header>
          <div className="prose text-[14px]">
            <p>
              Each release holds the manifest, the salt, the forecast and status files, the time-stamp proof and a CSV copy of the forecasts. To
              check a release against the ledger, download its files into a folder and run, from a copy of the repository:
            </p>
            <p>
              <code>python scripts/verify_published.py ledger/ledger.jsonl &lt;folder&gt;</code>
            </p>
            <p>
              The script needs only Python. It checks the ledger's hash chain, the manifest's hash against the ledger line, and the salted
              hashes of the forecast and status files against the manifest.
            </p>
          </div>
          <dl className="dl text-[13.5px]">
            <dt>Pre-registration</dt>
            <dd>
              <a href={`${REPO_URL}/blob/main/PREREGISTRATION.md`}>PREREGISTRATION.md</a>
              {preregistration && (
                <>
                  , SHA-256 <code title={preregistration.payload_sha256}>{short(preregistration.payload_sha256)}</code>, recorded{" "}
                  {longDate(preregistration.recorded_utc.slice(0, 10))}
                </>
              )}
            </dd>
            <dt>Amendment</dt>
            <dd>
              <a href={`${REPO_URL}/blob/main/PREREGISTRATION_AMENDMENTS.md`}>Amendment 1</a>: the sealed forecasts are published each month; the
              rule against early scoring stays.
            </dd>
          </dl>
        </section>
      </div>
    </div>
  );
}
