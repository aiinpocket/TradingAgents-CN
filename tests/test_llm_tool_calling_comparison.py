#!/usr/bin/env python3
"""
測試不同LLM模型在工具調用和技術分析方面的行為差異
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv()

def test_deepseek_tool_calling():
    """測試DeepSeek的工具調用行為"""
    print("🤖 測試DeepSeek工具調用行為")
    print("=" * 60)

    try:
        # 直接導入DeepSeek適配器，避免導入dashscope
        import sys
        sys.path.insert(0, str(project_root / "tradingagents" / "llm_adapters"))
        from deepseek_adapter import ChatDeepSeek
        from langchain_core.tools import BaseTool
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=2000
        )
        
        # 創建模擬的股票數據工具
        class MockChinaStockDataTool(BaseTool):
            name: str = "get_china_stock_data"
            description: str = "獲取中國A股股票000002的市場數據和技術指標"
            
            def _run(self, query: str = "") -> str:
                return """# 000002 万科A 股票數據分析

## 📊 實時行情
- 股票名稱: 万科A
- 當前價格: ¥6.56
- 涨跌幅: 0.61%
- 成交量: 934,783手

## 📈 技術指標
- 10日EMA: ¥6.45
- 50日SMA: ¥6.78
- 200日SMA: ¥7.12
- RSI: 42.5
- MACD: -0.08
- MACD信號線: -0.12
- 布林帶上轨: ¥7.20
- 布林帶中轨: ¥6.80
- 布林帶下轨: ¥6.40
- ATR: 0.25"""
        
        tools = [MockChinaStockDataTool()]
        
        # 測試提示詞
        prompt = """請對中國A股股票000002進行詳細的技術分析。

執行步骤：
1. 使用get_china_stock_data工具獲取股票市場數據
2. 基於獲取的真實數據進行深入的技術指標分析
3. 輸出完整的技術分析報告內容

重要要求：
- 必须調用工具獲取數據
- 必须輸出完整的技術分析報告內容，不要只是描述報告已完成
- 報告必须基於工具獲取的真實數據進行分析"""
        
        # 绑定工具並調用
        chain = deepseek_llm.bind_tools(tools)
        result = chain.invoke(prompt)
        
        print(f"📊 DeepSeek響應類型: {type(result)}")
        print(f"📊 DeepSeek工具調用數量: {len(result.tool_calls) if hasattr(result, 'tool_calls') else 0}")
        print(f"📊 DeepSeek響應內容長度: {len(result.content)}")
        print(f"📊 DeepSeek響應內容前500字符:")
        print("-" * 50)
        print(result.content[:500])
        print("-" * 50)
        
        if hasattr(result, 'tool_calls') and result.tool_calls:
            print(f"📊 DeepSeek工具調用詳情:")
            for i, call in enumerate(result.tool_calls):
                print(f"   工具{i+1}: {call.get('name', 'unknown')}")
                print(f"   參數: {call.get('args', {})}")
        
        return result
        
    except Exception as e:
        print(f"❌ DeepSeek測試失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dashscope_tool_calling():
    """測試百炼模型的工具調用行為"""
    print("\n🌟 測試百炼模型工具調用行為")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        from langchain_core.tools import BaseTool
        
        # 創建百炼實例
        dashscope_llm = ChatDashScope(
            model="qwen-plus",
            temperature=0.1,
            max_tokens=2000
        )
        
        # 創建相同的模擬工具
        class MockChinaStockDataTool(BaseTool):
            name: str = "get_china_stock_data"
            description: str = "獲取中國A股股票000002的市場數據和技術指標"
            
            def _run(self, query: str = "") -> str:
                return """# 000002 万科A 股票數據分析

## 📊 實時行情
- 股票名稱: 万科A
- 當前價格: ¥6.56
- 涨跌幅: 0.61%
- 成交量: 934,783手

## 📈 技術指標
- 10日EMA: ¥6.45
- 50日SMA: ¥6.78
- 200日SMA: ¥7.12
- RSI: 42.5
- MACD: -0.08
- MACD信號線: -0.12
- 布林帶上轨: ¥7.20
- 布林帶中轨: ¥6.80
- 布林帶下轨: ¥6.40
- ATR: 0.25"""
        
        tools = [MockChinaStockDataTool()]
        
        # 使用相同的提示詞
        prompt = """請對中國A股股票000002進行詳細的技術分析。

執行步骤：
1. 使用get_china_stock_data工具獲取股票市場數據
2. 基於獲取的真實數據進行深入的技術指標分析
3. 輸出完整的技術分析報告內容

