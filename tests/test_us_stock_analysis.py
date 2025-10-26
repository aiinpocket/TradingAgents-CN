#!/usr/bin/env python3
"""
測試美股分析功能
"""

import sys
import os
sys.path.append('..')

def test_us_stock_market_analysis():
    """測試美股市場分析"""
    print("🔍 測試美股市場分析...")
    
    try:
        from tradingagents.agents.analysts.market_analyst import create_market_analyst_react
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        from langchain_community.llms import Tongyi

        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config['online_tools'] = True

        # 創建工具包
        toolkit = Toolkit()
        toolkit.update_config(config)

        # 檢查工具包是否有正確的方法
        print(f"✅ 工具包方法檢查:")
        print(f"  - get_YFin_data_online: {hasattr(toolkit, 'get_YFin_data_online')}")
        print(f"  - get_china_stock_data: {hasattr(toolkit, 'get_china_stock_data')}")
        
        # 創建Tongyi LLM
        llm = Tongyi()
        llm.model_name = 'qwen-turbo'

        # 創建ReAct市場分析師
        analyst = create_market_analyst_react(llm, toolkit)

        # 測試美股
        test_state = {
            'trade_date': '2025-06-29',
            'company_of_interest': 'AAPL',
            'messages': [('human', '分析AAPL')],
            'market_report': ''
        }

        print(f"\n🔄 開始美股市場分析...")
        result = analyst(test_state)
        
        print(f"✅ 美股市場分析完成")
        print(f"市場報告長度: {len(result['market_report'])}")
        
        if len(result['market_report']) > 100:
            print(f"✅ 報告內容正常")
            print(f"報告前300字符:")
            print(result['market_report'][:300])
        else:
            print(f"❌ 報告內容異常:")
            print(result['market_report'])
            
        return result
        
    except Exception as e:
        print(f"❌ 美股市場分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_us_stock_fundamentals_analysis():
    """測試美股基本面分析"""
    print("\n" + "="*50)
    print("🔍 測試美股基本面分析...")
    
    try:
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst_react
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        from langchain_community.llms import Tongyi

        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config['online_tools'] = True

        # 創建工具包
        toolkit = Toolkit()
        toolkit.update_config(config)

        # 檢查工具包是否有正確的方法
        print(f"✅ 工具包方法檢查:")
        print(f"  - get_YFin_data_online: {hasattr(toolkit, 'get_YFin_data_online')}")
        print(f"  - get_fundamentals_openai: {hasattr(toolkit, 'get_fundamentals_openai')}")
        
        # 創建Tongyi LLM
        llm = Tongyi()
        llm.model_name = 'qwen-turbo'

        # 創建ReAct基本面分析師
        analyst = create_fundamentals_analyst_react(llm, toolkit)

        # 測試美股
        test_state = {
            'trade_date': '2025-06-29',
            'company_of_interest': 'AAPL',
            'messages': [('human', '分析AAPL')],
            'fundamentals_report': ''
        }

        print(f"\n🔄 開始美股基本面分析...")
        result = analyst(test_state)
        
        print(f"✅ 美股基本面分析完成")
        print(f"基本面報告長度: {len(result['fundamentals_report'])}")
        
        if len(result['fundamentals_report']) > 100:
            print(f"✅ 報告內容正常")
            print(f"報告前300字符:")
            print(result['fundamentals_report'][:300])
        else:
            print(f"❌ 報告內容異常:")
            print(result['fundamentals_report'])
            
        return result
        
    except Exception as e:
        print(f"❌ 美股基本面分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 開始美股分析測試")
    print("="*50)
    
    # 檢查API密鑰
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 請設置 DASHSCOPE_API_KEY 環境變量")
        sys.exit(1)
    
    print(f"✅ API密鑰已配置: {api_key[:10]}...")
    
    # 測試市場分析
    result1 = test_us_stock_market_analysis()
    
    # 測試基本面分析
    result2 = test_us_stock_fundamentals_analysis()
    
    print("\n" + "="*50)
    print("🎯 測試总結:")
    print(f"市場分析測試: {'✅ 成功' if result1 else '❌ 失败'}")
    print(f"基本面分析測試: {'✅ 成功' if result2 else '❌ 失败'}")
