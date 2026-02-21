# Docker

## 

TradingAgents-CN v0.1.7 DockerDockerTradingAgents-CN

## Docker

### Docker

- ****: `docker-compose up -d` 
- ****: 
- ****: 
- ****: Web
- ****: 

### 

| | | Docker |
|------|---------|-----------|
| **** | 30-60 | 5-10 |
| **** | | |
| **** | | |
| **** | | |
| **** | | |

## 

### 

| | | | |
|------|---------|----------|----------|
| **Docker** | 20.0+ | | [](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.0+ | | Docker |
| **** | 4GB | 8GB+ | |
| **** | 10GB | 20GB+ | |

### Docker

#### Windows
```bash
# 1. Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. Docker Desktop

# 3. 
docker --version
docker-compose --version
```

#### Linux (Ubuntu/Debian)
```bash
# 1. 
sudo apt update

# 2. Docker
sudo apt install docker.io docker-compose

# 3. Docker
sudo systemctl start docker
sudo systemctl enable docker

# 4. docker
sudo usermod -aG docker $USER

# 5. 
docker --version
docker-compose --version
```

#### macOS
```bash
# 1. Homebrew
brew install --cask docker

# 2. Docker Desktop

# 3. 
docker --version
docker-compose --version
```

## 

### 1: 

```bash
# 
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 
cat VERSION
```

### Docker

****: TradingAgents-CNDocker

#### 

1. ****: 
2. ****: 
3. ****: 
4. ****: 

#### 

```bash
# Docker
1. (python:3.10-slim) - 200MB
2. (pandoc, wkhtmltopdf, ) - 300MB
3. Python (requirements.txt) - 500MB
4. - 50MB
5. 

# 1GB5-10
```

### 2: 

```bash
# 
cp .env.example .env

# 
# Windows: notepad .env
# Linux/macOS: nano .env
```

#### 

```bash
# === LLM () ===
# OpenAI ( - )
OPENAI_API_KEY=your_openai_api_key
OPENAI_ENABLED=true

# Anthropic Claude ( - )
ANTHROPIC_API_KEY=your_anthropic_api_key
```

#### 

```bash
# === ===
FINNHUB_API_KEY=your_finnhub_key

# === ===
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf

# === Docker ===
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379
```

### 3: 

```bash
# 
docker-compose up -d --build

# Docker
# - (python:3.10-slim)
# - (pandoc, wkhtmltopdf)
# - Python
# - 
# 5-10

# 
# docker-compose up -d

# 
docker-compose ps

# 
docker-compose logs -f
```

### 4: 

```bash
# 
docker-compose ps

# :
# - TradingAgents-web (Web)
# - TradingAgents-mongodb ()
# - TradingAgents-redis ()
# - TradingAgents-mongo-express ()
# - TradingAgents-redis-commander ()
```

### 5: 

| | | |
|------|------|------|
| **** | http://localhost:8501 | |
| **** | http://localhost:8081 | MongoDB |
| **** | http://localhost:8082 | Redis |

## 

### 

1. ****: http://localhost:8501
2. **LLM**: GPT-4 Claude
3. ****:
 - : AAPL, TSLA, MSFT, GOOGL
4. ****: //
5. ****: ""
6. ****: Word/PDF/Markdown

### 

1. **MongoDB**: http://localhost:8081
2. ****: tradingagents
3. ****: 

### 

1. **Redis**: http://localhost:8082
2. ****: 
3. ****: 

## 

### 

```bash
# 
docker-compose up -d

# 
docker-compose down

# 
docker-compose restart

# 
docker-compose ps

# 
docker-compose logs -f web
docker-compose logs -f mongodb
docker-compose logs -f redis
```

### 

```bash
# 
docker exec TradingAgents-mongodb mongodump --out /backup
docker exec TradingAgents-redis redis-cli BGSAVE

# 
docker exec TradingAgents-redis redis-cli FLUSHALL

# 
docker exec TradingAgents-mongodb mongo --eval "db.stats()"
```

### 

```bash
# 1. 
docker-compose down

# 2. 
git pull origin main

# 3. 
docker-compose build

# 4. 
docker-compose up -d
```

## 

### 

#### 1. 

****: 

****:
```bash
# 
netstat -tulpn | grep :8501

# 
# docker-compose.yml
ports:
 - "8502:8501" # 
```

#### 2. 

****: 

****:
```bash
# 
docker stats

# Docker
# Docker Desktop -> Settings -> Resources -> Memory
# 4GB
```

#### 3. 

****: Web

****:
```bash
# 
docker logs TradingAgents-mongodb

# 
docker exec TradingAgents-web ping mongodb

# 
docker-compose restart mongodb
```

#### 4. API

****: LLM

****:
```bash
# 
docker exec TradingAgents-web env | grep API_KEY

# .env
# 
docker-compose restart web
```

### 

```bash
# 1. 
docker image prune

# 2. 
docker container prune

# 3. 
docker volume prune

# 4. 
docker stats
```

## 

### 

```bash
# 
docker-compose ps

# 
docker logs TradingAgents-web --tail 50

# 
docker stats --no-stream
```

### 

```bash
# 
# 1. 
docker exec TradingAgents-mongodb mongodump --out /backup/$(date +%Y%m%d)

# 2. 
docker-compose logs --tail 0 -f > /dev/null

# 3. 
docker-compose pull
docker-compose up -d
```

## 

### 

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
 web:
 deploy:
 resources:
 limits:
 cpus: '2.0'
 memory: 4G
 reservations:
 memory: 2G
 restart: unless-stopped
```

### 

```bash
# 
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=secure_password
REDIS_PASSWORD=secure_redis_password
```

---

## 

Docker

- [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
- [GitHub Discussions](https://github.com/hsliuping/TradingAgents-CN/discussions)
- [Docker](https://docs.docker.com/)

---

*: 2025-07-13* 
*: cn-0.1.7* 
*: [@breeze303](https://github.com/breeze303)*
