# TradingAgents-CN 大模型接入指導手冊

## 📋 概述

本手冊旨在幫助開發者為 TradingAgents-CN 項目添加新的大模型支持。通過遵循本指南，您可以快速集成新的大模型提供商，並提交高质量的 Pull Request。

## 🎯 適用場景

- 添加新的大模型提供商（如智谱、腾讯、百度等）
- 為現有提供商添加新模型
- 修複或優化現有 LLM 適配器
- 添加新的 API 兼容方式

## 🏗️ 系統架構概覽

TradingAgents 的 LLM 集成基於以下架構：

```
tradingagents/
├── llm_adapters/              # LLM 適配器實現
│   ├── __init__.py           # 導出所有適配器
│   ├── openai_compatible_base.py  # OpenAI 兼容基類 (核心)
│   ├── dashscope_adapter.py       # 阿里百炼適配器
│   ├── dashscope_openai_adapter.py # 阿里百炼 OpenAI 兼容適配器  
│   ├── deepseek_adapter.py        # DeepSeek 原生適配器
│   ├── deepseek_direct_adapter.py # DeepSeek 直接適配器
│   └── google_openai_adapter.py   # Google AI 適配器
└── web/
    ├── components/sidebar.py  # 前端模型選擇界面
    └── utils/analysis_runner.py  # 運行時配置与流程編排
```

### 核心組件

1. 適配器基類: <mcsymbol name="OpenAICompatibleBase" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="32" type="class"></mcsymbol> —— 為所有 OpenAI 兼容的 LLM 提供統一實現，是新增提供商最重要的擴展點 <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile>
2. 工厂方法: <mcsymbol name="create_openai_compatible_llm" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="329" type="function"></mcsymbol> —— 運行時根據提供商与模型創建對應的適配器實例（建议優先使用）
3. 提供商註冊: 在 <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile> 中的 `OPENAI_COMPATIBLE_PROVIDERS` 字典 —— 統一管理 base_url、API Key 環境變量名、受支持模型等（單一信息源）
4. 前端集成: <mcfile name="sidebar.py" path="web/components/sidebar.py"></mcfile> —— 模型選擇界面负责把用戶選擇的 llm_provider 和 llm_model 傳遞到後端
5. 運行時入口: <mcfile name="trading_graph.py" path="tradingagents/graph/trading_graph.py"></mcfile> 中統一使用工厂方法創建 LLM；<mcfile name="analysis_runner.py" path="web/utils/analysis_runner.py"></mcfile> 仅作為參數傳遞与流程編排，通常無需為新增提供商做修改

## 🚀 快速開始

### 第一步：環境準备

1. **Fork 並克隆仓庫**

   ```bash
   git clone https://github.com/your-username/TradingAgentsCN.git
   cd TradingAgentsCN
   ```
2. **安裝依賴**

   ```bash
   pip install -e .
   # 或使用 uv
   uv pip install -e .
   ```
3. **創建開發分支**

   ```bash
   git checkout develop
   git checkout -b feature/add-{provider_name}-llm
   ```

### 第二步：選擇集成方式

根據目標大模型的 API 類型，選擇適合的集成方式：

#### 方式一：OpenAI 兼容 API（推薦）

適用於：支持 OpenAI API 格式的模型（如智谱、MiniMax、月之暗面等）

**優势**：

- 開發工作量最小
- 複用現有的工具調用逻辑
- 統一的錯誤處理和日誌記錄

> 备註：百度千帆（Qianfan）已通過 OpenAI 兼容方式集成，provider 名稱為 `qianfan`，只需配置 `QIANFAN_API_KEY`。相關細節见專項文档 QIANFAN_INTEGRATION_GUIDE.md；pricing.json 已包含 ERNIE 系列占位價格，支持在 Web 配置页調整。

#### 方式二：原生 API 適配器

適用於：非 OpenAI 兼容格式的模型

**需要更多工作**：

- 需要自定義消息格式轉換
- 需要實現工具調用逻辑
- 需要處理特定的錯誤格式

## 📝 實現指南

### OpenAI 兼容適配器開發

#### 1. 創建適配器文件

在 `tradingagents/llm_adapters/` 下創建新文件：

