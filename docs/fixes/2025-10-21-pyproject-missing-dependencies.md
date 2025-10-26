# pyproject.toml 缺失依賴包修複

**日期**: 2025-10-21  
**版本**: v0.1.13-preview (main 分支)  
**類型**: Bug Fix  
**優先級**: High

## 問題描述

### 用戶反馈

用戶反馈在安裝項目時，很多包没有包含在 `pyproject.toml` 文件中，導致安裝後運行時出現 `ModuleNotFoundError`。

### 根本原因

`pyproject.toml` 中的 `dependencies` 列表不完整，缺少了以下關键依賴包：

1. **核心框架依賴**
   - `langchain` - LangChain 核心庫
   - `langchain-core` - LangChain 核心組件
   - `pydantic` - 數據驗證庫
   - `typer` - CLI 框架

2. **數據處理依賴**
   - `numpy` - 數值計算庫
   - `python-dateutil` - 日期處理庫
   - `beautifulsoup4` - HTML 解析庫

3. **AI/ML 依賴**
   - `sentence-transformers` - 句子嵌入模型
   - `torch` - PyTorch 深度學习框架
   - `transformers` - Hugging Face Transformers

4. **工具庫依賴**
   - `tenacity` - 重試機制庫
   - `urllib3` - HTTP 客戶端庫
   - `toml` - TOML 配置文件解析

5. **Streamlit 擴展**
   - `streamlit-cookies-manager` - Streamlit Cookie 管理

## 解決方案

### 1. 創建依賴檢查腳本

創建了 `scripts/check_missing_dependencies.py` 腳本，用於自動扫描代碼中使用的第三方包，並与 `pyproject.toml` 中聲明的依賴進行對比。

**腳本功能**:
- 扫描 `tradingagents/`, `web/`, `cli/` 目錄中的所有 Python 文件
- 提取所有 `import` 和 `from ... import` 語句
- 過濾掉標準庫和內部模塊
- 与 `pyproject.toml` 中的依賴進行對比
- 輸出缺失的依賴列表

### 2. 更新 pyproject.toml

在 `pyproject.toml` 的 `dependencies` 列表中添加了 14 個缺失的依賴包：

```toml
dependencies = [
    # ... 原有依賴 ...
    
    # 🆕 新增依賴
    "beautifulsoup4>=4.12.0",        # HTML 解析
    "langchain>=0.3.0",              # LangChain 核心庫
    "langchain-core>=0.3.0",         # LangChain 核心組件
    "numpy>=1.24.0",                 # 數值計算
    "pydantic>=2.0.0",               # 數據驗證
    "python-dateutil>=2.8.0",        # 日期處理
    "sentence-transformers>=2.2.0",  # 句子嵌入
    "streamlit-cookies-manager>=0.2.0",  # Streamlit Cookie 管理
    "tenacity>=8.0.0",               # 重試機制
    "toml>=0.10.0",                  # TOML 解析
    "torch>=2.0.0",                  # PyTorch
    "transformers>=4.30.0",          # Hugging Face Transformers
    "typer>=0.9.0",                  # CLI 框架
    "urllib3>=2.0.0",                # HTTP 客戶端
]
```

### 3. 依賴包总數

- **更新前**: 38 個依賴包
- **更新後**: 52 個依賴包
- **新增**: 14 個依賴包

## 驗證結果

運行依賴檢查腳本驗證：

```bash
python scripts/check_missing_dependencies.py
```

**輸出結果**:
```
✅ 所有第三方包都已在 pyproject.toml 中聲明！

📦 所有第三方包導入列表:
  ✅ akshare
  ✅ baostock
  ✅ bs4 (beautifulsoup4)
  ✅ chromadb
  ✅ dashscope
  ✅ dateutil (python-dateutil)
  ✅ langchain
  ✅ langchain_core
  ✅ numpy
  ✅ pydantic
  ✅ sentence_transformers
  ✅ streamlit_cookies_manager
  ✅ tenacity
  ✅ toml
  ✅ torch
  ✅ transformers
  ✅ typer
  ✅ urllib3
  ... (共 41 個第三方包)
```

## 影響範围

### 用戶安裝體驗

**更新前**:
```bash
pip install -e .
# 安裝後運行會出現 ModuleNotFoundError
python -m cli.main
# ❌ ModuleNotFoundError: No module named 'typer'
```

**更新後**:
```bash
pip install -e .
# 所有依賴都會自動安裝
python -m cli.main
# ✅ 正常運行
```

### 受影響的模塊

1. **CLI 模塊** (`cli/`)
   - 依賴 `typer` 框架
   - 依賴 `rich` 用於美化輸出

2. **Web 模塊** (`web/`)
   - 依賴 `streamlit-cookies-manager` 用於 Cookie 管理
   - 依賴 `beautifulsoup4` 用於 HTML 解析

3. **核心庫** (`tradingagents/`)
   - 依賴 `langchain` 和 `langchain-core` 用於 LLM 集成
   - 依賴 `numpy` 用於數值計算
   - 依賴 `pydantic` 用於數據驗證
   - 依賴 `sentence-transformers` 和 `torch` 用於嵌入模型
   - 依賴 `tenacity` 用於重試機制
   - 依賴 `toml` 用於配置文件解析

