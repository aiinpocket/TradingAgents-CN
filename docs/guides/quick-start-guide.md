---
version: cn-0.1.14-preview
last_updated: 2025-01-13
code_compatibility: cn-0.1.14-preview
status: updated
---

# TradingAgents-CN 

> ****: `cn-0.1.14-preview` 
> ****: 2025-01-13 
> ****: - 5

## 5

### 
- [](./installation-guide.md)
- LLM API
- 

### 1. 
```bash
# 
python examples/test_installation.py

# " "
```

### 2. 
```bash
# Web
python start_web.py

# streamlit
cd web && streamlit run app.py
```

### 3. 
: http://localhost:8501

### 4. 

#### LLM
LLM
- **OpenAI** - GPT-4GPT-4o-mini
- **Anthropic** - Claude 4 

#### 

- ****: GPT-4Claude Sonnet
- ****: GPT-4o-mini

### 5. 

#### 
```
: AAPL
: 2024-01-15
```

```
: TSLA
: 2024-01-15
```

## 

### 
- **LLM**: AI
- ****: 
- ****: 

### 
- ****: 
- ****: AI
- ****: 
- ****: API

### 
- ****: 
- ****: 
- ****: 
- ****: 

## 

### 1: 
```
: 
:
1. GPT-4 ()
2. : AAPL
3. 
4. ""
5. 
```

### 2: 
```
: 
:
1. ()
2. 
3. 
4. 
5. 
```

### 3: 
```
: 
:
1. 
2. 
3. AI
4. 
5. 
```

## 

### 

#### ()
- **OpenAI GPT-4**: 
- **Anthropic Claude Sonnet**: 

#### ()
- **GPT-4o-mini**: 

### 

#### 
1. **Yahoo Finance** - 
2. **FinnHub** - 
3. **Alpha Vantage** - 

## 

### 1. 
```python
# config/prompts/
# : custom_analysis.txt
```

### 2. 
```python
# Python
from tradingagents import TradingAgent

agent = TradingAgent()
stocks = ['AAPL', 'MSFT', 'GOOGL']
for stock in stocks:
 result = agent.analyze(stock)
 print(f"{stock}: {result.recommendation}")
```

### 3. 
```bash
# cron (Linux/macOS)
0 9 * * 1-5 cd /path/to/TradingAgents-CN && python scripts/daily_analysis.py

# (Windows)
# 9
```

## 

### 1. 
```bash
# .envRedis
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 2. 
```python
# config/settings.json
{
 "max_workers": 4,
 "request_timeout": 30
}
```

### 3. 
```bash
# ()
DATA_CACHE_TTL=3600
```

## 

### 1. API
- 
- 
- API

### 2. 
- 
- 
- 

### 3. 
- AI
- 
- 

## 

### Q: 
A: 
1. 
2. 
3. 
4. 

### Q: API
A:
1. 
2. API
3. API
4. 

### Q: 
A:
1. 
2. 
3. 
4. 

## 



1. **[](./config-management-guide.md)** - 
2. **[](./us-stock-analysis-guide.md)** - 
3. **[API](../development/api-development-guide.md)** - 
4. **[](../troubleshooting/)** - 

---

**AI** 
