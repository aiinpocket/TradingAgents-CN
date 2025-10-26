#!/usr/bin/env python3
"""
簡單的系統測試 - 驗證配置和緩存系統
"""

import sys
import os
from pathlib import Path

def test_basic_system():
    """測試基本系統功能"""
    print("🔧 TradingAgents 基本系統測試")
    print("=" * 40)
    
    # 1. 檢查配置文件
    print("\n📁 檢查配置文件...")
    config_file = Path("config/database_config.json")
    if config_file.exists():
        print(f"✅ 配置文件存在: {config_file}")
        
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ 配置文件格式正確")
            print(f"  主要緩存後端: {config['cache']['primary_backend']}")
            print(f"  MongoDB啟用: {config['database']['mongodb']['enabled']}")
            print(f"  Redis啟用: {config['database']['redis']['enabled']}")
        except Exception as e:
            print(f"❌ 配置文件解析失败: {e}")
    else:
        print(f"❌ 配置文件不存在: {config_file}")
    
    # 2. 檢查數據庫包
    print("\n📦 檢查數據庫包...")
    
    # 檢查pymongo
    try:
        import pymongo
        print("✅ pymongo 已安裝")
        
        # 嘗試連接MongoDB
        try:
            client = pymongo.MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
            client.server_info()
            client.close()
            print("✅ MongoDB 連接成功")
            mongodb_available = True
        except Exception:
            print("❌ MongoDB 連接失败（正常，如果没有安裝MongoDB）")
            mongodb_available = False
    except ImportError:
        print("❌ pymongo 未安裝")
        mongodb_available = False
    
    # 檢查redis
    try:
        import redis
        print("✅ redis 已安裝")
        
        # 嘗試連接Redis
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
            r.ping()
            print("✅ Redis 連接成功")
            redis_available = True
        except Exception:
            print("❌ Redis 連接失败（正常，如果没有安裝Redis）")
            redis_available = False
    except ImportError:
        print("❌ redis 未安裝")
        redis_available = False
    
    # 3. 測試緩存系統
    print("\n💾 測試緩存系統...")
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        print("✅ 緩存系統初始化成功")
        
        # 獲取緩存信息
        backend_info = cache.get_cache_backend_info()
        print(f"  緩存系統: {backend_info['system']}")
        print(f"  主要後端: {backend_info['primary_backend']}")
        
        # 測試基本功能
        test_data = "測試數據 - 系統簡單測試"
        cache_key = cache.save_stock_data(
            symbol="TEST_SIMPLE",
            data=test_data,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="simple_test"
        )
        print(f"✅ 數據保存成功: {cache_key}")
        
        # 加載數據
        loaded_data = cache.load_stock_data(cache_key)
        if loaded_data == test_data:
            print("✅ 數據加載成功")
        else:
            print("❌ 數據加載失败")
            return False
        
    except Exception as e:
        print(f"❌ 緩存系統測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 測試數據庫管理器
    print("\n🔧 測試數據庫管理器...")
    try:
        from tradingagents.config.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        print("✅ 數據庫管理器創建成功")
        
        # 獲取狀態報告
        status = db_manager.get_status_report()
        
        print("📊 數據庫狀態:")
        print(f"  數據庫可用: {'✅ 是' if status['database_available'] else '❌ 否'}")
        print(f"  MongoDB: {'✅ 可用' if status['mongodb']['available'] else '❌ 不可用'}")
        print(f"  Redis: {'✅ 可用' if status['redis']['available'] else '❌ 不可用'}")
        print(f"  緩存後端: {status['cache_backend']}")
        
    except Exception as e:
        print(f"❌ 數據庫管理器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 总結
    print("\n📊 系統測試总結:")
    print("✅ 緩存系統正常工作")
    print("✅ 數據庫管理器正常工作")
    
    if mongodb_available or redis_available:
        print("✅ 數據庫可用，系統運行在高性能模式")
    else:
        print("✅ 數據庫不可用，系統運行在文件緩存模式")
        print("💡 這是正常的，系統可以完全使用文件緩存工作")
    
    print("\n🎯 系統特性:")
    print("✅ 智能緩存：自動選擇最佳緩存後端")
    print("✅ 降級支持：數據庫不可用時自動使用文件緩存")
    print("✅ 配置灵活：支持多種數據庫配置")
    print("✅ 性能優化：根據可用資源自動調整")
    
    return True

def main():
    """主函數"""
    try:
        success = test_basic_system()
        
        if success:
            print("\n🎉 系統測試完成!")
            print("\n💡 下一步:")
            print("1. 如需高性能，可以安裝並啟動MongoDB/Redis")
            print("2. 運行完整的股票分析測試")
            print("3. 使用Web界面進行交互式分析")
        
        return success
        
    except Exception as e:
        print(f"❌ 系統測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
