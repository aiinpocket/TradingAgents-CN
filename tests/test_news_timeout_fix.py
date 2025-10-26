#!/usr/bin/env python3
"""
測試新聞獲取超時修複

這個測試程序驗證新聞獲取超時修複的有效性，特別是在一個新聞源失败時能否正確轮詢到下一個新聞源。
"""

import sys
import os
import time
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入需要測試的模塊
from tradingagents.dataflows.realtime_news_utils import get_realtime_stock_news
from tradingagents.dataflows.googlenews_utils import getNewsData, make_request
from tradingagents.dataflows.akshare_utils import get_stock_news_em


class TestNewsTimeoutFix(unittest.TestCase):
    """測試新聞獲取超時修複"""

    def setUp(self):
        """測試前的準备工作"""
        self.ticker = "600036.SH"  # 招商銀行
        self.curr_date = datetime.now().strftime("%Y-%m-%d")

    def test_make_request_timeout(self):
        """測試make_request函數的超時處理"""
        # 模擬請求超時
        with patch('requests.get') as mock_get:
            # 設置mock抛出超時異常
            import requests
            from tenacity import RetryError
            mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
            
            # 測試make_request函數
            with self.assertRaises(RetryError):
                make_request("https://www.google.com", {})
                
            # 驗證重試機制
            self.assertEqual(mock_get.call_count, 5)  # 應该嘗試5次

    def test_news_source_fallback(self):
        """測試新聞源轮詢機制"""
        # 模擬實時新聞聚合器失败
        with patch('tradingagents.dataflows.realtime_news_utils.RealtimeNewsAggregator.get_realtime_stock_news') as mock_aggregator:
            mock_aggregator.side_effect = Exception("模擬實時新聞聚合器失败")
            
            # 模擬Google新聞獲取失败
            with patch('tradingagents.dataflows.interface.get_google_news') as mock_google_news:
                mock_google_news.side_effect = Exception("模擬Google新聞獲取失败")
                
                # 模擬东方財富新聞獲取成功
                with patch('tradingagents.dataflows.akshare_utils.get_stock_news_em') as mock_em_news:
                    # 創建一個模擬的DataFrame作為返回值
                    mock_df = pd.DataFrame({
                        '標題': ['測試新聞1', '測試新聞2'],
                        '時間': ['2023-01-01 12:00:00', '2023-01-01 13:00:00'],
                        '內容': ['測試內容1', '測試內容2'],
                        '鏈接': ['http://example.com/1', 'http://example.com/2']
                    })
                    mock_em_news.return_value = mock_df
                    
                    # 調用測試函數
                    result = get_realtime_stock_news(self.ticker, self.curr_date)
                    
                    # 驗證結果
                    self.assertIn("东方財富新聞報告", result)
                    self.assertIn("測試新聞1", result)
                    self.assertIn("測試新聞2", result)
                    
                    # 驗證調用顺序
                    mock_aggregator.assert_called_once()
                    mock_google_news.assert_called_once()
                    mock_em_news.assert_called_once()

    def test_all_news_sources_fail(self):
        """測試所有新聞源都失败的情况"""
        # 模擬所有新聞源都失败
        with patch('tradingagents.dataflows.realtime_news_utils.RealtimeNewsAggregator.get_realtime_stock_news') as mock_aggregator:
            mock_aggregator.side_effect = Exception("模擬實時新聞聚合器失败")
            
            with patch('tradingagents.dataflows.interface.get_google_news') as mock_google_news:
                mock_google_news.side_effect = Exception("模擬Google新聞獲取失败")
                
                with patch('tradingagents.dataflows.akshare_utils.get_stock_news_em') as mock_em_news:
                    mock_em_news.side_effect = Exception("模擬东方財富新聞獲取失败")
                    
                    # 調用測試函數
                    result = get_realtime_stock_news(self.ticker, self.curr_date)
                    
                    # 驗證結果
                    self.assertIn("實時新聞獲取失败", result)
                    self.assertIn("所有可用的新聞源都未能獲取到相關新聞", result)
                    
                    # 驗證調用顺序
                    mock_aggregator.assert_called_once()
                    mock_google_news.assert_called_once()
                    mock_em_news.assert_called_once()


if __name__ == "__main__":
    unittest.main()