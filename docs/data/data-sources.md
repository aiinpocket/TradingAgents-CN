# 數據源集成 (v0.1.6)

## 概述

TradingAgents 中文增强版集成了多種金融數據源，特別加强了對中國A股市場的支持。為智能體提供全面、準確、實時的市場信息。本文档詳細介紹了支持的數據源、API集成方法、數據格式和使用指南。

## 🔄 v0.1.6 重大更新

### 數據源迁移完成
- ✅ **主數據源**: 從通達信完全迁移到Tushare
- ✅ **混合策略**: Tushare(歷史數據) + AKShare(實時數據)
- ✅ **統一接口**: 透明的數據源切換，用戶無感知
- ✅ **向後兼容**: 保持所有API接口不變
- ✅ **用戶界面**: 所有提示信息已更新為正確的數據源標识

## 🎯 v0.1.6 數據源狀態

| 數據源 | 市場 | 狀態 | 說明 |
|--------|------|------|------|
| 🇨🇳 **Tushare數據接口** | A股 | ✅ 完整支持 | 實時行情、歷史數據、技術指標 |
| **FinnHub** | 美股 | ✅ 完整支持 | 實時數據、基本面、新聞 |
| **Google News** | 全球 | ✅ 完整支持 | 財經新聞、市場資讯 |
| **Reddit** | 全球 | ✅ 完整支持 | 社交媒體情绪分析 |
| **MongoDB** | 緩存 | ✅ 完整支持 | 數據持久化存储 |
| **Redis** | 緩存 | ✅ 完整支持 | 高速數據緩存 |

## 支持的數據源

### 🇨🇳 1. Tushare數據接口 (新增 v0.1.3)

#### 簡介
Tushare數據接口是中國領先的股票數據提供商，為A股市場提供實時行情和歷史數據。

#### 數據類型
```python
tdx_data_types = {
    "實時數據": [
        "A股實時行情",
        "成交量",
        "涨跌幅",
        "換手率"
    ],
    "歷史數據": [
        "日K線數據",
        "分鐘級數據",
        "複權數據",
        "除權除息"
    ],
    "技術指標": [
        "MA移動平均",
        "MACD",
        "RSI",
        "KDJ"
    ],
    "市場數據": [
        "板塊分類",
        "概念股",
        "龙虎榜",
        "資金流向"
    ]
}
```

#### 使用示例
```python
from tradingagents.dataflows.tdx_utils import get_stock_data

# 獲取A股數據
data = get_stock_data(
    stock_code="000001",  # 平安銀行
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### 1. FinnHub API

#### 簡介
FinnHub 是領先的金融數據提供商，提供實時股票價格、公司基本面數據、新聞和市場指標。

#### 數據類型
```python
finnhub_data_types = {
    "實時數據": [
        "股票價格",
        "交易量",
        "市場深度",
        "實時新聞"
    ],
    "基本面數據": [
        "財務報表",
        "公司概况",
        "分析師評級",
        "盈利預測"
    ],
    "技術指標": [
        "RSI",
        "MACD",
        "布林帶",
        "移動平均線"
    ],
    "市場數據": [
        "IPO日歷",
        "分红信息",
        "股票分割",
        "期權數據"
    ]
}
```

#### API 配置
```python
# finnhub_utils.py
import finnhub

class FinnHubDataProvider:
    """FinnHub 數據提供器"""
    
    def __init__(self, api_key: str):
        self.client = finnhub.Client(api_key=api_key)
        self.rate_limiter = RateLimiter(calls_per_minute=60)  # 免費版限制
    
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
        """獲取公司概况"""
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

#### 使用示例
```python
# 初始化 FinnHub 客戶端
finnhub_provider = FinnHubDataProvider(api_key=os.getenv("FINNHUB_API_KEY"))

# 獲取股票價格
price_data = finnhub_provider.get_stock_price("AAPL")
print(f"AAPL 當前價格: ${price_data['current_price']}")

# 獲取公司信息
company_info = finnhub_provider.get_company_profile("AAPL")
print(f"公司名稱: {company_info['name']}")
```

### 2. Yahoo Finance

#### 簡介
Yahoo Finance 提供免費的歷史股票數據、財務信息和市場指標，是獲取歷史數據的優秀選擇。

