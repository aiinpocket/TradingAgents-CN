#!/usr/bin/env python3
"""
TradingAgents-CN 簡化啟動腳本
解決模塊導入問題的最簡單方案
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """主函數"""
    print("🚀 TradingAgents-CN Web應用啟動器")
    print("=" * 50)
    
    # 獲取項目根目錄
    project_root = Path(__file__).parent
    web_dir = project_root / "web"
    app_file = web_dir / "app.py"
    
    # 檢查文件是否存在
    if not app_file.exists():
        print(f"❌ 找不到應用文件: {app_file}")
        return
    
    # 檢查虛擬環境
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if not in_venv:
        print("⚠️ 建議在虛擬環境中運行:")
        print("   Windows: .\\env\\Scripts\\activate")
        print("   Linux/macOS: source env/bin/activate")
        print()
    
    # 檢查streamlit是否安裝
    try:
        import streamlit
        print("✅ Streamlit已安裝")
    except ImportError:
        print("❌ Streamlit未安裝，正在安裝...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "plotly"], check=True)
            print("✅ Streamlit安裝成功")
        except subprocess.CalledProcessError:
            print("❌ Streamlit安裝失敗，請手動安裝: pip install streamlit plotly")
            return
    
    # 設置環境變量，添加項目根目錄到Python路徑
    env = os.environ.copy()
    current_path = env.get('PYTHONPATH', '')
    if current_path:
        env['PYTHONPATH'] = f"{project_root}{os.pathsep}{current_path}"
    else:
        env['PYTHONPATH'] = str(project_root)
    
    # 構建啟動命令
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_file),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false",
        "--server.fileWatcherType", "none",
        "--server.runOnSave", "false"
    ]
    
    print("🌐 啟動Web應用...")
    print("📱 瀏覽器將自動打開 http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止應用")
    print("=" * 50)
    
    try:
        # 啟動應用，傳遞修改後的環境變量
        subprocess.run(cmd, cwd=project_root, env=env)
    except KeyboardInterrupt:
        print("\n⏹️ Web應用已停止")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        print("\n💡 如果遇到模塊導入問題，請嘗試:")
        print("   1. 激活虛擬環境")
        print("   2. 運行: pip install -e .")
        print("   3. 再次啟動Web應用")

if __name__ == "__main__":
    main()
