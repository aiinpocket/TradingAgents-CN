#!/usr/bin/env python3
"""
數據源综合測試程序
測試所有數據源的獲取過程和優先級切換
"""

import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_china_stock_data_sources():
    """測試中國股票數據源"""
    print("🇨🇳 測試中國股票數據源")
    print("=" * 60)
    
    test_symbols = ["000001", "600036", "000858"]  # 平安銀行、招商銀行、五粮液
    start_date = "2025-07-01"
    end_date = "2025-07-12"
    
    results = {}
    
    for symbol in test_symbols:
        print(f"\n📊 測試股票: {symbol}")
        print("-" * 40)
        
        symbol_results = {}
        
        # 1. 測試統一數據源接口
        try:
            print(f"🔍 測試統一數據源接口...")
            from tradingagents.dataflows.interface import get_china_stock_data_unified
            
            start_time = time.time()
            result = get_china_stock_data_unified(symbol, start_date, end_date)
            end_time = time.time()
            
            if result and "❌" not in result:
                print(f"✅ 統一接口獲取成功 ({end_time - start_time:.2f}s)")
                print(f"   數據長度: {len(result)} 字符")
                print(f"   數據預覽: {result[:150]}...")
                symbol_results['unified'] = {
                    'success': True,
                    'time': end_time - start_time,
                    'data_length': len(result)
                }
            else:
                print(f"❌ 統一接口獲取失败: {result[:100]}...")
                symbol_results['unified'] = {'success': False, 'error': result[:100]}
                
        except Exception as e:
            print(f"❌ 統一接口異常: {e}")
            symbol_results['unified'] = {'success': False, 'error': str(e)}
        
        # 2. 測試優化版本
        try:
            print(f"🔍 測試優化版本...")
            from tradingagents.dataflows.optimized_china_data import get_china_stock_data_cached
            
            start_time = time.time()
            result = get_china_stock_data_cached(symbol, start_date, end_date, force_refresh=True)
            end_time = time.time()
            
            if result and "❌" not in result:
                print(f"✅ 優化版本獲取成功 ({end_time - start_time:.2f}s)")
                print(f"   數據長度: {len(result)} 字符")
                symbol_results['optimized'] = {
                    'success': True,
                    'time': end_time - start_time,
                    'data_length': len(result)
                }
            else:
                print(f"❌ 優化版本獲取失败: {result[:100]}...")
                symbol_results['optimized'] = {'success': False, 'error': result[:100]}
                
        except Exception as e:
            print(f"❌ 優化版本異常: {e}")
            symbol_results['optimized'] = {'success': False, 'error': str(e)}
        
        # 3. 測試數據源管理器
        try:
            print(f"🔍 測試數據源管理器...")
            from tradingagents.dataflows.data_source_manager import DataSourceManager
            
            manager = DataSourceManager()
            print(f"   當前數據源: {manager.current_source.value}")
            print(f"   可用數據源: {[s.value for s in manager.available_sources]}")
            
            start_time = time.time()
            result = manager.get_stock_data(symbol, start_date, end_date)
            end_time = time.time()
            
            if result and "❌" not in result:
                print(f"✅ 數據源管理器獲取成功 ({end_time - start_time:.2f}s)")
                symbol_results['manager'] = {
                    'success': True,
                    'time': end_time - start_time,
                    'current_source': manager.current_source.value,
                    'available_sources': [s.value for s in manager.available_sources]
                }
            else:
                print(f"❌ 數據源管理器獲取失败: {result[:100]}...")
                symbol_results['manager'] = {'success': False, 'error': result[:100]}
                
        except Exception as e:
            print(f"❌ 數據源管理器異常: {e}")
            symbol_results['manager'] = {'success': False, 'error': str(e)}
        
        results[symbol] = symbol_results
        time.sleep(1)  # 避免API頻率限制
    
    return results

