"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { auth } from "@/lib/auth";
import { useToast } from "@/components/Toast";
import { AuthShell, Field } from "@/components/AuthShell";
import { PhoneInput } from "@/components/PhoneInput";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^\+[1-9]\d{6,14}$/;

function nameError(v: string) {
  return v.trim().length >= 2 ? undefined : "Enter your full name (at least 2 characters).";
}
function emailError(v: string) {
  return EMAIL_RE.test(v) ? undefined : "Enter a valid email address.";
}
function passwordError(v: string) {
  if (v.length < 8) return "At least 8 characters.";
  if (!/[A-Za-z]/.test(v) || !/\d/.test(v)) return "Include at least one letter and one number.";
  return undefined;
}
function phoneError(v: string) {
  return PHONE_RE.test(v) ? undefined : "Enter a valid phone number.";
}

export default function SignupPage() {
  const router = useRouter();
  const showToast = useToast();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", phone: "" });
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);

  const errors = {
    full_name: nameError(form.full_name),
    email: emailError(form.email),
    password: passwordError(form.password),
    phone: phoneError(form.phone),
  };
  const formValid = !errors.full_name && !errors.email && !errors.password && !errors.phone;

  function touch(field: string) {
    setTouched((t) => ({ ...t, [field]: true }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setTouched({ full_name: true, email: true, password: true, phone: true });
    if (!formValid) return;
    setLoading(true);
    try {
      await api.register(form.email, form.full_name, form.password, form.phone);
      const { access_token } = await api.login(form.email, form.password);
      auth.set(access_token);
      showToast("Account created — welcome!", "success");
      router.push("/dashboard");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Something went wrong", "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleCredential(credential: string) {
    try {
      const { access_token } = await api.googleAuth(credential);
      auth.set(access_token);
      showToast("Signed in with Google.", "success");
      router.push("/dashboard");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Google sign-in failed", "error");
    }
  }

  return (
    <AuthShell title="Create your profile" subtitle="Step one of your journey.">
      <form onSubmit={submit} className="space-y-4">
        <Field label="Full name" value={form.full_name}
          onChange={(v) => setForm({ ...form, full_name: v })}
          onBlur={() => touch("full_name")}
          error={touched.full_name ? errors.full_name : undefined} />
        <Field label="Email" type="email" value={form.email}
          onChange={(v) => setForm({ ...form, email: v })}
          onBlur={() => touch("email")}
          error={touched.email ? errors.email : undefined} />
        <PhoneInput value={form.phone}
          onChange={(v) => setForm({ ...form, phone: v })}
          onBlur={() => touch("phone")}
          error={touched.phone ? errors.phone : undefined} />
        <Field label="Password" type="password" value={form.password}
          onChange={(v) => setForm({ ...form, password: v })}
          onBlur={() => touch("password")}
          error={touched.password ? errors.password : undefined} />
        <button disabled={loading}
          className="w-full rounded-lg bg-jet py-2.5 font-medium text-white transition active:scale-95 hover:bg-jet/90 disabled:opacity-60">
          {loading ? "Creating…" : "Create account"}
        </button>
      </form>
      <GoogleSignInButton onCredential={handleGoogleCredential} />
      <p className="mt-6 text-center text-sm text-ink/60">
        Already have an account?{" "}
        <Link href="/login" className="text-jet hover:underline">Log in</Link>
      </p>
    </AuthShell>
  );
}
