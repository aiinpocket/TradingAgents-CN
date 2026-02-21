# 

## 

TradingAgents API

## 

| | | | |
|--------|------|------|------|
| **FinnHub** | | | |
| **Yahoo Finance** | | | |
| **Google News** | | | |
| **MongoDB** | | | |
| **Redis** | | | |

## 

### 1. FinnHub API

#### 
FinnHub 

#### 
```python
finnhub_data_types = {
 "": [
 "",
 "",
 "",
 ""
 ],
 "": [
 "",
 "",
 "",
 ""
 ],
 "": [
 "RSI",
 "MACD",
 "",
 ""
 ],
 "": [
 "IPO",
 "",
 "",
 ""
 ]
}
```

#### API 
```python
# finnhub_utils.py
import finnhub

class FinnHubDataProvider:
 """FinnHub """

 def __init__(self, api_key: str):
 self.client = finnhub.Client(api_key=api_key)
 self.rate_limiter = RateLimiter(calls_per_minute=60)

 def get_stock_price(self, symbol: str) -> Dict:
 """"""
 with self.rate_limiter:
 quote = self.client.quote(symbol)
 return {
 "symbol": symbol,
 "current_price": quote.get("c"),
 "change": quote.get("d"),
 "change_percent": quote.get("dp"),
 "high": quote.get("h"),
 "low": quote.get("l"),
 "open": quote.get("o"),
 "previous_close": quote.get("pc"),
 "timestamp": quote.get("t")
 }

 def get_company_profile(self, symbol: str) -> Dict:
 """"""
 with self.rate_limiter:
 profile = self.client.company_profile2(symbol=symbol)
 return {
 "symbol": symbol,
 "name": profile.get("name"),
 "industry": profile.get("finnhubIndustry"),
 "sector": profile.get("gsubind"),
 "market_cap": profile.get("marketCapitalization"),
 "shares_outstanding": profile.get("shareOutstanding"),
 "website": profile.get("weburl"),
 "logo": profile.get("logo"),
 "exchange": profile.get("exchange")
 }

 def get_financial_statements(self, symbol: str, statement_type: str = "ic") -> Dict:
 """"""
 with self.rate_limiter:
 financials = self.client.financials(symbol, statement_type, "annual")
 return {
 "symbol": symbol,
 "statement_type": statement_type,
 "data": financials.get("financials", []),
 "currency": financials.get("currency"),
 "last_updated": financials.get("cik")
 }
```

#### 
```python
# FinnHub 
finnhub_provider = FinnHubDataProvider(api_key=os.getenv("FINNHUB_API_KEY"))

# 
price_data = finnhub_provider.get_stock_price("AAPL")
print(f"AAPL : ${price_data['current_price']}")

# 
company_info = finnhub_provider.get_company_profile("AAPL")
print(f": {company_info['name']}")
```

### 2. Yahoo Finance

#### 
Yahoo Finance 

#### 
```python
yahoo_finance_data_types = {
 "": [
 "",
 "",
 "",
 ""
 ],
 "": [
 "",
 "",
 "",
 ""
 ],
 "": [
 "",
 "",
 "",
 ""
 ]
}
```

