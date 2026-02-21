#!/usr/bin/env python3
"""
調試基本面分析師的工具選擇問題
"""

import os
import sys

def test_fundamentals_analyst_directly():
    """直接測試基本面分析師函數"""
    print("🔧 直接測試基本面分析師...")
    
    try:
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包
        toolkit = Toolkit(config)
        
        # 創建LLM（模擬）
        class MockLLM:
            def bind_tools(self, tools):
                return self
            
            def invoke(self, messages):
                class MockResult:
                    def __init__(self):
                        self.tool_calls = []
                        self.content = "模擬分析結果"
                return MockResult()
        
        llm = MockLLM()
        
        # 創建基本面分析師
        analyst = create_fundamentals_analyst(llm, toolkit)
        
        # 模擬狀態
        state = {
            "trade_date": "2025-07-14",
            "company_of_interest": "0700.HK",
            "messages": []
        }
        
        print(f"  測試港股: {state['company_of_interest']}")
        print(f"  調用基本面分析師...")
        
        # 調用分析師（這會觸發工具選擇邏輯）
        result = analyst(state)
        
        print(f"  ✅ 基本面分析師調用完成")
        print(f"  結果類型: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 直接測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_utils_import():
    """測試StockUtils導入和功能"""
    print("\n🔧 測試StockUtils導入...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        # 測試港股識別
        ticker = "0700.HK"
        market_info = StockUtils.get_market_info(ticker)
        
        print(f"  股票: {ticker}")
        print(f"  市場信息: {market_info}")
        print(f"  是否港股: {market_info['is_hk']}")
        print(f"  是否A股: {market_info['is_china']}")
        print(f"  是否美股: {market_info['is_us']}")
        
        if market_info['is_hk']:
            print(f"  ✅ StockUtils正確識別港股")
            return True
        else:
            print(f"  ❌ StockUtils未能識別港股")
            return False
        
    except Exception as e:
        print(f"❌ StockUtils測試失敗: {e}")
        return False

def test_toolkit_hk_tools():
    """測試工具包中的港股工具"""
    print("\n🔧 測試工具包港股工具...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 檢查港股工具是否存在
        hk_tools = [
            'get_hk_stock_data_unified',
            'get_china_stock_data',
            'get_fundamentals_openai'
        ]
        
        for tool_name in hk_tools:
            has_tool = hasattr(toolkit, tool_name)
            print(f"  {tool_name}: {'✅' if has_tool else '❌'}")
            
            if has_tool:
                tool = getattr(toolkit, tool_name)
                print(f"    工具類型: {type(tool)}")
                print(f"    工具名稱: {getattr(tool, 'name', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具包測試失敗: {e}")
        return False

def test_import_paths():
    """測試導入路徑"""
    print("\n🔧 測試導入路徑...")
    
    imports_to_test = [
        "tradingagents.agents.analysts.fundamentals_analyst",
        "tradingagents.utils.stock_utils",
        "tradingagents.agents.utils.agent_utils",
        "tradingagents.default_config"
    ]
    
    for import_path in imports_to_test:
        try:
            __import__(import_path)
            print(f"  {import_path}: ✅")
        except Exception as e:
            print(f"  {import_path}: ❌ - {e}")
            return False
    
    return True

def main():
    """主測試函數"""
    print("🔧 基本面分析師調試測試")
    print("=" * 60)
    
    tests = [
        test_import_paths,
        test_stock_utils_import,
        test_toolkit_hk_tools,
        test_fundamentals_analyst_directly,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ 測試失敗: {test.__name__}")
        except Exception as e:
            print(f"❌ 測試異常: {test.__name__} - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！")
        return True
    else:
        print("⚠️ 部分測試失敗，需要進一步檢查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
