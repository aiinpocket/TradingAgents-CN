"""
美股工具函式
提供美股代碼識別和處理功能
"""

import re
from typing import Dict, Tuple

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


# 常見美股代碼對應的中文公司名稱
_US_STOCK_NAMES = {
    'AAPL': '蘋果公司',
    'TSLA': '特斯拉',
    'NVDA': '輝達',
    'MSFT': '微軟',
    'GOOGL': '谷歌',
    'GOOG': '谷歌',
    'AMZN': '亞馬遜',
    'META': 'Meta',
    'NFLX': 'Netflix',
    'AMD': '超微半導體',
    'INTC': '英特爾',
    'CRM': 'Salesforce',
    'AVGO': '博通',
    'QCOM': '高通',
}


def get_company_name(ticker: str) -> str:
    """根據股票代碼取得中文公司名稱（無對應時返回原代碼）"""
    return _US_STOCK_NAMES.get(ticker.upper(), ticker)


# 向後相容函式
def is_us_stock(ticker: str) -> bool:
    """判斷是否為有效的美股代碼"""
    return is_valid_us_ticker(ticker)
