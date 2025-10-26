#!/usr/bin/env python3
"""
簡化版數據源測試程序
快速測試主要數據源的可用性
"""

import sys
import os
import time
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_china_data_source():
    """測試中國股票數據源"""
    print("🇨🇳 測試中國股票數據源")
    print("-" * 40)
    
    try:
        # 測試數據源管理器
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        
        manager = DataSourceManager()
        print(f"✅ 數據源管理器初始化成功")
        print(f"   當前數據源: {manager.current_source.value}")
        print(f"   可用數據源: {[s.value for s in manager.available_sources]}")
        
        # 測試獲取數據
        print(f"\n📊 測試獲取平安銀行(000001)數據...")
        start_time = time.time()
        result = manager.get_stock_data("000001", "2025-07-01", "2025-07-12")
        end_time = time.time()
        
        if result and "❌" not in result:
            print(f"✅ 數據獲取成功 ({end_time - start_time:.2f}s)")
            print(f"   數據長度: {len(result)} 字符")
            print(f"   數據預覽: {result[:100]}...")
            return True
        else:
            print(f"❌ 數據獲取失败: {result[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ 中國股票數據源測試失败: {e}")
        return False

def test_us_data_source():
    """測試美股數據源"""
    print("\n🇺🇸 測試美股數據源")
    print("-" * 40)
    
    try:
        # 測試優化版本
        from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
        
        print(f"📊 測試獲取苹果(AAPL)數據...")
        start_time = time.time()
        result = get_us_stock_data_cached("AAPL", "2025-07-01", "2025-07-12", force_refresh=True)
        end_time = time.time()
        
        if result and "❌" not in result:
            print(f"✅ 數據獲取成功 ({end_time - start_time:.2f}s)")
            print(f"   數據長度: {len(result)} 字符")
            
            # 檢查數據源
            if "FINNHUB" in result.upper() or "finnhub" in result:
                print(f"   🎯 使用了FinnHub數據源")
            elif "Yahoo Finance" in result or "yfinance" in result:
                print(f"   ⚠️ 使用了Yahoo Finance备用數據源")
            
            print(f"   數據預覽: {result[:100]}...")
            return True
        else:
            print(f"❌ 數據獲取失败: {result[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ 美股數據源測試失败: {e}")
        return False

def test_cache_system():
    """測試緩存系統"""
    print("\n🗄️ 測試緩存系統")
    print("-" * 40)
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        print(f"✅ 緩存管理器初始化成功")
        print(f"   緩存類型: {type(cache).__name__}")
        
        # 測試緩存操作
        test_data = f"測試數據_{datetime.now().strftime('%H%M%S')}"
        
        # 保存測試數據
        cache_key = cache.save_stock_data(
            symbol="TEST001",
            data=test_data,
            start_date="2025-07-01",
            end_date="2025-07-12",
            data_source="test"
        )
        
        # 加載測試數據
        loaded_data = cache.load_stock_data(cache_key)
        
        if loaded_data == test_data:
            print(f"✅ 緩存讀寫測試成功")
            print(f"   緩存键: {cache_key}")
            return True
        else:
            print(f"❌ 緩存數據不匹配")
            return False
            
    except Exception as e:
        print(f"❌ 緩存系統測試失败: {e}")
        return False

def test_api_keys():
    """測試API密鑰配置"""
    print("\n🔑 測試API密鑰配置")
    print("-" * 40)
    
    api_keys = {
        'TUSHARE_TOKEN': os.getenv('TUSHARE_TOKEN'),
        'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY'),
        'DASHSCOPE_API_KEY': os.getenv('DASHSCOPE_API_KEY'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
    }
    
    configured_count = 0
    total_count = len(api_keys)
    
    for key_name, key_value in api_keys.items():
        if key_value:
            print(f"✅ {key_name}: 已配置")
            configured_count += 1
        else:
            print(f"❌ {key_name}: 未配置")
    
    print(f"\n📊 API密鑰配置率: {configured_count}/{total_count} ({configured_count/total_count*100:.1f}%)")
    
    return configured_count >= 2  # 至少需要2個API密鑰

def main():
    """主測試函數"""
    print("🧪 數據源簡化測試程序")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 1. 測試API密鑰配置
    api_result = test_api_keys()
    results.append(('API密鑰配置', api_result))
    
    # 2. 測試緩存系統
    cache_result = test_cache_system()
    results.append(('緩存系統', cache_result))
    
    # 3. 測試中國股票數據源
    china_result = test_china_data_source()
    results.append(('中國股票數據源', china_result))
    
    # 4. 測試美股數據源
    us_result = test_us_data_source()
    results.append(('美股數據源', us_result))
    
    # 統計結果
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📊 測試結果汇总")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 总體結果:")
    print(f"   通過: {passed}/{total}")
    print(f"   成功率: {success_rate:.1f}%")
    
    if success_rate >= 75:
        print(f"\n🎉 數據源系統運行良好！")
        print(f"✅ 主要功能正常")
        print(f"✅ 可以開始使用系統")
    else:
        print(f"\n⚠️ 數據源系統需要優化")
        print(f"❌ 請檢查失败的組件")
        print(f"❌ 參考錯誤信息進行修複")
    
    print(f"\n💡 建议:")
    if not api_result:
        print("- 配置更多API密鑰以提高數據源可用性")
    if not cache_result:
        print("- 檢查緩存系統配置和權限")
    if not china_result:
        print("- 檢查Tushare Token或AKShare安裝")
    if not us_result:
        print("- 檢查FinnHub API Key或網絡連接")
    
    return success_rate >= 75

if __name__ == "__main__":
    try:
        success = main()
        
        print(f"\n{'='*50}")
        if success:
            print("🎯 測試完成！可以運行完整分析流程。")
            print("   下一步: python -m cli.main")
        else:
            print("🔧 需要修複配置後再次測試。")
            print("   重新測試: python tests/test_data_sources_simple.py")
            
    except Exception as e:
        print(f"❌ 測試程序異常: {e}")
        import traceback
        traceback.print_exc()
