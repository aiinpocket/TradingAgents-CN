# TradingAgents 目錄初始化腳本 (PowerShell版本)
# 建立Docker容器需要的本機目錄結構

Write-Host "TradingAgents 目錄初始化" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

# 取得專案根目錄
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "專案根目錄: $ProjectRoot" -ForegroundColor Cyan

# 建立必要的目錄
$Directories = @(
    "logs",
    "data",
    "data\cache",
    "data\exports",
    "data\temp",
    "config",
    "config\runtime"
)

Write-Host ""
Write-Host "建立目錄結構..." -ForegroundColor Yellow

foreach ($dir in $Directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "建立目錄: $dir" -ForegroundColor Green
    } else {
        Write-Host "目錄已存在: $dir" -ForegroundColor Gray
    }
}

# 建立 .gitkeep 檔案保持目錄結構
Write-Host ""
Write-Host "建立 .gitkeep 檔案..." -ForegroundColor Yellow

$GitkeepDirs = @(
    "logs",
    "data\cache",
    "data\exports",
    "data\temp",
    "config\runtime"
)

foreach ($dir in $GitkeepDirs) {
    $gitkeepFile = Join-Path $dir ".gitkeep"
    if (-not (Test-Path $gitkeepFile)) {
        New-Item -ItemType File -Path $gitkeepFile -Force | Out-Null
        Write-Host "建立: $gitkeepFile" -ForegroundColor Green
    }
}

# 建立日誌配置檔案
Write-Host ""
Write-Host "建立日誌配置檔案..." -ForegroundColor Yellow

$LogConfigFile = "config\logging.toml"
if (-not (Test-Path $LogConfigFile)) {
    $LogConfigContent = @'
# TradingAgents 日誌配置檔案
[logging]
version = 1
disable_existing_loggers = false

[logging.formatters.standard]
format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"

[logging.formatters.detailed]
format = "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"

[logging.handlers.console]
class = "logging.StreamHandler"
level = "INFO"
formatter = "standard"
stream = "ext://sys.stdout"

[logging.handlers.file]
class = "logging.handlers.RotatingFileHandler"
level = "DEBUG"
formatter = "detailed"
filename = "/app/logs/tradingagents.log"
maxBytes = 104857600  # 100MB
backupCount = 5
encoding = "utf8"

[logging.handlers.error_file]
class = "logging.handlers.RotatingFileHandler"
level = "ERROR"
formatter = "detailed"
filename = "/app/logs/tradingagents_error.log"
maxBytes = 52428800  # 50MB
backupCount = 3
encoding = "utf8"

[logging.loggers.tradingagents]
level = "DEBUG"
handlers = ["console", "file", "error_file"]
propagate = false

[logging.loggers.streamlit]
level = "INFO"
handlers = ["console", "file"]
propagate = false

[logging.loggers.yfinance]
level = "WARNING"
handlers = ["file"]
propagate = false

[logging.loggers.finnhub]
level = "WARNING"
handlers = ["file"]
propagate = false

[logging.root]
level = "INFO"
handlers = ["console", "file"]
'@

    Set-Content -Path $LogConfigFile -Value $LogConfigContent -Encoding UTF8
    Write-Host "建立日誌配置: $LogConfigFile" -ForegroundColor Green
} else {
    Write-Host "日誌配置已存在: $LogConfigFile" -ForegroundColor Gray
}

# 更新 .gitignore 檔案
Write-Host ""
Write-Host "更新 .gitignore 檔案..." -ForegroundColor Yellow

$GitignoreEntries = @(
    "# 日誌檔案",
    "logs/*.log",
    "logs/*.log.*",
    "",
    "# 資料快取",
    "data/cache/*",
    "data/temp/*",
    "!data/cache/.gitkeep",
    "!data/temp/.gitkeep",
    "",
    "# 執行時配置",
    "config/runtime/*",
    "!config/runtime/.gitkeep",
    "",
    "# 匯出檔案",
    "data/exports/*.pdf",
    "data/exports/*.docx",
    "data/exports/*.xlsx",
    "!data/exports/.gitkeep"
)

# 檢查 .gitignore 是否存在
if (-not (Test-Path ".gitignore")) {
    New-Item -ItemType File -Path ".gitignore" -Force | Out-Null
}

# 讀取現有的 .gitignore 內容
$existingContent = Get-Content ".gitignore" -ErrorAction SilentlyContinue

