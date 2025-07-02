# NeuraRoute - AI-Native Hyperlocal Logistics System

An intelligent operating system for small city sectors, featuring autonomous agents, demand forecasting, and real-time logistics optimization with **agentic AI capabilities** for autonomous decision-making and action-taking.

## 🚀 Features

### Core System
- **LCM-Style Demand Forecaster**: AI-powered demand prediction using structured context
- **LAM-Style Autonomous Agents**: Goal-driven planners executing toolchains
- **🆕 Agentic AI System**: Autonomous decision-making with approval workflows
- **15-Minute Tick Simulation**: Real-time state updates in local database
- **Professional Frontend**: Modern UI with merchant chat, ops console, live route map, agent logs, and simulation playback

### AI/ML Capabilities
- **Intelligent Demand Forecasting**: Weather, events, historical data, seasonal factors
- **Autonomous Agent Coordination**: Restock, Route, Pricing, Dispatch, Forecasting agents
- **🆕 Agentic Decision Making**: LangChain agents with function-calling for autonomous actions
- **Real-time Route Optimization**: Dynamic fleet management and route planning
- **Predictive Analytics**: Market condition analysis and trend prediction

### 🆕 Agentic AI Features
- **Autonomous Action Taking**: Agents can place orders, reroute drivers, update inventory, adjust pricing, and dispatch fleet
- **Smart Approval Workflows**: Automatic approval for low-risk actions, manual approval for high-value decisions
- **Market Day Simulations**: Predefined scenarios for testing and demonstration
- **Real-time Action Monitoring**: Live tracking of agent decisions and their impact
- **Comprehensive Audit Trail**: Complete history of all actions, approvals, and executions

### Frontend Components
- **Merchant Chat Interface**: Real-time communication with merchants
- **Operations Console**: Centralized control and monitoring
- **🆕 Agentic Dashboard**: Action approval interface and simulation controls
- **Live Route Map**: Real-time fleet tracking and route visualization
- **Agent Monitor**: Live agent status and performance metrics
- **Simulation Playback**: Historical data review and analysis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Redis Cache   │◄─────────────┘
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   AI/ML Engine  │
                        │   (LangChain)   │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │ 🆕 Agentic AI   │
                        │   System        │
                        └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL** for primary database
- **Redis** for caching and session management
- **LangChain** for AI/ML orchestration
- **🆕 LangChain Agents** for autonomous decision-making
- **FAISS/Chroma** for vector memory
- **SQLAlchemy** for ORM
- **Pydantic** for data validation

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Mapbox/Leaflet** for mapping
- **React Query** for data fetching
- **Zustand** for state management
- **🆕 Agentic UI Components** for action approval and simulation

### AI/ML
- **GPT-4o** and **Anthropic Claude** for reasoning
- **🆕 Function Calling** for autonomous action execution
- **Prophet** for time series forecasting
- **YOLO** for traffic analysis
- **BERT/RoBERTa** for sentiment analysis
- **Graph Neural Networks** for route optimization
- **Stable Baselines3** for reinforcement learning

## 📦 Installation

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- **🆕 OpenAI API key or Anthropic API key**

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd NeuraRoute

# Copy environment template
cp .env.example .env

# Configure AI API keys
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env

# Start all services
./start.sh

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# 🆕 Agentic Dashboard: http://localhost:3000/agentic
```

### Manual Setup
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install

# Database setup
docker-compose up -d postgres redis
python backend/scripts/init_db.py
```

## 🚀 Usage

### Starting the System
```bash
# Start all services
./start.sh

# Or manually
docker-compose up -d
cd backend && python main.py
cd frontend && npm start
```

### 🆕 Agentic AI Usage

#### Process a Situation
```bash
curl -X POST http://localhost:8000/api/v1/agentic/process-situation \
  -H "Content-Type: application/json" \
  -d '{
    "inventory": [
      {"sku_name": "Fresh Bread", "quantity": 15, "reorder_threshold": 20}
    ],
    "demand_forecast": [
      {"sku_name": "Fresh Bread", "predicted_demand": 30}
    ],
    "deliveries": [
      {"driver_id": "DRV_001", "status": "in_transit", "estimated_arrival": "10:30"}
    ],
    "market_conditions": {
      "weather": "Sunny",
      "events": "Local farmers market",
      "traffic": "Moderate"
    }
  }'
```

#### Run Market Day Simulation
```bash
# Start simulation
curl -X POST "http://localhost:8000/api/v1/agentic/simulation/start?scenario_name=normal_market_day&speed=1.0"

# Run simulation steps
curl -X POST http://localhost:8000/api/v1/agentic/simulation/step

# Get pending actions
curl http://localhost:8000/api/v1/agentic/pending-actions

# Approve an action
curl -X POST http://localhost:8000/api/v1/agentic/actions/{action_id}/approve
```

### Simulation Control
1. Access the Operations Console at `http://localhost:3000`
2. Use the Simulation Control panel to start/stop the 15-minute tick loop
3. **🆕 Use the Agentic Dashboard for autonomous action approval**
4. Monitor agent performance in the Agent Monitor
5. View live routes on the Fleet Map
6. Chat with merchants through the Merchant Chat interface

