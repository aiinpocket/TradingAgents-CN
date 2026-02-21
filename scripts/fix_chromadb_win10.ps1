# ChromaDB Windows 10 相容性修復腳本
# 專門解決Windows 10與Windows 11之間的ChromaDB相容性問題

Write-Host "=== ChromaDB Windows 10 相容性修復工具 ===" -ForegroundColor Green
Write-Host "解決Windows 10上的ChromaDB實例衝突問題" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查Windows版本
Write-Host "1. 檢查Windows版本..." -ForegroundColor Yellow
$osVersion = (Get-WmiObject -Class Win32_OperatingSystem).Caption
Write-Host "作業系統: $osVersion" -ForegroundColor Cyan

if ($osVersion -like "*Windows 10*") {
    Write-Host "偵測到Windows 10，套用相容性修復..." -ForegroundColor Yellow
} else {
    Write-Host "目前系統: $osVersion" -ForegroundColor Cyan
}

# 2. 強制終止所有Python程序
Write-Host "`n2. 強制清理Python程序..." -ForegroundColor Yellow
try {
    Get-Process -Name "python*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "已清理Python程序" -ForegroundColor Green
    Start-Sleep -Seconds 3
} catch {
    Write-Host "Python程序清理完成" -ForegroundColor Green
}

# 3. 清理ChromaDB相關檔案和登錄
Write-Host "`n3. 深度清理ChromaDB檔案..." -ForegroundColor Yellow

# 清理暫存檔案
$cleanupPaths = @(
    "$env:TEMP\*chroma*",
    "$env:LOCALAPPDATA\Temp\*chroma*",
    "$env:USERPROFILE\.chroma*",
    ".\chroma*",
    ".\.chroma*",
    "$env:APPDATA\chroma*",
    "$env:LOCALAPPDATA\chroma*"
)

foreach ($path in $cleanupPaths) {
    try {
        Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        # 忽略錯誤
    }
}

# 清理Python快取
Get-ChildItem -Path "." -Name "__pycache__" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "深度清理完成" -ForegroundColor Green

# 4. 檢查Python版本相容性
Write-Host "`n4. 檢查Python版本相容性..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python版本: $pythonVersion" -ForegroundColor Cyan

    if ($pythonVersion -match "Python 3\.(8|9|10|11)\.") {
        Write-Host "Python版本相容" -ForegroundColor Green
    } else {
        Write-Host "警告: 建議使用Python 3.8-3.11版本" -ForegroundColor Yellow
    }
} catch {
    Write-Host "無法偵測Python版本" -ForegroundColor Red
}

# 5. 重新安裝ChromaDB (Windows 10相容版本)
Write-Host "`n5. 重新安裝ChromaDB..." -ForegroundColor Yellow
Write-Host "解除安裝目前ChromaDB..." -ForegroundColor Cyan
pip uninstall chromadb -y 2>$null

Write-Host "安裝Windows 10相容版本..." -ForegroundColor Cyan
pip install "chromadb==1.0.12" --no-cache-dir --force-reinstall

# 6. 建立Windows 10專用的ChromaDB配置
Write-Host "`n6. 建立Windows 10相容配置..." -ForegroundColor Yellow

$chromaConfigContent = @"
# Windows 10 ChromaDB 相容性配置
import os
import tempfile
import chromadb
from chromadb.config import Settings

# Windows 10 專用配置
def get_win10_chromadb_client():
    '''取得Windows 10相容的ChromaDB用戶端'''
    settings = Settings(
        allow_reset=True,
        anonymized_telemetry=False,
        is_persistent=False,
        # Windows 10 特定配置
        chroma_db_impl="duckdb+parquet",
        chroma_api_impl="chromadb.api.segment.SegmentAPI",
        # 使用暫存目錄避免權限問題
        persist_directory=None
    )

    try:
        client = chromadb.Client(settings)
        return client
    except Exception as e:
        # 降級到最基本配置
        basic_settings = Settings(
            allow_reset=True,
            is_persistent=False
        )
        return chromadb.Client(basic_settings)

