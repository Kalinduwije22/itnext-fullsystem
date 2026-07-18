"use client";

import { useEffect, useState } from "react";

const COUNTRIES: { name: string; dial: string }[] = [
  { name: "Sri Lanka", dial: "+94" },
  { name: "India", dial: "+91" },
  { name: "United Kingdom", dial: "+44" },
  { name: "United States", dial: "+1" },
  { name: "Canada", dial: "+1" },
  { name: "Australia", dial: "+61" },
  { name: "United Arab Emirates", dial: "+971" },
  { name: "Saudi Arabia", dial: "+966" },
  { name: "Qatar", dial: "+974" },
  { name: "Kuwait", dial: "+965" },
  { name: "Bahrain", dial: "+973" },
  { name: "Oman", dial: "+968" },
  { name: "Singapore", dial: "+65" },
  { name: "Malaysia", dial: "+60" },
  { name: "Germany", dial: "+49" },
  { name: "France", dial: "+33" },
  { name: "Italy", dial: "+39" },
  { name: "Spain", dial: "+34" },
  { name: "Netherlands", dial: "+31" },
  { name: "Ireland", dial: "+353" },
  { name: "Switzerland", dial: "+41" },
  { name: "New Zealand", dial: "+64" },
  { name: "Japan", dial: "+81" },
  { name: "South Korea", dial: "+82" },
  { name: "China", dial: "+86" },
  { name: "Hong Kong", dial: "+852" },
  { name: "Pakistan", dial: "+92" },
  { name: "Bangladesh", dial: "+880" },
  { name: "Nepal", dial: "+977" },
  { name: "Maldives", dial: "+960" },
  { name: "South Africa", dial: "+27" },
  { name: "Nigeria", dial: "+234" },
  { name: "Kenya", dial: "+254" },
  { name: "Philippines", dial: "+63" },
  { name: "Indonesia", dial: "+62" },
  { name: "Thailand", dial: "+66" },
  { name: "Brazil", dial: "+55" },
];

const DEFAULT_DIAL = "+94";

export function PhoneInput({
  value,
  onChange,
  onBlur,
  error,
}: {
  value: string;
  onChange: (e164: string) => void;
  onBlur?: () => void;
  error?: string;
}) {
  const [dial, setDial] = useState(DEFAULT_DIAL);
  const [digits, setDigits] = useState("");

  useEffect(() => {
    if (!value) return;
    const match = COUNTRIES.find((c) => value.startsWith(c.dial));
    if (match) {
      setDial(match.dial);
      setDigits(value.slice(match.dial.length));
    }
    // Only split the incoming value once, on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function update(newDial: string, newDigits: string) {
    setDial(newDial);
    setDigits(newDigits);
    onChange(`${newDial}${newDigits}`);
  }

  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-ink/80">Phone number</span>
      <div className="flex gap-2">
        <select
          value={dial}
          onChange={(e) => update(e.target.value, digits)}
          onBlur={onBlur}
          className="w-36 rounded-lg border border-line bg-paper px-2 py-2.5 text-sm outline-none focus:border-jet"
        >
          {COUNTRIES.map((c) => (
            <option key={`${c.name}-${c.dial}`} value={c.dial}>
              {c.dial} {c.name}
            </option>
          ))}
        </select>
        <input
          type="tel"
          inputMode="numeric"
          required
          value={digits}
          onChange={(e) => update(dial, e.target.value.replace(/\D/g, ""))}
          onBlur={onBlur}
          placeholder="771234567"
          className={`w-full rounded-lg border bg-paper px-3 py-2.5 outline-none focus:border-jet ${
            error ? "border-red-400" : "border-line"
          }`}
        />
      </div>
      {error && <span className="mt-1 block text-xs text-red-600">{error}</span>}
    </label>
  );
}
