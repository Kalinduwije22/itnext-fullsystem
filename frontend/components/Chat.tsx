"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Section } from "./PackagePicker";

interface Msg { role: "user" | "assistant"; content: string }

function renderInline(text: string, keyPrefix: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={`${keyPrefix}-${i}`}>{part.slice(2, -2)}</strong>
    ) : (
      <span key={`${keyPrefix}-${i}`}>{part}</span>
    )
  );
}

function Markdown({ text }: { text: string }) {
  const blocks = text.split(/\n\s*\n/);
  return (
    <div className="space-y-2">
      {blocks.map((block, i) => {
        const lines = block.split("\n").filter((l) => l.trim());
        const isList = lines.length > 0 && lines.every((l) => /^[*-]\s+/.test(l.trim()));
        if (isList) {
          return (
            <ul key={i} className="list-disc space-y-1 pl-4">
              {lines.map((l, j) => (
                <li key={j}>{renderInline(l.trim().replace(/^[*-]\s+/, ""), `${i}-${j}`)}</li>
              ))}
            </ul>
          );
        }
        return <p key={i}>{renderInline(lines.join(" "), `${i}`)}</p>;
      })}
    </div>
  );
}

export default function Chat() {
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: "assistant", content: "Hi! Ask me anything about your CV, interviews, or moving abroad." },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setMsgs((m) => [...m, { role: "user", content: text }]);
    setBusy(true);
    try {
      const { reply } = await api.chat(text);
      setMsgs((m) => [...m, { role: "assistant", content: reply }]);
    } catch (err) {
      setMsgs((m) => [
        ...m,
        { role: "assistant", content: err instanceof Error ? err.message : "Error." },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Section title="4 · Career assistant" note="Instant help, any time. Your advisor sees the highlights.">
      <div className="mb-4 max-h-72 space-y-3 overflow-y-auto">
        {msgs.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <span
              className={`inline-block max-w-[85%] rounded-2xl px-4 py-2 text-left text-sm ${
                m.role === "user" ? "bg-jet text-white" : "bg-paper text-ink"
              }`}
            >
              {m.role === "assistant" ? <Markdown text={m.content} /> : m.content}
            </span>
          </div>
        ))}
      </div>
      <form onSubmit={send} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          className="flex-1 rounded-lg border border-line bg-paper px-3 py-2.5 outline-none focus:border-jet"
        />
        <button disabled={busy}
          className="rounded-lg bg-jet px-5 font-medium text-white transition hover:bg-jet/90 disabled:opacity-60">
          Send
        </button>
      </form>
    </Section>
  );
}
