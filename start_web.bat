@echo off
echo  TradingAgents-CN Web...
echo.

REM 
call env\Scripts\activate.bat

REM 
python -c "import tradingagents" 2>nul
if errorlevel 1 (
echo  ...
pip install -e .
)

REM Streamlit
python start_web.py

pause
