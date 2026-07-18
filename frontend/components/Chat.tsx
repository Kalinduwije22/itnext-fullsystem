"use client";

import { useState } from "react";
import { api } from "@/lib/api";

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
  const [open, setOpen] = useState(false);
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
    <>
      {open && (
        <div className="fixed bottom-24 right-6 z-50 flex h-[28rem] w-[22rem] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-2xl border border-line bg-white shadow-xl">
          <div className="flex items-center justify-between border-b border-line bg-ink px-4 py-3 text-white">
            <div>
              <p className="font-display text-sm font-bold">Career assistant</p>
              <p className="text-xs text-white/60">Instant help, any time.</p>
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label="Close chat"
              className="rounded-full p-1 text-white/70 transition hover:bg-white/10 hover:text-white"
            >
              ✕
            </button>
          </div>
          <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
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
          <form onSubmit={send} className="flex gap-2 border-t border-line p-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your question..."
              className="flex-1 rounded-lg border border-line bg-paper px-3 py-2.5 text-sm outline-none focus:border-jet"
            />
            <button disabled={busy}
              className="rounded-lg bg-jet px-4 text-sm font-medium text-white transition hover:bg-jet/90 disabled:opacity-60">
              Send
            </button>
          </form>
        </div>
      )}

      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close career assistant chat" : "Open career assistant chat"}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-jet text-white shadow-lg transition hover:bg-jet/90 active:scale-95"
      >
        {open ? "✕" : "💬"}
      </button>
    </>
  );
}
