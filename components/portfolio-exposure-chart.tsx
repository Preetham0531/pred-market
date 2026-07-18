"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Category, Market, Position } from "@/lib/mock-data";

type PortfolioExposureChartProps = {
  categories: Category[];
  markets: Market[];
  positions: Position[];
  analyticsExposure?: Array<{ categorySlug: string; exposure: number }>;
};

export function PortfolioExposureChart({ categories, markets, positions, analyticsExposure = [] }: PortfolioExposureChartProps) {
  const data = categories
    .map((category) => {
      const analyticsItem = analyticsExposure.find((item) => item.categorySlug === category.slug);
      const exposure = analyticsItem?.exposure ?? positions
        .filter((position) => {
          const market = markets.find((item) => item.id === position.marketId);
          return market?.categorySlug === category.slug;
        })
        .reduce((sum, position) => sum + position.currentPrice * position.quantity, 0);

      return {
        name: category.shortName,
        exposure
      };
    })
    .filter((item) => item.exposure > 0);

  return (
    <div className="exchange-panel h-[260px] rounded-md p-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Exposure by category</h2>
        <span className="rounded-md border border-[var(--border)] bg-[var(--surface-muted)] px-2 py-1 text-xs text-[var(--muted)]">Scenario risk</span>
      </div>
      <div className="mt-3 h-[205px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: "var(--muted)", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "var(--muted)", fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                border: "1px solid var(--border)",
                borderRadius: 6,
                background: "var(--surface)",
                color: "var(--foreground)"
              }}
            />
            <Bar dataKey="exposure" fill="var(--primary)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
