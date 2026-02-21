#!/bin/bash
# TradingAgents-CN Docker (Linux/Mac Bash)
# Docker
# chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh
# 
# 
# 1. tradingagents-cn
# 2.  -> 
# 3.  ->   
# 4.  -> 

echo "=== TradingAgents-CN Docker  ==="
echo ": Linux/Mac Bash"

# 
if docker images | grep -q "tradingagents-cn"; then
echo " "
    
# 
if git diff --quiet HEAD~1 HEAD -- . ':!*.md' ':!docs/' ':!scripts/'; then
echo " "
docker-compose up -d
else
echo " "
docker-compose up -d --build
fi
else
echo " "
docker-compose up -d --build
fi

echo " "
echo "Web: http://localhost:8501"
echo "Redis: http://localhost:8081"