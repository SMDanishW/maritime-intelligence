"use client";
import type { DashboardSummary } from "../lib/types";
import clsx from "clsx";

interface RiskPanelProps {
  data: DashboardSummary | null;
  loading: boolean;
}

const LEVEL_STYLE: Record<string, { bar: string; badge: string }> = {
  Low: { bar: "bg-green-500", badge: "bg-green-950 text-green-400" },
  Medium: { bar: "bg-yellow-500", badge: "bg-yellow-950 text-yellow-400" },
  High: { bar: "bg-orange-500", badge: "bg-orange-950 text-orange-400" },
  Critical: { bar: "bg-red-500", badge: "bg-red-950 text-red-400" },
};

export function RiskPanel({ data, loading }: RiskPanelProps) {
  const risk = data?.risk;
  const style = LEVEL_STYLE[risk?.level ?? "Low"];

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-slate-300">Risk Assessment</h3>
        {risk && (
          <span className={clsx("text-xs px-2 py-0.5 rounded-full font-medium", style.badge)}>
            {risk.level}
          </span>
        )}
      </div>

      {loading || !risk ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-5 animate-pulse bg-slate-800 rounded" />
          ))}
        </div>
      ) : (
        <>
          <div className="flex items-end gap-2 mb-3">
            <span className={clsx("text-3xl font-bold", LEVEL_STYLE[risk.level]?.badge.split(" ")[1]?.replace("text-", "text-") ?? "text-slate-100")}>
              {risk.score}
            </span>
            <span className="text-slate-500 text-sm mb-1">/ 100</span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-1.5 mb-4">
            <div
              className={clsx("h-1.5 rounded-full transition-all", style.bar)}
              style={{ width: `${risk.score}%` }}
            />
          </div>

          <div className="space-y-2">
            {risk.components.map((c) => (
              <div key={c.name} className="flex items-center gap-2 text-xs">
                <span className="text-slate-400 w-32 truncate">{c.name}</span>
                <div className="flex-1 bg-slate-800 rounded-full h-1">
                  <div
                    className={clsx("h-1 rounded-full", style.bar)}
                    style={{ width: `${Math.min(c.score, 100)}%` }}
                  />
                </div>
                <span className="text-slate-500 w-8 text-right">{c.weighted.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
