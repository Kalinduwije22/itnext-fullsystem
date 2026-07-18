"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useToast } from "./Toast";
import { Section } from "./PackagePicker";

const FIELDS = [
  ["current_role", "Current role / field", "text"],
  ["experience_years", "Years of experience", "number"],
  ["target_country", "Target country", "text"],
  ["target_role", "Role you're aiming for", "text"],
  ["timeline", "When do you want to move?", "text"],
] as const;

export default function AssessmentForm() {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);
  const showToast = useToast();

  async function save(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.saveAssessment(answers);
      setSaved(true);
      showToast("Profile saved.", "success");
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Couldn't save profile.", "error");
    }
  }

  return (
    <Section title="3 · Your professional profile" note="Tell us where you are and where you want to be.">
      <form onSubmit={save} className="grid gap-4 sm:grid-cols-2">
        {FIELDS.map(([key, label, type]) => (
          <label key={key} className="block">
            <span className="mb-1 block text-sm font-medium text-ink/80">{label}</span>
            <input
              type={type}
              value={answers[key] ?? ""}
              onChange={(e) => setAnswers({ ...answers, [key]: e.target.value })}
              className="w-full rounded-lg border border-line bg-paper px-3 py-2.5 outline-none focus:border-jet"
            />
          </label>
        ))}
        <div className="sm:col-span-2">
          <button className="rounded-lg bg-jet px-5 py-2.5 font-medium text-white transition hover:bg-jet/90">
            {saved ? "Saved \u2713" : "Save profile"}
          </button>
        </div>
      </form>
    </Section>
  );
}
