"use client";
import { useState, useEffect, useCallback } from "react";
import { api } from "../lib/api";
import type { DashboardSummary, ChatResponse } from "../lib/types";
import { Header } from "../components/Header";
import { SummaryCards } from "../components/SummaryCards";
import { MarineMap } from "../components/MarineMap";
import { PortCallsPanel } from "../components/PortCallsPanel";
import { VesselActivityPanel } from "../components/VesselActivityPanel";
import { AtonFaultsPanel } from "../components/AtonFaultsPanel";
import { WinterNavPanel } from "../components/WinterNavPanel";
import { SeaStatePanel } from "../components/SeaStatePanel";
import { RiskPanel } from "../components/RiskPanel";
import { ChatWidget } from "../components/ChatWidget";

const REFRESH_INTERVAL_MS = 60_000;

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mapOverlay, setMapOverlay] = useState<ChatResponse["map_data"] | null>(null);
  const [chartOverlay, setChartOverlay] = useState<ChatResponse["chart_data"] | null>(null);

  const fetchData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const summary = await api.getDashboardSummary();
      setData(summary);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load dashboard data");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(true), REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Header
        lastUpdated={lastUpdated}
        refreshing={refreshing}
        onRefresh={() => fetchData(true)}
      />

      <main className="flex-1 p-4 space-y-4">
        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-2 text-sm">
            {error}
          </div>
        )}

        <SummaryCards data={data} loading={loading} />

        {/* Map — full width */}
        <MarineMap data={data} overlay={mapOverlay} />

        {/* Charts row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <PortCallsPanel data={data} loading={loading} />
          <VesselActivityPanel data={data} loading={loading} />
        </div>

        {/* Info panels row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <AtonFaultsPanel data={data} loading={loading} />
          <WinterNavPanel data={data} loading={loading} />
          <SeaStatePanel data={data} />
        </div>

        {/* Risk panel */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <RiskPanel data={data} loading={loading} />
        </div>
      </main>

      <ChatWidget
        onMapOverlay={setMapOverlay}
        onChartOverlay={setChartOverlay}
      />
    </div>
  );
}
