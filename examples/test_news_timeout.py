#!/usr/bin/env python3
"""
手動測試新聞獲取超時修複

這個腳本用於手動驗證新聞獲取功能，特別是在Google新聞獲取超時的情况下的轮詢機制。
"""

import sys
import os
import time
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入需要測試的模塊
from tradingagents.dataflows.realtime_news_utils import get_realtime_stock_news
from tradingagents.utils.logging_manager import get_logger

# 獲取日誌記錄器
logger = get_logger('test')

def test_news_for_stock(ticker):
    """
    測試獲取指定股票的新聞
    
    Args:
        ticker: 股票代碼
    """
    logger.info(f"開始獲取{ticker}的新聞...")
    curr_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # 獲取新聞
        start_time = time.time()
        news = get_realtime_stock_news(ticker, curr_date)
        end_time = time.time()
        
        # 打印結果
        logger.info(f"獲取{ticker}的新聞成功，耗時{end_time - start_time:.2f}秒")
        print("\n" + "=" * 80)
        print(f"股票: {ticker}")
        print("=" * 80)
        print(news)
        print("=" * 80 + "\n")
        
        return True
    except Exception as e:
        logger.error(f"獲取{ticker}的新聞失败: {e}")
        return False

def main():
    """
    主函數
    """
    # 測試A股
    a_shares = ["600036.SH", "000001.SZ", "601318.SH"]
    
    # 測試港股
    hk_shares = ["00700.HK", "09988.HK"]
    
    # 測試美股
    us_shares = ["AAPL.US", "MSFT.US", "GOOGL.US"]
    
    # 所有股票
    all_stocks = a_shares + hk_shares + us_shares
    
    # 測試結果統計
    success_count = 0
    fail_count = 0
    
    # 逐個測試
    for ticker in all_stocks:
        if test_news_for_stock(ticker):
            success_count += 1
        else:
            fail_count += 1
    
    # 打印統計結果
    print(f"\n測試完成: 成功 {success_count} 個, 失败 {fail_count} 個")

if __name__ == "__main__":
    main()