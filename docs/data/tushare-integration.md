# Tushare數據源集成指南

本指南介紹如何在TradingAgents中集成和使用Tushare數據源，獲取高质量的中國A股市場數據。

## 📊 Tushare簡介

Tushare是一個免費、開源的Python財經數據接口包，主要實現對股票等金融數據從數據採集、清洗加工到數據存储的過程，能夠為金融分析人員提供快速、整潔、和多樣的便於分析的數據。

### 主要特點

- **數據全面**: 覆蓋股票、基金、期貨、债券等多種金融產品
- **數據质量高**: 數據來源權威，經過清洗和驗證
- **更新及時**: 提供實時和歷史數據
- **接口簡單**: Python原生接口，易於使用
- **免費使用**: 基础功能免費，高級功能需要積分

## 🚀 快速開始

### 1. 註冊Tushare账號

1. 訪問 [Tushare官網](https://tushare.pro/register)
2. 註冊账號並完成邮箱驗證
3. 登錄後在個人中心獲取API Token

### 2. 安裝依賴

```bash
# Tushare已包含在項目依賴中
pip install tushare>=1.4.21
```

### 3. 配置環境變量

在項目根目錄創建或編辑 `.env` 文件：

```bash
# Tushare API Token
TUSHARE_TOKEN=your_tushare_token_here

# 設置默認A股數據源為Tushare
DEFAULT_CHINA_DATA_SOURCE=tushare

# 啟用數據緩存
ENABLE_DATA_CACHE=true
```

### 4. 驗證配置

運行測試腳本驗證配置：

```bash
python tests/test_tushare_integration.py
```

## 📚 使用方法

### 命令行界面 (CLI)

```bash
# 啟動CLI
python -m cli.main

# 選擇分析中國股票
# 系統會自動使用Tushare數據源
```

### Web界面

```bash
# 啟動Web界面
python -m streamlit run web/app.py

# 在配置页面選擇Tushare作為A股數據源
```

### API接口

```python
from tradingagents.dataflows import (
    get_china_stock_data_tushare,
    search_china_stocks_tushare,
    get_china_stock_fundamentals_tushare,
    get_china_stock_info_tushare
)

# 獲取股票歷史數據
data = get_china_stock_data_tushare("000001", "2024-01-01", "2024-12-31")

# 搜索股票
results = search_china_stocks_tushare("平安銀行")

# 獲取基本面數據
fundamentals = get_china_stock_fundamentals_tushare("000001")

# 獲取股票基本信息
info = get_china_stock_info_tushare("000001")
```

### 直接使用適配器

```python
from tradingagents.dataflows.tushare_adapter import get_tushare_adapter

# 獲取適配器實例
adapter = get_tushare_adapter()

# 獲取股票數據
data = adapter.get_stock_data("000001", "2024-01-01", "2024-12-31")

# 獲取股票信息
info = adapter.get_stock_info("000001")

# 搜索股票
results = adapter.search_stocks("平安")

# 獲取基本面數據
fundamentals = adapter.get_fundamentals("000001")
```

## 🔧 高級配置

### 緩存配置

Tushare集成支持多種緩存方式：

```bash
# 文件緩存 (默認)
CACHE_TYPE=file

# Redis緩存
CACHE_TYPE=redis
REDIS_HOST=localhost
REDIS_PORT=6379

# MongoDB緩存
CACHE_TYPE=mongodb
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

### API限制配置

```bash
# API調用頻率限制 (每分鐘)
TUSHARE_API_RATE_LIMIT=200

# API超時設置 (秒)
TUSHARE_API_TIMEOUT=30

# 並發請求數量
MAX_CONCURRENT_REQUESTS=5
```

### 數據源回退

```bash
# 备用數據源
FALLBACK_DATA_SOURCES=akshare,baostock

# 自動切換
AUTO_FALLBACK_ENABLED=true
```

## 📊 支持的數據類型

### 1. 股票基础數據

- **股票列表**: 獲取所有A股股票基本信息
- **股票信息**: 股票名稱、行業、地区等基本信息
- **歷史行情**: 日線、周線、月線數據
- **實時行情**: 最新價格和交易數據

### 2. 財務數據

- **資產负债表**: 公司資產、负债、股东權益
- **利润表**: 營業收入、利润、費用等
- **現金流量表**: 經營、投資、筹資活動現金流
- **財務指標**: PE、PB、ROE等關键指標

### 3. 市場數據

- **交易日歷**: 交易日、節假日信息
- **股票分類**: 行業分類、概念分類
- **指數數據**: 上證指數、深證成指等

## 🎯 最佳實踐

### 1. API使用優化

```python
# 批量獲取數據
symbols = ["000001", "000002", "600036"]
for symbol in symbols:
    data = adapter.get_stock_data(symbol, start_date, end_date)
    # 處理數據...
    time.sleep(0.1)  # 避免頻率限制
```

### 2. 緩存策略

```python
# 啟用緩存以提高性能
adapter = get_tushare_adapter()  # 默認啟用緩存

# 對於頻繁訪問的數據，設置合適的緩存時間
# 日線數據: 24小時
# 基本信息: 7天
# 財務數據: 30天
```

### 3. 錯誤處理

```python
try:
    data = adapter.get_stock_data("000001", start_date, end_date)
    if data.empty:
        print("未獲取到數據")
    else:
        # 處理數據
        pass
except Exception as e:
    print(f"數據獲取失败: {e}")
    # 使用备用數據源或緩存數據
```

## 🔍 故障排除

### 常见問題

1. **Token無效**
   ```
   錯誤: 無效的token
   解決: 檢查TUSHARE_TOKEN是否正確設置
   ```

2. **API調用超限**
   ```
   錯誤: 調用頻率超限
   解決: 降低調用頻率或升級账號權限
   ```

3. **網絡連接問題**
   ```
   錯誤: 連接超時
   解決: 檢查網絡連接，增加超時時間
   ```

4. **數據為空**
   ```
   錯誤: 返回空數據
   解決: 檢查股票代碼和日期範围是否正確
   ```

### 調試模式

啟用詳細日誌以便調試：

```bash
# 在.env文件中設置
LOG_LEVEL=DEBUG
ENABLE_VERBOSE_LOGGING=true
```

## 📈 性能優化

### 1. 緩存優化

- 啟用Redis或MongoDB緩存以提高性能
- 設置合適的緩存過期時間
- 定期清理過期緩存

### 2. 並發優化

- 使用連接池减少連接開銷
- 控制並發請求數量避免API限制
- 實現請求隊列管理

### 3. 數據預取

- 預先獲取常用股票數據
- 批量獲取减少API調用次數
- 使用異步請求提高效率

## 🔄 版本更新

### v0.1.6 新特性

- ✅ 完整的Tushare API集成
- ✅ 智能緩存機制
- ✅ 多數據源回退
- ✅ 統一接口設計
- ✅ 性能優化

### 後续計劃

- 🔄 實時數據推送
- 🔄 更多財務指標
- 🔄 技術指標計算
- 🔄 新聞情感分析

## 📞 技術支持

- **GitHub Issues**: 問題報告和功能請求
- **文档**: 詳細的API文档和示例
- **社区**: 用戶交流和經驗分享

---

**註意**: Tushare的高級功能需要積分，建议根據使用需求選擇合適的套餐。
