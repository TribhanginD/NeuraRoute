# NeuraRoute - AI-Native Hyperlocal Logistics System

An intelligent operating system for small city sectors, featuring autonomous agents, demand forecasting, and real-time logistics optimization with **agentic AI capabilities** for autonomous decision-making and action-taking.

## 🚀 Features

### Core System
- **LCM-Style Demand Forecaster**: AI-powered demand prediction using structured context
- **LAM-Style Autonomous Agents**: Goal-driven planners executing toolchains
- **🆕 Agentic AI System**: Autonomous decision-making with approval workflows
- **15-Minute Tick Simulation**: Real-time state updates in Supabase
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
- **🆕 Realistic Business Workflow**: Purchase orders and disposal orders instead of direct inventory manipulation

### 🆕 Purchase Order & Disposal Order System
- **Purchase Orders**: Agents create purchase orders for inventory increases (restock, reorder, new items)
- **Disposal Orders**: Agents create disposal orders for inventory decreases (clearance, discontinuation)
- **Order Tracking**: Complete order lifecycle with status tracking (pending, ordered, shipped, received, cancelled)
- **Realistic Inventory Management**: Professional workflow that mirrors real business operations
- **Order Details**: Comprehensive order information including quantities, delivery dates, locations, and reasons

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
│   Frontend      │    │   Supabase      │    │   Redis Cache   │
│   (React)       │◄──►│   (Database)    │◄──►│   (Caching)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   AI/ML Engine  │◄─────────────┘
                        │   (LangChain)   │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │ 🆕 Agentic AI   │
                        │   System        │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │ 🆕 Purchase &    │
                        │   Disposal      │
                        │   Orders        │
                        └─────────────────┘
```

## 🛠️ Tech Stack

### Data Layer
- **Supabase** for primary database and real-time subscriptions
- **Redis** for caching and session management
- **PostgreSQL** (via Supabase) for data storage

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Mapbox/Leaflet** for mapping
- **React Query** for data fetching
- **Zustand** for state management
- **🆕 Agentic UI Components** for action approval and simulation
- **Supabase JS Client** for database operations

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
- **🆕 Supabase account and project**
- **🆕 OpenAI API key or Anthropic API key**

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd NeuraRoute

# Copy environment template
cp .env.example .env

# Configure Supabase and AI API keys
echo "REACT_APP_SUPABASE_URL=your_supabase_url" >> .env
echo "REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key" >> .env
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env

# Start services
./start.sh

# Access the application
# Frontend: http://localhost:3000
# 🆕 Agentic Dashboard: http://localhost:3000/agentic
```

### Manual Setup
```bash
# Frontend setup
cd frontend
npm install

# Start services
docker-compose up -d redis
npm start
```

## 🚀 Usage

### Starting the System
```bash
# Start all services
./start.sh

# Or manually
docker-compose up -d redis
cd frontend && npm start
```

### 🆕 Agentic AI Usage

#### Process a Situation
The agentic system can process situations through the frontend interface:

1. Navigate to the Agentic Dashboard at `http://localhost:3000/agentic`
2. Use the interface to input situation data
3. Review and approve/deny agent actions
4. Monitor the impact of decisions in real-time

#### Run Market Day Simulation
1. Access the Operations Console at `http://localhost:3000`
2. Use the Simulation Control panel to start/stop the 15-minute tick loop
3. **🆕 Use the Agentic Dashboard for autonomous action approval**
4. Monitor agent performance in the Agent Monitor
5. View live routes on the Fleet Map
6. Chat with merchants through the Merchant Chat interface

### 🆕 Purchase Order & Disposal Order Workflow

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
1. Create a Supabase project
2. Run the SQL scripts in `database/` to set up tables
3. **🆕 Run the purchase orders schema script** (`database/purchase_orders_schema.sql`)
4. Configure environment variables with your Supabase credentials
5. The frontend will automatically connect to Supabase for all data operations

## 📊 Database Schema

The system uses the following Supabase tables:
- `fleet` - Vehicle and driver information
- `merchants` - Merchant profiles and locations
- `inventory` - Product inventory and stock levels
- `orders` - Customer orders and delivery information
- `agents` - AI agent configurations and status
- `agent_actions` - Pending and historical agent actions
- `agent_logs` - Agent decision history
- `simulation_status` - Current simulation state
- `agent_plans` - Agent execution plans
- **🆕 `purchase_orders`** - Purchase order tracking for inventory management
- **🆕 `disposal_orders`** - Disposal order tracking for inventory clearance

### 🆕 New Database Tables

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

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Development
```bash
# Run SQL scripts in Supabase SQL editor
# See database/ directory for schema files
# 🆕 Don't forget to run purchase_orders_schema.sql for the new order system
```

### Testing
```bash
cd frontend
npm test
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 