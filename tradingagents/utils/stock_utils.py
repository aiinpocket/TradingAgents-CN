"""
股票工具函數
提供股票代碼識別、分類和處理功能
"""

import re
from typing import Dict, Tuple, Optional
from enum import Enum

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


class StockMarket(Enum):
    """股票市場枚舉"""
    CHINA_A = "china_a"      # 中國A股
    HONG_KONG = "hong_kong"  # 港股
    US = "us"                # 美股
    UNKNOWN = "unknown"      # 未知


class StockUtils:
    """股票工具類"""
    
    @staticmethod
    def identify_stock_market(ticker: str) -> StockMarket:
        """
        識別股票代碼所屬市場
        
        Args:
            ticker: 股票代碼
            
        Returns:
            StockMarket: 股票市場類型
        """
        if not ticker:
            return StockMarket.UNKNOWN
            
        ticker = str(ticker).strip().upper()
        
        # 中國A股：6位數字
        if re.match(r'^\d{6}$', ticker):
            return StockMarket.CHINA_A

        # 港股：4-5位數字.HK（支持0700.HK和09988.HK格式）
        if re.match(r'^\d{4,5}\.HK$', ticker):
            return StockMarket.HONG_KONG

        # 美股：1-5位字母
        if re.match(r'^[A-Z]{1,5}$', ticker):
            return StockMarket.US
            
        return StockMarket.UNKNOWN
    
    @staticmethod
    def is_china_stock(ticker: str) -> bool:
        """
        判斷是否為中國A股
        
        Args:
            ticker: 股票代碼
            
        Returns:
            bool: 是否為中國A股
        """
        return StockUtils.identify_stock_market(ticker) == StockMarket.CHINA_A
    
    @staticmethod
    def is_hk_stock(ticker: str) -> bool:
        """
        判斷是否為港股
        
        Args:
            ticker: 股票代碼
            
        Returns:
            bool: 是否為港股
        """
        return StockUtils.identify_stock_market(ticker) == StockMarket.HONG_KONG
    
    @staticmethod
    def is_us_stock(ticker: str) -> bool:
        """
        判斷是否為美股
        
        Args:
            ticker: 股票代碼
            
        Returns:
            bool: 是否為美股
        """
        return StockUtils.identify_stock_market(ticker) == StockMarket.US
    
    @staticmethod
    def get_currency_info(ticker: str) -> Tuple[str, str]:
        """
        根據股票代碼獲取貨幣信息

        Args:
            ticker: 股票代碼

        Returns:
            Tuple[str, str]: (貨幣名稱, 貨幣符號)
        """
        market = StockUtils.identify_stock_market(ticker)
        
        if market == StockMarket.CHINA_A:
            return "人民幣", "¥"
        elif market == StockMarket.HONG_KONG:
            return "港幣", "HK$"
        elif market == StockMarket.US:
            return "美元", "$"
        else:
            return "未知", "?"
    
    @staticmethod
    def get_data_source(ticker: str) -> str:
        """
        根據股票代碼獲取推薦的數據源
        
        Args:
            ticker: 股票代碼
            
        Returns:
            str: 數據源名稱
        """
        market = StockUtils.identify_stock_market(ticker)
        
        if market == StockMarket.CHINA_A:
            return "china_unified"  # 使用統一的中國股票數據源
        elif market == StockMarket.HONG_KONG:
            return "yahoo_finance"  # 港股使用Yahoo Finance
        elif market == StockMarket.US:
            return "yahoo_finance"  # 美股使用Yahoo Finance
        else:
            return "unknown"
    
    @staticmethod
    def normalize_hk_ticker(ticker: str) -> str:
        """
        標準化港股代碼格式
        
        Args:
            ticker: 原始港股代碼
            
        Returns:
            str: 標準化後的港股代碼
        """
        if not ticker:
            return ticker
            
        ticker = str(ticker).strip().upper()
        
        # 如果是純4-5位數字，添加.HK後缀
        if re.match(r'^\d{4,5}$', ticker):
            return f"{ticker}.HK"

        # 如果已經是正確格式，直接返回
        if re.match(r'^\d{4,5}\.HK$', ticker):
            return ticker
            
        return ticker
    
    @staticmethod
    def get_market_info(ticker: str) -> Dict:
        """
        獲取股票市場的詳細信息
        
        Args:
            ticker: 股票代碼
            
        Returns:
            Dict: 市場信息字典
        """
        market = StockUtils.identify_stock_market(ticker)
        currency_name, currency_symbol = StockUtils.get_currency_info(ticker)
        data_source = StockUtils.get_data_source(ticker)
        
        market_names = {
            StockMarket.CHINA_A: "中國A股",
            StockMarket.HONG_KONG: "港股",
            StockMarket.US: "美股",
            StockMarket.UNKNOWN: "未知市場"
        }
        
        return {
            "ticker": ticker,
            "market": market.value,
            "market_name": market_names[market],
            "currency_name": currency_name,
            "currency_symbol": currency_symbol,
            "data_source": data_source,
            "is_china": market == StockMarket.CHINA_A,
            "is_hk": market == StockMarket.HONG_KONG,
            "is_us": market == StockMarket.US
        }


# 便捷函數，保持向後兼容
def is_china_stock(ticker: str) -> bool:
    """判斷是否為中國A股（向後兼容）"""
    return StockUtils.is_china_stock(ticker)


def is_hk_stock(ticker: str) -> bool:
    """判斷是否為港股"""
    return StockUtils.is_hk_stock(ticker)


def is_us_stock(ticker: str) -> bool:
    """判斷是否為美股"""
    return StockUtils.is_us_stock(ticker)


def get_stock_market_info(ticker: str) -> Dict:
    """獲取股票市場信息"""
    return StockUtils.get_market_info(ticker)
