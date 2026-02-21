# Token使用統計和成本跟蹤指南 (v0.1.7)

本指南介紹如何配置和使用TradingAgents-CN的Token使用統計和成本跟蹤功能，包括v0.1.7新增的

## 功能概述

TradingAgents提供了完整的Token使用統計和成本跟蹤功能，包括：

- **實時Token統計**: 自動記錄每次LLM調用的輸入和輸出token數量
- **成本計算**: 根據不同供應商的定價自動計算使用成本
- **多存储支持**: 支持JSON文件存储和MongoDB數據庫存储
- **統計分析**: 提供詳細的使用統計和成本分析
- **成本警告**: 當使用成本超過閾值時自動提醒

## 支持的LLM供應商

目前支持以下LLM供應商的Token統計：

- ✅ **
- ✅ **
- ✅ **Google AI**: 完全支持，Gemini系列模型token統計
- 🔄 **OpenAI**: 計劃支持
- 🔄 **Anthropic**: 計劃支持

## 配置方法

### 1. 基礎配置

在項目根目錄建立或編輯 `.env` 文件：

```bash
# 啟用成本跟蹤（預設啟用）
ENABLE_COST_TRACKING=true

# 成本警告閾值
COST_ALERT_THRESHOLD=100.0

# AI模型API密鑰
OPENAI_API_KEY=your_openai_key
```

### 2. 存储配置

#### 選項1: JSON文件存储（默認）

默認情況下，Token使用記錄保存在 `config/usage.json` 文件中。

```bash
# 最大記錄數量（默認10000）
MAX_USAGE_RECORDS=10000

# 自動保存使用記錄（默認啟用）
AUTO_SAVE_USAGE=true
```

#### 選項2: MongoDB存储（推薦用於生產環境）

對於大量數據和高性能需求，推薦使用MongoDB存储：

```bash
# 啟用MongoDB存储
USE_MONGODB_STORAGE=true

# MongoDB連接字符串
# 本地MongoDB
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/

# 或云MongoDB（如MongoDB Atlas）
# MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/

# 數據庫名稱
MONGODB_DATABASE_NAME=tradingagents
```

### 3. 安裝MongoDB依賴（如果使用MongoDB存储）

```bash
pip install pymongo
```

## 使用方法

### 1. 自動Token統計

當使用

```python
from tradingagents.llm_adapters.
from langchain_core.messages import HumanMessage

# 初始化LLM
llm = Chat
    model="gpt-4o-mini",
    temperature=0.7
)

# 發送消息（自動記錄token使用）
response = llm.invoke([
    HumanMessage(content="分析一下苹果公司的股票")
], session_id="my_session", analysis_type="stock_analysis")
```

### 2. 查看使用統計

```python
from tradingagents.config.config_manager import config_manager

# 獲取最近30天的統計
stats = config_manager.get_usage_statistics(30)

print(f"總成本: ¥{stats['total_cost']:.4f}")
print(f"總請求數: {stats['total_requests']}")
print(f"輸入tokens: {stats['total_input_tokens']}")
print(f"輸出tokens: {stats['total_output_tokens']}")

# 按供應商查看統計
for provider, provider_stats in stats['provider_stats'].items():
    print(f"{provider}: ¥{provider_stats['cost']:.4f}")
```

### 3. 查看會話成本

```python
from tradingagents.config.config_manager import token_tracker

# 查看特定會話的成本
session_cost = token_tracker.get_session_cost("my_session")
print(f"會話成本: ¥{session_cost:.4f}")
```

### 4. 估算成本

```python
# 估算成本（用於預算規劃）
estimated_cost = token_tracker.estimate_cost(
    provider="
    model_name="gpt-4o-mini",
    estimated_input_tokens=1000,
    estimated_output_tokens=500
)
print(f"估算成本: ¥{estimated_cost:.4f}")
```

## 定價配置

系統內置了主要LLM供應商的定價信息，也可以自定義定價：

```python
from tradingagents.config.config_manager import config_manager, PricingConfig

# 添加自定義定價
custom_pricing = PricingConfig(
    provider="
    model_name="gpt-4o",
    input_price_per_1k=0.02,   # 每1000個輸入token的價格（人民幣）
    output_price_per_1k=0.06,  # 每1000個輸出token的價格（人民幣）
    currency="CNY"
)

pricing_list = config_manager.load_pricing()
pricing_list.append(custom_pricing)
config_manager.save_pricing(pricing_list)
```

## 內置定價表

### 

| 模型 | 輸入價格 (¥/1K tokens) | 輸出價格 (¥/1K tokens) |
|------|----------------------|----------------------|
| gpt-4o-mini | 0.002 | 0.006 |
| gpt-4o | 0.004 | 0.012 |
| gpt-4o | 0.02 | 0.06 |

### OpenAI

| 模型 | 輸入價格 ($/1K tokens) | 輸出價格 ($/1K tokens) |
|------|----------------------|----------------------|
| gpt-3.5-turbo | 0.0015 | 0.002 |
| gpt-4 | 0.03 | 0.06 |
| gpt-4-turbo | 0.01 | 0.03 |

## 測試Token統計功能

運行測試腳本驗證功能：

```bash
# 測試
python tests/test_
```

## MongoDB存储優勢

使用MongoDB存储相比JSON文件存储有以下優勢：

1. **高性能**: 支持大量數據的高效查詢和聚合
2. **可擴展性**: 支持分布式部署和水平擴展
3. **數據安全**: 支持備份、複制和故障恢復
4. **高級查詢**: 支持複雜的聚合查詢和統計分析
5. **並發支持**: 支持多用戶並發訪問

### MongoDB索引優化

系統會自動創建以下索引以提高查詢性能：

- 複合索引：`(timestamp, provider, model_name)`
- 單字段索引：`session_id`, `analysis_type`

## 成本控制建議

1. **設置合理的成本警告閾值**
2. **定期查看使用統計，優化使用模式**
3. **根據需求選擇合適的模型（平衡成本和性能）**
4. **使用會話ID跟蹤特定分析的成本**
5. **定期清理舊的使用記錄（MongoDB支持自動清理）**

## 故障排除

### 1. Token統計不工作

- 檢查API密鑰是否正確配置
- 確認 `ENABLE_COST_TRACKING=true`
- 查看控制台是否有錯誤信息

### 2. MongoDB連接失敗

- 檢查MongoDB服務是否運行
- 驗證連接字符串格式
- 確認網絡連接和防火墙設置
- 檢查用戶權限

### 3. 成本計算不準確

- 檢查定價配置是否正確
- 確認模型名稱匹配
- 驗證token提取邏輯

## 最佳實踐

1. **生產環境使用MongoDB存储**
2. **定期備份使用數據**
3. **監控成本趨勢，及時調整策略**
4. **使用有意義的會話ID和分析類型**
5. **定期更新定價信息**

## 未來計劃

- [ ] 支持更多LLM供應商的Token統計
- [ ] 添加可視化儀表板
- [ ] 支持成本預算和限制
- [ ] 添加使用報告導出功能
- [ ] 支持團隊和用戶級別的成本跟蹤