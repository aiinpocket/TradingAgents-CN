#!/bin/bash
# TradingAgents Docker服務停止腳本
# 停止MongoDB、Redis和Redis Commander

echo "========================================"
echo "TradingAgents Docker服務停止腳本"
echo "========================================"

echo "🛑 停止TradingAgents相關服務..."

# 停止Redis Commander
echo "📊 停止Redis Commander..."
docker stop tradingagents-redis-commander 2>/dev/null
docker rm tradingagents-redis-commander 2>/dev/null

# 停止Redis
echo "📦 停止Redis..."
docker stop tradingagents-redis 2>/dev/null
docker rm tradingagents-redis 2>/dev/null

# 停止MongoDB
echo "📊 停止MongoDB..."
docker stop tradingagents-mongodb 2>/dev/null
docker rm tradingagents-mongodb 2>/dev/null

echo ""
echo "📋 檢查剩餘容器..."
docker ps --filter "name=tradingagents-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "========================================"
echo "✅ 所有TradingAgents服務已停止"
echo "========================================"
echo ""
echo "💡 提示:"
echo "   - 數據已保存在Docker卷中，下次啟動時會自動恢復"
echo "   - 如需完全清理數據，請手動刪除Docker卷:"
echo "     docker volume rm mongodb_data redis_data"
echo ""
