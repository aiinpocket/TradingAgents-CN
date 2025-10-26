#!/usr/bin/env python3
"""
股票代碼追蹤測試腳本
專門用於調試股票代碼在基本面分析中的誤判問題
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_stock_code_tracking():
    """測試股票代碼在整個流程中的傳遞"""
    print("\n🔍 股票代碼追蹤測試")
    print("=" * 80)
    
    # 測試分眾傳媒 002027
    test_ticker = "002027"
    print(f"📊 測試股票代碼: {test_ticker} (分眾傳媒)")
    
    try:
        # 導入必要的模塊
        from tradingagents.agents.utils.agent_utils import AgentUtils
        from tradingagents.utils.logging_init import get_logger
        
        # 設置日誌級別為INFO以顯示追蹤日誌
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        print(f"\n🔧 開始調用統一基本面分析工具...")
        
        # 調用統一基本面分析工具
        result = AgentUtils.get_stock_fundamentals_unified(
            ticker=test_ticker,
            start_date='2025-06-01',
            end_date='2025-07-15',
            curr_date='2025-07-15'
        )
        
        print(f"\n✅ 統一基本面分析工具調用完成")
        print(f"📊 返回結果長度: {len(result) if result else 0}")
        
        # 檢查結果中是否包含正確的股票代碼
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

def test_individual_components():
    """測試各個組件的股票代碼處理"""
    print("\n🔧 測試各個組件的股票代碼處理")
    print("=" * 80)
    
    test_ticker = "002027"
    
    try:
        # 1. 測試股票市場识別
        print(f"\n1️⃣ 測試股票市場识別...")
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(test_ticker)
        print(f"   市場信息: {market_info}")
        
        # 2. 測試Tushare代碼標準化
        print(f"\n2️⃣ 測試Tushare代碼標準化...")
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        provider = get_tushare_provider()
        if provider:
            normalized = provider._normalize_symbol(test_ticker)
            print(f"   標準化結果: {test_ticker} -> {normalized}")
        
        # 3. 測試數據源管理器
        print(f"\n3️⃣ 測試數據源管理器...")
        from tradingagents.dataflows.data_source_manager import get_china_stock_data_unified
        data_result = get_china_stock_data_unified(test_ticker, "2025-07-01", "2025-07-15")
        print(f"   數據獲取結果長度: {len(data_result) if data_result else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ 組件測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始股票代碼追蹤測試")
    
    # 測試1: 完整流程追蹤
    success1 = test_stock_code_tracking()
    
    # 測試2: 各個組件測試
    success2 = test_individual_components()
    
    if success1 and success2:
        print("\n✅ 所有測試通過")
    else:
        print("\n❌ 部分測試失败")
