# DeepSeek V3配置指南

## 📋 概述

DeepSeek V3是一個性能强大、性價比極高的大語言模型，在推理、代碼生成和中文理解方面表現優秀。本指南将詳細介紹如何在TradingAgents中配置和使用DeepSeek V3。

## 🎯 v0.1.5 新增功能

- ✅ **完整的DeepSeek V3集成**：支持全系列模型
- ✅ **工具調用支持**：完整的Function Calling功能
- ✅ **OpenAI兼容API**：使用標準OpenAI接口
- ✅ **Web界面支持**：在Web界面中選擇DeepSeek模型
- ✅ **智能體協作**：支持多智能體協作分析

## 🔑 獲取API密鑰

### 第一步：註冊DeepSeek账號
1. 訪問 [DeepSeek平台](https://platform.deepseek.com/)
2. 點擊"Sign Up"註冊账號
3. 使用邮箱或手機號完成註冊
4. 驗證邮箱或手機號

### 第二步：獲取API密鑰
1. 登錄DeepSeek控制台
2. 進入"API Keys"页面
3. 點擊"Create API Key"
4. 設置密鑰名稱（如：TradingAgents）
5. 複制生成的API密鑰（格式：sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx）

## ⚙️ 配置步骤

### 1. 環境變量配置

在項目根目錄的`.env`文件中添加：

```bash
# DeepSeek V3配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_ENABLED=true
```

### 2. 支持的模型

| 模型名稱 | 說明 | 適用場景 | 上下文長度 | 推薦度 |
|---------|------|---------|-----------|--------|
| **deepseek-chat** | 通用對話模型 | 股票投資分析、推薦使用 | 128K | ⭐⭐⭐⭐⭐ |

**說明**：
- ✅ **deepseek-chat**：最適合股票投資分析，平衡了技術分析和自然語言表達
- ⚠️ **deepseek-coder**：虽然支持工具調用，但專註代碼任務，在投資建议表達方面不如通用模型
- ❌ **deepseek-reasoner**：不支持工具調用，不適用於TradingAgents的智能體架構

### 3. Web界面配置

1. 啟動Web界面：`streamlit run web/app.py`
2. 進入"配置管理"页面
3. 在"模型配置"中找到DeepSeek模型
4. 填入API Key
5. 啟用相應的模型

## 🛠️ 使用方法

### 1. CLI使用

```bash
# 啟動CLI
python -m cli.main

# 選擇DeepSeek V3作為LLM提供商
# 選擇DeepSeek模型
# 開始分析
```

### 2. Web界面使用

1. 在分析页面選擇DeepSeek模型
2. 輸入股票代碼
3. 選擇分析深度
4. 開始分析

### 3. 編程接口

```python
from tradingagents.llm.deepseek_adapter import create_deepseek_adapter

# 創建DeepSeek適配器
adapter = create_deepseek_adapter(model="deepseek-chat")

# 獲取模型信息
info = adapter.get_model_info()
print(f"使用模型: {info['model']}")

# 創建智能體
from langchain.tools import tool

@tool
def get_stock_price(symbol: str) -> str:
    """獲取股票價格"""
    return f"股票{symbol}的價格信息"

agent = adapter.create_agent(
    tools=[get_stock_price],
    system_prompt="你是股票分析專家"
)

# 執行分析
result = agent.invoke({"input": "分析AAPL股票"})
print(result["output"])
```

## 🎯 最佳實踐

### 1. 模型選擇建议

- **日常分析**：使用deepseek-chat，通用性强，性價比高
- **逻辑分析**：使用deepseek-coder，逻辑推理能力强
- **深度推理**：使用deepseek-reasoner，複雜問題分析
- **長文本**：優先使用deepseek-chat，支持128K上下文

### 2. 參數調優

```python
# 推薦的參數設置
adapter = create_deepseek_adapter(
    model="deepseek-chat",
    temperature=0.1,  # 降低隨機性，提高一致性
    max_tokens=2000   # 適中的輸出長度
)
```

### 3. 成本控制

- DeepSeek V3價格極低，約為GPT-4的1/10
- 輸入：¥0.14/百万tokens
- 輸出：¥0.28/百万tokens
- 適合大量使用，成本壓力小

## 🔍 故障排除

### 常见問題

#### 1. API密鑰錯誤
```
錯誤：Authentication failed
解決：檢查API Key是否正確，確保以sk-開头
```

#### 2. 網絡連接問題
```
錯誤：Connection timeout
解決：檢查網絡連接，確保可以訪問api.deepseek.com
```

#### 3. 配置未生效
```
錯誤：DeepSeek not enabled
解決：確保DEEPSEEK_ENABLED=true
```

### 調試方法

1. **檢查配置**：
```python
from tradingagents.llm.deepseek_adapter import DeepSeekAdapter
print(DeepSeekAdapter.is_available())
```

2. **測試連接**：
```bash
python tests/test_deepseek_integration.py
```

3. **查看日誌**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 性能對比

| 指標 | DeepSeek V3 | GPT-4 | Claude-3 | 阿里百炼 |
|------|-------------|-------|----------|---------|
| **推理能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **中文理解** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **工具調用** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **響應速度** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **成本效益** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **穩定性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 💰 定價優势

### DeepSeek V3定價
- **輸入**：¥0.14/百万tokens
- **輸出**：¥0.28/百万tokens
- **平均**：約¥0.21/百万tokens

### 成本對比
- **vs GPT-4**：便宜約90%
- **vs Claude-3**：便宜約85%
- **vs 阿里百炼**：便宜約50%

### 實际使用成本
- **日常分析**：約¥0.01/次
- **深度分析**：約¥0.05/次
- **月度使用**：約¥10-50（重度使用）

## 🎉 总結

DeepSeek V3為TradingAgents提供了：

- 🧠 **强大的推理能力**：媲美GPT-4的分析水平
- 💰 **極高的性價比**：成本仅為GPT-4的1/10
- 🛠️ **完整的工具支持**：Function Calling功能完善
- 🇨🇳 **優秀的中文能力**：專門優化的中文理解
- 📊 **專業的分析能力**：適合金融數據分析
- 🚀 **快速的響應速度**：API響應穩定快速

通過DeepSeek V3，您可以享受到高质量、低成本的AI股票分析服務！
