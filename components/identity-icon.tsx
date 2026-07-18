import { cn } from "@/lib/utils";
import type { MarketIdentity } from "@/lib/market-identities";

type IdentityIconProps = {
  identity: MarketIdentity;
  size?: "sm" | "md" | "lg";
  className?: string;
};

const sizeClass = {
  sm: "h-7 w-7",
  md: "h-9 w-9",
  lg: "h-11 w-11"
};

export function IdentityIcon({ identity, size = "md", className }: IdentityIconProps) {
  return (
    <span
      className={cn(
        "inline-grid shrink-0 place-items-center overflow-hidden rounded-full bg-[var(--surface-muted)] ring-1 ring-[color-mix(in_srgb,var(--border)_72%,transparent)]",
        sizeClass[size],
        className
      )}
      title={identity.label}
      aria-label={identity.label}
    >
      {identity.src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={identity.src} alt="" className={cn("h-full w-full object-cover", identity.kind === "flag" ? "" : "p-0.5")} />
      ) : (
        <span className="text-xs font-semibold text-[var(--muted)]">{identity.label.slice(0, 2).toUpperCase()}</span>
      )}
    </span>
  );
}
