"use client";

import { Fragment, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  api,
  type AdminCV,
  type AdminOrder,
  type AdminStats,
  type AdminUser,
} from "@/lib/api";
import { auth } from "@/lib/auth";
import { Section } from "@/components/PackagePicker";
import { useToast } from "@/components/Toast";
import { Spinner } from "@/components/Spinner";

export default function AdminPage() {
  const router = useRouter();
  const [checked, setChecked] = useState(false);
  const [allowed, setAllowed] = useState(false);
  const [error, setError] = useState("");
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [orders, setOrders] = useState<AdminOrder[]>([]);
  const [cvs, setCvs] = useState<AdminCV[]>([]);

  useEffect(() => {
    if (!auth.isLoggedIn()) {
      router.replace("/login");
      return;
    }
    api
      .me()
      .then((u) => {
        if (!u.is_admin) {
          router.replace("/dashboard");
          return;
        }
        setAllowed(true);
        return Promise.all([
          api.admin.stats(),
          api.admin.users(),
          api.admin.orders(),
          api.admin.cvs(),
        ]).then(([s, u2, o, c]) => {
          setStats(s);
          setUsers(u2);
          setOrders(o);
          setCvs(c);
        });
      })
      .catch(() => setError("Couldn't load admin data."))
      .finally(() => setChecked(true));
  }, [router]);

  if (!checked || !allowed) {
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
          <Link href="/dashboard" className="text-sm text-white/70 hover:text-jet">
            Back to dashboard
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-5xl space-y-6 px-6 py-10">
        <div>
          <p className="eyebrow">Admin</p>
          <h1 className="mb-2 mt-2 font-display text-3xl font-bold">
            Users, CVs &amp; payments
          </h1>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        {stats && (
          <Section title="Overview">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
              <Stat label="Users" value={stats.total_users} />
              <Stat label="Orders" value={stats.total_orders} />
              <Stat label="Paid orders" value={stats.paid_orders} />
              <Stat label="CVs uploaded" value={stats.total_cvs} />
              <Stat
                label="Revenue (LKR)"
                value={stats.revenue_lkr.toLocaleString("en-LK")}
              />
            </div>
          </Section>
        )}

        <Section title={`Users (${users.length})`}>
          <Table
            columns={["Email", "Name", "Phone", "Admin", "Joined"]}
            rows={users.map((u) => [
              u.email,
              u.full_name,
              u.phone ?? "—",
              u.is_admin ? "Yes" : "",
              new Date(u.created_at).toLocaleDateString(),
            ])}
          />
        </Section>

        <Section title={`Uploaded CVs (${cvs.length})`}>
          <CVTable
            cvs={cvs}
            onGraded={(updated) =>
              setCvs((prev) => prev.map((c) => (c.id === updated.id ? updated : c)))
            }
          />
        </Section>

        <Section title={`Orders (${orders.length})`}>
          <Table
            columns={["User", "Amount (LKR)", "Status", "Created"]}
            rows={orders.map((o) => [
              o.user_email,
              o.amount_lkr.toLocaleString("en-LK"),
              o.status,
              new Date(o.created_at).toLocaleDateString(),
            ])}
          />
        </Section>
      </div>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-line p-4">
      <p className="font-display text-2xl font-bold">{value}</p>
      <p className="mt-1 text-xs text-ink/60">{label}</p>
    </div>
  );
}

