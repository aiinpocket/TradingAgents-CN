#!/bin/bash
# TradingAgents-CN 智能Docker啟動腳本 (Linux/Mac Bash版本)
# 功能：自動判斷是否需要重新構建Docker鏡像
# 使用：chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh
# 
# 判斷逻辑：
# 1. 檢查是否存在tradingagents-cn鏡像
# 2. 如果鏡像不存在 -> 執行構建啟動
# 3. 如果鏡像存在但代碼有變化 -> 執行構建啟動  
# 4. 如果鏡像存在且代碼無變化 -> 快速啟動

echo "=== TradingAgents-CN Docker 智能啟動腳本 ==="
echo "適用環境: Linux/Mac Bash"

# 檢查是否有鏡像
if docker images | grep -q "tradingagents-cn"; then
    echo "✅ 發現現有鏡像"
    
    # 檢查代碼是否有變化
    if git diff --quiet HEAD~1 HEAD -- . ':!*.md' ':!docs/' ':!scripts/'; then
        echo "📦 代碼無變化，使用快速啟動"
        docker-compose up -d
    else
        echo "🔄 檢測到代碼變化，重新構建"
        docker-compose up -d --build
    fi
else
    echo "🏗️ 首次運行，構建鏡像"
    docker-compose up -d --build
fi

echo "🚀 啟動完成！"
echo "Web界面: http://localhost:8501"
echo "Redis管理: http://localhost:8081"