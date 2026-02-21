#!/bin/bash
# 快速取得 TradingAgents Docker 容器日誌

echo "TradingAgents Docker 日誌取得工具"
echo "=================================="

# 查找容器
CONTAINER_NAMES=("tradingagents-data-service" "tradingagents_data-service_1" "data-service" "tradingagents-cn-data-service-1")
CONTAINER=""

for name in "${CONTAINER_NAMES[@]}"; do
    if docker ps --filter "name=$name" --format "{{.Names}}" | grep -q "$name"; then
        CONTAINER="$name"
        echo "[OK] 找到容器: $CONTAINER"
        break
    fi
done

if [ -z "$CONTAINER" ]; then
    echo "[ERROR] 未找到 TradingAgents 容器"
    echo "當前執行的容器:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    echo ""
    read -p "請輸入容器名稱: " CONTAINER
    if [ -z "$CONTAINER" ]; then
        echo "[ERROR] 未提供容器名稱，退出"
        exit 1
    fi
fi

# 建立時間戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo ""
echo "取得日誌資訊..."

# 1. 取得 Docker 標準日誌
echo "[1] 取得 Docker 標準日誌..."
docker logs "$CONTAINER" > "docker_logs_${TIMESTAMP}.log" 2>&1
echo "[OK] Docker 日誌已儲存到: docker_logs_${TIMESTAMP}.log"

# 2. 查找容器內日誌檔案
echo ""
echo "[2] 查找容器內日誌檔案..."
LOG_FILES=$(docker exec "$CONTAINER" find /app -name "*.log" -type f 2>/dev/null || true)

if [ -n "$LOG_FILES" ]; then
    echo "找到以下日誌檔案:"
    echo "$LOG_FILES"

    # 複製每個日誌檔案
    echo ""
    echo "[3] 複製日誌檔案到本地..."
    while IFS= read -r log_file; do
        if [ -n "$log_file" ]; then
            filename=$(basename "$log_file")
            local_file="${filename}_${TIMESTAMP}"

            echo "複製: $log_file -> $local_file"
            if docker cp "$CONTAINER:$log_file" "$local_file"; then
                echo "[OK] 成功複製: $local_file"

                # 顯示檔案資訊
                if [ -f "$local_file" ]; then
                    size=$(wc -c < "$local_file")
                    lines=$(wc -l < "$local_file")
                    echo "   檔案大小: $size 位元組, $lines 行"
                fi
            else
                echo "[ERROR] 複製失敗: $log_file"
            fi
        fi
    done <<< "$LOG_FILES"
else
    echo "[WARN] 未在容器中找到 .log 檔案"
fi

# 3. 取得容器內應用目錄資訊
echo ""
echo "[4] 檢查應用目錄結構..."
echo "/app 目錄內容:"
docker exec "$CONTAINER" ls -la /app/ 2>/dev/null || echo "[ERROR] 無法存取 /app 目錄"

echo ""
echo "查找所有可能的日誌檔案:"
docker exec "$CONTAINER" find /app -name "*log*" -type f 2>/dev/null || echo "[ERROR] 未找到包含 'log' 的檔案"

# 4. 檢查環境變數和配置
echo ""
echo "[5] 檢查日誌配置..."
echo "環境變數:"
docker exec "$CONTAINER" env | grep -i log || echo "[ERROR] 未找到日誌相關環境變數"

# 5. 取得最近的應用輸出
echo ""
echo "[6] 取得最近的應用輸出（最後 50 行）:"
echo "=================================="
docker logs --tail 50 "$CONTAINER" 2>&1
echo "=================================="

echo ""
echo "日誌取得完成！"
echo "產生的檔案:"
ls -la *_${TIMESTAMP}* 2>/dev/null || echo "   （無額外檔案產生）"

echo ""
echo "使用建議:"
echo "   - 如果原始碼目錄的 tradingagents.log 為空，說明日誌可能輸出到 stdout"
echo "   - Docker 標準日誌包含了應用的所有輸出"
echo "   - 檢查應用的日誌配置，確保日誌寫入到檔案"
echo ""
echo "發送日誌檔案:"
echo "   請將 docker_logs_${TIMESTAMP}.log 檔案發送給開發者"
if [ -f "tradingagents.log_${TIMESTAMP}" ]; then
    echo "   以及 tradingagents.log_${TIMESTAMP} 檔案"
fi
