import Link from "next/link";
import { SearchX } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function NotFound() {
  return (
    <section className="mx-auto grid max-w-xl place-items-center rounded-md border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
      <SearchX className="h-10 w-10 text-[var(--muted)]" />
      <h1 className="mt-4 text-2xl font-semibold">Nothing found</h1>
      <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
        The market, category, or admin item may have moved, expired, or not been approved yet.
      </p>
      <Link className={cn(buttonVariants({ variant: "primary", size: "md" }), "mt-5")} href="/markets">
        Back to markets
      </Link>
    </section>
  );
}
