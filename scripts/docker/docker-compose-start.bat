@echo off
REM TradingAgents Docker Compose
REM Docker Compose

echo ========================================
echo TradingAgents Docker Compose
echo ========================================

REM 從環境變數讀取密碼，未設定時使用預設值
if "%DB_PASSWORD%"=="" set DB_PASSWORD=changeme
if "%DB_PASSWORD%"=="changeme" (
    echo.
    echo [WARNING] DB_PASSWORD 未設定，使用預設密碼 changeme
    echo 建議設定安全密碼: set DB_PASSWORD=your_secure_password
    echo.
)

REM Docker Compose
echo Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
echo  Docker Compose
echo Docker DesktopDocker Compose
pause
exit /b 1
)
echo  Docker Compose

echo.
echo  TradingAgents...

REM  (MongoDB, Redis, Redis Commander)
echo  ...
docker-compose up -d mongodb redis redis-commander

if %errorlevel% equ 0 (
echo
) else (
echo
pause
exit /b 1
)

REM
echo  ...
timeout /t 10 /nobreak >nul

REM
echo  ...
docker-compose ps

echo.
echo  ...
:healthcheck_loop
docker-compose ps --filter "health=healthy" | findstr "tradingagents" >nul
if %errorlevel% neq 0 (
echo  ...
timeout /t 5 /nobreak >nul
goto healthcheck_loop
)

echo

echo.
echo  :
echo ========================================
echo  MongoDB:
echo    - : mongodb://admin:%DB_PASSWORD%@localhost:27017/tradingagents
echo    - : 27017
echo    - : admin
echo    - : %DB_PASSWORD%
echo.
echo  Redis:
echo    - : redis://localhost:6379
echo    - : 6379
echo    - : %DB_PASSWORD%
echo.
echo  :
echo    - Redis Commander: http://localhost:8081
echo    - Mongo Express: http://localhost:8082 ()
echo.

REM
set /p start_management="Mongo Express? (y/N): "
if /i "%start_management%"=="y" (
echo  Mongo Express...
docker-compose --profile management up -d mongo-express
if %errorlevel% equ 0 (
echo  Mongo Express: http://localhost:8082
echo    : admin, : %DB_PASSWORD%
) else (
echo  Mongo Express
)
)

echo.
echo  :
echo ========================================
echo : docker-compose logs []
echo : docker-compose down
echo : docker-compose restart []
echo : docker-compose ps
echo : docker-compose exec [] bash
echo.
echo  :
echo : python scripts/init_database.py
echo.
echo  Web:
echo python start_web.py
echo.

echo ========================================
echo  TradingAgents
echo ========================================

pause
