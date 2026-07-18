"use client";

import { useMemo } from "react";
import type { ChartPoint } from "@/lib/mock-data";

type MiniProbabilityChartProps = {
  data: ChartPoint[];
  tone?: "green" | "red" | "neutral";
  height?: number;
};

const width = 420;

function colorFor(tone: "green" | "red" | "neutral") {
  if (tone === "green") return "var(--green-border)";
  if (tone === "red") return "var(--red-border)";
  return "var(--primary-strong)";
}

export function MiniProbabilityChart({ data, tone = "neutral", height = 128 }: MiniProbabilityChartProps) {
  const chart = useMemo(() => {
    if (data.length < 2) return null;
    const values = data.map((point) => point.value);
    const min = Math.max(0, Math.min(...values) - 8);
    const max = Math.min(100, Math.max(...values) + 8);
    const xScale = (index: number) => (index / Math.max(1, data.length - 1)) * width;
    const yScale = (value: number) => 12 + ((max - value) / Math.max(1, max - min)) * (height - 24);
    const points = data.map((point, index) => ({ x: xScale(index), y: yScale(point.value), value: point.value }));
    const line = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(" ");
    const area = `${line} L ${width} ${height} L 0 ${height} Z`;
    return { line, area, points };
  }, [data, height]);

  if (!chart) {
    return <div className="grid h-28 place-items-center rounded-md bg-[var(--surface-raised)]/42 text-xs text-[var(--muted)]">No history yet</div>;
  }

  const stroke = colorFor(tone);

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-full min-h-28 w-full" role="img" aria-label="Compact probability chart">
      <defs>
        <linearGradient id={`mini-chart-${tone}`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.26" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      {[0.25, 0.5, 0.75].map((ratio) => (
        <line key={ratio} x1="0" x2={width} y1={height * ratio} y2={height * ratio} stroke="var(--border)" strokeOpacity="0.5" strokeDasharray="2 5" />
      ))}
      <path d={chart.area} fill={`url(#mini-chart-${tone})`} />
      <path className="exchange-chart-line" d={chart.line} fill="none" stroke={stroke} strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
      <circle cx={chart.points.at(-1)?.x} cy={chart.points.at(-1)?.y} r="4" fill="var(--surface)" stroke={stroke} strokeWidth="2" />
    </svg>
  );
}
