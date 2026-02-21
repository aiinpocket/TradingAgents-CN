# Finnhub

## 



```
[DEBUG] FinnhubNewsTool: AAPL 
: [Errno 2] No such file or directory: '/Users/yluo/Documents/Code/ScAI/FR1-data\\finnhub_data\\news_data\\AAPL_data_formatted.json'
```


1. ****UnixWindows
2. ****Finnhub
3. ****

## 

### 1. 

 `tradingagents/default_config.py` 

```python
# Unix
"data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",

# 
"data_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data"),
```

### 2. 



```
~/Documents/TradingAgents/data/
 finnhub_data/
 news_data/
 AAPL_data_formatted.json
 TSLA_data_formatted.json
 ...
 insider_senti/
 insider_trans/
 ...
 other_data/
```

### 3. Finnhub

#### API

1. **Finnhub API**
 ```bash
 # .env
 FINNHUB_API_KEY=your_finnhub_api_key_here
 ```

2. ****
 ```bash
 # 
 python scripts/download_finnhub_data.py --data-type news --symbols AAPL,TSLA,MSFT

 # 
 python scripts/download_finnhub_data.py --all

 # 
 python scripts/download_finnhub_data.py --force-refresh

 # 
 python scripts/download_finnhub_data.py --data-type news --days 30 --symbols AAPL
 ```

3. ****
 - `--data-type`: (news, sentiment, transactions, all)
 - `--symbols`: 
 - `--days`: (7)
 - `--force-refresh`: 
 - `--all`: 

#### 



```bash
# 
python scripts/development/download_finnhub_sample_data.py

# 
python tests/test_finnhub_news_fix.py
```

### 4. 



```bash
# 
python tests/test_finnhub_news_fix.py

# 
python -c "
from tradingagents.dataflows.interface import get_finnhub_news
result = get_finnhub_news('AAPL', '2025-01-02', 7)
print(result[:200])
"
```

## 



```
 AAPL (2024-12-26 2025-01-02)

1. 
2. 
3. Finnhub

```

## 

### 



```python
from tradingagents.dataflows.config import set_config

# 
config = {
 "data_dir": "C:/your/custom/data/directory"
}
set_config(config)
```

### 



```bash
# Windows
set TRADINGAGENTS_DATA_DIR=C:\your\custom\data\directory

# Linux/Mac
export TRADINGAGENTS_DATA_DIR=/your/custom/data/directory
```

## 

### Q1: 

****

****
```bash
# Windows
mkdir "C:\Users\%USERNAME%\Documents\TradingAgents\data"

# Linux/Mac
mkdir -p ~/Documents/TradingAgents/data
chmod 755 ~/Documents/TradingAgents/data
```

### Q2: Finnhub API

****API

****
1. Finnhub API
2. API
3. 

### Q3: 

****JSON

****
```bash
# JSON
python -c "import json; print(json.load(open('path/to/file.json')))"

# 
python scripts/download_finnhub_data.py --force-refresh
```

## 

### 

1. **`tradingagents/default_config.py`**
 - Unix
 - 

2. **`tradingagents/dataflows/finnhub_utils.py`**
 - 
 - 
 - UTF-8

3. **`tradingagents/dataflows/interface.py`**
 - get_finnhub_news
 - 

### 

```python
# 
data_path = os.path.join(
 data_dir, 
 "finnhub_data", 
 "news_data", 
 f"{ticker}_data_formatted.json"
)

# 
if not os.path.exists(data_path):
 print(f" [DEBUG] : {data_path}")
 return {}
```

## 



1. `python tests/test_finnhub_news_fix.py`
2. 
3. Finnhub API
4. 

---

****2025-01-02 
****v1.0 
****TradingAgents-CN v0.1.3+