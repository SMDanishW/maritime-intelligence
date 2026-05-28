# API Reference

## Digitraffic Marine Endpoints Used

| Service | Endpoint | Description |
|---------|----------|-------------|
| AIS Locations | `GET /api/ais/v1/locations` | All vessel positions |
| AIS Single Vessel | `GET /api/ais/v1/locations/{mmsi}` | Single vessel position |
| Vessel Details | `GET /api/port-call/v1/vessel-details` | Vessel metadata |
| Port Calls | `GET /api/port-call/v1/port-calls` | All port call records |
| Ports | `GET /api/port-call/v1/ports` | Port list |
| Sea State | `GET /api/aton/v1/sea-states` | Buoy sea state readings |
| AtoN Faults | `GET /api/aton/v1/faults` | Navigation aid faults |
| Winter Dirways | `GET /api/winter-navigation/v1/dirways` | Ice navigation fairways |
| Winter Ships | `GET /api/winter-navigation/v1/ships` | Ice-assisted vessels |

Base URL: `https://meri.digitraffic.fi`
Authentication: None (public API)

## Backend Endpoints

### Phase 1 (Test)
- `GET /api/test/ais`
- `GET /api/test/vessels`
- `GET /api/test/port-calls`
- `GET /api/test/sea-state`
- `GET /api/test/aton-faults`
- `GET /api/test/winter-navigation`

### Phase 2 (Production)
- `GET /api/dashboard/summary`
- `GET /api/vessels/live`
- `GET /api/ports/calls`
- `GET /api/sea-state`
- `GET /api/aton/faults`
- `GET /api/winter-navigation`
- `GET /api/risk/summary`
- `POST /api/chat`
- `GET /health`
- `GET /metrics`
