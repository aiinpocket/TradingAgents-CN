# 

TradingAgents-CN

## [v0.4.4] - 2026-02-23 - 效能並行化 + 背景刷新 + i18n 清理

### 概述

v0.4.4 對趨勢資料抓取進行並行化改造，新增背景定時刷新機制，並清理未使用的 i18n 翻譯鍵。

### 變更內容

#### 效能優化 - 趨勢資料抓取並行化
- **_fetch_movers() 批次並行**: 將 2 批 25 隻股票的串列抓取改為 ThreadPoolExecutor 並行，延遲降低約 50%
- **公司名稱快取**: 新增 _company_names 模組級快取，避免重複的 ticker.info API 呼叫
- **_fetch_market_news() 並行**: 6 個新聞來源從串列改為並行抓取，延遲降低約 70%
- **背景定時刷新**: 新增 start_background_refresh()，每 5 分鐘自動更新市場資料快取
- **960px RWD 斷點**: 表單 4 欄→2 欄斷點從 768px 提前至 960px

#### i18n 清理
- **移除 11 個未使用翻譯鍵**: status.api_label、analysis.symbol_placeholder、common.error、trending.title/subtitle/loading/error/view_more/rank、watchlist.empty/empty_desc
- **更新 refresh_hint**: 反映後端 5 分鐘 + 前端 10 分鐘的雙層刷新機制
- **鍵數**: 148 → 137（zh-TW/en 完全對稱）

#### 版本更新
- 版本升級至 0.4.4（VERSION、pyproject.toml、main.py、README.md、i18n footer）

---

## [v0.4.3d] - 2026-02-23 - CLS 0.00 + VIX 色彩修正 + 無障礙強化

### 概述

v0.4.3d 將 CLS 從 0.02 進一步優化至 0.00（Lighthouse），修復 VIX 恐慌指數色彩邏輯，全面強化無障礙支援。

### 變更內容

#### 效能優化 - CLS 從 0.02 降至 0.00
- **trending-panel min-height**: 添加 310px 最小高度，防止骨架→空狀態切換時 120px 高度抖動
- **indices 骨架標題佔位**: 新增與 section-title 同高的骨架列，消除資料載入時位置偏移
- **板塊/AI 面板 x-cloak 移除**: 移除不必要的 x-cloak（已由 x-show 控制可見性）
- **stockPreview 快取**: getStockPreview() 改為 $watch 驅動的快取屬性，模板 7 次重複計算降為 0

#### VIX 恐慌指數色彩修正
- **isPositiveForMarket()**: VIX 上漲時色彩反轉為紅色（恐慌指標，上漲=市場負面）
- **getMarketSentiment()**: 情緒計算正確反映 VIX 反向關係
- 箭頭方向保持不變（仍反映實際漲跌方向）

#### 無障礙強化
- **暗色模式對比度**: --text-faint 從 #9098a4 提升至 #a0a8b4（WCAG AA 合規）
- **checkbox sr-only**: .module-chip input 從 display:none 改為 sr-only 模式
- **新聞卡片巢狀修復**: `<a>` 內嵌 `<button>` 重構為同級元素
- **depth-btn aria-pressed**: 深度按鈕添加 aria-pressed 狀態
- **aria-current 修正**: false → null（符合 ARIA 規範）
- **導覽列 aria-label i18n**: 硬編碼改為 t('a11y.main_nav')
- **AI 分析 aria-live**: 內容區域添加 aria-live="polite"
- **骨架 role=status**: 載入區域添加 role="status" + aria-label

#### CDN 元件驗證
- Alpine.js 3.15.8（最新）— SRI hash 驗證通過
- DOMPurify 3.3.1（最新）— SRI hash 驗證通過

---

## [v0.4.3] - 2026-02-23 - CLS 0.02 達成與 k8s 部署修正

### 概述

v0.4.3 將 CLS 從 0.55 優化至 0.02（Good 等級），修復 k8s 部署 CreateContainerConfigError，升級 MongoDB 至 7.0 LTS。

### 變更內容

#### 效能優化 - CLS 從 0.55 降至 0.02
- **系統字體堆疊**: 移除 Google Fonts Inter，改用 -apple-system/BlinkMacSystemFont/Segoe UI/Roboto（消除字型載入 CLS 0.26）
- **移除 shimmer 動畫**: Chrome 將 opacity 脈衝標記為 ANIMATION_HAS_NO_VISIBLE_CHANGE 非合成動畫（消除 CLS 0.23）
- **trendingLoading 初始值 true**: 與 HTML 骨架可見狀態一致，Alpine 初始化時骨架保持可見（消除 CLS 0.27）
- **SSR 預設文字**: x-text 元素加入繁體中文預設文字，Alpine 初始化前就有正確尺寸
- **empty-state x-cloak**: 空態提示從首次渲染就隱藏（CSS [x-cloak] 在 head 生效）
- **骨架預先可見**: indices-bar 移除 x-cloak，骨架在 Alpine.js 載入前即可見
- **market-pulse 佔位**: 載入中顯示骨架佔位區段，防止資料到達時版面位移
- **LCP 改善**: 938ms（移除外部字型網路請求的副效果）

#### k8s 部署修復
- **CreateContainerConfigError**: deployment.yaml 加 runAsUser/runAsGroup: 1000（修復非數字 UID 驗證失敗）
- **MongoDB 7.0 LTS**: 從 4.4（EOL）升級至 7.0（values.yaml + values-production.yaml）
- **Redis 健康檢查**: redis-cli ping 加認證密碼（requirepass 相容）

#### 安全強化
- **快取雜湊升級**: MD5 → SHA-256（adaptive_cache、cache_manager、db_cache_manager）
- **URL 協議驗證**: safeUrl() 防止 javascript: URI 注入
- **API 快取控制**: /api/ 和 /health 端點加 Cache-Control: no-cache
- **Semgrep 全掃描**: OWASP Top 10 + Python 規則集零發現

#### 版本同步
- 全專案版本統一至 0.4.3（VERSION、pyproject.toml、app/main.py、i18n、README）

---

## [v0.4.2] - 2026-02-23 - 安全掃描清理

### 概述

v0.4.2 初步嘗試 CLS 改善（後由 v0.4.3 徹底修復）、Semgrep 安全掃描清理。

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


