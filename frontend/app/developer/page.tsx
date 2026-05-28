"use client";
import { useState, useEffect } from "react";
import { ChevronDown, ChevronRight, ArrowLeft, Terminal, Clock } from "lucide-react";
import Link from "next/link";
import type { AgentTrace } from "../../lib/types";
import clsx from "clsx";

const NODE_COLORS: Record<string, string> = {
  guardrail:       "border-l-yellow-500  bg-yellow-950/20",
  supervisor:      "border-l-purple-500  bg-purple-950/20",
  fetch_domains:   "border-l-blue-500    bg-blue-950/20",
  risk_agent:      "border-l-orange-500  bg-orange-950/20",
  visualization:   "border-l-cyan-500    bg-cyan-950/20",
  response_writer: "border-l-green-500   bg-green-950/20",
};
const NODE_BADGE: Record<string, string> = {
  guardrail:       "bg-yellow-950  text-yellow-400",
  supervisor:      "bg-purple-950  text-purple-400",
  fetch_domains:   "bg-blue-950    text-blue-400",
  risk_agent:      "bg-orange-950  text-orange-400",
  visualization:   "bg-cyan-950    text-cyan-400",
  response_writer: "bg-green-950   text-green-400",
};

interface StoredTrace {
  question: string;
  timestamp: string;
  trace: AgentTrace[];
}

function JsonNode({ value, depth = 0 }: { value: unknown; depth?: number }) {
  const [open, setOpen] = useState(depth < 2);

  if (value === null || value === undefined) return <span className="text-slate-500">null</span>;
  if (typeof value === "boolean") return <span className="text-blue-400">{String(value)}</span>;
  if (typeof value === "number") return <span className="text-amber-400">{value}</span>;
  if (typeof value === "string") {
    return (
      <span className="text-green-400 break-all">
        &quot;{value}&quot;
      </span>
    );
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-slate-500">[]</span>;
    return (
      <span>
        <button onClick={() => setOpen((v) => !v)} className="text-slate-400 hover:text-slate-200 inline-flex items-center gap-0.5">
          {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          <span className="text-slate-500 text-xs">[{value.length}]</span>
        </button>
        {open && (
          <div className="ml-4 border-l border-slate-700 pl-2 mt-1 space-y-1">
            {value.map((item, i) => (
              <div key={i} className="flex gap-1">
                <span className="text-slate-600 text-xs shrink-0">{i}:</span>
                <JsonNode value={item} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
      </span>
    );
  }

  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) return <span className="text-slate-500">{"{}"}</span>;
    return (
      <span>
        <button onClick={() => setOpen((v) => !v)} className="text-slate-400 hover:text-slate-200 inline-flex items-center gap-0.5">
          {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          <span className="text-slate-500 text-xs">{"{"}  {entries.length} keys {"}"}</span>
        </button>
        {open && (
          <div className="ml-4 border-l border-slate-700 pl-2 mt-1 space-y-1">
            {entries.map(([k, v]) => (
              <div key={k} className="flex gap-1.5 flex-wrap">
                <span className="text-slate-300 text-xs shrink-0">{k}:</span>
                <JsonNode value={v} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
      </span>
    );
  }

  return <span className="text-slate-400">{String(value)}</span>;
}

function TraceCard({ step, index }: { step: AgentTrace; index: number }) {
  const [expanded, setExpanded] = useState(true);
  const colorClass = NODE_COLORS[step.node] ?? "border-l-slate-500 bg-slate-800/30";
  const badgeClass = NODE_BADGE[step.node] ?? "bg-slate-800 text-slate-400";

  return (
    <div className={clsx("border-l-4 rounded-r-lg p-4", colorClass)}>
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-3 w-full text-left"
      >
        <span className="text-slate-500 text-xs font-mono w-5 shrink-0">#{index + 1}</span>
        <span className={clsx("text-xs px-2 py-0.5 rounded font-mono font-medium", badgeClass)}>
          {step.node}
        </span>
        <span className="text-slate-500 text-xs ml-auto">
          {Object.keys(step.output).join(", ")}
        </span>
        {expanded
          ? <ChevronDown className="h-3.5 w-3.5 text-slate-500 shrink-0" />
          : <ChevronRight className="h-3.5 w-3.5 text-slate-500 shrink-0" />
        }
      </button>

      {expanded && (
        <div className="mt-3 text-xs font-mono leading-relaxed">
          <JsonNode value={step.output} depth={0} />
        </div>
      )}
    </div>
  );
}

export default function DeveloperPage() {
  const [stored, setStored] = useState<StoredTrace | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("marine_dev_trace");
      if (raw) setStored(JSON.parse(raw));
    } catch {
      // localStorage unavailable
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="flex items-center gap-4 px-6 py-3 bg-slate-900 border-b border-slate-700">
        <Link href="/" className="flex items-center gap-1.5 text-slate-400 hover:text-slate-200 text-sm transition-colors">
          <ArrowLeft className="h-4 w-4" /> Dashboard
        </Link>
        <div className="flex items-center gap-2 ml-2">
          <Terminal className="h-4 w-4 text-green-400" />
          <span className="text-sm font-semibold text-slate-200">Agent Trace — Developer View</span>
        </div>
        {stored && (
          <div className="ml-auto flex items-center gap-1.5 text-xs text-slate-500">
            <Clock className="h-3 w-3" />
            {new Date(stored.timestamp).toLocaleTimeString()}
          </div>
        )}
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-4">
        {!stored ? (
          <div className="text-center py-24">
            <Terminal className="h-10 w-10 text-slate-700 mx-auto mb-4" />
            <p className="text-slate-500 text-sm">No trace yet.</p>
            <p className="text-slate-600 text-xs mt-1">
              Ask a question in the chat widget on the{" "}
              <Link href="/" className="text-blue-400 hover:underline">dashboard</Link>,
              then return here.
            </p>
          </div>
        ) : (
          <>
            {/* Question banner */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3">
              <p className="text-xs text-slate-500 mb-1">Query</p>
              <p className="text-slate-200 font-medium">{stored.question}</p>
            </div>

            {/* Pipeline overview */}
            <div className="flex items-center gap-2 flex-wrap">
              {stored.trace.map((step, i) => (
                <div key={i} className="flex items-center gap-1.5">
                  <span className={clsx("text-xs px-2 py-0.5 rounded font-mono", NODE_BADGE[step.node] ?? "bg-slate-800 text-slate-400")}>
                    {step.node}
                  </span>
                  {i < stored.trace.length - 1 && <span className="text-slate-700">→</span>}
                </div>
              ))}
            </div>

            {/* Per-node cards */}
            <div className="space-y-3">
              {stored.trace.map((step, i) => (
                <TraceCard key={i} step={step} index={i} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
