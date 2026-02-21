@echo off
REM Python

echo  TradingAgentsPython
echo ===============================================

echo.
echo  : %CD%
echo  ...

REM 
if not exist "env\Scripts\activate.bat" (
echo  : env\Scripts\activate.bat
echo  :
echo    python -m venv env
echo    env\Scripts\activate.bat
pause
exit /b 1
)

REM 
call env\Scripts\activate.bat

echo  
echo  Python: 
where python

echo.
echo  pip:
python -m pip --version

echo.
echo  pip...
python -m pip install --upgrade pip

echo.
echo  pymongo...
python -m pip install pymongo

echo.
echo  redis...
python -m pip install redis

echo.
echo ...
python -m pip install pandas requests

echo.
echo  ...
python -m pip list | findstr -i "pymongo redis pandas"

echo.
echo  ...
python -c "
try:
import pymongo
print(' pymongo ')
except ImportError as e:
print(' pymongo :', e)

try:
import redis
print(' redis ')
except ImportError as e:
print(' redis :', e)

try:
import pandas
print(' pandas ')
except ImportError as e:
print(' pandas :', e)
"

echo.
echo  !
echo.
echo  :
echo 1. 
echo 2. :
echo    python scripts\setup\initialize_system.py
echo 3. :
echo    python scripts\validation\check_system_status.py
echo.
echo  :
echo - : env\Scripts\activate.bat
echo - : deactivate
echo.

pause
