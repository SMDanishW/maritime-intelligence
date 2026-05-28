"use client";
import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Activity, Maximize2, Minimize2, ExternalLink } from "lucide-react";
import Link from "next/link";
import { api } from "../lib/api";
import type { ChatMessage, ChatResponse } from "../lib/types";
import clsx from "clsx";

interface ChatWidgetProps {
  onMapOverlay: (data: ChatResponse["map_data"]) => void;
  onChartOverlay: (data: ChatResponse["chart_data"]) => void;
}

const RISK_COLORS: Record<string, string> = {
  Low: "text-green-400",
  Medium: "text-yellow-400",
  High: "text-orange-400",
  Critical: "text-red-400",
};

type WidgetSize = "compact" | "expanded" | "fullscreen";

const SIZE_DIMS: Record<WidgetSize, { width: string; height: string }> = {
  compact:    { width: "320px",  height: "480px" },
  expanded:   { width: "560px",  height: "620px" },
  fullscreen: { width: "min(92vw, 860px)", height: "min(88vh, 860px)" },
};

function saveTrace(question: string, trace: ChatResponse["trace"]) {
  try {
    localStorage.setItem(
      "marine_dev_trace",
      JSON.stringify({ question, timestamp: new Date().toISOString(), trace }),
    );
  } catch {
    // localStorage unavailable in this env
  }
}

export function ChatWidget({ onMapOverlay, onChartOverlay }: ChatWidgetProps) {
  const [open, setOpen] = useState(false);
  const [size, setSize] = useState<WidgetSize>("compact");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hello! Ask me about Finnish marine traffic, vessels, AtoN faults, port calls, or winter navigation.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastHasTrace, setLastHasTrace] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
      inputRef.current?.focus();
    }
  }, [open, messages]);

  function cycleSize() {
    setSize((s) => s === "compact" ? "expanded" : s === "expanded" ? "fullscreen" : "compact");
  }

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setLastHasTrace(false);
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const resp = await api.chat(text, sessionId);

      if (resp.trace?.length) {
        saveTrace(text, resp.trace);
        setLastHasTrace(true);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: resp.answer,
          risk: resp.risk ?? undefined,
        },
      ]);
      if (resp.map_data) onMapOverlay(resp.map_data);
      if (resp.chart_data) onChartOverlay(resp.chart_data);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't reach the backend. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  const dims = SIZE_DIMS[size];

  return (
    <div className="fixed bottom-5 right-5 z-[1000] flex flex-col items-end gap-2">
      {open && (
        <div
          className="flex flex-col bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden transition-all duration-200"
          style={{ width: dims.width, height: dims.height }}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-slate-800 border-b border-slate-700 shrink-0">
            <div className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4 text-blue-400" />
              <span className="text-sm font-medium text-slate-200">Marine AI Assistant</span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={cycleSize}
                className="p-1 text-slate-500 hover:text-slate-300 transition-colors"
                title={`Switch to ${size === "compact" ? "expanded" : size === "expanded" ? "fullscreen" : "compact"}`}
              >
                {size === "fullscreen"
                  ? <Minimize2 className="h-3.5 w-3.5" />
                  : <Maximize2 className="h-3.5 w-3.5" />
                }
              </button>
              <button onClick={() => setOpen(false)} className="p-1 text-slate-500 hover:text-slate-300 transition-colors">
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-0">
            {messages.map((msg, i) => {
              const isLastAssistant = msg.role === "assistant" && i === messages.length - 1;
              return (
                <div key={i} className={clsx("flex", msg.role === "user" ? "justify-end" : "justify-start")}>
                  <div
                    className={clsx(
                      "max-w-[88%] rounded-lg px-3 py-2 text-xs leading-relaxed",
                      msg.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-slate-800 text-slate-300"
                    )}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>

                    {msg.risk && (
                      <div className="mt-2 pt-2 border-t border-slate-700 flex items-center gap-1.5">
                        <Activity className="h-3 w-3 text-slate-500" />
                        <span className="text-slate-500">Risk:</span>
                        <span className={clsx("font-medium", RISK_COLORS[msg.risk.level])}>
                          {msg.risk.score} — {msg.risk.level}
                        </span>
                      </div>
                    )}

                    {/* Developer trace link — only on last assistant message when trace was saved */}
                    {isLastAssistant && lastHasTrace && (
                      <div className="mt-2 pt-2 border-t border-slate-700">
                        <Link
                          href="/developer"
                          target="_blank"
                          className="flex items-center gap-1 text-slate-500 hover:text-blue-400 transition-colors text-xs"
                        >
                          <ExternalLink className="h-3 w-3" />
                          View agent trace
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-800 rounded-lg px-3 py-2 flex gap-1 items-center">
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-3 py-3 border-t border-slate-700 flex gap-2 shrink-0">
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask about vessels, faults, port calls…"
              disabled={loading}
              className="flex-1 bg-slate-800 text-slate-200 placeholder-slate-600 rounded-lg px-3 py-2 text-xs outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              onClick={send}
              disabled={!input.trim() || loading}
              className="p-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-4 w-4 text-white" />
            </button>
          </div>
        </div>
      )}

      {/* Toggle button */}
      <button
        onClick={() => setOpen((v) => !v)}
        className={clsx(
          "w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all",
          open ? "bg-slate-700 hover:bg-slate-600" : "bg-blue-600 hover:bg-blue-500"
        )}
      >
        {open ? <X className="h-5 w-5 text-white" /> : <MessageCircle className="h-5 w-5 text-white" />}
      </button>
    </div>
  );
}
