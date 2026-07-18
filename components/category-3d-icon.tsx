import { Activity, Banknote, CloudSun, Cpu, Landmark, LineChart, Megaphone, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Category } from "@/lib/mock-data";

type CategoryIconProps = {
  category: Pick<Category, "slug" | "iconTone" | "shortName">;
  size?: "sm" | "md" | "lg";
  className?: string;
};

const icons = {
  sports: Trophy,
  politics: Landmark,
  economics: LineChart,
  "stocks-mutual-funds": Activity,
  financials: Banknote,
  "weather-climate": CloudSun,
  culture: Megaphone,
  "tech-science": Cpu,
  mentions: Megaphone,
  commodities: Banknote
};

const toneClass = {
  green: "bg-[color-mix(in_srgb,var(--green-soft)_72%,transparent)] text-[var(--green-text)] ring-[color-mix(in_srgb,var(--green-border)_45%,transparent)]",
  blue: "bg-[color-mix(in_srgb,var(--blue-soft)_72%,transparent)] text-[var(--blue-text)] ring-[color-mix(in_srgb,var(--blue-border)_45%,transparent)]",
  brass: "bg-[color-mix(in_srgb,var(--brass-soft)_76%,transparent)] text-[var(--brass-text)] ring-[color-mix(in_srgb,var(--brass-border)_45%,transparent)]",
  red: "bg-[color-mix(in_srgb,var(--red-soft)_72%,transparent)] text-[var(--red-text)] ring-[color-mix(in_srgb,var(--red-border)_45%,transparent)]",
  violet: "bg-[color-mix(in_srgb,var(--primary-soft)_72%,transparent)] text-[var(--primary-strong)] ring-[color-mix(in_srgb,var(--primary-border)_45%,transparent)]",
  aqua: "bg-[color-mix(in_srgb,var(--primary-soft)_72%,transparent)] text-[var(--primary-strong)] ring-[color-mix(in_srgb,var(--primary-border)_45%,transparent)]"
};

const sizes = {
  sm: "h-7 w-7",
  md: "h-9 w-9",
  lg: "h-11 w-11"
};

const iconSizes = {
  sm: "h-3.5 w-3.5",
  md: "h-4 w-4",
  lg: "h-5 w-5"
};

export function CategoryIcon({ category, size = "md", className }: CategoryIconProps) {
  const Icon = icons[category.slug as keyof typeof icons] ?? Activity;

  return (
    <div
      className={cn(
        "grid shrink-0 place-items-center rounded-full ring-1 transition-colors duration-150",
        toneClass[category.iconTone],
        sizes[size],
        className
      )}
      aria-hidden="true"
    >
      <Icon className={iconSizes[size]} strokeWidth={2.2} />
    </div>
  );
}

export const Category3DIcon = CategoryIcon;
