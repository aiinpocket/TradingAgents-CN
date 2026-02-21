#!/usr/bin/env python3
"""
測試最終的.env配置系統
驗證啟用開關是否正常工作
"""

import os

def test_final_config():
    """測試最終配置"""
    print(" 測試最終的.env配置系統")
    print("=" * 40)
    
    # 1. 檢查.env 檔案
    print("\n 檢查.env 檔案...")
    if os.path.exists('.env'):
        print(" .env 檔案存在")
    else:
        print(" .env 檔案不存在")
        return False
    
    # 2. 讀取啟用開關
    print("\n 檢查啟用開關...")
    mongodb_enabled = os.getenv("MONGODB_ENABLED", "false").lower() == "true"
    redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    print(f"MONGODB_ENABLED: {os.getenv('MONGODB_ENABLED', 'false')} -> {mongodb_enabled}")
    print(f"REDIS_ENABLED: {os.getenv('REDIS_ENABLED', 'false')} -> {redis_enabled}")
    
    # 3. 顯示配置資訊
    print("\n 資料庫配置:")
    
    if mongodb_enabled:
        print("MongoDB:  啟用")
        print(f"  Host: {os.getenv('MONGODB_HOST', 'localhost')}")
        print(f"  Port: {os.getenv('MONGODB_PORT', '27017')}")
        print(f"  Database: {os.getenv('MONGODB_DATABASE', 'tradingagents')}")
    else:
        print("MongoDB:  禁用")
    
    if redis_enabled:
        print("Redis:  啟用")
        print(f"  Host: {os.getenv('REDIS_HOST', 'localhost')}")
        print(f"  Port: {os.getenv('REDIS_PORT', '6379')}")
        print(f"  DB: {os.getenv('REDIS_DB', '0')}")
    else:
        print("Redis:  禁用")
    
    # 4. 測試資料庫管理器
    print("\n 測試資料庫管理器...")
    try:
        from tradingagents.config.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        print(" 資料庫管理器建立成功")
        
        # 取得狀態報告
        status = db_manager.get_status_report()
        
        print(" 檢測結果:")
        print(f"  資料庫可用: {' 是' if status['database_available'] else ' 否'}")
        
        mongodb_info = status['mongodb']
        print(f"  MongoDB: {' 可用' if mongodb_info['available'] else ' 不可用'}")
        
        redis_info = status['redis']
        print(f"  Redis: {' 可用' if redis_info['available'] else ' 不可用'}")
        
        print(f"  快取後端: {status['cache_backend']}")
        
    except Exception as e:
        print(f" 資料庫管理器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 測試快取系統
    print("\n 測試快取系統...")
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        print(" 快取系統建立成功")
        
        # 取得性能模式
        performance_mode = cache.get_performance_mode()
        print(f"  性能模式: {performance_mode}")
        
        # 測試基本功能
        test_data = "測試資料 - 最終配置"
        cache_key = cache.save_stock_data(
            symbol="TEST_FINAL",
            data=test_data,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="final_test"
        )
        print(f" 資料保存成功: {cache_key}")
        
        # 載入資料
        loaded_data = cache.load_stock_data(cache_key)
        if loaded_data == test_data:
            print(" 資料載入成功")
        else:
            print(" 資料載入失敗")
            return False
        
    except Exception as e:
        print(f" 快取系統測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. 總結
    print("\n 配置總結:")
    print(" 使用.env 檔案進行配置")
    print(" 通過MONGODB_ENABLED和REDIS_ENABLED控制啟用狀態")
    print(" 預設情況下資料庫都是禁用的")
    print(" 系統使用檔案快取，性能良好")
    print(" 可以通過修改.env 檔案啟用資料庫")
    
    print("\n 使用說明:")
    print("1. 預設配置：MONGODB_ENABLED=false, REDIS_ENABLED=false")
    print("2. 啟用MongoDB：將MONGODB_ENABLED設定為true")
    print("3. 啟用Redis：將REDIS_ENABLED設定為true")
    print("4. 系統會自動檢測並使用啟用的資料庫")
    print("5. 如果資料庫不可用，自動降級到檔案快取")
    
    return True

def main():
    """主函式"""
    try:
        success = test_final_config()
        
        if success:
            print("\n 最終配置測試完成!")
            print("\n 系統特性:")
            print(" 簡化配置：只需要.env 檔案")
            print(" 明確控制：通過啟用開關控制資料庫")
            print(" 預設安全：預設不啟用資料庫")
            print(" 智能降級：資料庫不可用時自動使用檔案快取")
            print(" 性能優化：有資料庫時自動使用高性能模式")
        
        return success
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
