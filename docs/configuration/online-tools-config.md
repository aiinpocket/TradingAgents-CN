# 

## 

TradingAgents-CN /LLM

## 

### 

| | | |
|---------|--------|------|
| `ONLINE_TOOLS_ENABLED` | `false` | |
| `ONLINE_NEWS_ENABLED` | `true` | |
| `REALTIME_DATA_ENABLED` | `false` | |

### 

1. **** (.env) - 
2. **** (default_config.py) - 

## 

### 1. ()
```bash
# .env 
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=false
REALTIME_DATA_ENABLED=false
```

**:**
- 
- API
- 
- 

### 2. ()
```bash
# .env 
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
```

**:**
- 
- 
- 
- 

### 3. ()
```bash
# .env 
ONLINE_TOOLS_ENABLED=true
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=true
```

**:**
- 
- 
- API
- 

## 

### 1: .env 
```bash
# .env 
nano .env

# 
ONLINE_TOOLS_ENABLED=true
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
```

### 2: 
```bash
# Windows PowerShell
$env:ONLINE_TOOLS_ENABLED="true"
$env:ONLINE_NEWS_ENABLED="true"
$env:REALTIME_DATA_ENABLED="false"

# Linux/macOS
export ONLINE_TOOLS_ENABLED=true
export ONLINE_NEWS_ENABLED=true
export REALTIME_DATA_ENABLED=false
```

### 3: 
```python
from tradingagents.default_config import DEFAULT_CONFIG

# 
config = DEFAULT_CONFIG.copy()
config["online_tools"] = True
config["online_news"] = True
config["realtime_data"] = False

# 
from tradingagents.graph.trading_graph import TradingAgentsGraph
ta = TradingAgentsGraph(config=config)
```

## 

### 
```bash
python test_online_tools_config.py
```

### 
```python
from tradingagents.default_config import DEFAULT_CONFIG

print(":")
print(f": {DEFAULT_CONFIG['online_tools']}")
print(f": {DEFAULT_CONFIG['online_news']}")
print(f": {DEFAULT_CONFIG['realtime_data']}")
```

## 

### `ONLINE_TOOLS_ENABLED` 
- API
- 
- 

### `ONLINE_NEWS_ENABLED` 
- `get_google_news` - Google
- `get_finnhub_social_sentiment` - FinnHub 

### `REALTIME_DATA_ENABLED` 
- 
- 
- 

## 

### 1. 
- `ONLINE_TOOLS_ENABLED=false` `ONLINE_NEWS_ENABLED=true`
- 

### 2. API
- API
- 
- 

### 3. 
- 
- 

## 

### 
 `OPENAI_ENABLED` 

**:**
```bash
OPENAI_ENABLED=false # 
```

**:**
```bash
OPENAI_ENABLED=false # OpenAI
ONLINE_TOOLS_ENABLED=false # 
ONLINE_NEWS_ENABLED=true # 
```

## 

### 1. 
```bash
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=false
REALTIME_DATA_ENABLED=false
```

### 2. 
```bash
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
```

### 3. 
```bash
ONLINE_TOOLS_ENABLED=true
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=true
```

## 

### 

1. ****
 - .env 
 - (true/false)

2. ****
 - API
 - 

3. ****
 - `REALTIME_DATA_ENABLED=true`
 - API

### 
```bash
# 
python -c "from tradingagents.default_config import DEFAULT_CONFIG; print(DEFAULT_CONFIG)"

# 
python test_online_tools_config.py

# 
echo $ONLINE_TOOLS_ENABLED
echo $ONLINE_NEWS_ENABLED
echo $REALTIME_DATA_ENABLED
```

---

TradingAgents-CN