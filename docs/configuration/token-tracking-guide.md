# Token (v0.1.7)

TradingAgents-CNTokenv0.1.7

## 

TradingAgentsToken

- **Token**: LLMtoken
- ****: 
- ****: JSONMongoDB
- ****: 
- ****: 

## LLM

LLMToken

- **
- **
- **Google AI**: Geminitoken
- **OpenAI**: 
- **Anthropic**: 

## 

### 1. 

 `.env` 

```bash
# 
ENABLE_COST_TRACKING=true

# 
COST_ALERT_THRESHOLD=100.0

# AIAPI
OPENAI_API_KEY=your_openai_key
```

### 2. 

#### 1: JSON

Token `config/usage.json` 

```bash
# 10000
MAX_USAGE_RECORDS=10000

# 
AUTO_SAVE_USAGE=true
```

#### 2: MongoDB

MongoDB

```bash
# MongoDB
USE_MONGODB_STORAGE=true

# MongoDB
# MongoDB
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/

# MongoDBMongoDB Atlas
# MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/

# 
MONGODB_DATABASE_NAME=tradingagents
```

### 3. MongoDBMongoDB

```bash
pip install pymongo
```

## 

### 1. Token



```python
from tradingagents.llm_adapters.
from langchain_core.messages import HumanMessage

# LLM
llm = Chat
 model="gpt-4o-mini",
 temperature=0.7
)

# token
response = llm.invoke([
 HumanMessage(content="")
], session_id="my_session", analysis_type="stock_analysis")
```

### 2. 

```python
from tradingagents.config.config_manager import config_manager

# 30
stats = config_manager.get_usage_statistics(30)

print(f": ${stats['total_cost']:.4f}")
print(f": {stats['total_requests']}")
print(f"tokens: {stats['total_input_tokens']}")
print(f"tokens: {stats['total_output_tokens']}")

# 
for provider, provider_stats in stats['provider_stats'].items():
 print(f"{provider}: ${provider_stats['cost']:.4f}")
```

### 3. 

```python
from tradingagents.config.config_manager import token_tracker

# 
session_cost = token_tracker.get_session_cost("my_session")
print(f": ${session_cost:.4f}")
```

### 4. 

```python
# 
estimated_cost = token_tracker.estimate_cost(
 provider="
 model_name="gpt-4o-mini",
 estimated_input_tokens=1000,
 estimated_output_tokens=500
)
print(f": ${estimated_cost:.4f}")
```

## 

LLM

```python
from tradingagents.config.config_manager import config_manager, PricingConfig

# 
custom_pricing = PricingConfig(
 provider="
 model_name="gpt-4o",
 input_price_per_1k=0.02, # 1000token
 output_price_per_1k=0.06, # 1000token
 currency="USD"
)

pricing_list = config_manager.load_pricing()
pricing_list.append(custom_pricing)
config_manager.save_pricing(pricing_list)
```

## 

### OpenAI

| | ($/1K tokens) | ($/1K tokens) |
|------|----------------------|----------------------|
| gpt-4o-mini | 0.002 | 0.006 |
| gpt-4o | 0.004 | 0.012 |
| gpt-3.5-turbo | 0.0015 | 0.002 |
| gpt-4 | 0.03 | 0.06 |
| gpt-4-turbo | 0.01 | 0.03 |

## Token



```bash
# 
python tests/test_
```

## MongoDB

MongoDBJSON

1. ****: 
2. ****: 
3. ****: 
4. ****: 
5. ****: 

### MongoDB



- `(timestamp, provider, model_name)`
- `session_id`, `analysis_type`

## 

1. ****
2. ****
3. ****
4. **ID**
5. **MongoDB**

## 

### 1. Token

- API
- `ENABLE_COST_TRACKING=true`
- 

### 2. MongoDB

- MongoDB
- 
- 
- 

### 3. 

- 
- 
- token

## 

1. **MongoDB**
2. ****
3. ****
4. **ID**
5. ****

## 

- [ ] LLMToken
- [ ] 
- [ ] 
- [ ] 
- [ ] 