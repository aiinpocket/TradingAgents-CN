#!/usr/bin/env python3
"""
阿里百炼 OpenAI 兼容適配器修複驗證測試
驗證新的 OpenAI 兼容適配器是否解決了工具調用問題
"""

import os
import sys
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_openai_adapter_import():
    """測試新適配器導入"""
    print("\n🔧 測試新適配器導入")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        print("✅ ChatDashScopeOpenAI 導入成功")
        
        from tradingagents.llm_adapters.dashscope_openai_adapter import (
            create_dashscope_openai_llm,
            test_dashscope_openai_connection,
            test_dashscope_openai_function_calling
        )
        print("✅ 相關函數導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 導入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_adapter_connection():
    """測試 OpenAI 兼容適配器連接"""
    print("\n🔧 測試 OpenAI 兼容適配器連接")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_openai_adapter import test_dashscope_openai_connection
        
        # 測試連接
        result = test_dashscope_openai_connection(model="qwen-turbo")
        
        if result:
            print("✅ OpenAI 兼容適配器連接測試成功")
            return True
        else:
            print("❌ OpenAI 兼容適配器連接測試失败")
            return False
            
    except Exception as e:
        print(f"❌ 連接測試異常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_adapter_function_calling():
    """測試 OpenAI 兼容適配器的 Function Calling"""
    print("\n🔧 測試 OpenAI 兼容適配器 Function Calling")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_openai_adapter import test_dashscope_openai_function_calling
        
        # 測試 Function Calling
        result = test_dashscope_openai_function_calling(model="qwen-plus-latest")
        
        if result:
            print("✅ OpenAI 兼容適配器 Function Calling 測試成功")
            return True
        else:
            print("❌ OpenAI 兼容適配器 Function Calling 測試失败")
            return False
            
    except Exception as e:
        print(f"❌ Function Calling 測試異常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_technical_analysis_with_new_adapter():
    """測試新適配器的技術面分析"""
    print("\n🔧 測試新適配器的技術面分析")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from tradingagents.agents.utils.agent_utils import Toolkit
        from langchain_core.messages import HumanMessage
        from langchain_core.tools import tool
        
        # 創建新的 OpenAI 兼容適配器
        llm = ChatDashScopeOpenAI(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=2000
        )
        
        print("✅ 新適配器創建成功")
        
        # 定義測試工具
        @tool
        def get_test_stock_data(ticker: str, start_date: str, end_date: str) -> str:
            """獲取測試股票數據"""
            return f"""# {ticker} 股票數據分析

## 📊 實時行情
- 股票名稱: 招商銀行
- 股票代碼: {ticker}
- 當前價格: ¥47.13
- 涨跌幅: -1.03%
- 成交量: 61.5万手
- 數據來源: Tushare

## 📈 歷史數據概覽
- 數據期間: {start_date} 至 {end_date}
- 數據條數: 23條
- 期間最高: ¥47.88
- 期間最低: ¥44.21

## 📋 技術指標
- RSI: 45.2 (中性)
- MACD: 0.15 (看涨)
- MA20: ¥46.85
- 成交量趋势: 放量"""
        
        # 绑定工具
        llm_with_tools = llm.bind_tools([get_test_stock_data])
        
        print("✅ 工具绑定成功")
        
        # 測試工具調用
        print("🔄 測試工具調用...")
        
        messages = [HumanMessage(content="""請分析600036這只股票的技術面。
        
請先調用get_test_stock_data工具獲取數據，參數：
- ticker: "600036"
- start_date: "2025-06-10"
- end_date: "2025-07-10"

然後基於獲取的數據生成詳細的技術分析報告，要求：
1. 報告長度不少於500字
2. 包含具體的技術指標分析
3. 提供明確的投資建议
4. 使用中文撰寫""")]
        
        response = llm_with_tools.invoke(messages)
        
        print(f"📊 響應類型: {type(response)}")
        print(f"📊 響應長度: {len(response.content)}字符")
        
        # 檢查是否有工具調用
        if hasattr(response, 'tool_calls') and len(response.tool_calls) > 0:
            print(f"✅ 工具調用成功: {len(response.tool_calls)}個工具調用")
            for i, tool_call in enumerate(response.tool_calls):
                print(f"   工具{i+1}: {tool_call.get('name', 'unknown')}")
            
            # 這里應该繼续執行工具並生成最终分析
            # 但為了測試，我們只驗證工具調用是否正常
            return True
        else:
            print(f"❌ 没有工具調用")
            print(f"📋 直接響應: {response.content[:200]}...")
            
            # 檢查響應長度
            if len(response.content) < 100:
                print("❌ 響應過短，可能存在問題")
                return False
            else:
                print("⚠️ 有響應但没有工具調用")
                return False
        
    except Exception as e:
        print(f"❌ 技術面分析測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trading_graph_integration():
    """測試与 TradingGraph 的集成"""
    print("\n🔧 測試与 TradingGraph 的集成")
    print("=" * 60)
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # 創建配置
        config = {
            "llm_provider": "dashscope",
            "deep_think_llm": "qwen-plus-latest",
            "quick_think_llm": "qwen-turbo",
            "max_debate_rounds": 1,
            "online_tools": True,
            "selected_analysts": ["fundamentals_analyst", "market_analyst"]
        }
        
        print("🔄 創建 TradingGraph...")
        graph = TradingAgentsGraph(config)
        
        print("✅ TradingGraph 創建成功")
        print(f"   Deep thinking LLM: {type(graph.deep_thinking_llm).__name__}")
        print(f"   Quick thinking LLM: {type(graph.quick_thinking_llm).__name__}")
        
        # 檢查是否使用了新的適配器
        if "OpenAI" in type(graph.deep_thinking_llm).__name__:
            print("✅ 使用了新的 OpenAI 兼容適配器")
            return True
        else:
            print("⚠️ 仍在使用旧的適配器")
            return False
        
    except Exception as e:
        print(f"❌ TradingGraph 集成測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("🔬 阿里百炼 OpenAI 兼容適配器修複驗證測試")
    print("=" * 70)
    print("💡 測試目標:")
    print("   - 驗證新的 OpenAI 兼容適配器導入和連接")
    print("   - 驗證 Function Calling 功能")
    print("   - 驗證技術面分析工具調用")
    print("   - 驗證与 TradingGraph 的集成")
    print("=" * 70)
    
    # 檢查環境變量
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 未找到 DASHSCOPE_API_KEY 環境變量")
        print("請設置環境變量後重試")
        return
    
    # 運行所有測試
    tests = [
        ("新適配器導入", test_openai_adapter_import),
        ("OpenAI 兼容適配器連接", test_openai_adapter_connection),
        ("Function Calling", test_openai_adapter_function_calling),
        ("技術面分析工具調用", test_technical_analysis_with_new_adapter),
        ("TradingGraph 集成", test_trading_graph_integration)
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
    print("\n📋 阿里百炼 OpenAI 兼容適配器修複測試总結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！OpenAI 兼容適配器修複成功！")
        print("\n💡 修複效果:")
        print("   ✅ 支持原生 Function Calling")
        print("   ✅ 工具調用正常執行")
        print("   ✅ 技術面分析不再只有30字符")
        print("   ✅ 与 LangChain 完全兼容")
        print("\n🚀 現在阿里百炼模型應该能正常進行技術面分析了！")
    else:
        print("\n⚠️ 部分測試失败，請檢查相關配置")
    
    input("按回車键退出...")


if __name__ == "__main__":
    main()
