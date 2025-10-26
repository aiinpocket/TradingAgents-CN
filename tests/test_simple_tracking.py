#!/usr/bin/env python3
"""
簡單的股票代碼追蹤測試
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_data_flow():
    """測試數據流中的股票代碼處理"""
    print("\n🔍 數據流股票代碼追蹤測試")
    print("=" * 80)
    
    # 測試分眾傳媒 002027
    test_ticker = "002027"
    print(f"📊 測試股票代碼: {test_ticker} (分眾傳媒)")
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        print(f"\n🔧 測試數據源管理器...")
        
        # 測試數據源管理器
        from tradingagents.dataflows.data_source_manager import get_china_stock_data_unified
        
        result = get_china_stock_data_unified(test_ticker, "2025-07-01", "2025-07-15")
        
        print(f"\n✅ 數據源管理器調用完成")
        print(f"📊 返回結果長度: {len(result) if result else 0}")
        
        # 檢查結果中的股票代碼
        if result:
            print(f"\n🔍 檢查結果中的股票代碼...")
            if "002027" in result:
                print("✅ 結果中包含正確的股票代碼 002027")
            else:
                print("❌ 結果中不包含正確的股票代碼 002027")
                
            if "002021" in result:
                print("⚠️ 結果中包含錯誤的股票代碼 002021")
            else:
                print("✅ 結果中不包含錯誤的股票代碼 002021")
                
            # 顯示結果的前500字符
            print(f"\n📄 結果前500字符:")
            print("-" * 60)
            print(result[:500])
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tushare_direct():
    """直接測試Tushare接口"""
    print("\n🔧 直接測試Tushare接口")
    print("=" * 80)
    
    test_ticker = "002027"
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger.setLevel("INFO")
        
        print(f"\n🔧 測試Tushare接口...")
        
        # 測試Tushare接口
        from tradingagents.dataflows.interface import get_china_stock_data_tushare
        
        result = get_china_stock_data_tushare(test_ticker, "2025-07-01", "2025-07-15")
        
        print(f"\n✅ Tushare接口調用完成")
        print(f"📊 返回結果長度: {len(result) if result else 0}")
        
        # 檢查結果中的股票代碼
        if result:
            print(f"\n🔍 檢查結果中的股票代碼...")
            if "002027" in result:
                print("✅ 結果中包含正確的股票代碼 002027")
            else:
                print("❌ 結果中不包含正確的股票代碼 002027")
                
            if "002021" in result:
                print("⚠️ 結果中包含錯誤的股票代碼 002021")
            else:
                print("✅ 結果中不包含錯誤的股票代碼 002021")
                
            # 顯示結果的前500字符
            print(f"\n📄 結果前500字符:")
            print("-" * 60)
            print(result[:500])
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tushare_provider():
    """測試Tushare提供器"""
    print("\n🔧 測試Tushare提供器")
    print("=" * 80)
    
    test_ticker = "002027"
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger.setLevel("INFO")
        
        print(f"\n🔧 測試Tushare提供器...")
        
        # 測試Tushare提供器
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        provider = get_tushare_provider()
        
        if provider and provider.connected:
            print("✅ Tushare提供器連接成功")
            
            # 測試股票信息獲取
            stock_info = provider.get_stock_info(test_ticker)
            print(f"📊 股票信息: {stock_info}")
            
            # 測試股票數據獲取
            stock_data = provider.get_stock_daily(test_ticker, "2025-07-01", "2025-07-15")
            print(f"📊 股票數據形狀: {stock_data.shape if stock_data is not None and hasattr(stock_data, 'shape') else 'None'}")
            
            if stock_data is not None and not stock_data.empty:
                print(f"📊 股票數據列: {list(stock_data.columns)}")
                if 'ts_code' in stock_data.columns:
                    unique_codes = stock_data['ts_code'].unique()
                    print(f"📊 數據中的ts_code: {unique_codes}")
        else:
            print("❌ Tushare提供器連接失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始簡單股票代碼追蹤測試")
    
    # 測試1: Tushare提供器
    success1 = test_tushare_provider()
    
    # 測試2: Tushare接口
    success2 = test_tushare_direct()
    
    # 測試3: 數據源管理器
    success3 = test_data_flow()
    
    if success1 and success2 and success3:
        print("\n✅ 所有測試通過")
    else:
        print("\n❌ 部分測試失败")
