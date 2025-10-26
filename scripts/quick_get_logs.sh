#!/bin/bash
# 快速獲取TradingAgents Docker容器日誌

echo "🚀 TradingAgents Docker日誌獲取工具"
echo "=================================="

# 查找容器
CONTAINER_NAMES=("tradingagents-data-service" "tradingagents_data-service_1" "data-service" "tradingagents-cn-data-service-1")
CONTAINER=""

for name in "${CONTAINER_NAMES[@]}"; do
    if docker ps --filter "name=$name" --format "{{.Names}}" | grep -q "$name"; then
        CONTAINER="$name"
        echo "✅ 找到容器: $CONTAINER"
        break
    fi
done

if [ -z "$CONTAINER" ]; then
    echo "❌ 未找到TradingAgents容器"
    echo "📋 當前運行的容器:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    echo ""
    read -p "請輸入容器名稱: " CONTAINER
    if [ -z "$CONTAINER" ]; then
        echo "❌ 未提供容器名稱，退出"
        exit 1
    fi
fi

# 創建時間戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo ""
echo "📋 獲取日誌信息..."

# 1. 獲取Docker標準日誌
echo "1️⃣ 獲取Docker標準日誌..."
docker logs "$CONTAINER" > "docker_logs_${TIMESTAMP}.log" 2>&1
echo "✅ Docker日誌已保存到: docker_logs_${TIMESTAMP}.log"

# 2. 查找容器內日誌文件
echo ""
echo "2️⃣ 查找容器內日誌文件..."
LOG_FILES=$(docker exec "$CONTAINER" find /app -name "*.log" -type f 2>/dev/null || true)

if [ -n "$LOG_FILES" ]; then
    echo "📄 找到以下日誌文件:"
    echo "$LOG_FILES"
    
    # 複制每個日誌文件
    echo ""
    echo "3️⃣ 複制日誌文件到本地..."
    while IFS= read -r log_file; do
        if [ -n "$log_file" ]; then
            filename=$(basename "$log_file")
            local_file="${filename}_${TIMESTAMP}"
            
            echo "📤 複制: $log_file -> $local_file"
            if docker cp "$CONTAINER:$log_file" "$local_file"; then
                echo "✅ 成功複制: $local_file"
                
                # 顯示文件信息
                if [ -f "$local_file" ]; then
                    size=$(wc -c < "$local_file")
                    lines=$(wc -l < "$local_file")
                    echo "   📊 文件大小: $size 字節, $lines 行"
                fi
            else
                echo "❌ 複制失败: $log_file"
            fi
        fi
    done <<< "$LOG_FILES"
else
    echo "⚠️ 未在容器中找到.log文件"
fi

# 3. 獲取容器內應用目錄信息
echo ""
echo "4️⃣ 檢查應用目錄結構..."
echo "📂 /app 目錄內容:"
docker exec "$CONTAINER" ls -la /app/ 2>/dev/null || echo "❌ 無法訪問/app目錄"

echo ""
echo "📂 查找所有可能的日誌文件:"
docker exec "$CONTAINER" find /app -name "*log*" -type f 2>/dev/null || echo "❌ 未找到包含'log'的文件"

# 4. 檢查環境變量和配置
echo ""
echo "5️⃣ 檢查日誌配置..."
echo "🔧 環境變量:"
docker exec "$CONTAINER" env | grep -i log || echo "❌ 未找到日誌相關環境變量"

# 5. 獲取最近的應用輸出
echo ""
echo "6️⃣ 獲取最近的應用輸出 (最後50行):"
echo "=================================="
docker logs --tail 50 "$CONTAINER" 2>&1
echo "=================================="

echo ""
echo "🎉 日誌獲取完成!"
echo "📁 生成的文件:"
ls -la *_${TIMESTAMP}* 2>/dev/null || echo "   (無額外文件生成)"

echo ""
echo "💡 使用建议:"
echo "   - 如果源碼目錄的tradingagents.log為空，說明日誌可能輸出到stdout"
echo "   - Docker標準日誌包含了應用的所有輸出"
echo "   - 檢查應用的日誌配置，確保日誌寫入到文件"
echo ""
echo "📧 發送日誌文件:"
echo "   請将 docker_logs_${TIMESTAMP}.log 文件發送給開發者"
if [ -f "tradingagents.log_${TIMESTAMP}" ]; then
    echo "   以及 tradingagents.log_${TIMESTAMP} 文件"
fi