# 新增條目到 .gitignore（如果不存在）
$newEntries = @()
foreach ($entry in $GitignoreEntries) {
    if ($entry -ne "" -and $existingContent -notcontains $entry) {
        $newEntries += $entry
    }
}

if ($newEntries.Count -gt 0) {
    Add-Content -Path ".gitignore" -Value $newEntries
}

Write-Host "更新 .gitignore 檔案" -ForegroundColor Green

# 建立 README 檔案
Write-Host ""
Write-Host "建立目錄說明檔案..." -ForegroundColor Yellow

$ReadmeFile = "logs\README.md"
if (-not (Test-Path $ReadmeFile)) {
    $ReadmeContent = @'
# TradingAgents 日誌目錄

此目錄用於儲存 TradingAgents 應用的日誌檔案。

## 日誌檔案說明

- `tradingagents.log` - 主應用日誌檔案
- `tradingagents_error.log` - 錯誤日誌檔案
- `tradingagents.log.1`, `tradingagents.log.2` 等 - 輪轉的歷史日誌檔案

## 日誌級別

- **DEBUG** - 詳細的除錯資訊
- **INFO** - 一般資訊
- **WARNING** - 警告資訊
- **ERROR** - 錯誤資訊
- **CRITICAL** - 嚴重錯誤

## 日誌輪轉

- 主日誌檔案最大 100MB，保留 5 個歷史檔案
- 錯誤日誌檔案最大 50MB，保留 3 個歷史檔案

## 取得日誌

如果遇到問題需要發送日誌給開發者，請發送：
1. `tradingagents.log` - 主日誌檔案
2. `tradingagents_error.log` - 錯誤日誌檔案（如果存在）

## Docker 環境

在 Docker 環境中，此目錄映射到容器內的 `/app/logs` 目錄。
'@

    Set-Content -Path $ReadmeFile -Value $ReadmeContent -Encoding UTF8
    Write-Host "建立日誌說明: $ReadmeFile" -ForegroundColor Green
}

# 顯示目錄結構
Write-Host ""
Write-Host "目錄結構預覽:" -ForegroundColor Cyan
Write-Host "=================="

function Show-DirectoryTree {
    param([string]$Path = ".", [int]$Level = 0, [int]$MaxLevel = 3)

    if ($Level -gt $MaxLevel) { return }

    $items = Get-ChildItem $Path | Where-Object {
        $_.Name -notlike ".git*" -and
        $_.Name -notlike "__pycache__*" -and
        $_.Name -notlike "*.pyc"
    } | Sort-Object @{Expression={$_.PSIsContainer}; Descending=$true}, Name

    foreach ($item in $items) {
        $indent = "  " * $Level
        $prefix = if ($item.PSIsContainer) { "[DIR]" } else { "[FILE]" }
        Write-Host "$indent$prefix $($item.Name)" -ForegroundColor Gray

        if ($item.PSIsContainer -and $Level -lt $MaxLevel) {
            Show-DirectoryTree -Path $item.FullName -Level ($Level + 1) -MaxLevel $MaxLevel
        }
    }
}

Show-DirectoryTree

Write-Host ""
Write-Host "目錄初始化完成!" -ForegroundColor Green
Write-Host ""
Write-Host "接下來的步驟:" -ForegroundColor Yellow
Write-Host "1. 執行 Docker Compose: docker-compose up -d" -ForegroundColor Gray
Write-Host "2. 檢查日誌檔案: Get-ChildItem logs\" -ForegroundColor Gray
Write-Host "3. 即時查看日誌: Get-Content logs\tradingagents.log -Wait" -ForegroundColor Gray
Write-Host ""
Write-Host "重要目錄說明:" -ForegroundColor Cyan
Write-Host "   logs\     - 應用日誌檔案" -ForegroundColor Gray
Write-Host "   data\     - 資料快取和匯出檔案" -ForegroundColor Gray
Write-Host "   config\   - 執行時配置檔案" -ForegroundColor Gray
Write-Host ""
Write-Host "查看日誌的PowerShell命令:" -ForegroundColor Yellow
Write-Host "   Get-Content logs\tradingagents.log -Tail 50" -ForegroundColor Gray
Write-Host "   Get-Content logs\tradingagents.log -Wait" -ForegroundColor Gray
