"use client";
import { useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from "react-leaflet";
import type { DashboardSummary, ChatResponse } from "../lib/types";
import "leaflet/dist/leaflet.css";

const FINLAND_CENTER: [number, number] = [63.5, 25.0];
const DEFAULT_ZOOM = 5;

function MapRecenter({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [map, center, zoom]);
  return null;
}

interface MarineMapInnerProps {
  data: DashboardSummary | null;
  overlay: ChatResponse["map_data"] | null;
}

export function MarineMapInner({ data, overlay }: MarineMapInnerProps) {
  const center = overlay?.center ?? FINLAND_CENTER;
  const zoom = overlay?.zoom ?? DEFAULT_ZOOM;

  const vesselMarkers = overlay
    ? overlay.markers.filter((m) => m.type === "vessel")
    : data?.vessels.sample ?? [];

  const faultMarkers = overlay
    ? overlay.markers.filter((m) => m.type === "aton_fault")
    : (data?.aton_faults.faults ?? [])
        .filter((f) => f.state === "Open")
        .map((f) => ({ lat: f.lat, lon: f.lon, label: f.aton_name, detail: f.fault_type, type: "aton_fault" as const, moving: false }));

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: "100%", width: "100%", background: "#0f172a" }}
      className="rounded-lg"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        className="opacity-60"
      />
      <MapRecenter center={center} zoom={zoom} />

      {/* Vessel markers */}
      {vesselMarkers.map((v, i) => {
        const lat = "lat" in v ? v.lat : 0;
        const lon = "lon" in v ? v.lon : 0;
        const label = "label" in v ? v.label : `MMSI ${"mmsi" in v ? (v as { mmsi: number }).mmsi : i}`;
        const detail = "detail" in v ? v.detail : `SOG: ${"sog" in v ? (v as { sog: number }).sog : "?"}kn`;
        const moving = "moving" in v ? v.moving : ("sog" in v ? (v as { sog: number }).sog > 0.5 : false);
        return (
          <CircleMarker
            key={`v-${i}`}
            center={[lat, lon]}
            radius={5}
            pathOptions={{
              color: moving ? "#60a5fa" : "#94a3b8",
              fillColor: moving ? "#3b82f6" : "#64748b",
              fillOpacity: 0.85,
              weight: 1,
            }}
          >
            <Tooltip>{label} — {detail}</Tooltip>
          </CircleMarker>
        );
      })}

      {/* AtoN fault markers */}
      {faultMarkers.map((f, i) => (
        <CircleMarker
          key={`f-${i}`}
          center={[f.lat, f.lon]}
          radius={6}
          pathOptions={{
            color: "#f97316",
            fillColor: "#ea580c",
            fillOpacity: 0.9,
            weight: 1.5,
          }}
        >
          <Tooltip>{f.label} — {f.detail}</Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
