#!/usr/bin/env python3
"""
調試工具绑定問題
驗證LLM是否能訪問未绑定的工具
"""

import os
import sys

def test_tool_isolation():
    """測試工具隔離機制"""
    print("🔧 測試工具隔離機制...")
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        # 檢查API密鑰
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("⚠️ 未找到DASHSCOPE_API_KEY，跳過測試")
            return True
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 創建LLM
        llm = ChatDashScopeOpenAI(
            model="qwen-turbo",
            temperature=0.1,
            max_tokens=200
        )
        
        print(f"\n📋 工具包中的所有工具:")
        all_tools = []
        for attr_name in dir(toolkit):
            if not attr_name.startswith('_') and callable(getattr(toolkit, attr_name)):
                attr = getattr(toolkit, attr_name)
                if hasattr(attr, 'name'):
                    all_tools.append(attr.name)
                    print(f"  - {attr.name}")
        
        print(f"\n🔧 測試1: 只绑定港股工具")
        hk_tools = [toolkit.get_hk_stock_data_unified]
        llm_hk = llm.bind_tools(hk_tools)
        
        print(f"  绑定的工具: {[tool.name for tool in hk_tools]}")
        
        # 測試是否能調用其他工具
        test_message = HumanMessage(content="請調用get_fundamentals_openai工具獲取0700.HK的數據")
        
        try:
            response = llm_hk.invoke([test_message])
            print(f"  響應類型: {type(response)}")
            print(f"  工具調用數量: {len(getattr(response, 'tool_calls', []))}")
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                called_tools = [call.get('name', 'unknown') for call in response.tool_calls]
                print(f"  實际調用的工具: {called_tools}")
                
                # 檢查是否調用了未绑定的工具
                unexpected_tools = [tool for tool in called_tools if tool not in [t.name for t in hk_tools]]
                if unexpected_tools:
                    print(f"  ❌ 調用了未绑定的工具: {unexpected_tools}")
                    return False
                else:
                    print(f"  ✅ 只調用了绑定的工具")
            else:
                print(f"  ℹ️ 没有工具調用")
                
        except Exception as e:
            print(f"  ❌ 調用失败: {e}")
            return False
        
        print(f"\n🔧 測試2: 創建新的LLM實例")
        llm2 = ChatDashScopeOpenAI(
            model="qwen-turbo",
            temperature=0.1,
            max_tokens=200
        )
        
        china_tools = [toolkit.get_china_stock_data]
        llm2_china = llm2.bind_tools(china_tools)
        
        print(f"  绑定的工具: {[tool.name for tool in china_tools]}")
        
        test_message2 = HumanMessage(content="請調用get_hk_stock_data_unified工具獲取0700.HK的數據")
        
        try:
            response2 = llm2_china.invoke([test_message2])
            print(f"  響應類型: {type(response2)}")
            print(f"  工具調用數量: {len(getattr(response2, 'tool_calls', []))}")
            
            if hasattr(response2, 'tool_calls') and response2.tool_calls:
                called_tools2 = [call.get('name', 'unknown') for call in response2.tool_calls]
                print(f"  實际調用的工具: {called_tools2}")
                
                # 檢查是否調用了未绑定的工具
                unexpected_tools2 = [tool for tool in called_tools2 if tool not in [t.name for t in china_tools]]
                if unexpected_tools2:
                    print(f"  ❌ 調用了未绑定的工具: {unexpected_tools2}")
                    return False
                else:
                    print(f"  ✅ 只調用了绑定的工具")
            else:
                print(f"  ℹ️ 没有工具調用")
                
        except Exception as e:
            print(f"  ❌ 調用失败: {e}")
            return False
        
        print(f"\n✅ 工具隔離測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 工具隔離測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_instance_reuse():
    """測試LLM實例複用問題"""
    print("\n🔧 測試LLM實例複用...")
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 檢查是否存在全局LLM實例
        print(f"  檢查LLM實例創建...")
        
        llm1 = ChatDashScopeOpenAI(model="qwen-turbo")
        llm2 = ChatDashScopeOpenAI(model="qwen-turbo")
        
        print(f"  LLM1 ID: {id(llm1)}")
        print(f"  LLM2 ID: {id(llm2)}")
        print(f"  是否為同一實例: {llm1 is llm2}")
        
        # 檢查工具绑定狀態
        tools1 = [toolkit.get_hk_stock_data_unified]
        tools2 = [toolkit.get_china_stock_data]
        
        llm1_with_tools = llm1.bind_tools(tools1)
        llm2_with_tools = llm2.bind_tools(tools2)
        
        print(f"  LLM1绑定工具: {[t.name for t in tools1]}")
        print(f"  LLM2绑定工具: {[t.name for t in tools2]}")
        
        # 檢查绑定後的實例
        print(f"  LLM1绑定後ID: {id(llm1_with_tools)}")
        print(f"  LLM2绑定後ID: {id(llm2_with_tools)}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM實例複用測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔧 工具绑定問題調試")
    print("=" * 60)
    
    tests = [
        test_llm_instance_reuse,
        test_tool_isolation,
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
        print("🎉 所有測試通過！")
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步檢查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
