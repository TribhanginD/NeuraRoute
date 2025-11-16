# NeuraRoute Agentic System

A sophisticated AI-native logistics system powered by Groq LLMs that provides intelligent decision-making for inventory management, route optimization, and dynamic pricing.

## 🚀 Features

### 🤖 Intelligent Agents
- **Inventory Agent**: Manages stock levels, reordering, and expiry handling
- **Routing Agent**: Optimizes delivery routes and vehicle assignments
- **Pricing Agent**: Analyzes market conditions and adjusts pricing dynamically
- **Agent Manager**: Coordinates all agents and handles multi-agent decisions

### 🧠 LLM-Powered Decision Making
- Uses Groq's fast LLMs for real-time decision making
- Wraps Groq via AG2 (AutoGen) conversational agents for structured JSON decisions
- Structured JSON responses for consistent data handling
- Context-aware decisions based on current system state
- Multi-agent coordination for complex scenarios

### 📊 Real-time Monitoring
- Live agent status and health monitoring
- Comprehensive logging of all agent actions
- Action approval workflow
- System statistics and performance metrics

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Node.js 16+
- Supabase account
- Groq API key

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your credentials
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_anon_key
# GROQ_API_KEY=your_groq_api_key
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
```

### 3. Database Setup

Ensure your Supabase database has the following tables:
- `inventory`
- `orders`
- `fleet`
- `agent_logs`
- `agent_actions`
- `agent_decisions`

## 🚀 Running the System

### Start the Backend

```bash
cd backend

# Option 1: Run with FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Run agents only
python start_agents.py
```

### Start the Frontend

```bash
cd frontend
npm start
```

### Start Agents via API

```bash
# Start all agents
curl -X POST http://localhost:8000/api/v1/agents/start

# Check agent status
curl http://localhost:8000/api/v1/agents/status

# Get system health
curl http://localhost:8000/health
```

## 🤖 Agent Types

### Inventory Agent
Manages inventory levels and makes intelligent reordering decisions.

**Actions:**
- `check_low_stock`: Identifies items needing reorder
- `optimize_inventory`: Optimizes stock levels based on demand
- `handle_expired_items`: Manages items approaching expiry

**Example Trigger:**
```bash
curl -X POST "http://localhost:8000/api/v1/agents/trigger?agent_type=inventory&action=check_low_stock"
```

### Routing Agent
Optimizes delivery routes and assigns vehicles to orders.

**Actions:**
- `optimize_routes`: Creates optimal delivery routes
- `assign_vehicles`: Assigns vehicles to orders
- `handle_dynamic_routing`: Updates routes for in-progress deliveries

**Example Trigger:**
```bash
curl -X POST "http://localhost:8000/api/v1/agents/trigger?agent_type=routing&action=optimize_routes"
```

### Pricing Agent
Analyzes market conditions and adjusts pricing dynamically.

**Actions:**
- `analyze_market_conditions`: Analyzes market trends
- `optimize_inventory_pricing`: Adjusts prices based on demand
- `handle_dynamic_pricing`: Implements surge pricing for high-demand items

**Example Trigger:**
```bash
curl -X POST "http://localhost:8000/api/v1/agents/trigger?agent_type=pricing&action=analyze_market_conditions"
```

## 📊 API Endpoints

### Agent Management
- `POST /api/v1/agents/start` - Start all agents
- `POST /api/v1/agents/stop` - Stop all agents
- `GET /api/v1/agents/status` - Get agent status
- `POST /api/v1/agents/trigger` - Trigger specific agent action

### Monitoring
- `GET /health` - System health check
- `GET /api/v1/agents/logs` - Get agent logs
- `GET /api/v1/agents/actions` - Get agent actions
- `GET /api/v1/system/stats` - Get system statistics

## 🔧 Configuration

### Environment Variables

```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Groq LLM
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-8b-8192

# Agent Configuration
AGENT_UPDATE_INTERVAL=30
MAX_CONCURRENT_AGENTS=10

# Logging
LOG_LEVEL=INFO
```

### Agent Behavior

Agents run continuously and make decisions every 30 seconds by default. Each agent:

1. **Gathers Context**: Fetches current system state from Supabase
2. **Makes Decision**: Uses Groq LLM to analyze context and make decisions
3. **Executes Actions**: Updates database with decisions and actions
4. **Logs Activity**: Records all actions for monitoring

## 🧪 Testing

### Manual Testing

1. **Start the system**:
   ```bash
   # Backend
   cd backend && uvicorn app.main:app --reload
   
   # Frontend
   cd frontend && npm start
   ```

2. **Start agents**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/agents/start
   ```

3. **Monitor activity**:
   ```bash
   # Check logs
   curl http://localhost:8000/api/v1/agents/logs
   
   # Check actions
   curl http://localhost:8000/api/v1/agents/actions
   ```

### Trigger Specific Actions

```bash
# Inventory management
curl -X POST "http://localhost:8000/api/v1/agents/trigger?agent_type=inventory&action=check_low_stock"

# Route optimization
curl -X POST "http://localhost:8000/api/v1/agents/trigger?agent_type=routing&action=optimize_routes"

# Pricing analysis
curl -X POST "http://localhost:8000/api/v1/agents/trigger?agent_type=pricing&action=analyze_market_conditions"
```

## 📈 Monitoring

### Agent Logs
All agent actions are logged to the `agent_logs` table with:
- Agent ID and type
- Action performed
- Detailed context and reasoning
- Timestamp and status

### Action Tracking
Agent decisions are tracked in the `agent_actions` table:
- Action type and target
- Status (pending/approved/rejected)
- Execution details

### System Health
Monitor system health via:
- `/health` endpoint
- Agent status API
- Real-time logs

## 🔄 Multi-Agent Coordination

The system supports complex scenarios requiring multiple agents:

1. **Inventory-Routing Coordination**: Optimizes routes based on stock availability
2. **Pricing-Inventory Coordination**: Adjusts pricing based on inventory levels
3. **Routing-Pricing Coordination**: Optimizes delivery pricing based on routes

## 🚀 Deployment

### Docker Deployment

```bash
# Build backend
cd backend
docker build -t neuraroute-backend .

# Run backend
docker run -p 8000:8000 --env-file .env neuraroute-backend

# Build frontend
cd frontend
docker build -t neuraroute-frontend .

# Run frontend
docker run -p 3000:3000 neuraroute-frontend
```

### Production Considerations

1. **Environment Variables**: Use proper secrets management
2. **Database**: Use production Supabase instance
3. **Monitoring**: Add proper logging and monitoring
4. **Scaling**: Consider horizontal scaling for high load
5. **Security**: Implement proper authentication and authorization

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
1. Check the logs in Supabase
2. Review agent status via API
3. Check system health endpoint
4. Review agent coordination logs

The system is designed to be self-healing and will automatically restart failed agents. 
