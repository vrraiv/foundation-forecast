// Hand-drawn plots: the ratio track used in the accuracy lists, the forecast-against-outturn
// line chart and the PIT histogram. Positions and labels only; every figure comes from the export.
import { type CSSProperties, useState } from "react";
import { type Cell, inCovid, type Row } from "../lib/data";
import { f2, type Group } from "../lib/labels";
import { useWidth } from "./controls";
import { hideTip, showTip } from "./Shell";

const DOM0 = Math.log(0.4);
const DOM1 = Math.log(2.5);
const pos = (rel: number) => ((Math.max(DOM0, Math.min(DOM1, Math.log(rel))) - DOM0) / (DOM1 - DOM0)) * 100;

export interface Dot {
  rel: number | null;
  stem?: boolean;
  cls?: string;
  tip: string;
}
export function Track({ dots, group }: { dots: Dot[]; group: Group }) {
  const ref = pos(1);
  return (
    <div className={`track ${group === "fm" ? "fmc" : "benchc"}`}>
      <span className="ref" style={{ left: `${ref}%` }} />
      {dots.map((d, i) => {
        if (d.rel == null) return null;
        const p = pos(d.rel);
        const clip = d.rel < 0.4 || d.rel > 2.5;
        return (
          <span key={i}>
            {d.stem && <span className="stem" style={{ left: `${Math.min(p, ref)}%`, width: `${Math.abs(p - ref)}%` }} />}
            <span className={`dot ${d.cls ?? ""}${clip ? " clip" : ""}`} style={{ left: `${p}%` }} data-tip={d.tip} />
          </span>
        );
      })}
    </div>
  );
}
export function Axis() {
  return (
    <div className="axis">
      {[0.5, 0.75, 1, 1.5, 2].map((v) => (
        <span key={v} style={{ left: `${pos(v)}%` }}>
          {v}
        </span>
      ))}
    </div>
  );
}

function ticks(lo: number, hi: number, n: number): number[] {
  const span = hi - lo;
  let step = Math.pow(10, Math.floor(Math.log10(span / n)));
  const e = span / n / step;
  step *= e >= 5 ? 5 : e >= 2 ? 2 : 1;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
  return out;
}

export function OriginsChart({ cell, model, group, exCovid, unit }: { cell: Cell; model: string; group: Group; exCovid: boolean; unit: string }) {
  const [host, width] = useWidth<HTMLDivElement>();
  const [hover, setHover] = useState<number | null>(null);
  const tri = cell.m[model];
  if (!tri) return <p className="text-ink-2">No forecasts for this selection.</p>;
  const [med, lo, hi] = tri;
  const n = cell.origin.length;
  const keep = cell.period.map((p) => !exCovid || !inCovid(p));
  const xs = cell.origin.map((d) => Date.parse(d));
  const W = Math.max(300, width);
  const H = W < 520 ? 250 : 320;
  const [L, R, T, B] = [44, 10, 10, 26];
  const vals: number[] = [];
  for (let i = 0; i < n; i++) if (keep[i]) for (const v of [cell.y[i], med[i], lo[i], hi[i]]) if (v != null) vals.push(v);
  let y0 = Math.min(...vals);
  let y1 = Math.max(...vals);
  const pad = (y1 - y0) * 0.06 || 1;
  y0 -= pad;
  y1 += pad;
  const X = (t: number) => L + ((t - xs[0]) / (xs[n - 1] - xs[0])) * (W - L - R);
  const Y = (v: number) => T + ((y1 - v) / (y1 - y0)) * (H - T - B);
  const path = (arr: (number | null)[]) => {
    let d = "";
    let pen = false;
    for (let i = 0; i < n; i++) {
      const v = arr[i];
      if (!keep[i] || v == null) {
        pen = false;
        continue;
      }
      d += `${pen ? "L" : "M"}${X(xs[i]).toFixed(1)} ${Y(v).toFixed(1)}`;
      pen = true;
    }
    return d;
  };
  const band = () => {
    let d = "";
    let seg: number[] = [];
    const flush = () => {
      if (seg.length > 1)
        d += `M${seg.map((i) => `${X(xs[i]).toFixed(1)} ${Y(hi[i]!).toFixed(1)}`).join("L")}L${seg
          .slice()
          .reverse()
          .map((i) => `${X(xs[i]).toFixed(1)} ${Y(lo[i]!).toFixed(1)}`)
          .join("L")}Z`;
      seg = [];
    };
    for (let i = 0; i < n; i++) {
      if (keep[i] && lo[i] != null && hi[i] != null) seg.push(i);
      else flush();
    }
    flush();
    return d;
  };
  const col = group === "fm" ? "var(--c-fm)" : "var(--c-bench)";
  const dropped = keep.map((k, i) => (k ? -1 : i)).filter((i) => i >= 0);
  const yr0 = new Date(xs[0]).getUTCFullYear();
  const yr1 = new Date(xs[n - 1]).getUTCFullYear();
  const stepY = W < 520 ? 3 : W < 800 ? 2 : 1;
  const years: number[] = [];
  for (let yr = yr0 + 1; yr <= yr1; yr += stepY) years.push(yr);

  const move = (e: React.PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    let best = -1;
    let bd = Infinity;
    for (let i = 0; i < n; i++) {
      if (!keep[i]) continue;
      const dd = Math.abs(X(xs[i]) - px);
      if (dd < bd) {
        bd = dd;
        best = i;
      }
    }
    if (best < 0) return;
    setHover(best);
    const m = med[best];
    const a = lo[best];
    const b = hi[best];
    showTip(
      `Forecast date ${cell.origin[best]}\nTarget period ${cell.period[best]}\nFirst release   ${cell.y[best].toFixed(2)}${unit}\nMedian forecast ${m == null ? "–" : m.toFixed(2) + unit}\n80% interval    ${a == null || b == null ? "–" : `${a.toFixed(2)} to ${b.toFixed(2)}`}`,
      e.clientX,
      e.clientY,
    );
  };
  const leave = () => {
    setHover(null);
    hideTip();
  };
  const hx = hover == null ? 0 : X(xs[hover]);
  return (
    <div className="chart" ref={host}>
      {width > 0 && (
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Forecast median and 80% interval against the first-release outturn, by forecast date" onPointerMove={move} onPointerDown={move} onPointerLeave={leave}>
          {exCovid && dropped.length > 0 && (
            <>
              <rect x={X(xs[dropped[0]])} y={T} width={X(xs[dropped[dropped.length - 1]]) - X(xs[dropped[0]])} height={H - T - B} fill="var(--c-shade)" />
              <text x={(X(xs[dropped[0]]) + X(xs[dropped[dropped.length - 1]])) / 2} y={T + 14} textAnchor="middle">
                excluded
              </text>
            </>
          )}
          {ticks(y0, y1, 5).map((v) => (
            <g key={v}>
              <line x1={L} x2={W - R} y1={Y(v)} y2={Y(v)} stroke="var(--c-line-2)" strokeWidth={1} />
              <text x={L - 6} y={Y(v) + 4} textAnchor="end">
                {v}
              </text>
            </g>
          ))}
          {y0 < 0 && y1 > 0 && <line x1={L} x2={W - R} y1={Y(0)} y2={Y(0)} stroke="var(--c-line)" strokeWidth={1} />}
          {years.map((yr) => {
            const x = X(Date.UTC(yr, 0, 1));
            return (
              <g key={yr}>
                <line x1={x} x2={x} y1={H - B} y2={H - B + 4} stroke="var(--c-ink-2)" strokeWidth={1} />
                <text x={x} y={H - 8} textAnchor="middle">
                  {yr}
                </text>
              </g>
            );
          })}
          <path d={band()} fill={col} fillOpacity={0.2} stroke="none" />
          <path d={path(cell.y)} fill="none" stroke="var(--c-ink)" strokeWidth={1.5} strokeLinejoin="round" />
          <path d={path(med)} fill="none" stroke={col} strokeWidth={2} strokeLinejoin="round" />
          {hover != null && (
            <>
              <line x1={hx} x2={hx} y1={T} y2={H - B} stroke="var(--c-ink-2)" strokeWidth={1} />
              <circle cx={hx} cy={Y(cell.y[hover])} r={3.5} fill="var(--c-ink)" stroke="var(--c-panel)" strokeWidth={2} />
              {med[hover] != null && <circle cx={hx} cy={Y(med[hover]!)} r={3.5} fill={col} stroke="var(--c-panel)" strokeWidth={2} />}
            </>
          )}
        </svg>
      )}
    </div>
  );
}

