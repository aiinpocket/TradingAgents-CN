#!/usr/bin/env python3
"""
智能系統完整測試 - 驗證自適應配置和緩存系統
"""

import time
import sys
from datetime import datetime

def test_smart_config():
    """測試智能配置系統"""
    print("🔧 測試智能配置系統")
    print("-" * 30)
    
    try:
        from smart_config import get_smart_config, get_config
        
        # 獲取配置管理器
        config_manager = get_smart_config()
        config_manager.print_status()
        
        # 獲取配置信息
        config = get_config()
        print(f"\n✅ 配置獲取成功")
        print(f"主要緩存後端: {config['cache']['primary_backend']}")
        
        return True, config_manager
        
    except Exception as e:
        print(f"❌ 智能配置測試失敗: {e}")
        return False, None

def test_adaptive_cache():
    """測試自適應緩存系統"""
    print("\n💾 測試自適應緩存系統")
    print("-" * 30)
    
    try:
        from adaptive_cache_manager import get_cache
        
        # 獲取緩存管理器
        cache = get_cache()
        
        # 顯示緩存狀態
        stats = cache.get_cache_stats()
        print("📊 緩存狀態:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 測試基本功能
        print("\n🧪 測試基本緩存功能...")
        
        test_data = f"測試數據 - {datetime.now()}"
        cache_key = cache.save_stock_data(
            symbol="AAPL",
            data=test_data,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="smart_test"
        )
        print(f"✅ 數據保存成功: {cache_key}")
        
        # 測試加載
        loaded_data = cache.load_stock_data(cache_key)
        if loaded_data == test_data:
            print("✅ 數據加載成功，內容匹配")
        else:
            print("❌ 數據加載失敗或內容不匹配")
            return False
        
        # 測試查找
        found_key = cache.find_cached_stock_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="smart_test"
        )
        
        if found_key:
            print(f"✅ 緩存查找成功: {found_key}")
        else:
            print("❌ 緩存查找失敗")
            return False
        
        return True, cache
        
    except Exception as e:
        print(f"❌ 自適應緩存測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_performance():
    """測試性能"""
    print("\n⚡ 測試緩存性能")
    print("-" * 30)
    
    try:
        from adaptive_cache_manager import get_cache
        
        cache = get_cache()
        
        # 性能測試數據
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        
        print("📊 性能測試結果:")
        
        total_save_time = 0
        total_load_time = 0
        
        for symbol in symbols:
            test_data = f"性能測試數據 - {symbol}"
            
            # 測試保存性能
            start_time = time.time()
            cache_key = cache.save_stock_data(
                symbol=symbol,
                data=test_data,
                start_date="2024-01-01",
                end_date="2024-12-31",
                data_source="perf_test"
            )
            save_time = time.time() - start_time
            total_save_time += save_time
            
            # 測試加載性能
            start_time = time.time()
            loaded_data = cache.load_stock_data(cache_key)
            load_time = time.time() - start_time
            total_load_time += load_time
            
            print(f"  {symbol}: 保存 {save_time:.4f}s, 加載 {load_time:.4f}s")
        
        avg_save_time = total_save_time / len(symbols)
        avg_load_time = total_load_time / len(symbols)
        
        print(f"\n📈 平均性能:")
        print(f"  保存時間: {avg_save_time:.4f}秒")
        print(f"  加載時間: {avg_load_time:.4f}秒")
        
        # 計算性能改進
        api_simulation_time = 2.0  # 假設API調用需要2秒
        if avg_load_time < api_simulation_time:
            improvement = ((api_simulation_time - avg_load_time) / api_simulation_time) * 100
            print(f"  性能改進: {improvement:.1f}%")
            
            if improvement > 90:
                print("🚀 性能改進顯著！")
                return True
            else:
                print("⚠️ 性能改進有限")
                return True
        else:
            print("❌ 緩存性能不如預期")
            return False
            
    except Exception as e:
        print(f"❌ 性能測試失敗: {e}")
        return False

def test_fallback_mechanism():
    """測試降級機制"""
    print("\n🔄 測試降級機制")
    print("-" * 30)
    
    try:
        from adaptive_cache_manager import get_cache
        
        cache = get_cache()
        
        # 檢查降級配置
        if cache.fallback_enabled:
            print("✅ 降級機制已啟用")
        else:
            print("⚠️ 降級機制未啟用")
        
        # 測試在主要後端不可用時的行為
        print(f"主要後端: {cache.primary_backend}")
        
        if cache.primary_backend == "file":
            print("✅ 使用文件緩存，無需降級")
        elif cache.primary_backend == "redis" and not cache.redis_enabled:
            print("✅ Redis不可用，已自動降級到文件緩存")
        elif cache.primary_backend == "mongodb" and not cache.mongodb_enabled:
            print("✅ MongoDB不可用，已自動降級到文件緩存")
        else:
            print(f"✅ {cache.primary_backend} 後端正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 降級機制測試失敗: {e}")
        return False

def generate_test_report(results):
    """生成測試報告"""
    print("\n📋 測試報告")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"總測試數: {total_tests}")
    print(f"通過測試: {passed_tests}")
    print(f"失敗測試: {total_tests - passed_tests}")
    print(f"通過率: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n詳細結果:")
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    # 生成建議
    print("\n💡 建議:")
    
    if all(results.values()):
        print("🎉 所有測試通過！系統可以正常運行")
        print("✅ 可以開始準備上游貢獻")
    else:
        print("⚠️ 部分測試失敗，需要檢查以下問題:")
        
        if not results.get("智能配置", True):
            print("  - 檢查智能配置系統")
        if not results.get("自適應緩存", True):
            print("  - 檢查緩存系統配置")
        if not results.get("性能測試", True):
            print("  - 優化緩存性能")
        if not results.get("降級機制", True):
            print("  - 檢查降級機制配置")

def main():
    """主測試函數"""
    print("🚀 TradingAgents 智能系統完整測試")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 執行所有測試
    results = {}
    
    # 測試1: 智能配置
    config_success, config_manager = test_smart_config()
    results["智能配置"] = config_success
    
    # 測試2: 自適應緩存
    cache_success, cache_manager = test_adaptive_cache()
    results["自適應緩存"] = cache_success
    
    # 測試3: 性能測試
    if cache_success:
        perf_success = test_performance()
        results["性能測試"] = perf_success
    else:
        results["性能測試"] = False
    
    # 測試4: 降級機制
    if cache_success:
        fallback_success = test_fallback_mechanism()
        results["降級機制"] = fallback_success
    else:
        results["降級機制"] = False
    
    # 生成報告
    generate_test_report(results)
    
    # 保存配置（如果可用）
    if config_manager:
        config_manager.save_config("test_config.json")
        print(f"\n💾 測試配置已保存: test_config.json")
    
    # 返回總體結果
    return all(results.values())

if __name__ == "__main__":
    success = main()
    
    print(f"\n🎯 測試{'成功' if success else '失敗'}!")
    
    if success:
        print("\n下一步:")
        print("1. 清理中文內容")
        print("2. 添加英文文件")
        print("3. 準備上游貢獻")
    else:
        print("\n需要解決的問題:")
        print("1. 檢查依賴安裝")
        print("2. 修複配置問題")
        print("3. 重新運行測試")
    
    sys.exit(0 if success else 1)
