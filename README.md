# NeuraRoute - AI-Native Hyperlocal Logistics System

An intelligent operating system for small city sectors, featuring autonomous agents, demand forecasting, and real-time logistics optimization with **agentic AI capabilities** for autonomous decision-making and action-taking.

##  Features

### Core System
- **LCM-Style Demand Forecaster**: AI-powered demand prediction using structured context
- **LAM-Style Autonomous Agents**: Goal-driven planners executing toolchains
<<<<<<< Updated upstream
- **Agentic AI System**: Autonomous decision-making with approval workflows
- **15-Minute Tick Simulation**: Real-time state updates in Supabase
=======
- **🆕 Agentic AI System**: Autonomous decision-making with approval workflows
- **15-Minute Tick Simulation**: Real-time state updates in the local SQL store
>>>>>>> Stashed changes
- **Professional Frontend**: Modern UI with merchant chat, ops console, live route map, agent logs, and simulation playback

### AI/ML Capabilities
- **Intelligent Demand Forecasting**: Weather, events, historical data, seasonal factors
- **Autonomous Agent Coordination**: Restock, Route, Pricing, Dispatch, Forecasting agents
- **Agentic Decision Making**: LangChain agents with function-calling for autonomous actions
- **Real-time Route Optimization**: Dynamic fleet management and route planning
- **Predictive Analytics**: Market condition analysis and trend prediction

### Agentic AI Features
- **Autonomous Action Taking**: Agents can place orders, reroute drivers, update inventory, adjust pricing, and dispatch fleet
- **Smart Approval Workflows**: Automatic approval for low-risk actions, manual approval for high-value decisions
- **Market Day Simulations**: Predefined scenarios for testing and demonstration
- **Real-time Action Monitoring**: Live tracking of agent decisions and their impact
- **Comprehensive Audit Trail**: Complete history of all actions, approvals, and executions
- **Realistic Business Workflow**: Purchase orders and disposal orders instead of direct inventory manipulation

### Purchase Order & Disposal Order System
- **Purchase Orders**: Agents create purchase orders for inventory increases (restock, reorder, new items)
- **Disposal Orders**: Agents create disposal orders for inventory decreases (clearance, discontinuation)
- **Order Tracking**: Complete order lifecycle with status tracking (pending, ordered, shipped, received, cancelled)
- **Realistic Inventory Management**: Professional workflow that mirrors real business operations
- **Order Details**: Comprehensive order information including quantities, delivery dates, locations, and reasons

### Frontend Components
- **Operations Console**: Centralized control and monitoring
- **Agentic Dashboard**: Action approval interface and simulation controls
- **Live Route Map**: Real-time fleet tracking and route visualization
- **Agent Monitor**: Live agent status and performance metrics
- **Simulation Playback**: Historical data review and analysis

##  Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   SQL Database  │    │   Redis Cache   │
│   (React)       │◄──►│   (SQLite)      │◄──►│   (Caching)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   AI/ML Engine  │◄─────────────┘
                        │   (LangChain)   │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │ � Agentic AI   │
                        │   System        │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │  Purchase &    │
                        │   Disposal      │
                        │   Orders        │
                        └─────────────────┘
```

##  Tech Stack

### Data Layer
- **SQLite + SQLAlchemy** for the primary transactional store
- **Redis** for caching and session management

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Mapbox/Leaflet** for mapping
- **React Query** for data fetching
- **Zustand** for state management
<<<<<<< Updated upstream
- ** Agentic UI Components** for action approval and simulation
- **Supabase JS Client** for database operations

### AI/ML
- **GPT-4o** and **Anthropic Claude** for reasoning
- ** Function Calling** for autonomous action execution
=======
- **🆕 Agentic UI Components** for action approval and simulation

### AI/ML
- **GPT-4o** and **Anthropic Claude** for reasoning
- **🆕 Function Calling** for autonomous action execution
- **🆕 AG2 (AutoGen) Conversable Agents** coordinating Groq-backed structured decisions
>>>>>>> Stashed changes
- **Prophet** for time series forecasting
- **YOLO** for traffic analysis
- **BERT/RoBERTa** for sentiment analysis
- **Graph Neural Networks** for route optimization
- **Stable Baselines3** for reinforcement learning

##  Installation

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
<<<<<<< Updated upstream
- ** Supabase account and project**
- ** OpenAI API key or Anthropic API key**
=======
- **🆕 OpenAI API key or Anthropic API key**
>>>>>>> Stashed changes

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd NeuraRoute

# Copy environment template
cp .env.example .env

# Configure AI API keys (optional)
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env

# Start services
./start.sh

# Access the application
# Frontend: http://localhost:3000
# Agentic Dashboard: http://localhost:3000/agentic
```

### Manual Setup
```bash
# Backend setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend setup (in a new terminal)
cd frontend
npm install
npm start
```

<<<<<<< Updated upstream
##  Usage
=======
### Backend Environment Variables
Create `backend/.env` (optional) to override defaults:

