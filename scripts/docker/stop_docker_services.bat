@echo off
REM TradingAgents Docker
REM MongoDBRedisRedis Commander

echo ========================================
echo TradingAgents Docker
echo ========================================

echo  TradingAgents...

REM Redis Commander
echo  Redis Commander...
docker stop tradingagents-redis-commander 2>nul
docker rm tradingagents-redis-commander 2>nul

REM Redis
echo  Redis...
docker stop tradingagents-redis 2>nul
docker rm tradingagents-redis 2>nul

REM MongoDB
echo  MongoDB...
docker stop tradingagents-mongodb 2>nul
docker rm tradingagents-mongodb 2>nul

echo.
echo  ...
docker ps --filter "name=tradingagents-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ========================================
echo  TradingAgents
echo ========================================
echo.
echo  :
echo    - Docker
echo    - Docker:
echo      docker volume rm mongodb_data redis_data
echo.

pause
