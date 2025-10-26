# TradingAgents-CN API接口規範

## 📋 概述

本文档詳細描述了TradingAgents-CN系統中各個模塊的API接口規範，包括輸入參數、輸出格式、錯誤處理等。

---

## 🔧 核心API接口

### 1. 統一基本面分析工具

#### 接口定義
```python
def get_stock_fundamentals_unified(
    ticker: str,
    start_date: str,
    end_date: str,
    curr_date: str
) -> str
```

#### 輸入參數
```json
{
    "ticker": "002027",           // 股票代碼 (必填)
    "start_date": "2025-06-01",   // 開始日期 (必填)
    "end_date": "2025-07-15",     // 結束日期 (必填)
    "curr_date": "2025-07-15"     // 當前日期 (必填)
}
```

#### 輸出格式
```markdown
# 中國A股基本面分析報告 - 002027

## 📊 股票基本信息
- **股票代碼**: 002027
- **股票名稱**: 分眾傳媒
- **所屬行業**: 廣告包裝
- **當前股價**: ¥7.67
- **涨跌幅**: -1.41%

## 💰 財務數據分析
### 估值指標
- **PE比率**: 18.5倍
- **PB比率**: 1.8倍
- **股息收益率**: 2.5%

### 盈利能力
- **ROE**: 12.8%
- **ROA**: 6.2%
- **毛利率**: 25.5%

## 📈 投資建议
综合評分: 6.5/10
建议: 谨慎持有
```

### 2. 市場技術分析工具

#### 接口定義
```python
def get_stock_market_analysis(
    ticker: str,
    period: str = "1y",
    indicators: List[str] = None
) -> str
```

#### 輸入參數
```json
{
    "ticker": "002027",
    "period": "1y",
    "indicators": ["SMA", "EMA", "RSI", "MACD", "BOLL"]
}
```

#### 輸出格式
```markdown
# 市場技術分析報告 - 002027

## 📈 價格趋势分析
- **當前趋势**: 震荡下行
- **支撑位**: ¥7.12
- **阻力位**: ¥7.87

## 📊 技術指標
- **RSI(14)**: 45.2 (中性)
- **MACD**: -0.05 (看跌)
- **布林帶**: 價格接近下轨

## 🎯 技術面建议
短期: 觀望
中期: 谨慎
```

### 3. 新聞情绪分析工具

#### 接口定義
```python
def get_stock_news_analysis(
    ticker: str,
    company_name: str,
    date_range: str = "7d"
) -> str
```

#### 輸入參數
```json
{
    "ticker": "002027",
    "company_name": "分眾傳媒",
    "date_range": "7d"
}
```

#### 輸出格式
```markdown
# 新聞分析報告 - 002027

## 📰 新聞概覽
- **新聞总數**: 15條
- **正面新聞**: 8條 (53%)
- **负面新聞**: 3條 (20%)
- **中性新聞**: 4條 (27%)

## 🔥 熱點事件
1. Q2財報發布，業绩超預期
2. 新增重要客戶合作
3. 行業政策調整影響

## 📊 情绪指數
- **整體情绪**: 偏正面 (65%)
- **關註熱度**: 中等
- **影響評估**: 短期正面
```

---

## 🤖 智能體API接口

### 1. 基本面分析師

