"""
測試導入修複
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_fundamentals_analyst_import():
    """測試基本面分析師導入"""
    print("🧪 測試基本面分析師導入...")
    
    try:
        # 測試導入基本面分析師
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        print("  ✅ 基本面分析師導入成功")
        
        # 測試is_china_stock函數導入
        from tradingagents.utils.stock_utils import is_china_stock
        print("  ✅ is_china_stock函數導入成功")
        
        # 測試函數調用
        result = is_china_stock("000001")
        print(f"  ✅ is_china_stock('000001') = {result}")
        
        result = is_china_stock("0700.HK")
        print(f"  ✅ is_china_stock('0700.HK') = {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本面分析師導入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_utils_functions():
    """測試股票工具函數"""
    print("\n🧪 測試股票工具函數...")
    
    try:
        from tradingagents.utils.stock_utils import (
            is_china_stock, 
            is_hk_stock, 
            is_us_stock,
            StockUtils
        )
        
        # 測試各種股票代碼
        test_cases = [
            ("000001", "A股", True, False, False),
            ("600036", "A股", True, False, False),
            ("0700.HK", "港股", False, True, False),
            ("9988.HK", "港股", False, True, False),
            ("AAPL", "美股", False, False, True),
            ("TSLA", "美股", False, False, True),
        ]
        
        for ticker, market, expect_china, expect_hk, expect_us in test_cases:
            china_result = is_china_stock(ticker)
            hk_result = is_hk_stock(ticker)
            us_result = is_us_stock(ticker)
            
            print(f"  {ticker} ({market}):")
            print(f"    中國A股: {china_result} {'✅' if china_result == expect_china else '❌'}")
            print(f"    港股: {hk_result} {'✅' if hk_result == expect_hk else '❌'}")
            print(f"    美股: {us_result} {'✅' if us_result == expect_us else '❌'}")
            
            if (china_result != expect_china or 
                hk_result != expect_hk or 
                us_result != expect_us):
                print(f"❌ {ticker} 识別結果不正確")
                return False
        
        print("  ✅ 所有股票工具函數測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 股票工具函數測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_analysis_runner():
    """測試Web分析運行器"""
    print("\n🧪 測試Web分析運行器...")
    
    try:
        from web.utils.analysis_runner import validate_analysis_params
        
        # 測試港股驗證
        is_valid, errors = validate_analysis_params(
            stock_symbol="0700.HK",
            analysis_date="2025-07-14",
            analysts=["market", "fundamentals"],
            research_depth=3,
            market_type="港股"
        )
        
        print(f"  港股驗證結果: {'通過' if is_valid else '失败'}")
        if not is_valid:
            print(f"  錯誤信息: {errors}")
            return False
        
        print("  ✅ Web分析運行器測試通過")
        return True
        
    except Exception as e:
        print(f"❌ Web分析運行器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_analysis_flow():
    """測試完整分析流程（不實际運行）"""
    print("\n🧪 測試完整分析流程導入...")
    
    try:
        # 測試所有必要的導入
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        
        print("  ✅ 交易圖導入成功")
        print("  ✅ 默認配置導入成功")
        print("  ✅ 基本面分析師導入成功")
        
        # 測試配置創建
        config = DEFAULT_CONFIG.copy()
        print("  ✅ 配置創建成功")
        
        print("  ✅ 完整分析流程導入測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 完整分析流程導入測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """運行所有導入測試"""
    print("🔧 導入修複測試")
    print("=" * 40)
    
    tests = [
        test_fundamentals_analyst_import,
        test_stock_utils_functions,
        test_web_analysis_runner,
        test_complete_analysis_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 異常: {e}")
    
    print("\n" + "=" * 40)
    print(f"🔧 導入修複測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有導入測試通過！")
        print("\n現在可以正常進行港股分析了")
        print("建议重新啟動Web應用並測試0700.HK分析")
    else:
        print("⚠️ 部分導入測試失败，請檢查失败的測試")

if __name__ == "__main__":
    main()
