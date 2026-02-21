@echo off
REM .gitignoreGitAI

echo  Git
echo ========================

echo.
echo  .gitignore:
echo .trae.augment.gitignore...

findstr /C:".trae/" .gitignore >nul
if %errorlevel%==0 (
echo  .trae/ .gitignore
) else (
echo  .trae/ .gitignore
)

findstr /C:".augment/" .gitignore >nul
if %errorlevel%==0 (
echo  .augment/ .gitignore
) else (
echo  .augment/ .gitignore
)

echo.
echo  Git...

REM .traeGit
git ls-files .trae/ >nul 2>&1
if %errorlevel%==0 (
echo  .traeGit
echo  Git.trae...
git rm -r --cached .trae/
if %errorlevel%==0 (
echo  .traeGit
) else (
echo  .trae
)
) else (
echo  .traeGit
)

REM .augmentGit
git ls-files .augment/ >nul 2>&1
if %errorlevel%==0 (
echo  .augmentGit
echo  Git.augment...
git rm -r --cached .augment/
if %errorlevel%==0 (
echo  .augmentGit
) else (
echo  .augment
)
) else (
echo  .augmentGit
)

echo.
echo  Git...
git status --porcelain | findstr -E "\.(trae|augment)" >nul
if %errorlevel%==0 (
echo  AI
echo  :
git status --porcelain | findstr -E "\.(trae|augment)"
) else (
echo  AI
)

echo.
echo  :
echo 1. .trae/  .augment/ .gitignore
echo 2. AI
echo 3. Git
echo 4. AI
echo.
echo  
echo.

pause
