# 新聞分析系統使用指南

本指南詳細介紹了如何使用TradingAgentsCN系統中的新聞獲取和分析功能，幫助您獲取實時新聞並進行專業分析，為投資決策提供重要參考。

## 1. 基本概念

在開始使用新聞分析系統前，了解以下基本概念将有助於更好地利用系統功能：

- **實時新聞聚合**：從多個數據源獲取最新新聞，並進行去重、排序和緊急程度評估
- **新聞分析師**：專業的財經新聞分析智能體，能夠分析新聞對股票價格的潜在影響
- **統一新聞接口**：自動识別股票類型並選擇合適的新聞源的統一接口
- **东方財富新聞**：通過AKShare獲取东方財富網的個股新聞，為A股和港股提供專業的中文財經新聞

## 2. 配置準备

### 2.1 API密鑰配置

使用新聞分析系統需要配置以下API密鑰：

```python
# 在config.py或.env文件中配置
FINNHUB_API_KEY = "your_finnhub_api_key"
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_api_key"
NEWSAPI_API_KEY = "your_newsapi_api_key"
```

您可以從以下網站獲取API密鑰：
- FinnHub: https://finnhub.io/
- Alpha Vantage: https://www.alphavantage.co/
- NewsAPI: https://newsapi.org/

### 2.2 AKShare配置

系統已集成AKShare庫，用於獲取东方財富網的個股新聞。AKShare是一個優秀的Python金融數據接口庫，無需API密鑰，但需要確保已正確安裝：

```bash
pip install akshare
```

註意：AKShare的东方財富新聞功能會自動用於A股和港股的新聞獲取，無需額外配置。

### 2.3 導入必要模塊

```python
# 導入基本工具包
from tradingagents.agents.utils.agent_utils import Toolkit

# 如果需要使用新聞分析師
from langchain_openai import ChatOpenAI
from tradingagents.agents.analysts.news_analyst import create_news_analyst
```

## 3. 獲取實時新聞

### 3.1 使用實時新聞聚合器

```python
# 創建工具包實例
toolkit = Toolkit()

# 獲取特定股票的實時新聞
ticker = "AAPL"  # 股票代碼
curr_date = "2023-07-01"  # 當前日期
news_report = toolkit.get_realtime_stock_news(ticker, curr_date)

print(news_report)
```

實時新聞聚合器會返回一個格式化的新聞報告，包含：
- 生成時間
- 新聞总數
- 緊急新聞（高緊急程度）
- 重要新聞（中緊急程度）
- 一般新聞（低緊急程度）
- 數據時效性評估

### 3.2 使用統一新聞接口

統一新聞接口能夠自動识別股票類型並選擇合適的新聞源：

```python
# 使用統一接口獲取新聞
# A股示例
cn_ticker = "000001"  # A股股票
news_report = toolkit.get_stock_news_unified(cn_ticker, curr_date)
print(news_report)

# 美股示例
us_ticker = "AAPL"  # 美股股票
us_news = toolkit.get_stock_news_unified(us_ticker, curr_date)
print(us_news)

# 港股示例
hk_ticker = "00700"  # 港股股票
hk_news = toolkit.get_stock_news_unified(hk_ticker, curr_date)
print(hk_news)
```

統一新聞接口會根據股票類型自動選擇合適的新聞源：
- **A股和港股**：同時獲取东方財富新聞和Google新聞
- **美股**：獲取Finnhub新聞

### 3.3 直接獲取东方財富新聞

如果您只需要獲取东方財富網的個股新聞，可以直接使用AKShare接口：

```python
from tradingagents.dataflows.akshare_utils import get_stock_news_em

# 獲取特定股票的东方財富新聞
ticker = "000001"  # 股票代碼（不帶後缀）
news_df = get_stock_news_em(ticker)

# 顯示新聞標題和時間
for _, row in news_df.iterrows():
    print(f"標題: {row['標題']}")
    print(f"時間: {row['時間']}")
    print(f"鏈接: {row['鏈接']}")
    print("---")
```

## 4. 使用新聞分析師

新聞分析師是一個專業的財經新聞分析智能體，能夠分析新聞對股票價格的潜在影響：

```python
# 創建LLM和工具包
llm = ChatOpenAI()  # 使用OpenAI模型
toolkit = Toolkit()

# 創建新聞分析師
news_analyst = create_news_analyst(llm, toolkit)

# 準备狀態
state = {
    "trade_date": "2023-07-01",
    "company_of_interest": "AAPL",
    "messages": []
}

# 執行新聞分析
result = news_analyst(state)

# 獲取分析報告
print(result["news_report"])
```

