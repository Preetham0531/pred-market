import Image from "next/image";
import Link from "next/link";
import { ArrowRight, BarChart3, BookOpen, ShieldCheck } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const marketRows = [
  { icon: "/icons/3d/sports.svg", label: "Sports", title: "Will India win the final?", yes: 64, move: "+4.2" },
  { icon: "/icons/3d/economics.svg", label: "Economics", title: "Will the next policy decision hold rates?", yes: 57, move: "+1.8" },
  { icon: "/icons/3d/tech-science.svg", label: "Tech & science", title: "Will a frontier model launch before October?", yes: 46, move: "-2.1" }
];

export default function HomePage() {
  return (
    <div className="mx-auto max-w-[1440px]">
      <section className="grid min-h-[calc(100dvh-10rem)] items-center gap-12 py-12 lg:grid-cols-[0.82fr_1.18fr] lg:py-20">
        <div className="max-w-xl">
          <div className="mb-5 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.1em] text-[var(--muted)]">
            <span className="h-1.5 w-1.5 rounded-full bg-[var(--green-text)]" />
            Simulated-funds staging exchange
          </div>
          <h1 className="max-w-[12ch] text-4xl font-semibold leading-[1.08] text-[var(--foreground)] sm:text-5xl lg:text-6xl">
            Pred-Market
          </h1>
          <p className="mt-5 max-w-lg text-lg leading-8 text-[var(--muted)]">
            Analyze events, read market depth, and trade probability contracts in a calm exchange terminal built for evidence-led decisions.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className={cn(buttonVariants({ variant: "primary", size: "lg" }), "px-5")} href="/sign-up">
              Create account
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link className={buttonVariants({ variant: "secondary", size: "lg" })} href="/markets">
              Explore markets
            </Link>
          </div>
          <div className="mt-10 grid max-w-lg grid-cols-3 gap-5 border-t border-[color-mix(in_srgb,var(--border)_48%,transparent)] pt-5 text-sm">
            <div><ShieldCheck className="mb-2 h-4 w-4 text-[var(--blue-text)]" /><span className="text-[var(--muted)]">Admin-reviewed markets</span></div>
            <div><BookOpen className="mb-2 h-4 w-4 text-[var(--brass-text)]" /><span className="text-[var(--muted)]">Published resolution rules</span></div>
            <div><BarChart3 className="mb-2 h-4 w-4 text-[var(--green-text)]" /><span className="text-[var(--muted)]">Order-book pricing</span></div>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-lg border border-[color-mix(in_srgb,var(--border)_65%,transparent)] bg-[var(--surface-raised)] shadow-[0_28px_80px_rgba(0,0,0,0.28)]">
          <div className="flex items-center justify-between border-b border-[color-mix(in_srgb,var(--border)_55%,transparent)] px-5 py-4">
            <div>
              <div className="text-sm font-semibold">Market board</div>
              <div className="mt-0.5 text-xs text-[var(--muted)]">Probability, movement, and contract depth</div>
            </div>
            <span className="rounded border border-[var(--green-border)]/60 bg-[var(--green-soft)] px-2 py-1 text-xs font-medium text-[var(--green-text)]">Live</span>
          </div>
          <div className="grid grid-cols-[1fr_auto_auto] gap-4 px-5 py-2.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--muted)]">
            <span>Market</span><span>24h</span><span>YES</span>
          </div>
          <div>
            {marketRows.map((market, index) => (
              <Link
                key={market.title}
                href="/markets"
                className="grid grid-cols-[minmax(0,1fr)_auto_auto] items-center gap-4 px-5 py-4 transition-colors hover:bg-[var(--surface-muted)]/50"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <Image src={market.icon} alt="" width={36} height={36} className="h-9 w-9 shrink-0" />
                  <span className="min-w-0">
                    <span className="block text-[11px] text-[var(--muted)]">{market.label}</span>
                    <span className="mt-0.5 block truncate text-sm font-medium">{market.title}</span>
                  </span>
                </div>
                <span className={cn("numeric text-xs font-medium", market.move.startsWith("+") ? "text-[var(--green-text)]" : "text-[var(--red-text)]")}>{market.move}</span>
                <span className="numeric min-w-14 rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] px-2 py-1.5 text-center text-sm font-semibold text-[var(--green-text)]">{market.yes}</span>
                {index < marketRows.length - 1 ? <span className="col-span-3 h-px bg-[color-mix(in_srgb,var(--border)_38%,transparent)]" /> : null}
              </Link>
            ))}
          </div>
          <div className="grid grid-cols-3 border-t border-[color-mix(in_srgb,var(--border)_55%,transparent)] bg-[var(--surface)] px-5 py-4 text-xs">
            <div><span className="block text-[var(--muted)]">Contract payout</span><strong className="numeric mt-1 block">₹100</strong></div>
            <div><span className="block text-[var(--muted)]">Order type</span><strong className="mt-1 block">Limit</strong></div>
            <div><span className="block text-[var(--muted)]">Funds</span><strong className="mt-1 block">Simulated</strong></div>
          </div>
        </div>
      </section>
    </div>
  );
}
