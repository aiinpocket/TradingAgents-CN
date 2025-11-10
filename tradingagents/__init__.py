#!/usr/bin/env python3
"""
TradingAgents-CN 核心模塊

這是一個基於多智能體的股票分析系統，支持A股、港股和美股的綜合分析。
"""

__version__ = "0.1.8"
__author__ = "TradingAgents-CN Team"
__description__ = "Multi-agent stock analysis system for Chinese markets"

# 導入核心模塊
try:
    from .config import config_manager
    from .utils import logging_manager
except ImportError:
    # 如果導入失败，不影響模塊的基本功能
    pass

__all__ = [
    "__version__",
    "__author__", 
    "__description__"
]