# 🐳 Docker容器化部署指南

## 🎯 功能概述

TradingAgents-CN 提供了完整的Docker容器化部署方案，支持一键啟動完整的分析環境，包括Web應用、數據庫、緩存系統和管理界面。

## 🏗️ 架構設計

### 容器化架構圖

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ TradingAgents│  │   MongoDB   │  │    Redis    │     │
│  │     Web     │  │   Database  │  │    Cache    │     │
│  │  (Streamlit)│  │             │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                 │                 │          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Volume    │  │  Mongo      │  │   Redis     │     │
│  │   Mapping   │  │  Express    │  │ Commander   │     │
│  │ (開發環境)   │  │ (管理界面)   │  │ (管理界面)   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 服務組件

1. **🌐 TradingAgents-Web**
   - Streamlit Web應用
   - 端口: 8501
   - 功能: 股票分析、報告導出

2. **🗄️ MongoDB**
   - 數據持久化存储
   - 端口: 27017
   - 功能: 分析結果、用戶數據

3. **🔄 Redis**
   - 高性能緩存
   - 端口: 6379
   - 功能: 數據緩存、會話管理

4. **📊 MongoDB Express**
   - 數據庫管理界面
   - 端口: 8081
   - 功能: 數據庫可視化管理

5. **🎛️ Redis Commander**
   - 緩存管理界面
   - 端口: 8082
   - 功能: 緩存數據查看和管理

## 🚀 快速開始

### 環境要求

- Docker 20.0+
- Docker Compose 2.0+
- 4GB+ 可用內存
- 10GB+ 可用磁盘空間

### 一键部署

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 配置環境變量
cp .env.example .env
# 編辑 .env 文件，填入API密鑰

# 3. 構建並啟動所有服務
docker-compose up -d --build
# 註意：首次運行會構建Docker鏡像，需要5-10分鐘

# 4. 驗證部署
docker-compose ps
```

### 📦 Docker鏡像構建說明

**重要提醒**: TradingAgents-CN不提供預構建的Docker鏡像，需要本地構建。

#### 構建過程詳解

```bash
# 構建過程包括以下步骤：
1. 📥 下載基础鏡像 (python:3.10-slim)
2. 🔧 安裝系統依賴 (pandoc, wkhtmltopdf, 中文字體)
3. 📦 安裝Python依賴包 (requirements.txt)
4. 📁 複制應用代碼到容器
5. ⚙️ 配置運行環境和權限

# 預期構建時間和資源：
- ⏱️ 構建時間: 5-10分鐘 (取決於網絡速度)
- 💾 鏡像大小: 約1GB
- 🌐 網絡需求: 下載約800MB依賴
- 💻 內存需求: 構建時需要2GB+內存
```

#### 構建優化建议

```bash
# 1. 使用國內鏡像源加速 (可選)
# 編辑 Dockerfile，添加：
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 多階段構建緩存
# 如果需要頻繁重建，可以分步構建：
docker-compose build --no-cache  # 完全重建
docker-compose build             # 使用緩存構建

# 3. 查看構建進度
docker-compose up --build        # 顯示詳細構建日誌
```

### 訪問服務

部署完成後，可以通過以下地址訪問各個服務：

- **🌐 主應用**: http://localhost:8501
- **📊 數據庫管理**: http://localhost:8081
- **🎛️ 緩存管理**: http://localhost:8082

## ⚙️ 配置詳解

### Docker Compose配置

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .env:/app/.env
      # 開發環境映射（可選）
      - ./web:/app/web
      - ./tradingagents:/app/tradingagents
    depends_on:
      - mongodb
      - redis
    environment:
      - MONGODB_URL=mongodb://mongodb:27017/tradingagents
      - REDIS_URL=redis://redis:6379

  mongodb:
    image: mongo:4.4
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=tradingagents

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  mongo-express:
    image: mongo-express
    ports:
      - "8081:8081"
    environment:
      - ME_CONFIG_MONGODB_SERVER=mongodb
      - ME_CONFIG_MONGODB_PORT=27017
    depends_on:
      - mongodb

  redis-commander:
    image: rediscommander/redis-commander
    ports:
      - "8082:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379
    depends_on:
      - redis

volumes:
  mongodb_data:
  redis_data:
```

