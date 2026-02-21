# 🐳 Docker部署使用指南

## 📋 概述

TradingAgents-CN v0.1.7 引入了完整的Docker容器化部署方案，讓您可以通過一條命令啟動完整的股票分析環境。本指南將詳細介紹如何使用Docker部署和管理TradingAgents-CN。

## 🎯 Docker部署優勢

### 為什么選擇Docker？

- ✅ **一鍵部署**: `docker-compose up -d` 啟動完整環境
- ✅ **環境一致**: 開發、測試、生產環境完全一致
- ✅ **依賴管理**: 自動處理所有依賴和版本衝突
- ✅ **服務集成**: Web應用、數據庫、緩存一體化
- ✅ **易於維護**: 簡化更新、備份、恢復流程

### 與傳統部署對比

| 特性 | 傳統部署 | Docker部署 |
|------|---------|-----------|
| **部署時間** | 30-60分鐘 | 5-10分鐘 |
| **環境配置** | 複雜手動配置 | 自動化配置 |
| **依賴管理** | 手動安裝 | 自動處理 |
| **服務管理** | 分別啟動 | 統一管理 |
| **故障排除** | 複雜 | 簡化 |

## 🚀 快速開始

### 前置要求

| 組件 | 最低版本 | 推薦版本 | 安裝方法 |
|------|---------|----------|----------|
| **Docker** | 20.0+ | 最新版 | [官方安裝指南](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.0+ | 最新版 | 通常隨Docker一起安裝 |
| **內存** | 4GB | 8GB+ | 系統要求 |
| **磁盤空間** | 10GB | 20GB+ | 存储要求 |

### 安裝Docker

#### Windows
```bash
# 1. 下載Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. 安裝並啟動Docker Desktop

# 3. 驗證安裝
docker --version
docker-compose --version
```

#### Linux (Ubuntu/Debian)
```bash
# 1. 更新包索引
sudo apt update

# 2. 安裝Docker
sudo apt install docker.io docker-compose

# 3. 啟動Docker服務
sudo systemctl start docker
sudo systemctl enable docker

# 4. 添加用戶到docker組
sudo usermod -aG docker $USER

# 5. 驗證安裝
docker --version
docker-compose --version
```

#### macOS
```bash
# 1. 使用Homebrew安裝
brew install --cask docker

# 2. 啟動Docker Desktop

# 3. 驗證安裝
docker --version
docker-compose --version
```

## 🔧 部署步驟

### 步驟1: 獲取代碼

```bash
# 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 檢查版本
cat VERSION
```

### 📦 關於Docker鏡像

**重要說明**: TradingAgents-CN目前不提供預構建的Docker鏡像，需要在本地構建。

#### 為什么需要本地構建？

1. **定制化需求**: 不同用戶可能需要不同的配置
2. **安全考慮**: 避免在公共鏡像中包含敏感信息
3. **版本靈活性**: 支援用戶自定義修改和擴展
4. **依賴優化**: 根據實際需求安裝依賴

#### 構建過程說明

```bash
# Docker構建過程包括：
1. 下載基礎鏡像 (python:3.10-slim) - 約200MB
2. 安裝系統依賴 (pandoc, wkhtmltopdf, 中文字體) - 約300MB
3. 安裝Python依賴 (requirements.txt) - 約500MB
4. 複制應用代碼 - 約50MB
5. 配置運行環境

# 總鏡像大小約1GB，首次構建需要5-10分鐘
```

### 步驟2: 配置環境

```bash
# 複制配置模板
cp .env.example .env

# 編辑配置文件
# Windows: notepad .env
# Linux/macOS: nano .env
```

#### 必需配置

```bash
# === LLM模型配置 (至少配置一個) ===
# OpenAI (推薦 - 強大性能)
OPENAI_API_KEY=your_openai_api_key
OPENAI_ENABLED=true

# Google AI (推薦 - 推理能力強)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_ENABLED=true
```

#### 可選配置

```bash
# === 數據源配置 ===
FINNHUB_API_KEY=your_finnhub_key

# === 導出功能配置 ===
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf

# === Docker特定配置 ===
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379
```

### 步驟3: 構建並啟動服務

```bash
# 首次啟動：構建鏡像並啟動所有服務
docker-compose up -d --build

# 註意：首次運行會自動構建Docker鏡像，包含以下步驟：
# - 下載基礎鏡像 (python:3.10-slim)
# - 安裝系統依賴 (pandoc, wkhtmltopdf等)
# - 安裝Python依賴
# - 複制應用代碼
# 整個過程需要5-10分鐘，請耐心等待

# 後續啟動（鏡像已構建）：
# docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看啟動日誌
docker-compose logs -f
```

### 步驟4: 驗證部署

```bash
# 檢查服務狀態
docker-compose ps

# 應該看到以下服務運行中:
# - TradingAgents-web (Web應用)
# - TradingAgents-mongodb (數據庫)
# - TradingAgents-redis (緩存)
# - TradingAgents-mongo-express (數據庫管理)
# - TradingAgents-redis-commander (緩存管理)
```

### 步驟5: 訪問應用

| 服務 | 地址 | 用途 |
|------|------|------|
| **主應用** | http://localhost:8501 | 股票分析界面 |
| **數據庫管理** | http://localhost:8081 | MongoDB管理 |
| **緩存管理** | http://localhost:8082 | Redis管理 |

## 🎯 使用指南

### 進行股票分析

1. **訪問主界面**: http://localhost:8501
2. **選擇LLM模型**: 推薦 GPT-4 或 Google Gemini
3. **輸入股票代碼**:
   - 美股: AAPL, TSLA, MSFT, GOOGL
4. **選擇分析深度**: 快速/標準/深度
5. **開始分析**: 點擊"開始分析"按鈕
6. **導出報告**: 選擇Word/PDF/Markdown格式

### 管理數據庫

1. **訪問MongoDB管理**: http://localhost:8081
2. **查看分析結果**: 瀏覽tradingagents數據庫
3. **管理數據**: 查看、編辑、刪除分析記錄

### 管理緩存

1. **訪問Redis管理**: http://localhost:8082
2. **查看緩存數據**: 瀏覽緩存的股價和分析數據
3. **清理緩存**: 刪除過期或無用的緩存

## 🔧 日常管理

### 服務管理

```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 查看服務狀態
docker-compose ps

# 查看服務日誌
docker-compose logs -f web
docker-compose logs -f mongodb
docker-compose logs -f redis
```

### 數據管理

```bash
# 備份數據
docker exec TradingAgents-mongodb mongodump --out /backup
docker exec TradingAgents-redis redis-cli BGSAVE

# 清理緩存
docker exec TradingAgents-redis redis-cli FLUSHALL

# 查看數據使用情況
docker exec TradingAgents-mongodb mongo --eval "db.stats()"
```

### 更新應用

```bash
# 1. 停止服務
docker-compose down

# 2. 更新代碼
git pull origin main

# 3. 重新構建鏡像
docker-compose build

# 4. 啟動服務
docker-compose up -d
```

## 🚨 故障排除

### 常見問題

#### 1. 端口衝突

**問題**: 服務啟動失敗，提示端口被占用

**解決方案**:
```bash
# 檢查端口占用
netstat -tulpn | grep :8501

# 修改端口配置
# 編辑docker-compose.yml，修改端口映射
ports:
  - "8502:8501"  # 改為其他端口
```

#### 2. 內存不足

**問題**: 容器啟動失敗或運行緩慢

**解決方案**:
```bash
# 檢查內存使用
docker stats

# 增加Docker內存限制
# Docker Desktop -> Settings -> Resources -> Memory
# 建議分配至少4GB內存
```

#### 3. 數據庫連接失敗

**問題**: Web應用無法連接數據庫

**解決方案**:
```bash
# 檢查數據庫容器狀態
docker logs TradingAgents-mongodb

# 檢查網絡連接
docker exec TradingAgents-web ping mongodb

# 重啟數據庫服務
docker-compose restart mongodb
```

#### 4. API密鑰問題

**問題**: LLM調用失敗

**解決方案**:
```bash
# 檢查環境變量
docker exec TradingAgents-web env | grep API_KEY

# 重新配置.env文件
# 重啟服務
docker-compose restart web
```

### 性能優化

```bash
# 1. 清理無用鏡像
docker image prune

# 2. 清理無用容器
docker container prune

# 3. 清理無用數據卷
docker volume prune

# 4. 查看資源使用
docker stats
```

## 📊 監控和維護

### 健康檢查

```bash
# 檢查所有服務健康狀態
docker-compose ps

# 檢查特定服務日誌
docker logs TradingAgents-web --tail 50

# 檢查系統資源使用
docker stats --no-stream
```

### 定期維護

```bash
# 每周執行一次
# 1. 備份數據
docker exec TradingAgents-mongodb mongodump --out /backup/$(date +%Y%m%d)

# 2. 清理日誌
docker-compose logs --tail 0 -f > /dev/null

# 3. 更新鏡像
docker-compose pull
docker-compose up -d
```

## 🔮 高級配置

### 生產環境部署

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

### 安全配置

```bash
# 啟用認證
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=secure_password
REDIS_PASSWORD=secure_redis_password
```

---

## 📞 獲取幫助

如果在Docker部署過程中遇到問題：

- 🐛 [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
- 💬 [GitHub Discussions](https://github.com/hsliuping/TradingAgents-CN/discussions)
- 📚 [Docker官方文檔](https://docs.docker.com/)

---

*最後更新: 2025-07-13*  
*版本: cn-0.1.7*  
*貢獻者: [@breeze303](https://github.com/breeze303)*
