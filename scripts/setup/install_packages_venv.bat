@echo off
REM 在虛擬環境中安裝必要的Python包

echo 🔧 在虛擬環境中安裝TradingAgents必要的Python包
echo ===============================================

echo.
echo 📍 項目目錄: %CD%
echo 🐍 激活虛擬環境...

REM 檢查虛擬環境是否存在
if not exist "env\Scripts\activate.bat" (
    echo ❌ 虛擬環境不存在: env\Scripts\activate.bat
    echo 💡 請先創建虛擬環境:
    echo    python -m venv env
    echo    env\Scripts\activate.bat
    pause
    exit /b 1
)

REM 激活虛擬環境
call env\Scripts\activate.bat

echo ✅ 虛擬環境已激活
echo 📦 Python路徑: 
where python

echo.
echo 📊 當前pip版本:
python -m pip --version

echo.
echo 升級 pip...
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
echo 📊 檢查已安裝的包...
python -m pip list | findstr -i "pymongo redis pandas"

echo.
echo 🧪 測試包導入...
python -c "
try:
    import pymongo
    print('✅ pymongo 導入成功')
except ImportError as e:
    print('❌ pymongo 導入失敗:', e)

try:
    import redis
    print('✅ redis 導入成功')
except ImportError as e:
    print('❌ redis 導入失敗:', e)

try:
    import pandas
    print('✅ pandas 導入成功')
except ImportError as e:
    print('❌ pandas 導入失敗:', e)
"

echo.
echo ✅ 包安裝完成!
echo.
echo 💡 提示:
echo 1. 虛擬環境已激活，可以繼續運行其他腳本
echo 2. 下一步運行:
echo    python scripts\setup\initialize_system.py
echo 3. 或檢查系統狀態:
echo    python scripts\validation\check_system_status.py
echo.
echo 🎯 虛擬環境使用說明:
echo - 激活: env\Scripts\activate.bat
echo - 退出: deactivate
echo.

pause
