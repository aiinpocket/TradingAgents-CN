@echo off
REM 安裝必要的 Python 套件

echo 安裝 TradingAgents 必要的 Python 套件
echo =====================================

echo.
echo 升級 pip (避免安裝錯誤)...
python -m pip install --upgrade pip

echo.
echo 安裝 pymongo...
python -m pip install pymongo

echo.
echo 安裝 redis...
python -m pip install redis

echo.
echo 安裝其他常用套件...
python -m pip install pandas requests

echo.
echo 檢查已安裝的套件...
python -m pip list | findstr -i "pymongo redis pandas"

echo.
echo 套件安裝完成!
echo.
echo 下一步運行:
echo    python scripts\setup\initialize_system.py
echo.

pause
