# AI Model Integration for NeuraRoute

This document describes the comprehensive AI model integration system for NeuraRoute, which provides multi-provider AI capabilities with fallback mechanisms, caching, and monitoring.

## Overview

The AI integration system supports multiple AI providers and models, enabling the autonomous agents to make intelligent decisions for demand forecasting, dynamic pricing, route optimization, and dispatch coordination.

## Features

### 🤖 Multi-Provider Support
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku
- **Google AI**: Gemini-1.5-Pro, Gemini-1.5-Flash, Gemini-Pro
- **Local AI**: Ollama (Llama, Mistral, CodeLlama, Phi-3)

### 🔄 Fallback Mechanisms
- Automatic fallback to secondary provider if primary fails
- Configurable fallback chains
- Graceful degradation to heuristic-based decisions

### 💾 Caching System
- Redis-based response caching
- Configurable TTL and cache size
- Cache hit/miss metrics

### 📊 Monitoring & Metrics
- Request success/failure tracking
- Provider usage statistics
- Response time monitoring
- Rate limiting per provider

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# AI/ML API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
LOCAL_AI_BASE_URL=http://localhost:11434

# AI Model Configuration
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
FORECASTING_MODEL=gpt-4o
ROUTING_MODEL=gpt-4o
PRICING_MODEL=gpt-4o
DISPATCH_MODEL=gpt-4o

# AI Model Parameters
AI_TEMPERATURE=0.1
AI_MAX_TOKENS=4000
AI_TOP_P=0.9
AI_FREQUENCY_PENALTY=0.0
AI_PRESENCE_PENALTY=0.0

# AI Model Fallbacks
AI_FALLBACK_PROVIDER=anthropic
AI_FALLBACK_MODEL=claude-3-sonnet-20240229
AI_ENABLE_FALLBACK=true

# AI Model Caching
AI_CACHE_ENABLED=true
AI_CACHE_TTL=3600
AI_CACHE_MAX_SIZE=10000

# AI Model Monitoring
AI_MONITORING_ENABLED=true
AI_RATE_LIMIT_PER_MINUTE=60
AI_TIMEOUT_SECONDS=30
AI_RETRY_ATTEMPTS=3
```

## Architecture

### Core Components

#### 1. AI Model Manager (`app/ai/model_manager.py`)
- Central orchestrator for all AI operations
- Provider management and initialization
- Request routing and fallback handling
- Caching and monitoring

#### 2. Provider Classes
- `OpenAIProvider`: OpenAI API integration
- `AnthropicProvider`: Anthropic Claude integration
- `GoogleAIProvider`: Google Gemini integration
- `LocalAIProvider`: Local Ollama integration

#### 3. Agent-Specific AI Engines
- `DemandForecastingEngine`: AI-powered demand prediction
- `PricingEngine`: Dynamic pricing optimization
- `RouteOptimizationEngine`: Intelligent route planning
- `DispatchEngine`: Smart fleet dispatch

## Usage Examples

### Basic AI Generation

```python
from app.ai.model_manager import get_ai_model_manager

async def generate_response():
    ai_manager = await get_ai_model_manager()
    
    response = await ai_manager.generate_response(
        prompt="What is the optimal route for delivery?",
        system_message="You are a logistics expert.",
        model="gpt-4o",
        provider="openai"
    )
    
    print(response["content"])
```

### Demand Forecasting

```python
from app.forecasting.engine import DemandForecastingEngine

async def forecast_demand():
    engine = DemandForecastingEngine()
    await engine.initialize()
    
    forecast = await engine.generate_forecast(
        sku_id=1,
        location_id=1,
        forecast_date=datetime.utcnow(),
        horizon_hours=24
    )
    
    print(f"Predicted demand: {forecast.predicted_demand}")
    print(f"Confidence: {forecast.confidence_lower} - {forecast.confidence_upper}")
```

### Dynamic Pricing

```python
from app.agents.pricing_agent import PricingEngine

async def calculate_price():
    engine = PricingEngine()
    await engine.initialize()
    
    result = await engine.calculate_optimal_price(
        sku=sku,
        current_demand=50.0,
        forecasted_demand=60.0,
        competitor_prices={"comp1": 10.0, "comp2": 9.5},
        market_conditions={"economic_indicator": "stable"}
    )
    
    print(f"Optimal price: ${result['optimal_price']}")
    print(f"Price change: {result['price_change_percentage']}%")
