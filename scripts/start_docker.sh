#!/bin/bash
# TradingAgents Docker 
# Docker

echo " TradingAgents Docker "
echo "=========================="

# Docker
if ! docker info >/dev/null 2>&1; then
echo " DockerDocker"
exit 1
fi

# docker-compose
if ! command -v docker-compose >/dev/null 2>&1; then
echo " docker-compose"
exit 1
fi

# logs
echo " logs..."
mkdir -p logs
chmod 755 logs 2>/dev/null || true
echo " logs"

# .env
if [ ! -f ".env" ]; then
echo " .env"
if [ -f ".env.example" ]; then
echo " .env.example.env"
cp .env.example .env
echo " .envAPI"
else
echo " .env.example"
exit 1
fi
fi

# 
echo ""
echo " :"
echo "   : $(pwd)"
echo "   : $(pwd)/logs"
echo "   : .env"

# Docker
echo ""
echo " Docker..."
docker-compose up -d

# 
echo ""
echo " ..."
docker-compose ps

# 
echo ""
echo " ..."
sleep 10

# Web
echo ""
echo " Web..."
if curl -s http://localhost:8501/_stcore/health >/dev/null 2>&1; then
echo " Web"
echo " : http://localhost:8501"
else
echo " Web..."
echo " : http://localhost:8501"
fi

# 
echo ""
echo " :"
echo "   : ./logs/"
echo "   : tail -f logs/tradingagents.log"
echo "   Docker: docker-compose logs -f web"

echo ""
echo " "
echo ""
echo " :"
echo "   : docker-compose ps"
echo "   : docker-compose logs -f web"
echo "   : docker-compose down"
echo "   : docker-compose restart web"
