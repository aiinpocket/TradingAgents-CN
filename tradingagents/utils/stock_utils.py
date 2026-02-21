"""
美股工具函數
提供美股代碼識別和處理功能
"""

import re
from typing import Dict, Tuple, Optional

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def is_valid_us_ticker(ticker: str) -> bool:
    """
    驗證是否為有效的美股代碼
    美股代碼為 1-5 位大寫英文字母

    Args:
        ticker: 股票代碼

    Returns:
        bool: 是否為有效的美股代碼
    """
    if not ticker:
        return False
    ticker = str(ticker).strip().upper()
    return bool(re.match(r'^[A-Z]{1,5}$', ticker))


def get_currency_info() -> Tuple[str, str]:
    """
    取得美股貨幣資訊

    Returns:
        Tuple[str, str]: (貨幣名稱, 貨幣符號)
    """
    return "美元", "$"


def get_stock_market_info(ticker: str) -> Dict:
    """
    取得股票市場的詳細資訊（僅支援美股）

    Args:
        ticker: 股票代碼

    Returns:
        Dict: 市場資訊字典
    """
    ticker = str(ticker).strip().upper() if ticker else ""
    is_valid = is_valid_us_ticker(ticker)

    return {
        "ticker": ticker,
        "market": "us",
        "market_name": "美股",
        "currency_name": "美元",
        "currency_symbol": "$",
        "data_source": "yahoo_finance",
        "is_us": is_valid,
    }


# 向後相容函數
def is_us_stock(ticker: str) -> bool:
    """判斷是否為有效的美股代碼"""
    return is_valid_us_ticker(ticker)
