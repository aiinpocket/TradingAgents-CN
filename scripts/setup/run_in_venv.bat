@echo off
REM 在虛擬環境中運行Python腳本的通用腳本

if "%1"=="" (
    echo 用法: run_in_venv.bat ^<python_script^> [參數...]
    echo 示例: run_in_venv.bat scripts\setup\initialize_system.py
    pause
    exit /b 1
)

echo 🐍 在虛擬環境中運行: %*
echo ================================

REM 檢查虛擬環境
if not exist "env\Scripts\activate.bat" (
    echo ❌ 虛擬環境不存在: env\Scripts\activate.bat
    echo 💡 請先創建虛擬環境:
    echo    python -m venv env
    pause
    exit /b 1
)

REM 激活虛擬環境並運行腳本
call env\Scripts\activate.bat && python %*

echo.
echo 🎯 腳本執行完成
pause
