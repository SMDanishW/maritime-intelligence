"use client";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { DashboardSummary } from "../lib/types";

interface PortCallsPanelProps {
  data: DashboardSummary | null;
  loading: boolean;
}

const COLORS = ["#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#dbeafe"];

export function PortCallsPanel({ data, loading }: PortCallsPanelProps) {
  const byPort = data?.port_calls?.by_port ?? {};
  const chartData = Object.entries(byPort)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, value]) => ({ name: name.length > 12 ? name.slice(0, 12) + "…" : name, value }));

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <h3 className="text-sm font-medium text-slate-300 mb-3">Port Calls by Port</h3>
      {loading || !data ? (
        <div className="h-36 animate-pulse bg-slate-800 rounded" />
      ) : chartData.length === 0 ? (
        <p className="text-xs text-slate-500 py-10 text-center">No data</p>
      ) : (
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} />
            <Tooltip
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6, fontSize: 12 }}
              labelStyle={{ color: "#e2e8f0" }}
              itemStyle={{ color: "#60a5fa" }}
            />
            <Bar dataKey="value" radius={[3, 3, 0, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
      {data && (
        <div className="mt-2 text-xs text-slate-500 text-right">
          {data.port_calls.total.toLocaleString()} total port calls
        </div>
      )}
    </div>
  );
}
