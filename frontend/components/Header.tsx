"use client";
import { Anchor, RefreshCw } from "lucide-react";

interface HeaderProps {
  lastUpdated: Date | null;
  refreshing: boolean;
  onRefresh: () => void;
}

export function Header({ lastUpdated, refreshing, onRefresh }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-3 bg-slate-900 border-b border-slate-700">
      <div className="flex items-center gap-3">
        <Anchor className="text-blue-400 h-6 w-6" />
        <div>
          <h1 className="text-lg font-bold text-slate-100 leading-tight">
            Finnish Marine Traffic Intelligence
          </h1>
          {lastUpdated && (
            <p className="text-xs text-slate-500">
              Updated {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
      <button
        onClick={onRefresh}
        disabled={refreshing}
        className="flex items-center gap-2 px-3 py-1.5 text-sm rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-50 transition-colors"
      >
        <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
        Refresh
      </button>
    </header>
  );
}
