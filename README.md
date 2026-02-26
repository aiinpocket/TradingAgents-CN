# TradingAgents 

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.4.5-green.svg)](./VERSION)
[![Documentation](https://img.shields.io/badge/docs--green.svg)](./docs/)
[![Original](https://img.shields.io/badge/-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

> 基於多智能體辯論的美股分析系統
> **核心特性**: OpenAI | Anthropic Claude | 多智能體辯論 | LLM 可切換 | 完整 i18n（zh-TW / en） | 新聞標題翻譯 | AI 趨勢分析 | SSR 預渲染 (CLS 0.00) | Docker / K8s 部署 | 安全強化 | WCAG AA 無障礙

****

## 

 [Tauric Research](https://github.com/TauricResearch) [TradingAgents](https://github.com/TauricResearch/TradingAgents)

** **: AI

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
- **Markdown 渲染記憶化**: renderMarkdown() 使用 Map 快取（上限 30 筆），Alpine 反應式更新不再重複解析
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

#### i18n 國際化
- **154 翻譯鍵**: zh-TW / en 完全對稱，後端 33 key 雙語完整
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

### LLM

- ** LLM **: OpenAIAnthropic Claude
- **LLM **: OpenAI 
- ****: AI 
- ****: LLM 

### 

- ****: 
- ****: ETF 
- ****: 
- ****: 
- ****: 

> 

### i18n

- ****: i18n 
- ****: 
- ****: JSON 

### 

- **API **: Web API `.env` 
- ****: 

### 

- **TradingAgents**: 
- ****: 
- ****: PDF
- ****: 

### 

- ****: 
- ****: 
- ****: 
- **PR**: Pull Request

### 

- ****: GitHub
- ****: 
- ****: 
- ****: 

## v0.1.14 

### 

- **MongoDB**: MongoDB
- ****: 
- ****: 
- ****: 

### 

- ****: 6
- ****: Google
- ****: UI
- ****: 
- ****: 
- ****: 

---

## v0.1.13 

### OpenAI

- **OpenAI**: OpenAIAPI
- ****: OpenAI
- ****: OpenAI
- ****: 

### LLM

- ****: LLM
- ****: 
- ****: LLM

### Web

- ****: 
- **KeyError**: KeyError
- **UI**: 
- ****: 

## v0.1.12 

### 

- ****: AI
- ****: 
- ****: 
- ****: 

### 

- **LLM**: 
- ****: 

### 

- ****: 15+
- ****: 8
- ****: 
- ****: 

### 

- ****: docs
- ****: examples
- ****: 

## 

### 

- ****: 
- ****: /
- ****: 
- ****: 

## Web

### 

> **Web**: FastAPI + Alpine.js Web

> ****: 

### 

#### - 


- AAPLTSLANVDA
- 5
- LLMOpenAIAnthropic
- API

#### 


- 
- 
- 
- 

#### 


- //
- 
- 
- Markdown 匯出

### 

#### ****

- ** **: 
- ** 5**: 225
- ** **: 
- ** **: 

#### ****

- ** **: 
- ** **: 
- ** **: 
- ** **: 

#### ****

- ** **: //
- ** **: 
- ** **: 
- ** **: Markdown 匯出

#### **LLM**

- **AI**: OpenAIAnthropic
- ** 60+**: 
- ** **: URL
- ** **: 5

### Web

#### ****

1. **啟動系統**: `python start_app.py` 或 `docker-compose up -d`
2. **開啟瀏覽器**: `http://localhost:8501`
3. **瀏覽首頁**: 查看市場總覽、漲跌排行、AI 趨勢分析
4. **切換至分析頁籤**: 輸入股票代碼（AAPL、TSLA、NVDA 等）
5. **選擇模型**: 選擇 LLM 提供商與模型
6. **開始分析**: 點擊「開始分析」按鈕，透過 SSE 串流即時查看進度
7. **查看結果**: 瀏覽各智慧體分析報告與最終交易建議
8. **匯出報告**: 以 Markdown 格式匯出分析結果

#### ****

- ** **: `AAPL`, `TSLA`, `MSFT`, `NVDA`, `GOOGL`

#### **分析模式**

- **標準分析**: 多空辯論 + 風險評估（預設 2 輪辯論）
- **深度分析**: 可透過 .env 調整 `MAX_DEBATE_ROUNDS` 和 `MAX_RISK_DISCUSS_ROUNDS`

#### ****

- ** **: 
- ** **: 
- ** **: 
- ** **: Enter
- ** **: 

> ****: Web [ Web](docs/usage/web-interface-detailed-guide.md)

## 

### **v0.1.12**


| | | |
| ---------------------- | ----------- | ---------------------------------------- |
| ** ** | v0.1.12 | AI |
| ** ** | v0.1.12 | // |
| ** ** | v0.1.12 | |
| ** LLM** | v0.1.11 | 460+ |
| ** ** | v0.1.11 | URL |
| ** ** | v0.1.11 | |
| ** ** | v0.1.10 | |
| ** ** | v0.1.10 | |
| ** ** | v0.1.10 | |
| ** FastAPI ** | | |
| ** ** | | WebAPI |

### CLI **v0.1.9**


| | | |
| ----------------------- | ----------- | ------------------------------------ |
| ** ** | | |
| ** ** | | |
| ** ** | | |
| ** Rich** | | |

### LLM **v0.1.13**


| | | | |
| ----------------- | ---------------------------- | ----------------------- | -------- |
| **OpenAI** | GPT-4o, GPT-4o-mini | | |
| **Anthropic** | Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5 | | |

****: URL | ****: 

### 


| | | |
| ------------- | ---------------------- | ------------------------ |
| ** ** | FinnHub, Yahoo Finance | NYSE, NASDAQ |
| ** ** | Google News | |

### 

****: | | | 
****: | | 
****: | 

## 

### Docker ()

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
cp .env.example .env
# .env API

# 3. 
# 
docker-compose up -d --build

# 
docker-compose up -d

# 
# Windows
powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1

# Linux/Mac
chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh

# 4. 
# Web: http://localhost:8501
```

### 

```bash
# 1. pip ()
python -m pip install --upgrade pip

# 2. 
pip install -r requirements-lock.txt
pip install -e . --no-deps

# 
# pip install -e .

# Windows PyYAML 

# 3. 
python start_app.py

# 4. http://localhost:8501
```

### 

1. ****: OpenAI / Anthropic
2. ****: `AAPL` ()
3. ****: " "
4. ****: 
5. ****: " "
6. ****: Markdown

## 

- ** **: v0.1.12AI
- ** **: 
- ** **: 
- **LLM**: OpenAI Anthropic 
- ****: URL
- ** **: v0.1.10
- ** **: 
- ** **: + AI + 
- ** **: Docker
- ** **: 
- ** **: 

## 

**後端**: Python 3.10+ | LangChain 1.x | LangGraph | FastAPI | MongoDB | Redis
**AI 引擎**: OpenAI (GPT-4o, o4-mini) | Anthropic (Claude Opus 4.6, Sonnet 4.6)
**前端**: Alpine.js 3.15.8 | DOMPurify 3.3.1 | CSS Grid | SSE 即時串流 | SSR 預渲染
**資料來源**: FinnHub | Yahoo Finance | Google News
**部署**: Docker | Docker Compose | Kubernetes (Helm) | GitHub Actions CI/CD

## 

- ** **: [docs/](./docs/) - API
- ** **: [troubleshooting/](./docs/troubleshooting/) - 
- ** **: [CHANGELOG.md](./docs/releases/CHANGELOG.md) - 
- ** **: [QUICKSTART.md](./QUICKSTART.md) - 5

## 

****: | | | | LLM | | | | | | Docker | | | Web | 

**Docker**:

- **Web**: TradingAgents-CN
- **MongoDB**: 
- **Redis**: 
- **MongoDB Express**: 資料庫管理介面（需 `--profile management` 啟動）
- **Redis Commander**: 快取管理介面（需 `--profile management` 啟動）

#### 

****: 

### 

- Python 3.10+ ( 3.11)
- 4GB+ RAM ( 8GB+)
- 

### 

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

### API

#### API 

```bash
# 
cp .env.example .env

# .env API
FINNHUB_API_KEY=your_finnhub_api_key_here

# AIAPI
OPENAI_API_KEY=your_openai_api_key_here

# 
# 
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

#### 

****

```bash
# 
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_HOST=localhost # 
MONGODB_PORT=27017 # 
REDIS_HOST=localhost # 
REDIS_PORT=6379 # 
```

**Docker**

```bash
# Docker
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_HOST=mongodb # Docker
MONGODB_PORT=27017 # 
REDIS_HOST=redis # Docker
REDIS_PORT=6379 # 
```

> ****
>
> - MongoDBRedis
> - Dockerdocker-compose
> - docker-compose.yml

#### Anthropic Claude 

```bash
# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### MongoDB + Redis

#### 

 **MongoDB** **Redis** 

- ** **: API
- ** **: MongoDB → API → 
- ** **: Redis
- ** **: MongoDB

#### 

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



****

```bash
# MongoDB + Redis Web
docker-compose up -d mongodb redis mongo-express redis-commander

# 
docker-compose ps

# 
docker-compose down
```

****

```bash
# requirements.txt

# MongoDB ( 27017)
mongod --dbpath ./data/mongodb

# Redis ( 6379)
redis-server
```

> ****:
>
> - ** Docker**: 
> - ** **: 
> - ** **: Docker

#### 

****

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

****

```bash
# .env 資料庫設定
MONGODB_ENABLED=true
MONGODB_URI=mongodb://localhost:27017/trading_agents
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

#### 

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

#### 



```
 
1. Redis ()
2. MongoDB ()
3. Yahoo Finance / FinnHub API ()
4. ()
5. 
```

****

```bash
# .env 快取設定
MONGODB_ENABLED=true
REDIS_ENABLED=true
```

#### 

****

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

#### 

```bash
# 
python scripts/setup/init_database.py

# 
python scripts/validation/check_system_status.py

# 
python scripts/maintenance/cleanup_cache.py --days 7
```

#### 

****

1. ** Windows 10 ChromaDB**

 ****Windows 10 `Configuration error: An instance of Chroma already exists for ephemeral with different settings` Windows 11

 ****

 ```bash
 # 1
 # .env 
 MEMORY_ENABLED=false

 # 2
 powershell -ExecutionPolicy Bypass -File scripts\fix_chromadb_win10.ps1

 # 3
 # PowerShell -> ""
 ```

 **** [Windows 10](docs/troubleshooting/windows10-chromadb-fix.md)
2. **MongoDB**

 **Docker**

 ```bash
 # 
 docker-compose logs mongodb

 # 
 docker-compose restart mongodb
 ```

 ****

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

> ****: API

> ****: [](docs/architecture/database-architecture.md)

### 

#### 



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

### 

#### Docker

Docker

```bash
# Docker
# Web: http://localhost:8501
# MongoDB Express: http://localhost:8081 (需 --profile management)
# Redis Commander: http://localhost:8082 (需 --profile management)

# 
docker-compose ps

# 
docker-compose logs -f web
```

#### 



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

#### 

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# OpenAI
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-4o" # 
config["quick_think_llm"] = "gpt-4o-mini" # 

# 
ta = TradingAgentsGraph(debug=True, config=config)

# ()
state, decision = ta.propagate("AAPL", "2024-01-15")

# 
print(f": {decision['action']}")
print(f": {decision['confidence']:.1%}")
print(f": {decision['risk_score']:.1%}")
print(f": {decision['reasoning']}")
```

#### 

```bash
# OpenAI
python examples/simple_analysis_demo.py
```

#### 

****: 

```bash
# 
python -m cli.main data-config --show

# 
python -m cli.main data-config --set /path/to/your/data

# 
python -m cli.main data-config --reset
```

****:

```bash
# Windows
set TRADING_AGENTS_DATA_DIR=C:\MyTradingData

# Linux/macOS
export TRADING_AGENTS_DATA_DIR=/home/user/trading_data
```

****:

```python
from tradingagents.config_manager import ConfigManager

# 
config_manager = ConfigManager()
config_manager.set_data_directory("/path/to/data")

# 
data_dir = config_manager.get_data_directory()
print(f": {data_dir}")
```

****: > > > 

: [ ](docs/configuration/data-directory-configuration.md)

### 

```bash
# 
python -m cli.main
```

## **** - 


| **...** | **** | **** |
| --------------- | --------------------------------------------------------- | ---------------- |
| **** | [ ](docs/overview/quick-start.md) | 10 |
| **** | [ ](docs/architecture/system-architecture.md) | 15 |
| **** | [ ](docs/examples/basic-examples.md) | 20 |
| **** | [ ](docs/faq/faq.md) | 5 |
| **** | [ ](#-) | 2+ |

> ****: `docs/` **50,000+** 

## - 

> ** ** AI **50,000** **20+** **100+** 

### 


| | TradingAgents | **** |
| ------------ | ------------------ | -------------------------- |
| **** | | **** |
| **** | | **** |
| **** | | ** + ** |
| **** | | **** |
| **** | | **FAQ + ** |
| **** | | **100+ ** |

### - 

#### **** ()

1. [ ](docs/overview/project-overview.md) - ****
2. [ ](docs/overview/installation.md) - ****
3. [ ](docs/overview/quick-start.md) - **10**
4. [ ](docs/examples/basic-examples.md) - **8**

#### **** ()

1. [ ](docs/architecture/system-architecture.md) - ****
2. [ ](docs/architecture/agent-architecture.md) - ****
3. [ ](docs/architecture/data-flow-architecture.md) - ****
4. [ ](docs/architecture/graph-structure.md) - **LangGraph**

#### **** ()

1. [ ](docs/agents/analysts.md) - ****
2. [ ](docs/agents/researchers.md) - **/**
3. [ ](docs/agents/trader.md) - ****
4. [ ](docs/agents/risk-management.md) - ****
5. [ ](docs/agents/managers.md) - ****

#### **** ()

1. [ ](docs/data/data-sources.md) - **API**
2. [ ](docs/data/data-processing.md) - ****
3. [ ](docs/data/caching.md) - ****

#### **** ()

1. [ ](docs/configuration/config-guide.md) - ****
2. [ LLM](docs/configuration/llm-config.md) - ****

#### **** ()

1. [ ](docs/examples/basic-examples.md) - **8**
2. [ ](docs/examples/advanced-examples.md) - ****

#### **** ()

1. [ ](docs/faq/faq.md) - **FAQ**

### 

- ****: 20+ 
- ****: 50,000+ 
- ****: 100+ 
- ****: 10+ 
- ****: 

### 

- ** **: 
- ** **: 
- ** **: 
- ** **: 
- ** **: 

---

## 

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

### **** ()

#### ****

1. **[ ](docs/overview/project-overview.md)** - 

 > 5
 >
2. **[ ](docs/architecture/system-architecture.md)** - 

 > 
 >
3. **[ ](docs/examples/basic-examples.md)** - 

 > 8
 >

#### ****

1. **[ ](docs/architecture/agent-architecture.md)**

 > 
 >
2. **[ ](docs/architecture/data-flow-architecture.md)**

 > 
 >
3. **[ ](docs/agents/researchers.md)**

 > /
 >

#### ****

1. **[ Web](docs/usage/web-interface-guide.md)** - 

 > Web5
 >
2. **[ ](docs/usage/investment_analysis_guide.md)**

 > 
 >
3. **[ LLM](docs/configuration/llm-config.md)**

 > LLM
 >
4. **[ ](docs/data/caching.md)**

 > API
 >
5. **[ ](docs/faq/faq.md)**

 > FAQ
 >

### ****

<details>
<summary><strong> </strong> - </summary>

- [ ](docs/overview/project-overview.md) - 
- [ ](docs/overview/quick-start.md) - 
- [ ](docs/overview/installation.md) - 

</details>

<details>
<summary><strong> </strong> - </summary>

- [ ](docs/architecture/system-architecture.md) - 
- [ ](docs/architecture/agent-architecture.md) - 
- [ ](docs/architecture/data-flow-architecture.md) - 
- [ ](docs/architecture/graph-structure.md) - LangGraph

</details>

<details>
<summary><strong> </strong> - </summary>

- [ ](docs/agents/analysts.md) - 
- [ ](docs/agents/researchers.md) - /
- [ ](docs/agents/trader.md) - 
- [ ](docs/agents/risk-management.md) - 
- [ ](docs/agents/managers.md) - 

</details>

<details>
<summary><strong> </strong> - </summary>

- [ ](docs/data/data-sources.md) - API
- [ ](docs/data/data-processing.md) - 
- [ ](docs/data/caching.md) - 

</details>

<details>
<summary><strong> </strong> - </summary>

- [ ](docs/configuration/config-guide.md) - 
- [ LLM](docs/configuration/llm-config.md) - 

</details>

<details>
<summary><strong> </strong> - </summary>

- [ ](docs/examples/basic-examples.md) - 8
- [ ](docs/examples/advanced-examples.md) - 

</details>

<details>
<summary><strong> </strong> - </summary>

- [ ](docs/faq/faq.md) - FAQ

</details>

## 

### 

- ****: $0.01-0.05/ ( gpt-4o-mini)
- ****: $0.05-0.15/ ( gpt-4o)
- ****: $0.10-0.30/ ( gpt-4o + )

### 

```python
# 
cost_optimized_config = {
 "deep_think_llm": "gpt-4o-mini",
 "quick_think_llm": "gpt-4o-mini", 
 "max_debate_rounds": 1,
 "online_tools": False # 
}
```

## 



### 

- **Bug** - 
- **** - 
- **** - 
- **** - 
- **** - 

### 

1. Fork 
2. (`git checkout -b feature/AmazingFeature`)
3. (`git commit -m 'Add some AmazingFeature'`)
4. (`git push origin feature/AmazingFeature`)
5. Pull Request

### 

**[ ](CONTRIBUTORS.md)**

## 

 Apache 2.0 [LICENSE](LICENSE) 

### 

- 
- 
- 
- 
- 
- 

## 

### 

 [Tauric Research](https://github.com/TauricResearch) 

- ** **: AI
- ** **: 
- ** **: 
- ** **: AI
- ** **: 

### 

TradingAgents-CN

**[ ](CONTRIBUTORS.md)**



- **Docker** - 
- **** - 
- **Bug** - 
- **** - 
- **** - 
- **** - 
- ** **: Apache 2.0
- ** **: 

****[TradingAgents](https://github.com/TauricResearch/TradingAgents) Apache 2.0

### 



- ** **: TradingAgents
- ** **: AI
- ** **: 
- ** **: AI

### 



### 



- ****: 
- ****: 
- ****: 
- ****: 

## 

- **v0.4.5** (2026-02-27): 節點級別即時進度回報、多空/風險並行辯論、分析師直接工具呼叫、工具結果快取去重、快取 TTL 優化、圖結構精簡、SSE try/finally 清理、compositor-only 動畫、SSR 預渲染 CLS 0.00
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

 ****: [CHANGELOG.md](./docs/releases/CHANGELOG.md)

## 

- **GitHub Issues**: [](https://github.com/aiinpocket/TradingAgents-CN/issues)
- **Email**: hsliup@163.com
- ****: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- ****: [](docs/)

## 

****: 

- 
- AI
- 
- 

---

<div align="center">

** Star**

[ Star this repo](https://github.com/aiinpocket/TradingAgents-CN) | [ Fork this repo](https://github.com/aiinpocket/TradingAgents-CN/fork) | [ Read the docs](./docs/)

</div>
