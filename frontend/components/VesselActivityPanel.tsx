"use client";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { DashboardSummary } from "../lib/types";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

const STATUS_LABELS: Record<string, string> = {
  "0": "Under way (engine)",
  "1": "Anchored",
  "2": "Not under command",
  "3": "Restricted",
  "5": "Moored",
  "8": "Under way (sail)",
};

interface VesselActivityPanelProps {
  data: DashboardSummary | null;
  loading: boolean;
}

export function VesselActivityPanel({ data, loading }: VesselActivityPanelProps) {
  const byStatus = data?.vessels?.by_nav_status ?? {};
  const chartData = Object.entries(byStatus)
    .filter(([, v]) => v > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 7)
    .map(([key, value]) => ({
      name: STATUS_LABELS[key] ?? key,
      value,
    }));

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <h3 className="text-sm font-medium text-slate-300 mb-3">Vessel Navigation Status</h3>
      {loading || !data ? (
        <div className="h-36 animate-pulse bg-slate-800 rounded" />
      ) : chartData.length === 0 ? (
        <p className="text-xs text-slate-500 py-10 text-center">No data</p>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={65}
              dataKey="value"
              strokeWidth={0}
            >
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6, fontSize: 11 }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Legend
              iconSize={8}
              wrapperStyle={{ fontSize: 10, color: "#94a3b8" }}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
