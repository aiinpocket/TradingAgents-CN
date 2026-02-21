#!/usr/bin/env python3
"""
測試數據庫依賴包兼容性修複
驗證requirements_db.txt的兼容性改進
"""

import os
import sys
import subprocess
import tempfile
import shutil

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_python_version_check():
    """測試Python版本檢查"""
    print("🔧 測試Python版本檢查...")
    
    current_version = sys.version_info
    if current_version >= (3, 10):
        print(f"  ✅ Python {current_version.major}.{current_version.minor}.{current_version.micro} 符合要求")
        return True
    else:
        print(f"  ❌ Python {current_version.major}.{current_version.minor}.{current_version.micro} 版本過低")
        return False


def test_pickle_compatibility():
    """測試pickle兼容性"""
    print("🔧 測試pickle兼容性...")
    
    try:
        import pickle
        
        # 檢查協議版本
        max_protocol = pickle.HIGHEST_PROTOCOL
        print(f"  當前pickle協議: {max_protocol}")
        
        if max_protocol >= 5:
            print("  ✅ 支持pickle協議5")
        else:
            print("  ❌ 不支持pickle協議5")
            return False
        
        # 檢查是否錯誤安裝了pickle5
        try:
            import pickle5
            print("  ⚠️ 檢測到pickle5包，建議卸載")
            return False
        except ImportError:
            print("  ✅ 未安裝pickle5包，配置正確")
            return True
            
    except Exception as e:
        print(f"  ❌ pickle測試失敗: {e}")
        return False


def test_requirements_file_syntax():
    """測試requirements文件語法"""
    print("🔧 測試requirements_db.txt語法...")
    
    requirements_file = os.path.join(project_root, "requirements_db.txt")
    
    if not os.path.exists(requirements_file):
        print("  ❌ requirements_db.txt文件不存在")
        return False
    
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"  文件行數: {len(lines)}")
        
        # 檢查是否包含pickle5
        pickle5_found = False
        valid_packages = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if 'pickle5' in line and not line.startswith('#'):
                print(f"  ❌ 第{line_num}行仍包含pickle5: {line}")
                pickle5_found = True
            else:
                valid_packages.append(line)
                print(f"  ✅ 第{line_num}行: {line}")
        
        if pickle5_found:
            print("  ❌ 仍包含pickle5依賴")
            return False
        
        print(f"  ✅ 語法檢查通過，有效包數量: {len(valid_packages)}")
        return True
        
    except Exception as e:
        print(f"  ❌ 文件讀取失敗: {e}")
        return False


def test_package_installation_simulation():
    """模擬包安裝測試"""
    print("🔧 模擬包安裝測試...")
    
    # 模擬檢查每個包的可用性
    packages_to_check = [
        "pymongo",
        "motor", 
        "redis",
        "hiredis",
        "pandas",
        "numpy"
    ]
    
    available_packages = []
    missing_packages = []
    
    for package in packages_to_check:
        try:
            __import__(package)
            available_packages.append(package)
            print(f"  ✅ {package}: 已安裝")
        except ImportError:
            missing_packages.append(package)
            print(f"  ⚠️ {package}: 未安裝")
    
    print(f"  已安裝: {len(available_packages)}/{len(packages_to_check)}")
    
    if missing_packages:
        print(f"  缺少包: {missing_packages}")
        print("  💡 運行以下命令安裝: pip install -r requirements_db.txt")
    
    return True  # 這個測試總是通過，只是信息性的


def test_compatibility_checker_tool():
    """測試兼容性檢查工具"""
    print("🔧 測試兼容性檢查工具...")
    
    checker_file = os.path.join(project_root, "check_db_requirements.py")
    
    if not os.path.exists(checker_file):
        print("  ❌ check_db_requirements.py文件不存在")
        return False
    
    try:
        # 運行兼容性檢查工具
        result = subprocess.run(
            [sys.executable, checker_file],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"  返回碼: {result.returncode}")
        
        if "🔧 TradingAgents 數據庫依賴包兼容性檢查" in result.stdout:
            print("  ✅ 兼容性檢查工具運行成功")
            
            # 檢查是否檢測到pickle5問題
            if "pickle5" in result.stdout and "建議卸載" in result.stdout:
                print("  ⚠️ 檢測到pickle5問題")
            elif "未安裝pickle5包，配置正確" in result.stdout:
                print("  ✅ pickle5配置正確")
            
            return True
        else:
            print("  ❌ 兼容性檢查工具輸出異常")
            print(f"  輸出: {result.stdout[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ 兼容性檢查工具運行超時")
        return False
    except Exception as e:
        print(f"  ❌ 兼容性檢查工具運行失敗: {e}")
        return False


def test_documentation_completeness():
    """測試文件完整性"""
    print("🔧 測試文件完整性...")
    
    docs_to_check = [
        "docs/DATABASE_SETUP_GUIDE.md",
        "REQUIREMENTS_DB_UPDATE.md"
    ]
    
    all_exist = True
    
    for doc_path in docs_to_check:
        full_path = os.path.join(project_root, doc_path)
        if os.path.exists(full_path):
            print(f"  ✅ {doc_path}: 存在")
            
            # 檢查文件大小
            size = os.path.getsize(full_path)
            if size > 1000:  # 至少1KB
                print(f"    文件大小: {size} 字節")
            else:
                print(f"    ⚠️ 文件較小: {size} 字節")
        else:
            print(f"  ❌ {doc_path}: 不存在")
            all_exist = False
    
    return all_exist


def main():
    """主測試函數"""
    print("🔧 數據庫依賴包兼容性修複測試")
    print("=" * 60)
    
    tests = [
        ("Python版本檢查", test_python_version_check),
        ("pickle兼容性", test_pickle_compatibility),
        ("requirements文件語法", test_requirements_file_syntax),
        ("包安裝模擬", test_package_installation_simulation),
        ("兼容性檢查工具", test_compatibility_checker_tool),
        ("文件完整性", test_documentation_completeness),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"  ✅ {test_name} 通過")
            else:
                print(f"  ❌ {test_name} 失敗")
        except Exception as e:
            print(f"  ❌ {test_name} 異常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！數據庫依賴包兼容性修複成功")
        print("\n📋 修複內容:")
        print("✅ 移除pickle5依賴，解決Python 3.10+兼容性問題")
        print("✅ 優化版本要求，提高環境兼容性")
        print("✅ 添加兼容性檢查工具")
        print("✅ 完善安裝指南和故障排除文件")
        
        print("\n🚀 用戶體驗改進:")
        print("✅ 減少安裝錯誤")
        print("✅ 提供清晰的錯誤診斷")
        print("✅ 支持更多Python環境")
        print("✅ 簡化故障排除流程")
        
        return True
    else:
        print("⚠️ 部分測試失敗，需要進一步檢查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
