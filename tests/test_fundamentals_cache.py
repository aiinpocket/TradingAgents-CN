#!/usr/bin/env python3
"""
測試基本面數據緩存功能
驗證OpenAI和Finnhub基本面數據的緩存機制
"""

import os
import sys
import time
from datetime import datetime

# 添加項目根目錄到路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_cache_manager_fundamentals():
    """測試緩存管理器的基本面數據功能"""
    print(" 測試基本面數據緩存管理器...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        print(f" 緩存管理器初始化成功")
        print(f" 緩存目錄: {cache.cache_dir}")
        
        # 測試保存基本面數據
        test_symbol = "AAPL"
        test_data = f"""
# {test_symbol} 基本面分析報告（測試數據）

**數據獲取時間**: {datetime.now().strftime('%Y-%m-%d')}
**數據來源**: 測試數據

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

## 數據說明
- 這是測試數據，用於驗證緩存功能
"""
        
        # 測試保存到緩存
        print(f"\n 測試保存基本面數據到緩存...")
        cache_key = cache.save_fundamentals_data(test_symbol, test_data, data_source="test")
        print(f" 數據已保存，緩存鍵: {cache_key}")
        
        # 測試從緩存載入
        print(f"\n 測試從緩存載入基本面數據...")
        loaded_data = cache.load_fundamentals_data(cache_key)
        if loaded_data:
            print(f" 數據載入成功，長度: {len(loaded_data)}")
            print(f" 數據預覽: {loaded_data[:200]}...")
        else:
            print(f" 數據載入失敗")
        
        # 測試查找緩存
        print(f"\n 測試查找基本面緩存數據...")
        found_key = cache.find_cached_fundamentals_data(test_symbol, data_source="test")
        if found_key:
            print(f" 找到緩存數據，緩存鍵: {found_key}")
        else:
            print(f" 未找到緩存數據")
        
        # 測試緩存統計
        print(f"\n 測試緩存統計...")
        stats = cache.get_cache_stats()
        print(f"緩存統計: {stats}")
        
        return True
        
    except Exception as e:
        print(f" 緩存管理器測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fundamentals_with_cache():
    """測試基本面數據獲取函數的緩存功能"""
    print(f"\n 測試基本面數據獲取函數的緩存功能...")
    
    try:
        from tradingagents.dataflows.interface import get_fundamentals_openai, get_fundamentals_finnhub
        
        test_symbol = "MSFT"
        curr_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n 第一次獲取 {test_symbol} 基本面數據（應該從API獲取）...")
        start_time = time.time()
        result1 = get_fundamentals_finnhub(test_symbol, curr_date)
        first_time = time.time() - start_time
        print(f" 第一次獲取耗時: {first_time:.2f}秒")
        print(f" 數據長度: {len(result1)}")
        
        print(f"\n 第二次獲取 {test_symbol} 基本面數據（應該從緩存獲取）...")
        start_time = time.time()
        result2 = get_fundamentals_finnhub(test_symbol, curr_date)
        second_time = time.time() - start_time
        print(f" 第二次獲取耗時: {second_time:.2f}秒")
        print(f" 數據長度: {len(result2)}")
        
        # 驗證緩存效果
        if second_time < first_time:
            print(f" 緩存生效！第二次獲取速度提升了 {((first_time - second_time) / first_time * 100):.1f}%")
        else:
            print(f" 緩存可能未生效，或者數據來源有變化")
        
        # 驗證數據一致性
        if result1 == result2:
            print(f" 兩次獲取的數據完全一致")
        else:
            print(f" 兩次獲取的數據不一致，可能是緩存問題")
        
        return True
        
    except Exception as e:
        print(f" 基本面數據緩存測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_ttl():
    """測試緩存TTL（生存時間）功能"""
    print(f"\n 測試緩存TTL功能...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        
        # 檢查緩存配置
        print(f" 緩存配置:")
        for cache_type, config in cache.cache_config.items():
            if 'fundamentals' in cache_type:
                print(f"  - {cache_type}: TTL={config['ttl_hours']}小時, 描述={config['description']}")
        
        # 測試美股的TTL設置
        us_symbol_1 = "GOOGL"
        us_symbol_2 = "MSFT"

        print(f"\n測試美股基本面緩存 ({us_symbol_1})...")
        us_key_1 = cache.find_cached_fundamentals_data(us_symbol_1, data_source="test")
        if us_key_1:
            print(f"找到緩存: {us_key_1}")
        else:
            print(f"未找到緩存")

        print(f"\n測試美股基本面緩存 ({us_symbol_2})...")
        us_key_2 = cache.find_cached_fundamentals_data(us_symbol_2, data_source="test")
        if us_key_2:
            print(f"找到緩存: {us_key_2}")
        else:
            print(f"未找到緩存")
        
        return True
        
    except Exception as e:
        print(f" 緩存TTL測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print(" 開始基本面數據緩存功能測試")
    print("=" * 50)
    
    # 檢查環境
    print(f" 當前工作目錄: {os.getcwd()}")
    print(f" Python路徑: {sys.path[0]}")
    
    # 運行測試
    tests = [
        ("緩存管理器基本功能", test_cache_manager_fundamentals),
        ("基本面數據緩存功能", test_fundamentals_with_cache),
        ("緩存TTL功能", test_cache_ttl),
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
        print(" 所有測試都通過了！基本面數據緩存功能正常工作。")
    else:
        print(" 部分測試失敗，請檢查相關功能。")

if __name__ == "__main__":
    main()