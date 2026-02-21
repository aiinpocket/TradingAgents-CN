#!/usr/bin/env python3
"""
確保logs目錄存在的腳本
在啟動Docker容器前運行，創建必要的logs目錄
"""

import os
import sys
from pathlib import Path

def ensure_logs_directory():
    """確保logs目錄存在"""
    # 獲取項目根目錄
    project_root = Path(__file__).parent
    logs_dir = project_root / "logs"
    
    print("🚀 TradingAgents 日誌目錄檢查")
    print("=" * 40)
    print(f"📁 項目根目錄: {project_root}")
    print(f"📁 日誌目錄: {logs_dir}")
    
    # 創建logs目錄
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        print("✅ 創建logs目錄")
    else:
        print("📁 logs目錄已存在")
    
    # 設置目錄權限（Linux/macOS）
    if os.name != 'nt':  # 不是Windows
        try:
            os.chmod(logs_dir, 0o755)
            print("✅ 設置目錄權限: 755")
        except Exception as e:
            print(f"⚠️ 設置權限失敗: {e}")
    
    # 創建.gitkeep文件
    gitkeep_file = logs_dir / ".gitkeep"
    if not gitkeep_file.exists():
        gitkeep_file.touch()
        print("✅ 創建.gitkeep文件")
    
    # 創建README文件
    readme_file = logs_dir / "README.md"
    if not readme_file.exists():
        readme_content = """# TradingAgents 日誌目錄

此目錄用於存儲 TradingAgents 應用的日誌文件。

## 日誌文件說明

- `tradingagents.log` - 主應用日誌文件
- `tradingagents_error.log` - 錯誤日誌文件（如果有錯誤）
- `*.log.*` - 輪轉的歷史日誌文件

## Docker映射

在Docker環境中，此目錄映射到容器內的 `/app/logs` 目錄。
容器內生成的所有日誌文件都會出現在這裡。

## 獲取日誌

如果遇到問題需要發送日誌給開發者，請發送：
1. `tradingagents.log` - 主日誌文件
2. `tradingagents_error.log` - 錯誤日誌文件（如果存在）

## 實時查看日誌

```bash
# Linux/macOS
tail -f logs/tradingagents.log

# Windows PowerShell
Get-Content logs/tradingagents.log -Wait
```
"""
        readme_file.write_text(readme_content, encoding='utf-8')
        print("✅ 創建README.md文件")
    
    # 檢查現有日誌文件
    log_files = list(logs_dir.glob("*.log*"))
    if log_files:
        print(f"\n📋 現有日誌文件 ({len(log_files)} 個):")
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"   📄 {log_file.name} ({size:,} 字節)")
    else:
        print("\n📋 暫無日誌文件")
    
    print(f"\n🎉 日誌目錄準備完成！")
    print(f"📁 日誌將保存到: {logs_dir.absolute()}")
    
    return True

def main():
    """主函數"""
    try:
        ensure_logs_directory()
        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