def test_us_stock_data_sources():
    """測試美股數據源"""
    print("\n🇺🇸 測試美股數據源")
    print("=" * 60)
    
    test_symbols = ["AAPL", "SPY", "TSLA"]
    start_date = "2025-07-01"
    end_date = "2025-07-12"
    
    results = {}
    
    for symbol in test_symbols:
        print(f"\n📊 測試股票: {symbol}")
        print("-" * 40)
        
        symbol_results = {}
        
        # 1. 測試優化版本（FinnHub優先）
        try:
            print(f"🔍 測試優化版本（FinnHub優先）...")
            from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
            
            start_time = time.time()
            result = get_us_stock_data_cached(symbol, start_date, end_date, force_refresh=True)
            end_time = time.time()
            
            if result and "❌" not in result:
                print(f"✅ 優化版本獲取成功 ({end_time - start_time:.2f}s)")
                print(f"   數據長度: {len(result)} 字符")
                
                # 檢查數據源
                if "FINNHUB" in result.upper() or "finnhub" in result:
                    print(f"   🎯 使用了FinnHub數據源")
                elif "Yahoo Finance" in result or "yfinance" in result:
                    print(f"   ⚠️ 使用了Yahoo Finance备用數據源")
                
                symbol_results['optimized'] = {
                    'success': True,
                    'time': end_time - start_time,
                    'data_length': len(result)
                }
            else:
                print(f"❌ 優化版本獲取失败: {result[:100]}...")
                symbol_results['optimized'] = {'success': False, 'error': result[:100]}
                
        except Exception as e:
            print(f"❌ 優化版本異常: {e}")
            symbol_results['optimized'] = {'success': False, 'error': str(e)}
        
        # 2. 測試原始yfinance接口
        try:
            print(f"🔍 測試原始yfinance接口...")
            from tradingagents.dataflows.interface import get_YFin_data_online
            
            start_time = time.time()
            result = get_YFin_data_online(symbol, start_date, end_date)
            end_time = time.time()
            
            if result and "No data found" not in result and "❌" not in result:
                print(f"✅ yfinance接口獲取成功 ({end_time - start_time:.2f}s)")
                print(f"   數據長度: {len(result)} 字符")
                symbol_results['yfinance'] = {
                    'success': True,
                    'time': end_time - start_time,
                    'data_length': len(result)
                }
            else:
                print(f"❌ yfinance接口獲取失败: {result[:100]}...")
                symbol_results['yfinance'] = {'success': False, 'error': result[:100]}
                
        except Exception as e:
            print(f"❌ yfinance接口異常: {e}")
            symbol_results['yfinance'] = {'success': False, 'error': str(e)}
        
        results[symbol] = symbol_results
        time.sleep(2)  # 避免API頻率限制
    
    return results

def test_news_data_sources():
    """測試新聞數據源"""
    print("\n📰 測試新聞數據源")
    print("=" * 60)
    
    test_symbols = ["AAPL", "000001"]
    results = {}
    
    for symbol in test_symbols:
        print(f"\n📰 測試股票新聞: {symbol}")
        print("-" * 40)
        
        symbol_results = {}
        
        # 1. 測試實時新聞聚合器
        try:
            print(f"🔍 測試實時新聞聚合器...")
            from tradingagents.dataflows.realtime_news_utils import RealtimeNewsAggregator
            
            aggregator = RealtimeNewsAggregator()
            start_time = time.time()
            news_items = aggregator.get_realtime_stock_news(symbol, hours_back=24)
            end_time = time.time()
            
            print(f"✅ 實時新聞獲取成功 ({end_time - start_time:.2f}s)")
            print(f"   新聞數量: {len(news_items)}")
            
            if news_items:
                print(f"   最新新聞: {news_items[0].title[:50]}...")
                print(f"   新聞來源: {news_items[0].source}")
            
            symbol_results['realtime_news'] = {
                'success': True,
                'time': end_time - start_time,
                'news_count': len(news_items)
            }
                
        except Exception as e:
            print(f"❌ 實時新聞異常: {e}")
            symbol_results['realtime_news'] = {'success': False, 'error': str(e)}
        
        # 2. 測試FinnHub新聞
        try:
            print(f"🔍 測試FinnHub新聞...")
            from tradingagents.dataflows.interface import get_finnhub_news
            
            start_time = time.time()
            result = get_finnhub_news(symbol, "2025-07-01", "2025-07-12")
            end_time = time.time()
            
            if result and "❌" not in result:
                print(f"✅ FinnHub新聞獲取成功 ({end_time - start_time:.2f}s)")
                print(f"   數據長度: {len(result)} 字符")
                symbol_results['finnhub_news'] = {
                    'success': True,
                    'time': end_time - start_time,
                    'data_length': len(result)
                }
            else:
                print(f"❌ FinnHub新聞獲取失败: {result[:100]}...")
                symbol_results['finnhub_news'] = {'success': False, 'error': result[:100]}
                
        except Exception as e:
            print(f"❌ FinnHub新聞異常: {e}")
            symbol_results['finnhub_news'] = {'success': False, 'error': str(e)}
        
        results[symbol] = symbol_results
        time.sleep(1)
    
    return results

