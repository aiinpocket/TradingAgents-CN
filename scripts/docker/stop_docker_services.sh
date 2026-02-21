#!/bin/bash
# TradingAgents Docker
# MongoDBRedisRedis Commander

echo "========================================"
echo "TradingAgents Docker"
echo "========================================"

echo " TradingAgents..."

# Redis Commander
echo " Redis Commander..."
docker stop tradingagents-redis-commander 2>/dev/null
docker rm tradingagents-redis-commander 2>/dev/null

# Redis
echo " Redis..."
docker stop tradingagents-redis 2>/dev/null
docker rm tradingagents-redis 2>/dev/null

# MongoDB
echo " MongoDB..."
docker stop tradingagents-mongodb 2>/dev/null
docker rm tradingagents-mongodb 2>/dev/null

echo ""
echo " ..."
docker ps --filter "name=tradingagents-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "========================================"
echo " TradingAgents"
echo "========================================"
echo ""
echo " :"
echo "   - Docker"
echo "   - Docker:"
echo "     docker volume rm mongodb_data redis_data"
echo ""
