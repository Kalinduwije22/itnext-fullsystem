import Link from "next/link";
import Nav from "@/components/Nav";
import { Reveal } from "@/components/Reveal";

const JOURNEY = [
  ["01", "Assessment", "Career + employability review"],
  ["02", "Branding", "CV & LinkedIn, market-tailored"],
  ["03", "Skills", "Certifications & training paths"],
  ["04", "Matching", "Verified international roles"],
  ["05", "Applications", "Submitted & tracked for you"],
  ["06", "Interviews", "Mock rounds & coaching"],
  ["07", "Visa & move", "Documentation & relocation"],
  ["08", "Growth", "Support after you land"],
];

const SERVICES = [
  ["Career assessment", "Employability score, occupation mapping, salary benchmark."],
  ["Professional branding", "CV optimised for UK/AU/CA markets, ATS-friendly, LinkedIn."],
  ["Skills development", "Technical & soft skills, IELTS, industry certifications."],
  ["Job matching", "Employer matching, weekly alerts, sponsorship roles."],
  ["Application management", "Submission, tracking, recruiter follow-up."],
  ["Interview services", "Mock interviews, behavioural coaching, salary negotiation."],
  ["Visa & relocation", "Documentation, CoS guidance, accommodation, arrival support."],
  ["Career coaching", "Roadmap, promotion strategy, long-term mentoring."],
];

const PACKAGES = [
  ["Starter", 4900, ["Career assessment", "CV review", "LinkedIn review", "Job search guide"], false],
  ["Professional", 9900, ["Everything in Starter", "Interview coaching", "20 applications", "Cover letters"], true],
  ["Premium", 14900, ["Everything in Professional", "Unlimited applications", "Priority support", "Employer introductions"], false],
  ["VIP", 19900, ["End-to-end service", "Dedicated advisor", "Weekly meetings", "Relocation + salary help"], false],
] as const;

