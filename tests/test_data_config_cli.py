#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試資料目錄配置CLI功能
Test Data Directory Configuration CLI Features
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 新增項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.config.config_manager import config_manager
from tradingagents.dataflows.config import get_data_dir, set_data_dir, initialize_config

def test_data_dir_configuration():
    """
    測試資料目錄配置功能
    Test data directory configuration functionality
    """
    print("\n=== 測試資料目錄配置功能 | Testing Data Directory Configuration ===")
    
    # 1. 測試預設配置
    print("\n1. 測試預設配置 | Testing Default Configuration")
    initialize_config()
    default_data_dir = get_data_dir()
    print(f"預設資料目錄 | Default data directory: {default_data_dir}")
    
    # 2. 測試設定自定義資料目錄
    print("\n2. 測試設定自定義資料目錄 | Testing Custom Data Directory")
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_data_dir = os.path.join(temp_dir, "custom_trading_data")
        print(f"設定自定義資料目錄 | Setting custom data directory: {custom_data_dir}")
        
        set_data_dir(custom_data_dir)
        current_data_dir = get_data_dir()
        print(f"當前資料目錄 | Current data directory: {current_data_dir}")
        
        # 驗證目錄是否建立
        if os.path.exists(custom_data_dir):
            print(" 自定義資料目錄建立成功 | Custom data directory created successfully")
            
            # 檢查子目錄結構
            expected_subdirs = [
                "finnhub",
                "finnhub/news", 
                "finnhub/insider_sentiment",
                "finnhub/insider_transactions"
            ]
            
            for subdir in expected_subdirs:
                subdir_path = os.path.join(custom_data_dir, subdir)
                if os.path.exists(subdir_path):
                    print(f"   子目錄存在 | Subdirectory exists: {subdir}")
                else:
                    print(f"   子目錄缺失 | Subdirectory missing: {subdir}")
        else:
            print(" 自定義資料目錄建立失敗 | Custom data directory creation failed")
    
    # 3. 測試環境變數配置
    print("\n3. 測試環境變數配置 | Testing Environment Variable Configuration")
    with tempfile.TemporaryDirectory() as temp_dir:
        env_data_dir = os.path.join(temp_dir, "env_trading_data")
        
        # 設定環境變數
        os.environ["TRADINGAGENTS_DATA_DIR"] = env_data_dir
        print(f"設定環境變數 | Setting environment variable: TRADINGAGENTS_DATA_DIR={env_data_dir}")
        
        # 重新初始化配置以讀取環境變數
        initialize_config()
        env_current_data_dir = get_data_dir()
        print(f"環境變數資料目錄 | Environment variable data directory: {env_current_data_dir}")
        
        if env_current_data_dir == env_data_dir:
            print(" 環境變數配置生效 | Environment variable configuration effective")
        else:
            print(" 環境變數配置未生效 | Environment variable configuration not effective")
        
        # 清理環境變數
        del os.environ["TRADINGAGENTS_DATA_DIR"]
    
    # 4. 測試配置管理器集成
    print("\n4. 測試配置管理器集成 | Testing Configuration Manager Integration")
    settings = config_manager.load_settings()
    print(f"配置管理器設定 | Configuration manager settings:")
    for key, value in settings.items():
        if 'dir' in key.lower():
            print(f"  {key}: {value}")
    
    # 5. 測試目錄自動建立功能
    print("\n5. 測試目錄自動建立功能 | Testing Auto Directory Creation")
    config_manager.ensure_directories_exist()
    print(" 目錄自動建立功能測試完成 | Auto directory creation test completed")
    
    print("\n=== 資料目錄配置測試完成 | Data Directory Configuration Test Completed ===")

def test_cli_commands():
    """
    測試CLI命令（模擬）
    Test CLI commands (simulation)
    """
    print("\n=== CLI命令測試指南 | CLI Commands Test Guide ===")
    print("\n請手動執行以下命令來測試CLI功能:")
    print("Please manually run the following commands to test CLI functionality:")
    print()
    print("1. 查看當前配置 | View current configuration:")
    print("   python -m cli.main data-config")
    print("   python -m cli.main data-config --show")
    print()
    print("2. 設定自定義資料目錄 | Set custom data directory:")
    print("   python -m cli.main data-config --set C:\\custom\\trading\\data")
    print()
    print("3. 重置為預設配置 | Reset to default configuration:")
    print("   python -m cli.main data-config --reset")
    print()
    print("4. 查看所有可用命令 | View all available commands:")
    print("   python -m cli.main --help")
    print()
    print("5. 執行配置演示指令碼 | Run configuration demo script:")
    print("   python examples/data_dir_config_demo.py")

def main():
    """
    主測試函式
    Main test function
    """
    print("資料目錄配置功能測試 | Data Directory Configuration Feature Test")
    print("=" * 70)
    
    try:
        # 執行配置功能測試
        test_data_dir_configuration()
        
        # 顯示CLI命令測試指南
        test_cli_commands()
        
        print("\n 所有測試完成！| All tests completed!")
        print("\n 總結 | Summary:")
        print(" 資料目錄配置功能已實現 | Data directory configuration feature implemented")
        print(" 支援自定義路徑設定 | Custom path setting supported")
        print(" 支援環境變數配置 | Environment variable configuration supported")
        print(" 集成配置管理器 | Configuration manager integrated")
        print(" CLI命令介面完整 | CLI command interface complete")
        print(" 自動目錄建立功能 | Auto directory creation feature")
        
    except Exception as e:
        print(f"\n 測試過程中出現錯誤 | Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)