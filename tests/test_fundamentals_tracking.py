#!/usr/bin/env python3
"""
基本面分析股票代碼追蹤測試
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_fundamentals_analyst():
    """測試基本面分析師的股票代碼處理"""
    print("\n🔍 基本面分析師股票代碼追蹤測試")
    print("=" * 80)
    
    # 測試分眾傳媒 002027
    test_ticker = "002027"
    print(f"📊 測試股票代碼: {test_ticker} (分眾傳媒)")
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        # 創建模擬狀態
        state = {
            "company_of_interest": test_ticker,
            "trade_date": "2025-07-15",
            "messages": []
        }
        
        print(f"\n🔧 開始調用基本面分析師...")
        
        # 導入基本面分析師
        from tradingagents.agents.analysts.fundamentals_analyst import fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import AgentUtils
        
        # 創建工具包
        toolkit = AgentUtils()
        
        # 調用基本面分析師
        result = fundamentals_analyst(state, toolkit)
        
        print(f"\n✅ 基本面分析師調用完成")
        print(f"📊 返回狀態類型: {type(result)}")
        
        # 檢查返回的狀態
        if isinstance(result, dict):
            if 'fundamentals_report' in result:
                report = result['fundamentals_report']
                print(f"📄 基本面報告長度: {len(report) if report else 0}")
                
                # 檢查報告中的股票代碼
                if report:
                    print(f"\n🔍 檢查報告中的股票代碼...")
                    if "002027" in report:
                        print("✅ 報告中包含正確的股票代碼 002027")
                    else:
                        print("❌ 報告中不包含正確的股票代碼 002027")
                        
                    if "002021" in report:
                        print("⚠️ 報告中包含錯誤的股票代碼 002021")
                    else:
                        print("✅ 報告中不包含錯誤的股票代碼 002021")
                        
                    # 顯示報告的前500字符
                    print(f"\n📄 報告前500字符:")
                    print("-" * 60)
                    print(report[:500])
                    print("-" * 60)
            else:
                print("❌ 返回狀態中沒有 fundamentals_report")
        else:
            print(f"❌ 返回結果類型不正確: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_tool_direct():
    """直接測試統一基本面工具"""
    print("\n🔧 直接測試統一基本面工具")
    print("=" * 80)
    
    test_ticker = "002027"
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger.setLevel("INFO")
        
        # 導入工具包
        from tradingagents.agents.utils.agent_utils import AgentUtils
        
        # 創建工具包實例
        toolkit = AgentUtils()
        
        print(f"\n🔧 調用統一基本面工具...")
        
        # 直接調用統一基本面工具
        result = toolkit.get_stock_fundamentals_unified.invoke({
            'ticker': test_ticker,
            'start_date': '2025-06-01',
            'end_date': '2025-07-15',
            'curr_date': '2025-07-15'
        })
        
        print(f"\n✅ 統一基本面工具調用完成")
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
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始基本面分析股票代碼追蹤測試")
    
    # 測試1: 直接測試統一工具
    success1 = test_unified_tool_direct()
    
    # 測試2: 測試基本面分析師
    success2 = test_fundamentals_analyst()
    
    if success1 and success2:
        print("\n✅ 所有測試通過")
    else:
        print("\n❌ 部分測試失敗")