```bash
# Change the path or switch to Postgres by updating the URL
DATABASE_URL=sqlite:///./neuraroute.db
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-8b-8192
AUTO_START_AGENTS=true
AUTO_START_SIMULATION=true
```

`AUTO_START_AGENTS` and `AUTO_START_SIMULATION` can be set to `false` if you prefer to manually control their lifecycle via the API.

## 🚀 Usage
>>>>>>> Stashed changes

### Starting the System
```bash
# Start all services
./start.sh

# Or manually
docker-compose up -d redis
cd frontend && npm start
```

### Agentic AI Usage

#### Process a Situation
The agentic system can process situations through the frontend interface:

1. Navigate to the Agentic Dashboard at `http://localhost:3000/agentic`
2. Use the interface to input situation data
3. Review and approve/deny agent actions
4. Monitor the impact of decisions in real-time

#### Run Market Day Simulation
1. Access the Operations Console at `http://localhost:3000`
2. Use the Simulation Control panel to start/stop the 15-minute tick loop
3. ** Use the Agentic Dashboard for autonomous action approval**
4. Monitor agent performance in the Agent Monitor
5. View live routes on the Fleet Map

###  Purchase Order & Disposal Order Workflow

#### Agent Actions
- **Increase Actions**: Create purchase orders for inventory restocking
- **Decrease Actions**: Create disposal orders for inventory clearance
- **Discontinue Actions**: Create disposal orders for discontinued items
- **Maintain Actions**: No orders created (status quo)

#### Order Types
- **Purchase Orders**: `restock`, `reorder`, `new_item`
- **Disposal Orders**: `clearance`, `donation`, `destruction`, `return`

#### Order Status Tracking
- **Purchase Orders**: `pending` → `ordered` → `shipped` → `received` → `cancelled`
- **Disposal Orders**: `pending` → `approved` → `completed` → `cancelled`

### Database Setup
<<<<<<< Updated upstream
1. Create a Supabase project
2. Run the SQL scripts in `database/` to set up tables
3. ** Run the purchase orders schema script** (`database/purchase_orders_schema.sql`)
4. Configure environment variables with your Supabase credentials
5. The frontend will automatically connect to Supabase for all data operations
=======
The backend maintains a lightweight SQLite database automatically. On first boot it creates
`neuraroute.db` and seeds it with realistic demo data taken from `backend/app/db/sample_data.py`.

To customize or reset the dataset:
1. Stop the backend.
2. Delete `neuraroute.db`.
3. Edit `sample_data.py` with your desired rows.
4. Restart the backend (or run `python -m app.db.init_db`) and the schema plus seed records will be recreated.
5. Optionally set `DATABASE_URL` to point at a Postgres instance if you prefer an external database.
>>>>>>> Stashed changes

##  Database Schema

The local database includes:
- `fleet` - Vehicle and driver information
- `merchants` - Merchant profiles and locations
- `inventory` - Product inventory and stock levels
- `orders` - Customer orders and delivery information
- `routes` - Delivery route definitions
- `agents` - AI agent configurations and status
- `agent_actions` - Pending and historical agent actions
- `agent_decisions` - Structured LLM decisions awaiting approval
- `agent_logs` - Agent decision history
- `simulation_status` - Current simulation state
<<<<<<< Updated upstream
- `agent_plans` - Agent execution plans
- ** `purchase_orders`** - Purchase order tracking for inventory management
- ** `disposal_orders`** - Disposal order tracking for inventory clearance

###  New Database Tables

#### Purchase Orders Table
```sql
CREATE TABLE purchase_orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    item_id UUID REFERENCES inventory(id),
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    order_type TEXT NOT NULL CHECK (order_type IN ('restock', 'reorder', 'new_item')),
    status TEXT NOT NULL DEFAULT 'pending',
    requested_by TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expected_delivery TIMESTAMP WITH TIME ZONE,
    location TEXT,
    reason TEXT,
    cost_per_unit DECIMAL(10,2),
    total_cost DECIMAL(10,2)
);
```

#### Disposal Orders Table
```sql
CREATE TABLE disposal_orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    item_id UUID REFERENCES inventory(id),
    quantity INTEGER NOT NULL,
    disposal_type TEXT NOT NULL CHECK (disposal_type IN ('clearance', 'donation', 'destruction', 'return')),
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT,
    location TEXT,
    disposal_method TEXT,
    cost_savings DECIMAL(10,2)
);
```
=======
- `purchase_orders` - Purchase order tracking for inventory management
- `disposal_orders` - Disposal order tracking for inventory clearance
>>>>>>> Stashed changes

##  Development

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Development
```bash
<<<<<<< Updated upstream
# Run SQL scripts in Supabase SQL editor
# See database/ directory for schema files
#  Don't forget to run purchase_orders_schema.sql for the new order system
=======
# Rebuild the local database (drops existing data)
cd backend
rm -f neuraroute.db
python -m app.db.init_db
>>>>>>> Stashed changes
```

### Testing
```bash
cd frontend
npm test
```
<<<<<<< Updated upstream
=======

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 
>>>>>>> Stashed changes
