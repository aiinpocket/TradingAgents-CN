#!/bin/bash
# TradingAgents-CN Web應用啟動腳本

echo "🚀 啟動TradingAgents-CN Web應用..."
echo

# 激活虛擬環境
source env/bin/activate

# 檢查項目是否已安裝
if ! python -c "import tradingagents" 2>/dev/null; then
    echo "📦 安裝項目到虛擬環境..."
    pip install -e .
fi

# 啟動Streamlit應用
python start_web.py

echo "按任意键退出..."
read -n 1
