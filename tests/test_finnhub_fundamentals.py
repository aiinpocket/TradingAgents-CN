#!/usr/bin/env python3
"""
測試Finnhub基本面資料取得功能、OpenAI fallback機制和快取功能
"""

import os
import sys
import time
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_finnhub_api_key():
    """測試Finnhub API密鑰配置"""
    print(" 檢查Finnhub API密鑰...")
    
    api_key = os.getenv('FINNHUB_API_KEY')
    if api_key:
        print(f" Finnhub API密鑰已配置: {api_key[:8]}...")
        return True
    else:
        print(" 未配置FINNHUB_API_KEY環境變數")
        return False

def test_finnhub_fundamentals_with_cache():
    """測試Finnhub基本面資料取得和快取功能"""
    print("\n 測試Finnhub基本面資料取得和快取功能...")
    
    try:
        from tradingagents.dataflows.interface import get_fundamentals_finnhub
        from tradingagents.dataflows.cache_manager import get_cache
        
        # 清理可能存在的快取
        cache = get_cache()
        test_ticker = "AAPL"
        curr_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n 第一次取得 {test_ticker} 的基本面資料（從API取得）...")
        start_time = time.time()
        result1 = get_fundamentals_finnhub(test_ticker, curr_date)
        first_time = time.time() - start_time
        
        if result1 and len(result1) > 100:
            print(f" {test_ticker} 基本面資料取得成功，長度: {len(result1)}")
            print(f" 第一次取得耗時: {first_time:.2f}秒")
            print(f" 資料預覽: {result1[:200]}...")
            
            # 第二次取得，應該從快取讀取
            print(f"\n 第二次取得 {test_ticker} 的基本面資料（從快取取得）...")
            start_time = time.time()
            result2 = get_fundamentals_finnhub(test_ticker, curr_date)
            second_time = time.time() - start_time
            
            print(f" 第二次取得耗時: {second_time:.2f}秒")
            
            # 驗證快取效果
            if second_time < first_time and result1 == result2:
                print(f" 快取功能正常！速度提升了 {((first_time - second_time) / first_time * 100):.1f}%")
                return True
            else:
                print(f" 快取可能未生效")
                return False
        else:
            print(f" {test_ticker} 基本面資料取得失敗或資料過短")
            print(f" 返回內容: {result1}")
            return False
        
    except Exception as e:
        print(f" Finnhub基本面資料測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_fallback_with_cache():
    """測試OpenAI fallback機制和快取功能"""
    print("\n 測試OpenAI fallback機制和快取功能...")
    
    try:
        from tradingagents.dataflows.interface import get_fundamentals_openai
        
        # 臨時移除OpenAI配置來測試fallback
        original_backend_url = os.environ.get('BACKEND_URL')
        original_quick_think_llm = os.environ.get('QUICK_THINK_LLM')
        
        # 清除OpenAI配置
        if 'BACKEND_URL' in os.environ:
            del os.environ['BACKEND_URL']
        if 'QUICK_THINK_LLM' in os.environ:
            del os.environ['QUICK_THINK_LLM']
        
        print(" 已臨時移除OpenAI配置，測試fallback到Finnhub...")
        
        curr_date = datetime.now().strftime('%Y-%m-%d')
        test_ticker = "MSFT"
        
        print(f"\n 第一次通過OpenAI介面取得 {test_ticker} 資料（應fallback到Finnhub）...")
        start_time = time.time()
        result1 = get_fundamentals_openai(test_ticker, curr_date)
        first_time = time.time() - start_time
        
        if result1 and "Finnhub" in result1:
            print(" OpenAI fallback機制工作正常，成功回退到Finnhub API")
            print(f" 資料長度: {len(result1)}")
            print(f" 第一次取得耗時: {first_time:.2f}秒")
            
            # 第二次取得，應該從快取讀取
            print(f"\n 第二次通過OpenAI介面取得 {test_ticker} 資料（應從快取取得）...")
            start_time = time.time()
            result2 = get_fundamentals_openai(test_ticker, curr_date)
            second_time = time.time() - start_time
            
            print(f" 第二次取得耗時: {second_time:.2f}秒")
            
            # 驗證快取效果
            if second_time < first_time and result1 == result2:
                print(f" fallback + 快取功能正常！速度提升了 {((first_time - second_time) / first_time * 100):.1f}%")
                success = True
            else:
                print(f" 快取可能未生效")
                success = False
        else:
            print(" OpenAI fallback機制可能有問題")
            print(f" 返回內容: {result1[:500]}...")
            success = False
        
        # 恢復原始配置
        if original_backend_url:
            os.environ['BACKEND_URL'] = original_backend_url
        if original_quick_think_llm:
            os.environ['QUICK_THINK_LLM'] = original_quick_think_llm
        
        return success
        
    except Exception as e:
        print(f" OpenAI fallback測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_management():
    """測試快取管理功能"""
    print("\n 測試快取管理功能...")
    
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        
        cache = get_cache()
        
        # 取得快取統計
        stats = cache.get_cache_stats()
        print(f" 當前快取統計: {stats}")
        
        # 檢查快取配置
        print(f"\n 基本面資料快取配置:")
        for cache_type, config in cache.cache_config.items():
            if 'fundamentals' in cache_type:
                print(f"  - {cache_type}: TTL={config['ttl_hours']}小時, 最大檔案數={config['max_files']}, 描述={config['description']}")
        
        return True
        
    except Exception as e:
        print(f" 快取管理測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函式"""
    print(" 開始Finnhub基本面資料功能和快取測試")
    print("=" * 60)
    
    # 檢查環境
    print(f" 當前工作目錄: {os.getcwd()}")
    print(f" Python路徑: {sys.path[0]}")
    
    # 執行測試
    tests = [
        ("Finnhub API密鑰檢查", test_finnhub_api_key),
        ("Finnhub基本面資料取得和快取", test_finnhub_fundamentals_with_cache),
        ("OpenAI fallback機制和快取", test_openai_fallback_with_cache),
        ("快取管理功能", test_cache_management),
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
        print(" 所有測試都通過了！Finnhub基本面資料功能和快取系統正常工作。")
        print("\n 功能特性:")
        print("1.  當OpenAI配置不可用時，系統會自動使用Finnhub API")
        print("2.  Finnhub提供官方財務資料，包括PE、PS、ROE等關鍵指標")
        print("3.  資料來源於公司財報和SEC檔案，具有較高的可靠性")
        print("4. 支援智慧快取機制，美股基本面資料快取24小時")
        print("5.  快取按市場類型分類儲存，提高查找效率")
        print("6.  自動檢測快取有效性，過期資料會重新取得")
    else:
        print(" 部分測試失敗，請檢查相關配置。")

if __name__ == "__main__":
    main()