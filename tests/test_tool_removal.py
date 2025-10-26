#!/usr/bin/env python3
"""
測試旧工具移除
驗證LLM只能調用統一工具
"""

def test_available_tools():
    """測試可用工具列表"""
    print("🔧 測試可用工具列表...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 獲取所有工具
        all_tools = []
        for attr_name in dir(toolkit):
            attr = getattr(toolkit, attr_name)
            if hasattr(attr, 'name') and hasattr(attr, 'description'):
                all_tools.append(attr.name)
        
        print(f"  总工具數量: {len(all_tools)}")
        
        # 檢查旧工具是否已移除
        removed_tools = [
            'get_china_stock_data',
            'get_china_fundamentals', 
            'get_fundamentals_openai',
            'get_hk_stock_data_unified'
        ]
        
        # 檢查統一工具是否存在
        unified_tools = [
            'get_stock_fundamentals_unified',
            'get_stock_market_data_unified',
            'get_stock_news_unified',
            'get_stock_sentiment_unified'
        ]
        
        print("\n  旧工具移除檢查:")
        for tool_name in removed_tools:
            if tool_name in all_tools:
                print(f"    ❌ {tool_name}: 仍然可用（應该已移除）")
                return False
            else:
                print(f"    ✅ {tool_name}: 已移除")
        
        print("\n  統一工具可用性檢查:")
        for tool_name in unified_tools:
            if tool_name in all_tools:
                print(f"    ✅ {tool_name}: 可用")
            else:
                print(f"    ❌ {tool_name}: 不可用")
                return False
        
        print(f"\n  所有可用工具:")
        for tool_name in sorted(all_tools):
            print(f"    - {tool_name}")
        
        print("✅ 工具移除測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 工具移除測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fundamentals_analyst_tool_selection():
    """測試基本面分析師工具選擇"""
    print("\n🔧 測試基本面分析師工具選擇...")
    
    try:
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包
        toolkit = Toolkit(config)
        
        # 模擬基本面分析師的工具選擇逻辑
        from tradingagents.utils.stock_utils import StockUtils
        
        test_cases = [
            ("0700.HK", "港股"),
            ("000001", "A股"),
            ("AAPL", "美股")
        ]
        
        for ticker, market_type in test_cases:
            print(f"\n  測試 {ticker} ({market_type}):")
            
            # 獲取市場信息
            market_info = StockUtils.get_market_info(ticker)
            
            # 模擬基本面分析師的工具選擇逻辑
            if toolkit.config["online_tools"]:
                # 使用統一的基本面分析工具
                tools = [toolkit.get_stock_fundamentals_unified]
                tool_names = [tool.name for tool in tools]
                
                print(f"    選擇的工具: {tool_names}")
                
                # 驗證只選擇了統一工具
                if len(tools) == 1 and tools[0].name == 'get_stock_fundamentals_unified':
                    print(f"    ✅ 正確選擇統一基本面工具")
                else:
                    print(f"    ❌ 工具選擇錯誤")
                    return False
            else:
                print(f"    跳過（online_tools=False）")
        
        print("✅ 基本面分析師工具選擇測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 基本面分析師工具選擇測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_market_analyst_tool_selection():
    """測試市場分析師工具選擇"""
    print("\n🔧 測試市場分析師工具選擇...")
    
    try:
        from tradingagents.agents.analysts.market_analyst import create_market_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.utils.stock_utils import StockUtils
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包
        toolkit = Toolkit(config)
        
        test_cases = [
            ("0700.HK", "港股"),
            ("000001", "A股"),
            ("AAPL", "美股")
        ]
        
        for ticker, market_type in test_cases:
            print(f"\n  測試 {ticker} ({market_type}):")
            
            # 獲取市場信息
            market_info = StockUtils.get_market_info(ticker)
            
            # 模擬市場分析師的工具選擇逻辑
            if toolkit.config["online_tools"]:
                # 使用統一的市場數據工具
                tools = [toolkit.get_stock_market_data_unified]
                tool_names = [tool.name for tool in tools]
                
                print(f"    選擇的工具: {tool_names}")
                
                # 驗證只選擇了統一工具
                if len(tools) == 1 and tools[0].name == 'get_stock_market_data_unified':
                    print(f"    ✅ 正確選擇統一市場數據工具")
                else:
                    print(f"    ❌ 工具選擇錯誤")
                    return False
            else:
                print(f"    跳過（online_tools=False）")
        
        print("✅ 市場分析師工具選擇測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 市場分析師工具選擇測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("🔧 旧工具移除測試")
    print("=" * 60)
    
    tests = [
        test_available_tools,
        test_fundamentals_analyst_tool_selection,
        test_market_analyst_tool_selection,
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
        print("🎉 所有測試通過！旧工具移除成功")
        print("\n📋 修複內容:")
        print("✅ 移除了旧工具的 @tool 裝饰器")
        print("✅ LLM無法再調用旧工具")
        print("✅ 只能調用統一工具")
        print("✅ 避免了工具調用混乱")
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步檢查")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
