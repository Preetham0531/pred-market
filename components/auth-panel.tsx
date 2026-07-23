"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Loader2, LockKeyhole } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type AuthPanelProps = {
  mode: "sign-in" | "sign-up";
};

export function AuthPanel({ mode }: AuthPanelProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const requestedNext = searchParams.get("next");
  const next = useMemo(() => {
    if (!requestedNext || !requestedNext.startsWith("/") || requestedNext.startsWith("/sign-")) return "/";
    return requestedNext;
  }, [requestedNext]);
  const { user, loading, signIn, signUp, verifyMfa } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const isSignIn = mode === "sign-in";

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      if (mfaRequired) {
        await verifyMfa(mfaCode);
      } else if (isSignIn) {
        const result = await signIn(email, password);
        if (result.mfaRequired) {
          setMfaRequired(true);
          return;
        }
        if (result.mfaSetupRequired) {
          router.push("/account/security");
          return;
        }
      } else {
        await signUp(email, password, displayName);
      }
      router.push(next);
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Authentication failed.");
    } finally {
      setSubmitting(false);
    }
  }

  useEffect(() => {
    if (loading || !user || submitting) return;
    if (user.mfa.required && !user.mfa.enrolled) {
      router.replace("/account/security");
      return;
    }
    router.replace(user.roles.includes("ADMIN") && next === "/" ? "/admin" : next);
  }, [loading, next, router, submitting, user]);

  return (
    <main className="grid min-h-dvh place-items-center bg-[var(--background)] px-4 py-8 text-[var(--foreground)]">
      <div className="w-full max-w-[420px]">
        <Link href="/" className="mb-8 flex items-center justify-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-md bg-[var(--primary)] text-sm font-semibold text-white">PM</span>
          <span>
            <span className="block text-sm font-semibold">Pred-Market</span>
            <span className="block text-xs text-[var(--green-text)]">Simulated funds</span>
          </span>
        </Link>

        <section className="rounded-md border border-[var(--border)] bg-[var(--surface-raised)] p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)] sm:p-6">
          <div className="mb-5">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-[var(--primary-soft)] text-[var(--primary-strong)]">
              <LockKeyhole className="h-5 w-5" />
            </div>
            <h1 className="mt-4 text-2xl font-semibold">
              {mfaRequired ? "Verify your sign-in" : isSignIn ? "Sign in" : "Create account"}
            </h1>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {mfaRequired ? "Enter your authenticator or recovery code." : isSignIn ? "Continue to your markets." : "Start trading with simulated funds."}
            </p>
          </div>

          <form className="space-y-4" onSubmit={submit}>
            {!mfaRequired && !isSignIn ? (
              <label className="block">
                <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Display name</span>
                <Input className="h-11" value={displayName} onChange={(event) => setDisplayName(event.target.value)} autoComplete="name" required minLength={2} maxLength={80} />
              </label>
            ) : null}
            {!mfaRequired ? (
              <label className="block">
                <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Email</span>
                <Input className="h-11" value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete={isSignIn ? "username" : "email"} required />
              </label>
            ) : null}
            {!mfaRequired ? (
              <label className="block">
                <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Password</span>
                <Input className="h-11" value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete={isSignIn ? "current-password" : "new-password"} required minLength={isSignIn ? 1 : 12} />
              </label>
            ) : null}
            {mfaRequired ? (
              <label className="block">
                <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Authenticator or recovery code</span>
                <Input className="h-11 font-mono" value={mfaCode} onChange={(event) => setMfaCode(event.target.value)} autoComplete="one-time-code" placeholder="000000" required minLength={6} maxLength={32} autoFocus />
              </label>
            ) : null}
            {error ? <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red-text)]" role="alert">{error}</div> : null}
            <Button className="h-11 w-full" variant="primary" type="submit" disabled={submitting}>
              {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {submitting ? "Working" : mfaRequired ? "Verify and continue" : isSignIn ? "Sign in" : "Create account"}
              {!submitting ? <ArrowRight className="h-4 w-4" /> : null}
            </Button>
          </form>

          {mfaRequired ? (
            <button
              type="button"
              className="mt-4 text-sm text-[var(--muted)] hover:text-[var(--foreground)]"
              onClick={() => {
                setMfaRequired(false);
                setMfaCode("");
                setPassword("");
                setError("");
              }}
            >
              Use a different account
            </button>
          ) : (
            <div className="mt-5 flex items-center justify-between text-sm">
              {isSignIn ? (
                <>
                  <Link className="text-[var(--muted)] hover:text-[var(--foreground)]" href="/forgot-password">Forgot password?</Link>
                  <Link className="font-medium text-[var(--primary-strong)]" href="/sign-up">Create account</Link>
                </>
              ) : (
                <>
                  <span className="text-[var(--muted)]">Already registered?</span>
                  <Link className="font-medium text-[var(--primary-strong)]" href="/sign-in">Sign in</Link>
                </>
              )}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