function CVTable({
  cvs,
  onGraded,
}: {
  cvs: AdminCV[];
  onGraded: (updated: AdminCV) => void;
}) {
  const [downloading, setDownloading] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState("");
  const [gradingId, setGradingId] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const [scoreDraft, setScoreDraft] = useState<Record<string, string>>({});
  const [feedbackDraft, setFeedbackDraft] = useState<Record<string, string>>({});
  const showToast = useToast();

  async function download(cv: AdminCV) {
    setDownloadError("");
    setDownloading(cv.id);
    try {
      const blob = await api.admin.downloadCv(cv.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = cv.filename;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`Downloaded ${cv.filename}.`, "success");
    } catch {
      setDownloadError(`Couldn't download ${cv.filename}.`);
      showToast(`Couldn't download ${cv.filename}.`, "error");
    } finally {
      setDownloading(null);
    }
  }

  function startGrading(cv: AdminCV) {
    setGradingId(cv.id);
    setScoreDraft((d) => ({ ...d, [cv.id]: d[cv.id] ?? String(cv.grade_score ?? "") }));
    setFeedbackDraft((d) => ({ ...d, [cv.id]: d[cv.id] ?? cv.grade_feedback ?? "" }));
  }

  async function saveGrade(cv: AdminCV) {
    const score = Number(scoreDraft[cv.id]);
    const feedback = feedbackDraft[cv.id] ?? "";
    if (!Number.isInteger(score) || score < 0 || score > 100) {
      showToast("Score must be a whole number from 0 to 100.", "error");
      return;
    }
    if (!feedback.trim()) {
      showToast("Feedback is required.", "error");
      return;
    }
    setSaving(cv.id);
    try {
      const updated = await api.admin.gradeCv(cv.id, score, feedback.trim());
      onGraded(updated);
      setGradingId(null);
      showToast(`Graded ${cv.filename}.`, "success");
    } catch {
      showToast(`Couldn't save the grade for ${cv.filename}.`, "error");
    } finally {
      setSaving(null);
    }
  }

  if (cvs.length === 0) {
    return <p className="text-sm text-ink/50">Nothing here yet.</p>;
  }

  return (
    <div className="overflow-x-auto">
      {downloadError && <p className="mb-2 text-sm text-red-600">{downloadError}</p>}
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-line text-xs uppercase tracking-wide text-ink/50">
            <th className="py-2 pr-4 font-medium">User</th>
            <th className="py-2 pr-4 font-medium">Filename</th>
            <th className="py-2 pr-4 font-medium">Status</th>
            <th className="py-2 pr-4 font-medium">Uploaded</th>
            <th className="py-2 pr-4 font-medium">Score</th>
            <th className="py-2 pr-4 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {cvs.map((c) => (
            <Fragment key={c.id}>
              <tr className="border-b border-line/60">
                <td className="py-2 pr-4">{c.user_email}</td>
                <td className="py-2 pr-4">{c.filename}</td>
                <td className="py-2 pr-4">{c.status}</td>
                <td className="py-2 pr-4">
                  {new Date(c.created_at).toLocaleDateString()}
                </td>
                <td className="py-2 pr-4">{c.grade_score ?? "—"}</td>
                <td className="space-x-3 py-2 pr-4">
                  <button
                    onClick={() => download(c)}
                    disabled={downloading === c.id}
                    className="text-jet hover:underline disabled:opacity-50"
                  >
                    {downloading === c.id ? "Downloading…" : "Download"}
                  </button>
                  <button
                    onClick={() =>
                      gradingId === c.id ? setGradingId(null) : startGrading(c)
                    }
                    className="text-jet hover:underline"
                  >
                    {c.grade_score != null ? "Edit grade" : "Grade"}
                  </button>
                </td>
              </tr>
              {gradingId === c.id && (
                <tr className="border-b border-line/60 bg-paper">
                  <td colSpan={6} className="px-4 py-3">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start">
                      <input
                        type="number"
                        min={0}
                        max={100}
                        placeholder="Score (0-100)"
                        value={scoreDraft[c.id] ?? ""}
                        onChange={(e) =>
                          setScoreDraft((d) => ({ ...d, [c.id]: e.target.value }))
                        }
                        className="w-full rounded-lg border border-line px-3 py-2 sm:w-32"
                      />
                      <textarea
                        placeholder="Feedback"
                        value={feedbackDraft[c.id] ?? ""}
                        onChange={(e) =>
                          setFeedbackDraft((d) => ({ ...d, [c.id]: e.target.value }))
                        }
                        className="w-full flex-1 rounded-lg border border-line px-3 py-2"
                        rows={2}
                      />
                      <button
                        onClick={() => saveGrade(c)}
                        disabled={saving === c.id}
                        className="shrink-0 rounded-lg bg-jet px-4 py-2 font-medium text-white transition hover:bg-jet/90 disabled:opacity-60"
                      >
                        {saving === c.id ? "Saving…" : "Save grade"}
                      </button>
                    </div>
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Table({ columns, rows }: { columns: string[]; rows: string[][] }) {
  if (rows.length === 0) {
    return <p className="text-sm text-ink/50">Nothing here yet.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-line text-xs uppercase tracking-wide text-ink/50">
            {columns.map((c) => (
              <th key={c} className="py-2 pr-4 font-medium">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-line/60">
              {row.map((cell, j) => (
                <td key={j} className="py-2 pr-4">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
