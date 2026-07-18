"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { auth } from "@/lib/auth";
import { useToast } from "@/components/Toast";
import { AuthShell, Field } from "@/components/AuthShell";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";

export default function LoginPage() {
  const router = useRouter();
  const showToast = useToast();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { access_token } = await api.login(form.email, form.password);
      auth.set(access_token);
      showToast("Welcome back!", "success");
      router.push("/dashboard");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Invalid credentials";
      setError(message);
      showToast(message, "error");
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
    <AuthShell title="Welcome back" subtitle="Pick up where you left off.">
      <form onSubmit={submit} className="space-y-4">
        <Field label="Email" type="email" value={form.email}
          onChange={(v) => setForm({ ...form, email: v })} />
        <Field label="Password" type="password" value={form.password}
          onChange={(v) => setForm({ ...form, password: v })} />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading}
          className="w-full rounded-lg bg-jet py-2.5 font-medium text-white transition active:scale-95 hover:bg-jet/90 disabled:opacity-60">
          {loading ? "Signing in…" : "Log in"}
        </button>
      </form>
      <GoogleSignInButton onCredential={handleGoogleCredential} />
      <p className="mt-6 text-center text-sm text-ink/60">
        New here?{" "}
        <Link href="/signup" className="text-jet hover:underline">Create a profile</Link>
      </p>
    </AuthShell>
  );
}
