#!/bin/bash
# TradingAgents-CN Web

echo " TradingAgents-CN Web..."
echo

# 
source env/bin/activate

# 
if ! python -c "import tradingagents" 2>/dev/null; then
echo " ..."
pip install -e .
fi

# Streamlit
python start_web.py

echo "..."
read -n 1
