#!/usr/bin/env python3
"""
完整基本面分析流程測試
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_full_fundamentals_flow():
    """測試完整的基本面分析流程"""
    print("\n🔍 完整基本面分析流程測試")
    print("=" * 80)
    
    # 測試分眾傳媒 002027
    test_ticker = "002027"
    print(f"📊 測試股票代碼: {test_ticker} (分眾傳媒)")
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        print(f"\n🔧 步骤1: 初始化LLM和工具包...")
        
        # 導入必要的模塊
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.llm_adapters import get_llm

        # 獲取LLM實例
        llm = get_llm()
        print(f"✅ LLM初始化完成: {type(llm).__name__}")

        # 創建工具包
        toolkit = Toolkit()
        print(f"✅ 工具包初始化完成")
        
        print(f"\n🔧 步骤2: 創建基本面分析師...")
        
        # 創建基本面分析師
        fundamentals_analyst = create_fundamentals_analyst(llm, toolkit)
        print(f"✅ 基本面分析師創建完成")
        
        print(f"\n🔧 步骤3: 準备分析狀態...")
        
        # 創建分析狀態
        state = {
            "company_of_interest": test_ticker,
            "trade_date": "2025-07-15",
            "messages": []
        }
        
        print(f"✅ 分析狀態準备完成")
        print(f"   - 股票代碼: {state['company_of_interest']}")
        print(f"   - 交易日期: {state['trade_date']}")
        print(f"   - 消息數量: {len(state['messages'])}")
        
        print(f"\n🔧 步骤4: 執行基本面分析...")
        
        # 執行基本面分析
        result = fundamentals_analyst(state)
        
        print(f"\n✅ 基本面分析執行完成")
        print(f"📊 返回結果類型: {type(result)}")
        
        # 檢查返回結果
        if isinstance(result, dict):
            if 'fundamentals_report' in result:
                report = result['fundamentals_report']
                print(f"📄 基本面報告長度: {len(report) if report else 0}")
                
                # 檢查報告中的股票代碼
                if report:
                    print(f"\n🔍 最终檢查報告中的股票代碼...")
                    if "002027" in report:
                        print("✅ 報告中包含正確的股票代碼 002027")
                        count_002027 = report.count("002027")
                        print(f"   002027 出現次數: {count_002027}")
                    else:
                        print("❌ 報告中不包含正確的股票代碼 002027")
                        
                    if "002021" in report:
                        print("⚠️ 報告中包含錯誤的股票代碼 002021")
                        count_002021 = report.count("002021")
                        print(f"   002021 出現次數: {count_002021}")
                        
                        # 找出錯誤代碼的位置
                        import re
                        positions = [m.start() for m in re.finditer("002021", report)]
                        print(f"   002021 出現位置: {positions}")
                        
                        # 顯示錯誤代碼周围的文本
                        for pos in positions[:3]:  # 只顯示前3個位置
                            start = max(0, pos - 100)
                            end = min(len(report), pos + 100)
                            context = report[start:end]
                            print(f"   位置 {pos} 周围文本: ...{context}...")
                    else:
                        print("✅ 報告中不包含錯誤的股票代碼 002021")
                        
                    # 顯示報告的前1000字符
                    print(f"\n📄 報告前1000字符:")
                    print("-" * 80)
                    print(report[:1000])
                    print("-" * 80)
            else:
                print("❌ 返回結果中没有 fundamentals_report")
                print(f"   返回結果键: {list(result.keys())}")
        else:
            print(f"❌ 返回結果類型不正確: {type(result)}")
            if hasattr(result, 'content'):
                print(f"   內容: {result.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始完整基本面分析流程測試")
    
    # 執行完整流程測試
    success = test_full_fundamentals_flow()
    
    if success:
        print("\n✅ 測試完成")
    else:
        print("\n❌ 測試失败")
