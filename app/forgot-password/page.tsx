import Link from "next/link";
import { Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ForgotPasswordPage() {
  return (
    <section className="mx-auto flex min-h-dvh w-full max-w-md items-center px-4">
      <div className="w-full rounded-md border border-[var(--border)] bg-[var(--surface)] p-4">
        <Mail className="h-8 w-8 text-[var(--primary)]" />
        <h1 className="mt-4 text-xl font-semibold">Reset password</h1>
        <p className="mt-1 text-sm leading-6 text-[var(--muted)]">
          Enter your email. Delivery is mocked until the FastAPI mailer is implemented.
        </p>
        <form className="mt-4 space-y-3">
          <Input type="email" placeholder="you@example.com" autoComplete="email" />
          <Button className="w-full" variant="primary" type="submit">
            Send reset link
          </Button>
        </form>
        <Link className="mt-4 block text-sm font-medium text-[var(--primary-strong)]" href="/sign-in">
          Back to sign in
        </Link>
      </div>
    </section>
  );
}
