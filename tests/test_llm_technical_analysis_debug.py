#!/usr/bin/env python3
"""
LLM技術面分析調試測試
專門診斷阿里百炼vs DeepSeek在技術面分析中的差異
"""

import os
import sys
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_dashscope_technical_analysis():
    """測試阿里百炼的技術面分析"""
    print("\n🔧 測試阿里百炼技術面分析")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        from langchain.schema import HumanMessage
        
        # 創建阿里百炼模型
        llm = ChatDashScope(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=2000
        )
        
        print("✅ 阿里百炼模型創建成功")
        
        # 測試簡單對話
        print("🔄 測試簡單對話...")
        simple_messages = [HumanMessage(content="請簡單介紹股票技術分析的概念，控制在100字以內。")]
        simple_response = llm.invoke(simple_messages)
        print(f"📊 簡單對話響應長度: {len(simple_response.content)}字符")
        print(f"📋 簡單對話內容: {simple_response.content[:200]}...")
        
        # 測試複雜技術分析prompt
        print("\n🔄 測試複雜技術分析prompt...")
        complex_prompt = """現在請基於以下股票數據，生成詳細的技術分析報告。

要求：
1. 報告必须基於提供的數據進行分析
2. 包含具體的技術指標數值和專業分析
3. 提供明確的投資建议和風險提示
4. 報告長度不少於800字
5. 使用中文撰寫

請分析股票600036的技術面情况，包括：
- 價格趋势分析
- 技術指標解讀
- 支撑阻力位分析
- 成交量分析
- 投資建议

股票數據：
股票代碼: 600036
股票名稱: 招商銀行
當前價格: ¥47.13
涨跌幅: -1.03%
成交量: 61.5万手
"""
        
        complex_messages = [HumanMessage(content=complex_prompt)]
        complex_response = llm.invoke(complex_messages)
        print(f"📊 複雜分析響應長度: {len(complex_response.content)}字符")
        print(f"📋 複雜分析內容: {complex_response.content[:300]}...")
        
        if len(complex_response.content) < 100:
            print("❌ 阿里百炼複雜分析響應過短")
            return False
        else:
            print("✅ 阿里百炼複雜分析響應正常")
            return True
        
    except Exception as e:
        print(f"❌ 阿里百炼測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deepseek_technical_analysis():
    """測試DeepSeek的技術面分析"""
    print("\n🔧 測試DeepSeek技術面分析")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        from langchain.schema import HumanMessage
        
        # 創建DeepSeek模型
        llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=2000
        )
        
        print("✅ DeepSeek模型創建成功")
        
        # 測試簡單對話
        print("🔄 測試簡單對話...")
        simple_messages = [HumanMessage(content="請簡單介紹股票技術分析的概念，控制在100字以內。")]
        simple_response = llm.invoke(simple_messages)
        print(f"📊 簡單對話響應長度: {len(simple_response.content)}字符")
        print(f"📋 簡單對話內容: {simple_response.content[:200]}...")
        
        # 測試複雜技術分析prompt
        print("\n🔄 測試複雜技術分析prompt...")
        complex_prompt = """現在請基於以下股票數據，生成詳細的技術分析報告。

要求：
1. 報告必须基於提供的數據進行分析
2. 包含具體的技術指標數值和專業分析
3. 提供明確的投資建议和風險提示
4. 報告長度不少於800字
5. 使用中文撰寫

請分析股票600036的技術面情况，包括：
- 價格趋势分析
- 技術指標解讀
- 支撑阻力位分析
- 成交量分析
- 投資建议

股票數據：
股票代碼: 600036
股票名稱: 招商銀行
當前價格: ¥47.13
涨跌幅: -1.03%
成交量: 61.5万手
"""
        
        complex_messages = [HumanMessage(content=complex_prompt)]
        complex_response = llm.invoke(complex_messages)
        print(f"📊 複雜分析響應長度: {len(complex_response.content)}字符")
        print(f"📋 複雜分析內容: {complex_response.content[:300]}...")
        
        if len(complex_response.content) < 100:
            print("❌ DeepSeek複雜分析響應過短")
            return False
        else:
            print("✅ DeepSeek複雜分析響應正常")
            return True
        
    except Exception as e:
        print(f"❌ DeepSeek測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_sequence_handling():
    """測試複雜消息序列處理"""
    print("\n🔧 測試複雜消息序列處理")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        from langchain.schema import HumanMessage, AIMessage, ToolMessage
        
        # 創建阿里百炼模型
        llm = ChatDashScope(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=2000
        )
        
        print("✅ 阿里百炼模型創建成功")
        
        # 模擬複雜的消息序列（類似技術面分析中的情况）
        messages = [
            HumanMessage(content="請分析股票600036的技術面"),
            AIMessage(content="我需要獲取股票數據來進行分析", tool_calls=[
                {
                    "name": "get_china_stock_data",
                    "args": {"stock_code": "600036", "start_date": "2025-06-10", "end_date": "2025-07-10"},
                    "id": "call_1"
                }
            ]),
            ToolMessage(content="股票代碼: 600036\n股票名稱: 招商銀行\n當前價格: ¥47.13\n涨跌幅: -1.03%\n成交量: 61.5万手", tool_call_id="call_1"),
            HumanMessage(content="""現在請基於上述工具獲取的數據，生成詳細的技術分析報告。

要求：
1. 報告必须基於工具返回的真實數據進行分析
2. 包含具體的技術指標數值和專業分析
3. 提供明確的投資建议和風險提示
4. 報告長度不少於800字
5. 使用中文撰寫

請分析股票600036的技術面情况，包括：
- 價格趋势分析
- 技術指標解讀
- 支撑阻力位分析
- 成交量分析
- 投資建议""")
        ]
        
        print("🔄 測試複雜消息序列...")
        response = llm.invoke(messages)
        print(f"📊 複雜消息序列響應長度: {len(response.content)}字符")
        print(f"📋 複雜消息序列內容: {response.content[:300]}...")
        
        if len(response.content) < 100:
            print("❌ 阿里百炼複雜消息序列響應過短")
            return False
        else:
            print("✅ 阿里百炼複雜消息序列響應正常")
            return True
        
    except Exception as e:
        print(f"❌ 複雜消息序列測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_max_tokens_impact():
    """測試max_tokens參數的影響"""
    print("\n🔧 測試max_tokens參數影響")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        from langchain.schema import HumanMessage
        
        prompt = """請生成一份詳細的股票技術分析報告，要求不少於800字，包含：
1. 價格趋势分析
2. 技術指標解讀
3. 支撑阻力位分析
4. 成交量分析
5. 投資建议

股票：招商銀行(600036)
當前價格: ¥47.13
"""
        
        # 測試不同的max_tokens設置
        token_settings = [500, 1000, 2000, 4000]
        
        for max_tokens in token_settings:
            print(f"\n🔄 測試max_tokens={max_tokens}...")
            
            llm = ChatDashScope(
                model="qwen-plus-latest",
                temperature=0.1,
                max_tokens=max_tokens
            )
            
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            
            print(f"📊 max_tokens={max_tokens}, 響應長度: {len(response.content)}字符")
            
            if len(response.content) < 100:
                print(f"❌ max_tokens={max_tokens}時響應過短")
            else:
                print(f"✅ max_tokens={max_tokens}時響應正常")
        
        return True
        
    except Exception as e:
        print(f"❌ max_tokens測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔍 LLM技術面分析調試測試")
    print("=" * 70)
    print("💡 調試目標:")
    print("   - 診斷阿里百炼技術面分析報告過短問題")
    print("   - 對比DeepSeek和阿里百炼的響應差異")
    print("   - 測試複雜消息序列處理")
    print("   - 分析max_tokens參數影響")
    print("=" * 70)
    
    # 運行所有測試
    tests = [
        ("阿里百炼技術面分析", test_dashscope_technical_analysis),
        ("DeepSeek技術面分析", test_deepseek_technical_analysis),
        ("複雜消息序列處理", test_message_sequence_handling),
        ("max_tokens參數影響", test_max_tokens_impact)
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
    print("\n📋 LLM技術面分析調試总結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    print("\n💡 可能的解決方案:")
    print("   1. 調整阿里百炼的max_tokens參數")
    print("   2. 優化技術面分析的prompt設計")
    print("   3. 簡化複雜消息序列")
    print("   4. 添加模型特定的處理逻辑")
    
    input("按回車键退出...")


if __name__ == "__main__":
    main()
