# TradingAgents-CN API

## 

TradingAgents-CNAPI

---

## API

### 1. 

#### 
```python
def get_stock_fundamentals_unified(
 ticker: str,
 start_date: str,
 end_date: str,
 curr_date: str
) -> str
```

#### 
```json
{
 "ticker": "AAPL", // ()
 "start_date": "2025-06-01", // ()
 "end_date": "2025-07-15", // ()
 "curr_date": "2025-07-15" // ()
}
```

#### 
```markdown
# - AAPL

## 
- ****: AAPL
- ****: Apple Inc.
- ****: 
- ****: $185.23
- ****: +1.25%

## 
### 
- **PE**: 28.5
- **PB**: 42.8
- ****: 0.5%

### 
- **ROE**: 145.8%
- **ROA**: 28.2%
- ****: 45.5%

## 
: 8.5/10
: 
```

### 2. 

#### 
```python
def get_stock_market_analysis(
 ticker: str,
 period: str = "1y",
 indicators: List[str] = None
) -> str
```

#### 
```json
{
 "ticker": "AAPL",
 "period": "1y",
 "indicators": ["SMA", "EMA", "RSI", "MACD", "BOLL"]
}
```

#### 
```markdown
# - AAPL

## 
- ****: 
- ****: $178.50
- ****: $192.80

## 
- **RSI(14)**: 58.2 ()
- **MACD**: +0.12 ()
- ****: 

## 
: 
: 
```

### 3. 

#### 
```python
def get_stock_news_analysis(
 ticker: str,
 company_name: str,
 date_range: str = "7d"
) -> str
```

#### 
```json
{
 "ticker": "AAPL",
 "company_name": "Apple Inc.",
 "date_range": "7d"
}
```

#### 
```markdown
# - AAPL

## 
- ****: 25
- ****: 15 (60%)
- ****: 4 (16%)
- ****: 6 (24%)

## 
1. Q2
2. 
3. 

## 
- ****: (73%)
- ****: 
- ****: 

## 
...
```

---

## API

### 1. 

#### 
```python
def fundamentals_analyst(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 
```json
{
 "company_of_interest": "AAPL",
 "trade_date": "2025-07-15",
 "messages": [],
 "fundamentals_report": ""
}
```

#### 
```json
{
 "company_of_interest": "AAPL",
 "trade_date": "2025-07-15",
 "messages": [...],
 "fundamentals_report": "..."
}
```

### 2. 

#### 
```python
def market_analyst(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 
```json
{
 "company_of_interest": "AAPL",
 "trade_date": "2025-07-15",
 "messages": [],
 "market_report": ""
}
```

#### 
```json
{
 "company_of_interest": "AAPL",
 "trade_date": "2025-07-15",
 "messages": [...],
 "market_report": "..."
}
```

### 3. /

#### 
```python
def bull_researcher(state: Dict[str, Any]) -> Dict[str, Any]
def bear_researcher(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 
```json
{
 "company_of_interest": "AAPL",
 "trade_date": "2025-07-15",
 "fundamentals_report": "...",
 "market_report": "...",
 "investment_debate_state": {
 "history": "",
 "current_response": "",
 "count": 0
 }
}
```

#### 
```json
{
 "investment_debate_state": {
 "history": "...",
 "current_response": "...",
 "count": 1
 }
}
```

### 4. 

#### 
```python
def trader(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 
```json
{
 "company_of_interest": "AAPL",
 "trade_date": "2025-07-15",
 "fundamentals_report": "...",
 "market_report": "...",
 "news_report": "...",
 "sentiment_report": "...",
 "investment_debate_state": {
 "history": "..."
 }
}
```

#### 
```json
{
 "trader_signal": "...",
 "final_decision": {
 "action": "",
 "target_price": 195.80,
 "confidence": 0.82,
 "risk_score": 0.3,
 "reasoning": "..."
 }
}
```

---

## API

### 1. Yahoo Finance

#### 
```python
def get_yfinance_stock_data(
 ticker: str,
 start_date: str,
 end_date: str
) -> str
```

#### 
```python
def get_yfinance_stock_info(ticker: str) -> Dict[str, Any]
```

### 2. 

#### 
```python
def get_stock_data_unified(
 symbol: str,
 start_date: str,
 end_date: str
) -> str
```

#### 
```python
def switch_data_source(source: str) -> bool
```

---

## API

### 1. 

#### 
```python
def get_market_info(ticker: str) -> Dict[str, Any]
```

#### 
```json
{
 "ticker": "AAPL",
 "market": "us_stock",
 "market_name": "",
 "currency_name": "",
 "currency_symbol": "$",
 "is_us": true,
 "is_hk": false,
 "exchange": "NASDAQ"
}
```

### 2. API

#### 
```python
def get_cache(key: str) -> Any
def set_cache(key: str, value: Any, ttl: int = 3600) -> bool
def clear_cache(pattern: str = "*") -> int
```

---

## 

### 

| | | |
|---------|---------|------|
| 1001 | | |
| 1002 | | |
| 2001 | | API |
| 2002 | | |
| 3001 | LLM | |
| 3002 | | |
| 4001 | | |

### 
```json
{
 "success": false,
 "error_code": 1002,
 "error_message": "",
 "error_details": "",
 "timestamp": "2025-07-16T01:30:00Z"
}
```

---

## 

### 1. API
- API
- 
- 

### 2. 
- (RBAC)
- API
- 

### 3. 
- (HTTPS)
- 
- 

---

## 

### 1. 
- : < 5
- : < 30
- : < 3

### 2. 
- 10
- 
- 

### 3. 
- : 1
- : 24
- : 7

---

## 

### 1. 
- API
- > 80%
- 

### 2. 
- 
- 
- LLM

### 3. 
- 
- 
- 
