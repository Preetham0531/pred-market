"use client";

import Link from "next/link";
import { CheckCircle2, FileSearch, Plus, ShieldAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { useAdminReviews } from "@/lib/api-hooks";

export default function AdminPage() {
  const { data: adminQueue = [], isLoading, error } = useAdminReviews();

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Admin review</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">Market approval, resolution evidence, automation exceptions, and risk queue.</p>
        </div>
        <Link className={buttonVariants({ variant: "primary", size: "md" })} href="/admin/markets/issue">
          <Plus className="h-4 w-4" />
          Issue markets
        </Link>
      </div>
      {error ? (
        <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red-text)]">
          Admin queue could not be loaded. Admin access is required.
        </div>
      ) : null}
      <section className="grid gap-5 2xl:grid-cols-[1fr_340px]">
        <div className="exchange-panel overflow-x-auto rounded-md">
          <div className="border-b border-[var(--border)] px-3 py-2 text-sm font-semibold">Review queue</div>
          <div className="exchange-table-header hidden min-w-[980px] grid-cols-[90px_minmax(280px,1fr)_150px_110px_120px_120px_96px] px-3 py-2 lg:grid">
            <span>ID</span>
            <span>Market</span>
            <span>Category</span>
            <span>Risk</span>
            <span>Evidence</span>
            <span>Automation</span>
            <span>Action</span>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {isLoading ? (
              <div className="px-3 py-6 text-sm text-[var(--muted)]">Loading review queue...</div>
            ) : adminQueue.length ? adminQueue.map((item) => (
              <div key={item.id} className="grid min-h-[62px] gap-3 px-3 py-3 text-sm lg:min-w-[980px] lg:grid-cols-[90px_minmax(280px,1fr)_150px_110px_120px_120px_96px] lg:items-center">
                <div className="font-mono text-xs text-[var(--muted)]">{item.id}</div>
                <div>
                  <div className="font-medium">{item.title}</div>
                  <div className="mt-1 text-xs text-[var(--muted)]">
                    Submitted by {item.submittedBy} / {item.draftId ? `Draft ${item.draftId}` : "maker-checker required"}
                  </div>
                </div>
                <div>{item.category}</div>
                <Badge tone={item.risk === "LOW" ? "green" : item.risk === "MEDIUM" ? "blue" : "red"}>{item.risk}</Badge>
                <Badge tone={item.status.includes("Source") ? "brass" : "blue"}>{item.status.includes("Source") ? "Needs source" : "Attached"}</Badge>
                <Badge tone={item.risk === "RESTRICTED" ? "red" : "green"}>{item.risk === "RESTRICTED" ? "Blocked" : "Passed"}</Badge>
                <Link className={buttonVariants({ variant: "secondary", size: "sm" })} href={`/admin/markets/${item.id}`}>
                  Review
                </Link>
              </div>
            )) : (
              <div className="px-3 py-6 text-sm text-[var(--muted)]">No reviews pending.</div>
            )}
          </div>
        </div>

        <aside className="exchange-panel rounded-md p-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Automation checks</h2>
            <Badge tone="blue">V1 deterministic</Badge>
          </div>
          <div className="mt-3 space-y-2">
            {[
              { label: "Duplicate detection", icon: CheckCircle2, tone: "green" },
              { label: "Source availability", icon: CheckCircle2, tone: "green" },
              { label: "Restricted category", icon: ShieldAlert, tone: "red" },
              { label: "Evidence capture", icon: FileSearch, tone: "blue" }
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="flex items-center justify-between rounded-md border border-[var(--border)] px-3 py-2 text-sm">
                  <span className="flex items-center gap-2">
                    <Icon className={item.tone === "green" ? "h-4 w-4 text-[var(--green-text)]" : item.tone === "red" ? "h-4 w-4 text-[var(--red-text)]" : "h-4 w-4 text-[var(--blue-text)]"} />
                    {item.label}
                  </span>
                  <span className="text-xs text-[var(--muted)]">Active</span>
                </div>
              );
            })}
          </div>
        </aside>
      </section>
    </div>
  );
}