#### 接口定義
```python
def fundamentals_analyst(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 輸入狀態
```json
{
    "company_of_interest": "002027",
    "trade_date": "2025-07-15",
    "messages": [],
    "fundamentals_report": ""
}
```

#### 輸出狀態
```json
{
    "company_of_interest": "002027",
    "trade_date": "2025-07-15",
    "messages": [...],
    "fundamentals_report": "詳細的基本面分析報告..."
}
```

### 2. 市場分析師

#### 接口定義
```python
def market_analyst(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 輸入狀態
```json
{
    "company_of_interest": "002027",
    "trade_date": "2025-07-15",
    "messages": [],
    "market_report": ""
}
```

#### 輸出狀態
```json
{
    "company_of_interest": "002027",
    "trade_date": "2025-07-15",
    "messages": [...],
    "market_report": "詳細的市場分析報告..."
}
```

### 3. 看涨/看跌研究員

#### 接口定義
```python
def bull_researcher(state: Dict[str, Any]) -> Dict[str, Any]
def bear_researcher(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 輸入狀態
```json
{
    "company_of_interest": "002027",
    "trade_date": "2025-07-15",
    "fundamentals_report": "基本面分析報告...",
    "market_report": "市場分析報告...",
    "investment_debate_state": {
        "history": "",
        "current_response": "",
        "count": 0
    }
}
```

#### 輸出狀態
```json
{
    "investment_debate_state": {
        "history": "辩論歷史...",
        "current_response": "當前回應...",
        "count": 1
    }
}
```

### 4. 交易員

#### 接口定義
```python
def trader(state: Dict[str, Any]) -> Dict[str, Any]
```

#### 輸入狀態
```json
{
    "company_of_interest": "002027",
    "trade_date": "2025-07-15",
    "fundamentals_report": "基本面分析...",
    "market_report": "市場分析...",
    "news_report": "新聞分析...",
    "sentiment_report": "情绪分析...",
    "investment_debate_state": {
        "history": "研究員辩論歷史..."
    }
}
```

#### 輸出狀態
```json
{
    "trader_signal": "詳細的交易決策信號...",
    "final_decision": {
        "action": "买入",
        "target_price": 8.50,
        "confidence": 0.75,
        "risk_score": 0.4,
        "reasoning": "基於综合分析的投資理由..."
    }
}
```

---

## 📊 數據源API接口

### 1. Tushare數據接口

#### 股票基本數據
```python
def get_china_stock_data_tushare(
    ticker: str,
    start_date: str,
    end_date: str
) -> str
```

#### 股票信息
```python
def get_china_stock_info_tushare(ticker: str) -> Dict[str, Any]
```

### 2. 統一數據接口

#### 中國股票數據
```python
def get_china_stock_data_unified(
    symbol: str,
    start_date: str,
    end_date: str
) -> str
```

#### 數據源切換
```python
def switch_china_data_source(source: str) -> bool
```

---

## 🔧 工具API接口

### 1. 股票工具類

#### 市場信息獲取
```python
def get_market_info(ticker: str) -> Dict[str, Any]
```

#### 返回格式
```json
{
    "ticker": "002027",
    "market": "china_a",
    "market_name": "中國A股",
    "currency_name": "人民币",
    "currency_symbol": "¥",
    "is_china": true,
    "is_hk": false,
    "is_us": false
}
```

### 2. 緩存管理API

#### 緩存操作
```python
def get_cache(key: str) -> Any
def set_cache(key: str, value: Any, ttl: int = 3600) -> bool
def clear_cache(pattern: str = "*") -> int
```

---

## ⚠️ 錯誤處理

### 錯誤代碼規範

| 錯誤代碼 | 錯誤類型 | 描述 |
|---------|---------|------|
| 1001 | 參數錯誤 | 必填參數缺失或格式錯誤 |
| 1002 | 股票代碼錯誤 | 股票代碼不存在或格式錯誤 |
| 2001 | 數據源錯誤 | 外部API調用失败 |
| 2002 | 緩存錯誤 | 緩存系統異常 |
| 3001 | LLM錯誤 | 語言模型調用失败 |
| 3002 | 分析錯誤 | 分析過程異常 |
| 4001 | 系統錯誤 | 系統內部錯誤 |

### 錯誤響應格式
```json
{
    "success": false,
    "error_code": 1002,
    "error_message": "股票代碼格式錯誤",
    "error_details": "股票代碼應為6位數字",
    "timestamp": "2025-07-16T01:30:00Z"
}
```

---

## 🔒 安全規範

### 1. API密鑰管理
- 所有API密鑰通過環境變量配置
- 支持密鑰轮換和失效檢測
- 密鑰格式驗證和安全存储

### 2. 訪問控制
- 基於角色的訪問控制 (RBAC)
- API調用頻率限制
- 請求來源驗證

### 3. 數據安全
- 傳輸數據加密 (HTTPS)
- 敏感數據脫敏處理
- 審計日誌記錄

---

## 📈 性能規範

### 1. 響應時間要求
- 數據獲取: < 5秒
- 單個分析師: < 30秒
- 完整分析流程: < 3分鐘

### 2. 並發處理
- 支持最多10個並發分析請求
- 智能隊列管理
- 資源使用監控

### 3. 緩存策略
- 熱數據緩存: 1小時
- 溫數據緩存: 24小時
- 冷數據緩存: 7天

---

## 🧪 測試規範

### 1. 單元測試
- 每個API接口都有對應的單元測試
- 測試覆蓋率要求 > 80%
- 包含正常和異常情况測試

### 2. 集成測試
- 端到端流程測試
- 數據源集成測試
- LLM集成測試

### 3. 性能測試
- 负載測試
- 壓力測試
- 穩定性測試
