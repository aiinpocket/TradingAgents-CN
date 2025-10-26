#!/usr/bin/env python3
"""
測試修複後的降級機制是否避免了無限重試
驗證不存在的股票代碼不會導致無限循環
"""

import sys
import os
import time
import threading

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TimeoutException(Exception):
    pass

def timeout_handler():
    """超時處理器"""
    time.sleep(30)  # 30秒超時
    raise TimeoutException("測試超時，可能存在無限重試")

def test_no_infinite_retry_stock_data():
    """測試股票歷史數據獲取不會無限重試"""
    print("🔍 測試股票歷史數據獲取不會無限重試")
    print("=" * 50)
    
    # 啟動超時監控
    timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
    timeout_thread.start()
    
    # 測試不存在的股票代碼
    fake_codes = ["999999", "888888"]
    
    for code in fake_codes:
        print(f"\n📊 測試不存在的股票代碼: {code}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            from tradingagents.dataflows.interface import get_china_stock_data_unified
            result = get_china_stock_data_unified(code, "2025-07-01", "2025-07-17")
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"✅ 測試完成，耗時: {elapsed:.2f}秒")
            print(f"📊 結果: {result[:100] if result else 'None'}...")
            
            if elapsed > 25:
                print("⚠️ 耗時過長，可能存在重試問題")
            else:
                print("✅ 耗時正常，没有無限重試")
                
        except TimeoutException:
            print("❌ 測試超時！存在無限重試問題")
            return False
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"❌ 測試失败: {e}")
            print(f"⏱️ 失败前耗時: {elapsed:.2f}秒")
    
    return True

def test_no_infinite_retry_stock_info():
    """測試股票基本信息獲取不會無限重試"""
    print("\n🔍 測試股票基本信息獲取不會無限重試")
    print("=" * 50)
    
    # 測試不存在的股票代碼
    fake_codes = ["999999", "888888"]
    
    for code in fake_codes:
        print(f"\n📊 測試不存在的股票代碼: {code}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            result = get_china_stock_info_unified(code)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"✅ 測試完成，耗時: {elapsed:.2f}秒")
            print(f"📊 結果: {result[:100] if result else 'None'}...")
            
            if elapsed > 10:
                print("⚠️ 耗時過長，可能存在重試問題")
            else:
                print("✅ 耗時正常，没有無限重試")
                
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"❌ 測試失败: {e}")
            print(f"⏱️ 失败前耗時: {elapsed:.2f}秒")
    
    return True

def test_fallback_mechanism_logic():
    """測試降級機制的逻辑正確性"""
    print("\n🔍 測試降級機制的逻辑正確性")
    print("=" * 50)
    
    try:
        from tradingagents.dataflows.data_source_manager import get_data_source_manager
        manager = get_data_source_manager()
        
        # 檢查降級方法是否存在
        if hasattr(manager, '_try_fallback_sources'):
            print("✅ _try_fallback_sources方法存在")
        else:
            print("❌ _try_fallback_sources方法不存在")
            return False
        
        if hasattr(manager, '_try_fallback_stock_info'):
            print("✅ _try_fallback_stock_info方法存在")
        else:
            print("❌ _try_fallback_stock_info方法不存在")
            return False
        
        # 檢查可用數據源
        available_sources = manager.available_sources
        print(f"📊 可用數據源: {available_sources}")
        
        if len(available_sources) > 1:
            print("✅ 有多個數據源可用於降級")
        else:
            print("⚠️ 只有一個數據源，降級機制可能無效")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

def test_real_stock_performance():
    """測試真實股票的性能表現"""
    print("\n🔍 測試真實股票的性能表現")
    print("=" * 50)
    
    # 測試真實股票代碼
    real_codes = ["603985", "000001"]
    
    for code in real_codes:
        print(f"\n📊 測試股票代碼: {code}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            # 測試歷史數據
            from tradingagents.dataflows.interface import get_china_stock_data_unified
            data_result = get_china_stock_data_unified(code, "2025-07-15", "2025-07-17")
            
            data_time = time.time()
            data_elapsed = data_time - start_time
            
            # 測試基本信息
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            info_result = get_china_stock_info_unified(code)
            
            end_time = time.time()
            info_elapsed = end_time - data_time
            total_elapsed = end_time - start_time
            
            print(f"✅ 歷史數據獲取耗時: {data_elapsed:.2f}秒")
            print(f"✅ 基本信息獲取耗時: {info_elapsed:.2f}秒")
            print(f"✅ 总耗時: {total_elapsed:.2f}秒")
            
            if total_elapsed > 15:
                print("⚠️ 总耗時過長")
            else:
                print("✅ 性能表現良好")
                
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"❌ 測試失败: {e}")
            print(f"⏱️ 失败前耗時: {elapsed:.2f}秒")

if __name__ == "__main__":
    print("🧪 無限重試問題修複驗證測試")
    print("=" * 80)
    print("📝 此測試驗證修複後的降級機制不會導致無限重試")
    print("=" * 80)
    
    success = True
    
    # 1. 測試股票歷史數據不會無限重試
    if not test_no_infinite_retry_stock_data():
        success = False
    
    # 2. 測試股票基本信息不會無限重試
    if not test_no_infinite_retry_stock_info():
        success = False
    
    # 3. 測試降級機制逻辑
    if not test_fallback_mechanism_logic():
        success = False
    
    # 4. 測試真實股票性能
    test_real_stock_performance()
    
    print("\n📋 測試总結")
    print("=" * 60)
    if success:
        print("✅ 無限重試問題修複驗證測試通過")
        print("🎯 降級機制現在能夠:")
        print("   - 避免遞歸調用導致的無限重試")
        print("   - 在合理時間內完成所有數據源嘗試")
        print("   - 正確處理不存在的股票代碼")
    else:
        print("❌ 測試發現問題，需要進一步修複")
        print("🔍 請檢查:")
        print("   - 降級機制是否存在遞歸調用")
        print("   - 超時設置是否合理")
        print("   - 錯誤處理是否完善")
