import Link from "next/link";

export default function Nav({ variant = "light" }: { variant?: "light" | "dark" }) {
  const dark = variant === "dark";
  return (
    <header
      className={`sticky top-0 z-40 w-full backdrop-blur-sm ${dark ? "bg-ink/90" : "bg-paper/80"} `}
    >
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href="/" className="flex items-baseline gap-2">
          <span
            className={`font-display text-xl font-bold tracking-tight ${
              dark ? "text-white" : "text-ink"
            }`}
          >
            ITNEXT
          </span>
          <span className="eyebrow">Global Careers</span>
        </Link>
        <div className="flex items-center gap-6 text-sm">
          <Link
            href="/#services"
            className={`hidden sm:inline ${dark ? "text-white/80" : "text-ink/70"} hover:text-jet`}
          >
            Services
          </Link>
          <Link
            href="/#packages"
            className={`hidden sm:inline ${dark ? "text-white/80" : "text-ink/70"} hover:text-jet`}
          >
            Packages
          </Link>
          <Link
            href="/login"
            className={`${dark ? "text-white/80" : "text-ink/70"} hover:text-jet`}
          >
            Log in
          </Link>
          <Link
            href="/signup"
            className="rounded-lg bg-jet px-4 py-2 font-medium text-white transition hover:bg-jet/90"
          >
            Get started
          </Link>
        </div>
      </nav>
    </header>
  );
}
