# DeepSeek集成說明

本文档記錄了DeepSeek V3模型的集成過程和技術細節。

## 🎯 集成目標

- 支持DeepSeek V3高性價比大語言模型
- 提供完整的Token使用統計
- 確保与現有系統的兼容性
- 優化中文輸出质量

## 🔧 技術實現

### 1. DeepSeek適配器
- **文件**: `tradingagents/llm_adapters/deepseek_adapter.py`
- **功能**: 支持Token統計的DeepSeek聊天模型
- **特性**: 繼承ChatOpenAI，添加使用量跟蹤

### 2. Token統計功能
- 自動提取API響應中的token使用量
- 智能估算fallback機制
- 集成到TokenTracker系統
- 支持會話級別成本跟蹤

### 3. 系統集成
- **TradingGraph**: 自動使用DeepSeek適配器
- **配置管理**: 支持DeepSeek相關配置
- **成本跟蹤**: 完整的使用成本統計

## 📊 性能特點

### 成本優势
- **輸入Token**: ¥0.001/1K tokens
- **輸出Token**: ¥0.002/1K tokens
- **性價比**: 相比GPT-4顯著降低成本

### 质量表現
- **中文理解**: 優秀的中文語言理解能力
- **專業分析**: 適合金融分析任務
- **推理能力**: 强大的逻辑推理能力

## 🚀 使用方法

### 配置設置
```bash
# .env文件配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 代碼使用
```python
from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek

# 創建DeepSeek實例
llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.1,
    max_tokens=2000
)

# 調用模型
response = llm.invoke("分析一下股票市場")
```

## 📈 集成效果

### 功能驗證
- ✅ Token使用統計正常
- ✅ 成本計算準確
- ✅ 中文輸出優质
- ✅ 系統集成穩定

### 用戶體驗
- 顯著降低使用成本
- 保持分析质量
- 提供透明的成本統計
- 支持高並發使用

---

更多技術細節請參考相關代碼和測試文件。
