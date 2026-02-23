# 

TradingAgents-CN

## [v0.4.2] - 2026-02-23 - CLS 效能修復與安全掃描清理

### 概述

v0.4.2 著重於 Core Web Vitals CLS 指標改善、Semgrep 安全掃描清理和快取雜湊演算法升級。

### 變更內容

#### 效能優化
- **CLS 修復**: shimmer 動畫從 background-position 改為 transform: translateX()（GPU 合成層）
- **Skeleton 偽元素**: .skeleton 改用 ::after + will-change: transform，減少主執行緒 repaint
- **骨架尺寸匹配**: skeleton-card min-height 調整至 88px/100px，減少內容替換時的版面位移
- **DOMPurify async**: script 標籤加 async 屬性，不阻塞首次渲染

#### 安全強化
- **快取雜湊升級**: MD5 → SHA-256（adaptive_cache、cache_manager、db_cache_manager）
- **Semgrep 全掃描**: OWASP Top 10 + Python 規則集零發現
- **依賴審計**: 所有關鍵 CVE 均已在現有版本中修復

#### Helm 修正
- MongoDB 健康檢查改 tcpSocket（相容新版映像）
- Redis 密碼擴展改用 shell wrapper
- MongoDB/Redis 資源配置提升

#### 版本同步
- 全專案版本統一至 0.4.2（VERSION、pyproject.toml、app/main.py、i18n、README）

---

## [v0.4.1] - 2026-02-23 - Helm 安全強化與效能優化

### 概述

v0.4.1 著重於 Kubernetes 部署安全性、後端效能優化和前端無障礙改善。

### 變更內容

#### Kubernetes 安全強化
- **Pod SecurityContext**: 應用、MongoDB、Redis 全面啟用 runAsNonRoot、drop ALL capabilities
- **NetworkPolicy**: 生產環境限制 pod 間通訊，僅應用 pod 可存取資料庫
- **Dockerfile UID/GID**: 明確指定 UID/GID 1000，與 Helm fsGroup 一致

#### 後端效能優化
- **趨勢 API**: busy-wait 輪詢改 asyncio.Event 事件驅動，專用 ThreadPoolExecutor + 超時保護
- **SSE 串流**: 輪詢間隔 1s -> 0.5s，進度訊息改 deque(maxlen=200) 防記憶體無限增長
- **FinnHub 認證**: API 金鑰改用 X-Finnhub-Token header 認證，避免暴露於 URL

#### 前端改善
- **CDN 預連接**: 新增 preconnect 加速 cdn.jsdelivr.net 資源載入
- **非阻塞載入**: gtag-init.js 改為 async 載入
- **暗色模式對比度**: --text-faint 修正為 WCAG AA 4.73:1+
- **報告區域表格**: .report-body table 樣式與 AI 分析區一致
- **SSE 連接清理**: EventSource 關閉後清空、重連計時器正確清理

#### 依賴同步
- requirements.txt 同步 pyproject.toml（langchain 1.x、openai 2.x）
- 版本號統一至 0.4.1（VERSION、pyproject.toml、app/main.py、README）

---

## [v0.4.0] - 2026-02-23 - 分析師並行化與安全強化

### 概述

v0.4.0 實現分析師並行執行、全面安全強化、CDN 升級和行動裝置優化。

### 變更內容

#### 效能與並行化
- **分析師並行執行**: LangGraph fan-out/fan-in，4 位分析師同時啟動
- **趨勢資料預熱**: 伺服器啟動時背景預載快取
- **頁面可見性感知**: 瀏覽器分頁隱藏時暫停定時重新整理

#### 安全強化
- **速率限制器記憶體防護**: IP 追蹤上限 10,000 筆，自動清理
- **API 錯誤脫敏**: 不回傳內部錯誤堆疊
- **移除硬編碼密碼**: 開發腳本改用環境變數
- **MongoDB 升級**: 4.4 (EOL) -> 7.0 LTS

#### CDN 與前端
- **Alpine.js**: 3.14.8 -> 3.15.8（含 SRI）
- **DOMPurify**: 3.2.4 -> 3.3.1（含 SRI）
- **行動裝置觸控優化**: 觸控目標符合 WCAG 2.5.5（>= 36px）

---

## [v0.1.15] - 2025-01-15 - LLM

### 

v0.1.15LLM

### 

#### LLM
- **LLM**: OpenAI
- ****: LLM
- ****: LLM

#### 
- **TradingAgents**: 
- ****: 
- ****: PDF
- ****: 

#### 
- ****: 
- ****: 
- ****: 
- **PR**: Pull Request

#### 
- ****: GitHub
- ****: 
- ****: 
- ****: 

