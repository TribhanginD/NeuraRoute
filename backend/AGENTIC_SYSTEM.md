# Agentic AI System for NeuraRoute

## Overview

The Agentic AI System provides autonomous decision-making and action-taking capabilities for NeuraRoute's hyperlocal logistics operations. It uses LangChain agents with function-calling capabilities to intelligently manage inventory, optimize routes, adjust pricing, and dispatch fleet vehicles based on real-time data and demand forecasts.

## Architecture

### Core Components

1. **AgenticSystem** - Main orchestrator for autonomous decision-making
2. **AgenticTool** - Base class for all action-taking tools with approval workflows
3. **AgenticSimulationEngine** - Simulation engine for testing and demo scenarios
4. **Database Models** - Persistent storage for actions, approvals, and memory
5. **API Endpoints** - RESTful interface for frontend integration

### System Flow

```
Situation Context → AgenticSystem → LangChain Agent → Tools → Actions → Approval Workflow → Execution
```

## Key Features

### 1. Autonomous Decision Making
- **Goal-driven planning**: Agents optimize for stock availability and delivery efficiency
- **Context-aware reasoning**: Considers inventory, demand forecasts, weather, events, and traffic
- **Proactive actions**: Prevents stockouts and delivery delays through predictive actions

### 2. Approval Workflow
- **Automatic approval**: Low-risk actions (small orders, normal reroutes) are auto-approved
- **Manual approval**: High-value actions (>$1000 orders, urgent dispatches) require human approval
- **Audit trail**: Complete history of all actions, approvals, and executions

### 3. Tool Integration
- **place_order**: Order inventory from suppliers
- **reroute_driver**: Optimize delivery routes based on real-time conditions
- **update_inventory**: Update inventory levels at stores
- **adjust_pricing**: Modify pricing based on demand and market conditions
- **dispatch_fleet**: Assign vehicles to routes efficiently

### 4. Simulation Capabilities
- **Market day scenarios**: Predefined scenarios for testing and demonstration
- **Real-time simulation**: Step-by-step simulation with 15-minute intervals
- **Event-driven updates**: Dynamic events like demand spikes, delivery delays, weather changes

## Installation and Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- OpenAI API key or Anthropic API key

### Environment Variables
```bash
# AI Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEFAULT_MODEL=gpt-4o
AI_FALLBACK_MODEL=claude-3-sonnet-20240229

# Agentic System Configuration
AGENTIC_SIMULATION_MODE=false
AGENTIC_AUTO_APPROVAL_THRESHOLD=1000.0
AGENTIC_MAX_ITERATIONS=5
```

### Database Setup
```sql
-- The agentic system uses the existing AgenticAction and AgenticMemory models
-- These are automatically created when running database migrations
```

## Usage

### 1. Basic Usage

```python
from app.ai.agentic_system import get_agentic_system

# Initialize the system
agentic_system = await get_agentic_system()

# Process a situation
context = {
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
}

result = await agentic_system.process_situation(context)
print(f"Reasoning: {result['reasoning']}")
print(f"Actions: {result['actions']}")
```

### 2. Action Approval

```python
# Get pending actions
pending_actions = agentic_system.get_pending_actions()

# Approve an action
if pending_actions:
    action_id = pending_actions[0]["action_id"]
    result = await agentic_system.approve_action(action_id)
    print(f"Action approved: {result}")

# Deny an action
result = await agentic_system.deny_action(action_id)
print(f"Action denied: {result}")
```

### 3. Simulation

```python
from app.simulation.agentic_simulation import get_simulation_engine

# Initialize simulation engine
simulation_engine = await get_simulation_engine()

# Start a simulation
result = await simulation_engine.start_simulation("normal_market_day", speed=1.0)
print(f"Simulation started: {result}")

# Run simulation steps
while simulation_engine.is_running:
    step_result = await simulation_engine.run_simulation_step()
    print(f"Step result: {step_result}")
    
    if step_result.get("simulation_ended"):
        break

# Get simulation statistics
stats = simulation_engine.get_simulation_stats()
print(f"Final stats: {stats}")
```

## API Endpoints

### Core Endpoints

#### Process Situation
```http
POST /api/v1/agentic/process-situation
Content-Type: application/json

{
  "inventory": [...],
  "demand_forecast": [...],
  "deliveries": [...],
  "market_conditions": {...}
}
```

#### Get Pending Actions
```http
GET /api/v1/agentic/pending-actions
```

#### Approve Action
```http
POST /api/v1/agentic/actions/{action_id}/approve
```

#### Deny Action
```http
POST /api/v1/agentic/actions/{action_id}/deny
```

#### Get Action History
```http
GET /api/v1/agentic/action-history
```

### Simulation Endpoints

#### Get Available Scenarios
```http
GET /api/v1/agentic/simulation/scenarios
```

#### Start Simulation
```http
POST /api/v1/agentic/simulation/start?scenario_name=normal_market_day&speed=1.0
```

#### Run Simulation Step
```http
POST /api/v1/agentic/simulation/step
```

#### Stop Simulation
```http
POST /api/v1/agentic/simulation/stop
```

#### Auto-run Simulation
```http
POST /api/v1/agentic/simulation/auto-run?scenario_name=high_demand_day&speed=2.0
```

## Frontend Integration

### TypeScript Interfaces

The system provides comprehensive TypeScript interfaces for frontend integration:

