# DeepSeek V3 使用指南

## 📋 概述

本指南詳細介紹如何在TradingAgents-CN中使用DeepSeek V3進行股票投資分析。DeepSeek V3是一個高性價比的大語言模型，特別適合中文金融分析場景。

## 🚀 快速開始

### 1. 環境準备

#### 獲取API密鑰
1. 訪問 [DeepSeek平台](https://platform.deepseek.com/)
2. 註冊账號並完成認證
3. 進入控制台 → API Keys
4. 創建新的API Key
5. 複制API Key（格式：sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx）

#### 配置環境變量
```bash
# 編辑.env文件
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_ENABLED=true
```

### 2. 驗證配置

```bash
# 測試API連接
python -c "
import os
from dotenv import load_dotenv
from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek

load_dotenv()
llm = ChatDeepSeek(model='deepseek-chat')
response = llm.invoke('你好，請簡單介紹DeepSeek')
print('✅ DeepSeek連接成功')
print('響應:', response.content[:100])
"
```

## 💰 成本優势

### 定價對比
| 模型 | 輸入Token | 輸出Token | 相對GPT-4成本 |
|------|-----------|-----------|---------------|
| **DeepSeek V3** | ¥0.001/1K | ¥0.002/1K | **節省90%+** |
| GPT-4 | ¥0.03/1K | ¥0.06/1K | 基準 |
| GPT-3.5 | ¥0.0015/1K | ¥0.002/1K | 節省75% |

### 成本計算示例
```python
# 典型股票分析的Token使用量
輸入Token: ~2,000 (股票數據 + 分析提示)
輸出Token: ~1,500 (分析報告)

# DeepSeek V3成本
成本 = (2000 * 0.001 + 1500 * 0.002) / 1000 = ¥0.005

# GPT-4成本  
成本 = (2000 * 0.03 + 1500 * 0.06) / 1000 = ¥0.15

# 節省: 97%
```

## 📊 使用方式

### 1. Web界面使用

#### 啟動Web界面
```bash
streamlit run web/app.py
```

#### 操作步骤
1. **選擇模型**：在左侧邊栏選擇"DeepSeek V3"
2. **配置參數**：
   - 模型：deepseek-chat
   - 溫度：0.1（推薦，確保分析一致性）
   - 最大Token：2000（適中長度）
3. **輸入股票代碼**：如000001、600519、AAPL等
4. **選擇分析師**：建议選擇"基本面分析師"
5. **開始分析**：點擊"開始分析"按钮

#### 結果查看
- **決策摘要**：投資建议和關键指標
- **詳細報告**：完整的基本面分析
- **Token統計**：實時的使用量和成本
- **配置信息**：使用的模型和參數

### 2. CLI界面使用

#### 啟動CLI
```bash
python -m cli.main
```

#### 交互流程
1. **選擇LLM提供商**：選擇"DeepSeek V3"
2. **選擇模型**：選擇"deepseek-chat"
3. **輸入股票代碼**：輸入要分析的股票
4. **選擇分析師**：選擇需要的分析師類型
5. **查看結果**：等待分析完成並查看報告

### 3. Python API使用

#### 基础使用
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 配置DeepSeek
config = DEFAULT_CONFIG.copy()
config.update({
    "llm_provider": "deepseek",
    "llm_model": "deepseek-chat",
    "quick_think_llm": "deepseek-chat",
    "deep_think_llm": "deepseek-chat",
    "backend_url": "https://api.deepseek.com",
})

# 創建分析圖
ta = TradingAgentsGraph(
    selected_analysts=["fundamentals"],
    config=config
)

# 執行分析
result = ta.run_analysis("000001", "2025-01-08")
print(result)
```

#### 高級配置
```python
from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek

# 創建自定義DeepSeek實例
llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.1,        # 降低隨機性
    max_tokens=2000,        # 適中輸出長度
    session_id="my_session" # 會話級別統計
)