### 
- `docs/llm/LLM_INTEGRATION_GUIDE.md` - LLM
- `docs/paper/TradingAgents_.md` - 
- `examples/test_installation.py` - 
- `docs/DEVELOPMENT_WORKFLOW.md` - 

## [v0.1.14] - 2025-01-15 - Web

### 

v0.1.14

### 

- ****: 
- ****: 
- ****: 
- ****: 

## [v0.1.14-preview] - 2025-08-14 - Web

### 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

#### Web

- ****: 
- ****: 
- ****: 
- ****: 

#### 

- **MongoDB**: MongoDB
- ****: 
- ****: 
- ****: 

#### 

- ****: 6
- ****: Google
- ****: UI
- ****: 
- ****: 
- ****: 

### 

#### Web

- ****: 
- ****: 
- **UI**: UI
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

### 

#### 
- `web/components/login.py` - 
- `web/utils/auth_manager.py` - 
- `scripts/user_manager.py` - 
- `scripts/data_migration/` - 
- `tests/test_*_fix.py` - 6

#### 
- `web/components/sidebar.py` - 
- `tradingagents/` - 
- `web/` - Web

### 

- ****: 
- **Docker**: Docker
- ****: 

---

## [v0.1.13] - 2025-08-2 - OpenAILLM

### 

#### OpenAI

- **OpenAI**: OpenAIAPI
- ****: OpenAI
- ****: OpenAI
- ****: 

#### LLM

- ****: LLM
- ****: 
- ****: LLM

#### Web

- ****: 
- **KeyError**: KeyError
- **UI**: 
- ****: 

### 

#### 

- ****: 
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: LLM

### 

#### 

- ****: LLM
- ****: 

#### 

- ****: LLM
- ****: 
- ****: API
- ****: API

### 

#### 

- ****: 
- ****: LLM
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

### 

- **LLM**: OpenAI
- ****: 15+ ()
- ****: 8 ()

### 

0.1.13

- ****: OpenAILLM
- ****: 
- ****: 
- ****: 

### 

v0.1.12v0.1.13

1. ****: `pip install -r requirements.txt` `pip install -e .`
2. **API**: `.env`LLMAPI
3. ****: LLM
4. ****: 

---

## [v0.1.12] - 2025-07-29 - 

### 

#### 

- ****: AI
- ****: 
- ****: 
- ****: 

#### 

- **NewsFilter**: 
- **EnhancedNewsFilter**: 
- **NewsFilterIntegration**: 
- **UnifiedNewsTool**: 
- **EnhancedNewsRetriever**: 

#### 

- **
- **
- **LLM**: 
- ****: 

#### 

- ****: 15+
- ****: 8
- ****: 
- ****: 

#### 

- ****: docs
- ****: tests
- ****: examples
- ****: 

### 

#### 

- ****: → → 
- ****: 
- ****: 
- ****: 

#### 

- ****: LLM
- ****: 
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

### 

- ****: 5 ()
- ****: 15+ ()
- ****: 8 ()
- ****: 100% ()

### 

- ****: 40% ()
- ****: 25% ()
- ****: 80% ()
- ****: 90% ()

---

## [v0.1.11] - 2025-07-27 - LLM

### 

#### LLM

- **4**: 
- ****: OpenAI GPT-4oAnthropic Claude Opus 4 
- ****: OpenAIAnthropic 

#### 

- **URL**: `st.query_params`
- ****: 
- **URL**: URL
- ****: 

#### Web

- **320px**: 
- ****: 
- ****: 
- ****: 

### 

#### 

- **ModelPersistence**: 
- ****: URL + Session State
- ****: URLSession State
- ****: 

#### 

- **ChromaDB**: 
- ****: ChromaDB
- ****: 

#### 

- ****: 
- ****: 
- ****: 

### 

