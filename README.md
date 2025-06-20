# NeuraRoute - AI-Native Hyperlocal Logistics System

An intelligent operating system for small city sector logistics, featuring autonomous AI agents, demand forecasting, and real-time optimization.

## 🚀 Features

### 1. AI-Powered Demand Forecasting
- **LCM-style forecasting** using structured context (weather, events, sales history)
- **Context builder** for GPT-4o/Claude input with weather, events, seasonal factors
- **SKU-level predictions** with confidence intervals and AI reasoning
- **Fallback heuristics** when AI services are unavailable

### 2. Autonomous AI Agents
- **Modular LAM-style agents** with goal-driven planning
- **Agent types**: Restock, Route, Pricing, Dispatch, Forecasting
- **Memory management** with FAISS/Chroma integration
- **Error handling** with retry logic and escalation
- **Real-time monitoring** and health checks

### 3. Simulation Engine
- **15-minute tick simulation** with configurable speed
- **Agent coordination** and event processing
- **State persistence** in PostgreSQL
- **Real-time logging** of all agent actions

### 4. Professional Frontend
- **Modern React UI** with Tailwind CSS
- **Live dashboard** with real-time metrics
- **Agent monitoring** with logs and controls
- **Fleet map** (Mapbox integration ready)
- **Inventory management** with search and filtering
- **Merchant chat interface** with AI assistant

## 🏗️ Architecture

```
NeuraRoute/
├── backend/                 # FastAPI + Python backend
│   ├── app/
│   │   ├── agents/         # Autonomous AI agents
│   │   ├── forecasting/    # Demand forecasting engine
│   │   ├── models/         # Database models
│   │   ├── api/           # REST API endpoints
│   │   ├── simulation/    # Simulation engine
│   │   └── core/          # Configuration & database
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React + Tailwind UI
│   ├── src/
│   │   ├── components/    # React components
│   │   └── ...
│   ├── package.json
│   └── Dockerfile
├── database/              # Database initialization
├── docker-compose.yml     # Local deployment
├── start.sh              # Quick start script
└── README.md
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, LangChain
- **Database**: PostgreSQL, Redis
- **AI**: OpenAI GPT-4o, Anthropic Claude, LangChain
- **Frontend**: React, Tailwind CSS, Mapbox GL JS
- **Deployment**: Docker, Docker Compose
- **Monitoring**: Structured logging, health checks

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (optional)
- Anthropic API key (optional)
- Mapbox token (optional)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd NeuraRoute
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your API keys
```

### 3. Start the System
```bash
./start.sh
```

Or manually:
```bash
# Start database and Redis
docker-compose up -d postgres redis

# Start backend
docker-compose up -d backend

# Start frontend
docker-compose up -d frontend
```

### 4. Access the System
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 System Components

### Autonomous Agents

#### Restock Agent
- Monitors inventory levels across locations
- Generates restock recommendations using AI
- Executes restock actions automatically
- Considers demand forecasts and lead times

#### Route Agent
- Optimizes delivery routes using AI
- Considers traffic, weather, and vehicle capacity
- Implements TSP-like algorithms with real-time updates
- Provides route efficiency scoring

#### Pricing Agent
- Dynamic pricing based on demand forecasts
- Market condition analysis
- Competitive pricing strategies
- Revenue optimization

#### Dispatch Agent
- Fleet management and task assignment
- Real-time delivery monitoring
- Vehicle utilization optimization
- Emergency rerouting capabilities

#### Forecasting Agent
- Coordinates demand forecasting across SKUs
- Manages forecast accuracy and updates
- Integrates multiple data sources
- Provides forecast explanations

### API Endpoints

#### Simulation Control
- `GET /api/v1/simulation/status` - Get simulation status
- `POST /api/v1/simulation/start` - Start simulation
- `POST /api/v1/simulation/stop` - Stop simulation
- `POST /api/v1/simulation/reset` - Reset simulation
- `PUT /api/v1/simulation/speed` - Set simulation speed

#### Agent Management
- `GET /api/v1/agents/` - List all agents
- `GET /api/v1/agents/{id}` - Get agent details
- `POST /api/v1/agents/{id}/start` - Start agent
- `POST /api/v1/agents/{id}/stop` - Stop agent
- `GET /api/v1/agents/{id}/logs` - Get agent logs

#### Inventory Management
- `GET /api/v1/inventory/items` - List inventory items
- `GET /api/v1/inventory/skus` - List SKUs
- `GET /api/v1/inventory/locations` - List locations
- `GET /api/v1/inventory/summary` - Get inventory summary

#### Fleet Management
- `GET /api/v1/fleet/vehicles` - List vehicles
- `GET /api/v1/fleet/routes` - List routes
- `GET /api/v1/fleet/summary` - Get fleet summary

#### Forecasting
- `GET /api/v1/forecasting/forecasts` - List forecasts
- `POST /api/v1/forecasting/generate` - Generate forecast
- `GET /api/v1/forecasting/accuracy` - Get accuracy metrics

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U neuraroute -d neuraroute

# View logs
docker-compose logs -f backend
```

## 📈 Monitoring

### Health Checks
- Backend health: `GET /health`
- Database connectivity
- Redis connectivity
- Agent status monitoring

### Logging
- Structured JSON logging
- Agent action logging
- Error tracking and alerting
- Performance metrics

### Metrics
- Simulation performance
- Agent response times
- Forecast accuracy
- System utilization

## 🔒 Security

- Environment-based configuration
- API key management
- Database connection security
- CORS configuration
- Input validation and sanitization

## 🚀 Deployment

### Local Development
- Docker Compose for local deployment
- Hot reloading for development
- Sample data initialization

### Production Considerations
- Environment-specific configurations
- Database backups and recovery
- Monitoring and alerting
- Load balancing
- SSL/TLS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the health endpoint at `/health`
3. Check the logs: `docker-compose logs -f`
4. Open an issue in the repository

---

**NeuraRoute** - Intelligent logistics for the modern world. 