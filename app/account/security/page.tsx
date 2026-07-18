import { ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function AccountSecurityPage() {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Account security</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Session, verification, and admin security controls for the signed-in account.</p>
      </div>

      <section className="grid gap-3 md:grid-cols-3">
        {[
          ["Email verification", "Verified", "green"],
          ["Session storage", "HttpOnly cookie", "blue"],
          ["Admin MFA", "Required for admin", "brass"]
        ].map(([label, value, tone]) => (
          <div key={label} className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-3">
            <ShieldCheck className="h-5 w-5 text-[var(--primary)]" />
            <div className="mt-3 text-sm font-semibold">{label}</div>
            <Badge className="mt-2" tone={tone as "green" | "blue" | "brass"}>{value}</Badge>
          </div>
        ))}
      </section>

      <section className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-3">
        <h2 className="text-sm font-semibold">Production auth requirements</h2>
        <div className="mt-3 grid gap-2 text-sm text-[var(--muted)] md:grid-cols-2">
          <div className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3">Argon2id password hashing in FastAPI.</div>
          <div className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3">Refresh-token rotation with hashed tokens at rest.</div>
          <div className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3">CSRF protection for mutating browser requests.</div>
          <div className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3">Audit logs for admin and financial actions.</div>
        </div>
      </section>
    </div>
  );
}