```python
# tradingagents/llm_adapters/your_provider_adapter.py

from .openai_compatible_base import OpenAICompatibleBase
import os
from tradingagents.utils.tool_logging import log_llm_call
import logging

logger = logging.getLogger(__name__)

class ChatYourProvider(OpenAICompatibleBase):
    """你的提供商 OpenAI 兼容適配器"""
  
    def __init__(
        self,
        model: str = "your-default-model",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> None:
        super().__init__(
            provider_name="your_provider",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key_env_var="YOUR_PROVIDER_API_KEY",
            base_url="https://api.yourprovider.com/v1",
            **kwargs
        )
```

#### 2. 在基類中註冊提供商

編辑 `tradingagents/llm_adapters/openai_compatible_base.py`：

```python
# 在 OPENAI_COMPATIBLE_PROVIDERS 字典中添加配置
OPENAI_COMPATIBLE_PROVIDERS = {
    # ... 現有配置 ...
  
    "your_provider": {
        "adapter_class": ChatYourProvider,
        "base_url": "https://api.yourprovider.com/v1",
        "api_key_env": "YOUR_PROVIDER_API_KEY",
        "models": {
            "your-model-1": {"context_length": 8192, "supports_function_calling": True},
            "your-model-2": {"context_length": 32768, "supports_function_calling": True},
        }
    },
}
```

#### 3. 更新導入文件

編辑 `tradingagents/llm_adapters/__init__.py`：

```python
from .your_provider_adapter import ChatYourProvider

__all__ = ["ChatDashScope", "ChatDashScopeOpenAI", "ChatGoogleOpenAI", "ChatYourProvider"]
```

#### 4. 前端集成

編辑 `web/components/sidebar.py`，在模型選擇部分添加：

```python
# 在 llm_provider 選擇中添加選項
options=["dashscope", "deepseek", "google", "openai", "openrouter", "custom_openai", "your_provider"],

# 在格式化映射中添加
format_mapping={
    # ... 現有映射 ...
    "your_provider": "🚀 您的提供商",
}

# 添加模型選擇逻辑
elif llm_provider == "your_provider":
    your_provider_options = ["your-model-1", "your-model-2"]
  
    current_index = 0
    if st.session_state.llm_model in your_provider_options:
        current_index = your_provider_options.index(st.session_state.llm_model)
  
    llm_model = st.selectbox(
        "選擇模型",
        options=your_provider_options,
        index=current_index,
        format_func=lambda x: {
            "your-model-1": "Model 1 - 快速",
            "your-model-2": "Model 2 - 强大",
        }.get(x, x),
        help="選擇用於分析的模型",
        key="your_provider_model_select"
    )
```

#### 5. 運行時配置

在絕大多數情况下，新增一個 OpenAI 兼容提供商時，無需修改 <mcfile name="analysis_runner.py" path="web/utils/analysis_runner.py"></mcfile>。原因：

- 侧邊栏 <mcfile name="sidebar.py" path="web/components/sidebar.py"></mcfile> 收集 `llm_provider` 与 `llm_model`
- 這些參數會被傳入 <mcfile name="trading_graph.py" path="tradingagents/graph/trading_graph.py"></mcfile>，由 <mcsymbol name="create_openai_compatible_llm" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="329" type="function"></mcsymbol> 基於 `OPENAI_COMPATIBLE_PROVIDERS` 自動實例化正確的適配器
- 因此，真正的“運行時配置”主要體現在 <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile> 的註冊表和工厂方法，而非 analysis_runner 本身

推薦做法：

- 在 <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile> 中完善 `OPENAI_COMPATIBLE_PROVIDERS`（base_url、api_key 環境變量、模型清單等）
- 在 <mcfile name="sidebar.py" path="web/components/sidebar.py"></mcfile> 中新增该 `llm_provider` 的下拉選項与模型列表
- 保持 <mcfile name="analysis_runner.py" path="web/utils/analysis_runner.py"></mcfile> 無需改動

何時需要少量修改 analysis_runner：

- 该提供商要求在分析階段動態切換不同模型（例如“快速/深度”分開）
- 需要在任務執行流水線中註入特定的 header、代理或文件型鑒權
- 需要為该提供商設置額外的日誌或成本估算逻辑

即便如此，也請：

