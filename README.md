# Finnish Marine Traffic Intelligence Platform

> Real-time AI-powered marine traffic dashboard for Finnish waterways — built end-to-end with FastAPI, LangGraph, Groq Cloud, Next.js, and deployed on AWS EKS via GitHub Actions CI/CD.

Live data from [Digitraffic Marine APIs](https://www.digitraffic.fi/en/marine-traffic/) — no authentication required.

---

## What it does

- **Live vessel map** — AIS positions of all vessels in Finnish waters, rendered on an interactive Leaflet map with speed, heading, and nav-status overlays
- **Port call tracker** — real-time arrivals, departures, and port call history
- **Sea state & AtoN faults** — live buoy fault alerts and sea condition monitoring
- **Winter navigation** — active fairway directives updated in real time
- **Risk summary cards** — aggregated intelligence cards surfacing anomalies and alerts
- **AI chatbot** — domain-restricted conversational agent backed by a 6-node LangGraph workflow, Groq Cloud LLM (`llama-3.3-70b-versatile`), per-node trace capture, and hard guardrails (Finnish marine traffic only)
- **Developer trace view** — live pipeline visualization showing each agent node's reasoning, color-coded by type

---

## Architecture

```
User → Next.js (SSR) → /api/* proxy route
                      ↓
               FastAPI + Uvicorn
                      ↓
          ┌───────────────────────┐
          │  LangGraph StateGraph │
          │  guardrail → supervisor│
          │  → fetch_domains      │
          │  → risk_agent         │
          │  → visualization      │
          │  → response_writer    │
          └───────────────────────┘
                      ↓
          Groq Cloud (llama-3.3-70b)
                      ↓
          Redis (response cache) + PostgreSQL
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn (Python 3.11) |
| AI Agent | LangGraph `StateGraph` + Groq Cloud |
| LLM | `llama-3.3-70b-versatile` via langchain-groq |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Frontend | Next.js 14 App Router (TypeScript) |
| Map | React Leaflet (SSR-disabled) |
| Charts | Recharts |
| Containerization | Docker + Docker Compose |
| Kubernetes | AWS EKS (managed node groups) |
| Container Registry | AWS ECR |
| CI/CD | GitHub Actions (lint → test → bootstrap → deploy) |
| Load Balancer | AWS ALB via Helm (aws-load-balancer-controller) |
| IaC | eksctl + CloudFormation |

---

## Data Sources (Digitraffic Marine — all public)

| Dataset | Endpoint |
|---|---|
| AIS vessel positions | `/api/ais/v1/locations` |
| Vessel metadata | `/api/port-call/v1/vessel-details` |
| Port calls | `/api/port-call/v1/port-calls` |
| Sea state | `/api/aton/v1/sea-states` |
| AtoN faults | `/api/aton/v1/faults` |
| Winter navigation | `/api/winter-navigation/v1/dirways` |

---

## Quick Start (local)

```bash
# Clone
git clone <repo-url> && cd maritime-intelligence

# Backend
cd backend
pip install -r requirements-dev.txt
cp .env.example .env        # add GROQ_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Dashboard → http://localhost:3000  
Swagger UI → http://localhost:8000/docs

---

## Docker Compose (full stack)

```bash
cp backend/.env.example backend/.env   # add GROQ_API_KEY
docker compose up --build
```

Starts: PostgreSQL · Redis · FastAPI backend · Next.js frontend

---

## CI/CD Pipeline (GitHub Actions)

```
push to main
  ├── backend-ci   → ruff lint + pytest (Redis service container)
  ├── frontend-ci  → tsc --noEmit + next build
  └── bootstrap    → ECR repos + EKS cluster + managed node group
                     + ALB controller (Helm) + k8s manifests
        └── deploy → Docker build → ECR push → kubectl rollout
```

All AWS infra is idempotent — safe to re-run on every push.

---

## Agent Guardrails

The chatbot answers **only** Finnish marine traffic questions. Off-topic requests receive:

> *"I can only answer questions related to Finnish marine traffic using the available marine traffic data."*

Guardrail is enforced at the first node in the LangGraph pipeline before any tool calls or LLM invocations.

---

## Build Phases

| Phase | Description | Status |
|---|---|---|
| 0 | Repository scaffold | ✅ |
| 1 | Digitraffic API integration | ✅ |
| 2 | Backend core endpoints + DB + Redis | ✅ |
| 3 | LangGraph agent + Groq Cloud | ✅ |
| 4 | Frontend dashboard + AI chat widget | ✅ |
| 5 | Dockerization + Docker Compose | ✅ |
| 6 | GitHub Actions CI/CD + ECR | ✅ |
| 7 | Kubernetes manifests (EKS) | ✅ |
| 8 | AWS EKS deployment + ALB ingress | 🔄 In progress |
| 9 | Observability (Prometheus + Grafana) | ⬜ |

---

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `GROQ_API_KEY` | backend `.env` + GitHub Secret | Groq Cloud API key |
| `DATABASE_URL` | backend `.env` | PostgreSQL connection string |
| `REDIS_URL` | backend `.env` | Redis connection string |
| `BACKEND_URL` | frontend (runtime) | Internal service URL for API proxy |
| `AWS_ACCESS_KEY_ID` | GitHub Secret | AWS credentials for ECR/EKS |
| `AWS_SECRET_ACCESS_KEY` | GitHub Secret | AWS credentials |
| `AWS_REGION` | GitHub Secret | e.g. `eu-north-1` |
| `AWS_ACCOUNT_ID` | GitHub Secret | 12-digit AWS account ID |
| `EKS_CLUSTER_NAME` | GitHub Secret | EKS cluster name |
