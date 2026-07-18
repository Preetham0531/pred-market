"use client";

import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <section className="mx-auto grid max-w-xl place-items-center rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] p-8 text-center">
      <AlertTriangle className="h-10 w-10 text-[var(--red-text)]" />
      <h1 className="mt-4 text-2xl font-semibold text-[var(--red-text)]">Something failed</h1>
      <p className="mt-2 text-sm leading-6 text-[var(--red-text)]">
        The workspace could not load this view. Retry once; if it repeats, check the API and session state.
      </p>
      <Button className="mt-5" variant="danger" onClick={reset}>
        Retry
      </Button>
    </section>
  );
}
