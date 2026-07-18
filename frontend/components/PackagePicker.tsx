"use client";

import { useEffect, useState } from "react";
import { api, type Package } from "@/lib/api";
import { useToast } from "./Toast";

export default function PackagePicker({
  onOrderCreated,
}: {
  onOrderCreated?: () => void;
}) {
  const [packages, setPackages] = useState<Package[]>([]);
  const [chosen, setChosen] = useState<string | null>(null);
  const [msg, setMsg] = useState("");
  const [pendingOrderId, setPendingOrderId] = useState<string | null>(null);
  const [simulating, setSimulating] = useState(false);
  const showToast = useToast();

  useEffect(() => {
    api.packages().then(setPackages).catch(() => setMsg("Couldn't load packages."));
  }, []);

  async function choose(pkg: Package) {
    setChosen(pkg.id);
    setMsg("");
    try {
      const order = await api.checkout(pkg.id);
      setPendingOrderId(order.order_id);
      setMsg(
        `Order created (LKR ${order.amount_lkr.toLocaleString("en-LK")}). ` +
          "You'd now be redirected to PayHere to complete payment. " +
          "Your CV upload step unlocks automatically once payment is confirmed."
      );
      showToast(`Order created for ${pkg.name} — LKR ${order.amount_lkr.toLocaleString("en-LK")}.`, "success");
      onOrderCreated?.();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Checkout failed.";
      setMsg(message);
      showToast(message, "error");
    }
  }

  async function simulatePayment() {
    if (!pendingOrderId) return;
    setSimulating(true);
    try {
      await api.simulatePaid(pendingOrderId);
      setMsg("Payment simulated — CV upload is now unlocked.");
      setPendingOrderId(null);
      showToast("Payment simulated — CV upload is unlocked.", "success");
      onOrderCreated?.();
    } catch {
      const message = "Simulate-payment isn't available (only works outside production).";
      setMsg(message);
      showToast(message, "error");
    } finally {
      setSimulating(false);
    }
  }

  return (
    <Section title="1 · Choose your package" note="Select the level of support you want.">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {packages.map((p) => (
          <button
            key={p.id}
            onClick={() => choose(p)}
            className={`rounded-xl border p-5 text-left transition duration-300 active:scale-95 ${
              chosen === p.id
                ? "scale-[1.02] border-jet bg-jet/5 shadow-md shadow-jet/10"
                : "border-line hover:-translate-y-0.5 hover:border-jet hover:shadow-md"
            }`}
          >
            <h4 className="font-display font-semibold">{p.name}</h4>
            <p className="mt-1 font-display text-xl font-bold">
              LKR {p.price_lkr.toLocaleString("en-LK")}
            </p>
            <p className="mt-2 text-xs text-ink/60">{p.description}</p>
          </button>
        ))}
      </div>
      {msg && <p className="mt-4 text-sm text-jet">{msg}</p>}
      {pendingOrderId && (
        <button
          onClick={simulatePayment}
          disabled={simulating}
          className="mt-3 rounded-lg border border-dashed border-jet px-3 py-1.5 text-xs font-mono text-jet transition active:scale-95 hover:bg-jet/5 disabled:opacity-50"
        >
          {simulating ? "Simulating…" : "Simulate payment (dev/testing only — no PayHere needed)"}
        </button>
      )}
    </Section>
  );
}

export function Section({ title, note, children }:
  { title: string; note?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-line bg-white p-7">
      <h3 className="font-display text-lg font-bold">{title}</h3>
      {note && <p className="mb-5 mt-1 text-sm text-ink/60">{note}</p>}
      {children}
    </section>
  );
}
