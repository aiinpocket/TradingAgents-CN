@echo off
REM pip - 

echo  pip
echo ================

echo.
echo 1. pip
python -m pip install --upgrade pip

echo.
echo 2. 
python -m pip install pymongo redis pandas requests

echo.
echo 3. 
python -m pip list

echo.
echo 4. pip
python -m pip config list

echo.
echo  !
pause