- 不在 analysis_runner 硬編碼模型清單或 API 細節，統一放在 `OPENAI_COMPATIBLE_PROVIDERS`
- 仍然使用 <mcsymbol name="create_openai_compatible_llm" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="329" type="function"></mcsymbol> 創建實例，避免重複初始化逻辑

編辑 `web/utils/analysis_runner.py`，在模型配置部分添加：

```python
elif llm_provider == "your_provider":
    config["backend_url"] = "https://api.yourprovider.com/v1"
    logger.info(f"🚀 [您的提供商] 使用模型: {llm_model}")
    logger.info(f"🚀 [您的提供商] API端點: https://api.yourprovider.com/v1")
```

### 📋 必需的環境變量

在項目根目錄的 `.env.example` 文件中添加：

```bash
# 您的提供商 API 配置
YOUR_PROVIDER_API_KEY=your_api_key_here
```

## 🧪 測試指南

### 1. 基础連接測試

創建測試文件 `test_your_provider.py`：

```python
import os
from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider

def test_basic_connection():
    """測試基础連接"""
    # 設置測試環境變量
    os.environ["YOUR_PROVIDER_API_KEY"] = "your_test_key"
  
    try:
        llm = ChatYourProvider(model="your-model-1")
        response = llm.invoke("Hello, world!")
        print(f"✅ 連接成功: {response.content}")
        return True
    except Exception as e:
        print(f"❌ 連接失败: {e}")
        return False

if __name__ == "__main__":
    test_basic_connection()
```

### 2. 工具調用測試

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """獲取城市天气信息"""
    return f"{city}今天晴天，溫度25°C"

def test_function_calling():
    """測試工具調用"""
    llm = ChatYourProvider(model="your-model-1")
    llm_with_tools = llm.bind_tools([get_weather])
  
    response = llm_with_tools.invoke("北京天气如何？")
    print(f"工具調用測試: {response}")
