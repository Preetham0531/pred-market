"use client";

import { useState } from "react";
import { CheckCircle2, Copy, Download, KeyRound, Loader2, RefreshCw, ShieldCheck, Smartphone } from "lucide-react";
import { QRCodeSVG } from "qrcode.react";
import { useAuth } from "@/components/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiRequest, USE_MOCK_DATA } from "@/lib/api-client";

type TotpSetup = {
  factor_id: string;
  secret: string;
  otpauth_uri: string;
  issuer: string;
  account_name: string;
};

export default function AccountSecurityPage() {
  const { user, loading, refresh } = useAuth();
  const [setup, setSetup] = useState<TotpSetup | null>(null);
  const [code, setCode] = useState("");
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function beginSetup() {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      if (USE_MOCK_DATA) {
        setSetup({ factor_id: "mock", secret: "JBSWY3DPEHPK3PXP", otpauth_uri: "otpauth://totp/Pred-Market:demo?secret=JBSWY3DPEHPK3PXP&issuer=Pred-Market", issuer: "Pred-Market", account_name: user?.email || "demo" });
      } else {
        setSetup(await apiRequest<TotpSetup>("/api/v1/auth/mfa/totp/setup", { method: "POST" }));
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Authenticator setup could not start.");
    } finally {
      setBusy(false);
    }
  }

  async function confirmSetup(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = USE_MOCK_DATA
        ? { recovery_codes: ["PM-DEMO-0001", "PM-DEMO-0002"] }
        : await apiRequest<{ recovery_codes: string[] }>("/api/v1/auth/mfa/totp/confirm", {
            method: "POST",
            body: JSON.stringify({ code })
          });
      setRecoveryCodes(payload.recovery_codes);
      setSetup(null);
      setCode("");
      setMessage("Authenticator MFA is active for this account.");
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The authenticator code could not be confirmed.");
    } finally {
      setBusy(false);
    }
  }

  async function regenerateCodes(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = await apiRequest<{ recovery_codes: string[] }>("/api/v1/auth/mfa/recovery-codes/regenerate", {
        method: "POST",
        body: JSON.stringify({ code })
      });
      setRecoveryCodes(payload.recovery_codes);
      setCode("");
      setMessage("Previous recovery codes were revoked.");
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Recovery codes could not be regenerated.");
    } finally {
      setBusy(false);
    }
  }

  function downloadRecoveryCodes() {
    const content = ["Pred-Market recovery codes", "Store these offline. Each code can be used once.", "", ...recoveryCodes].join("\n");
    const url = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "pred-market-recovery-codes.txt";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  if (loading || !user) {
    return <div className="exchange-panel rounded-md p-4 text-sm text-[var(--muted)]">Checking security status...</div>;
  }

  const mfa = user.mfa;

  return (
    <div className="mx-auto max-w-5xl space-y-7">
      <header className="flex flex-wrap items-start justify-between gap-4 border-b border-[var(--border)]/60 pb-5">
        <div>
          <h1 className="text-2xl font-semibold text-balance">Account security</h1>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-[var(--muted)]">
            Protect access to orders, wallet data, and administrative actions with a rotating session and an authenticator app.
          </p>
        </div>
        <Badge tone={mfa.verifiedForSession ? "green" : mfa.required ? "brass" : "blue"}>
          {mfa.verifiedForSession ? "MFA verified" : mfa.required ? "Setup required" : "Standard session"}
        </Badge>
      </header>

      {mfa.required && !mfa.enrolled ? (
        <div className="rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] px-4 py-3 text-sm text-[var(--brass-text)]" role="status">
          Admin access remains locked until authenticator MFA is configured. You can still sign out or complete setup here.
        </div>
      ) : null}

      {message ? <div className="rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] px-4 py-3 text-sm text-[var(--green-text)]" role="status">{message}</div> : null}
      {error ? <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-4 py-3 text-sm text-[var(--red-text)]" role="alert">{error}</div> : null}

      <section className="grid gap-0 overflow-hidden rounded-md border border-[var(--border)] md:grid-cols-3">
        {[
          ["Password", "Argon2id", ShieldCheck],
          ["Session", "JWT + rotating refresh", KeyRound],
          ["Authenticator", mfa.enrolled ? "Configured" : "Not configured", Smartphone]
        ].map(([label, value, Icon], index) => {
          const SecurityIcon = Icon as typeof ShieldCheck;
          return (
            <div key={String(label)} className={`bg-[var(--surface)] p-4 ${index ? "border-t border-[var(--border)] md:border-l md:border-t-0" : ""}`}>
              <SecurityIcon className="h-5 w-5 text-[var(--primary-strong)]" aria-hidden="true" />
              <div className="mt-4 text-sm font-semibold">{String(label)}</div>
              <div className="mt-1 text-sm text-[var(--muted)]">{String(value)}</div>
            </div>
          );
        })}
      </section>

      {!mfa.enrolled && !setup ? (
        <section className="border-b border-[var(--border)] pb-7">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold">Authenticator app</h2>
              <p className="mt-1 max-w-2xl text-sm leading-6 text-[var(--muted)]">Use a time-based code from your phone when signing in. Admin accounts must complete this step.</p>
            </div>
            <Button variant="primary" onClick={beginSetup} disabled={busy}>
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Smartphone className="h-4 w-4" />}
              Set up authenticator
            </Button>
          </div>
        </section>
      ) : null}

      {setup ? (
        <section className="grid gap-6 border-b border-[var(--border)] pb-7 md:grid-cols-[220px_1fr]">
          <div className="grid place-items-center rounded-md bg-white p-4">
            <QRCodeSVG value={setup.otpauth_uri} size={184} level="M" title="Pred-Market authenticator QR code" />
          </div>
          <div>
            <h2 className="text-base font-semibold">Connect your authenticator</h2>
            <ol className="mt-3 space-y-2 text-sm leading-6 text-[var(--muted)]">
              <li>1. Open your authenticator app and add a new account.</li>
              <li>2. Scan the QR code. If scanning fails, enter the setup key manually.</li>
              <li>3. Enter the current six-digit code below.</li>
            </ol>
            <div className="mt-4 flex items-center gap-2 rounded-md bg-[var(--surface-muted)] px-3 py-2">
              <code className="min-w-0 flex-1 break-all text-xs text-[var(--foreground)]">{setup.secret}</code>
              <Button size="icon" variant="ghost" aria-label="Copy authenticator setup key" onClick={() => navigator.clipboard.writeText(setup.secret)}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <form className="mt-4 flex max-w-md gap-2" onSubmit={confirmSetup}>
              <Input value={code} onChange={(event) => setCode(event.target.value)} inputMode="numeric" autoComplete="one-time-code" placeholder="Six-digit code" minLength={6} maxLength={6} required />
              <Button variant="primary" type="submit" disabled={busy}>Confirm</Button>
            </form>
          </div>
        </section>
      ) : null}

      {mfa.enrolled && recoveryCodes.length === 0 ? (
        <section className="flex flex-wrap items-start justify-between gap-5 border-b border-[var(--border)] pb-7">
          <div>
            <h2 className="text-base font-semibold">Recovery codes</h2>
            <p className="mt-1 max-w-2xl text-sm leading-6 text-[var(--muted)]">{mfa.recoveryCodesRemaining} unused codes remain. Regenerating revokes every previous code.</p>
          </div>
          <form className="flex w-full max-w-md gap-2" onSubmit={regenerateCodes}>
            <Input value={code} onChange={(event) => setCode(event.target.value)} inputMode="numeric" autoComplete="one-time-code" placeholder="Current authenticator code" minLength={6} maxLength={6} required />
            <Button type="submit" disabled={busy}><RefreshCw className="h-4 w-4" />Regenerate</Button>
          </form>
        </section>
      ) : null}

      {recoveryCodes.length ? (
        <section className="rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-sm font-semibold text-[var(--brass-text)]"><CheckCircle2 className="h-4 w-4" />Store these codes now</div>
              <p className="mt-1 text-sm text-[var(--brass-text)]/85">They are displayed once. Each code replaces one authenticator challenge.</p>
            </div>
            <Button onClick={downloadRecoveryCodes}><Download className="h-4 w-4" />Download</Button>
          </div>
          <div className="mt-5 grid gap-2 sm:grid-cols-2">
            {recoveryCodes.map((recoveryCode) => <code key={recoveryCode} className="rounded bg-black/20 px-3 py-2 text-sm text-[var(--foreground)]">{recoveryCode}</code>)}
          </div>
        </section>
      ) : null}
    </div>
  );
}
