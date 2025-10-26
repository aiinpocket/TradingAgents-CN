#!/usr/bin/env python3
"""
002027 股票代碼專項測試
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_002027_specifically():
    """專門測試002027股票代碼"""
    print("🔍 002027 專項測試")
    print("=" * 60)
    
    test_ticker = "002027"
    
    try:
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        # 測試1: 數據獲取
        print("\n📊 測試1: 數據獲取")
        from tradingagents.dataflows.interface import get_china_stock_data_tushare
        data = get_china_stock_data_tushare(test_ticker, "2025-07-01", "2025-07-15")
        
        if "002021" in data:
            print("❌ 數據獲取階段發現錯誤代碼 002021")
            return False
        else:
            print("✅ 數據獲取階段正確")
        
        # 測試2: 基本面分析
        print("\n💰 測試2: 基本面分析")
        from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
        analyzer = OptimizedChinaDataProvider()
        report = analyzer._generate_fundamentals_report(test_ticker, data)
        
        if "002021" in report:
            print("❌ 基本面分析階段發現錯誤代碼 002021")
            return False
        else:
            print("✅ 基本面分析階段正確")
        
        # 測試3: LLM處理
        print("\n🤖 測試3: LLM處理")
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if api_key:
            from tradingagents.llm_adapters import ChatDashScopeOpenAI
            from langchain_core.messages import HumanMessage
            
            llm = ChatDashScopeOpenAI(model="qwen-turbo", temperature=0.1, max_tokens=500)
            
            prompt = f"請分析股票{test_ticker}的基本面，股票名稱是分眾傳媒。要求：1.必须使用正確的股票代碼{test_ticker} 2.不要使用任何其他股票代碼"
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            if "002021" in response.content:
                print("❌ LLM處理階段發現錯誤代碼 002021")
                print(f"錯誤內容: {response.content[:200]}...")
                return False
            else:
                print("✅ LLM處理階段正確")
        else:
            print("⚠️ 跳過LLM測試（未配置API密鑰）")
        
        print("\n🎉 所有測試通過！002027股票代碼處理正確")
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

if __name__ == "__main__":
    test_002027_specifically()