重要要求：
- 必须調用工具獲取數據
- 必须輸出完整的技術分析報告內容，不要只是描述報告已完成
- 報告必须基於工具獲取的真實數據進行分析"""
        
        # 绑定工具並調用
        chain = dashscope_llm.bind_tools(tools)
        result = chain.invoke(prompt)
        
        print(f"📊 百炼響應類型: {type(result)}")
        print(f"📊 百炼工具調用數量: {len(result.tool_calls) if hasattr(result, 'tool_calls') else 0}")
        print(f"📊 百炼響應內容長度: {len(result.content)}")
        print(f"📊 百炼響應內容前500字符:")
        print("-" * 50)
        print(result.content[:500])
        print("-" * 50)
        
        if hasattr(result, 'tool_calls') and result.tool_calls:
            print(f"📊 百炼工具調用詳情:")
            for i, call in enumerate(result.tool_calls):
                print(f"   工具{i+1}: {call.get('name', 'unknown')}")
                print(f"   參數: {call.get('args', {})}")
        
        return result
        
    except Exception as e:
        print(f"❌ 百炼測試失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_results(deepseek_result, dashscope_result):
    """對比两個模型的結果"""
    print("\n🔍 結果對比分析")
    print("=" * 60)
    
    if deepseek_result and dashscope_result:
        # 工具調用對比
        deepseek_tools = len(deepseek_result.tool_calls) if hasattr(deepseek_result, 'tool_calls') else 0
        dashscope_tools = len(dashscope_result.tool_calls) if hasattr(dashscope_result, 'tool_calls') else 0
        
        print(f"📊 工具調用對比:")
        print(f"   DeepSeek: {deepseek_tools} 次工具調用")
        print(f"   百炼: {dashscope_tools} 次工具調用")
        
        # 內容長度對比
        deepseek_length = len(deepseek_result.content)
        dashscope_length = len(dashscope_result.content)
        
        print(f"\n📝 響應內容對比:")
        print(f"   DeepSeek: {deepseek_length} 字符")
        print(f"   百炼: {dashscope_length} 字符")
        
        # 內容類型分析
        print(f"\n🔍 內容類型分析:")
        
        # 檢查是否包含實际數據分析
        deepseek_has_data = any(keyword in deepseek_result.content for keyword in ["¥6.56", "RSI", "MACD", "万科A"])
        dashscope_has_data = any(keyword in dashscope_result.content for keyword in ["¥6.56", "RSI", "MACD", "万科A"])
        
        print(f"   DeepSeek包含實际數據: {'✅' if deepseek_has_data else '❌'}")
        print(f"   百炼包含實际數據: {'✅' if dashscope_has_data else '❌'}")
        
        # 檢查是否只是描述過程
        deepseek_describes_process = any(keyword in deepseek_result.content for keyword in ["首先", "然後", "接下來", "步骤"])
        dashscope_describes_process = any(keyword in dashscope_result.content for keyword in ["首先", "然後", "接下來", "步骤"])
        
        print(f"   DeepSeek描述分析過程: {'⚠️' if deepseek_describes_process else '✅'}")
        print(f"   百炼描述分析過程: {'⚠️' if dashscope_describes_process else '✅'}")
        
        # 总結
        print(f"\n📋 总結:")
        if deepseek_tools > 0 and deepseek_has_data:
            print(f"   ✅ DeepSeek: 正確調用工具並分析數據")
        else:
            print(f"   ❌ DeepSeek: 未正確執行工具調用或數據分析")
            
        if dashscope_tools > 0 and dashscope_has_data:
            print(f"   ✅ 百炼: 正確調用工具並分析數據")
        else:
            print(f"   ❌ 百炼: 未正確執行工具調用或數據分析")

def main():
    """主函數"""
    print("🔬 LLM工具調用行為對比測試")
    print("=" * 80)
    
    # 檢查API密鑰
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not deepseek_key:
        print("⚠️ 未找到DEEPSEEK_API_KEY，跳過DeepSeek測試")
        deepseek_result = None
    else:
        deepseek_result = test_deepseek_tool_calling()
    
    if not dashscope_key:
        print("⚠️ 未找到DASHSCOPE_API_KEY，跳過百炼測試")
        dashscope_result = None
    else:
        dashscope_result = test_dashscope_tool_calling()
    
    # 對比結果
    if deepseek_result or dashscope_result:
        compare_results(deepseek_result, dashscope_result)
    else:
        print("❌ 無法進行對比，两個模型都測試失败")
    
    print("\n" + "=" * 80)
    print("🎯 測試完成！")

if __name__ == "__main__":
    main()
