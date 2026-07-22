"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  Landmark,
  Loader2,
  LockKeyhole,
  ShieldCheck,
  Sparkles,
  WalletCards
} from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type AuthPanelProps = {
  mode: "sign-in" | "sign-up";
};

const trustSignals = [
  { label: "HttpOnly sessions", icon: ShieldCheck },
  { label: "Role-aware routing", icon: Landmark },
  { label: "Ledger first design", icon: WalletCards }
];

export function AuthPanel({ mode }: AuthPanelProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const requestedNext = searchParams.get("next");
  const next = useMemo(() => {
    if (!requestedNext || !requestedNext.startsWith("/") || requestedNext.startsWith("/sign-")) return "/markets";
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

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      if (mfaRequired) {
        await verifyMfa(mfaCode);
      } else if (mode === "sign-in") {
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

  const isSignIn = mode === "sign-in";

  useEffect(() => {
    if (loading || !user || submitting) return;
    if (user.mfa.required && !user.mfa.enrolled) {
      router.replace("/account/security");
      return;
    }
    router.replace(user.roles.includes("ADMIN") && next === "/markets" ? "/admin" : next);
  }, [loading, next, router, submitting, user]);

  return (
    <section className="min-h-dvh bg-[var(--background)] text-[var(--foreground)]">

      <div className="relative mx-auto grid min-h-dvh w-full max-w-7xl items-center gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[1.05fr_440px] lg:px-8">
        <div className="hidden min-w-0 lg:block">
          <Link href="/markets" className="mb-8 inline-flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-md border border-[var(--border-strong)] bg-[var(--primary-soft)] text-sm font-bold text-[var(--primary-strong)]">
              PM
            </div>
            <div>
              <div className="text-sm font-semibold">Pred-Market</div>
              <div className="text-xs text-[var(--muted)]">Exchange terminal</div>
            </div>
          </Link>

          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-sm font-medium text-[var(--blue-text)]">
            <Sparkles className="h-4 w-4" />
            Fully collateralized prediction exchange
          </div>

          <h1 className="max-w-3xl text-4xl font-semibold leading-[1.02] sm:text-5xl lg:text-6xl">
            Enter the market with signal, speed, and control.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)]">
            Manage positions, submit limit orders, review ledger movement, and route market suggestions through admin review from one trading workspace.
          </p>

          <div className="mt-7 grid max-w-2xl gap-3 sm:grid-cols-3">
            {trustSignals.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="border-t border-[color-mix(in_srgb,var(--border)_58%,transparent)] px-1 py-3">
                  <Icon className="h-4 w-4 text-[var(--blue-text)]" />
                  <div className="mt-2 text-sm font-semibold">{item.label}</div>
                </div>
              );
            })}
          </div>

          <div className="mt-8 max-w-2xl border-l-2 border-[var(--border-strong)] pl-4">
            <div className="text-sm font-semibold">Built for controlled market operations</div>
            <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
              Access opens the trading workspace, wallet ledger, admin review queue, and market suggestion tools. Live market data stays inside the authenticated product.
            </p>
          </div>
        </div>

        <div className="relative">
          <Link href="/" className="mb-6 flex items-center gap-3 lg:hidden">
            <div className="grid h-10 w-10 place-items-center rounded-md border border-[var(--border-strong)] bg-[var(--primary-soft)] text-sm font-bold text-[var(--primary-strong)]">
              PM
            </div>
            <div>
              <div className="text-sm font-semibold">Pred-Market</div>
              <div className="text-xs text-[var(--muted)]">Secure account access</div>
            </div>
          </Link>
          <div className="relative rounded-lg border border-[var(--border)] bg-[var(--surface-raised)] p-5 shadow-[0_24px_70px_rgba(0,0,0,0.28)] md:p-6">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <div className="grid h-11 w-11 place-items-center rounded-md bg-[var(--primary-soft)] text-[var(--primary-strong)]">
                  <LockKeyhole className="h-5 w-5" />
                </div>
                <h2 className="mt-4 text-2xl font-semibold">
                  {mfaRequired ? "Verify your sign-in" : isSignIn ? "Welcome back" : "Create your account"}
                </h2>
                <p className="mt-1 text-sm leading-6 text-[var(--muted)]">
                  {mfaRequired
                    ? "Enter the current code from your authenticator app, or use one recovery code."
                    : isSignIn
                      ? "Use your Pred-Market account to continue."
                      : "Create a V1 account for simulated trading."}
                </p>
              </div>
              <div className="rounded-full border border-[var(--border)] bg-[var(--surface-muted)] px-2.5 py-1 text-xs font-medium text-[var(--blue-text)]">
                Secure
              </div>
            </div>

            <form className="space-y-4" onSubmit={submit}>
          {!mfaRequired && mode === "sign-up" ? (
            <label className="block">
              <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Display name</span>
              <Input
                className="h-11"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                autoComplete="name"
                required
                minLength={2}
                maxLength={80}
              />
            </label>
          ) : null}
          {!mfaRequired ? <label className="block">
            <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Email</span>
            <Input
              className="h-11"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              autoComplete={mode === "sign-in" ? "username" : "email"}
              required
            />
          </label> : null}
          {!mfaRequired ? <label className="block">
            <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Password</span>
            <Input
              className="h-11"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              autoComplete={mode === "sign-in" ? "current-password" : "new-password"}
              required
              minLength={mode === "sign-up" ? 12 : 1}
            />
          </label> : null}

          {mfaRequired ? (
            <label className="block">
              <span className="mb-1.5 block text-xs font-medium text-[var(--muted)]">Authenticator or recovery code</span>
              <Input
                className="h-11 font-mono"
                value={mfaCode}
                onChange={(event) => setMfaCode(event.target.value)}
                inputMode="text"
                autoComplete="one-time-code"
                placeholder="000000"
                required
                minLength={6}
                maxLength={32}
                autoFocus
              />
            </label>
          ) : null}

          {error ? (
            <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red-text)]" role="alert">
              {error}
            </div>
          ) : null}

          <Button className="h-11 w-full" variant="primary" type="submit" disabled={submitting}>
            {submitting ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : null}
            {submitting ? "Working" : mfaRequired ? "Verify and continue" : isSignIn ? "Sign in" : "Create account"}
            {!submitting ? <ArrowRight className="h-4 w-4" aria-hidden="true" /> : null}
          </Button>
        </form>

            {mfaRequired ? (
              <button
                type="button"
                className="mt-3 text-sm text-[var(--muted)] transition hover:text-[var(--foreground)]"
                onClick={() => {
                  setMfaRequired(false);
                  setMfaCode("");
                  setPassword("");
                  setError("");
                }}
              >
                Use a different account
              </button>
            ) : null}

            <div className="mt-5 rounded-md bg-[var(--surface-muted)] px-3 py-2 text-xs leading-5 text-[var(--muted)]">
              Roles are assigned by the backend account record after authentication. The login form never asks the user to choose trader or admin access.
            </div>

        {!mfaRequired ? <div className="mt-5 flex items-center justify-between text-sm">
          {mode === "sign-in" ? (
            <>
              <Link className="text-[var(--muted)] hover:text-[var(--foreground)]" href="/forgot-password">
                Forgot password?
              </Link>
              <Link className="font-medium text-[var(--primary-strong)]" href="/sign-up">
                Create account
              </Link>
            </>
          ) : (
            <>
              <span className="text-[var(--muted)]">Already have an account?</span>
              <Link className="font-medium text-[var(--primary-strong)]" href="/sign-in">
                Sign in
              </Link>
            </>
          )}
        </div> : null}
      </div>
        </div>
      </div>
    </section>
  );
}
