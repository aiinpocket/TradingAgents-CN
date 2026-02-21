# 資料源整合

## 概述

TradingAgents 整合了多種金融資料源，為智慧代理提供全面、準確、即時的市場資訊。本文件詳細介紹了支援的資料源、API整合方法、資料格式和使用指南。

## 🎯 資料源狀態

| 資料源 | 市場 | 狀態 | 說明 |
|--------|------|------|------|
| **FinnHub** | 美股 | ✅ 完整支援 | 即時資料、基本面、新聞 |
| **Yahoo Finance** | 全球 | ✅ 完整支援 | 歷史資料、財務資訊 |
| **Google News** | 全球 | ✅ 完整支援 | 財經新聞、市場資訊 |
| **MongoDB** | 快取 | ✅ 完整支援 | 資料持久化儲存 |
| **Redis** | 快取 | ✅ 完整支援 | 高速資料快取 |

## 支援的資料源

### 1. FinnHub API

#### 簡介
FinnHub 是領先的金融資料提供商，提供即時股票價格、公司基本面資料、新聞和市場指標。

#### 資料類型
```python
finnhub_data_types = {
    "即時資料": [
        "股票價格",
        "交易量",
        "市場深度",
        "即時新聞"
    ],
    "基本面資料": [
        "財務報表",
        "公司概況",
        "分析師評級",
        "盈利預測"
    ],
    "技術指標": [
        "RSI",
        "MACD",
        "布林帶",
        "移動平均線"
    ],
    "市場資料": [
        "IPO日曆",
        "股息資訊",
        "股票分割",
        "選擇權資料"
    ]
}
```

#### API 配置
```python
# finnhub_utils.py
import finnhub

class FinnHubDataProvider:
    """FinnHub 資料提供器"""

    def __init__(self, api_key: str):
        self.client = finnhub.Client(api_key=api_key)
        self.rate_limiter = RateLimiter(calls_per_minute=60)

    def get_stock_price(self, symbol: str) -> Dict:
        """獲取股票價格"""
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
        """獲取公司概況"""
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
        """獲取財務報表"""
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

#### 使用範例
```python
# 初始化 FinnHub 客戶端
finnhub_provider = FinnHubDataProvider(api_key=os.getenv("FINNHUB_API_KEY"))

# 獲取股票價格
price_data = finnhub_provider.get_stock_price("AAPL")
print(f"AAPL 當前價格: ${price_data['current_price']}")

# 獲取公司資訊
company_info = finnhub_provider.get_company_profile("AAPL")
print(f"公司名稱: {company_info['name']}")
```

### 2. Yahoo Finance

#### 簡介
Yahoo Finance 提供免費的歷史股票資料、財務資訊和市場指標，是獲取歷史資料的優秀選擇。

#### 資料類型
```python
yahoo_finance_data_types = {
    "歷史資料": [
        "股票價格歷史",
        "交易量歷史",
        "調整後價格",
        "股息歷史"
    ],
    "財務資料": [
        "損益表",
        "資產負債表",
        "現金流量表",
        "關鍵指標"
    ],
    "市場資料": [
        "選擇權鏈",
        "分析師建議",
        "機構持股",
        "內部人交易"
    ]
}
```

#### API 整合
```python
# yfin_utils.py
import yfinance as yf
import pandas as pd

class YahooFinanceProvider:
    """Yahoo Finance 資料提供器"""

    def __init__(self):
        self.cache = {}
        self.cache_duration = 300

    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """獲取歷史資料"""
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
        """獲取財務資訊"""
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
        """計算技術指標"""
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

#### 簡介
Google News API 提供即時新聞資料，用於分析市場事件和新聞對股價的影響。

#### 資料類型
```python
google_news_data_types = {
    "新聞內容": [
        "新聞標題",
        "新聞正文",
        "發布時間",
        "新聞來源"
    ],
    "影響分析": [
        "新聞情感",
        "影響程度",
        "相關性評分",
        "時效性分析"
    ],
    "事件追蹤": [
        "事件時間線",
        "關聯事件",
        "影響範圍",
        "後續發展"
    ]
}
```

#### API 整合
```python
# googlenews_utils.py
from GoogleNews import GoogleNews
import requests
from bs4 import BeautifulSoup

class GoogleNewsProvider:
    """Google News 資料提供器"""

    def __init__(self):
        self.googlenews = GoogleNews()
        self.sentiment_analyzer = SentimentAnalyzer()

    def get_stock_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """獲取股票相關新聞"""
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
        """獲取新聞詳情"""
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
        """分析新聞影響"""
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

## 資料整合介面

### 統一資料介面
```python
# interface.py
class DataInterface:
    """統一資料介面"""

    def __init__(self, config: Dict):
        self.config = config
        self.providers = self._initialize_providers()
        self.cache_manager = CacheManager()

    def _initialize_providers(self) -> Dict:
        """初始化資料提供器"""
        providers = {}

        if self.config.get("finnhub_api_key"):
            providers["finnhub"] = FinnHubDataProvider(self.config["finnhub_api_key"])

        providers["yahoo"] = YahooFinanceProvider()

        providers["google_news"] = GoogleNewsProvider()

        return providers

    def get_comprehensive_data(self, symbol: str, date: str = None) -> Dict:
        """獲取綜合資料"""
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
        """獲取價格資料"""
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

## 資料品質控制

### 資料驗證
```python
class DataValidator:
    """資料驗證器"""

    def validate_data(self, data: Dict, data_type: str) -> Tuple[bool, List[str]]:
        """驗證資料品質"""
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
        """驗證價格資料"""
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

## 使用最佳實踐

### 1. API 限制管理
```python
class RateLimiter:
    """API 限制管理器"""

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

### 2. 錯誤處理和重試
```python
def with_retry(max_retries: int = 3, delay: float = 1.0):
    """重試裝飾器"""
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

### 3. 資料快取策略
```python
class CacheManager:
    """快取管理器"""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = {
            "price_data": 60,
            "fundamental_data": 3600,
            "news_data": 1800,
            "social_data": 900
        }

    def get(self, key: str, data_type: str) -> Optional[Dict]:
        """獲取快取資料"""
        if key in self.cache:
            cached_item = self.cache[key]
            ttl = self.cache_ttl.get(data_type, 3600)

            if time.time() - cached_item["timestamp"] < ttl:
                return cached_item["data"]
            else:
                del self.cache[key]

        return None

    def set(self, key: str, data: Dict, data_type: str):
        """設置快取資料"""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time(),
            "type": data_type
        }
```

透過這些資料源的整合，TradingAgents 能夠獲得全面、即時、高品質的市場資料，為智慧代理的分析和決策提供堅實的資料基礎。
