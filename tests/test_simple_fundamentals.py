#!/usr/bin/env python3
"""
簡單基本面分析測試
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_simple_fundamentals():
    """測試簡單的基本面分析流程"""
    print("\n🔍 簡單基本面分析測試")
    print("=" * 80)
    
    # 測試分眾傳媒 002027
    test_ticker = "002027"
    print(f"📊 測試股票代碼: {test_ticker} (分眾傳媒)")
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        print(f"\n🔧 步骤1: 創建LLM實例...")
        
        # 檢查API密鑰
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("⚠️ 未找到DASHSCOPE_API_KEY，跳過LLM測試")
            return True
        
        # 創建LLM實例
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        llm = ChatDashScopeOpenAI(
            model="qwen-turbo",
            temperature=0.1,
            max_tokens=1000
        )
        print(f"✅ LLM實例創建完成: {type(llm).__name__}")
        
        print(f"\n🔧 步骤2: 創建工具包...")
        
        # 創建工具包
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit()
        toolkit.update_config(config)
        print(f"✅ 工具包創建完成")
        
        print(f"\n🔧 步骤3: 測試統一基本面工具...")
        
        # 直接測試統一基本面工具
        result = toolkit.get_stock_fundamentals_unified.invoke({
            'ticker': test_ticker,
            'start_date': '2025-06-01',
            'end_date': '2025-07-15',
            'curr_date': '2025-07-15'
        })
        
        print(f"✅ 統一基本面工具調用完成")
        print(f"📊 返回結果長度: {len(result) if result else 0}")
        
        # 檢查結果中的股票代碼
        if result:
            print(f"\n🔍 檢查工具返回結果中的股票代碼...")
            if "002027" in result:
                print("✅ 工具返回結果中包含正確的股票代碼 002027")
                count_002027 = result.count("002027")
                print(f"   002027 出現次數: {count_002027}")
            else:
                print("❌ 工具返回結果中不包含正確的股票代碼 002027")
                
            if "002021" in result:
                print("⚠️ 工具返回結果中包含錯誤的股票代碼 002021")
                count_002021 = result.count("002021")
                print(f"   002021 出現次數: {count_002021}")
            else:
                print("✅ 工具返回結果中不包含錯誤的股票代碼 002021")
        
        print(f"\n🔧 步骤4: 測試LLM處理...")
        
        # 創建一個簡單的提示詞，包含工具返回的數據
        prompt = f"""請基於以下真實數據，對股票{test_ticker}進行基本面分析：

{result}

要求：
1. 分析要詳細且專業
2. 必须使用中文
3. 股票代碼必须準確
4. 不要編造任何信息
"""
        
        print(f"🔍 [股票代碼追蹤] 發送給LLM的提示詞中的股票代碼: {test_ticker}")
        
        # 調用LLM
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        
        print(f"✅ LLM調用完成")
        print(f"📊 LLM響應長度: {len(response.content) if response.content else 0}")
        
        # 檢查LLM響應中的股票代碼
        if response.content:
            print(f"\n🔍 檢查LLM響應中的股票代碼...")
            if "002027" in response.content:
                print("✅ LLM響應中包含正確的股票代碼 002027")
                count_002027 = response.content.count("002027")
                print(f"   002027 出現次數: {count_002027}")
            else:
                print("❌ LLM響應中不包含正確的股票代碼 002027")
                
            if "002021" in response.content:
                print("⚠️ LLM響應中包含錯誤的股票代碼 002021")
                count_002021 = response.content.count("002021")
                print(f"   002021 出現次數: {count_002021}")
                
                # 找出錯誤代碼的位置
                import re
                positions = [m.start() for m in re.finditer("002021", response.content)]
                print(f"   002021 出現位置: {positions}")
                
                # 顯示錯誤代碼周围的文本
                for pos in positions[:3]:  # 只顯示前3個位置
                    start = max(0, pos - 100)
                    end = min(len(response.content), pos + 100)
                    context = response.content[start:end]
                    print(f"   位置 {pos} 周围文本: ...{context}...")
            else:
                print("✅ LLM響應中不包含錯誤的股票代碼 002021")
                
            # 顯示LLM響應的前1000字符
            print(f"\n📄 LLM響應前1000字符:")
            print("-" * 80)
            print(response.content[:1000])
            print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始簡單基本面分析測試")
    
    # 執行測試
    success = test_simple_fundamentals()
    
    if success:
        print("\n✅ 測試完成")
    else:
        print("\n❌ 測試失败")
