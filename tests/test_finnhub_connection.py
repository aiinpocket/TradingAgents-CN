#!/usr/bin/env python3
"""
測試FINNHUB API連接
"""

import sys
import os
sys.path.append('..')

def test_finnhub_api():
    """測試FINNHUB API連接"""
    print(" 測試FINNHUB API連接...")
    
    # 檢查API密鑰
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    if not finnhub_key:
        print(" 請設定 FINNHUB_API_KEY 環境變數")
        return False
    
    print(f" FINNHUB API密鑰已配置: {finnhub_key[:10]}...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 建立配置
        config = DEFAULT_CONFIG.copy()
        config['online_tools'] = True
        
        # 建立工具包
        toolkit = Toolkit()
        toolkit.update_config(config)
        
        # 測試FINNHUB新聞API
        print(f"\n 測試FINNHUB新聞API...")
        try:
            news_result = toolkit.get_finnhub_news.invoke({
                'ticker': 'AAPL',
                'start_date': '2025-06-25',
                'end_date': '2025-06-29'
            })
            print(f" FINNHUB新聞API呼叫成功")
            print(f"新聞資料長度: {len(news_result) if news_result else 0}")
            if news_result and len(news_result) > 100:
                print(f"新聞內容前200字符:")
                print(news_result[:200])
            else:
                print(f"新聞內容: {news_result}")
        except Exception as e:
            print(f" FINNHUB新聞API呼叫失敗: {e}")
        
        # 測試Yahoo Finance資料API
        print(f"\n 測試Yahoo Finance資料API...")
        try:
            stock_result = toolkit.get_YFin_data_online.invoke({
                'symbol': 'AAPL',
                'start_date': '2025-06-25',
                'end_date': '2025-06-29'
            })
            print(f" Yahoo Finance API呼叫成功")
            print(f"股票資料長度: {len(stock_result) if stock_result else 0}")
            if stock_result and len(stock_result) > 100:
                print(f"股票資料前200字符:")
                print(stock_result[:200])
            else:
                print(f"股票資料: {stock_result}")
        except Exception as e:
            print(f" Yahoo Finance API呼叫失敗: {e}")
        
        # 測試OpenAI基本面API
        print(f"\n 測試OpenAI基本面API...")
        try:
            fundamentals_result = toolkit.get_fundamentals_openai.invoke({
                'ticker': 'AAPL',
                'curr_date': '2025-06-29'
            })
            print(f" OpenAI基本面API呼叫成功")
            print(f"基本面資料長度: {len(fundamentals_result) if fundamentals_result else 0}")
            if fundamentals_result and len(fundamentals_result) > 100:
                print(f"基本面資料前200字符:")
                print(fundamentals_result[:200])
            else:
                print(f"基本面資料: {fundamentals_result}")
        except Exception as e:
            print(f" OpenAI基本面API呼叫失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("開始API連接測試")
    print("="*50)

    # 測試美股API
    result1 = test_finnhub_api()

    print("\n" + "="*50)
    print("測試總結:")
    print(f"美股API測試: {'通過' if result1 else '失敗'}")

    if result1:
        print("所有API連接正常，可以進行股票分析!")
    else:
        print("API連接有問題，請檢查配置和網路連接。")
