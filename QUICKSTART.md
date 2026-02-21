# TradingAgents-CN 快速開始指南

> **版本**: 0.1.18 | **更新時間**: 2026-02-21
> **目標**: 5 分鐘內完成部署並開始美股分析

## 選擇部署方式

### 方式一：Docker 部署（推薦）

**適用場景**: 正式環境、快速體驗、零配置啟動

```bash
# 1. 複製專案
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 配置環境變數
cp .env.example .env
# 編輯 .env 檔案，填入 API 密鑰

# 3. 建置並啟動服務
docker-compose up -d --build

# 首次執行會自動建置 Docker 映像檔，需要 5-10 分鐘
# 建置過程包括：
# - 下載基礎映像檔和依賴（約 800MB）
# - 安裝系統工具（pandoc、wkhtmltopdf 等）
# - 安裝 Python 依賴套件
# - 配置執行環境

# 4. 存取應用
# Web 介面: http://localhost:8501
# 資料庫管理: http://localhost:8081
# 快取管理: http://localhost:8082
```

### 分步建置方式（可選）

如果您希望分步進行，可以先單獨建置映像檔：

```bash
# 方式 A: 分步建置
# 1. 先建置 Docker 映像檔
docker build -t tradingagents-cn:latest .

# 2. 再啟動所有服務
docker-compose up -d

# 方式 B: 一鍵建置啟動（推薦）
docker-compose up -d --build
```

### 方式二：本機部署

**適用場景**: 開發環境、自訂配置、離線使用

```bash
# 1. 複製專案
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 建立虛擬環境
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/macOS

# 3. 升級 pip（重要！避免安裝錯誤）
python -m pip install --upgrade pip

# 4. 安裝依賴（推薦使用鎖定版本，安裝速度最快）
pip install -r requirements-lock.txt
pip install -e . --no-deps

# 或一步安裝（會重新解析依賴，速度較慢）
# pip install -e .

# 5. 配置環境變數
cp .env.example .env
# 編輯 .env 檔案

# 6. 啟動應用
# 方法 1: 使用簡化啟動腳本（推薦）
python start_web.py

# 方法 2: 使用專案啟動腳本
python web/run_web.py

# 方法 3: 直接使用 Streamlit（需要先安裝專案）
streamlit run web/app.py
```

## 環境配置

### 必需配置

建立 `.env` 檔案並配置以下內容：

```bash
# === LLM 模型配置（至少選擇一個）===

# OpenAI（通用能力強）
OPENAI_API_KEY=your_openai_api_key

# Anthropic Claude（分析能力強）
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### API 密鑰取得

| 提供商 | 取得位址 | 特色 | 成本 |
| --- | --- | --- | --- |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) | 通用能力強、工具呼叫 | 中高 |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) | 分析推理、長文本處理 | 中高 |

### 可選配置

```bash
# === 資料來源配置（可選）===
FINNHUB_API_KEY=your_finnhub_key          # 美股即時資料

# === 資料庫配置（Docker 自動配置）===
MONGODB_URL=mongodb://mongodb:27017/tradingagents  # Docker 環境
REDIS_URL=redis://redis:6379                       # Docker 環境

# === 匯出功能配置 ===
EXPORT_ENABLED=true                       # 啟用報告匯出
EXPORT_DEFAULT_FORMAT=word,pdf            # 預設匯出格式
```

## 開始使用

### 1. 存取 Web 介面

```bash
# 開啟瀏覽器存取
http://localhost:8501
```

### 2. 配置分析參數

- **選擇 LLM 模型**: GPT-4 / Claude
- **選擇分析深度**: 快速 / 標準 / 深度
- **選擇分析師**: 市場分析 / 基本面分析 / 新聞分析

### 3. 輸入股票代碼

```bash
# 美股範例
AAPL    # Apple
TSLA    # Tesla
MSFT    # Microsoft
NVDA    # NVIDIA
GOOGL   # Alphabet
AMZN    # Amazon
```

### 4. 開始分析

1. 點擊「開始分析」按鈕
2. **即時進度追蹤**: 觀察分析進度和目前步驟
   - 顯示已用時間和預計剩餘時間
   - 即時更新分析狀態和步驟說明
   - 支援手動重新整理和自動重新整理控制
3. **分析完成**: 等待分析完成（2-10 分鐘，取決於分析深度）
   - 顯示準確的總耗時
   - 自動顯示「分析完成」狀態
4. **查看報告**: 點擊「查看分析報告」按鈕
   - 即時顯示詳細的投資分析報告
   - 支援重複查看和頁面重新整理後恢復
5. **匯出報告**: 可選擇匯出為 Word/PDF/Markdown 格式

## 報告匯出功能

### 支援格式

| 格式 | 用途 | 特點 |
| --- | --- | --- |
| **Markdown** | 線上查看，版本控制 | 輕量級，可編輯 |
| **Word** | 商業報告，編輯修改 | 專業格式，易編輯 |
| **PDF** | 正式發布，列印存檔 | 固定格式，專業外觀 |

### 匯出步驟

1. 完成股票分析
2. 在結果頁面點擊匯出按鈕
3. 選擇匯出格式
4. 自動下載到本機

## 功能特色

### 多智能體協作

- **市場分析師**: 技術指標、趨勢分析
- **基本面分析師**: 財務資料、估值模型
- **新聞分析師**: 新聞情緒、事件影響
- **研究員**: 看漲看跌辯論
- **交易決策員**: 綜合決策制定

### 智能模型選擇

- **GPT-4**: 通用能力最強，工具呼叫優秀
- **Claude**: 分析推理強，長文本處理佳

### 全面資料支援

- **美股**: NYSE/NASDAQ，即時資料
- **新聞**: 即時財經新聞，情緒分析
- **社交**: FinnHub 情緒數據，市場熱度

## 常見問題

### 分析失敗怎麼辦？

1. **檢查 API 密鑰**: 確認密鑰正確且有餘額
2. **網路連線**: 確保網路穩定，可存取 API
3. **模型切換**: 嘗試切換其他 LLM 模型
4. **查看日誌**: 檢查主控台錯誤資訊

### 如何提高分析速度？

1. **選擇快速模型**: gpt-4o-mini 回應最快
2. **啟用快取**: 使用 Redis 快取重複資料
3. **快速模式**: 選擇快速分析深度
4. **網路最佳化**: 確保網路環境穩定

### Docker 部署問題？

```bash
# 檢查服務狀態
docker-compose ps

# 查看日誌
docker logs TradingAgents-web

# 重啟服務
docker-compose restart
```

## 下一步

### 深入使用

1. **閱讀文件**: [完整文件](./docs/)
2. **開發環境**: [開發指南](./docs/DEVELOPMENT_SETUP.md)
3. **疑難排解**: [問題解決](./docs/troubleshooting/)
4. **架構了解**: [技術架構](./docs/architecture/)

### 參與貢獻

- [回報問題](https://github.com/hsliuping/TradingAgents-CN/issues)
- [功能建議](https://github.com/hsliuping/TradingAgents-CN/discussions)
- [提交程式碼](https://github.com/hsliuping/TradingAgents-CN/pulls)
- [完善文件](https://github.com/hsliuping/TradingAgents-CN/tree/develop/docs)

---

## 恭喜完成快速開始！

**提示**: 建議先用熟悉的美股代碼進行測試，體驗完整的分析流程。

**技術支援**: [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)

---

*最後更新: 2026-02-21 | 版本: 0.1.18*
