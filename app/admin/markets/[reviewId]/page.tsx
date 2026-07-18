"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { CheckCircle2, FileSearch, ShieldAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { useAdminMarketAction, useAdminReview } from "@/lib/api-hooks";
import { cn } from "@/lib/utils";

export default function AdminMarketReviewPage() {
  const params = useParams<{ reviewId: string }>();
  const { data: review, isLoading } = useAdminReview(params.reviewId);
  const approveMarket = useAdminMarketAction("approve");
  const pauseMarket = useAdminMarketAction("pause");
  const marketActionDisabled = !review?.marketId || approveMarket.isPending || pauseMarket.isPending;

  if (isLoading) {
    return <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-6 text-sm text-[var(--muted)]">Loading review...</div>;
  }

  if (!review) {
    return <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] p-6 text-sm text-[var(--red-text)]">Review could not be loaded.</div>;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="mb-2 flex flex-wrap gap-2">
            <Badge tone={review.risk === "LOW" ? "green" : review.risk === "MEDIUM" ? "blue" : "red"}>{review.risk}</Badge>
            <Badge>{review.status}</Badge>
          </div>
          <h1 className="text-2xl font-semibold">{review.title}</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">Submitted by {review.submittedBy} / {review.category}</p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            Review {review.id} / {review.draftId ? `Draft ${review.draftId}` : review.marketId ? `Market ${review.marketId}` : "No market linked yet"} / Created {new Date(review.createdAt).toLocaleString()}
          </p>
        </div>
        <Link className={cn(buttonVariants({ variant: "secondary", size: "md" }), "w-fit")} href="/admin">
          Back to queue
        </Link>
      </div>

      <section className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-3">
          <h2 className="text-sm font-semibold">Review checklist</h2>
          <div className="mt-3 space-y-2">
            {[
              ["Duplicate detection", "No exact duplicate found.", CheckCircle2, "green"],
              ["Approved source", "Source needs admin confirmation before listing.", FileSearch, "blue"],
              ["Restricted topic", review.risk === "RESTRICTED" ? "Requires senior compliance sign-off." : "No restricted trigger found.", ShieldAlert, review.risk === "RESTRICTED" ? "red" : "green"],
              ["Resolution clarity", "Question needs final wording approval.", FileSearch, "blue"]
            ].map(([title, detail, Icon, tone]) => (
              <div key={title as string} className="flex gap-3 rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3 text-sm">
                <Icon className={tone === "red" ? "mt-0.5 h-4 w-4 text-[var(--red-text)]" : tone === "green" ? "mt-0.5 h-4 w-4 text-[var(--green-text)]" : "mt-0.5 h-4 w-4 text-[var(--blue-text)]"} />
                <div>
                  <div className="font-medium">{title as string}</div>
                  <div className="mt-1 text-xs leading-5 text-[var(--muted)]">{detail as string}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-3">
          <h2 className="text-sm font-semibold">Maker-checker actions</h2>
          <div className="mt-3 space-y-2">
            {review.draftId ? (
              <Link className={cn(buttonVariants({ variant: "primary", size: "md" }), "w-full")} href="/admin/markets/issue">
                Open issuing workspace
              </Link>
            ) : null}
            <Button
              className="w-full"
              disabled={marketActionDisabled || Boolean(review.draftId)}
              onClick={() => review.marketId && approveMarket.mutate(review.marketId)}
            >
              {approveMarket.isPending ? "Approving..." : "Approve market"}
            </Button>
            <Button
              className="w-full"
              variant="secondary"
              disabled={marketActionDisabled || Boolean(review.draftId)}
              onClick={() => review.marketId && pauseMarket.mutate(review.marketId)}
            >
              {pauseMarket.isPending ? "Pausing..." : "Pause market"}
            </Button>
            <button className={cn(buttonVariants({ variant: "danger", size: "md" }), "w-full")} disabled>Reject unavailable in V1</button>
          </div>
          <p className="mt-3 text-xs leading-5 text-[var(--muted)]">
            {review.marketId
              ? "Approve and pause actions call FastAPI, write audit logs, and update realtime admin status."
              : review.draftId
              ? "This review is linked to a market draft. Use the issuing workspace to inspect checks, approve, reject, or list the market."
              : "This review was created from a suggestion and has no linked market yet, so market status actions are disabled."}
          </p>
          {approveMarket.error || pauseMarket.error ? (
            <p className="mt-2 rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-xs text-[var(--red-text)]">
              Admin action failed. Confirm the backend session is signed in as an admin.
            </p>
          ) : null}
        </aside>
      </section>
    </div>
  );
}