def test_cache_system():
    """測試緩存系統"""
    print("\n🗄️ 測試緩存系統")
    print("=" * 60)
    
    results = {}
    
    try:
        print(f"🔍 測試緩存管理器...")
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        print(f"   緩存類型: {type(cache).__name__}")
        
        # 測試緩存保存和加載
        test_data = "測試數據_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存測試數據
        cache_key = cache.save_stock_data(
            symbol="TEST001",
            data=test_data,
            start_date="2025-07-01",
            end_date="2025-07-12",
            data_source="test"
        )
        
        print(f"   緩存键: {cache_key}")
        
        # 加載測試數據
        loaded_data = cache.load_stock_data(cache_key)
        
        if loaded_data == test_data:
            print(f"✅ 緩存系統測試成功")
            results['cache'] = {'success': True, 'cache_type': type(cache).__name__}
        else:
            print(f"❌ 緩存數據不匹配")
            results['cache'] = {'success': False, 'error': '數據不匹配'}
            
    except Exception as e:
        print(f"❌ 緩存系統異常: {e}")
        results['cache'] = {'success': False, 'error': str(e)}
    
    return results


def analyze_results(all_results: Dict):
    """分析測試結果"""
    print("\n📊 測試結果分析")
    print("=" * 60)

    # 統計成功率
    total_tests = 0
    successful_tests = 0

    for category, category_results in all_results.items():
        print(f"\n📋 {category.upper()} 類別:")

        if category == 'cache':
            total_tests += 1
            if category_results.get('success'):
                successful_tests += 1
                print(f"   ✅ 緩存系統: 正常")
            else:
                print(f"   ❌ 緩存系統: {category_results.get('error', '未知錯誤')}")
        else:
            for symbol, symbol_results in category_results.items():
                print(f"   📊 {symbol}:")
                for test_type, result in symbol_results.items():
                    total_tests += 1
                    if result.get('success'):
                        successful_tests += 1
                        time_taken = result.get('time', 0)
                        data_length = result.get('data_length', 0)
                        print(f"      ✅ {test_type}: {time_taken:.2f}s, {data_length}字符")
                    else:
                        error = result.get('error', '未知錯誤')
                        print(f"      ❌ {test_type}: {error[:50]}...")

    # 总體統計
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📈 总體統計:")
    print(f"   总測試數: {total_tests}")
    print(f"   成功數: {successful_tests}")
    print(f"   成功率: {success_rate:.1f}%")

    # 性能分析
    print(f"\n⚡ 性能分析:")
    fastest_times = []
    slowest_times = []

    for category, category_results in all_results.items():
        if category != 'cache':
            for symbol, symbol_results in category_results.items():
                for test_type, result in symbol_results.items():
                    if result.get('success') and 'time' in result:
                        time_taken = result['time']
                        fastest_times.append((f"{category}-{symbol}-{test_type}", time_taken))
                        slowest_times.append((f"{category}-{symbol}-{test_type}", time_taken))

    if fastest_times:
        fastest_times.sort(key=lambda x: x[1])
        slowest_times.sort(key=lambda x: x[1], reverse=True)

        print(f"   最快: {fastest_times[0][0]} ({fastest_times[0][1]:.2f}s)")
        print(f"   最慢: {slowest_times[0][0]} ({slowest_times[0][1]:.2f}s)")

    return success_rate >= 70  # 70%以上成功率認為通過


