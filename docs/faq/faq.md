# (FAQ)

## 

 TradingAgents 

## 

### Q1: 

**A:** 

```bash
# 1: 
conda create -n tradingagents-clean python=3.11
conda activate tradingagents-clean
pip install -r requirements.txt

# 2: pip-tools 
pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt

# 3: 
pip install langchain-openai langgraph finnhub-python pandas
```

### Q2: API 

**A:** 

1. ****
```bash
# 
echo $OPENAI_API_KEY
echo $FINNHUB_API_KEY

# Windows 
echo %OPENAI_API_KEY%
echo %FINNHUB_API_KEY%
```

2. ****
```python
import os
# OpenAI 'sk-' 
openai_key = os.getenv('OPENAI_API_KEY')
print(f"OpenAI Key: {openai_key[:10]}..." if openai_key else "Not set")

# FinnHub 
finnhub_key = os.getenv('FINNHUB_API_KEY')
print(f"FinnHub Key: {finnhub_key[:10]}..." if finnhub_key else "Not set")
```

3. ****
```python
# API 
import openai
import finnhub

# OpenAI
try:
 client = openai.OpenAI()
 response = client.chat.completions.create(
 model="gpt-3.5-turbo",
 messages=[{"role": "user", "content": "Hello"}],
 max_tokens=5
 )
 print("OpenAI API ")
except Exception as e:
 print(f"OpenAI API : {e}")

# FinnHub
try:
 finnhub_client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))
 quote = finnhub_client.quote('AAPL')
 print("FinnHub API ")
except Exception as e:
 print(f"FinnHub API : {e}")
```

### Q3: Python 

**A:** TradingAgents Python 3.10, 3.11, 3.12 Python 3.11 

```bash
# Python 
python --version

# pyenv 
pyenv install 3.11.7
pyenv global 3.11.7
```

## 

### Q4: TradingAgents 

**A:** LLM API 

****
- ****$0.01-0.05 gpt-4o-mini
- ****$0.05-0.15 gpt-4o
- ****$0.10-0.30 gpt-4o + 

****
```python
# 
cost_optimized_config = {
 "deep_think_llm": "gpt-4o-mini",
 "quick_think_llm": "gpt-4o-mini",
 "max_debate_rounds": 1,
 "max_risk_discuss_rounds": 1,
 "online_tools": False # 
}
```

### Q5: API 

**A:** 

1. ****
```python
class BudgetController:
 def __init__(self, daily_budget=50):
 self.daily_budget = daily_budget
 self.current_usage = 0

 def check_budget(self, estimated_cost):
 if self.current_usage + estimated_cost > self.daily_budget:
 raise Exception("Daily budget exceeded")
 return True
```

2. ****
```python
config = {
 "online_tools": False, # 
 "cache_duration": 3600 # 1
}
```

3. ****
```python
# 
selected_analysts = ["market", "fundamentals"] # 
```

## 

### Q6: 

**A:** 

1. ****
```python
config = {
 "parallel_analysis": True,
 "max_workers": 4
}
```

2. ****
```python
config = {
 "deep_think_llm": "gpt-4o-mini", # 
 "quick_think_llm": "gpt-4o-mini"
}
```

3. ****
```python
config = {
 "max_debate_rounds": 1,
 "max_risk_discuss_rounds": 1
}
```

4. ****
```python
config = {
 "online_tools": True,
 "cache_enabled": True
}
```

### Q7: 

**A:** 

1. ****
```python
config = {
 "memory_cache": {
 "max_size": 500, # 
 "cleanup_threshold": 0.7
 }
}
```

2. ****
```python
# 
def batch_analysis(symbols, batch_size=5):
 for i in range(0, len(symbols), batch_size):
 batch = symbols[i:i+batch_size]
 # 
 yield analyze_batch(batch)
```

3. ****
```python
import gc

def analyze_with_cleanup(symbol, date):
 try:
 result = ta.propagate(symbol, date)
 return result
 finally:
 gc.collect() # 
```

### Q8: 

**A:** 

