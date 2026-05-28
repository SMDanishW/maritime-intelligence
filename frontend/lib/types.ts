// ── Dashboard Summary ──────────────────────────────────────────────────────────
export interface DashboardSummary {
  vessels: {
    total: number;
    by_nav_status: Record<string, number>;
    sample: Array<{ mmsi: number; lat: number; lon: number; sog: number; heading: number; nav_status: string }>;
    updated_at: string | null;
  };
  port_calls: {
    total: number;
    by_port: Record<string, number>;
    recent: Array<{ vessel_name: string | null; port: string | null; arrival_time: string | null; departure_time: string | null }>;
    updated_at: string | null;
  };
  aton_faults: {
    total: number;
    open: number;
    by_type: Record<string, number>;
    faults: Array<{ aton_id: number | null; aton_name: string; state: string; lat: number; lon: number; fault_type: string; aton_type: string; fixed: boolean }>;
    updated_at: string | null;
  };
  winter_navigation: {
    vessels: Array<{ name: string; mmsi: number | null; vessel_type_code: number; active: boolean; current_activity: string | null }>;
    active_dirways: number;
    active_icebreakers: number;
    updated_at: string | null;
  };
  sea_state: {
    available: boolean;
    reason?: string;
    mqtt_broker?: string;
    topic_pattern?: string;
  };
  risk: {
    score: number;
    level: "Low" | "Medium" | "High" | "Critical";
    components: Array<{ name: string; score: number; weight: number; weighted: number; note: string }>;
  };
}

// ── Agent trace (developer view) ──────────────────────────────────────────────
export interface AgentTrace {
  node: string;
  output: Record<string, unknown>;
}

// ── Chat ───────────────────────────────────────────────────────────────────────
export interface ChatResponse {
  answer: string;
  in_scope: boolean;
  risk: {
    score: number;
    level: string;
    components: Array<{ name: string; score: number; weight: number; weighted: number; note: string }>;
  } | null;
  map_data: {
    markers: Array<{
      type: "vessel" | "aton_fault";
      lat: number;
      lon: number;
      label: string;
      detail: string;
      moving?: boolean;
    }>;
    center?: [number, number];
    zoom?: number;
  } | null;
  chart_data: {
    bar: Array<{ name: string; value: number }>;
    pie: Array<{ name: string; value: number }>;
  } | null;
  table_data: Array<Record<string, unknown>> | null;
  errors: string[] | null;
  trace: AgentTrace[] | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  risk?: ChatResponse["risk"];
}
