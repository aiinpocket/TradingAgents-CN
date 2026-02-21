# TradingAgents Docker 啟動腳本 (PowerShell版本)
# 自動建立必要目錄並啟動Docker容器

Write-Host "TradingAgents Docker 啟動" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

# 檢查Docker是否執行
try {
    docker info | Out-Null
    Write-Host "Docker執行正常" -ForegroundColor Green
} catch {
    Write-Host "Docker未執行，請先啟動Docker Desktop" -ForegroundColor Red
    exit 1
}

# 檢查docker-compose是否可用
try {
    docker-compose --version | Out-Null
    Write-Host "docker-compose可用" -ForegroundColor Green
} catch {
    Write-Host "docker-compose未安裝或不可用" -ForegroundColor Red
    exit 1
}

# 建立logs目錄
Write-Host ""
Write-Host "建立logs目錄..." -ForegroundColor Yellow
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    Write-Host "logs目錄已建立" -ForegroundColor Green
} else {
    Write-Host "logs目錄已存在" -ForegroundColor Gray
}

# 建立.gitkeep檔案
$gitkeepFile = "logs\.gitkeep"
if (-not (Test-Path $gitkeepFile)) {
    New-Item -ItemType File -Path $gitkeepFile -Force | Out-Null
    Write-Host "建立.gitkeep檔案" -ForegroundColor Green
}

# 檢查.env檔案
Write-Host ""
Write-Host "檢查配置檔案..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host ".env檔案不存在" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "已複製.env.example到.env" -ForegroundColor Green
        Write-Host "請編輯.env檔案配置API金鑰" -ForegroundColor Cyan
    } else {
        Write-Host ".env.example檔案也不存在" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ".env檔案存在" -ForegroundColor Green
}

# 顯示目前配置
Write-Host ""
Write-Host "目前配置:" -ForegroundColor Cyan
Write-Host "   專案目錄: $(Get-Location)" -ForegroundColor Gray
Write-Host "   日誌目錄: $(Join-Path (Get-Location) 'logs')" -ForegroundColor Gray
Write-Host "   配置檔案: .env" -ForegroundColor Gray

# 啟動Docker容器
Write-Host ""
Write-Host "啟動Docker容器..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker容器啟動成功" -ForegroundColor Green
} else {
    Write-Host "Docker容器啟動失敗" -ForegroundColor Red
    exit 1
}

# 檢查啟動狀態
Write-Host ""
Write-Host "檢查容器狀態..." -ForegroundColor Yellow
docker-compose ps

# 等待服務啟動
Write-Host ""
Write-Host "等待服務啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 檢查Web服務
Write-Host ""
Write-Host "檢查Web服務..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "Web服務正常執行" -ForegroundColor Green
        Write-Host "存取位址: http://localhost:8501" -ForegroundColor Cyan
    }
} catch {
    Write-Host "Web服務可能還在啟動中..." -ForegroundColor Yellow
    Write-Host "請稍等片刻後存取: http://localhost:8501" -ForegroundColor Cyan
}

# 顯示日誌資訊
Write-Host ""
Write-Host "日誌資訊:" -ForegroundColor Cyan
Write-Host "   日誌目錄: .\logs\" -ForegroundColor Gray
Write-Host "   即時查看: Get-Content logs\tradingagents.log -Wait" -ForegroundColor Gray
Write-Host "   Docker日誌: docker-compose logs -f web" -ForegroundColor Gray

# 檢查是否有日誌檔案產生
Write-Host ""
Write-Host "檢查日誌檔案..." -ForegroundColor Yellow
$logFiles = Get-ChildItem "logs\*.log" -ErrorAction SilentlyContinue
if ($logFiles) {
    Write-Host "找到日誌檔案:" -ForegroundColor Green
    foreach ($file in $logFiles) {
        $size = [math]::Round($file.Length / 1KB, 2)
        Write-Host "   $($file.Name) ($size KB)" -ForegroundColor Gray
    }
} else {
    Write-Host "日誌檔案還未產生，請稍等..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "啟動完成!" -ForegroundColor Green
Write-Host ""
Write-Host "常用命令:" -ForegroundColor Yellow
Write-Host "   查看狀態: docker-compose ps" -ForegroundColor Gray
Write-Host "   查看日誌: docker-compose logs -f web" -ForegroundColor Gray
Write-Host "   查看應用日誌: Get-Content logs\tradingagents.log -Wait" -ForegroundColor Gray
Write-Host "   停止服務: docker-compose down" -ForegroundColor Gray
Write-Host "   重啟服務: docker-compose restart web" -ForegroundColor Gray
Write-Host ""
Write-Host "Web介面: http://localhost:8501" -ForegroundColor Cyan
Write-Host "MongoDB管理: http://localhost:8082 (可選)" -ForegroundColor Cyan
Write-Host "Redis管理: http://localhost:8081" -ForegroundColor Cyan
