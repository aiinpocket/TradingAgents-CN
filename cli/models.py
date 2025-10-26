from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("cli")


class AnalystType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
