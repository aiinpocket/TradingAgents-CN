# TradingAgents 中文增強版

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.4.5-green.svg)](./VERSION)
[![Documentation](https://img.shields.io/badge/docs-中文文檔-green.svg)](./docs/)
[![Original](https://img.shields.io/badge/基於-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

> 基於多智能體辯論的美股分析系統
> **核心特性**: OpenAI | Anthropic Claude | 多智能體辯論 | LLM 可切換 | 完整 i18n（zh-TW / en） | 新聞標題翻譯 | AI 趨勢分析 | SSR 預渲染 (CLS 0.00) | Docker / K8s 部署 | 安全強化 | WCAG AA 無障礙

基於多智慧體大語言模型的**中文金融交易決策框架**。專為中文使用者優化，提供完整的美股分析能力。

## 致敬源專案

感謝 [Tauric Research](https://github.com/TauricResearch) 團隊創造的革命性多智慧體交易框架 [TradingAgents](https://github.com/TauricResearch/TradingAgents)！

**我們的使命**: 為中文使用者提供完整的中文化體驗，支持美股市場，推動 AI 金融技術在中文社群的普及應用。

## v0.4.5 - 節點即時進度 + 並行辯論 + 前端效能強化

> 最新版本：graph.stream() 串流偵測、節點級別即時進度回報、多空/風險並行辯論、分析速度大幅提升

### 亮點

#### 效能優化
- **節點級別即時進度**: graph.stream() 串流偵測狀態欄位變化，9 種進度事件即時回報前端（分析師完成、辯論進行中、決策完成等）
- **多空辯論並行化**: 單輪辯論時看漲/看跌研究員同時執行（parallel_invest_debate），串行 ~4s 降至 ~2s
- **風險分析師並行化**: 單輪辯論時 3 位風險分析師（激進/保守/中立）同時執行，串行 ~6s 降至 ~2s
- **分析師直接工具呼叫**: invoke_tools_direct() 跳過 LLM 工具決策，每位分析師節省 1 次 LLM 呼叫（2-5s）
- **資料預載入**: prefetch_analyst_data() 在圖執行前並行載入 7 個 API 結果到快取，分析師開始時零等待
- **工具結果快取**: 同一分析中多個分析師呼叫相同工具+參數時自動去重，避免重複 API 呼叫（如 FinnHub 情緒資料）
- **辯論輪數精簡**: depth 4 從 2 輪降為 1 輪（啟用並行），depth 5 從 3 輪降為 2 輪，大幅加速高深度分析
- **分析執行緒池擴容**: _ANALYSIS_EXECUTOR 4->8 workers，支援更高並行度
- **快取 TTL 優化**: 市場資料 2h->4h、新聞 6h->8h，減少同一交易日內重複 API 呼叫
- **MongoDB 連接池單例化**: 共享 MongoClient 單例（maxPoolSize=10），避免每次建立新連接
- **Markdown 渲染記憶化**: renderMarkdown() 使用 Map 快取（上限 100 筆），Alpine 反應式更新不再重複解析
- **圖結構精簡**: 移除 4 個不再使用的 ToolNode 圖節點和條件邊（-39 行）
- **英文翻譯異步化**: _background_translate() 不阻塞 SSE 回應，先回中文結果再背景翻譯
- **前端 compositor-only 動畫**: progress-fill 改用 transform scaleX()（零 layout reflow）
- **CSS containment**: log-container / panel / mover-row / index-card / debate-section 加入 contain（隔離 layout/style 回流範圍）
- **preload 最佳化**: Alpine.js + DOMPurify preload hint、preconnect 提前到 GA 之前
- **GZip 壓縮**: GZipMiddleware 自動壓縮回應（CSS/JS/API），傳輸量減少 ~60%
- **SSR 預渲染**: 後端注入快取 JSON 至 HTML，消除首屏 CLS（0.34 -> 0.00）
- **CWV 指標**: LCP 515ms / CLS 0.00 / TTFB 201ms — 全部 Good 等級
- **趨勢資料並行抓取**: ThreadPoolExecutor 批次並行，延遲降低約 50%
- **背景定時刷新**: 每 5 分鐘自動更新市場資料快取，前端每 5 分鐘重新載入
- **快取穿透防護**: 背景刷新採用「標記過期保留舊資料」策略，避免刷新中斷
- **AI 分析預產生**: 啟動時及背景刷新後自動生成中英文分析（2 小時 TTL）
- **前端平行初始化**: checkHealth + loadModels 使用 Promise.all 並行呼叫
- **共用 _stockMap 快取**: trendingData 變化時重建一次 symbol->stock 查詢表
- **dns-prefetch**: Google Analytics 域名 DNS 預解析
- **LLM Prompt 精簡**: Research/Risk Manager (~25-30%)、Trader/Bull/Bear (~40%) token 消耗降低
- **工具並行呼叫超時保護**: as_completed() 加入 30 秒超時，避免單一 API 卡住阻塞整個分析
- **fetchpriority**: CSS stylesheet=high、GA scripts=low（瀏覽器資源優先級提示）
- **touch-action: manipulation**: 消除行動裝置 300ms 點擊延遲
- **content-visibility: auto**: 首屏以下區域延遲繪製，提升捲動效能
- **分析管線效能計時器**: propagate() 自動記錄 prefetch/graph/total 各階段耗時，含節點級別完成時間戳
- **智慧模型配對**: 根據研究深度自動配對輕量快速模型（depth 1-3 分析師用 gpt-4o-mini/haiku，僅管理員用重型模型），o4-mini 不再拖慢全部 12 次 LLM 呼叫
- **工具快取命中率 100%**: prefetch 預載入 7 個 API -> 分析師 8 次呼叫全部命中，快取命中率日誌自動記錄
- **統一日期計算**: calc_start_date() 共用函式消除 3 處重複邏輯
- **MongoDB 深度防禦**: 查詢參數型別檢查防 NoSQL 操作符注入
- **原子性快取寫入**: 公司名稱快取使用 tempfile + os.replace 防止中斷損毀
- **投資辯論報告截斷**: 看漲/看跌研究員將 4 份分析報告截斷至 1500-2000 字元，降低辯論 token 消耗 ~25%
- **風險辯論者報告截斷**: truncate_report() 將 4 份完整報告截斷至 800 字元，減少風險辯論階段 ~50% LLM 輸入 token
- **共用公司名稱函式**: get_company_name() 提取至 stock_utils.py，4 位分析師共用單一映射表
- **股價計算去重**: _calc_price_change() 統一 3 處相同漲跌計算邏輯
- **WCAG 標題層級修正**: Markdown 標題統一映射 h3，消除 h2->h4 跳級問題

#### 資料更新頻率

首頁市場資料為「準即時」而非完全即時，更新機制如下：

| 資料類型 | 更新頻率 | 說明 |
|----------|----------|------|
| 指數/漲跌排行 | 每 5 分鐘 | 後端背景刷新 + 前端自動重新載入 |
| 新聞標題 | 每 5 分鐘 | 隨市場資料背景刷新同步更新 |
| AI 趨勢分析 | 每 2 小時 | 背景預產生，刷新後自動檢查更新 |
| 個股快照 | 5 分鐘快取 | 搜尋/選取時即時查詢，快取去重 |
| 資料來源延遲 | 15-20 分鐘 | yfinance 免費版 Yahoo Finance 延遲 |

> 實際使用者看到的市場數據總延遲約 **15-25 分鐘**（yfinance 延遲 + 快取週期）。如需完全即時數據，需升級至付費資料源。本系統定位為「日線級別分析」而非高頻交易。

#### i18n 國際化
- **161 翻譯鍵**: zh-TW / en 完全對稱，後端 33 key 雙語完整
- **新聞標題 i18n**: LLM 批次翻譯英文新聞為繁體中文，前端根據語言自動切換
- **台灣術語校正**: 確定性後處理（川普/輝達/標普/道瓊/聯準會/那斯達克）
- **後端 API 錯誤訊息 i18n**: 包含速率限制、請求大小、伺服器錯誤
- **document.title i18n**: 頁面標題隨語言切換

#### 安全強化
- **RequestSizeLimitMiddleware**: 同時防護 Content-Length 和 chunked transfer encoding
- **速率限制 IP 修復**: CF-Connecting-IP -> X-Real-IP -> client.host 優先順序
- **CSP 完整限制**: base-uri、form-action、object-src、worker-src、connect-src 精確域名（無萬用字元）
- **Swagger UI 安全預設**: 非 development 環境自動關閉 API 文件
- **SSR XSS 防護**: JSON 注入 `</script>` 自動跳脫
- **SEO Open Graph + JSON-LD**: og:url / og:site_name / og:locale + WebApplication schema
- **HSTS preload**: 強制 HTTPS + preload 指令
- **analysisId 前後端格式驗證**: 防止異常 ID 注入
- **並發安全**: asyncio.Lock 替換 bool + Event，消除 TOCTOU 競爭
- **DOMPurify defer**: 修復 SSR 競爭條件（async -> defer 確保載入順序）
- **CSP 修復**: 加入 GA inline script 的 sha256 hash（消除 console error）
- **安全依賴**: python-multipart>=0.0.22 / jinja2>=3.1.6 / certifi>=2026.2.25 / cryptography>=46.0.5 / tornado>=6.5.4
- **pip-audit**: 177 個依賴全數通過安全掃描（2026-02-27），0 個已知漏洞
- **安全審計**: 整體評分 8.3/10（後端 8/10、前端 9/10、容器 8/10、依賴 9/10）
- **翻譯管線 Prompt Injection 防護**: 外部新聞標題與分析報告翻譯前清理（角色偽裝/指令覆蓋/特殊 token 移除）
- **錯誤訊息清理**: 避免洩漏內部路徑與 API 金鑰（_sanitize_error_message）
- **Referrer Policy**: strict-origin-when-cross-origin 防止跨域洩漏

#### 無障礙 (a11y)
- **skip-to-content 快捷連結**: 鍵盤使用者直接跳至主要內容
- **WCAG AA 色彩對比**: 亮/暗色模式文字對比 >= 4.5:1（--text-faint 5.3:1、--amber-text 5.2:1）
- **ARIA table 語意**: 歷史表格完整 role 標記，報告區 tablist/tab/tabpanel 完整語意
- **觸控目標 44px**: 符合 WCAG 2.5.5 標準（含 480px 斷點 nav-btn / mover-row）
- **html lang 屬性**: 隨語言切換同步更新（zh-Hant / en）
- **WCAG 標題層級**: Markdown 渲染標題壓縮至 h3/h4（容器 h2 下不跳級）
- **Windows 高對比**: @media (forced-colors: active) 支援
- **高對比模式**: @media (prefers-contrast: more) 增強邊框和文字
- **列印友善**: @media print 表格/代碼塊分頁保護

#### UI/UX
- **漲跌排行 CSS Grid**: 固定欄寬跨行對齊，取代 flex 佈局
- **RWD 響應式**: 5 段式（桌面 1512px / 平板 960px / 768px / 手機 480px / 375px / 320px）
- **亮色/暗色主題**: 完整雙主題支援，一鍵切換
- **Markdown 渲染增強**: 代碼塊、引用區塊、連結、表格完整 CSS 樣式
- **分析取消**: DELETE API 端點 + 前端即時通知後端中止任務
- **表單驗證視覺回饋**: aria-invalid 紅色邊框 + 快速選股脈衝動畫
- **結果標籤頁淡入動畫**: x-transition.opacity 過渡效果
- **禁用按鈕提示文字**: 說明為何無法提交

#### 快取與資料管理
- **MongoDB TTL Index**: 30 天自動清理過期報告，防止資料無限膨脹
- **快取 TTL 修正**: 依資料類型區分清理策略（市場 10m / AI 分析 2h）
- **Dockerfile 多階段構建**: builder + runtime 分離，最終映像不含編譯工具（節省 ~400MB）

---

## v0.4.1

### Kubernetes 安全強化

- **Pod SecurityContext**: 應用、MongoDB、Redis 全面啟用 `runAsNonRoot`、`drop ALL capabilities`、`allowPrivilegeEscalation: false`
- **NetworkPolicy**: 生產環境限制 pod 間通訊，僅應用 pod 可存取 MongoDB/Redis
- **Dockerfile UID/GID**: 明確指定 UID/GID 1000，與 Helm `fsGroup` 一致

### 前端效能

- **SSE 連接生命週期**: 修復 EventSource 關閉後未清空、重連計時器未儲存的問題
- **CDN 預連接**: 新增 `<link rel="preconnect">` 加速 cdn.jsdelivr.net 資源載入
- **非阻塞載入**: gtag-init.js 改為 async 載入，不再阻塞渲染

### 無障礙與樣式

- **暗色模式對比度**: `--text-faint` 修正為 #9098a4（WCAG AA 4.73:1）
- **報告區域表格**: 新增 `.report-body table` 樣式，與 AI 分析內容表格一致

### 依賴同步

- **requirements.txt**: 同步 pyproject.toml 版本（langchain 1.x、openai 2.x）

---

## v0.4.0

### 效能與並行化

- **分析師並行執行**: LangGraph fan-out/fan-in 架構，4 位分析師（市場、社群、新聞、基本面）同時啟動，大幅縮短分析時間
- **風險分析師並行化**: 單輪辯論時 3 位風險分析師同時執行，省約 4 秒
- **分析引擎實例快取**: TradingAgentsGraph 依配置 hash 快取，省去重複初始化 LLM/Toolkit/圖結構的 3-5 秒
- **前端個股快照快取**: 5 分鐘記憶體快取 + 請求去重，避免重複查詢同一股票
- **FinnHub 報告鍵鎖去重**: per-key 雙重檢查鎖，避免並行分析師重複呼叫 API
- **API Rate Limiter 分離**: FinnHub (0.3s) / Yahoo Finance (0.1s) 獨立限速，消除跨端點阻塞
- **快取策略最佳化**: 基本面 key 移除日期參數（靠 TTL 控制）、股票資料 3 天日期桶、記憶體 metadata 索引避免重複掃描檔案系統
- **趨勢資料預熱**: 伺服器啟動時背景預載快取，第一位使用者無需等待
- **頁面可見性感知**: 瀏覽器分頁隱藏時暫停定時重新整理，節省資源
- **指數+板塊合併查詢**: 單一 yf.Tickers() 呼叫取得指數與板塊資料，減少 API 往返
- **漲跌幅小批次取得**: batch_size=10 降低 yfinance 併發壓力，提升穩定性
- **公司名稱持久化**: JSON 快取避免冷啟動大量 ticker.info 呼叫
- **記憶嵌入快取**: 5 個分析節點共用嵌入向量，減少 4 次嵌入 API 呼叫
- **Docker CSS/JS 壓縮**: 構建階段自動 minify 靜態資源（約 16% 縮減）

### 安全強化

- **速率限制器記憶體防護**: IP 追蹤上限 10,000 筆，自動清理過期條目，防止記憶體耗盡攻擊
- **API 錯誤脫敏**: 個股 API 不再回傳內部錯誤堆疊，改用 i18n 通用訊息
- **移除硬編碼密碼**: 所有開發腳本改用環境變數 `DB_PASSWORD`
- **MongoDB 升級**: 4.4 (EOL) -> 7.0 LTS

### CDN 與前端

- **Alpine.js**: 3.14.8 -> 3.15.8（含 SRI 完整性驗證）
- **DOMPurify**: 3.2.4 -> 3.3.1（含 SRI 完整性驗證）
- **更新頻率提示**: 首頁新增「每 10 分鐘自動更新」說明
- **行動裝置觸控優化**: 觸控目標符合 WCAG 2.5.5 標準（>= 36px）

---

## v0.1.15

### LLM生態系統大升級

- ** LLM **: OpenAIAnthropic Claude
- **LLM **: OpenAI 
- **純美股專注**: 移除所有中國 AI 模型，專注美股市場分析
- **動態供應商管理**: 支持動態添加和配置 LLM 供應商

### 核心特性

- **開放存取**: 公開專案，無需登入即可使用所有功能
- **產業板塊熱力圖**: 以視覺化方式呈現各產業 ETF 近一週表現
- **配置管理中心**: 視覺化的大模型配置、資料來源管理、系統設定
- **模型能力管理**: 智慧模型選擇，根據任務自動匹配最佳模型
- **宏觀經濟概覽**: 即時追蹤美股主要指數、國際指數、債券殖利率、商品價格

> 所有分析僅供資訊參考，不構成任何投資建議

### 國際化（i18n）支援

- **多語言架構**: 內建 i18n 翻譯框架，預設繁體中文，支援英文
- **熱門個股追蹤**: 自動篩選近一週波動最大的個股，依週漲跌幅排序
- **翻譯檔案**: 結構化的 JSON 語言檔案，方便擴充新語言

### 技術棧升級

- **API **: Web API `.env` 
- **成交量異常偵測**: 自動識別成交量顯著偏離均值的股票

### 內測申請

- **TradingAgents**: 
- **以「日」為分析單位**: 聚焦短中期市場動態，避免短線雜訊與長期預測
- **學術資料**: PDF論文和相關研究資料
- **語言切換**: 使用者可在介面中切換語言

### 熱門特區（全新功能）

- **開源友善**: 專為開源社群設計，不洩露任何敏感資訊
- **技術博客**: 詳細的技術分析和實現原理解讀
- **引用支持**: 標準的學術引用格式和參考文獻
- **PR**: Pull Request

### 安全性強化

- **分支保護**: GitHub分支保護策略和安全規則
- **開發工作流**: 標準化的開發流程和分支管理規範
- **安裝驗證**: 完整的安裝測試和驗證腳本
- **文檔重構**: 結構化的文檔系統和快速開始指南

## v0.1.14 

### 學術研究支持

- **MongoDB**: MongoDB
- **緊急程序**: 完整的緊急處理和故障恢複程序
- **測試框架**: 增強的測試覆蓋和驗證工具
- **部署指南**: 企業級部署和配置管理

### 開發者體驗升級

- **功能測試腳本**: 新增6個專項功能測試腳本
- **工具處理器測試**: Google工具處理器修複驗證
- **引導自動隱藏測試**: UI交互功能測試
- **數據目錄重組**: 優化的數據存儲結構和管理
- **數據遷移腳本**: 完整的數據遷移和備份工具
- **緩存優化**: 提升數據加載和分析結果緩存性能

---

## v0.1.13 

### 原生OpenAI端點支持

- **OpenAI**: OpenAIAPI
- **靈活模型選擇**: 可以使用任何OpenAI格式的模型，不限於官方模型
- **智能適配器**: 新增原生OpenAI適配器，提供更好的兼容性和性能
- **在線工具配置測試**: 工具配置和選擇邏輯測試

### LLM適配器架構優化

- **整合指南**: 完整的 LLM 整合開發文檔和測試工具
- **真實場景測試**: 實際使用場景的端到端測試
- **統一接口**: 所有LLM提供商使用統一的調用接口

### Web界面智能優化

- **美股獨立性測試**: 美股分析功能獨立性驗證
- **KeyError**: KeyError
- **UI**: 
- **配置管理**: 統一的端點和模型配置管理系統

## v0.1.12 

### 企業級工具鏈

- **智能新聞過濾器**: 基於AI的新聞相關性評分和質量評估
- **錯誤處理增強**: 改進的異常處理和自動重試機制
- **智能模型選擇**: 根據可用性自動選擇最佳模型
- **錯誤提示**: 更友好的錯誤提示和解決建議

### 數據管理優化

- **LLM**: 
- **多層次過濾機制**: 基礎過濾、增強過濾、集成過濾三級處理

### 測試覆蓋增強

- **全面測試覆蓋**: 新增15+個測試文件，覆蓋所有新功能
- **詳細技術文檔**: 新增8個技術分析報告和修複文檔
- **新聞質量評估**: 自動識別和過濾低質量、重複、無關新聞
- **統一新聞工具**: 整合多個新聞源，提供統一的新聞獲取接口

### 智能新聞分析模塊

- **文檔分類整理**: 按功能將文檔分類到docs子目錄
- **示例代碼歸位**: 演示腳本統一到examples目錄
- **新聞檢索器優化**: 增強新聞數據獲取和處理能力

## v0.1.12 重大更新

### 技術修複和優化

- **用戶指南完善**: 新增新聞過濾使用指南和最佳實踐
- **結構化辯論**: 看漲/看跌研究員進行深度分析
- **演示腳本**: 提供完整的新聞過濾功能演示
- **根目錄整潔**: 保持根目錄簡潔，提升項目專業度

## Web界面展示

### 完善測試和文檔

> **Web**: FastAPI + Alpine.js Web

> **截圖更新中**: 界面截圖正在更新，將使用美股分析範例替換。請參考下方的功能描述和使用指南。

### 項目結構優化

#### - 


- AAPLTSLANVDA
- 5
- LLMOpenAIAnthropic
- API

#### 實時分析進度


- 
- 
- 
- 

#### 分析結果展示


- //
- 
- 
- Markdown 匯出

### 多智能體協作架構

#### **全新技術架構**

- ** 美股支持**: 專注美股市場深度分析
- ** 5**: 225
- ** 智慧體選擇**: 市場技術、基本面、新聞、社交媒體分析師
- ** 彈性時間設定**: 支援歷史任意時間點分析

#### **企業級功能**

- ** 視覺化進度**: 即時顯示分析進展和剩餘時間
- ** 智慧步驟識別**: 自動識別目前分析階段
- ** 準確時間預估**: 基於歷史資料的智慧時間計算
- ** 狀態持久化**: 頁面重新整理不遺失分析進度

#### **智慧分析增強**

- ** 投資決策**: 明確的買入/持有/賣出建議
- ** 多維分析**: 技術面、基本面、新聞面綜合評估
- ** 量化指標**: 置信度、風險評分、目標價位
- **專業報告**: 支援 Markdown 格式匯出

#### **多LLM模型管理**

- **多AI提供商**: OpenAI、Anthropic
- ** 60+**: 
- ** 配置持久化**: URL參數儲存，重新整理保持設定
- ** 快速切換**: 5個熱門模型一鍵選擇按鈕

### Web界面操作指南

#### **智能分析配置**

1. **啟動系統**: `python start_app.py` 或 `docker-compose up -d`
2. **開啟瀏覽器**: `http://localhost:8501`
3. **瀏覽首頁**: 查看市場總覽、漲跌排行、AI 趨勢分析
4. **切換至分析頁籤**: 輸入股票代碼（AAPL、TSLA、NVDA 等）
5. **選擇模型**: 選擇 LLM 提供商與模型
6. **開始分析**: 點擊「開始分析」按鈕，透過 SSE 串流即時查看進度
7. **查看結果**: 瀏覽各智慧體分析報告與最終交易建議
8. **匯出報告**: 以 Markdown 格式匯出分析結果

#### **即時進度追蹤**

- ** 美股**: `AAPL`, `TSLA`, `MSFT`, `NVDA`, `GOOGL`

#### **分析模式**

- **標準分析**: 多空辯論 + 風險評估（預設 2 輪辯論）
- **深度分析**: 可透過 .env 調整 `MAX_DEBATE_ROUNDS` 和 `MAX_RISK_DISCUSS_ROUNDS`

#### **專業結果展示**

- ** 即時重新整理**: 分析過程中可隨時重新整理頁面，進度不遺失
- ** 行動裝置適配**: 支援手機和平板裝置訪問
- ** 深色模式**: 自動適配系統主題設定
- **快速鍵**: 支援Enter鍵快速提交分析
- ** 歷史記錄**: 自動儲存最近的分析配置

> **詳細指南**: 完整的Web界面使用說明請參考 [ Web界面詳細使用指南](docs/usage/web-interface-detailed-guide.md)

## 功能特性一覽

### **v0.1.12**


| | | |
| ---------------------- | ----------- | ---------------------------------------- |
| ** ** | v0.1.12 | AI |
| ** ** | v0.1.12 | // |
| ** ** | v0.1.12 | |
| ** LLM** | v0.1.11 | 460+ |
| ** ** | v0.1.11 | URL |
| ** ** | v0.1.11 | |
| ** 實時進度顯示** | v0.1.10 | 異步進度跟蹤，智能步驟識別，準確時間計算 |
| ** 智能會話管理** | v0.1.10 | 狀態持久化，自動降級，跨頁面恢複 |
| ** 一鍵查看報告** | v0.1.10 | 分析完成後一鍵查看，智能結果恢複 |
| ** FastAPI ** | | |
| ** 配置管理** | 完整支持 | Web端API密鑰管理，模型選擇，參數配置 |

### CLI **v0.1.9**


| | | |
| ----------------------- | ----------- | ------------------------------------ |
| ** 界面與日誌分離** | 完整支持 | 用戶界面清爽美觀，技術日誌獨立管理 |
| ** 智能進度顯示** | 完整支持 | 多階段進度跟蹤，防止重複提示 |
| ** 時間預估功能** | 完整支持 | 智能分析階段顯示預計耗時 |
| ** Rich** | | |

### LLM **v0.1.13**


| | | | |
| ----------------- | ---------------------------- | ----------------------- | -------- |
| **OpenAI** | GPT-4o, GPT-4o-mini | | |
| **Anthropic** | Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5 | | |

**持久化**: URL參數存儲，刷新保持 | **智能切換**: 一鍵切換不同提供商

### 界面截圖


| | | |
| ------------- | ---------------------- | ------------------------ |
| ** 美股** | FinnHub, Yahoo Finance | NYSE, NASDAQ，實時數據 |
| ** 新聞** | Google News | 實時新聞，多語言支持 |

### 主要功能展示

**分析師團隊**: 市場分析 | 基本面分析 | 新聞分析 | 情緒分析
**研究團隊**: 看漲研究員 | 看跌研究員 | 交易決策員
**管理層**: 風險管理員 | 研究主管

## 快速開始

### Docker ()

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
cp .env.example .env
# .env API

# 3. 啟動服務
# 首次啟動或代碼變更時（需要構建鏡像）
docker-compose up -d --build

# 日常啟動（鏡像已存在，無代碼變更）
docker-compose up -d

# 智能啟動（自動判斷是否需要構建）
# Windows環境
powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1

# Linux/Mac
chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh

# 4. 訪問應用
# Web界面: http://localhost:8501
```

### 核心功能特色

```bash
# 1. pip 升級（建議）
python -m pip install --upgrade pip

# 2. 安裝依賴
pip install -r requirements-lock.txt
pip install -e . --no-deps

# 完整安裝（含所有依賴，可能較慢）
# pip install -e .

# Windows PyYAML 編譯問題解決方案見文檔

# 3. 啟動應用
python start_app.py

# 4. 訪問 http://localhost:8501
```

### 數據源與市場

1. **額外說明**：: OpenAI / Anthropic
2. ****: `AAPL` ()
3. ****: " "
4. ****: 
5. ****: " "
6. ****: Markdown

## 核心優勢

- ** 智能新聞分析**: v0.1.12新增AI驅動的新聞過濾和品質評估系統
- ** 多層次過濾**: 基礎、增強、集成三級新聞過濾機制
- ** 統一新聞工具**: 整合多源新聞，提供統一的智能檢索接口
- **LLM**: OpenAI Anthropic 
- **配置持久化**: 模型選擇真正持久化，URL參數存儲，刷新保持
- **實時進度**: v0.1.10 異步進度跟蹤，告別黑盒等待
- ** 智能會話**: 狀態持久化，頁面刷新不遺失分析結果
- ** 全球市場**: 美股數據 + 國際AI模型 + 中文界面
- ** 容器化**: Docker一鍵部署，環境隔離，快速擴展
- ** 專業報告**: 多格式導出，自動生成投資建議
- ** 穩定可靠**: 多層數據源，智能降級，錯誤恢復

## 技術架構

**後端**: Python 3.10+ | LangChain 1.x | LangGraph | FastAPI | MongoDB | Redis
**AI 引擎**: OpenAI (GPT-4o, o4-mini) | Anthropic (Claude Opus 4.6, Sonnet 4.6)
**前端**: Alpine.js 3.15.8 | DOMPurify 3.3.1 | CSS Grid | SSE 即時串流 | SSR 預渲染
**資料來源**: FinnHub | Yahoo Finance | Google News
**部署**: Docker | Docker Compose | Kubernetes (Helm) | GitHub Actions CI/CD

## REST API 端點

所有 API 路徑皆以 `/api` 為前綴。

### 分析 (`/api/analysis`)

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/analysis/start` | 啟動股票分析（回傳 analysis_id） |
| GET | `/analysis/{id}/stream` | SSE 即時串流分析進度與結果 |
| GET | `/analysis/{id}/status` | 查詢分析狀態（pending/running/completed/failed） |
| DELETE | `/analysis/{id}` | 取消進行中的分析 |
| GET | `/analysis/history` | 取得歷史分析記錄（記憶體 + MongoDB） |
| GET | `/analysis/stock-context/{symbol}` | 取得個股快照（股價、新聞、基本資料） |

### 趨勢 (`/api/trending`)

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/trending/overview` | 市場總覽（指數、板塊、漲跌排行、新聞） |
| GET | `/trending/indices` | 主要指數即時數據 |
| GET | `/trending/ai-analysis` | AI 趨勢分析摘要（?lang=zh-TW/en） |

### 設定 (`/api/config`)

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/config/status` | API 金鑰配置狀態 |
| GET | `/config/models` | 可用 LLM 模型清單 |

### 共用端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/health` | 健康檢查（版本、運行時間、記憶體） |
| GET | `/` | 首頁（SSR 預渲染） |

## 文檔和支持

- ** 完整文檔**: [docs/](./docs/) - 安裝指南、使用教程、API文檔
- ** 故障排除**: [troubleshooting/](./docs/troubleshooting/) - 常見問題解決方案
- ** 更新日誌**: [CHANGELOG.md](./docs/releases/CHANGELOG.md) - 詳細版本歷史
- ** 快速開始**: [QUICKSTART.md](./QUICKSTART.md) - 5分鐘快速部署指南

## 中文增強特色

**相比原版新增**: 智能新聞分析 | 多層次新聞過濾 | 新聞質量評估 | 統一新聞工具 | 多LLM提供商集成 | 模型選擇持久化 | 快速切換按鈕 | 即時進度顯示 | 智慧會話管理 | 中文介面 | Docker部署 | 專業報告匯出 | 統一日誌管理 | Web配置介面 | 成本優化

**Docker**:

- **Web**: TradingAgents-CN
- **MongoDB**: 
- **Redis**: 
- **MongoDB Express**: 資料庫管理介面（需 `--profile management` 啟動）
- **Redis Commander**: 快取管理介面（需 `--profile management` 啟動）

#### 方式二：本地部署

**適用場景**: 開發環境、自定義配置、離線使用

### 智能體團隊

- Python 3.10+ ( 3.11)
- 4GB+ RAM ( 8GB+)
- 

### 本地部署

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
python -m venv env
# Windows
env\Scripts\activate
# Linux/macOS
source env/bin/activate

# 3. pip
python -m pip install --upgrade pip

# 4. 
pip install -e .

# requirements.txt 
# - (MongoDB + Redis)
# - (Yahoo Finance, FinnHub)
# - Web
```

### 配置API密鑰

#### API 

```bash
# 複製環境變數範本
cp .env.example .env

# .env API
FINNHUB_API_KEY=your_finnhub_api_key_here

# AIAPI
OPENAI_API_KEY=your_openai_api_key_here

# 無數據庫模式
# 環境變量設定
MONGODB_ENABLED=false # trueMongoDB
REDIS_ENABLED=false # trueRedis
MONGODB_HOST=localhost
MONGODB_PORT=27017 # MongoDB
REDIS_HOST=localhost
REDIS_PORT=6379 # Redis

# Docker
# MONGODB_HOST=mongodb
# REDIS_HOST=redis
```

#### 部署模式配置說明

**本地部署模式**：

```bash
# 數據庫配置（本地部署）
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_HOST=localhost # 
MONGODB_PORT=27017 # 本地快取
REDIS_HOST=localhost # 
REDIS_PORT=6379 # 
```

**Docker**

```bash
# Docker
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_HOST=mongodb # Docker
MONGODB_PORT=27017 # Docker 容器快取
REDIS_HOST=redis # Docker
REDIS_PORT=6379 # 
```

> **配置提示**：
>
> - - MongoDBRedis
> - Dockerdocker-compose
> - docker-compose.yml

#### Anthropic Claude 

```bash
# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### MongoDB + Redis

#### 高性能數據存儲支持

 **MongoDB** **Redis** 

- ** 股票數據緩存**: 減少API調用，提升響應速度
- ** 智能降級機制**: MongoDB → API → 本地緩存的多層數據源
- ** 高性能緩存**: Redis緩存熱點數據，毫秒級響應
- ** 數據持久化**: MongoDB存儲歷史數據，支持離線分析

#### 數據庫部署方式

** Docker**

Docker

```bash
# Docker
docker-compose up -d --build
# - Web (8501)
# - MongoDB (27017)
# - Redis (6379)
# - (8081, 8082)
```

** - **



**方式一：僅啟動數據庫服務**

```bash
# 僅啟動 MongoDB + Redis 服務（不啟動Web應用）
docker-compose up -d mongodb redis mongo-express redis-commander

# 查看服務狀態
docker-compose ps

# 停止服務
docker-compose down
```

**方式二：完全本地安裝**

```bash
# 數據庫依賴已包含在 requirements.txt 中

# MongoDB ( 27017)
mongod --dbpath ./data/mongodb

# Redis ( 6379)
redis-server
```

> **重要說明**：
>
> - - ** Docker**: 
> - ** **: 
> - ** **: Docker

#### 數據庫配置選項

**MongoDB 配置**

```bash
# MongoDB 
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=trading_agents
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_password

# Redis 
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

```bash
# .env 資料庫設定
MONGODB_ENABLED=true
MONGODB_URI=mongodb://localhost:27017/trading_agents
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

#### 數據庫功能特性

**MongoDB **

- 
- 
- 
- 
- 

**Redis **

- 
- API
- 
- 
- 

#### 智能降級機制



```
 
1. Redis ()
2. MongoDB ()
3. Yahoo Finance / FinnHub API ()
4. ()
5. 
```

```bash
# .env 快取設定
MONGODB_ENABLED=true
REDIS_ENABLED=true
```

#### 性能優化建議

**查詢優化**

```bash
# MongoDB 
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=5
MONGODB_MAX_IDLE_TIME=30000

# Redis 
REDIS_MAX_CONNECTIONS=20
REDIS_CONNECTION_POOL_SIZE=10
REDIS_SOCKET_TIMEOUT=5
```

#### 數據庫管理工具

```bash
# 初始化數據庫
python scripts/setup/init_database.py

# 驗證系統狀態
python scripts/validation/check_system_status.py

# 清理快取
python scripts/maintenance/cleanup_cache.py --days 7
```

#### 故障排除

**常見問題**

1. ** Windows 10 ChromaDB**

 **Windows 10 已知問題**：Windows 10 `Configuration error: An instance of Chroma already exists for ephemeral with different settings` Windows 11

 **解決方案**：

 ```bash
 # 1
 # .env 
 MEMORY_ENABLED=false

 # 2
 powershell -ExecutionPolicy Bypass -File scripts\fix_chromadb_win10.ps1

 # 3
 # PowerShell -> ""
 ```

 **完整修復指南**：[Windows 10](docs/troubleshooting/windows10-chromadb-fix.md)
2. **MongoDB**

 **Docker**

 ```bash
 # 查看 MongoDB 日誌
 docker-compose logs mongodb

 # 重啟 MongoDB
 docker-compose restart mongodb
 ```


 ```bash
 # MongoDB
 ps aux | grep mongod

 # MongoDB
 sudo systemctl restart mongod # Linux
 brew services restart mongodb # macOS
 ```
3. **Redis**

 ```bash
 # Redis
 redis-cli ping

 # Redis
 redis-cli flushdb
 ```
4. ****

 ```bash
 # 
 python scripts/validation/check_system_status.py

 # 
 python scripts/maintenance/cleanup_cache.py --days 7
 ```

> **提示**: 即使不配置數據庫，系統仍可正常運行，會自動降級到API直接調用模式。數據庫配置是可選的性能優化功能。

> **詳細文檔**: 更多數據庫配置信息請參考 [數據庫架構文檔](docs/architecture/database-architecture.md)

### 開始分析

#### 新增功能：專業分析報告導出



**支援格式**

- **Markdown (.md)** - 純文字格式，適合版本控制與二次編輯

**匯出內容**

- **各階段分析報告** - 市場/社群/新聞/基本面
- **辯論過程紀錄** - 多空辯論與風險討論
- **最終交易建議** - 含信心度與風險評估

**使用方式**

1. 完成分析後點擊「匯出」按鈕
2. 系統自動產生 Markdown 格式報告
3. 可直接下載或複製內容

### 環境要求

#### Docker

Docker

```bash
# Docker
# Web: http://localhost:8501
# MongoDB Express: http://localhost:8081 (需 --profile management)
# Redis Commander: http://localhost:8082 (需 --profile management)

# 查看服務狀態
docker-compose ps

# 查看 Web 日誌
docker-compose logs -f web
```

#### 本地啟動



```bash
# 1. 
# Windows
.\env\Scripts\activate
# Linux/macOS
source env/bin/activate

# 2. 
pip install -e .

# 3. Web
python start_app.py
```

 `http://localhost:8501`

**Web**:

- **股票代碼輸入**: AAPL, TSLA, NVDA 等美股代碼
- **即時資料**: FinnHub Yahoo Finance 多來源整合
- **SSE 串流**: 即時查看各智慧體分析進度
- **報告匯出**: Markdown 匯出
- **多空辯論**: 多方/空方研究員辯論機制
- **風險評估**: 積極/保守/中立三方風險辯論
- **歷史紀錄**: 分析結果持久化儲存
- **中英雙語**: 完整 i18n 國際化支援

**分析模式**:

- **標準分析**: 多空辯論 + 風險評估（預設 2 輪辯論）
- **深度分析**: 可透過 .env 調整 `MAX_DEBATE_ROUNDS` 和 `MAX_RISK_DISCUSS_ROUNDS`

#### 代碼調用（適合開發者）

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# OpenAI
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-4o" # 
config["quick_think_llm"] = "gpt-4o-mini" # 

# 初始化分析圖
ta = TradingAgentsGraph(debug=True, config=config)

# ()
state, decision = ta.propagate("AAPL", "2024-01-15")

# 輸出結果
print(f": {decision['action']}")
print(f": {decision['confidence']:.1%}")
print(f": {decision['risk_score']:.1%}")
print(f": {decision['reasoning']}")
```

#### 快速啟動腳本

```bash
# OpenAI
python examples/simple_analysis_demo.py
```

#### 數據目錄配置

**研究深度級別說明**:

```bash
# 查看當前配置
python -m cli.main data-config --show

# 設定數據目錄
python -m cli.main data-config --set /path/to/your/data

# 重置為預設值
python -m cli.main data-config --reset
```

**新功能**: 靈活配置數據存儲路徑，支持多種配置方式：

```bash
# Windows
set TRADING_AGENTS_DATA_DIR=C:\MyTradingData

# Linux/macOS
export TRADING_AGENTS_DATA_DIR=/home/user/trading_data
```

**環境變量配置**:

```python
from tradingagents.config_manager import ConfigManager

# 程式碼中使用
config_manager = ConfigManager()
config_manager.set_data_directory("/path/to/data")

# 取得數據目錄
data_dir = config_manager.get_data_directory()
print(f": {data_dir}")
```

**配置優先級**: 程序設置 > 環境變量 > 配置文件 > 默認值

詳細說明請參考: [ 數據目錄配置指南](docs/configuration/data-directory-configuration.md)

### 安裝步驟

```bash
# 啟動 CLI
python -m cli.main
```

## **快速導航** - 找到您需要的內容


| **...** | **** | **** |
| --------------- | --------------------------------------------------------- | ---------------- |
| **快速上手** | [ 快速開始](docs/overview/quick-start.md) | 10分鐘 |
| **了解架構** | [ 系統架構](docs/architecture/system-architecture.md) | 15分鐘 |
| **看代碼示例** | [ 基礎示例](docs/examples/basic-examples.md) | 20分鐘 |
| **遇到問題** | [常見問題](docs/faq/faq.md) | 5分鐘 |
| **深度學習** | [ 完整文檔目錄](#-詳細文檔目錄) | 2小時+ |

> **提示**: 我們的 `docs/` 目錄包含了 **50,000+字** 的詳細中文文檔，這是與原版最大的區別！

## - 

> ** ** AI **50,000** **20+** **100+** 

### 報告導出功能


| | TradingAgents | **** |
| ------------ | ------------------ | -------------------------- |
| **** | | **** |
| **** | | **** |
| **** | | ** + ** |
| **** | | **** |
| **** | | **FAQ + ** |
| **** | | **100+ ** |

### - 

#### **新手入門路徑** (推薦從這裡開始)

1. [ 項目概述](docs/overview/project-overview.md) - **了解項目背景和核心價值**
2. [ 詳細安裝](docs/overview/installation.md) - **各平台詳細安裝指南**
3. [ 快速開始](docs/overview/quick-start.md) - **10分鐘上手指南**
4. [ 基礎示例](docs/examples/basic-examples.md) - **8個實用的入門示例**

#### **架構理解路徑** (深入了解系統設計)

1. [ 系統架構](docs/architecture/system-architecture.md) - **完整的系統架構設計**
2. [ 智能體架構](docs/architecture/agent-architecture.md) - **多智能體協作機制**
3. [ 數據流架構](docs/architecture/data-flow-architecture.md) - **數據處理全流程**
4. [ 圖結構設計](docs/architecture/graph-structure.md) - **LangGraph工作流程**

#### **智能體深度解析** (了解每個智能體的設計)

1. [ 分析師團隊](docs/agents/analysts.md) - **四類專業分析師詳解**
2. [ 研究員團隊](docs/agents/researchers.md) - **看漲/看跌辯論機制**
3. [ 交易員智能體](docs/agents/trader.md) - **交易決策制定流程**
4. [ 風險管理](docs/agents/risk-management.md) - **多層次風險評估**
5. [ 管理層智能體](docs/agents/managers.md) - **協調和決策管理**

#### **數據處理專題** (掌握數據處理技術)

1. [ 數據源集成](docs/data/data-sources.md) - **多數據源API集成**
2. [ 數據處理流程](docs/data/data-processing.md) - **數據清洗和轉換**
3. [ 緩存策略](docs/data/caching.md) - **多層緩存優化性能**

#### **配置和優化** (性能調優和定制)

1. [ 配置指南](docs/configuration/config-guide.md) - **詳細配置選項說明**
2. [ LLM](docs/configuration/llm-config.md) - ****

#### **高級應用** (擴展開發和實戰)

1. [ 基礎示例](docs/examples/basic-examples.md) - **8個實用基礎示例**
2. [ 高級示例](docs/examples/advanced-examples.md) - **複雜場景和擴展開發**

#### **問題解決** (遇到問題時查看)

1. [常見問題](docs/faq/faq.md) - **FAQ和故障排除**

### 啟動應用

- **文檔文件數**: 20+ 個專業文檔
- **總字數**: 50,000+ 字詳細內容
- **代碼示例**: 100+ 個實用示例
- **架構圖表**: 10+ 個專業圖表
- **專業分工**: 基本面、技術面、新聞面、社交媒體四大分析師

### 交互式分析

- ** 完全中文化**: 專為中文用戶優化的表達方式
- ** 圖文並茂**: 豐富的架構圖和流程圖
- ** 代碼豐富**: 每個概念都有對應的代碼示例
- ** 深度剖析**: 不僅告訴你怎麼做，還告訴你為什麼這樣做
- ** 實用導向**: 所有文檔都面向實際應用場景

---

## 詳細文檔目錄

### **docs/ ** - 

```
docs/
 overview/ # - 
 project-overview.md # 
 quick-start.md # 10
 installation.md # 

 architecture/ # - 
 system-architecture.md # 
 agent-architecture.md # 
 data-flow-architecture.md # 
 graph-structure.md # LangGraph

 agents/ # - 
 analysts.md # 
 researchers.md # /
 trader.md # 
 risk-management.md # 
 managers.md # 

 data/ # - 
 data-sources.md # 
 data-processing.md # 
 caching.md # 

 configuration/ # - 
 config-guide.md # 
 llm-config.md # LLM

 examples/ # - 
 basic-examples.md # 8
 advanced-examples.md # 

 faq/ # - 
 faq.md # FAQ
```

### **重點推薦文檔** (必讀精選)

#### **最受歡迎的文檔**

1. **[項目概述](docs/overview/project-overview.md)**

   > 了解項目的核心價值和技術特色，5分鐘讀懂整個框架

2. **[系統架構](docs/architecture/system-architecture.md)**

   > 深度解析多智能體協作機制，包含詳細架構圖

3. **[基礎示例](docs/examples/basic-examples.md)**

   > 8個實用示例，從股票分析到投資組合優化

#### **技術深度文檔**

1. **[智能體架構](docs/architecture/agent-architecture.md)**

   > 多智能體設計模式和協作機制詳解

2. **[數據流架構](docs/architecture/data-flow-architecture.md)**

   > 數據獲取、處理、快取的完整流程

3. **[研究員團隊](docs/agents/researchers.md)**

   > 看漲/看跌研究員辯論機制的創新設計

#### **實用工具文檔**

1. **[Web界面指南](docs/usage/web-interface-guide.md)**

   > 完整的Web界面使用教程，包含分析深度詳細說明

2. **[投資分析指南](docs/usage/investment_analysis_guide.md)**

   > 從基礎到高級的完整投資分析教程

3. **[LLM配置](docs/configuration/llm-config.md)**

   > 多LLM模型配置和成本優化策略

4. **[快取策略](docs/data/caching.md)**

   > 多層快取設計，顯著降低API調用成本

5. **[常見問題](docs/faq/faq.md)**

   > 詳細的FAQ和故障排除指南

### **按模塊瀏覽文檔**

<details>
<summary><strong>概覽文檔</strong> - 項目入門必讀</summary>

- [項目概述](docs/overview/project-overview.md) - 詳細的項目背景和特性介紹
- [快速開始](docs/overview/quick-start.md) - 從安裝到第一次運行的完整指南
- [詳細安裝](docs/overview/installation.md) - 各平台詳細安裝說明

</details>

<details>
<summary><strong>架構文檔</strong> - 深度理解系統設計</summary>

- [系統架構](docs/architecture/system-architecture.md) - 完整的系統架構設計
- [智能體架構](docs/architecture/agent-architecture.md) - 智能體設計模式和協作機制
- [數據流架構](docs/architecture/data-flow-architecture.md) - 數據獲取、處理和分發流程
- [圖結構設計](docs/architecture/graph-structure.md) - LangGraph工作流程設計

</details>

<details>
<summary><strong>智能體文檔</strong> - 核心組件詳解</summary>

- [分析師團隊](docs/agents/analysts.md) - 四類專業分析師詳解
- [研究員團隊](docs/agents/researchers.md) - 看漲/看跌研究員和辯論機制
- [交易員智能體](docs/agents/trader.md) - 交易決策制定流程
- [風險管理](docs/agents/risk-management.md) - 多層次風險評估體系
- [管理層智能體](docs/agents/managers.md) - 協調和決策管理

</details>

<details>
<summary><strong>數據處理</strong> - 技術核心實現</summary>

- [數據源集成](docs/data/data-sources.md) - 支持的數據源和API集成
- [數據處理流程](docs/data/data-processing.md) - 數據清洗、轉換和驗證
- [快取策略](docs/data/caching.md) - 多層快取優化性能

</details>

<details>
<summary><strong>配置與部署</strong> - 性能調優指南</summary>

- [配置指南](docs/configuration/config-guide.md) - 詳細的配置選項說明
- [LLM配置](docs/configuration/llm-config.md) - 大語言模型配置優化

</details>

<details>
<summary><strong>示例和教程</strong> - 實戰應用指南</summary>

- [基礎示例](docs/examples/basic-examples.md) - 8個實用的基礎示例
- [高級示例](docs/examples/advanced-examples.md) - 複雜場景和擴展開發

</details>

<details>
<summary><strong>幫助文檔</strong> - 問題解決方案</summary>

- [常見問題](docs/faq/faq.md) - 詳細的FAQ和解決方案

</details>

## 成本控制

### 為什麼選擇我們的文檔？

- **經濟模式**: $0.01-0.05/次分析 (使用 gpt-4o-mini)
- **標準模式**: $0.05-0.15/次分析 (使用 gpt-4o)
- **高精度模式**: $0.10-0.30/次分析 (使用 gpt-4o + 多輪辯論)

### 文檔統計數據

```python
# 低成本配置範例
cost_optimized_config = {
 "deep_think_llm": "gpt-4o-mini",
 "quick_think_llm": "gpt-4o-mini", 
 "max_debate_rounds": 1,
 "online_tools": False # 
}
```

## 貢獻指南



### 文檔特色

- **Bug** - 
- **詳細分析報告** - 技術分析，基本面分析，市場情緒，新聞事件
- **風險提示** - 完整的投資風險聲明和免責條款
- **配置信息** - 分析參數，模型信息，生成時間
- **新功能** - 添加新的功能特性

### 典型使用成本

1. Fork 
2. (`git checkout -b feature/AmazingFeature`)
3. (`git commit -m 'Add some AmazingFeature'`)
4. (`git push origin feature/AmazingFeature`)
5. Pull Request

### 成本優化建議

查看所有貢獻者和詳細貢獻內容：**[ 貢獻者名單](CONTRIBUTORS.md)**

## 許可證

 Apache 2.0 [LICENSE](LICENSE) 

### 貢獻類型

- 
- 
- 
- 
- 
- 

## 貢獻方式

### 貢獻流程

 [Tauric Research](https://github.com/TauricResearch) 

- ** 願景領導者**: 感謝您們在AI金融領域的前瞻性思考和創新實踐
- ** 珍貴源碼**: 感謝您們開源的每一行代碼，它們凝聚着無數的智慧和心血
- ** 架構大師**: 感謝您們設計了如此優雅、可擴展的多智能體框架
- ** 技術先驅**: 感謝您們將前沿AI技術與金融實務完美結合
- ** 持續貢獻**: 感謝您們持續的維護、更新和改進工作

### 查看貢獻者

TradingAgents-CN

詳細的貢獻者名單和貢獻內容請查看：**[ 貢獻者名單](CONTRIBUTORS.md)**



- **Docker** - 
- **文檔改進** - 完善文檔和教程
- **Bug** - 
- **本地化** - 翻譯和本地化工作
- **代碼優化** - 性能優化和代碼重構
- **報告導出功能** - 多格式輸出支持
- ** 開源貢獻**: 感謝您們選擇Apache 2.0協議，給予開發者最大的自由
- ** 知識分享**: 感謝您們提供的詳細文檔和最佳實踐指導

本專案基於 [TradingAgents](https://github.com/TauricResearch/TradingAgents) 開發，採用 Apache 2.0 授權

### 許可證說明



- ** 技術傳播**: 讓優秀的TradingAgents技術得到更廣泛的應用
- ** 教育普及**: 為AI金融教育提供更好的工具和資源
- ** 文化橋梁**: 在技術社群之間搭建交流合作的橋梁
- ** 創新推動**: 推動金融科技領域的AI技術創新和應用

### 向源項目開發者致敬



### 社區貢獻者致謝



- **智能決策**: 交易員基於所有輸入做出最終投資建議
- **風險管理**: 多層次風險評估和管理機制
- **智能體選擇**: 可選擇不同的分析師組合
- **智能分析師選擇**: 市場技術、基本面、新聞、社交媒體分析師

## 版本歷史

- **v0.4.5** (2026-02-27): 節點級別即時進度回報、多空/風險並行辯論、分析師直接工具呼叫、工具結果快取去重、快取 TTL 優化、圖結構精簡、SSE try/finally 清理、compositor-only 動畫、SSR 預渲染 CLS 0.00、CSP 構建器提取消除重複、版本常數化、術語校正共用模組化、詞庫擴充（+8 組台灣慣用語）、AI 分析中英文平行產生、背景任務平行化、CSP 預快取、MongoDB 單例化、CI deploy race condition 修復
- **v0.4.4** (2026-02-26): SSR 預渲染 CLS 0.00、新聞 i18n 翻譯、AI 趨勢分析、WCAG AA 對比度、安全依賴更新（python-multipart/tornado/certifi CVE 修復）、台灣術語校正
- **v0.4.1** (2026-02-23): Helm 安全強化、SSE 連接修復、暗色對比度、CDN 預連接
- **v0.4.0** (2026-02-23): 分析師並行化、安全強化、CDN 升級、行動觸控優化
- **v0.1.13** (2025-08-02): OpenAILLM
- **v0.1.12** (2025-07-29): 
- **v0.1.11** (2025-07-27): LLM
- **v0.1.10** (2025-07-18): Web
- **v0.1.9** (2025-07-16): CLI
- **v0.1.8** (2025-07-15): Web
- **v0.1.7** (2025-07-13): 
- **v0.1.6** (2025-07-11): 
- **v0.1.5** (2025-07-08): 
- **v0.1.4** (2025-07-05): 
- **v0.1.3** (2025-06-28): 
- **v0.1.2** (2025-06-15): Web
- **v0.1.1** (2025-06-01): LLM

 **詳細更新日誌**: [CHANGELOG.md](./docs/releases/CHANGELOG.md)

## 聯繫方式

- **GitHub Issues**: [](https://github.com/aiinpocket/TradingAgents-CN/issues)
- **Email**: hsliup@163.com
- **原項目**: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- **文檔**: [完整文檔目錄](docs/)

## 風險提示

**程序化配置**:

- 
- AI
- 
- 

---

<div align="center">

** Star**

[ Star this repo](https://github.com/aiinpocket/TradingAgents-CN) | [ Fork this repo](https://github.com/aiinpocket/TradingAgents-CN/fork) | [ Read the docs](./docs/)

</div>
