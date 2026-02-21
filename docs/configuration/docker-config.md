# Docker

## 

TradingAgents-CNDocker

## Docker

### 

| | | Docker |
|-------|---------|-----------|
| **** | localhost | |
| **** | | |
| **** | | |
| **** | | |

### 

- ****: 
- ****: DNS
- ****: 
- ****: 

## 

### 

```bash
# === Docker ===
# 
APP_NAME=TradingAgents-CN
APP_VERSION=0.1.7
APP_ENV=production

# 
WEB_PORT=8501
MONGODB_PORT=27017
REDIS_PORT=6379
MONGO_EXPRESS_PORT=8081
REDIS_COMMANDER_PORT=8082
```

### 

```bash
# === ===
# MongoDB ()
MONGODB_URL=mongodb://mongodb:27017/tradingagents
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_DATABASE=tradingagents

# MongoDB ()
MONGODB_USERNAME=admin
MONGODB_PASSWORD=${MONGO_PASSWORD}
MONGODB_AUTH_SOURCE=admin

# Redis ()
REDIS_URL=redis://redis:6379
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Redis ()
REDIS_PASSWORD=${REDIS_PASSWORD}
```

### LLM

```bash
# === LLM ===
# OpenAI
OPENAI_API_KEY=${OPENAI_API_KEY}

# Anthropic Claude
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# 
LLM_SMART_ROUTING=true
LLM_PRIORITY_ORDER=openai,anthropic
```

## Docker Compose

### 

```yaml
# docker-compose.yml
version: '3.8'

services:
 web:
 build: .
 container_name: TradingAgents-web
 ports:
 - "${WEB_PORT:-8501}:8501"
 environment:
 # 
 - MONGODB_URL=mongodb://mongodb:27017/tradingagents
 - REDIS_URL=redis://redis:6379

 # LLM
 - OPENAI_API_KEY=${OPENAI_API_KEY}
 - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

 # 
 - APP_ENV=docker
 - EXPORT_ENABLED=true
 - EXPORT_DEFAULT_FORMAT=word,pdf
 volumes:
 # 
 - .env:/app/.env

 # ()
 - ./web:/app/web
 - ./tradingagents:/app/tradingagents

 # 
 - ./exports:/app/exports
 depends_on:
 - mongodb
 - redis
 networks:
 - tradingagents
 restart: unless-stopped
```

### 

```yaml
 mongodb:
 image: mongo:4.4
 container_name: TradingAgents-mongodb
 ports:
 - "${MONGODB_PORT:-27017}:27017"
 environment:
 - MONGO_INITDB_DATABASE=tradingagents
 # 
 - MONGO_INITDB_ROOT_USERNAME=${MONGO_USERNAME:-admin}
 - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
 volumes:
 - mongodb_data:/data/db
 - ./scripts/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
 networks:
 - tradingagents
 restart: unless-stopped

 redis:
 image: redis:6-alpine
 container_name: TradingAgents-redis
 ports:
 - "${REDIS_PORT:-6379}:6379"
 command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-}
 volumes:
 - redis_data:/data
 networks:
 - tradingagents
 restart: unless-stopped
```

### 

```yaml
 mongo-express:
 image: mongo-express
 container_name: TradingAgents-mongo-express
 ports:
 - "${MONGO_EXPRESS_PORT:-8081}:8081"
 environment:
 - ME_CONFIG_MONGODB_SERVER=mongodb
 - ME_CONFIG_MONGODB_PORT=27017
 - ME_CONFIG_MONGODB_ADMINUSERNAME=${MONGO_USERNAME:-admin}
 - ME_CONFIG_MONGODB_ADMINPASSWORD=${MONGO_PASSWORD}
 - ME_CONFIG_BASICAUTH_USERNAME=${ADMIN_USERNAME:-admin}
 - ME_CONFIG_BASICAUTH_PASSWORD=${ADMIN_PASSWORD}
 depends_on:
 - mongodb
 networks:
 - tradingagents
 restart: unless-stopped

 redis-commander:
 image: rediscommander/redis-commander
 container_name: TradingAgents-redis-commander
 ports:
 - "${REDIS_COMMANDER_PORT:-8082}:8081"
 environment:
 - REDIS_HOSTS=local:redis:6379:0:${REDIS_PASSWORD:-}
 depends_on:
 - redis
 networks:
 - tradingagents
 restart: unless-stopped
```

## 

### 

```yaml
networks:
 tradingagents:
 driver: bridge
 name: tradingagents_network
 ipam:
 config:
 - subnet: 172.20.0.0/16
```

### 

```bash
# 
# MongoDB: mongodb:27017
# Redis: redis:6379
# Web: web:8501

# 
# Web: localhost:8501
# MongoDB: localhost:27017
# Redis: localhost:6379
# Mongo Express: localhost:8081
# Redis Commander: localhost:8082
```

## 

### 

```yaml
volumes:
 mongodb_data:
 driver: local
 driver_opts:
 type: none
 o: bind
 device: ${DATA_PATH:-./data}/mongodb

 redis_data:
 driver: local
 driver_opts:
 type: none
 o: bind
 device: ${DATA_PATH:-./data}/redis
```

### 

```bash
# === ===
# 
BACKUP_PATH=./backups
BACKUP_RETENTION_DAYS=30

# 
ENABLE_AUTO_BACKUP=true
BACKUP_SCHEDULE="0 2 * * *" # 2

# 
BACKUP_COMPRESS=true
BACKUP_ENCRYPTION=false
```

## 

### 

```bash
# === ===
# 
ADMIN_USERNAME=admin
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# 
MONGO_USERNAME=admin
MONGO_PASSWORD=${MONGO_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}

# API
ENCRYPT_API_KEYS=true
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# 
ENABLE_FIREWALL=true
ALLOWED_IPS=127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

### SSL/TLS

```yaml
# HTTPS ()
 nginx:
 image: nginx:alpine
 ports:
 - "443:443"
 - "80:80"
 volumes:
 - ./nginx.conf:/etc/nginx/nginx.conf
 - ./ssl:/etc/nginx/ssl
 depends_on:
 - web
```

## 

### 

```yaml
healthcheck:
 test: ["CMD", "curl", "-f", "http://localhost:8501/health"]
 interval: 30s
 timeout: 10s
 retries: 3
 start_period: 40s
```

### 

```yaml
logging:
 driver: "json-file"
 options:
 max-size: "10m"
 max-file: "3"
```

## 

### 

```bash
# 
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_HOT_RELOAD=true
```

### 

```bash
# 
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_HOT_RELOAD=false

# 
WORKERS=4
MAX_MEMORY=4G
MAX_CPU=2.0
```

## 

### 

1. ****
 ```bash
 # 
 docker exec TradingAgents-web ping mongodb
 docker exec TradingAgents-web ping redis
 ```

2. ****
 ```bash
 # 
 docker volume ls
 docker volume inspect mongodb_data
 ```

3. ****
 ```bash
 # 
 docker exec TradingAgents-web env | grep MONGODB
 ```

---

*: 2025-07-13*
*: cn-0.1.7*
*: [@breeze303](https://github.com/breeze303)*
