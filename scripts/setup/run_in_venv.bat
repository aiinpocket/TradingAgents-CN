@echo off
REM Python

if "%1"=="" (
echo : run_in_venv.bat ^<python_script^> [...]
echo : run_in_venv.bat scripts\setup\initialize_system.py
pause
exit /b 1
)

echo  : %*
echo ================================

REM 
if not exist "env\Scripts\activate.bat" (
echo  : env\Scripts\activate.bat
echo  :
echo    python -m venv env
pause
exit /b 1
)

REM 
call env\Scripts\activate.bat && python %*

echo.
echo  
pause