const lkr = (n: number) => "LKR " + n.toLocaleString("en-LK");

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* ---------- HERO ---------- */}
      <div className="relative overflow-hidden bg-ink text-white">
        <div
          aria-hidden
          className="pointer-events-none absolute -top-40 left-1/2 h-[32rem] w-[32rem] -translate-x-1/2 rounded-full bg-jet/20 blur-3xl"
        />
        <Nav variant="dark" />
        <section className="relative mx-auto max-w-6xl px-6 pb-24 pt-10">
          <p className="eyebrow mb-5 animate-fade-up">
            Colombo &rarr; London &nbsp;·&nbsp; boarding
          </p>
          <h1 className="animate-fade-up max-w-3xl font-display text-5xl font-bold leading-[1.05] tracking-tight [animation-delay:100ms] sm:text-6xl">
            Sri Lankan talent,
            <br />
            <span className="text-jet">global opportunities.</span>
          </h1>
          <p className="animate-fade-up mt-6 max-w-xl text-lg text-white/70 [animation-delay:200ms]">
            We don&apos;t just help you find a job abroad. We prepare you to
            compete and succeed in international markets — from your first CV to
            your first day overseas, and beyond.
          </p>
          <div className="animate-fade-up mt-9 flex flex-wrap gap-4 [animation-delay:300ms]">
            <Link
              href="/signup"
              className="rounded-lg bg-jet px-6 py-3 font-medium text-white transition active:scale-95 hover:bg-jet/90"
            >
              Start your journey
            </Link>
            <Link
              href="/#packages"
              className="rounded-lg border border-white/25 px-6 py-3 font-medium text-white/90 transition active:scale-95 hover:border-jet hover:text-jet"
            >
              See packages
            </Link>
          </div>

          {/* flight-path journey strip */}
          <div className="animate-fade-up mt-20 [animation-delay:400ms]">
            <div className="flightpath mb-8 w-full" />
            <ol className="grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-4 lg:grid-cols-8">
              {JOURNEY.map(([code, title, sub]) => (
                <li key={code}>
                  <span className="font-mono text-xs text-sky">{code}</span>
                  <p className="mt-1 font-display text-sm font-semibold">{title}</p>
                  <p className="mt-1 text-xs leading-snug text-white/55">{sub}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>
      </div>

      {/* ---------- VALUE PROP ---------- */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="grid gap-10 md:grid-cols-2">
          <Reveal className="rounded-2xl border border-line bg-white p-8">
            <p className="eyebrow">For candidates</p>
            <h2 className="mt-3 font-display text-2xl font-bold">
              Job-ready for the world, not just applied.
            </h2>
            <p className="mt-3 text-ink/70">
              International-standard CVs tailored by market, a skills-gap plan
              with recommended training, and honest guidance — no misleading
              &ldquo;guaranteed job&rdquo; claims.
            </p>
          </Reveal>
          <Reveal delay={100} className="rounded-2xl border border-line bg-white p-8">
            <p className="eyebrow">For employers</p>
            <h2 className="mt-3 font-display text-2xl font-bold">
              Verified, prepared professionals.
            </h2>
            <p className="mt-3 text-ink/70">
              Access screened Sri Lankan talent that arrives interview-ready and
              internationally prepared, with ongoing support through relocation.
            </p>
          </Reveal>
        </div>
      </section>

      {/* ---------- SERVICES ---------- */}
      <section id="services" className="mx-auto max-w-6xl px-6 py-8">
        <p className="eyebrow">The portfolio</p>
        <h2 className="mt-3 font-display text-3xl font-bold">
          Eight services, one continuous journey.
        </h2>
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {SERVICES.map(([title, desc], i) => (
            <Reveal key={title} delay={(i % 4) * 60}>
              <div className="h-full rounded-xl border border-line bg-white p-6 transition duration-300 hover:-translate-y-1 hover:border-jet hover:shadow-lg hover:shadow-jet/10">
                <span className="font-mono text-xs text-jet">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h3 className="mt-2 font-display text-lg font-semibold">{title}</h3>
                <p className="mt-2 text-sm text-ink/65">{desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---------- PACKAGES ---------- */}
      <section id="packages" className="mx-auto max-w-6xl px-6 py-20">
        <p className="eyebrow">Choose your boarding class</p>
        <h2 className="mt-3 font-display text-3xl font-bold">Packages</h2>
        <p className="mt-2 text-ink/60">
          Transparent, published pricing. Upgrade any time.
        </p>
        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {PACKAGES.map(([name, price, features, popular], i) => (
            <Reveal key={name} delay={i * 80} className="h-full">
              <div
                className={`relative flex h-full flex-col rounded-2xl border bg-white p-7 transition duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-jet/10 ${
                  popular ? "border-jet shadow-lg shadow-jet/10" : "border-line"
                }`}
              >
                {popular && (
                  <span className="absolute -top-3 left-7 rounded-full bg-jet px-3 py-1 text-xs font-medium text-white">
                    Most chosen
                  </span>
                )}
                <h3 className="font-display text-xl font-bold">{name}</h3>
                <p className="mt-3 font-display text-3xl font-bold text-ink">
                  {lkr(price)}
                </p>
                <ul className="mt-5 flex-1 space-y-2 text-sm text-ink/70">
                  {features.map((f) => (
                    <li key={f} className="flex gap-2">
                      <span className="text-jet">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/signup"
                  className={`mt-6 rounded-lg px-4 py-2.5 text-center font-medium transition active:scale-95 ${
                    popular
                      ? "bg-jet text-white hover:bg-jet/90"
                      : "border border-line text-ink hover:border-jet hover:text-jet"
                  }`}
                >
                  Choose {name}
                </Link>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---------- CTA ---------- */}
      <section className="mx-auto max-w-6xl px-6 pb-24">
        <Reveal className="rounded-2xl bg-ink px-8 py-14 text-center text-white">
          <h2 className="font-display text-3xl font-bold">
            Let&apos;s build your global future.
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-white/70">
            Create your profile, pick a package, and upload your CV. Your advisor
            takes it from there.
          </p>
          <Link
            href="/signup"
            className="mt-8 inline-block rounded-lg bg-jet px-7 py-3 font-medium text-white transition active:scale-95 hover:bg-jet/90"
          >
            Get started
          </Link>
        </Reveal>
      </section>

      <footer className="border-t border-line py-8 text-center text-sm text-ink/50">
        ITNEXT Global Careers · Colombo, Sri Lanka ·{" "}
        <span className="font-mono">info@itnextglobalcareers.com</span>
      </footer>
    </main>
  );
}
