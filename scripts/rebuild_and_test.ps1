# Docker重建和測試腳本 (PowerShell版本)
# 修復KeyError後的完整測試流程

Write-Host "Docker重建和日誌測試" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# 1. 停止現有容器
Write-Host ""
Write-Host "停止現有容器..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "容器已停止" -ForegroundColor Green
} else {
    Write-Host "停止容器時出現警告" -ForegroundColor Yellow
}

# 2. 重新建構映像
Write-Host ""
Write-Host "重新建構Docker映像..." -ForegroundColor Yellow
Write-Host "這可能需要幾分鐘時間..." -ForegroundColor Gray

docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "映像建構成功" -ForegroundColor Green
} else {
    Write-Host "映像建構失敗" -ForegroundColor Red
    exit 1
}

# 3. 啟動容器
Write-Host ""
Write-Host "啟動容器..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "容器啟動成功" -ForegroundColor Green
} else {
    Write-Host "容器啟動失敗" -ForegroundColor Red
    exit 1
}

# 4. 等待容器完全啟動
Write-Host ""
Write-Host "等待容器完全啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 5. 檢查容器狀態
Write-Host ""
Write-Host "檢查容器狀態..." -ForegroundColor Yellow
docker-compose ps

# 6. 執行簡單日誌測試
Write-Host ""
Write-Host "執行簡單日誌測試..." -ForegroundColor Yellow
$testResult = docker exec TradingAgents-web python simple_log_test.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "簡單日誌測試通過" -ForegroundColor Green
    Write-Host $testResult
} else {
    Write-Host "簡單日誌測試失敗" -ForegroundColor Red
    Write-Host $testResult
}

# 7. 檢查本機日誌檔案
Write-Host ""
Write-Host "檢查本機日誌檔案..." -ForegroundColor Yellow
if (Test-Path "logs") {
    $logFiles = Get-ChildItem "logs\*.log*" -ErrorAction SilentlyContinue
    if ($logFiles) {
        Write-Host "找到日誌檔案:" -ForegroundColor Green
        foreach ($file in $logFiles) {
            $size = [math]::Round($file.Length / 1KB, 2)
            Write-Host "   $($file.Name) ($size KB)" -ForegroundColor Gray
        }
    } else {
        Write-Host "本機logs目錄中未找到日誌檔案" -ForegroundColor Yellow
    }
} else {
    Write-Host "logs目錄不存在" -ForegroundColor Red
}

# 8. 檢查容器內日誌檔案
Write-Host ""
Write-Host "檢查容器內日誌檔案..." -ForegroundColor Yellow
$containerLogs = docker exec TradingAgents-web ls -la /app/logs/
Write-Host $containerLogs

# 9. 查看最近的Docker日誌
Write-Host ""
Write-Host "查看最近的Docker日誌..." -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Gray
docker logs --tail 20 TradingAgents-web
Write-Host "================================" -ForegroundColor Gray

# 10. 嘗試觸發應用日誌
Write-Host ""
Write-Host "嘗試觸發應用日誌..." -ForegroundColor Yellow
$appTest = docker exec TradingAgents-web python -c "
import sys
sys.path.insert(0, '/app')
try:
    from tradingagents.utils.logging_init import setup_web_logging
    logger = setup_web_logging()
    logger.info('應用日誌測試成功')
    print('應用日誌測試完成')
except Exception as e:
    print(f'應用日誌測試失敗: {e}')
"

Write-Host $appTest

# 11. 最終檢查
Write-Host ""
Write-Host "最終檢查..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

if (Test-Path "logs") {
    $finalLogFiles = Get-ChildItem "logs\*.log*" -ErrorAction SilentlyContinue
    if ($finalLogFiles) {
        Write-Host "最終檢查 - 找到日誌檔案:" -ForegroundColor Green
        foreach ($file in $finalLogFiles) {
            $size = [math]::Round($file.Length / 1KB, 2)
            $lastWrite = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "   $($file.Name) ($size KB) - 最後修改: $lastWrite" -ForegroundColor Gray

            # 顯示最後幾行
            if ($file.Length -gt 0) {
                Write-Host "   最後3行內容:" -ForegroundColor Cyan
                $content = Get-Content $file.FullName -Tail 3 -ErrorAction SilentlyContinue
                foreach ($line in $content) {
                    Write-Host "      $line" -ForegroundColor White
                }
            }
        }
    }
}

Write-Host ""
Write-Host "測試完成!" -ForegroundColor Green
Write-Host ""
Write-Host "常用命令:" -ForegroundColor Yellow
Write-Host "   即時查看日誌: Get-Content logs\tradingagents.log -Wait" -ForegroundColor Gray
Write-Host "   查看Docker日誌: docker-compose logs -f web" -ForegroundColor Gray
Write-Host "   重啟服務: docker-compose restart web" -ForegroundColor Gray
Write-Host "   進入容器: docker exec -it TradingAgents-web bash" -ForegroundColor Gray
Write-Host ""
Write-Host "Web介面: http://localhost:8501" -ForegroundColor Cyan
