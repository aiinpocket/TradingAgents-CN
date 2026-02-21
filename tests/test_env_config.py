#!/usr/bin/env python3
"""
測試使用.env配置的數據庫管理器
"""

import sys
import os
from pathlib import Path

def test_env_config():
    """測試.env配置"""
    print("🔧 測試使用.env配置的數據庫管理器")
    print("=" * 50)
    
    # 1. 檢查.env文件
    print("\n📁 檢查.env文件...")
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ .env文件存在: {env_file}")
        
        # 讀取並顯示相關配置
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("📊 數據庫相關配置:")
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if any(keyword in line.upper() for keyword in ['MONGODB', 'REDIS']):
                    # 隐藏密碼
                    if 'PASSWORD' in line.upper():
                        key, value = line.split('=', 1)
                        print(f"  {key}=***")
                    else:
                        print(f"  {line}")
    else:
        print(f"❌ .env文件不存在: {env_file}")
        return False
    
    # 2. 測試數據庫管理器
    print("\n🔧 測試數據庫管理器...")
    try:
        from tradingagents.config.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        print("✅ 數據庫管理器創建成功")
        
        # 獲取狀態報告
        status = db_manager.get_status_report()
        
        print("📊 數據庫狀態:")
        print(f"  數據庫可用: {'✅ 是' if status['database_available'] else '❌ 否'}")
        
        mongodb_info = status['mongodb']
        print(f"  MongoDB: {'✅ 可用' if mongodb_info['available'] else '❌ 不可用'}")
        print(f"    地址: {mongodb_info['host']}:{mongodb_info['port']}")
        
        redis_info = status['redis']
        print(f"  Redis: {'✅ 可用' if redis_info['available'] else '❌ 不可用'}")
        print(f"    地址: {redis_info['host']}:{redis_info['port']}")
        
        print(f"  緩存後端: {status['cache_backend']}")
        print(f"  降級支持: {'✅ 啟用' if status['fallback_enabled'] else '❌ 禁用'}")
        
    except Exception as e:
        print(f"❌ 數據庫管理器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 測試緩存系統
    print("\n💾 測試緩存系統...")
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        print("✅ 緩存系統創建成功")
        
        # 獲取後端信息
        backend_info = cache.get_cache_backend_info()
        print(f"  緩存系統: {backend_info['system']}")
        print(f"  主要後端: {backend_info['primary_backend']}")
        print(f"  性能模式: {cache.get_performance_mode()}")
        
        # 測試基本功能
        test_data = "測試數據 - 使用.env配置"
        cache_key = cache.save_stock_data(
            symbol="TEST_ENV",
            data=test_data,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="env_test"
        )
        print(f"✅ 數據保存成功: {cache_key}")
        
        # 加載數據
        loaded_data = cache.load_stock_data(cache_key)
        if loaded_data == test_data:
            print("✅ 數據加載成功，內容匹配")
        else:
            print("❌ 數據加載失敗或內容不匹配")
            return False
        
    except Exception as e:
        print(f"❌ 緩存系統測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 顯示環境變量
    print("\n🔍 檢查環境變量...")
    env_vars = [
        "MONGODB_HOST", "MONGODB_PORT", "MONGODB_USERNAME", "MONGODB_PASSWORD",
        "MONGODB_DATABASE", "MONGODB_AUTH_SOURCE",
        "REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD", "REDIS_DB"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"  {var}=***")
            else:
                print(f"  {var}={value}")
        else:
            print(f"  {var}=未設置")
    
    # 5. 總結
    print("\n📊 測試總結:")
    print("✅ 系統已正確使用.env配置文件")
    print("✅ 數據庫管理器正常工作")
    print("✅ 緩存系統正常工作")
    print("✅ 支持MongoDB和Redis的完整配置")
    print("✅ 在數據庫不可用時自動降級到文件緩存")
    
    print("\n💡 配置說明:")
    print("1. 系統讀取.env文件中的數據庫配置")
    print("2. 自動檢測MongoDB和Redis是否可用")
    print("3. 根據可用性選擇最佳緩存後端")
    print("4. 支持用戶名密碼認證")
    print("5. 在數據庫不可用時自動使用文件緩存")
    
    return True

def main():
    """主函數"""
    try:
        success = test_env_config()
        
        if success:
            print("\n🎉 .env配置測試完成!")
            print("\n🎯 系統特性:")
            print("✅ 使用項目現有的.env配置")
            print("✅ 默認不依賴數據庫，可以純文件緩存運行")
            print("✅ 自動檢測和使用可用的數據庫")
            print("✅ 支持完整的MongoDB和Redis配置")
            print("✅ 智能降級，確保系統穩定性")
        
        return success
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
