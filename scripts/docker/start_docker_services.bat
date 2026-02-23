@echo off
chcp 65001 >nul
REM TradingAgents Docker服務啟動指令碼
REM 啟動MongoDB、Redis和Redis Commander

echo ========================================
echo TradingAgents Docker Service Startup
echo ========================================

REM 從環境變數讀取密碼，未設定時使用預設值
if "%DB_PASSWORD%"=="" set DB_PASSWORD=changeme
if "%DB_PASSWORD%"=="changeme" (
    echo.
    echo [WARNING] DB_PASSWORD 未設定，使用預設密碼 changeme
    echo 建議設定安全密碼: set DB_PASSWORD=your_secure_password
    echo.
)

REM 檢查Docker是否執行
echo Checking Docker service status...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running or not installed
    echo Please start Docker Desktop first
    pause
    exit /b 1
)
echo [OK] Docker service is running

echo.
echo Starting database services...

REM 啟動MongoDB
echo Starting MongoDB...
docker run -d ^
    --name tradingagents-mongodb ^
    -p 27017:27017 ^
    -e MONGO_INITDB_ROOT_USERNAME=admin ^
    -e MONGO_INITDB_ROOT_PASSWORD=%DB_PASSWORD% ^
    -e MONGO_INITDB_DATABASE=tradingagents ^
    -v mongodb_data:/data/db ^
    --restart unless-stopped ^
    mongo:7.0

if %errorlevel% equ 0 (
    echo [OK] MongoDB started successfully - Port: 27017
) else (
    echo [WARN] MongoDB may already be running or failed to start
)

REM 啟動Redis
echo Starting Redis...
docker run -d ^
    --name tradingagents-redis ^
    -p 6379:6379 ^
    -v redis_data:/data ^
    --restart unless-stopped ^
    redis:latest redis-server --appendonly yes --requirepass %DB_PASSWORD%

if %errorlevel% equ 0 (
    echo [OK] Redis started successfully - Port: 6379
) else (
    echo [WARN] Redis may already be running or failed to start
)

REM 等待服務啟動
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

REM 啟動Redis Commander (可選的Redis管理介面)
echo Starting Redis Commander...
docker run -d ^
    --name tradingagents-redis-commander ^
    -p 8081:8081 ^
    -e REDIS_HOSTS=local:tradingagents-redis:6379:0:%DB_PASSWORD% ^
    --link tradingagents-redis:redis ^
    --restart unless-stopped ^
    rediscommander/redis-commander:latest

if %errorlevel% equ 0 (
    echo [OK] Redis Commander started - Access: http://localhost:8081
) else (
    echo [WARN] Redis Commander may already be running or failed to start
)

echo.
echo Checking service status...
docker ps --filter "name=tradingagents-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ========================================
echo Docker services startup completed!
echo ========================================
echo.
echo MongoDB:
echo    - Connection: mongodb://admin:%DB_PASSWORD%@localhost:27017/tradingagents
echo    - Port: 27017
echo    - Username: admin
echo    - Password: %DB_PASSWORD%
echo.
echo Redis:
echo    - Connection: redis://localhost:6379
echo    - Port: 6379
echo    - Password: %DB_PASSWORD%
echo.
echo Redis Commander:
echo    - Web Interface: http://localhost:8081
echo.
echo Tips:
echo    - Use stop_docker_services.bat to stop all services
echo    - Use docker logs [container_name] to view logs
echo    - Data will be persisted in Docker volumes
echo.

pause
