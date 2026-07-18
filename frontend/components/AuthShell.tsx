import Link from "next/link";

export function AuthShell({ title, subtitle, children }:
  { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="animate-fade-up w-full max-w-md">
        <Link href="/" className="mb-8 flex items-baseline justify-center gap-2">
          <span className="font-display text-xl font-bold text-ink">ITNEXT</span>
          <span className="eyebrow">Global Careers</span>
        </Link>
        <div className="rounded-2xl border border-line bg-white p-8">
          <h1 className="font-display text-2xl font-bold">{title}</h1>
          <p className="mb-6 mt-1 text-sm text-ink/60">{subtitle}</p>
          {children}
        </div>
      </div>
    </main>
  );
}

export function Field({ label, value, onChange, type = "text", error, onBlur }:
  {
    label: string; value: string; onChange: (v: string) => void; type?: string;
    error?: string; onBlur?: () => void;
  }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-ink/80">{label}</span>
      <input type={type} value={value} required
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        className={`w-full rounded-lg border bg-paper px-3 py-2.5 outline-none focus:border-jet ${
          error ? "border-red-400" : "border-line"
        }`} />
      {error && <span className="mt-1 block text-xs text-red-600">{error}</span>}
    </label>
  );
}