export function PitChart({ row, group }: { row: Row | undefined; group: Group }) {
  const [host, width] = useWidth<HTMLDivElement>();
  if (!row?.pit) return <p className="text-ink-2">No calibration data for this selection.</p>;
  const pit = row.pit;
  const W = Math.max(260, width);
  const [H, L, R, T, B] = [190, 34, 8, 10, 26];
  const bw = (W - L - R) / 10;
  const ymax = Math.max(0.2, Math.max(...pit) * 1.1);
  const Y = (v: number) => T + ((ymax - v) / ymax) * (H - T - B);
  const col = group === "fm" ? "var(--c-fm)" : "var(--c-bench)";
  return (
    <div className="chart" ref={host} style={{ minHeight: H } as CSSProperties}>
      {width > 0 && (
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Histogram of where outturns fell within the forecast distribution">
          {[0, 0.1, 0.2].map((v) => (
            <g key={v}>
              <line x1={L} x2={W - R} y1={Y(v)} y2={Y(v)} stroke="var(--c-line-2)" strokeWidth={1} />
              <text x={L - 6} y={Y(v) + 4} textAnchor="end">
                {v * 100}%
              </text>
            </g>
          ))}
          {pit.map((v, i) => {
            const x = L + i * bw + 1;
            return (
              <path
                key={i}
                d={`M${x} ${Y(0)}V${Y(v) + 3}q0 -3 3 -3H${x + bw - 5}q3 0 3 3V${Y(0)}Z`}
                fill={col}
                data-tip={`Outturn fell in the ${i * 10} to ${i * 10 + 10}% band of the forecast distribution\n${(v * 100).toFixed(1)}% of the time (10% if calibrated)`}
              />
            );
          })}
          <line x1={L} x2={W - R} y1={Y(0.1)} y2={Y(0.1)} stroke="var(--c-ink)" strokeWidth={1.5} strokeDasharray="4 3" />
          {[0, 5, 10].map((i) => (
            <text key={i} x={L + i * bw} y={H - 8} textAnchor={i === 0 ? "start" : i === 10 ? "end" : "middle"}>
              {i * 10}%
            </text>
          ))}
        </svg>
      )}
    </div>
  );
}

export const ratioTip = (name: string, r: Row, rel: number | null, isAR: boolean, fpv: string) =>
  `${name}\nRMSFE ${r.rmsfe == null ? "–" : r.rmsfe.toFixed(3)}, ratio to AR ${f2(rel)}${isAR ? "" : `\nDiebold-Mariano p ${fpv}`}\nn = ${r.n}`;