```typescript
import {
  AgenticAction,
  ProcessSituationResponse,
  SimulationScenario,
  AgenticSystemStatus
} from './types/agentic';

// Process a situation
const response: ProcessSituationResponse = await fetch('/api/v1/agentic/process-situation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(context)
});

// Get pending actions
const pendingActions = await fetch('/api/v1/agentic/pending-actions');
```

### React Components

Example React component for action approval:

```tsx
import React from 'react';
import { AgenticAction, ApprovalStatus } from './types/agentic';

interface ActionCardProps {
  action: AgenticAction;
  onApprove: (actionId: string) => void;
  onDeny: (actionId: string) => void;
}

const ActionCard: React.FC<ActionCardProps> = ({ action, onApprove, onDeny }) => {
  return (
    <div className="border rounded-lg p-4 mb-4">
      <h3 className="text-lg font-semibold">{getActionTypeLabel(action.action_type)}</h3>
      <p className="text-gray-600">{action.reasoning}</p>
      <div className="flex justify-between items-center mt-4">
        <span className={`px-2 py-1 rounded ${getApprovalStatusColor(action.approval_status)}`}>
          {getApprovalStatusLabel(action.approval_status)}
        </span>
        <div className="space-x-2">
          <button
            onClick={() => onApprove(action.action_id)}
            className="bg-green-500 text-white px-4 py-2 rounded"
          >
            Approve
          </button>
          <button
            onClick={() => onDeny(action.action_id)}
            className="bg-red-500 text-white px-4 py-2 rounded"
          >
            Deny
          </button>
        </div>
      </div>
    </div>
  );
};
```

## Configuration

### Tool Configuration

Each tool has configurable approval thresholds:

```python
class PlaceOrderTool(AgenticTool):
    def __init__(self):
        super().__init__(
            name="place_order",
            description="Place an order with a supplier for inventory restocking",
            approval_threshold=1000.0  # Orders over $1000 require approval
        )
```

### System Configuration

```python
# In config.py
AGENTIC_SYSTEM_CONFIG = {
    "max_iterations": 5,
    "auto_approval_threshold": 1000.0,
    "simulation_mode": False,
    "memory_retention_days": 30,
    "confidence_threshold": 0.6
}
```

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
cd backend
pytest tests/test_agentic_system.py -v
```

### Integration Tests

Test the full workflow:

```bash
# Start the backend
uvicorn app.main:app --reload

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/agentic/demo/market-day
```

### Simulation Testing

```python
# Test simulation scenarios
simulation_engine = await get_simulation_engine()
scenarios = simulation_engine.get_available_scenarios()

for scenario in scenarios:
    result = await simulation_engine.start_simulation(scenario["name"])
    # Run simulation and verify results
```

## Monitoring and Logging

### Logging

The system uses structured logging with structlog:

```python
import structlog
logger = structlog.get_logger()

logger.info("Agentic action created", 
    action_id=action.action_id,
    action_type=action.action_type,
    approval_required=action.approval_required
)
```

### Metrics

Key metrics tracked:
- Actions generated per hour
- Approval rates
- Execution success rates
- Response times
- Tool usage statistics

### Health Checks

```http
GET /api/v1/agentic/status
```

Returns system health and performance metrics.

## Security Considerations

### Approval Workflows
- All high-value actions require manual approval
- Complete audit trail of all decisions
- Role-based access control for approvals

### API Security
- Input validation on all endpoints
- Rate limiting to prevent abuse
- Authentication required for sensitive operations

### Data Privacy
- No sensitive data logged
- Anonymized metrics collection
- Secure storage of action history

## Performance Optimization

### Caching
- Redis caching for frequently accessed data
- Memory caching for agent conversations
- Tool result caching

### Async Processing
- All operations are async for better performance
- Background processing for long-running tasks
- Non-blocking action execution

### Database Optimization
- Indexed queries for action lookups
- Efficient pagination for large datasets
- Connection pooling

## Troubleshooting

### Common Issues

1. **Agent not responding**
   - Check API key configuration
   - Verify model availability
   - Check rate limits

2. **Actions stuck in pending**
   - Verify approval workflow
   - Check for system errors
   - Review action parameters

3. **Simulation not starting**
   - Check scenario configuration
   - Verify agentic system initialization
   - Review simulation parameters

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Error Handling

The system includes comprehensive error handling:

```python
try:
    result = await agentic_system.process_situation(context)
except Exception as e:
    logger.error("Error processing situation", error=str(e))
    # Handle error appropriately
```

## Future Enhancements

### Planned Features

1. **Multi-agent coordination**: Multiple specialized agents working together
2. **Learning capabilities**: Agents that improve over time
3. **Advanced scenarios**: More complex simulation scenarios
4. **Real-time streaming**: WebSocket updates for live monitoring
5. **Mobile integration**: Mobile app for action approvals

### Extensibility

The system is designed for easy extension:

```python
class CustomTool(AgenticTool):
    def __init__(self):
        super().__init__(
            name="custom_action",
            description="Custom action for specific needs",
            approval_threshold=500.0
        )
    
    async def _perform_action(self, parameters):
        # Implement custom logic
        return {"status": "completed"}
```

## Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run tests: `pytest tests/`
5. Start development server: `uvicorn app.main:app --reload`

### Code Style

- Follow PEP 8 for Python code
- Use type hints throughout
- Write comprehensive docstrings
- Include unit tests for new features

### Pull Request Process

1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request
5. Code review and approval

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide
- Contact the development team 