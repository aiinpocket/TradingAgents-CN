# TradingAgents-CN 使用者密碼管理工具 (PowerShell版本)
param(
    [Parameter(Position=0)]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$Username,

    [Parameter(Position=2)]
    [string]$Password,

    [Parameter(Position=3)]
    [string]$Role = "user"
)

# 設定主控台編碼為UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "TradingAgents-CN 使用者密碼管理工具" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 檢查Python是否可用
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
} catch {
    Write-Host "錯誤: 未找到Python，請確保Python已安裝並新增到PATH" -ForegroundColor Red
    Read-Host "按Enter鍵繼續"
    exit 1
}

# 取得腳本目錄
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ManagerScript = Join-Path $ScriptDir "user_password_manager.py"

# 檢查管理腳本是否存在
if (-not (Test-Path $ManagerScript)) {
    Write-Host "錯誤: 找不到使用者管理腳本 $ManagerScript" -ForegroundColor Red
    Read-Host "按Enter鍵繼續"
    exit 1
}

# 如果沒有參數，顯示說明
if (-not $Command) {
    Write-Host ""
    Write-Host "使用方法:" -ForegroundColor Yellow
    Write-Host "  .\user_manager.ps1 list                              - 列出所有使用者" -ForegroundColor White
    Write-Host "  .\user_manager.ps1 change-password [使用者名稱] [新密碼]   - 修改使用者密碼" -ForegroundColor White
    Write-Host "  .\user_manager.ps1 create-user [使用者名稱] [密碼] [角色]   - 建立新使用者" -ForegroundColor White
    Write-Host "  .\user_manager.ps1 delete-user [使用者名稱]               - 刪除使用者" -ForegroundColor White
    Write-Host "  .\user_manager.ps1 reset                             - 重置為預設配置" -ForegroundColor White
    Write-Host ""
    Write-Host "範例:" -ForegroundColor Yellow
    Write-Host "  .\user_manager.ps1 list" -ForegroundColor Green
    Write-Host "  .\user_manager.ps1 change-password admin newpass123" -ForegroundColor Green
    Write-Host "  .\user_manager.ps1 create-user testuser pass123 user" -ForegroundColor Green
    Write-Host "  .\user_manager.ps1 delete-user testuser" -ForegroundColor Green
    Write-Host "  .\user_manager.ps1 reset" -ForegroundColor Green
    Write-Host ""
    Read-Host "按Enter鍵繼續"
    exit 0
}

# 建構參數列表
$args = @($Command)
if ($Username) { $args += $Username }
if ($Password) { $args += $Password }
if ($Role -and $Command -eq "create-user") { $args += "--role"; $args += $Role }

# 執行Python腳本
try {
    & python $ManagerScript @args
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Read-Host "按Enter鍵繼續"
    }
} catch {
    Write-Host "執行失敗: $_" -ForegroundColor Red
    Read-Host "按Enter鍵繼續"
    exit 1
}
