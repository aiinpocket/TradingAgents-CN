# 

## 

 TradingAgents 

## v0.1.7 

### Docker
- ****: Docker Compose
- ****: WebMongoDBRedis
- ****: Volume

### 
- ****: Word/PDF/Markdown
- ****: 
- ****: Web

### 
- ****: 

## 

### 
- ****: Windows 10+, macOS 10.15+, Linux
- **Python**: 3.10 
- ****: 4GB RAM ( 8GB+)
- ****: 2GB 

### API 
API

1. **FinnHub API Key** ()
 - [FinnHub](https://finnhub.io/)
 - API

2. **OpenAI API Key** ()
 - [OpenAI Platform](https://platform.openai.com/)
 - API

3. **API** ()
 - Anthropic API: [console.anthropic.com](https://console.anthropic.com/)

## 

### 1. 
```bash
# 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN
```

### 2. 
```bash
# conda
conda create -n tradingagents python=3.13
conda activate tradingagents

# venv
python -m venv tradingagents
source tradingagents/bin/activate # Linux/macOS
# tradingagents\Scripts\activate # Windows
```

### 3. 
```bash
pip install -r requirements.txt
```

### 4. 

 `.env` 
```bash
# 
cp .env.example .env

# .env API

# FinnHub ()
FINNHUB_API_KEY=your_finnhub_api_key_here

# OpenAI ()
OPENAI_API_KEY=your_openai_api_key_here

# ()
MONGODB_ENABLED=false
REDIS_ENABLED=false
```

## 

### Web ()

Web

```bash
# Web
python start_app.py
```

 `http://localhost:8501`

Web
1. 
2. API
3. 
4. Token
5. 

### (CLI)



```bash
python -m cli.main
```

### Python API

Python

```python
# quick_start.py
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini" # 
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1 # 
config["online_tools"] = True # 

# 
ta = TradingAgentsGraph(debug=True, config=config)

# 
print(" AAPL...")
state, decision = ta.propagate("AAPL", "2024-01-15")

# 
print("\n=== ===")
print(f": {decision.get('action', 'hold')}")
print(f": {decision.get('confidence', 0.5):.2f}")
print(f": {decision.get('risk_score', 0.5):.2f}")
print(f": {decision.get('reasoning', 'N/A')}")
```


```bash
python quick_start.py
```

## 

### 
```python
config = {
 # LLM 
 "llm_provider": "openai", # "anthropic"
 "deep_think_llm": "gpt-4o-mini", # 
 "quick_think_llm": "gpt-4o-mini", # 

 # 
 "max_debate_rounds": 1, # (1-5)
 "max_risk_discuss_rounds": 1, # 

 # 
 "online_tools": True, # 
}
```

### 
```python
# 
selected_analysts = [
 "market", # 
 "fundamentals", # 
 "news", # 
 "social" # 
]

ta = TradingAgentsGraph(
 selected_analysts=selected_analysts,
 debug=True,
 config=config
)
```

## 

### 
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import json

def analyze_stock(symbol, date):
 """"""

 # 
 config = DEFAULT_CONFIG.copy()
 config["deep_think_llm"] = "gpt-4o-mini"
 config["quick_think_llm"] = "gpt-4o-mini"
 config["max_debate_rounds"] = 2
 config["online_tools"] = True

 # 
 ta = TradingAgentsGraph(
 selected_analysts=["market", "fundamentals", "news", "social"],
 debug=True,
 config=config
 )

 print(f" {symbol} ({date})...")

 try:
 # 
 state, decision = ta.propagate(symbol, date)

 # 
 print("\n" + "="*50)
 print(f": {symbol}")
 print(f": {date}")
 print("="*50)

 print(f"\n :")
 print(f" : {decision.get('action', 'hold').upper()}")
 print(f" : {decision.get('quantity', 0)}")
 print(f" : {decision.get('confidence', 0.5):.1%}")
 print(f" : {decision.get('risk_score', 0.5):.1%}")

 print(f"\n :")
 print(f" {decision.get('reasoning', 'N/A')}")

 # 
 if hasattr(state, 'analyst_reports'):
 print(f"\n :")
 for analyst, report in state.analyst_reports.items():
 score = report.get('overall_score', report.get('score', 0.5))
 print(f" {analyst}: {score:.1%}")

 return decision

 except Exception as e:
 print(f" : {e}")
 return None

# 
if __name__ == "__main__":
 # 
 result = analyze_stock("AAPL", "2024-01-15")

 if result:
 print("\n !")
 else:
 print("\n !")
```

## 

### 1. API 
```
: OpenAI API key not found
: OPENAI_API_KEY 
```

### 2. 
```
: Connection timeout
: 
```

### 3. 
```
: Out of memory
: max_debate_rounds 
```

### 4. 
```
: Failed to fetch data
: FINNHUB_API_KEY 
```

## 

### 1. 
```python
config["deep_think_llm"] = "gpt-4o-mini" # "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini" # "gpt-4o"
```

### 2. 
```python
config["max_debate_rounds"] = 1 # 3-5
config["max_risk_discuss_rounds"] = 1 # 2-3
```

### 3. 
```python
# 
selected_analysts = ["market", "fundamentals"] # 
```

### 4. 
```python
config["online_tools"] = False # 
```

## 



1. ****: [API](../api/core-api.md)
2. ****: [](../configuration/config-guide.md)
3. ****: [](../development/extending.md)
4. ****: [](../examples/basic-examples.md)

## 


- [](../faq/faq.md)
- [GitHub Issues](https://github.com/TauricResearch/TradingAgents/issues)
- [Discord ](https://discord.com/invite/hk9PGKShPK)
- [](../faq/troubleshooting.md)


