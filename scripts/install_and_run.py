#!/usr/bin/env python3
"""
TradingAgents-CN 安裝和啟動腳本
解決模塊導入問題，提供一键安裝和啟動
"""

import os
import sys
import subprocess
from pathlib import Path

def check_virtual_env():
    """檢查是否在虛擬環境中"""
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if not in_venv:
        print("❌ 請先激活虛擬環境:")
        print("   Windows: .\\env\\Scripts\\activate")
        print("   Linux/macOS: source env/bin/activate")
        return False
    
    print("✅ 虛擬環境已激活")
    return True

def install_project():
    """安裝項目到虛擬環境"""
    print("\n📦 安裝項目到虛擬環境...")
    
    project_root = Path(__file__).parent.parent
    
    try:
        # 開發模式安裝
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], cwd=project_root, check=True, capture_output=True, text=True)
        
        print("✅ 項目安裝成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 項目安裝失败: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return False

def install_web_dependencies():
    """安裝Web界面依賴"""
    print("\n🌐 安裝Web界面依賴...")
    
    web_deps = [
        "streamlit>=1.28.0",
        "plotly>=5.15.0", 
        "altair>=5.0.0"
    ]
    
    try:
        for dep in web_deps:
            print(f"   安裝 {dep}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
        
        print("✅ Web依賴安裝成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Web依賴安裝失败: {e}")
        return False

def check_env_file():
    """檢查.env文件"""
    print("\n🔑 檢查環境配置...")
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_example = project_root / ".env_example"
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️ .env文件不存在，正在從.env_example創建...")
            try:
                import shutil
                shutil.copy(env_example, env_file)
                print("✅ .env文件已創建")
                print("💡 請編辑.env文件，配置您的API密鑰")
            except Exception as e:
                print(f"❌ 創建.env文件失败: {e}")
                return False
        else:
            print("❌ 找不到.env_example文件")
            return False
    else:
        print("✅ .env文件存在")
    
    return True

def start_web_app():
    """啟動Web應用"""
    print("\n🚀 啟動Web應用...")
    
    project_root = Path(__file__).parent.parent
    web_dir = project_root / "web"
    app_file = web_dir / "app.py"
    
    if not app_file.exists():
        print(f"❌ 找不到應用文件: {app_file}")
        return False
    
    # 構建啟動命令
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_file),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("📱 Web應用啟動中...")
    print("🌐 浏覽器将自動打開 http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止應用")
    print("=" * 50)
    
    try:
        # 啟動應用
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n⏹️ Web應用已停止")
    except Exception as e:
        print(f"\n❌ 啟動失败: {e}")
        return False
    
    return True

def main():
    """主函數"""
    print("🔧 TradingAgents-CN 安裝和啟動工具")
    print("=" * 50)
    
    # 檢查虛擬環境
    if not check_virtual_env():
        return
    
    # 安裝項目
    if not install_project():
        return
    
    # 安裝Web依賴
    if not install_web_dependencies():
        return
    
    # 檢查環境文件
    if not check_env_file():
        return
    
    # 啟動Web應用
    start_web_app()

if __name__ == "__main__":
    main()
