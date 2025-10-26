#!/usr/bin/env python3
"""
緩存優化功能測試
測試美股和A股數據的緩存策略和性能
"""

import os
import sys
import time
from datetime import datetime, timedelta

# 添加項目根目錄到路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_cache_manager():
    """測試緩存管理器基本功能"""
    print("🧪 測試緩存管理器...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        print(f"✅ 緩存管理器初始化成功")
        print(f"📁 緩存目錄: {cache.cache_dir}")
        
        # 測試緩存配置
        if hasattr(cache, 'cache_config'):
            print(f"⚙️ 緩存配置:")
            for config_name, config_data in cache.cache_config.items():
                print(f"  - {config_name}: TTL={config_data.get('ttl_hours')}h, 描述={config_data.get('description')}")
        
        # 測試緩存統計
        stats = cache.get_cache_stats()
        print(f"📊 緩存統計: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 緩存管理器測試失败: {e}")
        return False


def test_us_stock_cache():
    """測試美股數據緩存"""
    print("\n🇺🇸 測試美股數據緩存...")
    
    try:
        from tradingagents.dataflows.optimized_us_data import get_optimized_us_data_provider
        
        provider = get_optimized_us_data_provider()
        symbol = "AAPL"
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📈 測試股票: {symbol} ({start_date} 到 {end_date})")
        
        # 第一次調用（應该從API獲取）
        print("🌐 第一次調用（從API獲取）...")
        start_time = time.time()
        result1 = provider.get_stock_data(symbol, start_date, end_date)
        time1 = time.time() - start_time
        print(f"⏱️ 第一次調用耗時: {time1:.2f}秒")
        
        # 第二次調用（應该從緩存獲取）
        print("⚡ 第二次調用（從緩存獲取）...")
        start_time = time.time()
        result2 = provider.get_stock_data(symbol, start_date, end_date)
        time2 = time.time() - start_time
        print(f"⏱️ 第二次調用耗時: {time2:.2f}秒")
        
        # 驗證結果一致性
        if result1 == result2:
            print("✅ 緩存數據一致性驗證通過")
        else:
            print("⚠️ 緩存數據不一致")
        
        # 性能提升
        if time2 < time1:
            improvement = ((time1 - time2) / time1) * 100
            print(f"🚀 緩存性能提升: {improvement:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 美股緩存測試失败: {e}")
        return False


def test_china_stock_cache():
    """測試A股數據緩存"""
    print("\n🇨🇳 測試A股數據緩存...")
    
    try:
        from tradingagents.dataflows.optimized_china_data import get_optimized_china_data_provider
        
        provider = get_optimized_china_data_provider()
        symbol = "000001"
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📈 測試股票: {symbol} ({start_date} 到 {end_date})")
        
        # 第一次調用（應该從API獲取）
        print("🌐 第一次調用（從Tushare數據接口獲取）...")
        start_time = time.time()
        result1 = provider.get_stock_data(symbol, start_date, end_date)
        time1 = time.time() - start_time
        print(f"⏱️ 第一次調用耗時: {time1:.2f}秒")
        
        # 第二次調用（應该從緩存獲取）
        print("⚡ 第二次調用（從緩存獲取）...")
        start_time = time.time()
        result2 = provider.get_stock_data(symbol, start_date, end_date)
        time2 = time.time() - start_time
        print(f"⏱️ 第二次調用耗時: {time2:.2f}秒")
        
        # 驗證結果一致性
        if result1 == result2:
            print("✅ 緩存數據一致性驗證通過")
        else:
            print("⚠️ 緩存數據不一致")
        
        # 性能提升
        if time2 < time1:
            improvement = ((time1 - time2) / time1) * 100
            print(f"🚀 緩存性能提升: {improvement:.1f}%")
        
        # 測試基本面數據緩存
        print("\n📊 測試A股基本面數據緩存...")
        start_time = time.time()
        fundamentals1 = provider.get_fundamentals_data(symbol)
        time1 = time.time() - start_time
        print(f"⏱️ 基本面數據第一次調用耗時: {time1:.2f}秒")
        
        start_time = time.time()
        fundamentals2 = provider.get_fundamentals_data(symbol)
        time2 = time.time() - start_time
        print(f"⏱️ 基本面數據第二次調用耗時: {time2:.2f}秒")
        
        if fundamentals1 == fundamentals2:
            print("✅ 基本面數據緩存一致性驗證通過")
        
        return True
        
    except Exception as e:
        print(f"❌ A股緩存測試失败: {e}")
        return False


def test_cache_ttl():
    """測試緩存TTL功能"""
    print("\n⏰ 測試緩存TTL功能...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        
        # 測試美股緩存TTL
        us_cache_key = cache.find_cached_stock_data(
            symbol="AAPL",
            start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            data_source="yfinance"
        )
        
        if us_cache_key:
            is_valid = cache.is_cache_valid(us_cache_key, symbol="AAPL", data_type="stock_data")
            print(f"📈 美股緩存有效性: {'✅ 有效' if is_valid else '❌ 過期'}")
        
        # 測試A股緩存TTL
        china_cache_key = cache.find_cached_stock_data(
            symbol="000001",
            start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            data_source="tdx"
        )
        
        if china_cache_key:
            is_valid = cache.is_cache_valid(china_cache_key, symbol="000001", data_type="stock_data")
            print(f"📈 A股緩存有效性: {'✅ 有效' if is_valid else '❌ 過期'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 緩存TTL測試失败: {e}")
        return False


def test_cache_cleanup():
    """測試緩存清理功能"""
    print("\n🧹 測試緩存清理功能...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        
        # 獲取清理前的統計
        stats_before = cache.get_cache_stats()
        print(f"📊 清理前統計: {stats_before}")
        
        # 執行清理（清理7天前的緩存）
        print("🧹 執行緩存清理...")
        cache.clear_old_cache(max_age_days=7)
        
        # 獲取清理後的統計
        stats_after = cache.get_cache_stats()
        print(f"📊 清理後統計: {stats_after}")
        
        # 計算清理效果
        files_removed = stats_before['total_files'] - stats_after['total_files']
        size_freed = stats_before['total_size_mb'] - stats_after['total_size_mb']
        
        print(f"🗑️ 清理結果: 刪除 {files_removed} 個文件，釋放 {size_freed:.2f} MB 空間")
        
        return True
        
    except Exception as e:
        print(f"❌ 緩存清理測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🚀 開始緩存優化功能測試")
    print("=" * 50)
    
    test_results = []
    
    # 測試緩存管理器
    test_results.append(("緩存管理器", test_cache_manager()))
    
    # 測試美股緩存
    test_results.append(("美股數據緩存", test_us_stock_cache()))
    
    # 測試A股緩存
    test_results.append(("A股數據緩存", test_china_stock_cache()))
    
    # 測試緩存TTL
    test_results.append(("緩存TTL", test_cache_ttl()))
    
    # 測試緩存清理
    test_results.append(("緩存清理", test_cache_cleanup()))
    
    # 輸出測試結果
    print("\n" + "=" * 50)
    print("📋 測試結果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有緩存優化功能測試通過！")
    else:
        print("⚠️ 部分測試失败，請檢查系統配置")


if __name__ == "__main__":
    main()
