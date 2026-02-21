#!/bin/bash
# Docker - Linux/Mac

echo "=== Docker ==="

# 1. Docker
echo -e "\n1. Docker:"
if docker version > /dev/null 2>&1; then
echo " Docker"
else
echo " Docker"
exit 1
fi

# 2. 
echo -e "\n2. :"
docker-compose ps -a

# 3. 
echo -e "\n3. Docker:"
docker network ls | grep tradingagents

# 4. 
echo -e "\n4. :"
docker volume ls | grep tradingagents

# 5. 
echo -e "\n5. :"
ports=(8501 27017 6379 8081 8082)
for port in "${ports[@]}"; do
if lsof -i :$port > /dev/null 2>&1; then
echo " $port :"
lsof -i :$port
else
echo " $port "
fi
done

# 6. 
echo -e "\n6. :"
docker system df

echo -e "\n===  ==="
echo ":"
echo "docker-compose logs []"
echo ": docker-compose logs web"