### 環境變量配置

```bash
# .env 文件示例
# LLM API配置
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_
QWEN_API_KEY=your_qwen_key

# 數據源配置
TUSHARE_TOKEN=your__token
FINNHUB_API_KEY=your_finnhub_key

# 數據庫配置
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379

# 導出功能配置
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf
```

## 🔧 開發環境配置

### Volume映射

開發環境支持實時代碼同步：

```yaml
volumes:
  - .env:/app/.env
  - ./web:/app/web                    # Web界面代碼
  - ./tradingagents:/app/tradingagents # 核心分析代碼
  - ./scripts:/app/scripts            # 腳本文件
  - ./test_conversion.py:/app/test_conversion.py # 測試工具
```

### 開發工作流

```bash
# 1. 啟動開發環境
docker-compose up -d

# 2. 修改代碼（自動同步到容器）
# 編辑本地文件，容器內立即生效

# 3. 查看日誌
docker logs TradingAgents-web --follow

# 4. 進入容器調試
docker exec -it TradingAgents-web bash

# 5. 測試功能
docker exec TradingAgents-web python test_conversion.py
```

## 📊 監控和管理

### 服務狀態檢查

```bash
# 查看所有服務狀態
docker-compose ps

# 查看特定服務日誌
docker logs TradingAgents-web
docker logs TradingAgents-mongodb
docker logs TradingAgents-redis

# 查看資源使用情况
docker stats
```

### 數據管理

```bash
# 备份MongoDB數據
docker exec TradingAgents-mongodb mongodump --out /backup

# 备份Redis數據
docker exec TradingAgents-redis redis-cli BGSAVE

# 清理緩存
docker exec TradingAgents-redis redis-cli FLUSHALL
```

### 服務重啟

```bash
# 重啟單個服務
docker-compose restart web

# 重啟所有服務
docker-compose restart

# 重新構建並啟動
docker-compose up -d --build
```

## 🚨 故障排除

### 常见問題

1. **端口冲突**
   ```bash
   # 檢查端口占用
   netstat -tulpn | grep :8501
   
   # 修改端口映射
   # 編辑 docker-compose.yml 中的 ports 配置
   ```

2. **內存不足**
   ```bash
   # 增加Docker內存限制
   # 在 docker-compose.yml 中添加：
   deploy:
     resources:
       limits:
         memory: 4G
   ```

3. **數據庫連接失败**
   ```bash
   # 檢查數據庫服務狀態
   docker logs TradingAgents-mongodb
   
   # 檢查網絡連接
   docker exec TradingAgents-web ping mongodb
   ```

### 性能優化

1. **資源限制**
   ```yaml
   services:
     web:
       deploy:
         resources:
           limits:
             cpus: '2.0'
             memory: 4G
           reservations:
             memory: 2G
   ```

2. **數據持久化**
   ```yaml
   volumes:
     mongodb_data:
       driver: local
       driver_opts:
         type: none
         o: bind
         device: /path/to/mongodb/data
   ```

## 🔒 安全配置

### 生產環境安全

```yaml
# 生產環境配置示例
services:
  mongodb:
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secure_password
    
  mongo-express:
    environment:
      - ME_CONFIG_BASICAUTH_USERNAME=admin
      - ME_CONFIG_BASICAUTH_PASSWORD=secure_password
```

### 網絡安全

```yaml
networks:
  tradingagents:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  web:
    networks:
      - tradingagents
```

## 🙏 致谢

### 功能贡献者

Docker容器化功能由社区贡献者 **[@breeze303](https://github.com/breeze303)** 設計並實現，包括：

- 🐳 Docker Compose多服務編排配置
- 🏗️ 容器化架構設計和優化
- 📊 數據庫和緩存服務集成
- 🔧 開發環境Volume映射配置
- 📚 完整的部署文档和最佳實踐

感谢他的杰出贡献，让TradingAgents-CN擁有了專業級的容器化部署能力！

---

*最後更新: 2025-07-13*  
*版本: cn-0.1.7*  
*功能贡献: [@breeze303](https://github.com/breeze303)*
