#!/usr/bin/env python3
"""
TradingAgents-CN 核心模組

這是一個基於多智慧體的股票分析系統，專注於美股的綜合分析。
"""

__version__ = "0.1.19"
__author__ = "TradingAgents-CN Team"
__description__ = "Multi-agent stock analysis system for US markets"

# 匯入核心模組
try:
    from .config import config_manager
    from .utils import logging_manager
except ImportError:
    # 如果匯入失敗，不影響模組的基本功能
    pass

__all__ = [
    "__version__",
    "__author__", 
    "__description__"
]