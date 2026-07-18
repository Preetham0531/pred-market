import { Badge } from "@/components/ui/badge";

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const tone =
    status === "Open"
      ? "neutral"
      : status === "Closing soon"
        ? "brass"
        : status === "Pending resolution"
          ? "blue"
          : "neutral";

  return <Badge tone={tone}>{status}</Badge>;
}
