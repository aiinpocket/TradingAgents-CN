#!/usr/bin/env python3
"""
確保logs目錄存在的指令碼
在啟動Docker容器前執行，建立必要的logs目錄
"""

import os
import sys
from pathlib import Path

def ensure_logs_directory():
    """確保logs目錄存在"""
    # 取得項目根目錄
    project_root = Path(__file__).parent
    logs_dir = project_root / "logs"
    
    print(" TradingAgents 日誌目錄檢查")
    print("=" * 40)
    print(f" 項目根目錄: {project_root}")
    print(f" 日誌目錄: {logs_dir}")
    
    # 建立logs目錄
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        print(" 建立logs目錄")
    else:
        print(" logs目錄已存在")
    
    # 設定目錄權限（Linux/macOS）
    if os.name != 'nt':  # 不是Windows
        try:
            os.chmod(logs_dir, 0o755)
            print(" 設定目錄權限: 755")
        except Exception as e:
            print(f" 設定權限失敗: {e}")
    
    # 建立.gitkeep檔案
    gitkeep_file = logs_dir / ".gitkeep"
    if not gitkeep_file.exists():
        gitkeep_file.touch()
        print(" 建立.gitkeep檔案")
    
    # 建立README檔案
    readme_file = logs_dir / "README.md"
    if not readme_file.exists():
        readme_content = """# TradingAgents 日誌目錄

此目錄用於存儲 TradingAgents 應用的日誌檔案。

## 日誌檔案說明

- `tradingagents.log` - 主應用日誌檔案
- `tradingagents_error.log` - 錯誤日誌檔案（如果有錯誤）
- `*.log.*` - 輪轉的歷史日誌檔案

## Docker映射

在Docker環境中，此目錄映射到容器內的 `/app/logs` 目錄。
容器內生成的所有日誌檔案都會出現在這裡。

## 取得日誌

如果遇到問題需要發送日誌給開發者，請發送：
1. `tradingagents.log` - 主日誌檔案
2. `tradingagents_error.log` - 錯誤日誌檔案（如果存在）

## 實時查看日誌

```bash
# Linux/macOS
tail -f logs/tradingagents.log

# Windows PowerShell
Get-Content logs/tradingagents.log -Wait
```
"""
        readme_file.write_text(readme_content, encoding='utf-8')
        print(" 建立README.md檔案")
    
    # 檢查現有日誌檔案
    log_files = list(logs_dir.glob("*.log*"))
    if log_files:
        print(f"\n 現有日誌檔案 ({len(log_files)} 個):")
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"    {log_file.name} ({size:,} 位元組)")
    else:
        print("\n 暫無日誌檔案")
    
    print(f"\n 日誌目錄準備完成！")
    print(f" 日誌將保存到: {logs_dir.absolute()}")
    
    return True

def main():
    """主函式"""
    try:
        ensure_logs_directory()
        return True
    except Exception as e:
        print(f" 錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
