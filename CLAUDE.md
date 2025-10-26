# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**非常重要一定要遵守**
- 對話及coding都必須使用繁體中文
- coding中不使用任何的emoji圖案
- 避免撰寫過多的註解讓人發現是AI
- 對於每個功能都必須要寫註解讓人知道這個功能主要處理什麼

## 專案概述

TradingAgents-CN 是一個基於多智慧體大語言模型的中文金融交易決策框架，專為中文使用者優化，提供完整的 A股/港股/美股分析能力。這是 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 的中文增強版本。

**核心特性**：
- 🤖 多智慧體協作：分析師、研究員、交易決策員協同工作
- 🇨🇳 中國市場優化：支持 A股/港股數據，集成國產大模型
- 🧠 多 LLM 支持：DeepSeek、阿里百煉、Google AI、OpenAI 等 60+ 模型
- 🐳 容器化部署：完整的 Docker 多架構支持
- 📊 即時分析：Web 界面即時進度跟蹤

## 常用命令

### 環境設置

```bash
# 創建虛擬環境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# 升級 pip (重要！避免安裝錯誤)
python -m pip install --upgrade pip

# 安裝依賴 (推薦使用鎖定版本，速度最快)
pip install -r requirements-lock.txt
pip install -e . --no-deps

# 或一步安裝（會重新解析依賴，速度較慢）
# pip install -e .
```

### 啟動應用

```bash
# Web 界面啟動（推薦）
python start_web.py

# 或使用 streamlit 直接啟動
streamlit run web/app.py

# CLI 交互式界面
python -m cli.main
```

### Docker 部署

```bash
# 首次啟動或程式碼變更時（需要建構映像）
docker-compose up -d --build

# 日常啟動（映像已存在，無程式碼變更）
docker-compose up -d

# 智能啟動（自動判斷是否需要建構）
# Windows
powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1
# Linux/Mac
./scripts/smart_start.sh

# 檢視服務狀態
docker-compose ps

# 檢視日誌
docker-compose logs -f web

# 停止服務
docker-compose down
```

### 測試

```bash
# 運行所有測試
pytest tests/

# 運行特定測試文件
pytest tests/integration/test_dashscope_integration.py

# 運行單個測試
pytest tests/integration/test_dashscope_integration.py::test_specific_function -v

# 帶覆蓋率的測試
pytest --cov=tradingagents tests/

# 調試模式運行測試
pytest -v -s tests/
```

### 開發工具

```bash
# 檢查 API 配置
python scripts/check_api_config.py

# 系統狀態檢查
python scripts/validation/check_system_status.py

# 使用者管理
python scripts/user_password_manager.py list
python scripts/user_password_manager.py change-password admin
python scripts/user_password_manager.py create newuser --role trader

# 資料目錄配置
python -m cli.main data-config --show
python -m cli.main data-config --set /path/to/data

# 清理快取
python scripts/maintenance/cleanup_cache.py --days 7
```

## 核心架構

### 多智慧體系統

專案採用分層的多智慧體架構：

```
Research Director (研究主管)
    ├─> Analysts (分析師團隊)
    │   ├─> Market Analyst (市場分析師) - 技術指標和趨勢分析
    │   ├─> Fundamental Analyst (基本面分析師) - 財務數據和估值
    │   ├─> News Analyst (新聞分析師) - 新聞情緒分析
    │   └─> Social Media Analyst (社交媒體分析師) - Reddit/Twitter情緒
    │
    ├─> Researchers (研究員團隊)
    │   ├─> Bullish Researcher (看漲研究員) - 找出看漲理由
    │   └─> Bearish Researcher (看跌研究員) - 找出看跌理由
    │
    └─> Decision Makers (決策團隊)
        ├─> Trader (交易員) - 綜合決策制定
        └─> Risk Manager (風險管理) - 風險評估和控制
```

**關鍵設計模式**：
- **辯論機制**：看漲/看跌研究員進行結構化辯論
- **層次化決策**：從資料採集 → 分析 → 研究 → 決策的完整流程
- **LangGraph 工作流**：使用 LangGraph 編排智慧體協作

### 目錄結構

