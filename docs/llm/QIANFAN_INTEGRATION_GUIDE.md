# 百度千帆模型接入指南

## 📋 概述

本指南專門针對百度千帆（文心一言）模型的接入過程，結合項目的最新實現，提供“OpenAI 兼容模式”的推薦用法，並保留“原生 AK/SK + Access Token”方式的歷史說明（仅供參考）。

## 🎯 推薦接入模式：OpenAI 兼容（仅需 QIANFAN_API_KEY）

- 使用統一的 OpenAI 兼容適配器，無需 AK/SK 獲取 Access Token。
- 只需要配置一個環境變量：QIANFAN_API_KEY（格式一般以 bce-v3/ 開头）。
- 統一走 openai-compatible 基座，支持 function calling、上下文長度、工具绑定等核心能力。

### 環境變量
```bash
# .env 文件
QIANFAN_API_KEY=bce-v3/ALTAK-xxxx/xxxx
```

### 代碼入口（適配器）
- 適配器類：ChatQianfanOpenAI（位於 openai_compatible_base.py 內部註冊）
- 基础地址：https://qianfan.baidubce.com/v2
- Provider 名稱：qianfan

示例：
```python
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm

llm = create_openai_compatible_llm(
    provider="qianfan",
    model="ernie-3.5-8k",
    temperature=0.1,
    max_tokens=800
)

resp = llm.invoke("你好，簡單自我介紹一下")
print(resp.content)
```

### 千帆常见模型（兼容模式）
- ernie-3.5-8k（默認）
- ernie-4.0-turbo-8k
- ERNIE-Speed-8K
- ERNIE-Lite-8K

> 提示：模型名稱需与 openai_compatible_base.py 中的 qianfan 映射保持一致。

### 定價与計費（pricing.json）
- 已在 config/pricing.json 中新增 qianfan/ERNIE 系列占位價格，可在 Web 配置页調整。

## 🧰 可選：原生 AK/SK + Access Token（歷史說明）
- 如需對接歷史腳本或某些特定 API，可使用 AK/SK 方式獲取 Access Token。
- 項目主路徑已不再依賴 AK/SK，仅保留在腳本示例中（.env.example 註明為可選）。

參考流程（仅示意，不再作為默認路徑）：
```python
import os, requests
api_key = os.getenv("QIANFAN_API_KEY")
secret_key = os.getenv("QIANFAN_SECRET_KEY")
url = "https://aip.baidubce.com/oauth/2.0/token"
params = {"grant_type":"client_credentials","client_id":api_key,"client_secret":secret_key}
r = requests.post(url, params=params, timeout=30)
print(r.json())
```

## 🧪 測試与驗證

- 連接測試：確保 QIANFAN_API_KEY 已設置並能正常返回內容。
- 工具調用：通過 bind_tools 驗證 function calling 在千帆上正常工作。

示例：
```python
from langchain_core.tools import tool
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm

@tool
def get_stock_price(symbol: str) -> str:
    return f"股票 {symbol} 的當前價格是 $150.00"

llm = create_openai_compatible_llm(provider="qianfan", model="ernie-3.5-8k")
llm_tools = llm.bind_tools([get_stock_price])
res = llm_tools.invoke("請查詢 AAPL 的價格")
print(res.content)
```

## 🔧 故障排查
- QIANFAN_API_KEY 未設置或格式不正確（應以 bce-v3/ 開头）。
- 網絡或限流問題：稍後重試，或降低並發。
- 模型名不在映射列表：參考 openai_compatible_base.py 的 qianfan 條目。

## 📚 相關文件
- tradingagents/llm_adapters/openai_compatible_base.py（核心適配器与 provider 映射）
- tradingagents/graph/trading_graph.py（運行時 provider 選擇与校驗）
- config/pricing.json（定價配置，可在 Web 中調整）
- .env.example（環境變量示例）