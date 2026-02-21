#!/usr/bin/env python3
"""
調試工具選擇問題 - 檢查LLM實際看到的工具列表
"""

import os
import sys

def test_llm_tool_binding():
    """測試LLM工具綁定時的實際工具列表"""
    print("🔧 測試LLM工具綁定...")
    
    try:
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包
        toolkit = Toolkit(config)
        
        # 檢查工具包中的所有工具
        print(f"\n📋 工具包中的所有工具:")
        all_tools = []
        for attr_name in dir(toolkit):
            if not attr_name.startswith('_') and callable(getattr(toolkit, attr_name)):
                attr = getattr(toolkit, attr_name)
                if hasattr(attr, 'name'):
                    all_tools.append((attr_name, attr.name))
                    print(f"  {attr_name}: {attr.name}")
        
        # 檢查港股相關工具
        hk_related_tools = [tool for tool in all_tools if 'hk' in tool[0].lower() or 'hk' in tool[1].lower()]
        print(f"\n🇭🇰 港股相關工具:")
        for attr_name, tool_name in hk_related_tools:
            print(f"  {attr_name}: {tool_name}")
        
        # 檢查基本面相關工具
        fundamentals_tools = [tool for tool in all_tools if 'fundamental' in tool[0].lower() or 'fundamental' in tool[1].lower()]
        print(f"\n📊 基本面相關工具:")
        for attr_name, tool_name in fundamentals_tools:
            print(f"  {attr_name}: {tool_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具綁定測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_descriptions():
    """測試工具描述內容"""
    print("\n🔧 測試工具描述...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 檢查關鍵工具的描述
        key_tools = [
            'get_hk_stock_data_unified',
            'get_fundamentals_openai',
            'get_china_stock_data'
        ]
        
        for tool_name in key_tools:
            if hasattr(toolkit, tool_name):
                tool = getattr(toolkit, tool_name)
                print(f"\n📋 {tool_name}:")
                print(f"  名稱: {getattr(tool, 'name', 'N/A')}")
                print(f"  描述: {getattr(tool, 'description', 'N/A')}")
                
                # 檢查描述中是否提到港股
                desc = getattr(tool, 'description', '')
                if '港股' in desc or 'HK' in desc or 'Hong Kong' in desc:
                    print(f"  ✅ 描述中包含港股相關內容")
                else:
                    print(f"  ⚠️ 描述中不包含港股相關內容")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具描述測試失敗: {e}")
        return False

def test_fundamentals_analyst_tool_selection():
    """測試基本面分析師的實際工具選擇"""
    print("\n🔧 測試基本面分析師工具選擇...")
    
    try:
        # 模擬基本面分析師的工具選擇邏輯
        from tradingagents.utils.stock_utils import StockUtils
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 測試港股
        ticker = "0700.HK"
        market_info = StockUtils.get_market_info(ticker)
        is_china = market_info['is_china']
        is_hk = market_info['is_hk']
        is_us = market_info['is_us']
        
        print(f"\n📊 股票: {ticker}")
        print(f"  市場信息: {market_info['market_name']}")
        print(f"  is_china: {is_china}")
        print(f"  is_hk: {is_hk}")
        print(f"  is_us: {is_us}")
        
        # 模擬工具選擇邏輯
        if toolkit.config["online_tools"]:
            if is_china:
                tools = [
                    toolkit.get_china_stock_data,
                    toolkit.get_china_fundamentals
                ]
                print(f"  選擇的工具（A股）: {[tool.name for tool in tools]}")
            elif is_hk:
                tools = [toolkit.get_hk_stock_data_unified]
                print(f"  選擇的工具（港股）: {[tool.name for tool in tools]}")
            else:
                tools = [toolkit.get_fundamentals_openai]
                print(f"  選擇的工具（美股）: {[tool.name for tool in tools]}")
        
        # 檢查是否有工具名稱衝突
        tool_names = [tool.name for tool in tools]
        print(f"  工具名稱列表: {tool_names}")
        
        # 檢查工具描述
        for tool in tools:
            print(f"  工具 {tool.name} 描述: {tool.description[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本面分析師工具選擇測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🔧 工具選擇調試測試")
    print("=" * 60)
    
    tests = [
        test_llm_tool_binding,
        test_tool_descriptions,
        test_fundamentals_analyst_tool_selection,
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