#### 數據類型
```python
yahoo_finance_data_types = {
    "歷史數據": [
        "股票價格歷史",
        "交易量歷史",
        "調整後價格",
        "股息歷史"
    ],
    "財務數據": [
        "損益表",
        "資產负债表",
        "現金流量表",
        "關键指標"
    ],
    "市場數據": [
        "期權鏈",
        "分析師建议",
        "機構持股",
        "內部人交易"
    ]
}
```

#### API 集成
```python
# yfin_utils.py
import yfinance as yf
import pandas as pd

class YahooFinanceProvider:
    """Yahoo Finance 數據提供器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5分鐘緩存
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """獲取歷史數據"""
        cache_key = f"{symbol}_{period}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period)
        
        # 緩存數據
        self.cache[cache_key] = {
            "data": hist_data,
            "timestamp": time.time()
        }
        
        return hist_data
    
    def get_financial_info(self, symbol: str) -> Dict:
        """獲取財務信息"""
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
        
        # 計算移動平均線
        hist_data["MA_20"] = hist_data["Close"].rolling(window=20).mean()
        hist_data["MA_50"] = hist_data["Close"].rolling(window=50).mean()
        
        # 計算 RSI
        hist_data["RSI"] = self._calculate_rsi(hist_data["Close"])
        
        # 計算 MACD
        macd_data = self._calculate_macd(hist_data["Close"])
        hist_data = pd.concat([hist_data, macd_data], axis=1)
        
        return {
            "symbol": symbol,
            "indicators": hist_data.tail(1).to_dict("records")[0],
            "trend_analysis": self._analyze_trend(hist_data),
            "support_resistance": self._find_support_resistance(hist_data)
        }
```

### 3. Reddit API

#### 簡介
Reddit API 提供社交媒體討論數據，用於分析投資者情绪和市場熱點。

#### 數據類型
```python
reddit_data_types = {
    "討論數據": [
        "熱門帖子",
        "評論內容",
        "用戶互動",
        "話題趋势"
    ],
    "情感數據": [
        "情感極性",
        "情感强度",
        "情感分布",
        "情感變化"
    ],
    "熱度指標": [
        "提及頻率",
        "討論熱度",
        "用戶參与度",
        "傳播速度"
    ]
}
```

#### API 集成
```python
# reddit_utils.py
import praw
from textblob import TextBlob

class RedditDataProvider:
    """Reddit 數據提供器"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def get_stock_discussions(self, symbol: str, subreddit: str = "stocks", limit: int = 100) -> List[Dict]:
        """獲取股票討論"""
        discussions = []
        
        # 搜索相關帖子
        for submission in self.reddit.subreddit(subreddit).search(symbol, limit=limit):
            # 分析情感
            sentiment = self.sentiment_analyzer.analyze(submission.title + " " + submission.selftext)
            
            discussions.append({
                "id": submission.id,
                "title": submission.title,
                "content": submission.selftext,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "author": str(submission.author),
                "url": submission.url,
                "sentiment": sentiment
            })
        
        return discussions
    
    def analyze_sentiment_trends(self, discussions: List[Dict]) -> Dict:
        """分析情感趋势"""
        if not discussions:
            return {"error": "No discussions found"}
        
        # 計算整體情感
        sentiments = [d["sentiment"]["polarity"] for d in discussions]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # 時間序列分析
        time_series = self._create_sentiment_time_series(discussions)
        
        # 熱度分析
        engagement_metrics = self._calculate_engagement_metrics(discussions)
        
        return {
            "overall_sentiment": avg_sentiment,
            "sentiment_distribution": self._calculate_sentiment_distribution(sentiments),
            "time_series": time_series,
            "engagement_metrics": engagement_metrics,
            "trending_topics": self._extract_trending_topics(discussions)
        }
```

### 4. Google News

#### 簡介
Google News API 提供實時新聞數據，用於分析市場事件和新聞對股價的影響。

#### 數據類型
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
        "影響範围",
        "後续發展"
    ]
}
```

#### API 集成
```python
# googlenews_utils.py
from GoogleNews import GoogleNews
import requests
from bs4 import BeautifulSoup