```
tradingagents/              # 核心套件
├── agents/                 # 智慧體實現
│   ├── analysts/          # 分析師團隊
│   ├── researchers/       # 研究員團隊
│   ├── trader/           # 交易決策
│   ├── risk_mgmt/        # 風險管理
│   └── managers/         # 管理層協調
├── graph/                 # LangGraph 工作流
│   ├── trading_graph.py  # 主工作流定義
│   ├── signal_processing.py  # 訊號處理
│   └── conditional_logic.py  # 條件邏輯
├── llm/                   # LLM 集成層
├── llm_adapters/          # LLM 適配器（統一接口）
├── tools/                 # 工具集合
│   └── unified_news_tool.py  # 統一新聞工具
├── dataflows/             # 資料處理流程
├── api/                   # API 客戶端
├── config/                # 配置管理
└── utils/                 # 工具函數

web/                       # Streamlit Web 界面
├── app.py                # 主應用入口
├── pages/                # 多頁面應用
├── components/           # UI 組件
└── config/               # Web 配置（使用者管理）

cli/                       # 命令列界面
├── main.py               # CLI 主程式
└── utils.py              # CLI 工具

scripts/                   # 維護和部署腳本
├── deployment/           # 部署相關
├── development/          # 開發工具
├── validation/           # 驗證腳本
└── maintenance/          # 維護工具

config/                    # 全域配置檔案
docs/                      # 詳細文檔（50,000+ 字）
tests/                     # 測試套件
data/                      # 資料儲存目錄
```

### LLM 適配器架構

所有 LLM 提供商透過統一的適配器接口集成：

```python
# tradingagents/llm_adapters/
├── base_adapter.py           # 基礎適配器接口
├── dashscope_adapter.py      # 阿里百煉適配器
├── deepseek_adapter.py       # DeepSeek 適配器
├── google_openai_adapter.py  # Google AI OpenAI 相容適配器
└── openai_adapter.py         # 原生 OpenAI 適配器
```

**關鍵設計**：
- 所有適配器繼承統一基類，提供一致的呼叫接口
- 支持工具呼叫（Tool Calling）的智慧處理和降級
- 錯誤處理和自動重試機制

### 資料流架構

```
資料來源層
├─> Tushare (A股專業資料)
├─> AkShare (A股/港股即時資料)
├─> FinnHub (美股資料)
├─> Yahoo Finance (全球市場)
└─> Google News (新聞資料)

快取層（多級快取）
├─> Redis (熱資料快取，毫秒級)
├─> MongoDB (歷史資料持久化)
└─> 本機檔案快取（備用）

智慧降級機制
1. 檢查 Redis 快取
2. 查詢 MongoDB
3. 呼叫 API
4. 使用本機快取
5. 返回錯誤
```

### 配置管理

專案使用多層配置系統：

1. **環境變數** (`.env`) - 最高優先順序
2. **預設配置** (`tradingagents/default_config.py`)
3. **執行時配置** - 程式動態設定

**關鍵配置**：
```python
# LLM 配置
llm_provider: str       # dashscope/deepseek/google/openai
deep_think_llm: str     # 深度分析模型
quick_think_llm: str    # 快速任務模型

# 工具配置
online_tools: bool      # 啟用線上工具
online_news: bool       # 啟用新聞分析
realtime_data: bool     # 啟用即時資料

# 辯論配置
max_debate_rounds: int  # 辯論輪數
max_risk_discuss_rounds: int  # 風險討論輪數
```

## 開發指南

### 添加新的 LLM 提供商

1. 在 `tradingagents/llm_adapters/` 創建新適配器
2. 繼承 `BaseAdapter` 並實現必需方法
3. 在 `tradingagents/llm/` 註冊新提供商
4. 更新 `.env.example` 添加 API 金鑰配置
5. 在 Web 界面的模型選擇中添加新選項

### 添加新的分析師

1. 在 `tradingagents/agents/analysts/` 創建新分析師類別
2. 定義分析師的提示詞和工具
3. 在 `tradingagents/graph/setup.py` 註冊新智慧體
4. 更新 `tradingagents/graph/trading_graph.py` 添加到工作流
5. 在 Web 界面添加分析師選擇選項

### 添加新的資料來源

1. 在 `tradingagents/api/` 創建新的 API 客戶端
2. 在 `tradingagents/dataflows/` 實現資料處理流程
3. 更新快取邏輯支持新資料來源
4. 添加降級策略
5. 編寫相應的測試案例

### 程式碼風格規範

- **Python 版本**：3.10+
- **格式化**：遵循 PEP 8
- **類型註解**：對公共 API 使用類型註解
- **文檔字串**：使用 Google 風格的 docstring
- **錯誤處理**：使用 try-except 並記錄詳細日誌
- **日誌**：使用 `tradingagents.utils.logging` 統一日誌系統

