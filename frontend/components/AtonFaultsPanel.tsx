"use client";
import { AlertTriangle } from "lucide-react";
import type { DashboardSummary } from "../lib/types";

interface AtonFaultsPanelProps {
  data: DashboardSummary | null;
  loading: boolean;
}

const STATE_COLORS: Record<string, string> = {
  Open: "text-orange-400",
  Closed: "text-green-400",
};

export function AtonFaultsPanel({ data, loading }: AtonFaultsPanelProps) {
  const faults = data?.aton_faults?.faults ?? [];
  const openFaults = faults.filter((f) => f.state === "Open");
  const byType = data?.aton_faults?.by_type ?? {};

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-slate-300">AtoN Faults</h3>
        {data && (
          <span className="text-xs bg-orange-950 text-orange-400 px-2 py-0.5 rounded-full">
            {data.aton_faults.open} open
          </span>
        )}
      </div>

      {loading || !data ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-8 animate-pulse bg-slate-800 rounded" />
          ))}
        </div>
      ) : openFaults.length === 0 ? (
        <p className="text-xs text-green-400 py-4 text-center">No open faults</p>
      ) : (
        <>
          <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
            {openFaults.slice(0, 10).map((f) => (
              <div key={f.aton_id} className="flex items-start gap-2 text-xs py-1 border-b border-slate-800">
                <AlertTriangle className="h-3 w-3 text-orange-400 mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <span className="text-slate-300 font-medium truncate block">{f.aton_name}</span>
                  <span className="text-slate-500">{f.fault_type} · {f.aton_type}</span>
                </div>
              </div>
            ))}
          </div>

          {Object.keys(byType).length > 0 && (
            <div className="mt-3 pt-3 border-t border-slate-700">
              <p className="text-xs text-slate-500 mb-1">By fault type</p>
              <div className="space-y-1">
                {Object.entries(byType)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 4)
                  .map(([type, count]) => (
                    <div key={type} className="flex items-center gap-2 text-xs">
                      <span className="text-slate-400 w-24 truncate">{type}</span>
                      <div className="flex-1 bg-slate-800 rounded-full h-1.5">
                        <div
                          className="bg-orange-500 h-1.5 rounded-full"
                          style={{ width: `${Math.min((count / (data.aton_faults.total || 1)) * 100, 100)}%` }}
                        />
                      </div>
                      <span className="text-slate-500 w-5 text-right">{count}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
