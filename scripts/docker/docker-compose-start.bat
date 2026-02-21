@echo off
REM TradingAgents Docker Compose啟動腳本
REM 使用Docker Compose管理所有服務

echo ========================================
echo TradingAgents Docker Compose啟動腳本
echo ========================================

REM 檢查Docker Compose是否可用
echo 檢查Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose未安裝或不可用
    echo 請安裝Docker Desktop或Docker Compose
    pause
    exit /b 1
)
echo ✅ Docker Compose可用

echo.
echo 🚀 啟動TradingAgents服務棧...

REM 啟動核心服務 (MongoDB, Redis, Redis Commander)
echo 📊 啟動核心數據庫服務...
docker-compose up -d mongodb redis redis-commander

if %errorlevel% equ 0 (
    echo ✅ 核心服務啟動成功
) else (
    echo ❌ 核心服務啟動失敗
    pause
    exit /b 1
)

REM 等待服務啟動
echo ⏳ 等待服務啟動和健康檢查...
timeout /t 10 /nobreak >nul

REM 檢查服務狀態
echo 📋 檢查服務狀態...
docker-compose ps

echo.
echo 🔍 等待健康檢查完成...
:healthcheck_loop
docker-compose ps --filter "health=healthy" | findstr "tradingagents" >nul
if %errorlevel% neq 0 (
    echo ⏳ 等待服務健康檢查...
    timeout /t 5 /nobreak >nul
    goto healthcheck_loop
)

echo ✅ 所有服務健康檢查通過

echo.
echo 📊 服務訪問信息:
echo ========================================
echo 🗄️ MongoDB:
echo    - 連接地址: mongodb://admin:tradingagents123@localhost:27017/tradingagents
echo    - 端口: 27017
echo    - 用戶名: admin
echo    - 密碼: tradingagents123
echo.
echo 📦 Redis:
echo    - 連接地址: redis://localhost:6379
echo    - 端口: 6379
echo    - 密碼: tradingagents123
echo.
echo 🖥️ 管理界面:
echo    - Redis Commander: http://localhost:8081
echo    - Mongo Express: http://localhost:8082 (可選，需要啟動)
echo.

REM 詢問是否啟動管理界面
set /p start_management="是否啟動Mongo Express管理界面? (y/N): "
if /i "%start_management%"=="y" (
    echo 🖥️ 啟動Mongo Express...
    docker-compose --profile management up -d mongo-express
    if %errorlevel% equ 0 (
        echo ✅ Mongo Express啟動成功: http://localhost:8082
        echo    用戶名: admin, 密碼: tradingagents123
    ) else (
        echo ❌ Mongo Express啟動失敗
    )
)

echo.
echo 💡 管理命令:
echo ========================================
echo 查看日誌: docker-compose logs [服務名]
echo 停止服務: docker-compose down
echo 重啟服務: docker-compose restart [服務名]
echo 查看狀態: docker-compose ps
echo 進入容器: docker-compose exec [服務名] bash
echo.
echo 🔧 數據庫初始化:
echo 運行初始化腳本: python scripts/init_database.py
echo.
echo 🌐 啟動Web應用:
echo python start_web.py
echo.

echo ========================================
echo 🎉 TradingAgents服務棧啟動完成！
echo ========================================

pause
