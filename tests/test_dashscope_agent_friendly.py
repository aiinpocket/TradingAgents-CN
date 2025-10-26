#!/usr/bin/env python3
"""
阿里百炼工具調用測試 - Agent友好版本
專門為agent執行優化，避免闪退問題
"""

import os
import sys
import time
import traceback

# 强制刷新輸出
def flush_print(msg):
    """强制刷新輸出"""
    print(msg)
    sys.stdout.flush()
    time.sleep(0.1)  # 給agent時間捕獲輸出

def main():
    """主測試函數"""
    flush_print("🔬 阿里百炼工具調用測試 - Agent友好版本")
    flush_print("=" * 60)
    
    try:
        # 添加項目根目錄到Python路徑
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        flush_print("✅ 項目路徑配置完成")
        
        # 檢查API密鑰
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            flush_print("❌ 未找到DASHSCOPE_API_KEY環境變量")
            return False
        
        flush_print(f"✅ API密鑰已配置: {api_key[:10]}...")
        
        # 測試1: 基本導入
        flush_print("\n🔧 測試1: 基本導入")
        flush_print("-" * 40)
        
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        flush_print("✅ 所有模塊導入成功")
        
        # 測試2: LLM創建
        flush_print("\n🔧 測試2: LLM創建")
        flush_print("-" * 40)
        
        llm = ChatDashScopeOpenAI(
            model="qwen-turbo",
            temperature=0.1,
            max_tokens=200
        )
        
        flush_print("✅ LLM實例創建成功")
        
        # 測試3: 工具定義和绑定
        flush_print("\n🔧 測試3: 工具定義和绑定")
        flush_print("-" * 40)
        
        @tool
        def get_stock_info(symbol: str) -> str:
            """獲取股票信息"""
            return f"股票{symbol}的信息: 價格100元，涨幅+2.5%"
        
        llm_with_tools = llm.bind_tools([get_stock_info])
        flush_print("✅ 工具绑定成功")
        
        # 測試4: 簡單調用（不要求工具調用）
        flush_print("\n🔧 測試4: 簡單調用")
        flush_print("-" * 40)
        
        simple_response = llm.invoke([
            HumanMessage(content="請簡單回複：你好")
        ])
        
        flush_print(f"✅ 簡單調用成功")
        flush_print(f"   響應長度: {len(simple_response.content)}字符")
        flush_print(f"   響應內容: {simple_response.content}")
        
        # 測試5: 工具調用測試
        flush_print("\n🔧 測試5: 工具調用測試")
        flush_print("-" * 40)
        
        # 嘗試多種prompt策略
        prompts = [
            "請調用get_stock_info工具查詢AAPL股票信息",
            "我需要AAPL的股票信息，請使用可用的工具",
            "必须調用get_stock_info工具，參數symbol='AAPL'"
        ]
        
        tool_call_success = False
        
        for i, prompt in enumerate(prompts, 1):
            flush_print(f"\n   策略{i}: {prompt[:30]}...")
            
            try:
                response = llm_with_tools.invoke([HumanMessage(content=prompt)])
                
                tool_calls = getattr(response, 'tool_calls', [])
                flush_print(f"   工具調用數量: {len(tool_calls)}")
                flush_print(f"   響應長度: {len(response.content)}字符")
                
                if len(tool_calls) > 0:
                    flush_print(f"   ✅ 策略{i}成功: 觸發了工具調用")
                    for j, tool_call in enumerate(tool_calls):
                        tool_name = tool_call.get('name', 'unknown')
                        tool_args = tool_call.get('args', {})
                        flush_print(f"      工具{j+1}: {tool_name}({tool_args})")
                    tool_call_success = True
                    break
                else:
                    flush_print(f"   ❌ 策略{i}失败: 未觸發工具調用")
                    flush_print(f"   直接響應: {response.content[:100]}...")
                    
            except Exception as e:
                flush_print(f"   ❌ 策略{i}異常: {e}")
        
        # 測試6: 不同模型測試
        flush_print("\n🔧 測試6: 不同模型測試")
        flush_print("-" * 40)
        
        models = ["qwen-turbo", "qwen-plus-latest"]
        
        for model in models:
            flush_print(f"\n   測試模型: {model}")
            
            try:
                test_llm = ChatDashScopeOpenAI(
                    model=model,
                    temperature=0.0,  # 降低溫度
                    max_tokens=100
                )
                
                test_llm_with_tools = test_llm.bind_tools([get_stock_info])
                
                response = test_llm_with_tools.invoke([
                    HumanMessage(content="請調用get_stock_info工具查詢TSLA")
                ])
                
                tool_calls = getattr(response, 'tool_calls', [])
                flush_print(f"   {model}: 工具調用數量 = {len(tool_calls)}")
                
                if len(tool_calls) > 0:
                    flush_print(f"   ✅ {model}: 支持工具調用")
                else:
                    flush_print(f"   ❌ {model}: 不支持工具調用")
                    
            except Exception as e:
                flush_print(f"   ❌ {model}: 測試異常 - {str(e)[:100]}")
        
        # 总結
        flush_print("\n📋 測試总結")
        flush_print("=" * 50)
        
        if tool_call_success:
            flush_print("🎉 阿里百炼工具調用測試成功！")
            flush_print("   ✅ 模型能夠理解並執行工具調用")
            flush_print("   ✅ OpenAI兼容適配器工作正常")
        else:
            flush_print("⚠️ 阿里百炼工具調用存在問題")
            flush_print("   ❌ 模型不主動調用工具")
            flush_print("   💡 建议: 使用手動工具調用作為备用方案")
        
        flush_print("\n🔍 問題分析:")
        flush_print("   1. 適配器創建: ✅ 正常")
        flush_print("   2. 工具绑定: ✅ 正常")
        flush_print("   3. API調用: ✅ 正常")
        flush_print(f"   4. 工具調用: {'✅ 正常' if tool_call_success else '❌ 異常'}")
        
        if not tool_call_success:
            flush_print("\n💡 解決方案:")
            flush_print("   1. 使用更明確的工具調用指令")
            flush_print("   2. 調整模型參數(temperature=0.0)")
            flush_print("   3. 使用手動工具調用模式")
            flush_print("   4. 考慮使用DeepSeek作為替代")
        
        return tool_call_success
        
    except Exception as e:
        flush_print(f"\n💥 測試異常: {e}")
        flush_print("異常詳情:")
        traceback.print_exc()
        return False
    
    finally:
        flush_print("\n" + "="*60)
        flush_print("測試完成！")
        # 不使用input()避免掛起

if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        flush_print(f"退出碼: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        flush_print(f"主函數異常: {e}")
        sys.exit(1)
