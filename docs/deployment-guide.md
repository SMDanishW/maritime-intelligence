# Deployment Guide

## Local Development

```bash
# Backend
cd backend
pip install -e ".[dev]"
cp .env.example .env   # fill in GROQ_API_KEY
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Docker Compose

```bash
cp backend/.env.example backend/.env   # fill in GROQ_API_KEY
cp frontend/.env.example frontend/.env
docker compose up --build
```

Frontend: http://localhost:3000
Backend:  http://localhost:8000/docs

## Minikube (Phase 7)

```bash
minikube start
kubectl apply -f k8s/minikube/
kubectl get pods -n marine-traffic
```

## AWS EKS (Phase 9)

See `k8s/aws/` manifests and Phase 9 instructions.
