"use client";
import dynamic from "next/dynamic";
import type { DashboardSummary, ChatResponse } from "../lib/types";

const MarineMapInner = dynamic(
  () => import("./MarineMapInner").then((m) => ({ default: m.MarineMapInner })),
  { ssr: false, loading: () => <div className="h-full bg-slate-900 animate-pulse rounded-lg" /> }
);

interface MarineMapProps {
  data: DashboardSummary | null;
  overlay: ChatResponse["map_data"] | null;
}

export function MarineMap({ data, overlay }: MarineMapProps) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg overflow-hidden" style={{ height: 420 }}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-700">
        <span className="text-sm font-medium text-slate-300">Live Marine Traffic Map</span>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-blue-500" /> Vessel (moving)
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-slate-500" /> Vessel (anchored)
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-orange-500" /> AtoN fault
          </span>
        </div>
      </div>
      <div style={{ height: "calc(100% - 41px)" }}>
        <MarineMapInner data={data} overlay={overlay} />
      </div>
    </div>
  );
}