新聞分析師的分析報告包含：
- 新聞對股價短期影響的分析
- 預期的波動幅度
- 價格調整建议
- 支撑位和阻力位分析
- 對長期投資價值的影響分析
- 新聞時效性限制說明

## 5. 獲取全球宏觀經濟新聞

```python
# 獲取全球宏觀經濟新聞
global_news = toolkit.get_global_news_openai(curr_date)
print(global_news)
```

## 6. 高級用法

### 6.1 自定義新聞源優先級

您可以自定義實時新聞聚合器的新聞源優先級：

```python
from tradingagents.dataflows.realtime_news_utils import RealtimeNewsAggregator

# 創建自定義新聞聚合器
aggregator = RealtimeNewsAggregator(
    finnhub_enabled=True,
    alpha_vantage_enabled=True,
    newsapi_enabled=False,  # 禁用NewsAPI
    chinese_finance_enabled=True,  # 啟用中文財經新聞（包括东方財富新聞）
    akshare_enabled=True  # 啟用AKShare东方財富新聞
)

# 獲取新聞
news_items = aggregator.get_news(ticker, curr_date)

# 格式化報告
report = aggregator.format_news_report(news_items, ticker, curr_date)
print(report)
```

### 6.2 自定義緊急程度評估

您可以自定義新聞緊急程度評估的關键詞：

```python
from tradingagents.dataflows.realtime_news_utils import RealtimeNewsAggregator

# 自定義緊急程度關键詞
high_urgency_keywords = ["破產", "诉讼", "收購", "合並", "FDA批準", "盈利警告"]
medium_urgency_keywords = ["財報", "業绩", "合作", "新產品", "市場份額"]

# 創建自定義新聞聚合器
aggregator = RealtimeNewsAggregator()

# 設置自定義關键詞
aggregator.high_urgency_keywords = high_urgency_keywords
aggregator.medium_urgency_keywords = medium_urgency_keywords

# 獲取新聞
news_items = aggregator.get_news(ticker, curr_date)

# 格式化報告
report = aggregator.format_news_report(news_items, ticker, curr_date)
print(report)
```

## 7. 最佳實踐

1. **優先使用實時新聞聚合器**：對於需要最新市場動態的場景，優先使用 `get_realtime_stock_news` 方法。

2. **使用統一接口處理多市場**：當需要分析不同市場（A股、港股、美股）的股票時，使用 `get_stock_news_unified` 方法可以自動選擇合適的新聞源。

3. **利用东方財富新聞**：對於A股和港股分析，系統會自動獲取东方財富網的專業財經新聞，提供更準確的中文市場信息。

4. **結合全球宏觀新聞**：使用 `get_global_news_openai` 獲取全球宏觀經濟新聞，与股票特定新聞結合分析，獲得更全面的市場視角。

5. **註意API密鑰配置**：確保已正確配置 FinnHub、Alpha Vantage、NewsAPI 等服務的API密鑰，以獲取完整的新聞數據。

6. **考慮時效性**：新聞的時效性對投資決策至關重要，始终關註新聞發布時間与當前時間的差距。

7. **定期更新關键詞**：根據市場變化和投資策略，定期更新緊急程度評估的關键詞，以提高新聞分析的準確性。

## 8. 故障排除

### 8.1 API限制問題

如果遇到API限制問題，可以嘗試以下解決方案：

- 减少API調用頻率
- 使用API密鑰轮換策略
- 優先使用本地緩存數據

### 8.2 新聞质量問題

如果新聞质量不佳，可以嘗試以下解決方案：

- 調整緊急程度評估的關键詞
- 增加新聞源的數量
- 使用更專業的財經新聞源

## 9. 总結

新聞分析系統提供了全面的新聞獲取和分析功能，能夠從多個數據源獲取實時新聞，並進行專業的分析和評估。統一的新聞獲取接口使得系統能夠自動识別股票類型並選擇合適的新聞源，提供格式化的新聞分析報告。新聞分析師能夠分析新聞對股票價格的潜在影響，提供量化的交易建议和價格影響評估。

系統現已集成AKShare的东方財富新聞功能，為A股和港股提供更專業、更本地化的中文財經新聞，大幅提升了中文市場的新聞覆蓋率和分析準確性。

通過本指南，您應该能夠熟練使用TradingAgentsCN系統中的新聞分析功能，為您的投資決策提供重要參考。