#!/bin/bash
# Docker排查命令集合 - Linux/Mac版本

echo "=== Docker容器排查工具 ==="

# 1. 檢查Docker服務狀態
echo -e "\n1. 檢查Docker服務狀態:"
if docker version > /dev/null 2>&1; then
    echo "✅ Docker服務正常運行"
else
    echo "❌ Docker服務未運行或有問題"
    exit 1
fi

# 2. 檢查容器狀態
echo -e "\n2. 檢查容器狀態:"
docker-compose ps -a

# 3. 檢查網絡狀態
echo -e "\n3. 檢查Docker網絡:"
docker network ls | grep tradingagents

# 4. 檢查數據卷狀態
echo -e "\n4. 檢查數據卷:"
docker volume ls | grep tradingagents

# 5. 檢查端口占用
echo -e "\n5. 檢查端口占用:"
ports=(8501 27017 6379 8081 8082)
for port in "${ports[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "端口 $port 被占用:"
        lsof -i :$port
    else
        echo "端口 $port 空閒"
    fi
done

# 6. 檢查磁碟空間
echo -e "\n6. 檢查磁碟空間:"
docker system df

echo -e "\n=== 排查完成 ==="
echo "如需查看詳細日誌，請執行:"
echo "docker-compose logs [服務名]"
echo "例如: docker-compose logs web"