#!/usr/bin/env python3
"""
TradingAgents-CN 快速安裝腳本
自動檢測環境並引導用戶完成安裝配置
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class Colors:
    """控制台颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.GREEN):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.END}")

def print_header():
    """打印欢迎信息"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("🚀 TradingAgents-CN 快速安裝向導", Colors.BOLD)
    print_colored("=" * 60, Colors.BLUE)
    print()

def check_python_version():
    """檢查Python版本"""
    print_colored("🔍 檢查Python版本...", Colors.BLUE)
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro} - 版本符合要求", Colors.GREEN)
        return True
    else:
        print_colored(f"❌ Python {version.major}.{version.minor}.{version.micro} - 需要Python 3.10+", Colors.RED)
        print_colored("請升級Python版本: https://www.python.org/downloads/", Colors.YELLOW)
        return False

def check_git():
    """檢查Git是否安裝"""
    print_colored("🔍 檢查Git...", Colors.BLUE)
    
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"✅ {result.stdout.strip()}", Colors.GREEN)
            return True
    except FileNotFoundError:
        pass
    
    print_colored("❌ Git未安裝", Colors.RED)
    print_colored("請安裝Git: https://git-scm.com/downloads", Colors.YELLOW)
    return False

def check_docker():
    """檢查Docker是否安裝"""
    print_colored("🔍 檢查Docker...", Colors.BLUE)
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"✅ {result.stdout.strip()}", Colors.GREEN)
            
            # 檢查Docker Compose
            try:
                result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print_colored(f"✅ {result.stdout.strip()}", Colors.GREEN)
                    return True
            except FileNotFoundError:
                pass
            
            print_colored("❌ Docker Compose未安裝", Colors.YELLOW)
            return False
    except FileNotFoundError:
        pass
    
    print_colored("❌ Docker未安裝", Colors.YELLOW)
    return False

def choose_installation_method():
    """選擇安裝方式"""
    print_colored("\n📋 請選擇安裝方式:", Colors.BLUE)
    print("1. Docker安裝 (推薦，簡單穩定)")
    print("2. 本地安裝 (適合開發者)")
    
    while True:
        choice = input("\n請輸入選擇 (1/2): ").strip()
        if choice in ['1', '2']:
            return choice
        print_colored("請輸入有效選擇 (1或2)", Colors.YELLOW)

def docker_install():
    """Docker安裝流程"""
    print_colored("\n🐳 開始Docker安裝...", Colors.BLUE)
    
    # 檢查項目目錄
    if not Path('docker-compose.yml').exists():
        print_colored("❌ 未找到docker-compose.yml文件", Colors.RED)
        print_colored("請確保在項目根目錄運行此腳本", Colors.YELLOW)
        return False
    
    # 檢查.env文件
    if not Path('.env').exists():
        print_colored("📝 創建環境配置文件...", Colors.BLUE)
        if Path('.env.example').exists():
            shutil.copy('.env.example', '.env')
            print_colored("✅ 已創建.env文件", Colors.GREEN)
        else:
            print_colored("❌ 未找到.env.example文件", Colors.RED)
            return False
    
    # 提示配置API密鑰
    print_colored("\n⚠️  重要提醒:", Colors.YELLOW)
    print_colored("請編辑.env文件，配置至少一個AI模型的API密鑰", Colors.YELLOW)
    print_colored("推薦配置DeepSeek或通義千問API密鑰", Colors.YELLOW)
    
    input("\n按回車键繼续...")
    
    # 啟動Docker服務
    print_colored("🚀 啟動Docker服務...", Colors.BLUE)
    try:
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_colored("✅ Docker服務啟動成功!", Colors.GREEN)
            print_colored("\n🌐 訪問地址:", Colors.BLUE)
            print_colored("主應用: http://localhost:8501", Colors.GREEN)
            print_colored("Redis管理: http://localhost:8081", Colors.GREEN)
            return True
        else:
            print_colored(f"❌ Docker啟動失败: {result.stderr}", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"❌ Docker啟動異常: {e}", Colors.RED)
        return False

def local_install():
    """本地安裝流程"""
    print_colored("\n💻 開始本地安裝...", Colors.BLUE)
    
    # 檢查虛擬環境
    venv_path = Path('env')
    if not venv_path.exists():
        print_colored("📦 創建虛擬環境...", Colors.BLUE)
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'env'], check=True)
            print_colored("✅ 虛擬環境創建成功", Colors.GREEN)
        except subprocess.CalledProcessError as e:
            print_colored(f"❌ 虛擬環境創建失败: {e}", Colors.RED)
            return False
    
    # 激活虛擬環境的Python路徑
    if platform.system() == "Windows":
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"
    
    # 升級pip
    print_colored("📦 升級pip...", Colors.BLUE)
    try:
        subprocess.run([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print_colored("✅ pip升級成功", Colors.GREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"⚠️  pip升級失败，繼续安裝: {e}", Colors.YELLOW)
    
    # 安裝依賴
    print_colored("📦 安裝項目依賴...", Colors.BLUE)
    try:
        result = subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_colored("✅ 依賴安裝成功", Colors.GREEN)
        else:
            print_colored(f"❌ 依賴安裝失败: {result.stderr}", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"❌ 依賴安裝異常: {e}", Colors.RED)
        return False
    
    # 創建.env文件
    if not Path('.env').exists():
        print_colored("📝 創建環境配置文件...", Colors.BLUE)
        if Path('.env.example').exists():
            shutil.copy('.env.example', '.env')
            print_colored("✅ 已創建.env文件", Colors.GREEN)
        else:
            print_colored("❌ 未找到.env.example文件", Colors.RED)
            return False
    
    # 提示配置API密鑰
    print_colored("\n⚠️  重要提醒:", Colors.YELLOW)
    print_colored("請編辑.env文件，配置至少一個AI模型的API密鑰", Colors.YELLOW)
    print_colored("推薦配置DeepSeek或通義千問API密鑰", Colors.YELLOW)
    
    input("\n按回車键繼续...")
    
    # 啟動應用
    print_colored("🚀 啟動應用...", Colors.BLUE)
    print_colored("應用将在浏覽器中打開: http://localhost:8501", Colors.GREEN)
    
    # 提供啟動命令
    if platform.system() == "Windows":
        activate_cmd = "env\\Scripts\\activate"
        start_cmd = f"{activate_cmd} && python -m streamlit run web/app.py"
    else:
        activate_cmd = "source env/bin/activate"
        start_cmd = f"{activate_cmd} && python -m streamlit run web/app.py"
    
    print_colored(f"\n📋 啟動命令:", Colors.BLUE)
    print_colored(f"  {start_cmd}", Colors.GREEN)
    
    return True

def main():
    """主函數"""
    print_header()
    
    # 檢查基础環境
    if not check_python_version():
        return
    
    check_git()
    docker_available = check_docker()
    
    # 選擇安裝方式
    if docker_available:
        choice = choose_installation_method()
    else:
        print_colored("\n💡 Docker未安裝，将使用本地安裝方式", Colors.YELLOW)
        choice = '2'
    
    # 執行安裝
    success = False
    if choice == '1':
        success = docker_install()
    else:
        success = local_install()
    
    # 安裝結果
    if success:
        print_colored("\n🎉 安裝完成!", Colors.GREEN)
        print_colored("📖 詳細文档: docs/INSTALLATION_GUIDE.md", Colors.BLUE)
        print_colored("❓ 遇到問題: https://github.com/hsliuping/TradingAgents-CN/issues", Colors.BLUE)
    else:
        print_colored("\n❌ 安裝失败", Colors.RED)
        print_colored("📖 請查看詳細安裝指南: docs/INSTALLATION_GUIDE.md", Colors.YELLOW)

if __name__ == "__main__":
    main()