class GoogleNewsProvider:
    """Google News 數據提供器"""
    
    def __init__(self):
        self.googlenews = GoogleNews()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def get_stock_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """獲取股票相關新聞"""
        # 設置搜索參數
        self.googlenews.clear()
        self.googlenews.set_time_range(f"{days}d")
        self.googlenews.set_lang("en")
        
        # 搜索新聞
        search_terms = [symbol, f"{symbol} stock", f"{symbol} earnings"]
        all_news = []
        
        for term in search_terms:
            self.googlenews.search(term)
            news_results = self.googlenews.results()
            
            for news in news_results:
                # 獲取新聞詳情
                news_detail = self._get_news_detail(news)
                if news_detail:
                    all_news.append(news_detail)
        
        # 去重和排序
        unique_news = self._deduplicate_news(all_news)
        return sorted(unique_news, key=lambda x: x["published_date"], reverse=True)
    
    def _get_news_detail(self, news_item: Dict) -> Dict:
        """獲取新聞詳情"""
        try:
            # 分析新聞情感
            sentiment = self.sentiment_analyzer.analyze(news_item.get("title", ""))
            
            # 評估新聞重要性
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
        
        # 情感分析
        sentiment_analysis = self._analyze_news_sentiment(news_list)
        
        # 影響評估
        impact_assessment = self._assess_news_impact(news_list, symbol)
        
        # 時間線分析
        timeline_analysis = self._create_news_timeline(news_list)
        
        return {
            "sentiment_analysis": sentiment_analysis,
            "impact_assessment": impact_assessment,
            "timeline_analysis": timeline_analysis,
            "key_events": self._identify_key_events(news_list),
            "market_implications": self._analyze_market_implications(news_list, symbol)
        }
```

## 數據集成接口

### 統一數據接口
```python
# interface.py
class DataInterface:
    """統一數據接口"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.providers = self._initialize_providers()
        self.cache_manager = CacheManager()
        
    def _initialize_providers(self) -> Dict:
        """初始化數據提供器"""
        providers = {}
        
        # FinnHub
        if self.config.get("finnhub_api_key"):
            providers["finnhub"] = FinnHubDataProvider(self.config["finnhub_api_key"])
        
        # Yahoo Finance
        providers["yahoo"] = YahooFinanceProvider()
        
        # Reddit
        if self.config.get("reddit_credentials"):
            providers["reddit"] = RedditDataProvider(**self.config["reddit_credentials"])
        
        # Google News
        providers["google_news"] = GoogleNewsProvider()
        
        return providers
    
    def get_comprehensive_data(self, symbol: str, date: str = None) -> Dict:
        """獲取综合數據"""
        data = {}
        
        # 並行獲取數據
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
        """獲取價格數據"""
        # 優先使用 FinnHub，备用 Yahoo Finance
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

## 數據质量控制

### 數據驗證
```python
class DataValidator:
    """數據驗證器"""
    
    def validate_data(self, data: Dict, data_type: str) -> Tuple[bool, List[str]]:
        """驗證數據质量"""
        errors = []
        
        # 基本完整性檢查
        if not data:
            errors.append("Data is empty")
            return False, errors
        
        # 特定類型驗證
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
        """驗證價格數據"""
        errors = []
        
        required_fields = ["symbol", "current_price"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # 價格合理性檢查
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
        
        # 清理過期的調用記錄
        self.calls = [call_time for call_time in self.calls if current_time - call_time < 60]
        
        # 檢查是否超過限制
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
    """重試裝饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))  # 指數退避
            return None
        return wrapper
    return decorator
```

### 3. 數據緩存策略
```python
class CacheManager:
    """緩存管理器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {
            "price_data": 60,      # 1分鐘
            "fundamental_data": 3600,  # 1小時
            "news_data": 1800,     # 30分鐘
            "social_data": 900     # 15分鐘
        }
    
    def get(self, key: str, data_type: str) -> Optional[Dict]:
        """獲取緩存數據"""
        if key in self.cache:
            cached_item = self.cache[key]
            ttl = self.cache_ttl.get(data_type, 3600)
            
            if time.time() - cached_item["timestamp"] < ttl:
                return cached_item["data"]
            else:
                del self.cache[key]
        
        return None
    
    def set(self, key: str, data: Dict, data_type: str):
        """設置緩存數據"""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time(),
            "type": data_type
        }
```

通過這些數據源的集成，TradingAgents 能夠獲得全面、實時、高质量的市場數據，為智能體的分析和決策提供坚實的數據基础。
