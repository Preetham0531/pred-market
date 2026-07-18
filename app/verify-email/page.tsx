import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function VerifyEmailPage() {
  return (
    <section className="mx-auto flex min-h-dvh w-full max-w-md items-center px-4">
      <div className="w-full rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] p-4">
        <CheckCircle2 className="h-8 w-8 text-[var(--green-text)]" />
        <h1 className="mt-4 text-xl font-semibold text-[var(--green-text)]">Email verification ready</h1>
        <p className="mt-1 text-sm leading-6 text-[var(--green-text)]">
          The frontend confirmation screen is in place. Production confirmation will be handled by the FastAPI auth service.
        </p>
        <Link className={cn(buttonVariants({ variant: "primary", size: "md" }), "mt-4 w-full")} href="/markets">
          Continue to markets
        </Link>
      </div>
    </section>
  );
}
