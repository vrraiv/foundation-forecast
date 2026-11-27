import { Footer, Masthead, Tip } from "./components/Shell";
import type { Scores } from "./lib/data";
import { Appendix } from "./pages/Appendix";
import { Data } from "./pages/Data";
import { Live } from "./pages/Live";
import { Models } from "./pages/Models";
import { NotFound } from "./pages/NotFound";
import { Overview } from "./pages/Overview";
import { Results } from "./pages/Results";
import { Tables } from "./pages/Tables";
import type { PageId } from "./routes";

export function App({ page, scores }: { page: PageId | null; scores: Scores | null }) {
  let body;
  if (page === null) body = <NotFound />;
  else if (page === "models") body = <Models />;
  else if (page === "data") body = <Data />;
  else if (page === "appendix") body = <Appendix />;
  else if (page === "live") body = <Live />;
  else if (!scores) body = <p className="text-ink-2">Loading the backtest tables…</p>;
  else if (page === "overview") body = <Overview scores={scores} />;
  else if (page === "results") body = <Results scores={scores} />;
  else body = <Tables scores={scores} />;
  return (
    <>
      <Masthead current={page} />
      <main className="gutter pt-[26px] pb-10">
        <div className="inner">{body}</div>
      </main>
      <Footer />
      <Tip />
    </>
  );
}
