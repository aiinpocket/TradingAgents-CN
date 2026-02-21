# TradingAgents-CN 智慧Docker啟動腳本 (Windows PowerShell版本)
# 功能：自動判斷是否需要重新建構Docker映像
# 使用：powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1
#
# 判斷邏輯：
# 1. 檢查是否存在tradingagents-cn映像
# 2. 如果映像不存在 -> 執行建構啟動
# 3. 如果映像存在但程式碼有變化 -> 執行建構啟動
# 4. 如果映像存在且程式碼無變化 -> 快速啟動

Write-Host "=== TradingAgents-CN Docker 智慧啟動腳本 ===" -ForegroundColor Green
Write-Host "適用環境: Windows PowerShell" -ForegroundColor Cyan

# 檢查是否有映像
$imageExists = docker images | Select-String "tradingagents-cn"

if ($imageExists) {
    Write-Host "發現現有映像" -ForegroundColor Green

    # 檢查程式碼是否有變化（簡化版本）
    $gitStatus = git status --porcelain
    if ([string]::IsNullOrEmpty($gitStatus)) {
        Write-Host "程式碼無變化，使用快速啟動" -ForegroundColor Blue
        docker-compose up -d
    } else {
        Write-Host "偵測到程式碼變化，重新建構" -ForegroundColor Yellow
        docker-compose up -d --build
    }
} else {
    Write-Host "首次執行，建構映像" -ForegroundColor Yellow
    docker-compose up -d --build
}

Write-Host "啟動完成!" -ForegroundColor Green
Write-Host "Web介面: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Redis管理: http://localhost:8081" -ForegroundColor Cyan
