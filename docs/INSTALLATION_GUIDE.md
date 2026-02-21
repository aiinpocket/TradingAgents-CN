# TradingAgents-CN 

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker--blue.svg)](https://www.docker.com/)

> ****: Docker
>
> ****: Docker 15-30 | 30-60

## 

- [](#)
- [](#)
- [Docker](#docker)
- [](#)
- [](#)
- [API](#api)
- [](#)
- [](#)
- [](#)

## 

### 
- ****: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- ****: 4GB RAM 8GB+
- ****: 5GB 
- ****: 

### 
- ****: Windows 11, macOS 12+, Ubuntu 20.04+
- ****: 16GB RAM
- ****: 20GB SSD
- **CPU**: 4

### 

#### Docker
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.0+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+

#### 
- [Python](https://www.python.org/downloads/) 3.10+
- [Git](https://git-scm.com/downloads) 2.30+
- [Node.js](https://nodejs.org/) 16+ ()

## 

### Docker

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
cp .env.example .env

# 3. API
# Windows: notepad .env
# macOS/Linux: nano .env

# 4. 
docker-compose up -d

# 5. 
# : http://localhost:8501
```

### 

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
python -m venv env

# 3. 
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate

# 4. pip ()
python -m pip install --upgrade pip

# 5. 
pip install -e .

# 6. 
cp .env.example .env

# 7. API
# Windows: notepad .env
# macOS/Linux: nano .env

# 8. 
python start_web.py
```

## Docker

Docker

### 1Docker

#### Windows
1. [Docker Desktop for Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
2. 
3. 
4. Docker Desktop

#### macOS
1. [Docker Desktop for Mac](https://desktop.docker.com/mac/main/amd64/Docker.dmg)
2. Applications
3. Docker Desktop

#### Linux (Ubuntu/Debian)
```bash
# 
sudo apt update

# 
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# DockerGPG
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker
sudo systemctl start docker
sudo systemctl enable docker

# docker
sudo usermod -aG docker $USER
```

### 2Docker

```bash
# Docker
docker --version
docker-compose --version

# Docker
docker run hello-world
```

### 3

```bash
# 
git clone https://github.com/aiinpocket/TradingAgents-CN.git

# 
cd TradingAgents-CN

# 
ls -la
```

### 4

```bash
# 
cp .env.example .env

# 
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env
```

****: AIAPI

### 5Docker

```bash
# 
docker-compose up -d

# 
docker-compose ps

# 
docker-compose logs -f web
```

### 6



- ****: http://localhost:8501
- **Redis**: http://localhost:8081 (/: admin/tradingagents123)
- **MongoDB**: http://localhost:8082 ()

## 



### 1Python

#### Windows
1. [Python](https://www.python.org/downloads/windows/)
2. Python 3.10
3. **Add Python to PATH**
4. 
 ```cmd
 python --version
 pip --version
 ```

#### macOS
```bash
# Homebrew
brew install python@3.10

# 
# https://www.python.org/downloads/macos/
```

#### Linux (Ubuntu/Debian)
```bash
# 
sudo apt update

# Python 3.10+
sudo apt install python3.10 python3.10-venv python3.10-pip

# 
sudo ln -sf /usr/bin/python3.10 /usr/bin/python
sudo ln -sf /usr/bin/pip3 /usr/bin/pip
```

### 2

```bash
# 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN
```

### 3

```bash
# 
python -m venv env

# 
# Windows:
env\Scripts\activate

# macOS/Linux:
source env/bin/activate

# 
which python # python
```

### 4

```bash
# pip
python -m pip install --upgrade pip

# 
pip install -r requirements.txt

# 
python -c "import streamlit; print('Streamlit')"
python -c "import openai; print('OpenAI')"
python -c "import finnhub; print('FinnHub')"
```

### 5

```bash
# 
cp .env.example .env

# 
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env
```

### 6

#### MongoDB ()
```bash
# Windows: MongoDB Community Server
# https://www.mongodb.com/try/download/community

# macOS:
brew tap mongodb/brew
brew install mongodb-community

# Ubuntu/Debian:
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install mongodb-org
```

#### Redis ()
```bash
# Windows: Redis for Windows
# https://github.com/microsoftarchive/redis/releases

# macOS:
brew install redis

# Ubuntu/Debian:
sudo apt install redis-server
```

### 7

```bash
# 
# Windows: env\Scripts\activate
# macOS/Linux: source env/bin/activate

# Streamlit
python -m streamlit run web/app.py

# 
# Windows: start_web.bat
# macOS/Linux: ./start_web.sh
```

## 

### .env

`.env`

```bash
# =============================================================================
# AI ()
# =============================================================================

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1 # API

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# =============================================================================
# 
# =============================================================================

# FinnHub ()
FINNHUB_API_KEY=your_finnhub_api_key_here

# =============================================================================
# ()
# =============================================================================

# MongoDB
MONGODB_ENABLED=false # trueMongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_mongodb_password
MONGODB_DATABASE=tradingagents

# Redis
REDIS_ENABLED=false # trueRedis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# =============================================================================
# 
# =============================================================================

# 
LOG_LEVEL=INFO # DEBUG, INFO, WARNING, ERROR

# 
CACHE_ENABLED=true
CACHE_TTL=3600 # 

# 
REQUEST_TIMEOUT=30 # 
MAX_RETRIES=3 # 
```

### 

1. ****: AIAPI
2. ****: FinnHub API Key
3. ****: 
4. ****: 

## API

### AIAPI

#### 1. OpenAI ()
1. [OpenAI](https://platform.openai.com/)
2. 
3. API Keys
4. API
5. `.env``OPENAI_API_KEY`

****: 

#### 2. Anthropic Claude ()
1. [Anthropic Console](https://console.anthropic.com/)
2. 
3. API
4. `.env``ANTHROPIC_API_KEY`

****: 

### API

#### FinnHub ()
1. [FinnHub](https://finnhub.io/)
2. 
3. API
4. `.env``FINNHUB_API_KEY`

****: 

### API

1. **Git**: `.env``.gitignore`
2. ****: API
3. ****: 
4. ****: API

## 

### 

```bash
# 1. Python
python --version # 3.10+

# 2. 
python -c "import streamlit; print(' Streamlit')"
python -c "import openai; print('OpenAI')"
python -c "import finnhub; print('FinnHub')"

# 3. 
python -c "import os; print('API' if os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY') else 'API')"
```

### Web

1. http://localhost:8501
2. 
3. AAPL
4. 
5. 
6. 

### Docker

```bash
# 
docker-compose ps

# 
docker-compose logs web

# 
docker-compose logs mongodb
docker-compose logs redis
```

### 

#### 
```bash
# Web
: AAPL
: 
: 3
: + 
```

## 

### Q1: ModuleNotFoundError
**A**: 
```bash
# 
pip install -r requirements.txt --upgrade
```

### Q2: API
**A**: 
```bash
# 
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# 
```

### Q3: Docker
**A**: Docker
```bash
# Docker
docker info

# 
netstat -an | grep 8501

# 
docker-compose build --no-cache
```

### Q4: 
**A**: API
- 
- API
- 

### Q5: 
**A**: 
- FinnHub API Key
- 
- 

### Q6: 
**A**: 
```bash
# Windows: 
chcp 65001

# Linux/macOS: locale
locale
```

### Q7: 
**A**: 
- 
- 
- 

### Q8: 
**A**: 
```bash
# pandoc (PDF)
# Windows: 
# macOS: brew install pandoc
# Linux: sudo apt install pandoc
```

## 

### 

#### Docker
```bash
# 
docker-compose logs -f web

# 
docker-compose logs mongodb
docker-compose logs redis

# 
docker-compose logs
```

#### 
```bash
# 
tail -f logs/tradingagents.log

# 
python -m streamlit run web/app.py --logger.level=debug
```

### 

#### 
```bash
# HTTP
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# .env
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

#### DNS
```bash
# DNS
# Windows: DNS8.8.8.8
# Linux: /etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
```

### 

#### 
```bash
# .env
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
```

#### 
```bash
# Redis
REDIS_ENABLED=true
CACHE_TTL=7200 # 
```

### 

#### MongoDB
```bash
# MongoDB
# Windows: services.msc MongoDB
# Linux: sudo systemctl status mongod
# macOS: brew services list | grep mongodb

# MongoDB
docker-compose down
docker volume rm tradingagents_mongodb_data
docker-compose up -d mongodb
```

#### Redis
```bash
# Redis
redis-cli ping

# Redis
docker-compose down
docker volume rm tradingagents_redis_data
docker-compose up -d redis
```

### 

#### Linux/macOS
```bash
# 
chmod +x start_web.sh

# 
sudo chown -R $USER:$USER .
```

#### Windows
- 
- 
- PythonPATH

### 

#### Docker
```bash
# 
docker-compose down

# 
docker volume prune
docker system prune -a

# 
docker-compose build --no-cache
docker-compose up -d
```

#### 
```bash
# 
rm -rf env

# 
python -m venv env
source env/bin/activate # Linux/macOS
# env\Scripts\activate # Windows

# 
pip install -r requirements.txt
```

## 

### 
- ****: https://github.com/aiinpocket/TradingAgents-CN
- ****: https://www.tradingagents.cn/
- ****: https://github.com/aiinpocket/TradingAgents-CN/issues

### 
- **GitHub Issues**: 
- **GitHub Discussions**: 
- **Email **: 

### 
Pull RequestIssue

---

 **** TradingAgents-CNAI