1. ****
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
 def decorator(func):
 @wraps(func)
 def wrapper(*args, **kwargs):
 for attempt in range(max_retries):
 try:
 return func(*args, **kwargs)
 except Exception as e:
 if attempt == max_retries - 1:
 raise e
 time.sleep(delay * (2 ** attempt))
 return None
 return wrapper
 return decorator

@retry_on_failure(max_retries=3)
def robust_analysis(symbol, date):
 return ta.propagate(symbol, date)
```

2. ****
```python
config = {
 "timeout": 60, # 60
 "connect_timeout": 10
}
```

3. ****
```python
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'https://proxy.company.com:8080'
```

## 

### Q9: 

**A:** 

1. ****
```python
# 
symbols = {
 "US": "AAPL", # 
}
```

2. ****
```python
def check_data_availability(symbol):
 try:
 # FinnHub
 finnhub_data = finnhub_client.quote(symbol)
 print(f"FinnHub: {symbol} - OK")
 except:
 print(f"FinnHub: {symbol} - Failed")

 try:
 # Yahoo Finance
 import yfinance as yf
 ticker = yf.Ticker(symbol)
 info = ticker.info
 print(f"Yahoo: {symbol} - OK")
 except:
 print(f"Yahoo: {symbol} - Failed")
```

3. ****
```python
config = {
 "data_sources": {
 "primary": "finnhub",
 "fallback": ["yahoo", "alpha_vantage"]
 }
}
```

### Q10: 

**A:** 

1. ****
```python
config = {
 "max_debate_rounds": 3, # 
 "max_risk_discuss_rounds": 2
}
```

2. ****
```python
config = {
 "deep_think_llm": "gpt-4o", # 
 "quick_think_llm": "gpt-4o-mini"
}
```

3. ****
```python
config = {
 "analyst_weights": {
 "fundamentals": 0.4, # 
 "technical": 0.3,
 "news": 0.2,
 "social": 0.1
 }
}
```

4. ****
```python
config = {
 "online_tools": True,
 "data_sources": ["finnhub", "yahoo", "google_news"]
}
```

## 

### Q11: 

**A:** 

1. ****
```python
from tradingagents.agents.analysts.base_analyst import BaseAnalyst

class CustomAnalyst(BaseAnalyst):
 def __init__(self, llm, config):
 super().__init__(llm, config)
 self.custom_tools = self._initialize_custom_tools()

 def perform_analysis(self, data: Dict) -> Dict:
 # 
 return {
 "custom_score": 0.75,
 "custom_insights": ["insight1", "insight2"],
 "recommendation": "buy"
 }
```

2. ****
```python
# 
config = {
 "custom_analysts": {
 "custom": CustomAnalyst
 }
}
```

### Q12: 

**A:** 

1. ****
```python
class CustomDataProvider:
 def __init__(self, api_key):
 self.api_key = api_key

 def get_data(self, symbol):
 # 
 return {"custom_metric": 0.85}
```

2. ****
```python
config = {
 "custom_data_sources": {
 "custom_provider": CustomDataProvider
 }
}
```

## 

### Q13: 

**A:** 

| | | |
|---------|------|---------|
| `API_KEY_INVALID` | API | |
| `RATE_LIMIT_EXCEEDED` | API | |
| `NETWORK_TIMEOUT` | | |
| `DATA_NOT_FOUND` | | |
| `INSUFFICIENT_MEMORY` | | |

### Q14: 

**A:** 

```python
# 
import logging
logging.basicConfig(level=logging.DEBUG)

# 
config = {
 "debug": True,
 "log_level": "DEBUG",
 "save_intermediate_results": True
}

# 
ta = TradingAgentsGraph(debug=True, config=config)
```

## 

### Q15: 

**A:** 

1. ****: [docs/README.md](../README.md)
2. **GitHub Issues**: [](https://github.com/TauricResearch/TradingAgents/issues)
3. **Discord **: [](https://discord.com/invite/hk9PGKShPK)
4. ****: support@tauric.ai

### Q16: Bug

**A:** Bug 

```markdown
## Bug 


## 
1. 
2. 
3. 

## 


## 


## 
- Python :
- TradingAgents :
- :
- :

## 

```


