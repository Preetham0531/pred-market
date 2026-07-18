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
  const { user, loading, signIn, signUp } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      if (mode === "sign-in") {
        await signIn(email, password);
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
    router.replace(user.roles.includes("ADMIN") && next === "/markets" ? "/admin" : next);
  }, [loading, next, router, submitting, user]);

  return (
    <section className="relative min-h-dvh overflow-hidden bg-[#080d14] text-white">

      <div className="relative mx-auto grid min-h-dvh w-full max-w-7xl items-center gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[1.05fr_440px] lg:px-8">
        <div className="min-w-0">
          <Link href="/markets" className="mb-8 inline-flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-md border border-cyan-300/30 bg-cyan-300/15 text-sm font-bold text-cyan-100 shadow-lg shadow-sky-950/30">
              PM
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Pred-Market</div>
              <div className="text-xs text-slate-400">Exchange terminal</div>
            </div>
          </Link>

          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-sky-300/25 bg-sky-300/10 px-3 py-1.5 text-sm font-medium text-sky-100">
            <Sparkles className="h-4 w-4" />
            Fully collateralized prediction exchange
          </div>

          <h1 className="max-w-3xl text-4xl font-semibold leading-[1.02] text-white sm:text-5xl lg:text-6xl">
            Enter the market with signal, speed, and control.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            Manage positions, submit limit orders, review ledger movement, and route market suggestions through admin review from one trading workspace.
          </p>

          <div className="mt-7 grid max-w-2xl gap-3 sm:grid-cols-3">
            {trustSignals.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="rounded-lg border border-white/10 bg-white/[0.055] px-3 py-3 shadow-lg shadow-black/10 backdrop-blur">
                  <Icon className="h-4 w-4 text-sky-300" />
                  <div className="mt-2 text-sm font-semibold text-slate-100">{item.label}</div>
                </div>
              );
            })}
          </div>

          <div className="mt-8 max-w-2xl rounded-lg border border-white/10 bg-white/[0.035] p-4 shadow-lg shadow-black/10">
            <div className="text-sm font-semibold text-white">Built for controlled market operations</div>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Access opens the trading workspace, wallet ledger, admin review queue, and market suggestion tools. Live market data stays inside the authenticated product.
            </p>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-px rounded-xl bg-[linear-gradient(135deg,rgba(56,189,248,0.72),rgba(129,140,248,0.56),rgba(232,121,249,0.46))] opacity-80" />
          <div className="relative rounded-xl border border-white/14 bg-[#11171d]/96 p-5 shadow-2xl shadow-black/40 backdrop-blur md:p-6">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <div className="grid h-11 w-11 place-items-center rounded-md bg-emerald-400 text-[#062014] shadow-lg shadow-emerald-950/30">
                  <LockKeyhole className="h-5 w-5" />
                </div>
                <h2 className="mt-4 text-2xl font-semibold text-white">{isSignIn ? "Welcome back" : "Create your account"}</h2>
                <p className="mt-1 text-sm leading-6 text-slate-400">
                  {isSignIn ? "Use your Pred-Market account to continue." : "Create a V1 account for simulated trading."}
                </p>
              </div>
              <div className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-2.5 py-1 text-xs font-medium text-emerald-200">
                Secure
              </div>
            </div>

            <form className="space-y-4" onSubmit={submit}>
          {mode === "sign-up" ? (
            <label className="block">
              <span className="mb-1.5 block text-xs font-medium text-slate-300">Display name</span>
              <Input
                className="h-11 border-white/12 bg-white/[0.055] text-white placeholder:text-slate-500 focus:border-emerald-300 focus:ring-emerald-300/20"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                autoComplete="name"
                required
                minLength={2}
                maxLength={80}
              />
            </label>
          ) : null}
          <label className="block">
            <span className="mb-1.5 block text-xs font-medium text-slate-300">Email</span>
            <Input
              className="h-11 border-white/12 bg-white/[0.055] text-white placeholder:text-slate-500 focus:border-emerald-300 focus:ring-emerald-300/20"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              autoComplete={mode === "sign-in" ? "username" : "email"}
              required
            />
          </label>
          <label className="block">
            <span className="mb-1.5 block text-xs font-medium text-slate-300">Password</span>
            <Input
              className="h-11 border-white/12 bg-white/[0.055] text-white placeholder:text-slate-500 focus:border-emerald-300 focus:ring-emerald-300/20"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              autoComplete={mode === "sign-in" ? "current-password" : "new-password"}
              required
              minLength={8}
            />
          </label>

          {error ? (
            <div className="rounded-md border border-red-400/30 bg-red-400/10 px-3 py-2 text-sm text-red-200" role="alert">
              {error}
            </div>
          ) : null}

          <Button className="h-11 w-full border-emerald-300 bg-emerald-400 text-[#061710] hover:bg-emerald-300" variant="primary" type="submit" disabled={submitting}>
            {submitting ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : null}
            {submitting ? "Working" : isSignIn ? "Sign in" : "Create account"}
            {!submitting ? <ArrowRight className="h-4 w-4" aria-hidden="true" /> : null}
          </Button>
        </form>

            <div className="mt-5 rounded-md bg-white/[0.035] px-3 py-2 text-xs leading-5 text-slate-400">
              Roles are assigned by the backend account record after authentication. The login form never asks the user to choose trader or admin access.
            </div>

        <div className="mt-5 flex items-center justify-between text-sm">
          {mode === "sign-in" ? (
            <>
              <Link className="text-slate-400 hover:text-white" href="/forgot-password">
                Forgot password?
              </Link>
              <Link className="font-medium text-emerald-300 hover:text-emerald-200" href="/sign-up">
                Create account
              </Link>
            </>
          ) : (
            <>
              <span className="text-slate-400">Already have an account?</span>
              <Link className="font-medium text-emerald-300 hover:text-emerald-200" href="/sign-in">
                Sign in
              </Link>
            </>
          )}
        </div>
      </div>
        </div>
      </div>
    </section>
  );
}
