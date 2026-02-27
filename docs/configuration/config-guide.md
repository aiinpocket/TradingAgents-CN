# (v0.1.7)

## 

TradingAgents-CN `.env` v0.1.7Docker

## v0.1.7 

### 
- **Docker**: 
- ****: 
- ****: 

### 
- ****: Word/PDF/Markdown
- ****: 
- ****: Pandocwkhtmltopdf

### LLM
- ****: 
- ****: 

## 

### .env ()
```bash
# ===========================================
# TradingAgents-CN (v0.1.7)
# ===========================================

# LLM ()
# OpenAI ( - )
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude ( - )
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 
FINNHUB_API_KEY=your_finnhub_api_key_here

# (Docker)
MONGODB_ENABLED=false
REDIS_ENABLED=false
MONGODB_HOST=localhost
MONGODB_PORT=27018
REDIS_HOST=localhost
REDIS_PORT=6380

# 
TRADINGAGENTS_RESULTS_DIR=./results
TRADINGAGENTS_DATA_DIR=./data
```

## 

### 1. 

#### project_dir
- ****: `str`
- ****: 
- ****: 

#### results_dir
- ****: `str`
- ****: `"./results"`
- ****: `TRADINGAGENTS_RESULTS_DIR`
- ****: 

```python
config = {
 "results_dir": "/path/to/custom/results", # 
}
```

#### data_cache_dir
- ****: `str`
- ****: `"tradingagents/dataflows/data_cache"`
- ****: 

### 2. LLM 

#### llm_provider
- ****: `str`
- ****: `"openai"`, `"anthropic"`
- ****: `"openai"`
- ****: 

```python
# OpenAI 
config = {
 "llm_provider": "openai",
 "backend_url": "https://api.openai.com/v1",
 "deep_think_llm": "gpt-4o",
 "quick_think_llm": "gpt-4o-mini",
}

# Anthropic 
config = {
 "llm_provider": "anthropic",
 "backend_url": "https://api.anthropic.com",
 "deep_think_llm": "claude-3-opus-20240229",
 "quick_think_llm": "claude-3-haiku-20240307",
}

```

#### deep_think_llm
- ****: `str`
- ****: `"o4-mini"`
- ****: 

****:
- ****: `"gpt-4o"`, `"claude-3-opus-20240229"`
- ****: `"gpt-4o-mini"`, `"claude-3-sonnet-20240229"`
- ****: `"gpt-3.5-turbo"`, `"claude-3-haiku-20240307"`

#### quick_think_llm
- ****: `str`
- ****: `"gpt-4o-mini"`
- ****: 

### 3. 

#### max_debate_rounds
- ****: `int`
- ****: `1`
- ****: `1-10`
- ****: 

```python
# 
config_scenarios = {
 "quick_analysis": {"max_debate_rounds": 1}, # 
 "standard": {"max_debate_rounds": 2}, # 
 "thorough": {"max_debate_rounds": 3}, # 
 "comprehensive": {"max_debate_rounds": 5}, # 
}
```

#### max_risk_discuss_rounds
- ****: `int`
- ****: `1`
- ****: `1-5`
- ****: 

#### max_recur_limit
- ****: `int`
- ****: `30`
- ****: 

### 4. 

#### online_tools
- ****: `bool`
- ****: `True`
- ****: 

```python
# - 
config = {"online_tools": True}

# - 
config = {"online_tools": False}
```

## 

### 1. 
```python
config = {
 "analyst_weights": {
 "fundamentals": 0.3, # 
 "technical": 0.3, # 
 "news": 0.2, # 
 "social": 0.2, # 
 }
}
```

### 2. 
```python
config = {
 "risk_management": {
 "risk_threshold": 0.8, # 
 "max_position_size": 0.1, # 
 "stop_loss_threshold": 0.05, # 
 "take_profit_threshold": 0.15, # 
 }
}
```

### 3. 
```python
config = {
 "data_sources": {
 "primary": "finnhub", # 
 "fallback": ["yahoo", "alpha_vantage"], # 
 "cache_ttl": {
 "price_data": 300, # 5
 "fundamental_data": 86400, # 24
 "news_data": 3600, # 1
 }
 }
}
```

### 4. 
```python
config = {
 "performance": {
 "parallel_analysis": True, # 
 "max_workers": 4, # 
 "timeout": 300, # 
 "retry_attempts": 3, # 
 "batch_size": 10, # 
 }
}
```

## 

### 
```bash
# OpenAI API
export OPENAI_API_KEY="your_openai_api_key"

# FinnHub API
export FINNHUB_API_KEY="your_finnhub_api_key"

# 
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export TRADINGAGENTS_RESULTS_DIR="/custom/results/path"
```

