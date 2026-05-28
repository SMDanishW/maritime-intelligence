# Architecture

## Overview

```
[Digitraffic Marine APIs] ──► [FastAPI Backend] ──► [PostgreSQL]
                                     │                    │
                                  [Redis]          [LangGraph Agent]
                                     │                    │
                              [Next.js Frontend] ◄────────┘
                                     │
                              [React Leaflet Map]
                              [Recharts Panels]
                              [Chat Widget]
```

## Agent Workflow

```
User Question
     │
     ▼
[Guardrail Agent] ──(out-of-scope)──► Fixed refusal response
     │ (in-scope)
     ▼
[Supervisor Agent]
     │
     ├──► [AIS Agent]
     ├──► [Port Call Agent]
     ├──► [Sea State Agent]
     ├──► [AtoN Fault Agent]
     ├──► [Winter Navigation Agent]
     │
     ▼
[Risk Scoring Agent]
     │
     ▼
[Visualization Agent]  ──► map markers, chart data, tables
     │
     ▼
[Response Writer Agent] ──► final JSON response
```

## Risk Score Formula

```
risk_score = (vessel_density   × 0.25)
           + (port_congestion  × 0.20)
           + (sea_state        × 0.25)
           + (aton_faults      × 0.15)
           + (winter_nav       × 0.15)

0-25:   Low
26-50:  Medium
51-75:  High
76-100: Critical
```
