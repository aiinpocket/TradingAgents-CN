# ChromaDB 問題診斷和修復腳本 (Windows PowerShell版本)
# 用於解決 "Configuration error: An instance of Chroma already exists for ephemeral with different settings" 錯誤

Write-Host "=== ChromaDB 問題診斷和修復工具 ===" -ForegroundColor Green
Write-Host "適用環境: Windows PowerShell" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查Python程序中的ChromaDB實例
Write-Host "1. 檢查Python程序..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "發現Python程序:" -ForegroundColor Red
    $pythonProcesses | Format-Table -Property Id, ProcessName, StartTime -AutoSize

    $choice = Read-Host "是否終止所有Python程序? (y/N)"
    if ($choice -eq "y" -or $choice -eq "Y") {
        $pythonProcesses | Stop-Process -Force
        Write-Host "已終止所有Python程序" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
} else {
    Write-Host "未發現Python程序" -ForegroundColor Green
}

# 2. 清理ChromaDB暫存檔案和快取
Write-Host "`n2. 清理ChromaDB暫存檔案..." -ForegroundColor Yellow

# 清理使用者暫存目錄中的ChromaDB檔案
$tempPaths = @(
    "$env:TEMP\chroma*",
    "$env:LOCALAPPDATA\Temp\chroma*",
    "$env:USERPROFILE\.chroma*",
    ".\chroma*",
    ".\.chroma*"
)

$cleanedFiles = 0
foreach ($path in $tempPaths) {
    $items = Get-ChildItem -Path $path -ErrorAction SilentlyContinue
    if ($items) {
        Write-Host "清理: $path" -ForegroundColor Cyan
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            $cleanedFiles += $items.Count
        } catch {
            Write-Host "無法刪除: $path" -ForegroundColor Yellow
        }
    }
}

if ($cleanedFiles -gt 0) {
    Write-Host "已清理 $cleanedFiles 個ChromaDB暫存檔案" -ForegroundColor Green
} else {
    Write-Host "未發現ChromaDB暫存檔案" -ForegroundColor Green
}

# 3. 清理Python快取
Write-Host "`n3. 清理Python快取..." -ForegroundColor Yellow
$pycachePaths = @(
    ".\__pycache__",
    ".\tradingagents\__pycache__",
    ".\tradingagents\agents\__pycache__",
    ".\tradingagents\agents\utils\__pycache__"
)

$cleanedCache = 0
foreach ($path in $pycachePaths) {
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Recurse -Force
            $cleanedCache++
            Write-Host "清理: $path" -ForegroundColor Cyan
        } catch {
            Write-Host "無法刪除: $path" -ForegroundColor Yellow
        }
    }
}

if ($cleanedCache -gt 0) {
    Write-Host "已清理 $cleanedCache 個Python快取目錄" -ForegroundColor Green
} else {
    Write-Host "未發現Python快取目錄" -ForegroundColor Green
}

# 4. 檢查ChromaDB版本相容性
Write-Host "`n4. 檢查ChromaDB版本..." -ForegroundColor Yellow
try {
    $chromaVersion = python -c "import chromadb; print(chromadb.__version__)" 2>$null
    if ($chromaVersion) {
        Write-Host "ChromaDB版本: $chromaVersion" -ForegroundColor Cyan

        # 檢查是否為推薦版本
        if ($chromaVersion -match "^1\.0\.") {
            Write-Host "ChromaDB版本相容" -ForegroundColor Green
        } else {
            Write-Host "建議使用ChromaDB 1.0.x版本" -ForegroundColor Yellow
            $upgrade = Read-Host "是否升級ChromaDB? (y/N)"
            if ($upgrade -eq "y" -or $upgrade -eq "Y") {
                Write-Host "升級ChromaDB..." -ForegroundColor Cyan
                pip install --upgrade "chromadb>=1.0.12"
            }
        }
    } else {
        Write-Host "無法偵測ChromaDB版本" -ForegroundColor Red
    }
} catch {
    Write-Host "ChromaDB檢查失敗" -ForegroundColor Red
}

# 5. 檢查環境變數衝突
Write-Host "`n5. 檢查環境變數..." -ForegroundColor Yellow
$chromaEnvVars = @(
    "CHROMA_HOST",
    "CHROMA_PORT",
    "CHROMA_DB_IMPL",
    "CHROMA_API_IMPL",
    "CHROMA_TELEMETRY"
)

$foundEnvVars = @()
foreach ($var in $chromaEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        $foundEnvVars += "$var=$value"
    }
}

if ($foundEnvVars.Count -gt 0) {
    Write-Host "發現ChromaDB環境變數:" -ForegroundColor Yellow
    $foundEnvVars | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
    Write-Host "這些環境變數可能導致配置衝突" -ForegroundColor Yellow
} else {
    Write-Host "未發現ChromaDB環境變數衝突" -ForegroundColor Green
}

# 6. 測試ChromaDB初始化
Write-Host "`n6. 測試ChromaDB初始化..." -ForegroundColor Yellow
$testScript = @"
import chromadb
from chromadb.config import Settings
import sys

try:
    # 測試基本初始化
    client = chromadb.Client()
    print("基本初始化成功")

    # 測試專案配置
    settings = Settings(
        allow_reset=True,
        anonymized_telemetry=False,
        is_persistent=False
    )
    client2 = chromadb.Client(settings)
    print("專案配置初始化成功")

    # 測試集合建立
    collection = client2.create_collection(name="test_collection")
    print("集合建立成功")

    # 清理測試
    client2.delete_collection(name="test_collection")
    print("ChromaDB測試完成")

except Exception as e:
    print(f"ChromaDB測試失敗: {e}")
    sys.exit(1)
"@

try {
    $testResult = python -c $testScript 2>&1
    Write-Host $testResult -ForegroundColor Green
} catch {
    Write-Host "ChromaDB測試失敗" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# 7. 提供解決方案建議
Write-Host "`n=== 解決方案建議 ===" -ForegroundColor Green
Write-Host "如果問題仍然存在，請嘗試以下方案:" -ForegroundColor Cyan
Write-Host ""
Write-Host "方案1: 重啟系統" -ForegroundColor Yellow
Write-Host "  - 完全清理記憶體中的ChromaDB實例"
Write-Host ""
Write-Host "方案2: 使用虛擬環境" -ForegroundColor Yellow
Write-Host "  python -m venv fresh_env"
Write-Host "  fresh_env\Scripts\activate"
Write-Host "  pip install -r requirements.txt"
Write-Host ""
Write-Host "方案3: 重新安裝ChromaDB" -ForegroundColor Yellow
Write-Host "  pip uninstall chromadb -y"
Write-Host "  pip install chromadb==1.0.12"
Write-Host ""
Write-Host "方案4: 檢查Python版本相容性" -ForegroundColor Yellow
Write-Host "  - 確保使用Python 3.8-3.11"
Write-Host "  - 避免使用Python 3.12+"
Write-Host ""

Write-Host "修復完成! 請重新執行應用程式。" -ForegroundColor Green
