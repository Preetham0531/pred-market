export default function Loading() {
  return (
    <div className="space-y-4">
      <div className="h-8 w-56 animate-pulse rounded-md bg-[var(--surface-muted)]" />
      <div className="grid gap-3 md:grid-cols-3">
        <div className="h-24 animate-pulse rounded-md border border-[var(--border)] bg-[var(--surface)]" />
        <div className="h-24 animate-pulse rounded-md border border-[var(--border)] bg-[var(--surface)]" />
        <div className="h-24 animate-pulse rounded-md border border-[var(--border)] bg-[var(--surface)]" />
      </div>
      <div className="h-72 animate-pulse rounded-md border border-[var(--border)] bg-[var(--surface)]" />
    </div>
  );
}
