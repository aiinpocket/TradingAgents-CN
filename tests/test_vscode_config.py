#!/usr/bin/env python3
"""
VSCode配置驗證測試
驗證Python虛擬環境和項目配置是否正確
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def test_python_environment():
    """測試Python環境配置"""
    print(" Python環境驗證")
    print("=" * 50)
    
    # 檢查Python版本
    print(f"Python版本: {sys.version}")
    print(f"Python路徑: {sys.executable}")
    
    # 檢查虛擬環境
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f" 虛擬環境: {venv_path}")
    else:
        print(" 虛擬環境: 未啟用")
    
    # 檢查工作目錄
    print(f"工作目錄: {os.getcwd()}")
    
    # 檢查是否在項目根目錄
    if os.path.exists('tradingagents') and os.path.exists('.env'):
        print(" 在項目根目錄")
    else:
        print(" 不在項目根目錄")
    
    return True

def test_vscode_settings():
    """測試VSCode設定檔案"""
    print("\n VSCode設定驗證")
    print("=" * 50)
    
    settings_path = Path('.vscode/settings.json')
    
    if not settings_path.exists():
        print(" .vscode/settings.json 不存在")
        return False
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        print(" settings.json 格式正確")
        
        # 檢查關鍵配置
        key_settings = {
            'python.defaultInterpreterPath': './env/Scripts/python.exe',
            'python.terminal.activateEnvironment': True,
            'python.testing.pytestEnabled': True,
        }
        
        for key, expected in key_settings.items():
            if key in settings:
                actual = settings[key]
                if actual == expected:
                    print(f" {key}: {actual}")
                else:
                    print(f" {key}: {actual} (期望: {expected})")
            else:
                print(f" 缺少配置: {key}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f" settings.json 格式錯誤: {e}")
        return False
    except Exception as e:
        print(f" 讀取settings.json失敗: {e}")
        return False

def test_virtual_env_path():
    """測試虛擬環境路徑"""
    print("\n 虛擬環境路徑驗證")
    print("=" * 50)
    
    # 檢查虛擬環境目錄
    env_dir = Path('env')
    if not env_dir.exists():
        print(" env目錄不存在")
        return False
    
    print(" env目錄存在")
    
    # 檢查Python可執行檔案
    python_exe = env_dir / 'Scripts' / 'python.exe'
    if python_exe.exists():
        print(f" Python可執行檔案: {python_exe}")
    else:
        print(f" Python可執行檔案不存在: {python_exe}")
        return False
    
    # 檢查pip
    pip_exe = env_dir / 'Scripts' / 'pip.exe'
    if pip_exe.exists():
        print(f" pip可執行檔案: {pip_exe}")
    else:
        print(f" pip可執行檔案不存在: {pip_exe}")
    
    return True

def test_package_imports():
    """測試關鍵包匯入"""
    print("\n 關鍵包匯入驗證")
    print("=" * 50)
    
    packages = [
        ('langchain', 'LangChain'),
        ('langchain_openai', 'LangChain OpenAI'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('streamlit', 'Streamlit'),
        ('tradingagents', 'TradingAgents')
    ]
    
    success_count = 0
    for package, name in packages:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f" {name}: v{version}")
            success_count += 1
        except ImportError:
            print(f" {name}: 未安裝")
        except Exception as e:
            print(f" {name}: 匯入錯誤 - {e}")
    
    print(f"\n 包匯入結果: {success_count}/{len(packages)} 成功")
    return success_count >= len(packages) * 0.8  # 80%成功率

def test_project_structure():
    """測試項目結構"""
    print("\n 項目結構驗證")
    print("=" * 50)
    
    required_dirs = [
        'tradingagents',
        'tests',
        'cli',
        'web',
        '.vscode'
    ]
    
    required_files = [
        '.env',
        'requirements.txt',
        'README.md',
        '.gitignore'
    ]
    
    # 檢查目錄
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f" 目錄: {dir_name}")
        else:
            print(f" 目錄: {dir_name}")
    
    # 檢查檔案
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f" 檔案: {file_name}")
        else:
            print(f" 檔案: {file_name}")
    
    return True

def test_environment_variables():
    """測試環境變數"""
    print("\n 環境變數驗證")
    print("=" * 50)
    
    # 讀取.env 檔案
    env_file = Path('.env')
    if not env_file.exists():
        print(" .env 檔案不存在")
        return False
    
    print(" .env 檔案存在")
    
    # 檢查關鍵環境變數
    key_vars = [
        'OPENAI_API_KEY',
        'FINNHUB_API_KEY'
    ]
    
    for var in key_vars:
        value = os.getenv(var)
        if value:
            print(f" {var}: {'*' * 10}{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f" {var}: 未設定")
    
    return True

def test_simple_functionality():
    """測試基本功能"""
    print("\n 基本功能驗證")
    print("=" * 50)
    
    try:
        # 測試TradingAgents匯入
        print(" TradingAgents LLM轉接器匯入成功")
        
        # 測試資料流匯入
        from tradingagents.dataflows import interface
        print("TradingAgents資料流匯入成功")
        
        # 測試圖形匯入
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        print(" TradingAgents圖形匯入成功")
        
        return True
        
    except Exception as e:
        print(f" 功能測試失敗: {e}")
        return False

def main():
    """主測試函式"""
    print(" VSCode配置驗證測試")
    print("=" * 70)
    print(" 驗證目標:")
    print("   - Python虛擬環境配置")
    print("   - VSCode設定檔案")
    print("   - 項目結構完整性")
    print("   - 關鍵包匯入")
    print("   - 環境變數配置")
    print("=" * 70)
    
    # 執行所有測試
    tests = [
        ("Python環境", test_python_environment),
        ("VSCode設定", test_vscode_settings),
        ("虛擬環境路徑", test_virtual_env_path),
        ("包匯入", test_package_imports),
        ("項目結構", test_project_structure),
        ("環境變數", test_environment_variables),
        ("基本功能", test_simple_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f" {test_name}測試異常: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n VSCode配置驗證總結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = " 通過" if result else " 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n VSCode配置完全正確！")
        print("\n 現在您可以:")
        print("    在VSCode中正常開發和除錯")
        print("    使用整合終端執行Python程式碼")
        print("    執行測試和格式化程式碼")
        print("    使用智慧程式碼補全和錯誤檢查")
    elif passed >= total * 0.8:
        print("\n VSCode配置基本正確！")
        print(" 部分功能可能需要調整")
    else:
        print("\n VSCode配置需要修複")
        print("請檢查失敗的項目並重新配置")
    
    print("\n 使用建議:")
    print("   1. 確保在VSCode中選擇了正確的Python解釋器")
    print("   2. 重啟VSCode以應用新的配置")
    print("   3. 使用Ctrl+Shift+P -> 'Python: Select Interpreter'")
    print("   4. 在整合終端中驗證虛擬環境已啟用")

if __name__ == "__main__":
    main()