## 安裝指南

### 方式 1: 使用 pip（推薦）

```bash
# 開發模式安裝（可編辑）
pip install -e .

# 或者從 PyPI 安裝（如果已發布）
pip install tradingagents
```

### 方式 2: 使用 uv（更快）

```bash
# 開發模式安裝
uv pip install -e .
```

### 方式 3: 安裝可選依賴

```bash
# 安裝千帆大模型支持
pip install -e ".[qianfan]"
```

## 依賴包說明

### 核心依賴（必需）

| 包名 | 版本要求 | 用途 |
|------|----------|------|
| langchain | >=0.3.0 | LangChain 核心庫，用於 LLM 集成 |
| langchain-core | >=0.3.0 | LangChain 核心組件 |
| pydantic | >=2.0.0 | 數據驗證和序列化 |
| numpy | >=1.24.0 | 數值計算和數組操作 |
| pandas | >=2.3.0 | 數據處理和分析 |
| typer | >=0.9.0 | CLI 命令行框架 |

### AI/ML 依賴

| 包名 | 版本要求 | 用途 |
|------|----------|------|
| openai | >=1.0.0,<2.0.0 | OpenAI API 客戶端 |
| dashscope | >=1.20.0 | 阿里云百炼 API 客戶端 |
| langchain-openai | >=0.3.23 | LangChain OpenAI 集成 |
| langchain-anthropic | >=0.3.15 | LangChain Anthropic 集成 |
| sentence-transformers | >=2.2.0 | 句子嵌入模型 |
| torch | >=2.0.0 | PyTorch 深度學习框架 |
| transformers | >=4.30.0 | Hugging Face Transformers |

### 數據源依賴

| 包名 | 版本要求 | 用途 |
|------|----------|------|
| akshare | >=1.16.98 | A股數據源 |
| tushare | >=1.4.21 | Tushare 數據源 |
| yfinance | >=0.2.63 | Yahoo Finance 數據源 |
| baostock | >=0.8.8 | BaoStock 數據源 |
| finnhub-python | >=2.4.23 | Finnhub 數據源 |

### Web 框架依賴

| 包名 | 版本要求 | 用途 |
|------|----------|------|
| streamlit | >=1.28.0 | Web 應用框架 |
| streamlit-cookies-manager | >=0.2.0 | Cookie 管理 |
| chainlit | >=2.5.5 | 對話式 AI 界面 |

### 工具庫依賴

| 包名 | 版本要求 | 用途 |
|------|----------|------|
| requests | >=2.32.4 | HTTP 請求 |
| urllib3 | >=2.0.0 | HTTP 客戶端 |
| beautifulsoup4 | >=4.12.0 | HTML 解析 |
| python-dateutil | >=2.8.0 | 日期處理 |
| tenacity | >=8.0.0 | 重試機制 |
| toml | >=0.10.0 | TOML 配置解析 |
| rich | >=14.0.0 | 终端美化輸出 |

## 後续維護

### 定期檢查依賴

建议定期運行依賴檢查腳本，確保 `pyproject.toml` 与實际代碼保持同步：

```bash
python scripts/check_missing_dependencies.py
```

### 添加新依賴的流程

1. 在代碼中使用新的第三方包
2. 運行依賴檢查腳本
3. 将缺失的依賴添加到 `pyproject.toml`
4. 更新文档說明新依賴的用途
5. 提交代碼並更新版本號

### 版本管理建议

- 使用 `>=` 指定最低版本要求
- 對於關键依賴（如 openai），使用版本範围限制（如 `>=1.0.0,<2.0.0`）
- 定期更新依賴版本，修複安全漏洞

## 相關鏈接

- **Issue**: 用戶反馈依賴包缺失問題
- **Commit**: 待提交
- **檢查腳本**: `scripts/check_missing_dependencies.py`
- **配置文件**: `pyproject.toml`

## 註意事項

### torch 和 transformers 依賴

這两個包體積較大（torch 約 2GB），安裝時間較長。如果用戶不需要使用嵌入模型功能，可以考慮：

1. 将這些依賴移到 `[project.optional-dependencies]` 中
2. 創建一個 `ai` 或 `ml` 可選依賴組

**建议的可選依賴配置**:
```toml
[project.optional-dependencies]
qianfan = ["qianfan>=0.4.20"]
ai = [
    "sentence-transformers>=2.2.0",
    "torch>=2.0.0",
    "transformers>=4.30.0",
]
```

用戶可以選擇性安裝：
```bash
# 不安裝 AI 依賴
pip install -e .

# 安裝 AI 依賴
pip install -e ".[ai]"
```

### 兼容性說明

- **Python 版本**: 要求 Python >= 3.10
- **操作系統**: 支持 Windows, Linux, macOS
- **架構**: 支持 x86_64 和 ARM64（Apple Silicon）

某些依賴（如 torch）在不同平台上的安裝方式可能不同，建议參考官方文档。

