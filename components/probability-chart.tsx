"use client";

import { useMemo, useState } from "react";
import { DataState } from "@/components/ui/data-state";
import type { ChartPoint } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

type ProbabilityChartProps = {
  data: ChartPoint[];
  sourceLabel?: string;
  closeTime?: string;
  status?: string;
};

const ranges = ["1D", "1W", "1M", "ALL"] as const;
const chartWidth = 720;
const chartHeight = 280;
const padding = { top: 18, right: 44, bottom: 30, left: 24 };

function clampRange(value: number) {
  return Math.min(99, Math.max(1, value));
}

export function ProbabilityChart({ data, sourceLabel = "", closeTime = "", status = "" }: ProbabilityChartProps) {
  const [range, setRange] = useState<(typeof ranges)[number]>("1W");
  const visibleData = useMemo(() => {
    if (range === "1D") return data.slice(-2);
    if (range === "1W") return data.slice(-7);
    if (range === "1M") return data.slice(-30);
    return data;
  }, [data, range]);
  const maxVolume = Math.max(...visibleData.map((point) => point.volume), 1);
  const latest = visibleData.at(-1);
  const previous = visibleData.at(-2);
  const change = latest && previous ? latest.value - previous.value : 0;
  const isSparse = visibleData.length > 0 && visibleData.length < 3;

  const chart = useMemo(() => {
    if (!visibleData.length) return null;
    const values = visibleData.map((point) => clampRange(point.value));
    const minValue = Math.max(0, Math.min(...values) - 8);
    const maxValue = Math.min(100, Math.max(...values) + 8);
    const innerWidth = chartWidth - padding.left - padding.right;
    const innerHeight = chartHeight - padding.top - padding.bottom;
    const yScale = (value: number) => padding.top + ((maxValue - value) / Math.max(1, maxValue - minValue)) * innerHeight;
    const xScale = (index: number) => padding.left + (index / Math.max(1, visibleData.length - 1)) * innerWidth;
    const points = visibleData.map((point, index) => ({
      ...point,
      x: xScale(index),
      y: yScale(clampRange(point.value))
    }));
    const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(" ");
    const areaPath = `${linePath} L ${points.at(-1)?.x.toFixed(2)} ${chartHeight - padding.bottom} L ${points[0]?.x.toFixed(2)} ${chartHeight - padding.bottom} Z`;
    const yTicks = Array.from({ length: 5 }, (_, index) => {
      const value = minValue + ((maxValue - minValue) / 4) * index;
      return {
        value: Math.round(value),
        y: yScale(value)
      };
    }).reverse();

    return { points, linePath, areaPath, yTicks };
  }, [visibleData]);

  return (
    <section className="rounded-md bg-[var(--surface)]/38 p-3">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold">Probability history</h2>
          <p className="text-xs text-[var(--muted)]">YES price over time.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className={cn("numeric rounded-md px-2 py-1 text-xs font-medium", change >= 0 ? "bg-[var(--green-soft)] text-[var(--green-text)]" : "bg-[var(--red-soft)] text-[var(--red-text)]")}>
            {change >= 0 ? "+" : ""}{change.toFixed(0)} pts
          </div>
          <div className="inline-flex rounded-md bg-[var(--surface-muted)]/60 p-1">
            {ranges.map((item) => (
              <button
                key={item}
                className={cn(
                  "h-7 cursor-pointer rounded px-2 text-xs font-medium transition",
                  range === item ? "bg-[var(--surface-raised)] text-[var(--foreground)]" : "text-[var(--muted)] hover:text-[var(--foreground)]"
                )}
                onClick={() => setRange(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </div>

      {chart ? (
        <>
          {isSparse ? (
            <div className="mb-3 rounded-md border border-[var(--brass-border)] bg-[var(--brass-soft)] px-3 py-2 text-xs leading-5 text-[var(--brass-text)]">
              Limited history is available for this timeframe. Use broader ranges before treating the trend as stable.
            </div>
          ) : null}
          <div className="mx-auto aspect-[18/7] w-full max-w-[720px] overflow-hidden rounded-md bg-[var(--surface-raised)]/46">
            <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="h-full w-full" role="img" aria-label="YES probability chart">
              <defs>
                <linearGradient id="probability-area" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.22" />
                  <stop offset="100%" stopColor="var(--primary)" stopOpacity="0.02" />
                </linearGradient>
              </defs>
              {chart.yTicks.map((tick) => (
                <g key={tick.value}>
                  <line x1={padding.left} x2={chartWidth - padding.right} y1={tick.y} y2={tick.y} stroke="var(--border)" strokeWidth="1" />
                  <text x={chartWidth - padding.right + 10} y={tick.y + 4} className="fill-[var(--muted)] text-[11px]">
                    {tick.value}
                  </text>
                </g>
              ))}
              {chart.points.map((point) => (
                <line key={`x-${point.time}`} x1={point.x} x2={point.x} y1={padding.top} y2={chartHeight - padding.bottom} stroke="var(--surface-muted)" strokeWidth="1" />
              ))}
              <path d={chart.areaPath} fill="url(#probability-area)" />
              <path d={chart.linePath} fill="none" stroke="var(--primary-strong)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.4" />
              {chart.points.map((point, index) => (
                <g key={point.time}>
                  <circle cx={point.x} cy={point.y} r={index === chart.points.length - 1 ? 4 : 3} fill="var(--surface)" stroke="var(--primary-strong)" strokeWidth="2" />
                  <text x={point.x} y={chartHeight - 10} textAnchor="middle" className="fill-[var(--muted)] text-[11px]">
                    {new Date(point.time).getUTCDate()}
                  </text>
                </g>
              ))}
              {latest ? (
                <>
                  <line x1={padding.left} x2={chartWidth - padding.right} y1={chart.points.at(-1)?.y} y2={chart.points.at(-1)?.y} stroke="var(--primary-strong)" strokeDasharray="2 3" />
                  <circle cx={chart.points.at(-1)?.x} cy={chart.points.at(-1)?.y} r="7" fill="none" stroke="var(--brass)" strokeDasharray="2 2" />
                  <text x={chartWidth - padding.right + 10} y={(chart.points.at(-1)?.y ?? 0) + 4} className="fill-[var(--green-text)] text-[11px] font-semibold">
                    {latest.value}
                  </text>
                </>
              ) : null}
            </svg>
          </div>
          <div className="mx-auto mt-3 grid h-10 w-full max-w-[720px] grid-flow-col items-end gap-1 pt-2">
            {visibleData.map((point) => (
              <div
                key={`${point.time}-${point.volume}`}
                className="min-w-1 rounded-t bg-[var(--blue-border)]"
                title={`${point.time}: ${point.volume}`}
                style={{ height: `${Math.max(14, (point.volume / maxVolume) * 100)}%` }}
              />
            ))}
          </div>
          {sourceLabel || closeTime || status ? (
            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[var(--muted)]">
              {sourceLabel ? <span className="text-[var(--blue-text)]">{sourceLabel}</span> : null}
              {closeTime ? <span className="text-[var(--brass-text)]">Closes {closeTime}</span> : null}
              {status ? <span>{status}</span> : null}
            </div>
          ) : null}
        </>
      ) : (
        <DataState
          className="min-h-[300px]"
          title="No probability history yet"
          message="The chart will populate after the backend provides price history or live trades for this contract."
          tone="empty"
          badge="Chart empty"
        />
      )}
    </section>
  );
}
