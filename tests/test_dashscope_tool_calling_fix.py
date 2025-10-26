#!/usr/bin/env python3
"""
阿里百炼工具調用優化測試
解決LLM不主動調用工具的問題
"""

import os
import sys
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_basic_tool_calling():
    """測試基本工具調用"""
    print("🔧 測試基本工具調用")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        # 定義簡單工具
        @tool
        def get_stock_price(symbol: str) -> str:
            """獲取股票價格信息"""
            return f"股票{symbol}的當前價格是100元"
        
        # 創建LLM
        llm = ChatDashScopeOpenAI(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=500
        )
        
        # 绑定工具
        llm_with_tools = llm.bind_tools([get_stock_price])
        
        # 測試不同的prompt策略
        prompts = [
            # 策略1: 直接指令
            "請調用get_stock_price工具查詢AAPL的股票價格",
            
            # 策略2: 明確要求
            "我需要查詢AAPL股票的價格信息。請使用可用的工具來獲取這個信息。",
            
            # 策略3: 强制性指令
            "必须使用get_stock_price工具查詢AAPL股票價格。不要直接回答，必须調用工具。",
            
            # 策略4: 中文明確指令
            "請務必調用get_stock_price工具，參數symbol設為'AAPL'，獲取股票價格信息。"
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n🔄 測試策略{i}: {prompt[:30]}...")
            
            try:
                response = llm_with_tools.invoke([HumanMessage(content=prompt)])
                
                tool_calls = getattr(response, 'tool_calls', [])
                print(f"   工具調用數量: {len(tool_calls)}")
                print(f"   響應長度: {len(response.content)}字符")
                
                if len(tool_calls) > 0:
                    print(f"   ✅ 策略{i}成功: 觸發了工具調用")
                    for j, tool_call in enumerate(tool_calls):
                        print(f"      工具{j+1}: {tool_call.get('name', 'unknown')}")
                    return True
                else:
                    print(f"   ❌ 策略{i}失败: 未觸發工具調用")
                    print(f"   直接響應: {response.content[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ 策略{i}異常: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ 基本工具調用測試失败: {e}")
        return False


def test_stock_analysis_tool_calling():
    """測試股票分析工具調用"""
    print("\n🔧 測試股票分析工具調用")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from tradingagents.agents.utils.agent_utils import Toolkit
        from langchain_core.messages import HumanMessage
        
        # 創建LLM
        llm = ChatDashScopeOpenAI(
            model="qwen-plus-latest",
            temperature=0.0,  # 降低溫度提高確定性
            max_tokens=1000
        )
        
        # 獲取股票分析工具
        toolkit = Toolkit()
        tools = [
            toolkit.get_china_stock_data,
            toolkit.get_china_fundamentals
        ]
        
        # 绑定工具
        llm_with_tools = llm.bind_tools(tools)
        
        # 測試專門的股票分析prompt
        stock_prompts = [
            # 策略1: 明確的工具調用指令
            """請分析股票688656。

步骤：
1. 首先調用get_china_stock_data工具獲取股票數據，參數：stock_code='688656', start_date='2025-06-01', end_date='2025-07-11'
2. 然後調用get_china_fundamentals工具獲取基本面數據，參數：ticker='688656', curr_date='2025-07-11'

請嚴格按照上述步骤執行，必须調用工具。""",

            # 策略2: 問題導向
            """我想了解688656這只股票的詳細情况，包括：
- 最近的價格走势和交易數據
- 基本面分析和財務狀况

請使用可用的工具來獲取這些信息。""",

            # 策略3: 强制工具調用
            """分析688656股票。註意：你必须使用工具來獲取數據，不能凭空回答。請調用相關工具獲取股票數據和基本面信息。"""
        ]
        
        for i, prompt in enumerate(stock_prompts, 1):
            print(f"\n🔄 測試股票分析策略{i}...")
            
            try:
                response = llm_with_tools.invoke([HumanMessage(content=prompt)])
                
                tool_calls = getattr(response, 'tool_calls', [])
                print(f"   工具調用數量: {len(tool_calls)}")
                print(f"   響應長度: {len(response.content)}字符")
                
                if len(tool_calls) > 0:
                    print(f"   ✅ 股票分析策略{i}成功")
                    for j, tool_call in enumerate(tool_calls):
                        tool_name = tool_call.get('name', 'unknown')
                        tool_args = tool_call.get('args', {})
                        print(f"      工具{j+1}: {tool_name}({tool_args})")
                    return True
                else:
                    print(f"   ❌ 股票分析策略{i}失败")
                    print(f"   直接響應: {response.content[:150]}...")
                    
            except Exception as e:
                print(f"   ❌ 股票分析策略{i}異常: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ 股票分析工具調用測試失败: {e}")
        return False


def test_parameter_optimization():
    """測試參數優化"""
    print("\n🔧 測試參數優化")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        # 定義測試工具
        @tool
        def analyze_stock(symbol: str, period: str) -> str:
            """分析股票"""
            return f"分析{symbol}股票，時間周期{period}"
        
        # 測試不同參數配置
        configs = [
            {"temperature": 0.0, "max_tokens": 500, "description": "低溫度"},
            {"temperature": 0.1, "max_tokens": 500, "description": "默認溫度"},
            {"temperature": 0.3, "max_tokens": 500, "description": "中等溫度"},
        ]
        
        prompt = "請調用analyze_stock工具分析AAPL股票，時間周期設為'1month'"
        
        for config in configs:
            print(f"\n🔄 測試{config['description']}配置...")
            
            try:
                llm = ChatDashScopeOpenAI(
                    model="qwen-plus-latest",
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"]
                )
                
                llm_with_tools = llm.bind_tools([analyze_stock])
                response = llm_with_tools.invoke([HumanMessage(content=prompt)])
                
                tool_calls = getattr(response, 'tool_calls', [])
                print(f"   工具調用數量: {len(tool_calls)}")
                
                if len(tool_calls) > 0:
                    print(f"   ✅ {config['description']}配置成功")
                    return config
                else:
                    print(f"   ❌ {config['description']}配置失败")
                    
            except Exception as e:
                print(f"   ❌ {config['description']}配置異常: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ 參數優化測試失败: {e}")
        return None


def test_model_comparison():
    """測試不同模型的工具調用能力"""
    print("\n🔧 測試不同模型的工具調用能力")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        # 定義測試工具
        @tool
        def get_info(query: str) -> str:
            """獲取信息"""
            return f"查詢結果: {query}"
        
        # 測試不同模型
        models = [
            "qwen-turbo",
            "qwen-plus",
            "qwen-plus-latest",
            "qwen-max-latest"
        ]
        
        prompt = "請調用get_info工具查詢'股票市場今日表現'"
        
        for model in models:
            print(f"\n🔄 測試模型: {model}...")
            
            try:
                llm = ChatDashScopeOpenAI(
                    model=model,
                    temperature=0.1,
                    max_tokens=300
                )
                
                llm_with_tools = llm.bind_tools([get_info])
                response = llm_with_tools.invoke([HumanMessage(content=prompt)])
                
                tool_calls = getattr(response, 'tool_calls', [])
                print(f"   工具調用數量: {len(tool_calls)}")
                
                if len(tool_calls) > 0:
                    print(f"   ✅ {model}: 支持工具調用")
                else:
                    print(f"   ❌ {model}: 不支持工具調用")
                    print(f"   響應: {response.content[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ {model}: 測試異常 - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型比較測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔬 阿里百炼工具調用優化測試")
    print("=" * 70)
    print("💡 目標: 解決LLM不主動調用工具的問題")
    print("=" * 70)
    
    # 檢查API密鑰
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 未找到DASHSCOPE_API_KEY環境變量")
        return
    
    # 運行測試
    tests = [
        ("基本工具調用", test_basic_tool_calling),
        ("股票分析工具調用", test_stock_analysis_tool_calling),
        ("參數優化", test_parameter_optimization),
        ("模型比較", test_model_comparison)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}測試異常: {e}")
            results.append((test_name, False))
    
    # 总結
    print("\n📋 工具調用優化測試总結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        if result:
            status = "✅ 通過"
            passed += 1
        else:
            status = "❌ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    if passed > 0:
        print("\n💡 建议:")
        print("   1. 使用更明確的工具調用指令")
        print("   2. 調整temperature參數")
        print("   3. 嘗試不同的模型版本")
        print("   4. 考慮使用强制工具調用模式")
    else:
        print("\n⚠️ 阿里百炼可能需要特殊的工具調用處理")
        print("   建议使用手動工具調用作為备用方案")


if __name__ == "__main__":
    main()
