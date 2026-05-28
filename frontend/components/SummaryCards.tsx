"use client";
import { Ship, Anchor, AlertTriangle, Snowflake, Activity } from "lucide-react";
import type { DashboardSummary } from "../lib/types";
import clsx from "clsx";

const RISK_COLORS: Record<string, string> = {
  Low: "text-green-400",
  Medium: "text-yellow-400",
  High: "text-orange-400",
  Critical: "text-red-400",
};

interface SummaryCardsProps {
  data: DashboardSummary | null;
  loading: boolean;
}

function Card({
  icon,
  label,
  value,
  sub,
  valueClass,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  valueClass?: string;
}) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 flex gap-4 items-start">
      <div className="mt-0.5 text-blue-400">{icon}</div>
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-wide">{label}</p>
        <p className={clsx("text-2xl font-bold mt-0.5", valueClass ?? "text-slate-100")}>
          {value}
        </p>
        {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

export function SummaryCards({ data, loading }: SummaryCardsProps) {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 rounded-lg p-4 h-24 animate-pulse" />
        ))}
      </div>
    );
  }

  const riskLevel = data.risk.level;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
      <Card
        icon={<Ship className="h-5 w-5" />}
        label="Live Vessels"
        value={data.vessels.total.toLocaleString()}
        sub="in Finnish waters"
      />
      <Card
        icon={<Anchor className="h-5 w-5" />}
        label="Port Calls"
        value={data.port_calls.total.toLocaleString()}
        sub="active"
      />
      <Card
        icon={<AlertTriangle className="h-5 w-5" />}
        label="AtoN Faults"
        value={data.aton_faults.open}
        sub={`of ${data.aton_faults.total} total`}
        valueClass={data.aton_faults.open > 0 ? "text-orange-400" : "text-green-400"}
      />
      <Card
        icon={<Snowflake className="h-5 w-5" />}
        label="Winter Nav"
        value={data.winter_navigation.vessels?.length ?? 0}
        sub={`${data.winter_navigation.active_dirways ?? 0} active dirways`}
      />
      <Card
        icon={<Activity className="h-5 w-5" />}
        label="Risk Score"
        value={`${data.risk.score} — ${riskLevel}`}
        sub="composite risk"
        valueClass={RISK_COLORS[riskLevel] ?? "text-slate-100"}
      />
    </div>
  );
}