# 直接調用
response = llm.invoke(
    "分析平安銀行(000001)的投資價值",
    session_id="analysis_001",
    analysis_type="fundamentals"
)
```

## 📈 分析功能

### 1. 基本面分析

#### 支持的指標
- **估值指標**：PE、PB、PS、股息收益率
- **盈利能力**：ROE、ROA、毛利率、净利率
- **財務健康**：資產负债率、流動比率、速動比率
- **成長性**：營收增長率、利润增長率

#### 分析輸出
```python
# 示例輸出
{
    "investment_advice": "买入",
    "confidence": 0.75,
    "risk_score": 0.3,
    "fundamental_score": 7.5,
    "valuation_score": 8.0,
    "growth_score": 6.5,
    "key_metrics": {
        "PE": 5.2,
        "PB": 0.65,
        "ROE": 12.5,
        "debt_ratio": 0.15
    }
}
```

### 2. 多智能體協作

#### 支持的分析師
- **基本面分析師**：財務指標和投資價值分析
- **技術分析師**：技術指標和趋势分析
- **新聞分析師**：新聞事件影響分析
- **社交媒體分析師**：市場情绪分析

#### 協作流程
```python
# 多分析師協作
ta = TradingAgentsGraph(
    selected_analysts=["fundamentals", "market", "news"],
    config=config
)

# 獲得综合分析結果
result = ta.run_analysis("AAPL", "2025-01-08")
```

## 🔧 高級配置

### 1. 性能優化

#### 推薦參數
```python
# 快速分析（成本優先）
config = {
    "temperature": 0.1,
    "max_tokens": 1000,
    "max_debate_rounds": 1
}

# 深度分析（质量優先）
config = {
    "temperature": 0.05,
    "max_tokens": 3000,
    "max_debate_rounds": 2
}
```

#### 緩存策略
```python
# 啟用緩存减少重複調用
config["enable_cache"] = True
config["cache_ttl"] = 3600  # 1小時緩存
```

### 2. Token管理

#### 使用量監控
```python
from tradingagents.config.config_manager import config_manager

# 查看使用統計
stats = config_manager.get_usage_statistics(days=7)
print(f"7天总成本: ¥{stats['total_cost']:.4f}")
print(f"DeepSeek使用: {stats['provider_stats']['deepseek']}")
```

#### 成本控制
```python
# 設置成本警告
config_manager.update_settings({
    "cost_alert_threshold": 10.0,  # ¥10警告阈值
    "enable_cost_tracking": True
})
```

## 🧪 測試和驗證

### 1. 功能測試

#### 基础連接測試
```bash
python tests/test_deepseek_integration.py
```

#### 基本面分析測試
```bash
python tests/test_fundamentals_analysis.py
```

#### Token統計測試
```bash
python tests/test_deepseek_token_tracking.py
```

### 2. 性能測試

#### 響應時間測試
```python
import time
start_time = time.time()
result = llm.invoke("簡單分析AAPL")
end_time = time.time()
print(f"響應時間: {end_time - start_time:.2f}秒")
```

#### 並發測試
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def concurrent_analysis():
    with ThreadPoolExecutor(max_workers=3) as executor:
        tasks = [
            executor.submit(ta.run_analysis, "000001", "2025-01-08"),
            executor.submit(ta.run_analysis, "600519", "2025-01-08"),
            executor.submit(ta.run_analysis, "AAPL", "2025-01-08")
        ]
        results = [task.result() for task in tasks]
    return results
```

## 🐛 故障排除

### 常见問題

#### 1. API密鑰錯誤
```
錯誤：Authentication failed
解決：檢查DEEPSEEK_API_KEY是否正確配置
```

#### 2. 網絡連接問題
```
錯誤：Connection timeout
解決：檢查網絡連接，確認能訪問api.deepseek.com
```

#### 3. Token統計不準確
```
問題：顯示¥0.0000
解決：檢查API響應中的usage字段，啟用調試模式
```

### 調試方法

#### 啟用詳細日誌
```bash
export TRADINGAGENTS_LOG_LEVEL=DEBUG
python your_script.py
```

#### 檢查API響應
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看詳細的API調用信息
```

## 📚 最佳實踐

### 1. 成本控制
- 使用緩存减少重複調用
- 設置合理的max_tokens限制
- 監控每日使用量和成本

### 2. 分析质量
- 使用較低的temperature（0.1）確保一致性
- 選擇合適的分析師組合
- 驗證分析結果的合理性

### 3. 系統穩定性
- 配置錯誤重試機制
- 使用fallback模型
- 定期檢查API密鑰余額

---

通過本指南，您應该能夠充分利用DeepSeek V3的高性價比優势，進行專業的股票投資分析。如有問題，請參考故障排除部分或提交GitHub Issue。
