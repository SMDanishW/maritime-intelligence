"use client";
import { Waves } from "lucide-react";
import type { DashboardSummary } from "../lib/types";

interface SeaStatePanelProps {
  data: DashboardSummary | null;
}

export function SeaStatePanel({ data }: SeaStatePanelProps) {
  const ss = data?.sea_state;

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Waves className="h-4 w-4 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-300">Sea State</h3>
      </div>

      <div className="flex flex-col items-center justify-center py-4 gap-2 text-center">
        <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded-full">MQTT only</span>
        <p className="text-xs text-slate-500 max-w-xs leading-relaxed">
          {ss?.reason ?? "Sea state data is available via MQTT stream only."}
        </p>
        {ss?.mqtt_broker && (
          <code className="text-xs text-cyan-600 font-mono truncate max-w-full">
            {ss.mqtt_broker}
          </code>
        )}
        {ss?.topic_pattern && (
          <p className="text-xs text-slate-600">
            Topic: <code className="text-slate-500">{ss.topic_pattern}</code>
          </p>
        )}
      </div>
    </div>
  );
}
