"use client";

import Link from "next/link";
import { PortfolioExposureChart } from "@/components/portfolio-exposure-chart";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/components/auth-provider";
import { useCategories, useMarkets, usePortfolioData, useUserAnalytics, useWalletData } from "@/lib/api-hooks";
import { formatCurrency } from "@/lib/utils";

export function ProfileWorkspace({ title = "Profile" }: { title?: string }) {
  const { user } = useAuth();
  const { data: portfolio, isLoading, error } = usePortfolioData();
  const { data: wallet } = useWalletData();
  const { data: markets = [] } = useMarkets();
  const { data: categories = [] } = useCategories();
  const { data: userAnalytics } = useUserAnalytics();
  const positions = (portfolio?.positions ?? []).map((position) => {
    const market = markets.find((item) => item.id === position.marketId);
    return {
      ...position,
      currentPrice: market?.probability ?? position.currentPrice,
      maxPayout: position.quantity * 100
    };
  });
  const lockedCash = userAnalytics?.lockedCash ?? wallet?.locked ?? 0;

  return (
    <div className="space-y-5">
      <div className="grid gap-3 xl:grid-cols-[1fr_360px]">
        <div>
          <h1 className="text-2xl font-semibold">{title}</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">{title === "Portfolio" ? "Your positions, value, and possible payouts." : "Your account and trading activity."}</p>
        </div>
        <div className="exchange-panel rounded-md p-3">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-[var(--muted)]">Signed-in account</div>
          <div className="mt-2 text-sm font-semibold">{user?.displayName ?? "Trader"}</div>
          <div className="mt-1 text-xs text-[var(--muted)]">{user?.email ?? "No active session"}</div>
          <div className="mt-2 flex flex-wrap gap-1">
            {(user?.roles ?? []).map((role) => (
              <Badge key={role} tone={role === "ADMIN" ? "brass" : "blue"}>
                {role}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      {error ? (
        <div className="rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red-text)]">
          Profile portfolio data could not be loaded. Sign in and try again.
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="exchange-panel overflow-hidden rounded-md">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--border)] px-3 py-2">
            <div className="text-sm font-semibold">Open positions</div>
            <div className="text-xs text-[var(--muted)]">{positions.length} positions / {formatCurrency(lockedCash)} locked</div>
          </div>
          <div className="exchange-table-header hidden grid-cols-[1fr_90px_100px_100px_110px] px-3 py-2 md:grid">
            <span>Market</span>
            <span>Qty</span>
            <span>Entry</span>
            <span>Current</span>
            <span>PnL</span>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {isLoading ? (
              <div className="px-3 py-6 text-sm text-[var(--muted)]">Loading positions...</div>
            ) : positions.length ? (
              positions.map((position) => {
                const market = markets.find((item) => item.id === position.marketId);
                const positionPnl = (position.currentPrice - position.averageEntry) * position.quantity;

                return (
                  <Link
                    href={`/markets/${position.marketId}`}
                    key={`${position.marketId}-${position.outcome}`}
                    className="grid gap-2 px-3 py-3 text-sm hover:bg-[var(--surface-muted)] md:grid-cols-[1fr_90px_100px_100px_110px] md:items-center"
                  >
                    <div>
                      <div className="font-medium">{market?.title ?? position.marketId}</div>
                      <div className="mt-1 text-xs text-[var(--muted)]">{position.outcome} / {market?.subcategory}</div>
                    </div>
                    <div className="numeric">{position.quantity}</div>
                    <div className="numeric">{position.averageEntry}</div>
                    <div className="numeric">{position.currentPrice}</div>
                    <div className={positionPnl >= 0 ? "numeric font-medium text-[var(--green-text)]" : "numeric font-medium text-[var(--red-text)]"}>
                      {formatCurrency(positionPnl)}
                    </div>
                  </Link>
                );
              })
            ) : (
              <div className="px-3 py-6 text-sm text-[var(--muted)]">No open positions yet.</div>
            )}
          </div>
        </div>

        <PortfolioExposureChart categories={categories} markets={markets} positions={positions} analyticsExposure={userAnalytics?.categoryExposure} />
      </div>

      <section className="exchange-panel rounded-md p-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Scenario payout table</h2>
          <span className="text-xs text-[var(--muted)]">Gross payout before V1 fees</span>
        </div>
        <div className="mt-3 grid gap-2 md:grid-cols-2">
          {positions.length ? (
            positions.map((position) => {
              const market = markets.find((item) => item.id === position.marketId);
              return (
                <div key={`${position.marketId}-${position.outcome}`} className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] p-3 text-sm">
                  <div className="font-medium">{market?.title ?? position.marketId}</div>
                  <div className="mt-2 flex justify-between text-[var(--muted)]">
                    <span>If {position.outcome} wins</span>
                    <span className="numeric">{formatCurrency(position.maxPayout)}</span>
                  </div>
                  <div className="mt-1 flex justify-between text-[var(--muted)]">
                    <span>If it loses</span>
                    <span className="numeric">{formatCurrency(0)}</span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-sm text-[var(--muted)]">No scenario exposure yet.</div>
          )}
        </div>
      </section>
    </div>
  );
}
