#!/usr/bin/env python3
"""
測試完整的工具調用工作流程
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv()

def test_deepseek_complete_workflow():
    """測試DeepSeek的完整工具調用工作流程"""
    print("🤖 測試DeepSeek完整工作流程")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        from langchain_core.tools import BaseTool
        from langchain_core.messages import HumanMessage, ToolMessage
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=2000
        )
        
        # 創建模擬工具
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
        
        # 第一步：發送初始請求
        prompt = """請對中國A股股票000002進行詳細的技術分析。

要求：
1. 首先調用get_china_stock_data工具獲取數據
2. 然後基於獲取的數據進行分析
3. 輸出完整的技術分析報告"""
        
        print("📤 發送初始請求...")
        chain = deepseek_llm.bind_tools(tools)
        result1 = chain.invoke([HumanMessage(content=prompt)])
        
        print(f"📊 第一次響應:")
        print(f"   工具調用數量: {len(result1.tool_calls) if hasattr(result1, 'tool_calls') else 0}")
        print(f"   響應內容長度: {len(result1.content)}")
        print(f"   響應內容: {result1.content[:200]}...")
        
        if hasattr(result1, 'tool_calls') and result1.tool_calls:
            print(f"\n🔧 執行工具調用...")
            
            # 模擬工具執行
            tool_messages = []
            for tool_call in result1.tool_calls:
                tool_name = tool_call.get('name')
                tool_id = tool_call.get('id')
                
                print(f"   執行工具: {tool_name}")
                
                # 執行工具
                tool = tools[0]  # 我們只有一個工具
                tool_result = tool._run("")
                
                # 創建工具消息
                tool_message = ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_id
                )
                tool_messages.append(tool_message)
            
            # 第二步：發送工具結果，要求生成分析
            print(f"\n📤 發送工具結果，要求生成分析...")
            messages = [
                HumanMessage(content=prompt),
                result1,
                *tool_messages,
                HumanMessage(content="現在請基於上述工具獲取的數據，生成詳細的技術分析報告。報告應该包含具體的數據分析和投資建议。")
            ]
            
            result2 = deepseek_llm.invoke(messages)
            
            print(f"📊 第二次響應:")
            print(f"   響應內容長度: {len(result2.content)}")
            print(f"   響應內容前500字符:")
            print("-" * 50)
            print(result2.content[:500])
            print("-" * 50)
            
            # 檢查是否包含實际數據分析
            has_data = any(keyword in result2.content for keyword in ["¥6.56", "RSI", "MACD", "万科A", "42.5"])
            print(f"   包含實际數據: {'✅' if has_data else '❌'}")
            
            return result2
        else:
            print("❌ 没有工具調用")
            return result1
        
    except Exception as e:
        print(f"❌ DeepSeek測試失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dashscope_react_agent():
    """測試百炼的ReAct Agent模式"""
    print("\n🌟 測試百炼ReAct Agent模式")
    print("=" * 60)
    
    try:
        from langchain.agents import create_react_agent, AgentExecutor
        from langchain_core.prompts import PromptTemplate
        from langchain_core.tools import BaseTool
        
        # 檢查是否有百炼API密鑰
        if not os.getenv("DASHSCOPE_API_KEY"):
            print("⚠️ 未找到DASHSCOPE_API_KEY，跳過百炼測試")
            return None
        
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        
        # 創建百炼實例
        dashscope_llm = ChatDashScope(
            model="qwen-plus",
            temperature=0.1,
            max_tokens=2000
        )
        
        # 創建工具
        class MockChinaStockDataTool(BaseTool):
            name: str = "get_china_stock_data"
            description: str = "獲取中國A股股票000002的市場數據和技術指標。直接調用，無需參數。"
            
            def _run(self, query: str = "") -> str:
                print("🔧 [工具執行] get_china_stock_data被調用")
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
        
        # 創建ReAct Agent
        prompt_template = """請對中國A股股票000002進行詳細的技術分析。

執行步骤：
1. 使用get_china_stock_data工具獲取股票市場數據
2. 基於獲取的真實數據進行深入的技術指標分析
3. 輸出完整的技術分析報告內容

重要要求：
- 必须調用工具獲取數據
- 必须輸出完整的技術分析報告內容，不要只是描述報告已完成
- 報告必须基於工具獲取的真實數據進行分析

你有以下工具可用:
{tools}

使用以下格式:

Question: 輸入的問題
Thought: 你應该思考要做什么
Action: 要採取的行動，應该是[{tool_names}]之一
Action Input: 行動的輸入
Observation: 行動的結果
... (這個Thought/Action/Action Input/Observation可以重複N次)
Thought: 我現在知道最终答案了
Final Answer: 對原始輸入問題的最终答案

Question: {input}
{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(prompt_template)
        
        # 創建agent
        agent = create_react_agent(dashscope_llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=3)
        
        print("📤 執行ReAct Agent...")
        result = agent_executor.invoke({
            "input": "請對中國A股股票000002進行詳細的技術分析"
        })
        
        print(f"📊 ReAct Agent結果:")
        print(f"   輸出長度: {len(result['output'])}")
        print(f"   輸出內容前500字符:")
        print("-" * 50)
        print(result['output'][:500])
        print("-" * 50)
        
        # 檢查是否包含實际數據分析
        has_data = any(keyword in result['output'] for keyword in ["¥6.56", "RSI", "MACD", "万科A", "42.5"])
        print(f"   包含實际數據: {'✅' if has_data else '❌'}")
        
        return result
        
    except Exception as e:
        print(f"❌ 百炼ReAct Agent測試失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函數"""
    print("🔬 完整工具調用工作流程測試")
    print("=" * 80)
    
    # 測試DeepSeek
    deepseek_result = test_deepseek_complete_workflow()
    
    # 測試百炼ReAct Agent
    dashscope_result = test_dashscope_react_agent()
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    if deepseek_result:
        has_data = any(keyword in deepseek_result.content for keyword in ["¥6.56", "RSI", "MACD", "万科A"])
        print(f"✅ DeepSeek: {'成功生成基於數據的分析' if has_data else '調用工具但分析不完整'}")
    else:
        print(f"❌ DeepSeek: 測試失败")
    
    if dashscope_result:
        has_data = any(keyword in dashscope_result['output'] for keyword in ["¥6.56", "RSI", "MACD", "万科A"])
        print(f"✅ 百炼ReAct: {'成功生成基於數據的分析' if has_data else '執行但分析不完整'}")
    else:
        print(f"❌ 百炼ReAct: 測試失败")
    
    print("\n🎯 測試完成！")

if __name__ == "__main__":
    main()
