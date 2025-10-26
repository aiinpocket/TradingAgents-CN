#!/bin/bash
# TradingAgents Docker 啟動腳本
# 自動創建必要目錄並啟動Docker容器

echo "🚀 TradingAgents Docker 啟動"
echo "=========================="

# 檢查Docker是否運行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker未運行，請先啟動Docker"
    exit 1
fi

# 檢查docker-compose是否可用
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ docker-compose未安裝"
    exit 1
fi

# 創建logs目錄
echo "📁 創建logs目錄..."
mkdir -p logs
chmod 755 logs 2>/dev/null || true
echo "✅ logs目錄準备完成"

# 檢查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️ .env文件不存在"
    if [ -f ".env.example" ]; then
        echo "📋 複制.env.example到.env"
        cp .env.example .env
        echo "✅ 請編辑.env文件配置API密鑰"
    else
        echo "❌ .env.example文件也不存在"
        exit 1
    fi
fi

# 顯示當前配置
echo ""
echo "📋 當前配置:"
echo "   項目目錄: $(pwd)"
echo "   日誌目錄: $(pwd)/logs"
echo "   配置文件: .env"

# 啟動Docker容器
echo ""
echo "🐳 啟動Docker容器..."
docker-compose up -d

# 檢查啟動狀態
echo ""
echo "📊 檢查容器狀態..."
docker-compose ps

# 等待服務啟動
echo ""
echo "⏳ 等待服務啟動..."
sleep 10

# 檢查Web服務
echo ""
echo "🌐 檢查Web服務..."
if curl -s http://localhost:8501/_stcore/health >/dev/null 2>&1; then
    echo "✅ Web服務正常運行"
    echo "🌐 訪問地址: http://localhost:8501"
else
    echo "⚠️ Web服務可能还在啟動中..."
    echo "💡 請稍等片刻後訪問: http://localhost:8501"
fi

# 顯示日誌信息
echo ""
echo "📋 日誌信息:"
echo "   日誌目錄: ./logs/"
echo "   實時查看: tail -f logs/tradingagents.log"
echo "   Docker日誌: docker-compose logs -f web"

echo ""
echo "🎉 啟動完成！"
echo ""
echo "💡 常用命令:"
echo "   查看狀態: docker-compose ps"
echo "   查看日誌: docker-compose logs -f web"
echo "   停止服務: docker-compose down"
echo "   重啟服務: docker-compose restart web"