#### API 
```python
# yfin_utils.py
import yfinance as yf
import pandas as pd

class YahooFinanceProvider:
 """Yahoo Finance """

 def __init__(self):
 self.cache = {}
 self.cache_duration = 300

 def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
 """"""
 cache_key = f"{symbol}_{period}"

 if self._is_cache_valid(cache_key):
 return self.cache[cache_key]["data"]

 ticker = yf.Ticker(symbol)
 hist_data = ticker.history(period=period)

 self.cache[cache_key] = {
 "data": hist_data,
 "timestamp": time.time()
 }

 return hist_data

 def get_financial_info(self, symbol: str) -> Dict:
 """"""
 ticker = yf.Ticker(symbol)
 info = ticker.info

 return {
 "symbol": symbol,
 "market_cap": info.get("marketCap"),
 "enterprise_value": info.get("enterpriseValue"),
 "pe_ratio": info.get("trailingPE"),
 "pb_ratio": info.get("priceToBook"),
 "debt_to_equity": info.get("debtToEquity"),
 "roe": info.get("returnOnEquity"),
 "revenue_growth": info.get("revenueGrowth"),
 "profit_margins": info.get("profitMargins"),
 "beta": info.get("beta")
 }

 def get_technical_indicators(self, symbol: str, period: str = "1y") -> Dict:
 """"""
 hist_data = self.get_historical_data(symbol, period)

 hist_data["MA_20"] = hist_data["Close"].rolling(window=20).mean()
 hist_data["MA_50"] = hist_data["Close"].rolling(window=50).mean()
 hist_data["RSI"] = self._calculate_rsi(hist_data["Close"])

 macd_data = self._calculate_macd(hist_data["Close"])
 hist_data = pd.concat([hist_data, macd_data], axis=1)

 return {
 "symbol": symbol,
 "indicators": hist_data.tail(1).to_dict("records")[0],
 "trend_analysis": self._analyze_trend(hist_data),
 "support_resistance": self._find_support_resistance(hist_data)
 }
```

### 3. Google News

#### 
Google News API 

#### 
```python
google_news_data_types = {
 "": [
 "",
 "",
 "",
 ""
 ],
 "": [
 "",
 "",
 "",
 ""
 ],
 "": [
 "",
 "",
 "",
 ""
 ]
}
```

#### API 
```python
# googlenews_utils.py
from GoogleNews import GoogleNews
import requests
from bs4 import BeautifulSoup

class GoogleNewsProvider:
 """Google News """

 def __init__(self):
 self.googlenews = GoogleNews()
 self.sentiment_analyzer = SentimentAnalyzer()

 def get_stock_news(self, symbol: str, days: int = 7) -> List[Dict]:
 """"""
 self.googlenews.clear()
 self.googlenews.set_time_range(f"{days}d")
 self.googlenews.set_lang("en")

 search_terms = [symbol, f"{symbol} stock", f"{symbol} earnings"]
 all_news = []

 for term in search_terms:
 self.googlenews.search(term)
 news_results = self.googlenews.results()

 for news in news_results:
 news_detail = self._get_news_detail(news)
 if news_detail:
 all_news.append(news_detail)

 unique_news = self._deduplicate_news(all_news)
 return sorted(unique_news, key=lambda x: x["published_date"], reverse=True)

 def _get_news_detail(self, news_item: Dict) -> Dict:
 """"""
 try:
 sentiment = self.sentiment_analyzer.analyze(news_item.get("title", ""))
 importance = self._assess_news_importance(news_item)

 return {
 "title": news_item.get("title"),
 "link": news_item.get("link"),
 "published_date": news_item.get("date"),
 "source": news_item.get("media"),
 "sentiment": sentiment,
 "importance": importance,
 "relevance_score": self._calculate_relevance_score(news_item)
 }
 except Exception as e:
 print(f"Error processing news item: {e}")
 return None

 def analyze_news_impact(self, news_list: List[Dict], symbol: str) -> Dict:
 """"""
 if not news_list:
 return {"error": "No news found"}

 sentiment_analysis = self._analyze_news_sentiment(news_list)
 impact_assessment = self._assess_news_impact(news_list, symbol)
 timeline_analysis = self._create_news_timeline(news_list)

 return {
 "sentiment_analysis": sentiment_analysis,
 "impact_assessment": impact_assessment,
 "timeline_analysis": timeline_analysis,
 "key_events": self._identify_key_events(news_list),
 "market_implications": self._analyze_market_implications(news_list, symbol)
 }
```

## 