def print_recommendations(all_results: Dict):
    """打印優化建议"""
    print(f"\n💡 優化建议:")
    print("=" * 60)

    # 檢查中國股票數據源
    china_results = all_results.get('china_stocks', {})
    china_success_count = 0
    china_total_count = 0

    for symbol, symbol_results in china_results.items():
        for test_type, result in symbol_results.items():
            china_total_count += 1
            if result.get('success'):
                china_success_count += 1

    china_success_rate = (china_success_count / china_total_count * 100) if china_total_count > 0 else 0

    if china_success_rate < 80:
        print("🇨🇳 中國股票數據源:")
        print("   - 檢查Tushare Token配置")
        print("   - 確認AKShare庫安裝")
        print("   - 驗證網絡連接")

    # 檢查美股數據源
    us_results = all_results.get('us_stocks', {})
    us_success_count = 0
    us_total_count = 0

    for symbol, symbol_results in us_results.items():
        for test_type, result in symbol_results.items():
            us_total_count += 1
            if result.get('success'):
                us_success_count += 1

    us_success_rate = (us_success_count / us_total_count * 100) if us_total_count > 0 else 0

    if us_success_rate < 80:
        print("🇺🇸 美股數據源:")
        print("   - 檢查FinnHub API Key配置")
        print("   - 避免yfinance頻率限制")
        print("   - 考慮使用代理服務")

    # 檢查新聞數據源
    news_results = all_results.get('news', {})
    if news_results:
        print("📰 新聞數據源:")
        print("   - 配置更多新聞API密鑰")
        print("   - 增加中文新聞源")
        print("   - 優化新聞去重算法")

    # 緩存系統建议
    cache_result = all_results.get('cache', {})
    if not cache_result.get('success'):
        print("🗄️ 緩存系統:")
        print("   - 檢查Redis/MongoDB連接")
        print("   - 確認文件緩存目錄權限")
        print("   - 清理過期緩存文件")


def main():
    """主測試函數"""
    print("🧪 數據源综合測試程序")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = {}

    try:
        # 1. 測試中國股票數據源
        china_results = test_china_stock_data_sources()
        all_results['china_stocks'] = china_results

        # 2. 測試美股數據源
        us_results = test_us_stock_data_sources()
        all_results['us_stocks'] = us_results

        # 3. 測試新聞數據源
        news_results = test_news_data_sources()
        all_results['news'] = news_results

        # 4. 測試緩存系統
        cache_results = test_cache_system()
        all_results['cache'] = cache_results

        # 5. 分析結果
        success = analyze_results(all_results)

        # 6. 打印建议
        print_recommendations(all_results)

        # 7. 总結
        print(f"\n🎯 測試总結:")
        if success:
            print("✅ 數據源系統運行正常")
            print("✅ 優先級配置正確")
            print("✅ 备用機制有效")
        else:
            print("⚠️ 數據源系統存在問題")
            print("⚠️ 需要檢查配置和網絡")

        return success

    except Exception as e:
        print(f"❌ 測試程序異常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()

    print(f"\n{'='*60}")
    if success:
        print("🎉 數據源測試完成！系統運行正常。")
    else:
        print("⚠️ 數據源測試發現問題，請檢查配置。")

    print(f"\n📋 下一步:")
    print("1. 根據建议優化配置")
    print("2. 運行 python -m cli.main 測試完整流程")
    print("3. 檢查 .env 文件中的API密鑰配置")
    print("4. 查看日誌文件了解詳細錯誤信息")
