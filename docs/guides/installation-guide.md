---
version: cn-0.1.14-preview
last_updated: 2025-01-13
code_compatibility: cn-0.1.14-preview
status: updated
---

# TradingAgents-CN 

> ****: `cn-0.1.14-preview` 
> ****: 2025-01-13 
> ****: - 

## 

1. [](#)
2. [](#)
3. [](#)
4. [](#)
5. [](#)
6. [](#)
7. [](#)
8. [](#)
9. [](#)

## 

### 
- **Windows 10/11** ()
- **macOS 10.15+**
- **Linux (Ubuntu 20.04+, CentOS 8+)**

### 
- **CPU**: 4 (8)
- ****: 8GB (16GB)
- ****: 10GB
- ****: 

### 
- **Python**: 3.10+ ()
- **Git**: 
- **Redis**: 6.2+ ()
- **MongoDB**: 4.4+ ()

## 

### 1. Python 3.10+

#### Windows
```bash
# Python 3.10+
# https://www.python.org/downloads/
# "Add Python to PATH"
```

#### macOS
```bash
# Homebrew
brew install python@3.10

# pyenv
pyenv install 3.10.12
pyenv global 3.10.12
```

#### Linux (Ubuntu)
```bash
# 
sudo apt update

# Python 3.10
sudo apt install python3.10 python3.10-venv python3.10-pip

# 
python3.10 --version
```

### 2. Git
```bash
# Windows: Git for Windows
# https://git-scm.com/download/win

# macOS
brew install git

# Linux
sudo apt install git # Ubuntu
sudo yum install git # CentOS
```

### 3. uv ()
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 
uv --version
```

## 

### 1. 
```bash
# 
git clone https://github.com/your-repo/TradingAgents-CN.git
cd TradingAgents-CN

# 
cat VERSION
```

### 2. 
```bash
# uv ()
uv venv

# 
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 
which python # python
```

### 3. 

#### 1: uv ()
```bash
# 
uv pip install -e .

# 
uv pip install yfinance langgraph 

# 
python -c "import tradingagents; print('!')"
```

#### 2: pip
```bash
# 
pip install -e .

# 
pip install yfinance langgraph 

# 
pip install -r requirements.txt

# 
python -c "import tradingagents; print('!')"
```

#### 3: ()
```bash
# 1. 
pip install streamlit pandas numpy requests plotly

# 2. LLM
pip install openai langchain langgraph 

# 3. 
pip install yfinance 

# 4. ()
pip install redis pymongo

# 5. 
pip install -e .
```

## 

### 1. 
```bash
# 
cp .env.example .env

# 
# Windows: notepad .env
# macOS/Linux: nano .env
```

### 2. API

 `.env` 

```bash
# ===========================================
# TradingAgents-CN 
# ===========================================

# 
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# ===========================================
# LLM API ()
# ===========================================

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ===========================================
# API
# ===========================================

# FinnHub ()
FINNHUB_API_KEY=your_finnhub_api_key_here

# Alpha Vantage
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# ===========================================
# ()
# ===========================================

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# MongoDB
MONGODB_URI=mongodb://localhost:27017/tradingagents
MONGODB_DATABASE=tradingagents

# ===========================================
# 
# ===========================================

# Web
WEB_HOST=localhost
WEB_PORT=8501
WEB_DEBUG=true

# 
DATA_CACHE_DIR=./data/cache

# 
LOG_DIR=./logs
LOG_FILE=tradingagents.log
```

### 3. API

#### OpenAI API
1. [OpenAI Platform](https://platform.openai.com/)
2. /
3. API Keys 
4. API

#### Anthropic Claude API
1. [Anthropic Console](https://console.anthropic.com/)
2. 
3. API
4. API Key

#### FinnHub API
1. [FinnHub](https://finnhub.io/)
2. 
3. API Key

#### Alpha Vantage API
1. [Alpha Vantage](https://www.alphavantage.co/)
2. 
3. API Key

## 

### Redis ()

#### Windows
```bash
# Redis for Windows
# https://github.com/microsoftarchive/redis/releases

# Docker
docker run -d --name redis -p 6379:6379 redis:latest
```

#### macOS
```bash
# Homebrew
brew install redis

# Redis
brew services start redis

# 
redis-cli ping
```

#### Linux
```bash
# Ubuntu
sudo apt install redis-server

# CentOS
sudo yum install redis

# 
sudo systemctl start redis
sudo systemctl enable redis
```

### MongoDB ()

#### Docker ()
```bash
# MongoDB
docker run -d --name mongodb -p 27017:27017 mongo:latest

# 
docker exec -it mongodb mongosh
```

#### 
```bash
# MongoDB
# https://www.mongodb.com/try/download/community

## 

### 1. Web

#### 1: ()
```bash
# 
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Web
python start_web.py
```

#### 2: Streamlit
```bash
# web
cd web

# Streamlit
streamlit run app.py --server.port 8501
```

#### 3: (Windows)
```bash
# 
start_web.bat
```

### 2. 
: http://localhost:8501

### 3. 

1. **LLM**: LLM
2. ****: 
3. ****: 
4. ****: 

## 

### 1. 
```bash
# Python
python -c "import tradingagents; print(' ')"

# 
python -c "import streamlit, pandas, yfinance; print(' ')"

# 
python -c "from tradingagents.config import get_config; print(' ')"
```

### 2. API
```bash
# 
cd examples

# LLM
python test_llm_connection.py

# 
python test_data_sources.py
```

### 3. Web
1. http://localhost:8501
2. 
3. LLM
4. (: AAPL, MSFT)

## 

### 1. 
```bash
# : ModuleNotFoundError: No module named 'tradingagents'
# :
pip install -e .

# 
pip uninstall tradingagents
pip install -e .
```

### 2. 
```bash
# : 
# :
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 
which python
```

### 3. 
```bash
# : Port 8501 is already in use
# :
streamlit run app.py --server.port 8502

# 
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8501 | xargs kill -9
```

### 4. API
```bash
# : API
# :
1. .envAPI
2. API
3. 
4. : logs/tradingagents.log
```

### 5. 
```bash
# : 
# :
1. 
2. API
3. 
4. : data/cache
```

## 

### 1. 

#### Redis
```bash
# .envRedis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=true
```

#### 
```python
# config/settings.json
{
 "max_workers": 4,
 "request_timeout": 30,
 "cache_ttl": 3600
}
```

### 2. 

#### 
```bash
# .env
LOG_LEVEL=DEBUG # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/tradingagents.log
```

#### 
```python
# config/logging.toml
[loggers.tradingagents]
level = "INFO"
handlers = ["console", "file"]
```

### 3. 

#### 
```python
# config/settings.json
{
 "data_sources": {
 "china_stocks": ["", "", "tdx"],
 "us_stocks": ["yfinance", "finnhub", "alpha_vantage"],
 "hk_stocks": ["", "yfinance"]
 }
}
```

### 4. 

#### 
```python
# config/models.json
{
 "openai": {
 "temperature": 0.1,
 "max_tokens": 4000,
 "timeout": 60
 }
}
```

## Docker ()

### 1. Docker
```bash
# 
docker build -t tradingagents-cn .

# 
docker run -d \
 --name tradingagents \
 -p 8501:8501 \
 -v $(pwd)/.env:/app/.env \
 tradingagents-cn
```

### 2. Docker Compose
```bash
# 
docker-compose up -d

# 
docker-compose ps

# 
docker-compose logs -f
```

## 



1. **[](../QUICK_START.md)** - 
2. **[](./config-management-guide.md)** - 
3. **[](./a-share-analysis-guide.md)** - 
4. **[Docker](./docker-deployment-guide.md)** - 
5. **[](../troubleshooting/)** - 

## 



- **GitHub Issues**: [](https://github.com/your-repo/TradingAgents-CN/issues)
- ****: [](../README.md)
- ****: [](https://your-community-link)

---

**** 
```
