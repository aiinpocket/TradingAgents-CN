# TradingAgents-CN Web 應用啟動腳本

Write-Host "啟動 TradingAgents-CN Web 應用..." -ForegroundColor Green
Write-Host ""

# 啟動虛擬環境
& ".\env\Scripts\Activate.ps1"

# 檢查專案是否已安裝
try {
    python -c "import tradingagents" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安裝專案到虛擬環境..." -ForegroundColor Yellow
        pip install -e .
    }
} catch {
    Write-Host "安裝專案到虛擬環境..." -ForegroundColor Yellow
    pip install -e .
}

# 啟動 FastAPI 應用
python start_app.py

Write-Host "按任意鍵退出..." -ForegroundColor Yellow
Read-Host
