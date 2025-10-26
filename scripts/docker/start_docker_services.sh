#!/bin/bash
# TradingAgents Docker服務啟動腳本
# 啟動MongoDB、Redis和Redis Commander

echo "========================================"
echo "TradingAgents Docker服務啟動腳本"
echo "========================================"

# 檢查Docker是否運行
echo "檢查Docker服務狀態..."
if ! docker version >/dev/null 2>&1; then
    echo "❌ Docker未運行或未安裝，請先啟動Docker"
    exit 1
fi
echo "✅ Docker服務正常"

echo ""
echo "🚀 啟動數據庫服務..."

# 啟動MongoDB
echo "📊 啟動MongoDB..."
docker run -d \
    --name tradingagents-mongodb \
    -p 27017:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=admin \
    -e MONGO_INITDB_ROOT_PASSWORD=tradingagents123 \
    -e MONGO_INITDB_DATABASE=tradingagents \
    -v mongodb_data:/data/db \
    --restart unless-stopped \
    mongo:4.4

if [ $? -eq 0 ]; then
    echo "✅ MongoDB啟動成功 - 端口: 27017"
else
    echo "⚠️ MongoDB可能已在運行或啟動失败"
fi

# 啟動Redis
echo "📦 啟動Redis..."
docker run -d \
    --name tradingagents-redis \
    -p 6379:6379 \
    -v redis_data:/data \
    --restart unless-stopped \
    redis:latest redis-server --appendonly yes --requirepass tradingagents123

if [ $? -eq 0 ]; then
    echo "✅ Redis啟動成功 - 端口: 6379"
else
    echo "⚠️ Redis可能已在運行或啟動失败"
fi

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 5

# 啟動Redis Commander (可選的Redis管理界面)
echo "🖥️ 啟動Redis Commander..."
docker run -d \
    --name tradingagents-redis-commander \
    -p 8081:8081 \
    -e REDIS_HOSTS=local:tradingagents-redis:6379:0:tradingagents123 \
    --link tradingagents-redis:redis \
    --restart unless-stopped \
    rediscommander/redis-commander:latest

if [ $? -eq 0 ]; then
    echo "✅ Redis Commander啟動成功 - 訪問地址: http://localhost:8081"
else
    echo "⚠️ Redis Commander可能已在運行或啟動失败"
fi

echo ""
echo "📋 服務狀態檢查..."
docker ps --filter "name=tradingagents-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "========================================"
echo "🎉 Docker服務啟動完成！"
echo "========================================"
echo ""
echo "📊 MongoDB:"
echo "   - 連接地址: mongodb://admin:tradingagents123@localhost:27017/tradingagents"
echo "   - 端口: 27017"
echo "   - 用戶名: admin"
echo "   - 密碼: tradingagents123"
echo ""
echo "📦 Redis:"
echo "   - 連接地址: redis://localhost:6379"
echo "   - 端口: 6379"
echo "   - 密碼: tradingagents123"
echo ""
echo "🖥️ Redis Commander:"
echo "   - 管理界面: http://localhost:8081"
echo ""
echo "💡 提示:"
echo "   - 使用 ./stop_docker_services.sh 停止所有服務"
echo "   - 使用 docker logs [容器名] 查看日誌"
echo "   - 數據将持久化保存在Docker卷中"
echo ""
