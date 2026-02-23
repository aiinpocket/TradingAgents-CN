@echo off
echo ========================================
echo Starting Debug MongoDB and Redis
echo ========================================

REM 從環境變數讀取密碼，未設定時使用預設值
if "%DB_PASSWORD%"=="" set DB_PASSWORD=changeme
if "%DB_PASSWORD%"=="changeme" (
    echo.
    echo [WARNING] DB_PASSWORD 未設定，使用預設密碼 changeme
    echo 建議設定安全密碼: set DB_PASSWORD=your_secure_password
    echo.
)

echo Checking Docker...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Cleaning up existing containers...
docker stop tradingagents-mongodb tradingagents-redis 2>nul
docker rm tradingagents-mongodb tradingagents-redis 2>nul

echo Starting MongoDB on port 27017...
docker run -d ^
    --name tradingagents-mongodb ^
    -p 27017:27017 ^
    -e MONGO_INITDB_ROOT_USERNAME=admin ^
    -e MONGO_INITDB_ROOT_PASSWORD=%DB_PASSWORD% ^
    -e MONGO_INITDB_DATABASE=tradingagents ^
    --restart unless-stopped ^
    mongo:7.0

if %errorlevel% equ 0 (
    echo [OK] MongoDB started successfully
) else (
    echo [ERROR] MongoDB failed to start
)

echo Starting Redis on port 6379...
docker run -d ^
    --name tradingagents-redis ^
    -p 6379:6379 ^
    --restart unless-stopped ^
    redis:latest redis-server --appendonly yes --requirepass %DB_PASSWORD%

if %errorlevel% equ 0 (
    echo [OK] Redis started successfully
) else (
    echo [ERROR] Redis failed to start
)

echo Waiting 10 seconds for services to start...
timeout /t 10 /nobreak >nul

echo.
echo Service Status:
docker ps --filter "name=tradingagents-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ========================================
echo Debug Services Started!
echo ========================================
echo MongoDB: localhost:27017
echo   Username: admin
echo   Password: %DB_PASSWORD%
echo   Database: tradingagents
echo.
echo Redis: localhost:6379
echo   Password: %DB_PASSWORD%
echo.
echo To stop services: docker stop tradingagents-mongodb tradingagents-redis
echo.

pause
