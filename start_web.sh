#!/bin/bash
# TradingAgents-CN Web 啟動腳本
# 此腳本已棄用，請直接使用 python start_app.py

echo "TradingAgents-CN Web 啟動中..."
echo

# 啟用虛擬環境
source env/bin/activate

# 安裝套件（如未安裝）
if ! python -c "import tradingagents" 2>/dev/null; then
    echo "安裝套件..."
    pip install -e .
fi

# 啟動 FastAPI 應用
python start_app.py

echo "應用已停止"
read -n 1