### API Endpoints
- `GET /api/v1/health` - System health check
- `GET /api/v1/agents` - List all agents
- `POST /api/v1/simulation/start` - Start simulation
- `POST /api/v1/simulation/stop` - Stop simulation
- `GET /api/v1/forecast` - Get demand forecast
- `GET /api/v1/routes` - Get current routes

### 🆕 Agentic API Endpoints
- `POST /api/v1/agentic/process-situation` - Process situation and generate actions
- `GET /api/v1/agentic/pending-actions` - Get actions requiring approval
- `POST /api/v1/agentic/actions/{id}/approve` - Approve an action
- `POST /api/v1/agentic/actions/{id}/deny` - Deny an action
- `GET /api/v1/agentic/action-history` - Get complete action history
- `GET /api/v1/agentic/simulation/scenarios` - Get available simulation scenarios
- `POST /api/v1/agentic/simulation/start` - Start simulation
- `POST /api/v1/agentic/simulation/auto-run` - Auto-run complete simulation

## 🤖 AI/ML Features

### Demand Forecasting (LCM-Style)
- **Structured Context Building**: Weather, events, historical data, seasonal factors
- **AI Reasoning**: GPT-4o and Claude for demand prediction
- **Fallback Heuristics**: Rule-based forecasting when AI unavailable
- **Real-time Updates**: 15-minute intervals with context refresh

### Autonomous Agents (LAM-Style)
- **Goal-Driven Planning**: Each agent has specific objectives and constraints
- **Toolchain Execution**: Agents use specialized tools for their domain
- **Memory Management**: Persistent memory with vector storage
- **Health Monitoring**: Automatic restart on failure

### 🆕 Agentic AI System
- **Autonomous Decision Making**: LangChain agents with function-calling capabilities
- **Smart Approval Workflows**: Automatic approval for low-risk actions, manual approval for high-value decisions
- **Tool Integration**: place_order, reroute_driver, update_inventory, adjust_pricing, dispatch_fleet
- **Market Day Simulations**: Predefined scenarios for testing and demonstration
- **Real-time Action Monitoring**: Live tracking of agent decisions and their impact

### Agent Types
1. **Restock Agent**: Inventory management and replenishment
2. **Route Agent**: Dynamic route optimization
3. **Pricing Agent**: Dynamic pricing based on demand
4. **Dispatch Agent**: Fleet coordination and task assignment
5. **Forecasting Agent**: Demand prediction and trend analysis
6. **🆕 Agentic System**: Autonomous decision-making and action-taking

## 📊 Monitoring & Analytics

### Real-time Metrics
- Agent performance and health
- Fleet utilization and efficiency
- Demand forecast accuracy
- Route optimization metrics
- System resource usage
- **🆕 Agentic action approval rates and execution success**

### Logging
- Structured JSON logging
- Agent action logs
- Error tracking and alerting
- Performance analytics
- **🆕 Complete audit trail of agentic decisions**

## 🔒 Security

### Authentication
- JWT-based authentication
- Role-based access control
- API key management

### Data Protection
- Encrypted data transmission
- Secure database connections
- Environment variable management

### 🆕 Agentic Security
- **Approval Workflows**: All high-value actions require manual approval
- **Audit Trail**: Complete history of all decisions and approvals
- **Input Validation**: Comprehensive validation of all agentic actions
- **Rate Limiting**: Protection against abuse of autonomous systems

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/

# 🆕 Test agentic system specifically
pytest tests/test_agentic_system.py -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### 🆕 Agentic System Testing
```bash
# Test simulation scenarios
curl -X POST "http://localhost:8000/api/v1/agentic/simulation/auto-run?scenario_name=normal_market_day"

# Test tool execution
curl -X POST http://localhost:8000/api/v1/agentic/tools/place_order/execute \
  -H "Content-Type: application/json" \
  -d '{"supplier_id": "SUP_001", "sku_id": "SKU_001", "quantity": 100}'
```

## 📚 Documentation

- **🆕 [Agentic System Documentation](backend/AGENTIC_SYSTEM.md)** - Comprehensive guide to the agentic AI system
- **API Documentation**: Available at `http://localhost:8000/docs`
- **Frontend TypeScript Interfaces**: `frontend/src/types/agentic.ts`

## 🚀 Quick Demo

### 1. Start the System
```bash
./start.sh
```

### 2. Run Market Day Simulation
```bash
# Auto-run a complete market day simulation
curl -X POST "http://localhost:8000/api/v1/agentic/simulation/auto-run?scenario_name=high_demand_day&speed=2.0"
```

### 3. Monitor Actions
```bash
# Check for pending actions
curl http://localhost:8000/api/v1/agentic/pending-actions

# View action history
curl http://localhost:8000/api/v1/agentic/action-history
```

### 4. Access the Dashboard
- Open `http://localhost:3000/agentic` in your browser
- View real-time agentic actions and approvals
- Monitor simulation progress
- Approve or deny pending actions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [Agentic System Documentation](backend/AGENTIC_SYSTEM.md)
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions and ideas 