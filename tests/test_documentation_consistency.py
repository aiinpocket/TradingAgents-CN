#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案一致性測試
Documentation Consistency Test

測試檔案中的配置和說明是否一致
Test if configurations and descriptions in documentation are consistent
"""

import os
import re
import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_redis_commander_port_consistency():
    """
    測試 Redis Commander 端口配置的一致性
    Test Redis Commander port configuration consistency
    """
    print(" 測試 Redis Commander 端口配置一致性...")
    
    # 檢查 .env.example 檔案
    env_example_path = project_root / ".env.example"
    if env_example_path.exists():
        with open(env_example_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
            # 應該包含 8082 端口
            if "localhost:8082" in env_content and "Redis Commander" in env_content:
                print(" .env.example 中 Redis Commander 端口配置正確 (8082)")
            else:
                print(" .env.example 中 Redis Commander 端口配置不正確")
                return False
    
    # 檢查 database_setup.md 檔案
    db_setup_path = project_root / "docs" / "database_setup.md"
    if db_setup_path.exists():
        with open(db_setup_path, 'r', encoding='utf-8') as f:
            db_content = f.read()
            # 應該包含 8082 端口
            if "8082" in db_content and "Redis Commander" in db_content:
                print(" database_setup.md 中 Redis Commander 端口配置正確 (8082)")
            else:
                print(" database_setup.md 中 Redis Commander 端口配置不正確")
                return False
    
    return True


def test_cli_command_format_consistency():
    """
    測試 CLI 命令格式的一致性
    Test CLI command format consistency
    """
    print("\n 測試 CLI 命令格式一致性...")
    
    # 檢查主要檔案檔案
    docs_to_check = [
        "README-CN.md",
        "docs/configuration/config-guide.md"
    ]
    
    for doc_file in docs_to_check:
        doc_path = project_root / doc_file
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 檢查是否使用了推薦的 python -m cli.main 格式
                old_format_count = len(re.findall(r'python cli/main\.py', content))
                new_format_count = len(re.findall(r'python -m cli\.main', content))
                
                if old_format_count == 0:
                    print(f" {doc_file} 中 CLI 命令格式正確")
                else:
                    print(f" {doc_file} 中仍有 {old_format_count} 處使用舊格式")
                    return False
    
    return True


def test_cli_smart_suggestions():
    """
    測試 CLI 智慧建議功能
    Test CLI smart suggestions feature
    """
    print("\n 測試 CLI 智慧建議功能...")
    
    # 檢查 cli/main.py 是否包含智慧建議代碼
    cli_main_path = project_root / "cli" / "main.py"
    if cli_main_path.exists():
        with open(cli_main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 檢查是否包含智慧建議相關程式碼
            if "get_close_matches" in content and "您是否想要使用以下命令之一" in content:
                print(" CLI 智慧建議功能已實現")
                return True
            else:
                print(" CLI 智慧建議功能未找到")
                return False
    
    return False


def test_documentation_structure():
    """
    測試檔案結構的完整性
    Test documentation structure completeness
    """
    print("\n 測試檔案結構完整性...")
    
    # 檢查關鍵檔案是否存在
    key_docs = [
        "README.md",
        "docs/README.md",
        "docs/database_setup.md",
        "docs/overview/quick-start.md",
        "docs/configuration/data-directory-configuration.md"
    ]
    
    missing_docs = []
    for doc in key_docs:
        doc_path = project_root / doc
        if not doc_path.exists():
            missing_docs.append(doc)
    
    if not missing_docs:
        print(" 所有關鍵檔案都存在")
        return True
    else:
        print(f" 缺少檔案: {', '.join(missing_docs)}")
        return False


def main():
    """
    主測試函式
    Main test function
    """
    print(" 開始檔案一致性測試...")
    print("=" * 50)
    
    tests = [
        test_redis_commander_port_consistency,
        test_cli_command_format_consistency,
        test_cli_smart_suggestions,
        test_documentation_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f" 測試 {test_func.__name__} 執行失敗: {e}")
    
    print("\n" + "=" * 50)
    print(f" 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print(" 所有檔案一致性測試通過！")
        return True
    else:
        print(" 部分測試未通過，請檢查上述問題")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)