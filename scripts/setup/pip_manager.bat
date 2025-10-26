@echo off
REM pip管理腳本 - 使用國內鏡像

echo 🔧 pip管理工具
echo ================

echo.
echo 1. 升級pip
python -m pip install --upgrade pip

echo.
echo 2. 安裝常用包
python -m pip install pymongo redis pandas requests

echo.
echo 3. 顯示已安裝包
python -m pip list

echo.
echo 4. 檢查pip配置
python -m pip config list

echo.
echo ✅ 完成!
pause
