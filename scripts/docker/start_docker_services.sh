#!/bin/bash
# TradingAgents Docker
# MongoDBRedisRedis Commander

echo "========================================"
echo "TradingAgents Docker"
echo "========================================"

# Docker
echo "Docker..."
if ! docker version >/dev/null 2>&1; then
echo " DockerDocker"
exit 1
fi
echo " Docker"

echo ""
echo " ..."

# MongoDB
echo " MongoDB..."
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
echo " MongoDB - : 27017"
else
echo " MongoDB"
fi

# Redis
echo " Redis..."
docker run -d \
--name tradingagents-redis \
-p 6379:6379 \
-v redis_data:/data \
--restart unless-stopped \
redis:latest redis-server --appendonly yes --requirepass tradingagents123

if [ $? -eq 0 ]; then
echo " Redis - : 6379"
else
echo " Redis"
fi

# 
echo " ..."
sleep 5

# Redis Commander (Redis)
echo " Redis Commander..."
docker run -d \
--name tradingagents-redis-commander \
-p 8081:8081 \
-e REDIS_HOSTS=local:tradingagents-redis:6379:0:tradingagents123 \
--link tradingagents-redis:redis \
--restart unless-stopped \
rediscommander/redis-commander:latest

if [ $? -eq 0 ]; then
echo " Redis Commander - : http://localhost:8081"
else
echo " Redis Commander"
fi

echo ""
echo " ..."
docker ps --filter "name=tradingagents-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "========================================"
echo " Docker"
echo "========================================"
echo ""
echo " MongoDB:"
echo "   - : mongodb://admin:tradingagents123@localhost:27017/tradingagents"
echo "   - : 27017"
echo "   - : admin"
echo "   - : tradingagents123"
echo ""
echo " Redis:"
echo "   - : redis://localhost:6379"
echo "   - : 6379"
echo "   - : tradingagents123"
echo ""
echo " Redis Commander:"
echo "   - : http://localhost:8081"
echo ""
echo " :"
echo "   -  ./stop_docker_services.sh "
echo "   -  docker logs [] "
echo "   - Docker"
echo ""