### .env 
```bash
# .env 
OPENAI_API_KEY=your_openai_api_key
FINNHUB_API_KEY=your_finnhub_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
TRADINGAGENTS_RESULTS_DIR=./custom_results
TRADINGAGENTS_LOG_LEVEL=INFO
```

## 

### 1. 
```python
# 
cost_optimized_config = {
 "llm_provider": "openai",
 "deep_think_llm": "gpt-4o-mini",
 "quick_think_llm": "gpt-4o-mini",
 "max_debate_rounds": 1,
 "max_risk_discuss_rounds": 1,
 "online_tools": False, # 
}
```

### 2. 
```python
# 
high_performance_config = {
 "llm_provider": "openai",
 "deep_think_llm": "gpt-4o",
 "quick_think_llm": "gpt-4o",
 "max_debate_rounds": 3,
 "max_risk_discuss_rounds": 2,
 "online_tools": True,
 "performance": {
 "parallel_analysis": True,
 "max_workers": 8,
 }
}
```

### 3. 
```python
# 
dev_config = {
 "llm_provider": "openai",
 "deep_think_llm": "gpt-4o-mini",
 "quick_think_llm": "gpt-4o-mini",
 "max_debate_rounds": 1,
 "online_tools": True,
 "debug": True,
 "log_level": "DEBUG",
}
```

### 4. 
```python
# 
prod_config = {
 "llm_provider": "openai",
 "deep_think_llm": "gpt-4o",
 "quick_think_llm": "gpt-4o-mini",
 "max_debate_rounds": 2,
 "max_risk_discuss_rounds": 1,
 "online_tools": True,
 "performance": {
 "parallel_analysis": True,
 "max_workers": 4,
 "timeout": 600,
 "retry_attempts": 3,
 },
 "logging": {
 "level": "INFO",
 "file": "/var/log/tradingagents.log",
 }
}
```

## 

### 
```python
class ConfigValidator:
 """"""

 def validate(self, config: Dict) -> Tuple[bool, List[str]]:
 """"""
 errors = []

 # 
 required_fields = ["llm_provider", "deep_think_llm", "quick_think_llm"]
 for field in required_fields:
 if field not in config:
 errors.append(f"Missing required field: {field}")

 # LLM
 valid_providers = ["openai", "anthropic"]
 if config.get("llm_provider") not in valid_providers:
 errors.append(f"Invalid llm_provider. Must be one of: {valid_providers}")

 # 
 if config.get("max_debate_rounds", 1) < 1:
 errors.append("max_debate_rounds must be >= 1")

 return len(errors) == 0, errors

# 
validator = ConfigValidator()
is_valid, errors = validator.validate(config)
if not is_valid:
 print("Configuration errors:", errors)
```

## 

### 
```python
class TradingAgentsGraph:
 def update_config(self, new_config: Dict):
 """"""

 # 
 validator = ConfigValidator()
 is_valid, errors = validator.validate(new_config)

 if not is_valid:
 raise ValueError(f"Invalid configuration: {errors}")

 # 
 self.config.update(new_config)

 # 
 self._reinitialize_components()

 def _reinitialize_components(self):
 """"""
 # LLM
 self._setup_llms()

 # 
 self._setup_agents()
```

 TradingAgents-CN 

## Docker (v0.1.7)

### Docker

```bash
# === Docker ===
# ()
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379

# 
WEB_PORT=8501
MONGODB_PORT=27017
REDIS_PORT=6379
MONGO_EXPRESS_PORT=8081
REDIS_COMMANDER_PORT=8082
```

## (v0.1.7)

### 

```bash
# === ===
# 
EXPORT_ENABLED=true

# (word,pdf,markdown)
EXPORT_DEFAULT_FORMAT=word,pdf

# 
EXPORT_OUTPUT_PATH=./exports

# Pandoc
PANDOC_PATH=/usr/bin/pandoc
WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf
```

## LLM (v0.1.7)

### 

```bash
# === ===
# 
LLM_SMART_ROUTING=true

# 
LLM_PRIORITY_ORDER=openai,anthropic

# 
LLM_DAILY_COST_LIMIT=10.0
LLM_COST_ALERT_THRESHOLD=8.0
```

## (v0.1.7)

### 1. 
- **API**: `.env` 
- ****: (600)
- ****: API

### 2. 
- ****: 
- ****: TTL
- ****: 

### 3. 
- ****: 
- ****: Token
- ****: 

---

*: 2025-07-13*
*: cn-0.1.7*
