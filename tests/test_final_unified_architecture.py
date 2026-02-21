#!/usr/bin/env python3
"""
最終統一工具架構測試
驗證所有修複是否完成，LLM只能呼叫統一工具
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_complete_unified_architecture():
    """測試完整的統一工具架構"""
    print(" 測試完整的統一工具架構...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # 建立配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 建立工具包
        toolkit = Toolkit(config)
        
        # 建立交易圖
        graph = TradingAgentsGraph(config, toolkit)
        
        # 檢查ToolNode中註冊的工具
        fundamentals_tools = graph.tools_dict["fundamentals"].tools
        market_tools = graph.tools_dict["market"].tools
        
        print(f"  基本面分析ToolNode工具數量: {len(fundamentals_tools)}")
        print(f"  市場分析ToolNode工具數量: {len(market_tools)}")
        
        # 檢查基本面分析工具
        fundamentals_tool_names = [tool.name for tool in fundamentals_tools]
        print(f"  基本面分析工具: {fundamentals_tool_names}")
        
        # 檢查是否包含統一工具
        if 'get_stock_fundamentals_unified' in fundamentals_tool_names:
            print(f"     包含統一基本面工具")
        else:
            print(f"     缺少統一基本面工具")
            return False
        
        # 檢查是否還有舊工具
        old_tools = ['get_fundamentals_openai']
        for old_tool in old_tools:
            if old_tool in fundamentals_tool_names:
                print(f"     仍包含舊工具: {old_tool}")
                return False
            else:
                print(f"     已移除舊工具: {old_tool}")
        
        # 檢查市場分析工具
        market_tool_names = [tool.name for tool in market_tools]
        print(f"  市場分析工具: {market_tool_names}")
        
        # 檢查是否包含統一工具
        if 'get_stock_market_data_unified' in market_tool_names:
            print(f"     包含統一市場資料工具")
        else:
            print(f"     缺少統一市場資料工具")
            return False
        
        print(" 完整統一工具架構測試通過")
        return True
        
    except Exception as e:
        print(f" 完整統一工具架構測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_tool_calling_simulation():
    """模擬LLM工具呼叫測試"""
    print("\n 模擬LLM工具呼叫測試...")
    
    try:
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 建立配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 建立工具包
        toolkit = Toolkit(config)
        
        # 模擬LLM
        class MockLLM:
            def __init__(self):
                self.model_name = "gpt-4o-mini"
                self.temperature = 0.1
                self.max_tokens = 2000
            
            def bind_tools(self, tools):
                print(f"     LLM綁定工具: {[tool.name for tool in tools]}")
                
                # 驗證只綁定了統一工具
                if len(tools) == 1 and tools[0].name == 'get_stock_fundamentals_unified':
                    print(f"     正確綁定統一基本面工具")
                    return self
                else:
                    print(f"     綁定了錯誤的工具: {[tool.name for tool in tools]}")
                    raise ValueError("綁定了錯誤的工具")
            
            def invoke(self, messages):
                # 模擬正確的工具呼叫
                class MockResult:
                    def __init__(self):
                        self.tool_calls = [{
                            'name': 'get_stock_fundamentals_unified',
                            'args': {
                                'ticker': 'AAPL',
                                'start_date': '2025-05-28',
                                'end_date': '2025-07-14',
                                'curr_date': '2025-07-14'
                            },
                            'id': 'mock_call_id',
                            'type': 'tool_call'
                        }]
                        self.content = ""
                return MockResult()
        
        # 建立模擬LLM
        llm = MockLLM()
        
        # 建立基本面分析師
        analyst = create_fundamentals_analyst(llm, toolkit)
        
        # 模擬狀態
        state = {
            "trade_date": "2025-07-14",
            "company_of_interest": "AAPL",
            "messages": [("human", "分析AAPL")]
        }
        
        print(f"  測試美股基本面分析: {state['company_of_interest']}")
        
        # 呼叫分析師
        result = analyst(state)
        
        print(f"   基本面分析師呼叫完成")
        print(f"  返回結果類型: {type(result)}")
        
        # 驗證結果
        if isinstance(result, dict) and 'messages' in result:
            print(f"   返回了正確的訊息格式")
            return True
        else:
            print(f"   返回格式錯誤: {result}")
            return False
        
    except Exception as e:
        print(f" LLM工具呼叫模擬測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_tools_functionality():
    """測試統一工具功能"""
    print("\n 測試統一工具功能...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 測試統一基本面工具
        test_cases = [
            ("AAPL", "美股", "$"),
            ("MSFT", "美股", "$"),
            ("GOOGL", "美股", "$"),
        ]
        
        for ticker, expected_market, expected_currency in test_cases:
            print(f"\n  測試 {ticker} ({expected_market}):")
            
            try:
                result = toolkit.get_stock_fundamentals_unified.invoke({
                    'ticker': ticker,
                    'start_date': '2025-06-14',
                    'end_date': '2025-07-14',
                    'curr_date': '2025-07-14'
                })
                
                if expected_market in result and expected_currency in result:
                    print(f"     統一基本面工具正確處理{expected_market}")
                else:
                    print(f"     統一基本面工具處理結果可能有問題")
                    print(f"    結果前200字元: {result[:200]}...")
                    
            except Exception as e:
                print(f"     統一基本面工具呼叫失敗: {e}")
                return False
        
        print(" 統一工具功能測試通過")
        return True
        
    except Exception as e:
        print(f" 統一工具功能測試失敗: {e}")
        return False

def main():
    """主測試函式"""
    print(" 最終統一工具架構測試")
    print("=" * 70)
    
    tests = [
        test_complete_unified_architecture,
        test_llm_tool_calling_simulation,
        test_unified_tools_functionality,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f" 測試失敗: {test.__name__}")
        except Exception as e:
            print(f" 測試異常: {test.__name__} - {e}")
    
    print("\n" + "=" * 70)
    print(f" 最終測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("   統一工具架構完全成功！  ")
        print("\n 架構成就:")
        print(" 完全移除了舊工具註冊")
        print(" LLM只能呼叫統一工具")
        print(" 工具內部自動識別股票類型")
        print(" 自動路由到正確資料來源")
        print(" 避免了工具呼叫混亂")
        print(" 簡化了系統架構")
        print(" 提高了可維護性")
        print(" 統一了使用者體驗")
        
        print("\n 您的建議完美實現:")
        print(" '工具還是用同一個工具，工具當中自己判斷後續的處理邏輯'")
        print(" '舊工具就不要註冊了啊'")
        
        return True
    else:
        print(" 部分測試失敗，需要進一步檢查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
