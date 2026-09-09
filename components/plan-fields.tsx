'use client';
import { useEffect, useId, useState } from 'react';

export const money = (n: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n);
export function NumberField({
  label,
  value,
  onChange,
  prefix = '$',
  min = 0,
  max = 100000000,
  step = 100,
}: {
  label: string;
  value: number;
  onChange: (n: number) => void;
  prefix?: string;
  min?: number;
  max?: number;
  step?: number;
}) {
  const [draft, setDraft] = useState(String(value));
  const id = useId();
  useEffect(() => setDraft(String(value)), [value]);
  const n = Number(draft);
  const invalid = draft !== '' && (!Number.isFinite(n) || n < min || n > max);
  return (
    <label className="number-field">
      <span>{label}</span>
      <div>
        <span>{prefix}</span>
        <input
          aria-label={label}
          aria-invalid={invalid}
          aria-describedby={invalid ? id : undefined}
          type="number"
          min={min}
          max={max}
          step={step}
          value={draft}
          onChange={(e) => {
            setDraft(e.target.value);
            const next = Number(e.target.value);
            if (
              e.target.value !== '' &&
              Number.isFinite(next) &&
              next >= min &&
              next <= max
            )
              onChange(next);
          }}
          onBlur={() => {
            const next =
              draft === '' || !Number.isFinite(n)
                ? value
                : Math.min(max, Math.max(min, n));
            setDraft(String(next));
            onChange(next);
          }}
        />
      </div>
      {invalid && (
        <small id={id} className="input-error">
          Use {min.toLocaleString()} to {max.toLocaleString()}. Results use the
          last valid value.
        </small>
      )}
    </label>
  );
}
