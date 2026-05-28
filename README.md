# Finnish Marine Traffic Intelligence Platform

Real-time marine traffic intelligence dashboard for Finnish waterways powered by
[Digitraffic Marine APIs](https://www.digitraffic.fi/en/marine-traffic/),
FastAPI, LangGraph + Groq Cloud, and Next.js.

## What it does

- **Live dashboard** — vessels on a Leaflet map, port calls, sea state, AtoN faults, winter navigation, risk summary cards
- **AI chatbot** — domain-restricted agent (Finnish marine traffic only) backed by a 9-node LangGraph workflow and Groq Cloud LLM

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Agent | LangGraph + Groq Cloud (`llama-3.3-70b-versatile`) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Frontend | Next.js 14 App Router |
| Map | React Leaflet |
| Charts | Recharts |
| Container | Docker + Docker Compose |
| Kubernetes (local) | Minikube |
| Kubernetes (cloud) | AWS EKS |
| CI/CD | GitHub Actions + AWS ECR |

## Data Sources (Digitraffic Marine)

| Data | API path |
|------|----------|
| AIS vessel positions | `/api/ais/v1/locations` |
| Vessel metadata | `/api/port-call/v1/vessel-details` |
| Port calls | `/api/port-call/v1/port-calls` |
| Sea state | `/api/aton/v1/sea-states` |
| AtoN faults | `/api/aton/v1/faults` |
| Winter navigation | `/api/winter-navigation/v1/dirways` |

All APIs are public — no authentication required.

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd marine-traffic-intelligence

# 2. Backend
cd backend
pip install -e ".[dev]"
cp .env.example .env        # add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000 (dashboard) and http://localhost:8000/docs (Swagger).

## Docker Compose

```bash
cp backend/.env.example backend/.env   # add GROQ_API_KEY
docker compose up --build
```

## Build Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Repository scaffold | ✅ Done |
| 1 | Digitraffic API testing | ⬜ Next |
| 2 | Backend core endpoints + DB + Redis | ⬜ |
| 3 | LangGraph agent workflow | ⬜ |
| 4 | Frontend dashboard + chat widget | ⬜ |
| 5 | Dockerization | ⬜ |
| 6 | CI/CD (GitHub Actions + ECR) | ⬜ |
| 7 | Minikube deployment | ⬜ |
| 8 | Observability (Prometheus + Grafana) | ⬜ |
| 9 | AWS EKS deployment | ⬜ |

## Environment Variables

See [`backend/.env.example`](backend/.env.example) and [`frontend/.env.example`](frontend/.env.example).

## Agent Guardrails

The chatbot answers **only** Finnish marine traffic questions. Out-of-scope requests receive:

> *I can only answer questions related to Finnish marine traffic using the available marine traffic data...*

## Docs

- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment-guide.md)
