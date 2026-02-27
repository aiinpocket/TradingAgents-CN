"""
日誌系統初始化模組
從 logging_manager 重新匯出常用函式，供各子模組統一匯入
"""

from tradingagents.utils.logging_manager import get_logger


def setup_dataflow_logging():
    """設定資料流專用日誌"""
    return get_logger('dataflows')
