# TradingAgents Docker日誌取得工具 (PowerShell版本)

Write-Host "TradingAgents Docker日誌取得工具" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# 查找容器
$ContainerNames = @("tradingagents-data-service", "tradingagents_data-service_1", "data-service", "tradingagents-cn-data-service-1")
$Container = $null

foreach ($name in $ContainerNames) {
    $result = docker ps --filter "name=$name" --format "{{.Names}}" 2>$null
    if ($result -and $result.Trim() -eq $name) {
        $Container = $name
        Write-Host "找到容器: $Container" -ForegroundColor Green
        break
    }
}

if (-not $Container) {
    Write-Host "未找到TradingAgents容器" -ForegroundColor Red
    Write-Host "目前執行的容器:" -ForegroundColor Yellow
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    Write-Host ""
    $Container = Read-Host "請輸入容器名稱"
    if (-not $Container) {
        Write-Host "未提供容器名稱，退出" -ForegroundColor Red
        exit 1
    }
}

# 建立時間戳記
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host ""
Write-Host "取得日誌資訊..." -ForegroundColor Cyan

# 1. 取得Docker標準日誌
Write-Host "1. 取得Docker標準日誌..." -ForegroundColor Yellow
$DockerLogFile = "docker_logs_$Timestamp.log"
docker logs $Container > $DockerLogFile 2>&1
Write-Host "Docker日誌已儲存到: $DockerLogFile" -ForegroundColor Green

# 2. 查找容器內日誌檔案
Write-Host ""
Write-Host "2. 查找容器內日誌檔案..." -ForegroundColor Yellow
$LogFiles = docker exec $Container find /app -name "*.log" -type f 2>$null

if ($LogFiles) {
    Write-Host "找到以下日誌檔案:" -ForegroundColor Cyan
    $LogFiles | ForEach-Object { Write-Host "   $_" }

    # 複製每個日誌檔案
    Write-Host ""
    Write-Host "3. 複製日誌檔案到本機..." -ForegroundColor Yellow
    $LogFiles | ForEach-Object {
        if ($_.Trim()) {
            $LogFile = $_.Trim()
            $FileName = Split-Path $LogFile -Leaf
            $LocalFile = "${FileName}_$Timestamp"

            Write-Host "複製: $LogFile -> $LocalFile" -ForegroundColor Cyan
            $result = docker cp "${Container}:$LogFile" $LocalFile 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "成功複製: $LocalFile" -ForegroundColor Green

                # 顯示檔案資訊
                if (Test-Path $LocalFile) {
                    $FileInfo = Get-Item $LocalFile
                    $Lines = (Get-Content $LocalFile | Measure-Object -Line).Lines
                    Write-Host "   檔案大小: $($FileInfo.Length) 位元組, $Lines 行" -ForegroundColor Gray
                }
            } else {
                Write-Host "複製失敗: $LogFile" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "未在容器中找到.log檔案" -ForegroundColor Yellow
}

# 3. 取得容器內應用目錄資訊
Write-Host ""
Write-Host "4. 檢查應用目錄結構..." -ForegroundColor Yellow
Write-Host "/app 目錄內容:" -ForegroundColor Cyan
$AppDir = docker exec $Container ls -la /app/ 2>$null
if ($AppDir) {
    $AppDir | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "無法存取/app目錄" -ForegroundColor Red
}

Write-Host ""
Write-Host "查找所有可能的日誌檔案:" -ForegroundColor Cyan
$AllLogFiles = docker exec $Container find /app -name "*log*" -type f 2>$null
if ($AllLogFiles) {
    $AllLogFiles | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "未找到包含'log'的檔案" -ForegroundColor Red
}

# 4. 檢查環境變數和配置
Write-Host ""
Write-Host "5. 檢查日誌配置..." -ForegroundColor Yellow
Write-Host "環境變數:" -ForegroundColor Cyan
$EnvVars = docker exec $Container env 2>$null | Select-String -Pattern "log" -CaseSensitive:$false
if ($EnvVars) {
    $EnvVars | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "未找到日誌相關環境變數" -ForegroundColor Red
}

# 5. 取得最近的應用輸出
Write-Host ""
Write-Host "6. 取得最近的應用輸出 (最後50行):" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Gray
docker logs --tail 50 $Container 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor White }
Write-Host "==================================" -ForegroundColor Gray

Write-Host ""
Write-Host "日誌取得完成!" -ForegroundColor Green
Write-Host "產生的檔案:" -ForegroundColor Cyan
Get-ChildItem "*_$Timestamp*" 2>$null | ForEach-Object {
    Write-Host "   $($_.Name) ($($_.Length) 位元組)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "使用建議:" -ForegroundColor Yellow
Write-Host "   - 如果原始碼目錄的tradingagents.log為空，說明日誌可能輸出到stdout" -ForegroundColor Gray
Write-Host "   - Docker標準日誌包含了應用的所有輸出" -ForegroundColor Gray
Write-Host "   - 檢查應用的日誌配置，確保日誌寫入到檔案" -ForegroundColor Gray
Write-Host ""
Write-Host "傳送日誌檔案:" -ForegroundColor Cyan
Write-Host "   請將 $DockerLogFile 檔案傳送給開發者" -ForegroundColor Gray
if (Test-Path "tradingagents.log_$Timestamp") {
    Write-Host "   以及 tradingagents.log_$Timestamp 檔案" -ForegroundColor Gray
}

Write-Host ""
Write-Host "如果需要即時監控日誌，請執行:" -ForegroundColor Yellow
Write-Host "   docker logs -f $Container" -ForegroundColor Gray
