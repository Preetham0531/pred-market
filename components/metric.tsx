import { cn } from "@/lib/utils";

type MetricProps = {
  label: string;
  value: string;
  detail?: string;
  tone?: "neutral" | "green" | "red" | "blue";
  className?: string;
};

const toneClasses = {
  neutral: "text-[var(--foreground)]",
  green: "text-[var(--green-text)]",
  red: "text-[var(--red-text)]",
  blue: "text-[var(--blue-text)]"
};

export function Metric({ label, value, detail, tone = "neutral", className }: MetricProps) {
  return (
    <div className={cn("exchange-panel rounded-md p-3", className)}>
      <div className="text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--muted)]">{label}</div>
      <div className={cn("numeric mt-1 text-xl font-semibold leading-none", toneClasses[tone])}>{value}</div>
      {detail ? <div className="mt-1 text-xs text-[var(--muted)]">{detail}</div> : null}
    </div>
  );
}
