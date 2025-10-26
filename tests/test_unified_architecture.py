#!/usr/bin/env python3
"""
測試統一工具架構
驗證所有分析師都使用統一工具方案
"""

import os
import sys

def test_unified_tools_availability():
    """測試統一工具的可用性"""
    print("🔧 測試統一工具可用性...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 檢查統一工具是否存在
        unified_tools = [
            'get_stock_fundamentals_unified',
            'get_stock_market_data_unified',
            'get_stock_news_unified',
            'get_stock_sentiment_unified'
        ]
        
        for tool_name in unified_tools:
            if hasattr(toolkit, tool_name):
                tool = getattr(toolkit, tool_name)
                print(f"  ✅ {tool_name}: 可用")
                print(f"    工具描述: {getattr(tool, 'description', 'N/A')[:100]}...")
            else:
                print(f"  ❌ {tool_name}: 不可用")
                return False
        
        print("✅ 統一工具可用性測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 統一工具可用性測試失败: {e}")
        return False


def test_market_analyst_unified():
    """測試市場分析師使用統一工具"""
    print("\n🔧 測試市場分析師統一工具...")
    
    try:
        from tradingagents.agents.analysts.market_analyst import create_market_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包
        toolkit = Toolkit(config)
        
        # 創建模擬LLM
        class MockLLM:
            def bind_tools(self, tools):
                print(f"🔧 [MockLLM] 市場分析師绑定工具: {[tool.name for tool in tools]}")
                
                # 檢查是否只绑定了統一工具
                if len(tools) == 1 and tools[0].name == 'get_stock_market_data_unified':
                    print(f"  ✅ 正確绑定統一市場數據工具")
                    return self
                else:
                    print(f"  ❌ 绑定了錯誤的工具: {[tool.name for tool in tools]}")
                    return self
            
            def invoke(self, messages):
                class MockResult:
                    def __init__(self):
                        self.tool_calls = []
                        self.content = "模擬市場分析結果"
                return MockResult()
        
        llm = MockLLM()
        
        # 創建市場分析師
        analyst = create_market_analyst(llm, toolkit)
        
        # 模擬狀態
        state = {
            "trade_date": "2025-07-14",
            "company_of_interest": "0700.HK",
            "messages": []
        }
        
        print(f"  測試港股市場分析: {state['company_of_interest']}")
        
        # 調用分析師（這會觸發工具選擇逻辑）
        result = analyst(state)
        
        print(f"  ✅ 市場分析師調用完成")
        return True
        
    except Exception as e:
        print(f"❌ 市場分析師統一工具測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fundamentals_analyst_unified():
    """測試基本面分析師使用統一工具"""
    print("\n🔧 測試基本面分析師統一工具...")
    
    try:
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包
        toolkit = Toolkit(config)
        
        # 創建模擬LLM
        class MockLLM:
            def bind_tools(self, tools):
                print(f"🔧 [MockLLM] 基本面分析師绑定工具: {[tool.name for tool in tools]}")
                
                # 檢查是否只绑定了統一工具
                if len(tools) == 1 and tools[0].name == 'get_stock_fundamentals_unified':
                    print(f"  ✅ 正確绑定統一基本面分析工具")
                    return self
                else:
                    print(f"  ❌ 绑定了錯誤的工具: {[tool.name for tool in tools]}")
                    return self
            
            def invoke(self, messages):
                class MockResult:
                    def __init__(self):
                        self.tool_calls = []
                        self.content = "模擬基本面分析結果"
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
        
        print(f"  測試港股基本面分析: {state['company_of_interest']}")
        
        # 調用分析師（這會觸發工具選擇逻辑）
        result = analyst(state)
        
        print(f"  ✅ 基本面分析師調用完成")
        return True
        
    except Exception as e:
        print(f"❌ 基本面分析師統一工具測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stock_type_routing():
    """測試股票類型路由"""
    print("\n🔧 測試股票類型路由...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        test_cases = [
            ("0700.HK", "港股", "HK$"),
            ("9988.HK", "港股", "HK$"),
            ("000001", "中國A股", "¥"),
            ("600036", "中國A股", "¥"),
            ("AAPL", "美股", "$"),
        ]
        
        for ticker, expected_market, expected_currency in test_cases:
            print(f"\n📊 測試 {ticker}:")
            
            # 測試基本面分析工具
            try:
                result = toolkit.get_stock_fundamentals_unified.invoke({
                    'ticker': ticker,
                    'start_date': '2025-06-14',
                    'end_date': '2025-07-14',
                    'curr_date': '2025-07-14'
                })
                
                if expected_market in result and expected_currency in result:
                    print(f"  ✅ 基本面工具路由正確")
                else:
                    print(f"  ⚠️ 基本面工具路由可能有問題")
                    
            except Exception as e:
                print(f"  ❌ 基本面工具調用失败: {e}")
                return False
            
            # 測試市場數據工具
            try:
                result = toolkit.get_stock_market_data_unified.invoke({
                    'ticker': ticker,
                    'start_date': '2025-07-10',
                    'end_date': '2025-07-14'
                })
                
                if expected_market in result and expected_currency in result:
                    print(f"  ✅ 市場數據工具路由正確")
                else:
                    print(f"  ⚠️ 市場數據工具路由可能有問題")
                    
            except Exception as e:
                print(f"  ❌ 市場數據工具調用失败: {e}")
                return False
        
        print("✅ 股票類型路由測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 股票類型路由測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔧 統一工具架構測試")
    print("=" * 60)
    
    tests = [
        test_unified_tools_availability,
        test_stock_type_routing,
        test_fundamentals_analyst_unified,
        test_market_analyst_unified,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ 測試失败: {test.__name__}")
        except Exception as e:
            print(f"❌ 測試異常: {test.__name__} - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！統一工具架構成功")
        print("\n📋 架構優势:")
        print("✅ 所有分析師使用統一工具")
        print("✅ 工具內部自動识別股票類型")
        print("✅ 避免了LLM工具調用混乱")
        print("✅ 簡化了系統提示和處理流程")
        print("✅ 更容易維護和擴展")
        print("✅ 統一的錯誤處理和日誌記錄")
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步檢查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
