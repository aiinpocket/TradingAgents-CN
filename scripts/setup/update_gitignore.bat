@echo off
REM 更新.gitignore並從Git中移除AI工具目錄

echo 🔧 更新Git忽略規則
echo ========================

echo.
echo 📋 當前.gitignore狀態:
echo 檢查.trae和.augment目錄是否已添加到.gitignore...

findstr /C:".trae/" .gitignore >nul
if %errorlevel%==0 (
    echo ✅ .trae/ 已在.gitignore中
) else (
    echo ❌ .trae/ 不在.gitignore中
)

findstr /C:".augment/" .gitignore >nul
if %errorlevel%==0 (
    echo ✅ .augment/ 已在.gitignore中
) else (
    echo ❌ .augment/ 不在.gitignore中
)

echo.
echo 🗂️ 檢查目錄是否被Git跟蹤...

REM 檢查.trae目錄是否被Git跟蹤
git ls-files .trae/ >nul 2>&1
if %errorlevel%==0 (
    echo ⚠️ .trae目錄被Git跟蹤，需要移除
    echo 📤 從Git中移除.trae目錄...
    git rm -r --cached .trae/
    if %errorlevel%==0 (
        echo ✅ .trae目錄已從Git中移除
    ) else (
        echo ❌ 移除.trae目錄失败
    )
) else (
    echo ✅ .trae目錄未被Git跟蹤
)

REM 檢查.augment目錄是否被Git跟蹤
git ls-files .augment/ >nul 2>&1
if %errorlevel%==0 (
    echo ⚠️ .augment目錄被Git跟蹤，需要移除
    echo 📤 從Git中移除.augment目錄...
    git rm -r --cached .augment/
    if %errorlevel%==0 (
        echo ✅ .augment目錄已從Git中移除
    ) else (
        echo ❌ 移除.augment目錄失败
    )
) else (
    echo ✅ .augment目錄未被Git跟蹤
)

echo.
echo 📊 檢查Git狀態...
git status --porcelain | findstr -E "\.(trae|augment)" >nul
if %errorlevel%==0 (
    echo ⚠️ 仍有AI工具目錄相關的變更
    echo 📋 相關變更:
    git status --porcelain | findstr -E "\.(trae|augment)"
) else (
    echo ✅ 没有AI工具目錄相關的變更
)

echo.
echo 💡 說明:
echo 1. .trae/ 和 .augment/ 目錄已添加到.gitignore
echo 2. 這些目錄包含AI工具的配置和緩存文件
echo 3. 不應该提交到Git仓庫中
echo 4. 每個開發者可以有自己的AI工具配置
echo.
echo 🎯 下次提交時，這些目錄将被忽略
echo.

pause
