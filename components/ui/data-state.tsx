import { AlertTriangle, Database, Loader2, RefreshCw, SearchX } from "lucide-react";
import Link from "next/link";
import { Button, buttonVariants } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type DataStateProps = {
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  actionHref?: string;
  tone?: "loading" | "empty" | "error" | "warning";
  badge?: string;
  className?: string;
};

export function DataState({ title, message, actionLabel, onAction, actionHref, tone = "empty", badge, className }: DataStateProps) {
  const Icon = tone === "loading" ? Loader2 : tone === "empty" ? SearchX : AlertTriangle;
  const iconClass =
    tone === "error"
      ? "bg-[var(--red-soft)] text-[var(--red-text)]"
      : tone === "warning"
        ? "bg-[var(--brass-soft)] text-[var(--brass-text)]"
        : tone === "loading"
          ? "bg-[var(--blue-soft)] text-[var(--blue-text)]"
          : "bg-[var(--surface-muted)] text-[var(--muted)]";

  return (
    <div className={cn("exchange-panel rounded-md p-5", className)} role={tone === "error" ? "alert" : "status"}>
      <div className="flex items-start gap-3">
        <div className={cn("grid h-10 w-10 shrink-0 place-items-center rounded-md", iconClass)}>
          <Icon className={cn("h-5 w-5", tone === "loading" && "animate-spin")} aria-hidden="true" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold">{title}</h2>
            {badge ? <Badge tone={tone === "error" ? "red" : tone === "warning" ? "brass" : "blue"}>{badge}</Badge> : null}
          </div>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-[var(--muted)]">{message}</p>
          {actionLabel && onAction ? (
            <Button className="mt-4" type="button" variant={tone === "error" ? "primary" : "secondary"} onClick={onAction}>
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
              {actionLabel}
            </Button>
          ) : null}
          {actionLabel && actionHref ? (
            <Link className={cn(buttonVariants({ variant: tone === "error" ? "primary" : "secondary" }), "mt-4")} href={actionHref}>
              {actionLabel}
            </Link>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export function DataSkeleton({ rows = 4, className }: { rows?: number; className?: string }) {
  return (
    <div className={cn("exchange-panel rounded-md p-4", className)} aria-busy="true">
      <div className="space-y-3">
        <div className="exchange-skeleton h-5 w-40 rounded" />
        <div className="exchange-skeleton h-9 w-full rounded" />
        {Array.from({ length: rows }, (_, index) => (
          <div key={index} className="grid gap-2 md:grid-cols-[1fr_110px_90px_90px]">
            <div className="exchange-skeleton h-10 rounded" />
            <div className="exchange-skeleton h-10 rounded" />
            <div className="exchange-skeleton h-10 rounded" />
            <div className="exchange-skeleton h-10 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ApiModeHint({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] px-3 py-2 text-xs leading-5 text-[var(--brass-text)]", className)}>
      <span className="inline-flex items-center gap-1 font-medium">
        <Database className="h-3.5 w-3.5" aria-hidden="true" />
        Local QA note:
      </span>{" "}
      use `NEXT_PUBLIC_USE_MOCK_DATA=true` for populated visual review, or start the seeded FastAPI backend for integration review.
    </div>
  );
}
