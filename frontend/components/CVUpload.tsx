"use client";

import { useEffect, useState } from "react";
import { api, type CV } from "@/lib/api";
import { useToast } from "./Toast";
import { Section } from "./PackagePicker";

export default function CVUpload({ unlocked }: { unlocked: boolean }) {
  const [status, setStatus] = useState("");
  const [cv, setCv] = useState<CV | null>(null);
  const [downloading, setDownloading] = useState(false);
  const showToast = useToast();

  useEffect(() => {
    if (!unlocked) return;
    api.myCv().then(setCv).catch(() => {});
  }, [unlocked]);

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setStatus(`Uploading ${file.name}…`);
    try {
      // Uploads go straight to our own API, which stores the bytes
      // server-side and creates the record — this also supersedes any
      // previous CV, so the new (ungraded) doc becomes what's shown below.
      const doc = await api.uploadCV(file);
      setCv(doc);
      setStatus(`${file.name} received. We'll parse it and pre-fill your profile.`);
      showToast(`${file.name} uploaded successfully.`, "success");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed.";
      setStatus(message);
      showToast(message, "error");
    }
  }

  async function download() {
    setDownloading(true);
    try {
      const blob = await api.downloadMyCv();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = cv?.filename ?? "cv";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      showToast("Couldn't download your CV.", "error");
    } finally {
      setDownloading(false);
    }
  }

  async function dismissGrade() {
    try {
      setCv(await api.acknowledgeGrade());
    } catch {
      showToast("Couldn't dismiss the notification.", "error");
    }
  }

  if (!unlocked) {
    return (
      <Section
        title="2 · Upload your CV"
        note="Purchase a package above to unlock CV upload."
      >
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-line bg-paper py-10 text-center opacity-60">
          <span className="font-mono text-sm text-ink/50">LOCKED</span>
          <span className="mt-1 text-xs text-ink/50">
            Complete payment for your package to unlock this step.
          </span>
        </div>
      </Section>
    );
  }

  const showBanner = cv && cv.grade_score != null && !cv.grade_acknowledged;

  return (
    <div className="animate-fade-up">
      <Section
        title={cv ? "2 · Your CV" : "2 · Upload your CV"}
        note="PDF or Word. We extract your skills automatically."
      >
        {showBanner && (
          <div className="mb-4 rounded-xl border border-gold bg-gold/10 p-4">
            <p className="text-sm font-medium text-ink">
              Your CV was graded: {cv!.grade_score}/100
            </p>
            {cv!.grade_feedback && (
              <p className="mt-1 text-sm text-ink/80">{cv!.grade_feedback}</p>
            )}
            <button onClick={dismissGrade} className="mt-2 text-sm text-jet hover:underline">
              Dismiss
            </button>
          </div>
        )}

        {cv && (
          <div className="mb-4 flex items-center justify-between rounded-xl border border-line bg-paper px-4 py-3 text-sm">
            <div>
              <p className="font-medium text-ink">{cv.filename}</p>
              <p className="mt-0.5 text-xs text-ink/60">
                Uploaded {new Date(cv.created_at).toLocaleDateString()} · {cv.status}
                {cv.grade_score != null && !showBanner && <> · Score: {cv.grade_score}/100</>}
              </p>
              {cv.grade_feedback && !showBanner && (
                <p className="mt-1 text-xs text-ink/60">{cv.grade_feedback}</p>
              )}
            </div>
            <button
              onClick={download}
              disabled={downloading}
              className="shrink-0 text-jet hover:underline disabled:opacity-50"
            >
              {downloading ? "Downloading…" : "Download"}
            </button>
          </div>
        )}

        <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-line bg-paper py-10 text-center transition hover:border-jet">
          <span className="font-mono text-sm text-jet">
            {cv ? "REPLACE FILE" : "DROP / SELECT FILE"}
          </span>
          <span className="mt-1 text-xs text-ink/50">.pdf, .doc, .docx</span>
          <input type="file" accept=".pdf,.doc,.docx" className="hidden" onChange={onFile} />
        </label>
        {status && <p className="mt-4 text-sm text-ink/70">{status}</p>}
      </Section>
    </div>
  );
}
