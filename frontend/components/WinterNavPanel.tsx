"use client";
import { Snowflake } from "lucide-react";
import type { DashboardSummary } from "../lib/types";

interface WinterNavPanelProps {
  data: DashboardSummary | null;
  loading: boolean;
}

export function WinterNavPanel({ data, loading }: WinterNavPanelProps) {
  const vessels = data?.winter_navigation?.vessels ?? [];
  const activeDirways = data?.winter_navigation?.active_dirways ?? 0;

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Snowflake className="h-4 w-4 text-blue-300" />
        <h3 className="text-sm font-medium text-slate-300">Winter Navigation</h3>
      </div>

      {loading || !data ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-7 animate-pulse bg-slate-800 rounded" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          <div>
            <p className="text-xs text-slate-500 mb-1.5">
              Icebreaker / Assistance vessels ({vessels.length})
            </p>
            {vessels.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No active vessels</p>
            ) : (
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {vessels.map((v, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-0.5">
                    <span className={`w-2 h-2 rounded-full shrink-0 ${v.active ? "bg-green-400" : "bg-slate-500"}`} />
                    <span className="text-slate-300">{v.name}</span>
                    <span className="text-slate-600 ml-auto text-xs">
                      {v.active ? "active" : v.current_activity ?? "stopped"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-2 border-t border-slate-700 flex items-center justify-between">
            <span className="text-xs text-slate-500">Active dirways</span>
            <span className={`text-sm font-semibold ${activeDirways > 0 ? "text-blue-300" : "text-green-400"}`}>
              {activeDirways}
            </span>
          </div>

          {activeDirways === 0 && vessels.length === 0 && (
            <p className="text-xs text-green-400 text-center py-1">
              No winter navigation restrictions active
            </p>
          )}
        </div>
      )}
    </div>
  );
}