```

### 3. Web 界面測試

啟動 Web 應用進行集成測試：

```bash
cd web
streamlit run app.py
```

驗證：

- [ ]  在侧邊栏能正確選擇新提供商
- [ ]  模型選擇下拉菜單工作正常
- [ ]  API 密鑰檢查顯示正確狀態
- [ ]  能成功進行股票分析

## 📊 驗證清單

提交 PR 前，請確保以下項目都已完成：

### 代碼實現

- [ ]  創建了適配器類並繼承正確的基類
- [ ]  在 `OPENAI_COMPATIBLE_PROVIDERS` 中正確註冊
- [ ]  更新了 `__init__.py` 導入
- [ ]  前端集成完整（模型選擇、配置界面）
- [ ]  運行時配置正確

### 環境配置

- [ ]  添加了環境變量示例到 `.env.example`
- [ ]  API 密鑰驗證逻辑正確
- [ ]  錯誤處理完善

### 測試驗證

- [ ]  基础連接測試通過
- [ ]  工具調用測試通過（如果支持）
- [ ]  Web 界面集成測試通過
- [ ]  至少完成一次完整的股票分析

### 文档更新

- [ ]  更新了相關 README 文档
- [ ]  添加了模型特性說明
- [ ]  提供了使用示例

## 💡 實际接入案例：百度千帆模型

### 案例背景

百度千帆模型是一個典型的國產大模型接入案例，在實际接入過程中遇到了一些特殊問題，以下是完整的解決方案。

### 接入步骤詳解

#### 1. 使用 OpenAI 兼容基座註冊千帆提供商

```python
# 在 tradingagents/llm_adapters/openai_compatible_base.py 內部註冊
OPENAI_COMPATIBLE_PROVIDERS["qianfan"] = {
    "base_url": "https://qianfan.baidubce.com/v2",
    "api_key_env": "QIANFAN_API_KEY",
    "models": {
        "ernie-3.5-8k": {"context_length": 8192, "supports_function_calling": True},
        "ernie-4.0-turbo-8k": {"context_length": 8192, "supports_function_calling": True},
        "ERNIE-Speed-8K": {"context_length": 8192, "supports_function_calling": True},
        "ERNIE-Lite-8K": {"context_length": 8192, "supports_function_calling": False},
    }
}
```

> 提示：無需單獨的 qianfan_adapter.py 文件，統一由 openai_compatible_base 進行適配。

#### 2. 註冊千帆提供商

```python
# 在 openai_compatible_base.py 中添加
OPENAI_COMPATIBLE_PROVIDERS = {
    # ... 現有配置 ...
  
    "qianfan": {
        "base_url": "https://qianfan.baidubce.com/v2",
        "api_key_env": "QIANFAN_API_KEY",
        "models": {
            "ernie-3.5-8k": {"context_length": 8192, "supports_function_calling": True},
            "ernie-4.0-turbo-8k": {"context_length": 8192, "supports_function_calling": True},
            "ERNIE-Lite-8K": {"context_length": 8192, "supports_function_calling": False},
            "ERNIE-Speed-8K": {"context_length": 8192, "supports_function_calling": True},
        }
    },
}
```

#### 3. 配置環境變量

在 `.env` 文件中添加千帆API配置：

```bash
# 千帆API配置
QIANFAN_ACCESS_KEY=your_access_key_here
QIANFAN_SECRET_KEY=your_secret_key_here
```

#### 4. 添加模型價格配置

在 `config/pricing.json` 文件中添加千帆模型的價格信息：

```json
{
  "provider": "qianfan",
  "model_name": "ernie-3.5-8k",
  "input_price_per_1k": 0.0025,
  "output_price_per_1k": 0.005,
  "currency": "CNY"
},
{
  "provider": "qianfan",
  "model_name": "ernie-4.0-turbo-8k",
  "input_price_per_1k": 0.03,
  "output_price_per_1k": 0.09,
  "currency": "CNY"
},
{
  "provider": "qianfan",
  "model_name": "ERNIE-Speed-8K",
  "input_price_per_1k": 0.0004,
  "output_price_per_1k": 0.0008,
  "currency": "CNY"
},
{
  "provider": "qianfan",
  "model_name": "ERNIE-Lite-8K",
  "input_price_per_1k": 0.0008,
  "output_price_per_1k": 0.002,
  "currency": "CNY"
}
```

**價格說明**：
- 價格單位為每1000個token的費用
- 貨币單位為人民币（CNY）
- 價格基於百度千帆官方定價，可能會有調整

#### 5. 前端界面集成

```python
# 在 sidebar.py 中添加千帆選項
elif llm_provider == "qianfan":
    qianfan_options = [
        "ernie-3.5-8k",
        "ernie-4.0-turbo-8k",
        "ERNIE-Speed-8K",
        "ERNIE-Lite-8K"
    ]

    current_index = 0
    if st.session_state.llm_model in qianfan_options:
        current_index = qianfan_options.index(st.session_state.llm_model)

    llm_model = st.selectbox(
        "選擇文心一言模型",
        options=qianfan_options,
        index=current_index,
        format_func=lambda x: {
            "ernie-3.5-8k": "ERNIE 3.5 8K - ⚡ 快速高效",
            "ernie-4.0-turbo-8k": "ERNIE 4.0 Turbo 8K - 🚀 强大推理",
            "ERNIE-Speed-8K": "ERNIE Speed 8K - 🏃 極速響應",
            "ERNIE-Lite-8K": "ERNIE Lite 8K - 💡 轻量經濟"
        }[x],
        help="選擇用於分析的文心一言（千帆）模型",
        key="qianfan_model_select"
    )

    if st.session_state.llm_model != llm_model:
        logger.debug(f"🔄 [Persistence] Qianfan模型變更: {st.session_state.llm_model} → {llm_model}")
    st.session_state.llm_model = llm_model
    logger.debug(f"💾 [Persistence] Qianfan模型已保存: {llm_model}")
```


## 🚨 常见問題与解決方案

### 1. API 密鑰驗證失败

**問題**: 環境變量設置正確但仍提示 API 密鑰錯誤

**解決方案**:

- 檢查 API 密鑰格式是否符合提供商要求
- 確認環境變量名稱拼寫正確
- 檢查 `.env` 文件是否在正確位置
- **千帆特殊情况**: 需要同時設置 `QIANFAN_API_KEY`

### 2. 工具調用不工作

**問題**: 模型不能正確調用工具

**解決方案**:

- 確認模型本身支持 Function Calling
- 檢查 API 格式是否完全兼容 OpenAI 標準
- 查看是否需要特殊的工具調用格式
- **千帆特殊情况**: 需要轉換工具定義格式，參考上述案例

### 3. 前端界面不顯示新模型

**問題**: 侧邊栏看不到新添加的提供商

**解決方案**:

- 清除浏覽器緩存
- 檢查 `sidebar.py` 中的選項列表
- 確認 Streamlit 重新加載了代碼
- **調試技巧**: 在浏覽器開發者工具中查看控制台錯誤

### 4. 請求超時或連接錯誤

**問題**: API 請求經常超時

**解決方案**:

- 調整 `timeout` 參數
- 檢查網絡連接和 API 端點狀態
- 考慮添加重試機制
- **國產模型特殊情况**: 某些國產模型服務器在海外訪問較慢，建议增加超時時間

### 5. 中文編碼問題

**問題**: 中文輸入或輸出出現乱碼

**解決方案**:

```python
# 確保請求和響應都使用 UTF-8 編碼
import json

