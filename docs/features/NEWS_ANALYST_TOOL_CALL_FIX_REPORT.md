# 

## 

 Pydantic 

```
 : 1 validation error for get_realtime_stock_news 
curr_date 
 Field required [type=missing, input_value={'ticker': '600036'}, input_type=dict]

 : 2 validation errors for get_google_news 
query 
 Field required [type=missing, input_value={'ticker': '600036'}, input_type=dict]
curr_date 
 Field required [type=missing, input_value={'ticker': '600036'}, input_type=dict]
```

## 

 `news_analyst.py` 

### 1get_realtime_stock_news 
```python
# 
fallback_news = toolkit.get_realtime_stock_news.invoke({"ticker": ticker})

# 
def get_realtime_stock_news(
 ticker: Annotated[str, "Ticker of a company. e.g. AAPL, TSM"],
 curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
) -> str:
```

### 2get_google_news 
```python
# 
backup_news = toolkit.get_google_news.invoke({"ticker": ticker})

# 
def get_google_news(
 query: Annotated[str, "Query to search with"],
 curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
):
```

## 

### 1get_realtime_stock_news 
```python
# 
fallback_news = toolkit.get_realtime_stock_news.invoke({
 "ticker": ticker, 
 "curr_date": current_date
})
```

### 2get_google_news 
```python
# 
backup_news = toolkit.get_google_news.invoke({
 "query": f"{ticker} ", 
 "curr_date": current_date
})
```

## 

### 
```
 
==================================================

 :
 - ticker: 600036
 - curr_date: 2025-07-28

 get_realtime_stock_news ...
 : {'ticker': '600036', 'curr_date': '2025-07-28'}
 get_realtime_stock_news 
 : 26555 

 get_google_news ...
 : {'query': '600036 ', 'curr_date': '2025-07-28'}
 get_google_news 
 : 676 

 ...
 get_realtime_stock_news curr_date:
 : 1 validation error for get_realtime_stock_news
 get_google_news query curr_date:
 : 2 validation errors for get_google_news
```

## 

### 
1. **get_realtime_stock_news** `ticker` `curr_date` 
2. **get_google_news** `query` `curr_date` 
3. **Pydantic ** 
4. **** 

### 
- `get_realtime_stock_news` 26,555 
- `get_google_news` 676 
- 

## 

### 
- `tradingagents/agents/analysts/news_analyst.py`
 - 179 `get_realtime_stock_news` 
 - 230 `get_google_news` 

### 
1. **** - 
2. **** - 
3. **** - 
4. **

## 



1. 
2. 
3. 
4. Pydantic 
5. 

