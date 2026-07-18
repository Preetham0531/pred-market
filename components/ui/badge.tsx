import { cn } from "@/lib/utils";

type BadgeProps = {
  children: React.ReactNode;
  tone?: "neutral" | "green" | "blue" | "brass" | "red";
  className?: string;
};

const tones = {
  neutral: "border-[var(--border)] bg-[var(--surface-muted)] text-[var(--muted)]",
  green: "border-[var(--green-border)] bg-[var(--green-soft)] text-[var(--green-text)]",
  blue: "border-[var(--blue-border)] bg-[var(--blue-soft)] text-[var(--blue-text)]",
  brass: "border-[var(--brass-border)] bg-[var(--brass-soft)] text-[var(--brass-text)]",
  red: "border-[var(--red-border)] bg-[var(--red-soft)] text-[var(--red-text)]"
};

export function Badge({ children, tone = "neutral", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex h-6 items-center rounded-md border px-2 text-xs font-medium",
        tones[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