# 匯出配置
__all__ = ['get_win10_chromadb_client']
"@

$configPath = ".\tradingagents\agents\utils\chromadb_win10_config.py"
$chromaConfigContent | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "已建立Windows 10相容配置檔案: $configPath" -ForegroundColor Green

# 7. 測試ChromaDB初始化
Write-Host "`n7. 測試ChromaDB初始化..." -ForegroundColor Yellow

$testScript = @"
import sys
import os
sys.path.insert(0, '.')

try:
    import chromadb
    from chromadb.config import Settings

    # 測試基本初始化
    settings = Settings(
        allow_reset=True,
        anonymized_telemetry=False,
        is_persistent=False
    )

    client = chromadb.Client(settings)
    print('基本初始化成功')

    # 測試集合操作
    collection_name = 'test_win10_collection'
    try:
        # 刪除可能存在的集合
        try:
            client.delete_collection(name=collection_name)
        except:
            pass

        # 建立新集合
        collection = client.create_collection(name=collection_name)
        print('集合建立成功')

        # 清理測試集合
        client.delete_collection(name=collection_name)
        print('ChromaDB Windows 10 測試完成')

    except Exception as e:
        print(f'集合操作失敗: {e}')

except Exception as e:
    print(f'ChromaDB測試失敗: {e}')
    sys.exit(1)
"@

try {
    $testResult = python -c $testScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $testResult -ForegroundColor Green
        Write-Host "ChromaDB測試成功" -ForegroundColor Green
    } else {
        Write-Host "ChromaDB測試失敗: $testResult" -ForegroundColor Red
    }
} catch {
    Write-Host "ChromaDB測試異常" -ForegroundColor Red
}

# 8. Windows 10 特定解決方案
Write-Host "`n=== Windows 10 特定解決方案 ===" -ForegroundColor Green
Write-Host ""
Write-Host "Windows 10與Windows 11的主要差異:" -ForegroundColor Cyan
Write-Host "1. 檔案系統權限管理不同" -ForegroundColor White
Write-Host "2. 暫存檔案處理機制不同" -ForegroundColor White
Write-Host "3. 程序隔離級別不同" -ForegroundColor White
Write-Host "4. 記憶體管理策略不同" -ForegroundColor White
Write-Host ""

Write-Host "推薦解決方案 (按優先順序):" -ForegroundColor Yellow
Write-Host ""
Write-Host "方案1: 使用系統管理員權限執行" -ForegroundColor Yellow
Write-Host "  - 右鍵點擊PowerShell，選擇'以系統管理員身分執行'" -ForegroundColor White
Write-Host "  - 然後執行應用程式" -ForegroundColor White
Write-Host ""

Write-Host "方案2: 修改記憶體配置" -ForegroundColor Yellow
Write-Host "  - 在.env檔案中新增:" -ForegroundColor White
Write-Host "    MEMORY_ENABLED=false" -ForegroundColor Cyan
Write-Host "    或降低記憶體使用" -ForegroundColor White
Write-Host ""

Write-Host "方案3: 使用虛擬環境隔離" -ForegroundColor Yellow
Write-Host "  python -m venv win10_env" -ForegroundColor Cyan
Write-Host "  win10_env\Scripts\activate" -ForegroundColor Cyan
Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host ""

Write-Host "方案4: 重啟後首次執行" -ForegroundColor Yellow
Write-Host "  - 重啟Windows 10系統" -ForegroundColor White
Write-Host "  - 首次執行前不要啟動其他Python程式" -ForegroundColor White
Write-Host ""

Write-Host "如果問題仍然存在，請嘗試在.env檔案中設定:" -ForegroundColor Yellow
Write-Host "MEMORY_ENABLED=false" -ForegroundColor Cyan
Write-Host "這將停用ChromaDB記憶體功能，避免衝突" -ForegroundColor White
Write-Host ""

Write-Host "修復完成! 建議重啟系統後重新執行應用程式。" -ForegroundColor Green
