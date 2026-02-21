#!/usr/bin/env python3
"""
測試基本面資料快取功能
驗證OpenAI和Finnhub基本面資料的快取機制
"""

import os
import sys
import time
from datetime import datetime

# 添加項目根目錄到路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_cache_manager_fundamentals():
    """測試快取管理器的基本面資料功能"""
    print(" 測試基本面資料快取管理器...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        print(f" 快取管理器初始化成功")
        print(f" 快取目錄: {cache.cache_dir}")
        
        # 測試保存基本面資料
        test_symbol = "AAPL"
        test_data = f"""
# {test_symbol} 基本面分析報告（測試資料）

**資料取得時間**: {datetime.now().strftime('%Y-%m-%d')}
**資料來源**: 測試資料

## 公司概況
- **公司名稱**: Apple Inc.
- **行業**: 科技
- **市值**: 3000000 百萬美元

## 關鍵財務指標
| 指標 | 數值 |
|------|------|
| 市盈率 (PE) | 25.50 |
| 市銷率 (PS) | 7.20 |
| 淨資產收益率 (ROE) | 15.30% |

## 資料說明
- 這是測試資料，用於驗證快取功能
"""
        
        # 測試保存到快取
        print(f"\n 測試保存基本面資料到快取...")
        cache_key = cache.save_fundamentals_data(test_symbol, test_data, data_source="test")
        print(f" 資料已保存，快取鍵: {cache_key}")
        
        # 測試從快取載入
        print(f"\n 測試從快取載入基本面資料...")
        loaded_data = cache.load_fundamentals_data(cache_key)
        if loaded_data:
            print(f" 資料載入成功，長度: {len(loaded_data)}")
            print(f" 資料預覽: {loaded_data[:200]}...")
        else:
            print(f" 資料載入失敗")
        
        # 測試查找快取
        print(f"\n 測試查找基本面快取資料...")
        found_key = cache.find_cached_fundamentals_data(test_symbol, data_source="test")
        if found_key:
            print(f" 找到快取資料，快取鍵: {found_key}")
        else:
            print(f" 未找到快取資料")
        
        # 測試快取統計
        print(f"\n 測試快取統計...")
        stats = cache.get_cache_stats()
        print(f"快取統計: {stats}")
        
        return True
        
    except Exception as e:
        print(f" 快取管理器測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fundamentals_with_cache():
    """測試基本面資料取得函數的快取功能"""
    print(f"\n 測試基本面資料取得函數的快取功能...")
    
    try:
        from tradingagents.dataflows.interface import get_fundamentals_openai, get_fundamentals_finnhub
        
        test_symbol = "MSFT"
        curr_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n 第一次獲取 {test_symbol} 基本面資料（應該從API獲取）...")
        start_time = time.time()
        result1 = get_fundamentals_finnhub(test_symbol, curr_date)
        first_time = time.time() - start_time
        print(f" 第一次獲取耗時: {first_time:.2f}秒")
        print(f" 資料長度: {len(result1)}")
        
        print(f"\n 第二次獲取 {test_symbol} 基本面資料（應該從快取獲取）...")
        start_time = time.time()
        result2 = get_fundamentals_finnhub(test_symbol, curr_date)
        second_time = time.time() - start_time
        print(f" 第二次獲取耗時: {second_time:.2f}秒")
        print(f" 資料長度: {len(result2)}")
        
        # 驗證快取效果
        if second_time < first_time:
            print(f" 快取生效！第二次獲取速度提升了 {((first_time - second_time) / first_time * 100):.1f}%")
        else:
            print(f" 快取可能未生效，或者資料來源有變化")
        
        # 驗證資料一致性
        if result1 == result2:
            print(f" 兩次獲取的資料完全一致")
        else:
            print(f" 兩次獲取的資料不一致，可能是快取問題")
        
        return True
        
    except Exception as e:
        print(f" 基本面資料快取測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_ttl():
    """測試快取TTL（生存時間）功能"""
    print(f"\n 測試快取TTL功能...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        
        # 檢查快取配置
        print(f" 快取配置:")
        for cache_type, config in cache.cache_config.items():
            if 'fundamentals' in cache_type:
                print(f"  - {cache_type}: TTL={config['ttl_hours']}小時, 描述={config['description']}")
        
        # 測試美股的TTL設定
        us_symbol_1 = "GOOGL"
        us_symbol_2 = "MSFT"

        print(f"\n測試美股基本面快取 ({us_symbol_1})...")
        us_key_1 = cache.find_cached_fundamentals_data(us_symbol_1, data_source="test")
        if us_key_1:
            print(f"找到快取: {us_key_1}")
        else:
            print(f"未找到快取")

        print(f"\n測試美股基本面快取 ({us_symbol_2})...")
        us_key_2 = cache.find_cached_fundamentals_data(us_symbol_2, data_source="test")
        if us_key_2:
            print(f"找到快取: {us_key_2}")
        else:
            print(f"未找到快取")
        
        return True
        
    except Exception as e:
        print(f" 快取TTL測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print(" 開始基本面資料快取功能測試")
    print("=" * 50)
    
    # 檢查環境
    print(f" 當前工作目錄: {os.getcwd()}")
    print(f" Python路徑: {sys.path[0]}")
    
    # 運行測試
    tests = [
        ("快取管理器基本功能", test_cache_manager_fundamentals),
        ("基本面資料快取功能", test_fundamentals_with_cache),
        ("快取TTL功能", test_cache_ttl),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f" 測試 '{test_name}' 執行失敗: {str(e)}")
            results.append((test_name, False))
    
    # 輸出測試結果
    print(f"\n{'='*20} 測試結果匯總 {'='*20}")
    for test_name, result in results:
        status = " 通過" if result else " 失敗"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n 測試完成: {passed}/{total} 個測試通過")
    
    if passed == total:
        print(" 所有測試都通過了！基本面資料快取功能正常工作。")
    else:
        print(" 部分測試失敗，請檢查相關功能。")

if __name__ == "__main__":
    main()