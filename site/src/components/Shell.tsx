import { useEffect, useRef, useState } from "react";
import { needed, REPO_URL, sealed } from "../lib/ledger";
import { GROUPS, pageById, type PageId } from "../routes";

/** Twelve ticks, one filled per sealed forecast date: a count already public in the ledger. */
export function Ticks() {
  return (
    <span className="ticks" style={{ "--n": needed } as React.CSSProperties} aria-hidden="true">
      {Array.from({ length: needed }, (_, i) => (
        <i key={i} className={i < sealed ? "on" : undefined} />
      ))}
    </span>
  );
}

function ThemeToggle() {
  // The theme is set on <html> before first paint by the inline script; this only reflects it.
  const [theme, setTheme] = useState<string | null>(null);
  useEffect(() => setTheme(document.documentElement.getAttribute("data-theme")), []);
  const pick = (t: string) => {
    document.documentElement.setAttribute("data-theme", t);
    try {
      localStorage.setItem("ff-theme", t);
    } catch {
      /* storage unavailable: the choice lasts for this page only */
    }
    setTheme(t);
  };
  return (
    <div className="seg small" role="group" aria-label="Colour theme">
      {["light", "dark"].map((t) => (
        <button key={t} type="button" aria-pressed={theme === t} onClick={() => pick(t)}>
          {t === "light" ? "Light" : "Dark"}
        </button>
      ))}
    </div>
  );
}

export function Masthead({ current }: { current: PageId | null }) {
  const live = pageById("live");
  return (
    <header className="mast gutter">
      <div className="inner">
        <div className="brand">
          <a href="/">Foundation Forecast</a>
          <span className="text-[13px] text-ink-2">Time-series foundation models on real-time macro data</span>
        </div>
        <ThemeToggle />
        <nav className="toc" aria-label="Pages">
          {GROUPS.map((g) => (
            <div className="g" key={g.name}>
              <span className="label">{g.name}</span>
              <span className="it">
                {g.pages.map((id) => {
                  const p = pageById(id);
                  return (
                    <a key={id} href={p.path} aria-current={id === current ? "page" : undefined}>
                      {p.name}
                    </a>
                  );
                })}
              </span>
            </div>
          ))}
          <a className="g live" href={live.path} aria-current={current === "live" ? "page" : undefined}>
            <span className="label">{live.name}</span>
            <span className="it">
              <Ticks />
              <span className="t">
                {sealed} of {needed} sealed
              </span>
            </span>
          </a>
        </nav>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="gutter border-t border-line pt-[18px] pb-7 text-[13px] text-ink-2">
      <div className="inner grid gap-1.5">
        <div>
          Data: Statistics Canada (Statistics Canada Open Licence), ECB Real Time Database, Eurostat, OECD. Growth rates and differences are
          computed by this project from those sources; none of them endorses it. Details on the <a href="/data/">Data</a> page.
        </div>
        <div>
          A personal project on public data. Code, tables and the pre-registration: <a href={REPO_URL}>{REPO_URL.replace("https://", "")}</a>
        </div>
      </div>
    </footer>
  );
}

// One tooltip for the whole page. Elements opt in with data-tip; charts call showTip directly.
let tipEl: HTMLDivElement | null = null;
export function showTip(text: string, x: number, y: number) {
  if (!tipEl) return;
  tipEl.textContent = text;
  tipEl.hidden = false;
  const w = tipEl.offsetWidth;
  const h = tipEl.offsetHeight;
  const left = Math.min(window.innerWidth - w - 8, Math.max(8, x + 12));
  const top = y + 16 + h > window.innerHeight ? y - h - 10 : y + 16;
  tipEl.style.left = `${left}px`;
  tipEl.style.top = `${Math.max(8, top)}px`;
}
export function hideTip() {
  if (tipEl) tipEl.hidden = true;
}
export function Tip() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    tipEl = ref.current;
    const target = (e: Event) => (e.target instanceof Element ? e.target.closest<HTMLElement>("[data-tip]") : null);
    const over = (e: PointerEvent) => {
      const el = target(e);
      if (el) showTip(el.dataset.tip ?? "", e.clientX, e.clientY);
    };
    const out = (e: PointerEvent) => {
      if (target(e)) hideTip();
    };
    const focus = (e: FocusEvent) => {
      const el = target(e);
      if (!el) return;
      const r = el.getBoundingClientRect();
      showTip(el.dataset.tip ?? "", r.left, r.bottom - 10);
    };
    document.addEventListener("pointerover", over);
    document.addEventListener("pointerout", out);
    document.addEventListener("focusin", focus);
    document.addEventListener("focusout", hideTip);
    window.addEventListener("scroll", hideTip, { passive: true });
    return () => {
      document.removeEventListener("pointerover", over);
      document.removeEventListener("pointerout", out);
      document.removeEventListener("focusin", focus);
      document.removeEventListener("focusout", hideTip);
      window.removeEventListener("scroll", hideTip);
      tipEl = null;
    };
  }, []);
  return <div id="tip" ref={ref} hidden />;
}
