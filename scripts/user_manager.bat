@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🔧 TradingAgents-CN 用戶密碼管理工具
echo ================================================

REM 檢查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到Python，請確保Python已安裝並添加到PATH
    pause
    exit /b 1
)

REM 獲取腳本目錄
set "SCRIPT_DIR=%~dp0"
set "MANAGER_SCRIPT=%SCRIPT_DIR%user_password_manager.py"

REM 檢查管理腳本是否存在
if not exist "%MANAGER_SCRIPT%" (
    echo ❌ 錯誤: 找不到用戶管理腳本 %MANAGER_SCRIPT%
    pause
    exit /b 1
)

REM 如果没有參數，顯示幫助
if "%~1"=="" (
    echo.
    echo 使用方法:
    echo   %~nx0 list                              - 列出所有用戶
    echo   %~nx0 change-password [用戶名] [新密碼]   - 修改用戶密碼
    echo   %~nx0 create-user [用戶名] [密碼] [角色]   - 創建新用戶
    echo   %~nx0 delete-user [用戶名]               - 刪除用戶
    echo   %~nx0 reset                             - 重置為默認配置
    echo.
    echo 示例:
    echo   %~nx0 list
    echo   %~nx0 change-password admin newpass123
    echo   %~nx0 create-user testuser pass123 user
    echo   %~nx0 delete-user testuser
    echo   %~nx0 reset
    echo.
    pause
    exit /b 0
)

REM 執行Python腳本
python "%MANAGER_SCRIPT%" %*

REM 如果有錯誤，暂停顯示
if errorlevel 1 (
    echo.
    echo 按任意键繼续...
    pause >nul
)