```

## API Endpoints

### AI Management Endpoints

- `GET /api/v1/ai/status` - Get AI system status
- `POST /api/v1/ai/test` - Test AI generation
- `GET /api/v1/ai/metrics` - Get AI metrics
- `GET /api/v1/ai/providers` - Get available providers
- `POST /api/v1/ai/cache/clear` - Clear AI cache

### Testing Endpoints

- `POST /api/v1/ai/forecast` - Test demand forecasting
- `POST /api/v1/ai/pricing` - Test dynamic pricing

## Testing

### Run AI Integration Tests

```bash
cd backend
python test_ai_integration.py
```

### Test via API

```bash
# Test basic AI generation
curl -X POST "http://localhost:8000/api/v1/ai/test" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "system_message": "You are a helpful assistant."
  }'

# Test demand forecasting
curl -X POST "http://localhost:8000/api/v1/ai/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "sku_id": 1,
    "location_id": 1,
    "horizon_hours": 24
  }'

# Test dynamic pricing
curl -X POST "http://localhost:8000/api/v1/ai/pricing" \
  -H "Content-Type: application/json" \
  -d '{
    "sku_id": 1,
    "current_demand": 50.0,
    "forecasted_demand": 60.0
  }'
```

## Monitoring

### Metrics Available

- Total requests
- Successful requests
- Failed requests
- Cache hits/misses
- Provider usage statistics
- Response times

### View Metrics

```bash
# Get AI metrics
curl "http://localhost:8000/api/v1/ai/metrics"

# Get provider status
curl "http://localhost:8000/api/v1/ai/providers"
```

## Best Practices

### 1. Provider Selection
- Use OpenAI for general tasks and complex reasoning
- Use Anthropic for creative tasks and long-form content
- Use Google AI for cost-effective operations
- Use Local AI for privacy-sensitive operations

### 2. Model Selection
- Use `gpt-4o` for high-accuracy tasks
- Use `gpt-4o-mini` for cost-effective operations
- Use `claude-3-sonnet` for balanced performance
- Use `gemini-1.5-pro` for multimodal tasks

### 3. Error Handling
- Always implement fallback mechanisms
- Monitor provider availability
- Set appropriate timeouts and retry limits
- Log AI interactions for debugging

### 4. Cost Optimization
- Enable caching for repeated requests
- Use appropriate model sizes for tasks
- Monitor usage and set rate limits
- Consider local models for high-volume operations

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API keys are correctly set in environment
   - Check API key permissions and quotas
   - Ensure proper formatting (no extra spaces)

2. **Provider Unavailable**
   - Check provider service status
   - Verify network connectivity
   - Review rate limits and quotas

3. **Response Parsing Errors**
   - Check JSON response format
   - Verify system message instructions
   - Review prompt structure

4. **Performance Issues**
   - Monitor response times
   - Check cache hit rates
   - Review rate limiting settings

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# Check AI system health
curl "http://localhost:8000/api/v1/ai/status"

# Check provider availability
curl "http://localhost:8000/api/v1/ai/providers"
```

## Future Enhancements

### Planned Features

1. **Advanced Caching**
   - Semantic caching based on content similarity
   - Multi-level caching (memory, Redis, disk)
   - Cache invalidation strategies

2. **Model Fine-tuning**
   - Domain-specific model training
   - Custom model deployment
   - A/B testing for model selection

3. **Advanced Monitoring**
   - Real-time performance dashboards
   - Anomaly detection
   - Predictive scaling

4. **Enhanced Security**
   - Request encryption
   - API key rotation
   - Audit logging

5. **Cost Management**
   - Usage analytics and reporting
   - Budget controls and alerts
   - Cost optimization recommendations

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the API documentation
3. Check system logs for errors
4. Test with the provided test scripts
5. Verify configuration settings

## Contributing

To contribute to the AI integration:

1. Follow the existing code structure
2. Add comprehensive tests
3. Update documentation
4. Follow error handling patterns
5. Add monitoring and metrics 