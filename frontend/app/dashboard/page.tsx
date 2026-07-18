"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, type Order } from "@/lib/api";
import { auth } from "@/lib/auth";
import PackagePicker from "@/components/PackagePicker";
import CVUpload from "@/components/CVUpload";
import AssessmentForm from "@/components/AssessmentForm";
import Chat from "@/components/Chat";
import { Spinner } from "@/components/Spinner";

export default function Dashboard() {
  const router = useRouter();
  const [name, setName] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [checked, setChecked] = useState(false);
  const [orders, setOrders] = useState<Order[]>([]);

  const refreshOrders = useCallback(() => {
    api.myOrders().then(setOrders).catch(() => {});
  }, []);

  useEffect(() => {
    if (!auth.isLoggedIn()) {
      router.replace("/login");
      return;
    }
    api
      .me()
      .then((u) => {
        setName(u.full_name);
        setIsAdmin(u.is_admin);
      })
      .catch(() => {
        auth.clear();
        router.replace("/login");
      })
      .finally(() => setChecked(true));
    refreshOrders();
  }, [router, refreshOrders]);

  const hasPaid = orders.some((o) => o.status === "paid");
  const hasPendingOrder = orders.some((o) => o.status === "pending");

  useEffect(() => {
    if (!hasPendingOrder || hasPaid) return;
    const id = setInterval(refreshOrders, 4000);
    return () => clearInterval(id);
  }, [hasPendingOrder, hasPaid, refreshOrders]);

  if (!checked) {
    return (
      <div className="grid min-h-screen place-items-center">
        <Spinner />
      </div>
    );
  }

  return (
    <main className="min-h-screen">
      <header className="bg-ink text-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
          <Link href="/" className="flex items-baseline gap-2">
            <span className="font-display text-lg font-bold">ITNEXT</span>
            <span className="eyebrow">Global Careers</span>
          </Link>
          <div className="flex items-center gap-5 text-sm">
            <span className="text-white/70">{name}</span>
            {isAdmin && (
              <Link href="/admin" className="text-white/70 hover:text-jet">
                Admin
              </Link>
            )}
            <button
              onClick={() => {
                auth.clear();
                router.push("/");
              }}
              className="text-white/70 hover:text-jet"
            >
              Log out
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-6 py-10">
        <p className="eyebrow">Your profile</p>
        <h1 className="mb-8 mt-2 font-display text-3xl font-bold">
          Welcome{name ? `, ${name.split(" ")[0]}` : ""}.
        </h1>
        <div className="space-y-6">
          <PackagePicker onOrderCreated={refreshOrders} />
          <CVUpload unlocked={hasPaid} />
          <AssessmentForm />
        </div>
      </div>

      <Chat />
    </main>
  );
}
