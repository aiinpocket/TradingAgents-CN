# TradingAgents-CN 

## 

TradingAgents-CN 

## 

### 1. 

API

```bash
# 
python -m cli.main config

# 
python -m cli.main test
```

### 2. 

#### Web ()
```bash
# Web
python start_app.py
```
 `http://localhost:8501`

****:
- 
- 
- 
- 

****: [Web](web-interface-guide.md)

#### ()
```bash
# 
python examples/demo_analysis.py
```

****:
- 
- 
- 

## 

### 
- ****: 
- ****: MAMACDRSI
- ****: 
- ****: 

### 
- ****: 
- ****: 
- ****: 
- ****: 

### 
- ****: 
- ****: 
- ****: 
- ****: 

### 
- ****: 
- ****: 
- ****: 
- ****: 

### 
- ****: //
- ****: 
- ****: 
- ****: 

## 

### 



```python
# 
STOCK_SYMBOL = "TSLA" # 
ANALYSIS_DATE = "2024-06-26" # 
```

### 

- ****: AAPL, TSLA, MSFT, GOOGL, AMZN, NVDA 
- ****: SPY, QQQ, DIA ETF
- ****: 

## 

### 1. 

```python
# 
"deep_think_llm": "o4-mini", #
"quick_think_llm": "gpt-4o-mini", #
```

### 2. 

```python
# 
ANALYSIS_DATE = "2024-01-01" # 
ANALYSIS_DATE = "2024-06-01" # 
```

### 3. 


- 
- 
- 
- 

## 

### 

1. ****: 
2. ****: 
3. ****: 
4. ****: 

### 

1. ****: 
2. ****: AI
3. ****: 

## 

### 

1. **API**: .env
2. ****: 
3. ****: 

### 

```bash
# 
python -m cli.main help

# 
python -m cli.main examples
```

## 

### 



```python
stocks = ["AAPL", "MSFT", "GOOGL", "TSLA"]
for stock in stocks:
 # 
 analyze_stock(stock)
```

### 



```bash
# cronWindows
# 
0 9 * * * python examples/demo_analysis.py
```

## 

### 

1. ****: 
2. ****: 
3. ****: 
4. ****: 

### 

1. ****: 
2. ****: 
3. ****: 
4. ****: 

---

*: *
