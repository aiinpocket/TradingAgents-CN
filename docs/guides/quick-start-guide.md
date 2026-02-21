---
version: cn-0.1.14-preview
last_updated: 2025-01-13
code_compatibility: cn-0.1.14-preview
status: updated
---

# TradingAgents-CN 快速開始指南

> **版本說明**: 本文檔基於 `cn-0.1.14-preview` 版本編寫  
> **最後更新**: 2025-01-13  
> **狀態**: ✅ 已更新 - 5分鐘快速上手指南

## 🚀 5分鐘快速上手

### 前提條件
- ✅ 已完成[安裝配置](./installation-guide.md)
- ✅ 已配置至少一個LLM API密鑰
- ✅ 虛擬環境已激活

### 1. 驗證安裝
```bash
# 運行安裝驗證腳本
python examples/test_installation.py

# 應該看到 "🎉 恭喜！安裝驗證全部通過！"
```

### 2. 啟動應用
```bash
# 啟動Web應用
python start_web.py

# 或直接使用streamlit
cd web && streamlit run app.py
```

### 3. 訪問界面
打開瀏覽器訪問: http://localhost:8501

### 4. 首次配置

#### 選擇LLM提供商
在左側邊欄選擇你已配置的LLM提供商：
- **OpenAI** - GPT-4、GPT-4o-mini
- **Anthropic** - Claude 4 系列

#### 選擇模型
根據你的需求選擇具體模型：
- **高性能**: GPT-4、Claude Sonnet
- **經濟**: GPT-4o-mini

### 5. 第一次分析

#### 美股分析示例
```
股票代碼: AAPL
分析日期: 2024-01-15
```

```
股票代碼: TSLA
分析日期: 2024-01-15
```

## 📊 界面功能介紹

### 左側邊欄
- **LLM配置**: 選擇AI模型提供商和具體模型
- **分析參數**: 設置分析日期、股票代碼
- **高級選項**: 配置分析深度、資料來源等

### 主界面
- **股票輸入**: 輸入要分析的股票代碼
- **分析結果**: 顯示AI生成的分析報告
- **圖表展示**: 股價走勢、技術指標圖表
- **成本統計**: 顯示API調用成本

### 分析報告內容
- **基本面分析**: 財務指標、估值分析
- **技術面分析**: 技術指標、趨勢分析
- **市場情緒**: 新聞分析、社交媒體情緒
- **投資建議**: 綜合評分和操作建議

## 🎯 使用場景示例

### 場景1: 日常股票分析
```
目標: 分析某只股票的投資價值
步驟:
1. 選擇GPT-4模型 (高品質分析)
2. 輸入股票代碼: AAPL
3. 設置當前日期
4. 點擊"開始分析"
5. 查看綜合分析報告
```

### 場景2: 批量股票篩選
```
目標: 從多只股票中篩選投資標的
步驟:
1. 選擇經濟型模型 (降低成本)
2. 逐個分析候選股票
3. 對比分析結果
4. 記錄投資評分
5. 選擇最優標的
```

### 場景3: 技術分析驗證
```
目標: 驗證技術分析信號
步驟:
1. 選擇專業技術分析模型
2. 輸入技術信號股票
3. 查看AI技術分析結論
4. 對比自己的判斷
5. 制定交易策略
```

## ⚙️ 常用配置

### 模型選擇建議

#### 高品質分析 (成本較高)
- **OpenAI GPT-4**: 最佳分析品質
- **Anthropic Claude Sonnet**: 強大的推理分析

#### 經濟選擇 (推薦)
- **GPT-4o-mini**: 性價比最佳

### 資料來源配置

#### 美股資料來源優先級
1. **Yahoo Finance** - 免費可靠
2. **FinnHub** - 專業資料
3. **Alpha Vantage** - 備用選擇

## 🔧 高級功能

### 1. 自定義分析提示詞
```python
# 在config/prompts/目錄下創建自定義提示詞
# 例如: custom_analysis.txt
```

### 2. 批量分析腳本
```python
# 使用Python腳本進行批量分析
from tradingagents import TradingAgent

agent = TradingAgent()
stocks = ['AAPL', 'MSFT', 'GOOGL']
for stock in stocks:
    result = agent.analyze(stock)
    print(f"{stock}: {result.recommendation}")
```

### 3. 定時分析任務
```bash
# 使用cron設置定時任務 (Linux/macOS)
0 9 * * 1-5 cd /path/to/TradingAgents-CN && python scripts/daily_analysis.py

# 使用任務計劃程序 (Windows)
# 創建每日9點執行的任務
```

## 📈 性能優化

### 1. 啟用緩存
```bash
# 在.env文件中啟用Redis緩存
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 2. 並發設置
```python
# 在config/settings.json中調整
{
  "max_workers": 4,
  "request_timeout": 30
}
```

### 3. 數據緩存
```bash
# 設置數據緩存時間 (秒)
DATA_CACHE_TTL=3600
```

## 🚨 注意事項

### 1. API成本控制
- 選擇合適的模型平衡品質和成本
- 使用快取避免重複請求
- 監控每日API使用量

### 2. 資料準確性
- 驗證股票代碼格式
- 注意交易日期和時區
- 關注資料來源的更新頻率

### 3. 投資風險
- AI分析僅供參考，不構成投資建議
- 結合多種分析方法
- 控制投資風險

## 🆘 常見問題

### Q: 分析結果不準確怎么辦？
A: 
1. 檢查股票代碼是否正確
2. 確認分析日期是否為交易日
3. 嘗試更換數據源或模型
4. 查看日誌文件排查問題

### Q: API調用失敗怎么辦？
A:
1. 檢查網絡連接
2. 驗證API密鑰有效性
3. 確認API額度是否充足
4. 查看錯誤日誌詳細信息

### Q: 如何降低使用成本？
A:
1. 選擇經濟型模型
2. 啟用緩存功能
3. 避免重複分析
4. 設置使用限額

## 📚 進階學習

完成快速開始後，建議繼續學習：

1. **[配置管理指南](./config-management-guide.md)** - 深入配置
2. **[美股分析指南](./us-stock-analysis-guide.md)** - 美股專項
3. **[API開發指南](../development/api-development-guide.md)** - 二次開發
4. **[故障排除指南](../troubleshooting/)** - 問題解決

---

**開始你的AI投資分析之旅！** 🚀
