# Docker容器啟動失敗排查指南

## 🔍 快速排查步驟

### 1. 基礎檢查

```bash
# 檢查容器狀態
docker-compose ps -a

# 檢查Docker服務
docker version

# 檢查系統資源
docker system df
```

### 2. 查看日誌

```bash
# 查看所有服務日誌
docker-compose logs

# 查看特定服務日誌
docker-compose logs web
docker-compose logs mongodb
docker-compose logs redis

# 實時查看日誌
docker-compose logs -f web

# 查看最近的日誌
docker-compose logs --tail=50 web
```

### 3. 常見問題排查

#### 🔴 端口衝突
```bash
# Windows檢查端口占用
netstat -an | findstr :8501
netstat -an | findstr :27017
netstat -an | findstr :6379

# 杀死占用端口的進程
taskkill /PID <進程ID> /F
```

#### 🔴 數據卷問題
```bash
# 查看數據卷
docker volume ls | findstr tradingagents

# 刪除有問題的數據卷（會丟失數據）
docker volume rm tradingagents_mongodb_data
docker volume rm tradingagents_redis_data

# 重新創建數據卷
docker volume create tradingagents_mongodb_data
docker volume create tradingagents_redis_data
```

#### 🔴 網絡問題
```bash
# 查看網絡
docker network ls | findstr tradingagents

# 刪除網絡
docker network rm tradingagents-network

# 重新創建網絡
docker network create tradingagents-network
```

#### 🔴 鏡像問題
```bash
# 查看鏡像
docker images | findstr tradingagents

# 強制重新構建
docker-compose build --no-cache

# 刪除鏡像重新構建
docker rmi tradingagents-cn:latest
docker-compose up -d --build
```

### 4. 環境變量檢查

```bash
# 檢查.env文件是否存在
ls .env

# 檢查環境變量
docker-compose config
```

### 5. 磁盘空間檢查

```bash
# 檢查Docker磁盘使用
docker system df

# 清理無用資源
docker system prune -f

# 清理所有未使用資源（谨慎使用）
docker system prune -a -f
```

## 🛠️ 具體服務排查

### Web服務 (Streamlit)
```bash
# 查看Web服務日誌
docker-compose logs web

# 進入容器調試
docker-compose exec web bash

# 檢查Python環境
docker-compose exec web python --version
docker-compose exec web pip list
```

### MongoDB服務
```bash
# 查看MongoDB日誌
docker-compose logs mongodb

# 連接MongoDB測試
docker-compose exec mongodb mongo -u admin -p tradingagents123

# 檢查數據庫狀態
docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
```

### Redis服務
```bash
# 查看Redis日誌
docker-compose logs redis

# 連接Redis測試
docker-compose exec redis redis-cli -a tradingagents123

# 檢查Redis狀態
docker-compose exec redis redis-cli -a tradingagents123 ping
```

## 🚨 緊急修複命令

### 完全重置（會丟失數據）
```bash
# 停止所有容器
docker-compose down

# 刪除所有相關資源
docker-compose down -v --remove-orphans

# 清理系統
docker system prune -f

# 重新啟動
docker-compose up -d --build
```

### 保留數據重啟
```bash
# 停止容器
docker-compose down

# 重新啟動
docker-compose up -d
```

## 📝 日誌分析技巧

### 常見錯誤模式

1. **端口占用**: `bind: address already in use`
2. **權限問題**: `permission denied`
3. **磁盘空間**: `no space left on device`
4. **內存不足**: `out of memory`
5. **網絡問題**: `network not found`
6. **鏡像問題**: `image not found`

### 日誌過濾
```bash
# 只看錯誤日誌
docker-compose logs | findstr ERROR

# 只看警告日誌
docker-compose logs | findstr WARN

# 查看特定時間段日誌
docker-compose logs --since="2025-01-01T00:00:00"
```

## 🔧 預防措施

1. **定期清理**: `docker system prune -f`
2. **監控資源**: `docker system df`
3. **備份數據**: 定期備份數據卷
4. **版本控制**: 記錄工作的配置版本
5. **健康檢查**: 配置容器健康檢查

## 📞 獲取幫助

如果以上方法都無法解決問題，請：

1. 收集完整的錯誤日誌
2. 記錄系統環境信息
3. 描述具體的操作步驟
4. 提供docker-compose.yml配置