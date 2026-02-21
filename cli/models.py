from enum import Enum

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("cli")


class AnalystType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