def safe_json_dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2)

def safe_json_loads(text):
    return json.loads(text.encode('utf-8').decode('utf-8'))
```
### 6. 成本控制問題

**問題**: 某些模型調用成本過高

**解決方案**:

- 在配置中設置合理的 `max_tokens` 限制
- 使用成本較低的模型進行初步分析
- 實現智能模型路由，根據任務複雜度選擇模型

```python
# 智能模型選擇示例
def select_model_by_task(task_complexity: str) -> str:
    if task_complexity == "simple":
        return "ERNIE-Lite-8K"  # 成本低
    elif task_complexity == "medium":
        return "ERNIE-3.5-8K"  # 平衡
    else:
        return "ERNIE-4.0-8K"  # 性能强
```
## 📝 PR 提交規範

### 提交信息格式

```
feat(llm): add {ProviderName} LLM integration

- Add {ProviderName} OpenAI-compatible adapter
- Update frontend model selection UI
- Add configuration and environment variables
- Include basic tests and documentation

Closes #{issue_number}
```
### PR 描述模板

```markdown
## 🚀 新增大模型支持：{ProviderName}

### 📋 變更概述
- 添加了 {ProviderName} 的 OpenAI 兼容適配器
- 更新了前端模型選擇界面
- 完善了配置和環境變量
- 包含了基础測試

### 🧪 測試情况
- [x] 基础連接測試通過
- [x] 工具調用測試通過（如適用）
- [x] Web 界面集成測試通過
- [x] 完整的股票分析測試通過

### 📚 支持的模型
- `model-1`: 快速模型，適合簡單任務
- `model-2`: 强大模型，適合複雜分析

### 🔧 配置要求
需要設置環境變量：`YOUR_PROVIDER_API_KEY`

### 📸 截圖
（添加前端界面截圖）

### ✅ 檢查清單
- [x] 代碼遵循項目規範
- [x] 添加了必要的測試
- [x] 更新了相關文档
- [x] 通過了所有現有測試
```
## 🎯 最佳實踐

### 1. 錯誤處理

- 提供清晰的錯誤消息
- 区分不同類型的錯誤（API 密鑰、網絡、模型等）
- 添加重試機制處理臨時故障

### 2. 日誌記錄

- 使用統一的日誌格式
- 記錄關键操作和錯誤
- 避免記錄敏感信息（API 密鑰等）

### 3. 性能優化

- 合理設置超時時間
- 考慮並發限制
- 優化大模型調用的 token 使用

### 4. 用戶體驗

- 提供清晰的模型選擇說明
- 添加合適的幫助文本
- 確保錯誤消息用戶友好

## 📞 獲取幫助

如果在開發過程中遇到問題：

1. **查看現有實現**: 參考 `deepseek_adapter.py` 或 `dashscope_adapter.py`
2. **阅讀基類文档**: 查看 `openai_compatible_base.py` 的註釋
3. **提交 Issue**: 在 GitHub 上創建問題描述
4. **加入討論**: 參与項目的 Discussion 板塊

## 🔄 版本控制建议

1. **分支命名**: `feature/add-{provider}-llm`
2. **提交頻率**: 小步骤頻繁提交
3. **提交信息**: 使用清晰的描述性信息
4. **代碼審查**: 提交前自我審查代碼质量

---

**感谢您為 TradingAgentsCN 項目贡献新的大模型支持！** 🎉

通過遵循本指南，您的贡献将更容易被審查和合並，同時也為其他開發者提供了良好的參考示例。
