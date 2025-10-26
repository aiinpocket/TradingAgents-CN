@echo off
echo 🚀 啟動TradingAgents-CN Web應用...
echo.

REM 激活虛擬環境
call env\Scripts\activate.bat

REM 檢查項目是否已安裝
python -c "import tradingagents" 2>nul
if errorlevel 1 (
    echo 📦 安裝項目到虛擬環境...
    pip install -e .
)

REM 啟動Streamlit應用
python start_web.py

pause
