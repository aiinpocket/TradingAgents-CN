@echo off
echo TradingAgents-CN Web 啟動中...
echo.

REM 啟用虛擬環境
call env\Scripts\activate.bat

REM 安裝套件（如未安裝）
python -c "import tradingagents" 2>nul
if errorlevel 1 (
    echo 安裝套件...
    pip install -e .
)

REM 啟動 FastAPI 應用
python start_app.py

pause
