import { type ReactNode, useEffect, useRef, useState } from "react";
import { MODELS, type Group } from "../lib/labels";

export function Seg<T extends string | number>({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: { value: T; label: string; disabled?: boolean }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <div className="seg" role="group" aria-label={label}>
      {options.map((o) => (
        <button key={String(o.value)} type="button" aria-pressed={o.value === value} disabled={o.disabled} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Field({ label, htmlFor, children }: { label: string; htmlFor?: string; children: ReactNode }) {
  return (
    <div className="field">
      {htmlFor ? (
        <label className="label" htmlFor={htmlFor}>
          {label}
        </label>
      ) : (
        <span className="label">{label}</span>
      )}
      {children}
    </div>
  );
}

export function ModelSelect({ id, value, onChange, only }: { id: string; value: string; onChange: (v: string) => void; only?: (key: string) => boolean }) {
  const group = (g: Group, label: string) => (
    <optgroup label={label}>
      {MODELS.filter((m) => m.group === g && (!only || only(m.key))).map((m) => (
        <option key={m.key} value={m.key}>
          {m.name}
        </option>
      ))}
    </optgroup>
  );
  return (
    <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
      {group("fm", "Foundation models")}
      {group("bench", "Benchmarks")}
    </select>
  );
}

/** Width of an element, for charts drawn to the pixel. Zero until measured in the browser. */
export function useWidth<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    setWidth(el.clientWidth);
    const ro = new ResizeObserver(() => setWidth(el.clientWidth));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, width] as const;
}
