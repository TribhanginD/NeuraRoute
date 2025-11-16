# NeuraRoute - AI-Native Hyperlocal Logistics System

An intelligent operating system for city-scale logistics that blends autonomous agents, live routing, and inventory controls. The stack now runs entirely on a self-contained SQLite/SQLAlchemy backend with Groq-backed agentic reasoning—no Supabase required.

## Features

- Autonomous agents for inventory, routing, and pricing (Groq + AutoGen/AG2).
- Agentic dashboard with human approvals for actions.
- Purchase/disposal order workflow instead of direct inventory edits.
- Live fleet/map view (Leaflet) with seeded realistic data.
- Local SQL store seeded automatically; optional Postgres via `DATABASE_URL`.

## Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   SQL Database  │    │   Redis Cache   │
│   (React)       │◄──►│   (SQLite)      │◄──►│   (Caching)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   AI/ML Engine  │◄─────────────┘
                        │   (AutoGen/Groq)│
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │ Agentic AI     │
                        │ + Orders       │
                        └─────────────────┘
```

## Tech Stack

- Backend: FastAPI, SQLAlchemy (SQLite by default), Uvicorn.
- Agentic: AutoGen/AG2 with Groq model (OpenAI-compatible), code execution disabled.
- Frontend: React 18 + TypeScript, react-query, Tailwind, Leaflet.
- Data: SQLite seed with realistic fleet/orders/inventory/routes; Postgres supported via `DATABASE_URL`.

## Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional; Redis optional)

### Environment (backend)
`backend/.env` is optional. Defaults:
- `DATABASE_URL=sqlite:///./neuraroute.db`
- `AUTO_START_AGENTS=false` (set true to auto-run agents)
- `SIMULATION_ENABLED=false` (simulation disabled)
- `AGENT_UPDATE_INTERVAL=300` (seconds between autonomous cycles)
- `GROQ_API_KEY`, `GROQ_MODEL` (required for real LLM calls)

### Environment (frontend)
`frontend/.env`:
```
HOST=localhost
PORT=3000
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws/agent-actions
REACT_APP_MAPBOX_TOKEN=your_mapbox_token_here
```

### Install & Run
Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm start
```

### Database
- On first start, `neuraroute.db` is created and seeded from `backend/app/db/sample_data.py`.
- To reset with fresh seed:
```bash
cd backend
rm -f neuraroute.db
python -m app.db.init_db
```
- To use Postgres: set `DATABASE_URL=postgresql://user:pass@host:port/dbname` and restart; schema is auto-created.

## Key Endpoints (backend)
- Agents: `/api/v1/agents/status`, `/api/v1/agents/start`, `/api/v1/agents/stop`, `/api/v1/agents/actions`
- Inventory/Fleet/Orders: `/api/v1/inventory`, `/api/v1/fleet`, `/api/v1/routes`, `/api/v1/orders`
- Orders workflow: `/api/v1/purchase-orders`, `/api/v1/disposal-orders`
- Simulation: `/api/v1/simulation/*` (returns “disabled” unless `SIMULATION_ENABLED=true`)

## Notes
- Agents are LLM-driven demos; they rely on the seeded data unless you replace it with your own.
- Host checks are relaxed in `npm start` for local dev; lock down for production.
- If you don’t want autonomous runs, keep `AUTO_START_AGENTS=false` and trigger manually via the API.