### 
```python
# interface.py
class DataInterface:
 """"""

 def __init__(self, config: Dict):
 self.config = config
 self.providers = self._initialize_providers()
 self.cache_manager = CacheManager()

 def _initialize_providers(self) -> Dict:
 """"""
 providers = {}

 if self.config.get("finnhub_api_key"):
 providers["finnhub"] = FinnHubDataProvider(self.config["finnhub_api_key"])

 providers["yahoo"] = YahooFinanceProvider()

 providers["google_news"] = GoogleNewsProvider()

 return providers

 def get_comprehensive_data(self, symbol: str, date: str = None) -> Dict:
 """"""
 data = {}

 with ThreadPoolExecutor(max_workers=4) as executor:
 futures = {
 executor.submit(self._get_price_data, symbol): "price_data",
 executor.submit(self._get_fundamental_data, symbol): "fundamental_data",
 executor.submit(self._get_news_data, symbol): "news_data",
 executor.submit(self._get_social_data, symbol): "social_data"
 }

 for future in as_completed(futures):
 data_type = futures[future]
 try:
 data[data_type] = future.result()
 except Exception as e:
 print(f"Error fetching {data_type}: {e}")
 data[data_type] = {}

 return data

 def _get_price_data(self, symbol: str) -> Dict:
 """"""
 if "finnhub" in self.providers:
 try:
 return self.providers["finnhub"].get_stock_price(symbol)
 except Exception:
 pass

 if "yahoo" in self.providers:
 hist_data = self.providers["yahoo"].get_historical_data(symbol, "5d")
 latest = hist_data.iloc[-1]
 return {
 "symbol": symbol,
 "current_price": latest["Close"],
 "change": latest["Close"] - latest["Open"],
 "high": latest["High"],
 "low": latest["Low"],
 "volume": latest["Volume"]
 }

 return {}
```

## 

### 
```python
class DataValidator:
 """"""

 def validate_data(self, data: Dict, data_type: str) -> Tuple[bool, List[str]]:
 """"""
 errors = []

 if not data:
 errors.append("Data is empty")
 return False, errors

 if data_type == "price_data":
 errors.extend(self._validate_price_data(data))
 elif data_type == "fundamental_data":
 errors.extend(self._validate_fundamental_data(data))
 elif data_type == "news_data":
 errors.extend(self._validate_news_data(data))
 elif data_type == "social_data":
 errors.extend(self._validate_social_data(data))

 return len(errors) == 0, errors

 def _validate_price_data(self, data: Dict) -> List[str]:
 """"""
 errors = []

 required_fields = ["symbol", "current_price"]
 for field in required_fields:
 if field not in data:
 errors.append(f"Missing required field: {field}")

 if "current_price" in data:
 price = data["current_price"]
 if not isinstance(price, (int, float)) or price <= 0:
 errors.append("Invalid price value")

 return errors
```

## 

### 1. API 
```python
class RateLimiter:
 """API """

 def __init__(self, calls_per_minute: int):
 self.calls_per_minute = calls_per_minute
 self.calls = []

 def __enter__(self):
 current_time = time.time()

 self.calls = [call_time for call_time in self.calls if current_time - call_time < 60]

 if len(self.calls) >= self.calls_per_minute:
 sleep_time = 60 - (current_time - self.calls[0])
 if sleep_time > 0:
 time.sleep(sleep_time)

 self.calls.append(current_time)

 def __exit__(self, exc_type, exc_val, exc_tb):
 pass
```

### 2. 
```python
def with_retry(max_retries: int = 3, delay: float = 1.0):
 """"""
 def decorator(func):
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
```

### 3. 
```python
class CacheManager:
 """"""

 def __init__(self):
 self.cache = {}
 self.cache_ttl = {
 "price_data": 60,
 "fundamental_data": 3600,
 "news_data": 1800,
 "social_data": 900
 }

 def get(self, key: str, data_type: str) -> Optional[Dict]:
 """"""
 if key in self.cache:
 cached_item = self.cache[key]
 ttl = self.cache_ttl.get(data_type, 3600)

 if time.time() - cached_item["timestamp"] < ttl:
 return cached_item["data"]
 else:
 del self.cache[key]

 return None

 def set(self, key: str, data: Dict, data_type: str):
 """"""
 self.cache[key] = {
 "data": data,
 "timestamp": time.time(),
 "type": data_type
 }
```

TradingAgents 
