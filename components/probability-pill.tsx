import { cn } from "@/lib/utils";

type ProbabilityPillProps = {
  label: string;
  probability: number;
  price?: number;
  compact?: boolean;
  className?: string;
};

function toneFor(label: string) {
  const normalized = label.toUpperCase();
  if (normalized === "YES") return "border-[color-mix(in_srgb,var(--green-border)_60%,transparent)] bg-[color-mix(in_srgb,var(--green-soft)_78%,transparent)] text-[var(--green-text)]";
  if (normalized === "NO") return "border-[color-mix(in_srgb,var(--red-border)_58%,transparent)] bg-[color-mix(in_srgb,var(--red-soft)_78%,transparent)] text-[var(--red-text)]";
  return "border-[color-mix(in_srgb,var(--border)_72%,transparent)] bg-[var(--surface-muted)]/64 text-[var(--primary-strong)]";
}

export function ProbabilityPill({ label, probability, price, compact = false, className }: ProbabilityPillProps) {
  return (
    <span
      className={cn(
        "numeric inline-flex items-center justify-center gap-2 rounded-full border font-semibold leading-none",
        compact ? "h-8 min-w-16 px-3 text-xs" : "h-10 min-w-20 px-4 text-sm",
        toneFor(label),
        className
      )}
    >
      <span>{label}</span>
      <span>{price ?? probability}%</span>
    </span>
  );
}