- ****: 4 (
- ****: 60+ (AI)
- ****: 5 ()
- ****: 100% ()

### 

- ****: 100% ()
- ****: 80% ()
- ****: 60% ()
- ****: 90% ()

---

## [v0.1.10] - 2025-07-18 - Web

### 

#### 

- ****: 
- **AsyncProgressTracker**: 
- ****: Streamlit
- ****: 

#### 

- ****: " "
- ****: 
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

### 

#### 

- **SmartSessionManager**: Redis
- ****: Redis
- ****: 
- **Cookie**: Cookie

#### 

- **AsyncProgressDisplay**: 
- ****: 
- ****: 
- ****: 

#### 

- ****: UnboundLocalError
- ****: 
- ****: 
- ****: 

### 

#### 

- ****: 
- ****: 
- ****: 
- ****: UI

#### 

- ****: 
- ****: 
- ****: 
- ****: 

### 

#### 

- ****: 
- ****: API
- ****: 
- ****: 

#### 

- ****: 39
- ****: 
- ****: 
- ****: Git

### 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

### 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 

## [v0.1.9] - 2025-07-16 - CLI

### 

#### CLI

- ****: 
- **CLIUserInterface**: Rich
- ****: 
- ****: 

#### 

- ****: 
- ****: 
- ****: 
- ****: 5

#### 

- ****: "10"
- ****: 
- ****: 
- ****: 

#### 

- **LoggingManager**: 
- **TOML**: Docker
- ****: 
- ****: 

### 

#### 

- ****: 
- ****: 
- **fallback**: 

#### OpenAI

- ****: OpenAI
- ****: API
- ****: 

### 

#### 

```
2025-07-16 14:47:20,108 | cli | INFO | [bold cyan]...
 
 
 
[...]
```

#### 

```
 | Please select stock market:
1. | US Stock
2. | China A-Share

 3: | AI Analysis Phase (10)
 ...
 10
 
 
 ...
 
```

### 

- CLI
- 
- 
- OpenAI
- 
- 

### 

- ****: 
- ****: CLI
- ****: 

## [v0.1.8] - 2025-07-15 - Web

### 

#### Web

- ****: markdown (`****`)
- ****: 
- ****: 8px
- ****: 

#### 

- ****: 
- ****: 2:11/3
- ****: 
- ****: 

#### 

- ****: (AAPL, MSFT, TSLA)
- ****: 
- ****: 
- ****: 

#### 

- **100%**: 100%
- ****: " "
- ****: 1
- ****: 

#### Bug

- ****: 
- ****: 
- ****: 
- ****: 

#### 

- ****: get_stock_fundamentals_unifiedget_stock_market_data_unified
- ****: 
- ****: (/) + () + (FinnHub/YFinance)
- ****: 

### 

#### 

- markdown
- 8px
- 2:1
- 

#### 

- 
- 
- 
- 

#### 

- 0%-100%
- 
- 
- 

#### 

- (AAPL, MSFT )
- 
- 
- 

#### 

- 
- 
- 
- 

### 

#### 

- 
- 
- 
- 

#### 

- 100%
- 
- 
- 

#### 

- 
- 
- 
- 

#### 

- (^\d{4,5}\.HK$)
- 
- AttributeError
- is_china

#### 

- 
- 
- ChromaDB
- 

### 

- ****: `web/pages/` `web/modules/`
- ****: 
- ****: 

### 

- ****: 
- ****: 
- ****: (0%-100%)
- ****: 

## [v0.1.7] - 2025-07-13 - 

### 

#### Docker

- ****: Docker Compose
- ****: WebMongoDBRedis
- ****: Volume
- ****: MongoDB ExpressRedis Commander
- ****: 

#### 

- ****: (Word/PDF/Markdown)
- ****: Pandocwkhtmltopdf
- ****: 
- ****: 
- ****: Web

#### 

- ****: 
- ****: GPT-490%
- ****: 
- ****: 
- ****: 

### 

#### 

- Docker Compose
- 
- 
- 
- 

#### 

- Markdown
- Word (.docx)
- PDF (.pdf)
- 
- 

#### LLM

- 
- 
- 
- 
- 

### 

- WordYAML
- PDF
- Docker
- 
- 

### 

- Docker80%
- 60%
- 40%
- 30%
- API25%

### 

- Docker
- 
- 
- 
- 

### 

- **[@breeze303](https://github.com/breeze303)**: Docker
- **[@baiyuxiong](https://github.com/baiyuxiong)**: 
- ****: 

## [v0.1.6] - 2025-07-11 - 

### 

#### OpenAI

- ****: `Chat
- ****: 30
- ****: Function Calling
- ****: LLMReAct
- ****: 

#### 

- ****: 
- ****: () + ()
- ****: 
- ****: API

### 

- OpenAI
- LLM
- Token
- 1500+
- 

### 

- 
- 
- 
- 

### 

- LLM50%
- 35%
- API60%
- 40%

### 

- OpenAI
- 
- 
- README

## [v0.1.5] - 2025-01-08

### 

- ****: 
- **
- ****: 

### 

- PEPBROE
- 
- 
- 
- 

### 

- 
- 
- 
- 
- 

### 

- 
- 
- 

### 

- tests
- docs
- utils

## [0.1.4] - 2024-12-XX

### 

- Web
- Token
- 

### 

- 
- 

## [0.1.3] - 2024-12-XX

### 

- LLM
- 
- 

### 

- 
- 

## [0.1.2] - 2024-11-XX

### 

- Web
- 
- 

### 

- 

---


