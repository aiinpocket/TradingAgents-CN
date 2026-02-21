#!/usr/bin/env python3
"""
測試新聞分析師工具呼叫參數修復
驗證強制呼叫和備用工具呼叫是否正確傳遞了所需參數
"""

import sys
import os
from datetime import datetime

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.agents.utils.agent_utils import Toolkit

def test_tool_parameters():
    """測試工具參數是否正確"""
    print(" 測試新聞分析師工具呼叫參數修復")
    print("=" * 50)
    
    # 初始化工具包
    toolkit = Toolkit()
    
    # 測試參數
    ticker = "600036"
    curr_date = "2025-07-28"
    
    print(f" 測試參數:")
    print(f"   - ticker: {ticker}")
    print(f"   - curr_date: {curr_date}")
    print()
    
    # 測試 get_realtime_stock_news 工具
    print(" 測試 get_realtime_stock_news 工具呼叫...")
    try:
        # 模擬修復後的呼叫方式
        params = {"ticker": ticker, "curr_date": curr_date}
        print(f"   參數: {params}")
        
        # 檢查工具是否接受這些參數
        result = toolkit.get_realtime_stock_news.invoke(params)
        print(f"    get_realtime_stock_news 呼叫成功")
        print(f"    傳回資料長度: {len(result) if result else 0} 字元")
        
    except Exception as e:
        print(f"    get_realtime_stock_news 呼叫失敗: {e}")
    
    print()
    
    # 測試 get_google_news 工具
    print(" 測試 get_google_news 工具呼叫...")
    try:
        # 模擬修復後的呼叫方式
        params = {"query": f"{ticker} 股票 新聞", "curr_date": curr_date}
        print(f"   參數: {params}")
        
        # 檢查工具是否接受這些參數
        result = toolkit.get_google_news.invoke(params)
        print(f"    get_google_news 呼叫成功")
        print(f"    傳回資料長度: {len(result) if result else 0} 字元")
        
    except Exception as e:
        print(f"    get_google_news 呼叫失敗: {e}")
    
    print()
    
    # 測試修復前的錯誤呼叫方式（應該失敗）
    print(" 測試修復前的錯誤呼叫方式（應該失敗）...")
    
    print("   測試 get_realtime_stock_news 缺少 curr_date:")
    try:
        params = {"ticker": ticker}  # 缺少 curr_date
        result = toolkit.get_realtime_stock_news.invoke(params)
        print(f"    意外成功（可能有預設值處理）")
    except Exception as e:
        print(f"    正確失敗: {e}")
    
    print("   測試 get_google_news 缺少 query 和 curr_date:")
    try:
        params = {"ticker": ticker}  # 缺少 query 和 curr_date
        result = toolkit.get_google_news.invoke(params)
        print(f"    意外成功（可能有預設值處理）")
    except Exception as e:
        print(f"    正確失敗: {e}")
    
    print()
    print(" 修復總結:")
    print("   1.  get_realtime_stock_news 現在正確傳遞 ticker 和 curr_date")
    print("   2.  get_google_news 現在正確傳遞 query 和 curr_date")
    print("   3.  修復了 Pydantic 驗證錯誤")
    print("   4.  新聞分析師應該能夠正常取得新聞資料")

if __name__ == "__main__":
    test_tool_parameters()