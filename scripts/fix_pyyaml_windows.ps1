# Windows PyYAML 編譯錯誤快速修復腳本
#
# 問題: PyYAML 在 Windows 上安裝時出現 "AttributeError: cython_sources" 錯誤
# 原因: PyYAML 需要編譯，但缺少 C 編譯器或 Cython 相依套件
#
# 使用方法:
#   .\scripts\fix_pyyaml_windows.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "Windows PyYAML 編譯錯誤修復腳本" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan

# 檢查 Python 環境
Write-Host "`n檢查 Python 環境..." -ForegroundColor Yellow
$pythonCmd = if (Test-Path ".\.venv\Scripts\python.exe") {
    ".\.venv\Scripts\python"
} else {
    "python"
}

try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "Python 版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "未找到 Python，請先安裝 Python 3.10+" -ForegroundColor Red
    exit 1
}

# 升級 pip、setuptools、wheel
Write-Host "`n升級 pip、setuptools、wheel..." -ForegroundColor Yellow
$upgradeCmd = "$pythonCmd -m pip install --upgrade pip setuptools wheel"
Write-Host "執行: $upgradeCmd" -ForegroundColor Gray
Invoke-Expression $upgradeCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "升級失敗" -ForegroundColor Red
    exit 1
}

# 安裝專案相依套件（使用 --only-binary 避免編譯 PyYAML）
Write-Host "`n安裝專案相依套件（使用預編譯套件）..." -ForegroundColor Yellow
$installCmd = "$pythonCmd -m pip install -e . --only-binary pyyaml"
Write-Host "執行: $installCmd" -ForegroundColor Gray
Write-Host "使用 --only-binary pyyaml 避免編譯錯誤" -ForegroundColor Cyan

$startTime = Get-Date
Invoke-Expression $installCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n專案相依套件安裝失敗" -ForegroundColor Red
    Write-Host "`n請查看錯誤資訊，或在 GitHub Issues 中回報" -ForegroundColor Yellow
    exit 1
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "安裝完成!" -ForegroundColor Green
Write-Host "耗時: $($duration.TotalSeconds) 秒" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan

# 驗證安裝
Write-Host "`n驗證安裝..." -ForegroundColor Yellow
$verifyCmd = "$pythonCmd -c `"import yaml; import tradingagents; print('驗證成功')`""
try {
    Invoke-Expression $verifyCmd
} catch {
    Write-Host "驗證失敗，但安裝可能已完成" -ForegroundColor Yellow
}

# 顯示後續步驟
Write-Host "`n後續步驟:" -ForegroundColor Yellow
Write-Host "  1. 複製 .env.example 為 .env 並配置 API Key" -ForegroundColor White
Write-Host "  2. 執行 Web 介面: streamlit run web/main.py" -ForegroundColor White
Write-Host "  3. 或使用 CLI: python -m cli.main" -ForegroundColor White

Write-Host "`n祝使用愉快!" -ForegroundColor Green