### 環境變數約定

所有環境變數應在 `.env.example` 中定義：

```bash
# LLM API 金鑰
DASHSCOPE_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# 資料來源 API
TUSHARE_TOKEN=your_token
FINNHUB_API_KEY=your_key

# 資料庫配置
MONGODB_ENABLED=true
MONGODB_HOST=localhost
MONGODB_PORT=27017
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# 功能開關
ONLINE_TOOLS_ENABLED=false
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
```

### Docker 建構註意事項

- **多架構支持**：專案支持 amd64 和 arm64 架構
- **基礎映像**：使用 `python:3.11-slim`
- **依賴安裝**：優先使用 `requirements-lock.txt` 以加快建構
- **匯出依賴**：需要安裝 `pandoc` 和 `wkhtmltopdf`
- **資料庫連線**：Docker 環境使用服務名（mongodb、redis）

### 資料庫遷移和備份

專案自動創建資料備份：
```bash
data_backup_YYYYMMDD_HHMMSS/  # 自動備份目錄
```

初始化資料庫：
```bash
python scripts/setup/init_database.py
```

## 調試技巧

### 啟用調試模式

```python
# 在程式碼中啟用調試
from tradingagents.graph.trading_graph import TradingAgentsGraph

ta = TradingAgentsGraph(debug=True, config=config)
```

### 檢視 LangGraph 工作流

```bash
# 生成工作流視覺化（需要安裝 graphviz）
python scripts/development/visualize_graph.py
```

### 日誌位置

- **應用日誌**：`logs/`
- **Docker 日誌**：`docker-compose logs -f web`
- **Streamlit 日誌**：終端輸出

### 常見問題排查

1. **ChromaDB 相容性問題（Windows 10）**
   ```bash
   # 停用記憶體功能
   # 在 .env 添加：MEMORY_ENABLED=false

   # 或使用修復腳本
   powershell -ExecutionPolicy Bypass -File scripts\fix_chromadb_win10.ps1
   ```

2. **MongoDB 連線失敗**
   ```bash
   # 檢查服務狀態
   docker-compose logs mongodb

   # 重新啟動服務
   docker-compose restart mongodb
   ```

3. **API 金鑰錯誤**
   ```bash
   # 驗證配置
   python scripts/check_api_config.py
   ```

4. **快取問題**
   ```bash
   # 清理快取
   python scripts/maintenance/cleanup_cache.py --days 7
   ```

## 重要提醒

### 安裝相關

- **必須升級 pip**：`python -m pip install --upgrade pip`
- **推薦使用鎖定版本**：`requirements-lock.txt` 避免依賴衝突
- **國內映像加速**：使用清華源加速下載
- **Windows PyYAML 問題**：使用鎖定版本可避免編譯錯誤

### 部署相關

- **首次啟動**：Docker 建構需要 5-10 分鐘
- **資料庫主機名**：本機部署用 `localhost`，Docker 用服務名
- **連接埠衝突**：確保 8501（Web）、27017（MongoDB）、6379（Redis）連接埠可用
- **預設帳號**：admin/admin123，user/user123（首次登入後立即修改）

### 開發相關

- **不要直接修改**：`requirements-lock.txt`（由 uv.lock 生成）
- **保持同步**：`requirements.txt` 和 `pyproject.toml` 應保持一致
- **環境變數優先**：配置優先順序為環境變數 > 執行時配置 > 預設配置
- **完整測試**：修改核心邏輯後運行完整測試套件
- **文檔更新**：添加新功能時同步更新 `docs/` 目錄

### 資料庫相關

- **可選功能**：資料庫是效能優化功能，非必需
- **智慧降級**：資料庫不可用時自動降級到 API 直接呼叫
- **快取策略**：Redis（熱資料）→ MongoDB（歷史）→ API → 本機檔案

## 參考資源

- **完整文檔**：`docs/` 目錄（50,000+ 字詳細文檔）
- **快速開始**：`QUICKSTART.md`（5 分鐘部署指南）
- **使用者管理**：`scripts/USER_MANAGEMENT.md`
- **匯出功能**：`docs/EXPORT_GUIDE.md`
- **故障排除**：`docs/troubleshooting/`
- **架構文檔**：`docs/architecture/`
- **原專案**：https://github.com/TauricResearch/TradingAgents
