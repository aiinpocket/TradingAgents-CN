# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

# 嘗試匯入 yfinance 相關模組，如果失敗則跳過
try:
    from .yfin_utils import YFinanceUtils
    YFINANCE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"yfinance 模組不可用: {e}")
    YFinanceUtils = None
    YFINANCE_AVAILABLE = False

try:
    from .stockstats_utils import StockstatsUtils
    STOCKSTATS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"stockstats 模組不可用: {e}")
    StockstatsUtils = None
    STOCKSTATS_AVAILABLE = False

from .interface import (
    # 新聞與情緒相關函式
    get_finnhub_news,
    get_finnhub_company_insider_sentiment,
    get_finnhub_company_insider_transactions,
    get_google_news,
    # 財務報表相關函式
    get_simfin_balance_sheet,
    get_simfin_cashflow,
    get_simfin_income_statements,
    # 技術分析相關函式
    get_stock_stats_indicators_window,
    get_stockstats_indicator,
    # 市場資料相關函式
    get_YFin_data_window,
    get_YFin_data,
)

__all__ = [
    # 新聞與情緒相關函式
    "get_finnhub_news",
    "get_finnhub_company_insider_sentiment",
    "get_finnhub_company_insider_transactions",
    "get_google_news",
    # 財務報表相關函式
    "get_simfin_balance_sheet",
    "get_simfin_cashflow",
    "get_simfin_income_statements",
    # 技術分析相關函式
    "get_stock_stats_indicators_window",
    "get_stockstats_indicator",
    # 市場資料相關函式
    "get_YFin_data_window",
    "get_YFin_data",
]
