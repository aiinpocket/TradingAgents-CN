# TradingAgents 

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.4.1-green.svg)](./VERSION)
[![Documentation](https://img.shields.io/badge/docs--green.svg)](./docs/)
[![Original](https://img.shields.io/badge/-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

>
> ****: OpenAI | Anthropic Claude | | LLM | | Docker | | | 

****

## 

 [Tauric Research](https://github.com/TauricResearch) [TradingAgents](https://github.com/TauricResearch/TradingAgents)

** **: AI

## v1.0.0-preview - 

> ****: v1.0.0-preview FastAPI + Vue 3 

### 

#### ****
- ****: FastAPI RESTful API
- ****: Vue 3 + Element Plus
- ****: MongoDB + Redis 10 
- ****: Docker amd64 + arm64

#### ****
- ****: 
- ****: 
- ****: MongoDB/Redis/
- ****: SSE 

#### ****
- ****: LLM 
- ****: 
- ****: Yahoo FinanceFinnHub
- ****: Markdown/Word/PDF 

#### **Docker **
- ****: x86_64 ARM64 Apple SiliconAWS Graviton
- **GitHub Actions**: Docker 
- ****: Docker Compose 5 

### 

| | v0.1.x | v1.0.0-preview |
|------|--------|----------------|
| **** | FastAPI + Uvicorn | FastAPI + Uvicorn |
| **** | Alpine.js | Vue 3 + Vite + Element Plus |
| **** | MongoDB | MongoDB + Redis |
| **API ** | | RESTful API + WebSocket |
| **** | /Docker | Docker + GitHub Actions |

### 

v1.0.0-preview 

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
- Markdown/Word/PDF

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
- ** **: Markdown/Word/PDF

#### **LLM**

- **AI**: OpenAIAnthropic
- ** 60+**: 
- ** **: URL
- ** **: 5

### Web

#### ****

1. ****: `python start_web.py` `docker-compose up -d`
2. ****: `http://localhost:8501`
3. ****: LLM
4. ****: AAPLTSLANVDA
5. ****: 1-5
6. ****: 
7. ****: 
8. ****: 

#### ****

- ** **: `AAPL`, `TSLA`, `MSFT`, `NVDA`, `GOOGL`

#### ****

- **1 (2-4)**: 
- **2 (4-6)**: +
- **3 (6-10)**: ****
- **4 (10-15)**: 
- **5 (15-25)**: 

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
| **Anthropic** | Claude Opus 4, Claude Sonnet 4 | | |

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
python start_web.py

# 4. http://localhost:8501
```

### 

1. ****: OpenAI / Anthropic
2. ****: `AAPL` ()
3. ****: " "
4. ****: 
5. ****: " "
6. ****: Word/PDF/Markdown

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

****: Python 3.10+ | LangChain | FastAPI | MongoDB | Redis
**AI**: OpenAI | Anthropic
****: FinnHub | Yahoo Finance | Google News
****: Docker | Docker Compose | 

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
- **MongoDB Express**: 
- **Redis Commander**: 

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

```python
# config/database_config.py
DATABASE_CONFIG = {
 'mongodb': {
 'host': 'localhost',
 'port': 27017,
 'database': 'trading_agents',
 'username': 'admin',
 'password': 'your_password'
 },
 'redis': {
 'host': 'localhost',
 'port': 6379,
 'password': 'your_redis_password',
 'db': 0
 }
}
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

```python
# .env 
ENABLE_MONGODB=true
ENABLE_REDIS=true
ENABLE_FALLBACK=true

# 
REDIS_CACHE_TTL=300
MONGODB_CACHE_TTL=3600
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



****

- ** Markdown (.md)** - 
- ** Word (.docx)** - Microsoft Word
- ** PDF (.pdf)** - 

****

- **** - //
- **** - 
- **** - 
- **** - 

****

1. " "
2. MarkdownWordPDF
3. 

****

```bash
# Python
pip install markdown pypandoc

# PDF
# Windows: choco install pandoc wkhtmltopdf
# macOS: brew install pandoc wkhtmltopdf
# Linux: sudo apt-get install pandoc wkhtmltopdf
```

> ****: [](docs/EXPORT_GUIDE.md)

### 

#### Docker

Docker

```bash
# Docker
# Web: http://localhost:8501
# : http://localhost:8081
# : http://localhost:8082

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

- ****: AAPL, TSLA, NVDA 
- ****: FinnHub Yahoo Finance 
- ****: 
- ****: Markdown/Word/PDF
- **5**: (2-4)(15-25)
- ****: 
- ****: 
- ****: 
- ****: 

****:

- **1 - ** (2-4): 
- **2 - ** (4-6): 
- **3 - ** (6-10): 
- **4 - ** (10-15): 
- **5 - ** (15-25): 

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

# 
python examples/custom_analysis_demo.py
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
