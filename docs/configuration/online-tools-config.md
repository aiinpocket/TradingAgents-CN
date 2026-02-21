# 在線工具配置指南

## 📋 概述

TradingAgents-CN 現在提供了更精細的在線工具控制機制，您可以通過環境變量靈活配置系統的在線/離線行為，而不再依賴於特定LLM提供商的啟用狀態。

## 🔧 配置字段說明

### 主要配置字段

| 環境變量 | 默認值 | 說明 |
|---------|--------|------|
| `ONLINE_TOOLS_ENABLED` | `false` | 在線工具總開關 |
| `ONLINE_NEWS_ENABLED` | `true` | 在線新聞工具開關 |
| `REALTIME_DATA_ENABLED` | `false` | 實時數據獲取開關 |

### 配置優先級

1. **環境變量** (.env文件) - 最高優先級
2. **默認配置** (default_config.py) - 備用默認值

## 🎯 配置模式

### 1. 開發模式 (完全離線)
```bash
# .env 文件配置
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=false
REALTIME_DATA_ENABLED=false
```

**特點:**
- ✅ 完全使用緩存數據
- ✅ 零API調用成本
- ✅ 適合開發和調試
- ❌ 數據可能不是最新的

### 2. 測試模式 (部分在線)
```bash
# .env 文件配置
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
```

**特點:**
- ✅ 新聞數據實時獲取
- ✅ 股價數據使用緩存
- ✅ 平衡功能和成本
- ✅ 適合功能測試

### 3. 生產模式 (完全在線)
```bash
# .env 文件配置
ONLINE_TOOLS_ENABLED=true
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=true
```

**特點:**
- ✅ 獲取最新實時數據
- ✅ 適合實盤交易
- ❌ API調用成本較高
- ❌ 需要穩定網絡連接

## 🛠️ 配置方法

### 方法1: 修改 .env 文件
```bash
# 編辑 .env 文件
nano .env

# 添加或修改以下配置
ONLINE_TOOLS_ENABLED=true
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
```

### 方法2: 環境變量設置
```bash
# Windows PowerShell
$env:ONLINE_TOOLS_ENABLED="true"
$env:ONLINE_NEWS_ENABLED="true"
$env:REALTIME_DATA_ENABLED="false"

# Linux/macOS
export ONLINE_TOOLS_ENABLED=true
export ONLINE_NEWS_ENABLED=true
export REALTIME_DATA_ENABLED=false
```

### 方法3: 代碼中動態配置
```python
from tradingagents.default_config import DEFAULT_CONFIG

# 創建自定義配置
config = DEFAULT_CONFIG.copy()
config["online_tools"] = True
config["online_news"] = True
config["realtime_data"] = False

# 使用自定義配置
from tradingagents.graph.trading_graph import TradingAgentsGraph
ta = TradingAgentsGraph(config=config)
```

## 🔍 配置驗證

### 使用測試腳本驗證
```bash
python test_online_tools_config.py
```

### 手動驗證配置
```python
from tradingagents.default_config import DEFAULT_CONFIG

print("當前配置:")
print(f"在線工具: {DEFAULT_CONFIG['online_tools']}")
print(f"在線新聞: {DEFAULT_CONFIG['online_news']}")
print(f"實時數據: {DEFAULT_CONFIG['realtime_data']}")
```

## 📊 工具影響範圍

### 受 `ONLINE_TOOLS_ENABLED` 控制的工具
- 所有需要API調用的數據獲取工具
- 實時股價數據獲取
- 在線技術指標計算

### 受 `ONLINE_NEWS_ENABLED` 控制的工具
- `get_google_news` - Google新聞獲取
- `get_finnhub_social_sentiment` - FinnHub 情緒數據

### 受 `REALTIME_DATA_ENABLED` 控制的工具
- 實時股價數據
- 實時市場指數
- 實時交易量數據

## ⚠️ 註意事項

### 1. 配置衝突處理
- 如果 `ONLINE_TOOLS_ENABLED=false` 但 `ONLINE_NEWS_ENABLED=true`，新聞工具仍然可用
- 這種設計允許更精細的控制

### 2. API配額管理
- 在線模式會消耗API配額
- 建議在開發階段使用離線模式
- 生產環境根據需要選擇合適的模式

### 3. 網絡依賴
- 在線模式需要穩定的網絡連接
- 網絡異常時會自動回退到緩存數據

## 🔄 遷移指南

### 從舊配置遷移
如果您之前使用的是基於 `OPENAI_ENABLED` 的配置：

**舊方式:**
```bash
OPENAI_ENABLED=false  # 這會影響整個系統的在線狀態
```

**新方式:**
```bash
OPENAI_ENABLED=false        # 只控制OpenAI模型
ONLINE_TOOLS_ENABLED=false  # 專門控制在線工具
ONLINE_NEWS_ENABLED=true    # 精細控制新聞工具
```

## 🎯 最佳實踐

### 1. 開發階段
```bash
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=false
REALTIME_DATA_ENABLED=false
```

### 2. 測試階段
```bash
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
```

### 3. 生產環境
```bash
ONLINE_TOOLS_ENABLED=true
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=true
```

## 🔧 故障排除

### 常見問題

1. **配置不生效**
   - 檢查 .env 文件是否正確加載
   - 確認環境變量格式正確 (true/false)

2. **工具調用失敗**
   - 檢查相關API密鑰是否配置
   - 確認網絡連接是否正常

3. **數據不是最新的**
   - 確認 `REALTIME_DATA_ENABLED=true`
   - 檢查數據源API是否正常

### 調試命令
```bash
# 檢查當前配置
python -c "from tradingagents.default_config import DEFAULT_CONFIG; print(DEFAULT_CONFIG)"

# 測試配置系統
python test_online_tools_config.py

# 檢查環境變量
echo $ONLINE_TOOLS_ENABLED
echo $ONLINE_NEWS_ENABLED
echo $REALTIME_DATA_ENABLED
```

---

通過這個新的配置系統，您可以更精確地控制TradingAgents-CN的在線行為，在功能需求和成本控制之間找到最佳平衡點。