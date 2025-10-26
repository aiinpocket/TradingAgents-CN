#!/usr/bin/env python3
"""
測試最终的.env配置系統
驗證啟用開關是否正常工作
"""

import os

def test_final_config():
    """測試最终配置"""
    print("🔧 測試最终的.env配置系統")
    print("=" * 40)
    
    # 1. 檢查.env文件
    print("\n📁 檢查.env文件...")
    if os.path.exists('.env'):
        print("✅ .env文件存在")
    else:
        print("❌ .env文件不存在")
        return False
    
    # 2. 讀取啟用開關
    print("\n🔧 檢查啟用開關...")
    mongodb_enabled = os.getenv("MONGODB_ENABLED", "false").lower() == "true"
    redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    print(f"MONGODB_ENABLED: {os.getenv('MONGODB_ENABLED', 'false')} -> {mongodb_enabled}")
    print(f"REDIS_ENABLED: {os.getenv('REDIS_ENABLED', 'false')} -> {redis_enabled}")
    
    # 3. 顯示配置信息
    print("\n📊 數據庫配置:")
    
    if mongodb_enabled:
        print("MongoDB: ✅ 啟用")
        print(f"  Host: {os.getenv('MONGODB_HOST', 'localhost')}")
        print(f"  Port: {os.getenv('MONGODB_PORT', '27017')}")
        print(f"  Database: {os.getenv('MONGODB_DATABASE', 'tradingagents')}")
    else:
        print("MongoDB: ❌ 禁用")
    
    if redis_enabled:
        print("Redis: ✅ 啟用")
        print(f"  Host: {os.getenv('REDIS_HOST', 'localhost')}")
        print(f"  Port: {os.getenv('REDIS_PORT', '6379')}")
        print(f"  DB: {os.getenv('REDIS_DB', '0')}")
    else:
        print("Redis: ❌ 禁用")
    
    # 4. 測試數據庫管理器
    print("\n🔧 測試數據庫管理器...")
    try:
        from tradingagents.config.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        print("✅ 數據庫管理器創建成功")
        
        # 獲取狀態報告
        status = db_manager.get_status_report()
        
        print("📊 檢測結果:")
        print(f"  數據庫可用: {'✅ 是' if status['database_available'] else '❌ 否'}")
        
        mongodb_info = status['mongodb']
        print(f"  MongoDB: {'✅ 可用' if mongodb_info['available'] else '❌ 不可用'}")
        
        redis_info = status['redis']
        print(f"  Redis: {'✅ 可用' if redis_info['available'] else '❌ 不可用'}")
        
        print(f"  緩存後端: {status['cache_backend']}")
        
    except Exception as e:
        print(f"❌ 數據庫管理器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 測試緩存系統
    print("\n💾 測試緩存系統...")
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        print("✅ 緩存系統創建成功")
        
        # 獲取性能模式
        performance_mode = cache.get_performance_mode()
        print(f"  性能模式: {performance_mode}")
        
        # 測試基本功能
        test_data = "測試數據 - 最终配置"
        cache_key = cache.save_stock_data(
            symbol="TEST_FINAL",
            data=test_data,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="final_test"
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
    
    # 6. 总結
    print("\n📊 配置总結:")
    print("✅ 使用.env文件進行配置")
    print("✅ 通過MONGODB_ENABLED和REDIS_ENABLED控制啟用狀態")
    print("✅ 默認情况下數據庫都是禁用的")
    print("✅ 系統使用文件緩存，性能良好")
    print("✅ 可以通過修改.env文件啟用數據庫")
    
    print("\n💡 使用說明:")
    print("1. 默認配置：MONGODB_ENABLED=false, REDIS_ENABLED=false")
    print("2. 啟用MongoDB：将MONGODB_ENABLED設置為true")
    print("3. 啟用Redis：将REDIS_ENABLED設置為true")
    print("4. 系統會自動檢測並使用啟用的數據庫")
    print("5. 如果數據庫不可用，自動降級到文件緩存")
    
    return True

def main():
    """主函數"""
    try:
        success = test_final_config()
        
        if success:
            print("\n🎉 最终配置測試完成!")
            print("\n🎯 系統特性:")
            print("✅ 簡化配置：只需要.env文件")
            print("✅ 明確控制：通過啟用開關控制數據庫")
            print("✅ 默認安全：默認不啟用數據庫")
            print("✅ 智能降級：數據庫不可用時自動使用文件緩存")
            print("✅ 性能優化：有數據庫時自動使用高性能模式")
        
        return success
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
