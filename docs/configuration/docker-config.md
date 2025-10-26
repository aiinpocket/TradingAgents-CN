# 🐳 Docker環境配置指南

## 📋 概述

本文档詳細介紹TradingAgents-CN在Docker環境中的配置方法，包括環境變量設置、服務配置、網絡配置和數據持久化配置。

## 🎯 Docker配置特點

### 与本地部署的区別

| 配置項 | 本地部署 | Docker部署 |
|-------|---------|-----------|
| **數據庫連接** | localhost | 容器服務名 |
| **端口配置** | 直接端口 | 端口映射 |
| **文件路徑** | 絕對路徑 | 容器內路徑 |
| **環境隔離** | 系統環境 | 容器環境 |

### 配置優势

- ✅ **環境一致性**: 開發、測試、生產環境完全一致
- ✅ **自動服務發現**: 容器間自動DNS解析
- ✅ **網絡隔離**: 安全的內部網絡通信
- ✅ **數據持久化**: 數據卷保證數據安全

## 🔧 環境變量配置

### 基础環境變量

```bash
# === Docker環境基础配置 ===
# 應用配置
APP_NAME=TradingAgents-CN
APP_VERSION=0.1.7
APP_ENV=production

# 服務端口配置
WEB_PORT=8501
MONGODB_PORT=27017
REDIS_PORT=6379
MONGO_EXPRESS_PORT=8081
REDIS_COMMANDER_PORT=8082
```

### 數據庫連接配置

```bash
# === 數據庫連接配置 ===
# MongoDB配置 (使用容器服務名)
MONGODB_URL=mongodb://mongodb:27017/tradingagents
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_DATABASE=tradingagents

# MongoDB認證 (生產環境)
MONGODB_USERNAME=admin
MONGODB_PASSWORD=${MONGO_PASSWORD}
MONGODB_AUTH_SOURCE=admin

# Redis配置 (使用容器服務名)
REDIS_URL=redis://redis:6379
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Redis認證 (生產環境)
REDIS_PASSWORD=${REDIS_PASSWORD}
```

### LLM服務配置

```bash
# === LLM模型配置 ===
# DeepSeek配置
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
DEEPSEEK_ENABLED=true
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 阿里百炼配置
QWEN_API_KEY=${QWEN_API_KEY}
QWEN_ENABLED=true
QWEN_MODEL=qwen-plus

# Google AI配置
GOOGLE_API_KEY=${GOOGLE_API_KEY}
GOOGLE_ENABLED=true
GOOGLE_MODEL=gemini-1.5-pro

# 模型路由配置
LLM_SMART_ROUTING=true
LLM_PRIORITY_ORDER=deepseek,qwen,gemini
```

## 📊 Docker Compose配置

### 主應用服務配置

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
      # 數據庫連接
      - MONGODB_URL=mongodb://mongodb:27017/tradingagents
      - REDIS_URL=redis://redis:6379
      
      # LLM配置
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - QWEN_API_KEY=${QWEN_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      
      # 應用配置
      - APP_ENV=docker
      - EXPORT_ENABLED=true
      - EXPORT_DEFAULT_FORMAT=word,pdf
    volumes:
      # 配置文件
      - .env:/app/.env
      
      # 開發環境代碼同步 (可選)
      - ./web:/app/web
      - ./tradingagents:/app/tradingagents
      
      # 導出文件存储
      - ./exports:/app/exports
    depends_on:
      - mongodb
      - redis
    networks:
      - tradingagents
    restart: unless-stopped
```

### 數據庫服務配置

```yaml
  mongodb:
    image: mongo:4.4
    container_name: TradingAgents-mongodb
    ports:
      - "${MONGODB_PORT:-27017}:27017"
    environment:
      - MONGO_INITDB_DATABASE=tradingagents
      # 生產環境認證
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

### 管理界面配置

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

## 🌐 網絡配置

### 網絡定義

```yaml
networks:
  tradingagents:
    driver: bridge
    name: tradingagents_network
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 服務發現

```bash
# 容器內服務訪問
# MongoDB: mongodb:27017
# Redis: redis:6379
# Web應用: web:8501

# 外部訪問
# Web界面: localhost:8501
# MongoDB: localhost:27017
# Redis: localhost:6379
# Mongo Express: localhost:8081
# Redis Commander: localhost:8082
```

## 💾 數據持久化配置

### 數據卷定義

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

### 备份配置

```bash
# === 數據备份配置 ===
# 备份路徑
BACKUP_PATH=./backups
BACKUP_RETENTION_DAYS=30

# 自動备份
ENABLE_AUTO_BACKUP=true
BACKUP_SCHEDULE="0 2 * * *"  # 每天凌晨2點

# 备份壓縮
BACKUP_COMPRESS=true
BACKUP_ENCRYPTION=false
```

## 🔒 安全配置

### 生產環境安全

```bash
# === 安全配置 ===
# 管理員認證
ADMIN_USERNAME=admin
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# 數據庫認證
MONGO_USERNAME=admin
MONGO_PASSWORD=${MONGO_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}

# API密鑰加密
ENCRYPT_API_KEYS=true
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# 網絡安全
ENABLE_FIREWALL=true
ALLOWED_IPS=127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

### SSL/TLS配置

```yaml
# HTTPS配置 (可選)
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

## 📊 監控配置

### 健康檢查

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 日誌配置

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🚀 部署配置

### 開發環境

```bash
# 開發環境配置
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_HOT_RELOAD=true
```

### 生產環境

```bash
# 生產環境配置
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_HOT_RELOAD=false

# 性能配置
WORKERS=4
MAX_MEMORY=4G
MAX_CPU=2.0
```

## 🔧 故障排除

### 常见問題

1. **服務連接失败**
   ```bash
   # 檢查網絡連接
   docker exec TradingAgents-web ping mongodb
   docker exec TradingAgents-web ping redis
   ```

2. **數據持久化問題**
   ```bash
   # 檢查數據卷
   docker volume ls
   docker volume inspect mongodb_data
   ```

3. **環境變量問題**
   ```bash
   # 檢查環境變量
   docker exec TradingAgents-web env | grep MONGODB
   ```

---

*最後更新: 2025-07-13*  
*版本: cn-0.1.7*  
*贡献者: [@breeze303](https://github.com/breeze303)*
