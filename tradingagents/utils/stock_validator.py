#!/usr/bin/env python3
"""
股票數據預獲取和驗證模塊
用於在分析流程開始前驗證股票是否存在，並預先獲取和緩存必要的數據
"""

import re
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('stock_validator')


class StockDataPreparationResult:
    """股票數據預獲取結果類"""

    def __init__(self, is_valid: bool, stock_code: str, market_type: str = "",
                 stock_name: str = "", error_message: str = "", suggestion: str = "",
                 has_historical_data: bool = False, has_basic_info: bool = False,
                 data_period_days: int = 0, cache_status: str = ""):
        self.is_valid = is_valid
        self.stock_code = stock_code
        self.market_type = market_type
        self.stock_name = stock_name
        self.error_message = error_message
        self.suggestion = suggestion
        self.has_historical_data = has_historical_data
        self.has_basic_info = has_basic_info
        self.data_period_days = data_period_days
        self.cache_status = cache_status

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'is_valid': self.is_valid,
            'stock_code': self.stock_code,
            'market_type': self.market_type,
            'stock_name': self.stock_name,
            'error_message': self.error_message,
            'suggestion': self.suggestion,
            'has_historical_data': self.has_historical_data,
            'has_basic_info': self.has_basic_info,
            'data_period_days': self.data_period_days,
            'cache_status': self.cache_status
        }


# 保持向後兼容
StockValidationResult = StockDataPreparationResult


class StockDataPreparer:
    """股票數據預獲取和驗證器"""

    def __init__(self, default_period_days: int = 30):
        self.timeout_seconds = 15  # 數據獲取超時時間
        self.default_period_days = default_period_days  # 默認歷史數據時長（天）
    
    def prepare_stock_data(self, stock_code: str, market_type: str = "auto",
                          period_days: int = None, analysis_date: str = None) -> StockDataPreparationResult:
        """
        預獲取和驗證股票數據（僅支援美股）

        Args:
            stock_code: 股票代碼（美股，1-5位字母）
            market_type: 市場類型 ("美股" 或 "auto")
            period_days: 歷史數據時長（天），默認使用類初始化時的值
            analysis_date: 分析日期，默認為今天

        Returns:
            StockDataPreparationResult: 數據準備結果
        """
        if period_days is None:
            period_days = self.default_period_days

        if analysis_date is None:
            analysis_date = datetime.now().strftime('%Y-%m-%d')

        logger.info(f"📊 [數據準備] 開始準備股票數據: {stock_code} (市場: {market_type}, 時長: {period_days}天)")

        # 1. 基本格式驗證
        format_result = self._validate_format(stock_code, market_type)
        if not format_result.is_valid:
            return format_result

        # 2. 自動檢測市場類型
        if market_type == "auto":
            market_type = self._detect_market_type(stock_code)
            logger.debug(f"📊 [數據準備] 自動檢測市場類型: {market_type}")

        # 3. 預獲取數據並驗證
        return self._prepare_data_by_market(stock_code, market_type, period_days, analysis_date)
    
    def _validate_format(self, stock_code: str, market_type: str) -> StockDataPreparationResult:
        """驗證股票代碼格式"""
        stock_code = stock_code.strip()
        
        if not stock_code:
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=stock_code,
                error_message="股票代碼不能為空",
                suggestion="請輸入有效的股票代碼"
            )

        if len(stock_code) > 10:
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=stock_code,
                error_message="股票代碼長度不能超過10個字符",
                suggestion="請檢查股票代碼格式"
            )
        
        # 驗證美股代碼格式
        if market_type == "美股":
            if not re.match(r'^[A-Z]{1,5}$', stock_code.upper()):
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=stock_code,
                    market_type="美股",
                    error_message="美股代碼格式錯誤，應為1-5位字母",
                    suggestion="請輸入1-5位字母的美股代碼，如：AAPL、TSLA"
                )
        
        return StockDataPreparationResult(
            is_valid=True,
            stock_code=stock_code,
            market_type=market_type
        )
    
    def _detect_market_type(self, stock_code: str) -> str:
        """自動檢測市場類型（僅支援美股）"""
        stock_code = stock_code.strip().upper()

        # 美股：1-5位字母
        if re.match(r'^[A-Z]{1,5}$', stock_code):
            return "美股"

        return "未知"

    def _prepare_data_by_market(self, stock_code: str, market_type: str,
                               period_days: int, analysis_date: str) -> StockDataPreparationResult:
        """根據市場類型預獲取數據（僅支援美股）"""
        logger.debug(f"[數據準備] 開始為{market_type}股票{stock_code}準備數據")

        try:
            if market_type == "美股":
                return self._prepare_us_stock_data(stock_code, period_days, analysis_date)
            else:
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=stock_code,
                    market_type=market_type,
                    error_message=f"不支援的市場類型: {market_type}",
                    suggestion="目前僅支援美股，請輸入1-5位字母的美股代碼，如：AAPL、TSLA"
                )
        except Exception as e:
            logger.error(f"[數據準備] 數據準備異常: {e}")
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=stock_code,
                market_type=market_type,
                error_message=f"數據準備過程中發生錯誤: {str(e)}",
                suggestion="請檢查網絡連接或稍後重試"
            )

    def _prepare_us_stock_data(self, stock_code: str, period_days: int,
                              analysis_date: str) -> StockDataPreparationResult:
        """預獲取美股數據"""
        logger.info(f"📊 [美股數據] 開始準備{stock_code}的數據 (時長: {period_days}天)")

        # 標準化美股代碼格式
        formatted_code = stock_code.upper()

        # 計算日期範围
        end_date = datetime.strptime(analysis_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=period_days)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        has_historical_data = False
        has_basic_info = False
        stock_name = formatted_code  # 美股通常使用代碼作為名稱
        cache_status = ""

        try:
            # 1. 獲取歷史數據（美股通常直接通過歷史數據驗證股票是否存在）
            logger.debug(f"📊 [美股數據] 獲取{formatted_code}歷史數據 ({start_date_str} 到 {end_date_str})...")
            from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached

            historical_data = get_us_stock_data_cached(
                formatted_code,
                start_date_str,
                end_date_str
            )

            if historical_data and "❌" not in historical_data and "錯誤" not in historical_data and "無法獲取" not in historical_data:
                # 更寬鬆的數據有效性檢查
                data_indicators = [
                    "開盤價", "收盤價", "最高價", "最低價", "成交量",
                    "Open", "Close", "High", "Low", "Volume",
                    "日期", "Date", "時間", "Time"
                ]

                has_valid_data = (
                    len(historical_data) > 50 and  # 降低長度要求
                    any(indicator in historical_data for indicator in data_indicators)
                )

                if has_valid_data:
                    has_historical_data = True
                    has_basic_info = True  # 美股通常不單獨獲取基本信息
                    logger.info(f"✅ [美股數據] 歷史數據獲取成功: {formatted_code} ({period_days}天)")
                    cache_status = f"歷史數據已緩存({period_days}天)"

                    # 數據準備成功
                    logger.info(f"🎉 [美股數據] 數據準備完成: {formatted_code}")
                    return StockDataPreparationResult(
                        is_valid=True,
                        stock_code=formatted_code,
                        market_type="美股",
                        stock_name=stock_name,
                        has_historical_data=has_historical_data,
                        has_basic_info=has_basic_info,
                        data_period_days=period_days,
                        cache_status=cache_status
                    )
                else:
                    logger.warning(f"⚠️ [美股數據] 歷史數據無效: {formatted_code}")
                    logger.debug(f"🔍 [美股數據] 數據內容預覽: {historical_data[:200]}...")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=formatted_code,
                        market_type="美股",
                        error_message=f"美股 {formatted_code} 的歷史數據無效或不足",
                        suggestion="該股票可能為新上市股票或數據源暫時不可用，請稍後重試"
                    )
            else:
                logger.warning(f"⚠️ [美股數據] 無法獲取歷史數據: {formatted_code}")
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=formatted_code,
                    market_type="美股",
                    error_message=f"美股代碼 {formatted_code} 不存在或無法獲取數據",
                    suggestion="請檢查美股代碼是否正確，如：AAPL、TSLA、MSFT"
                )

        except Exception as e:
            logger.error(f"❌ [美股數據] 數據準備失敗: {e}")
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=formatted_code,
                market_type="美股",
                error_message=f"數據準備失敗: {str(e)}",
                suggestion="請檢查網絡連接或數據源配置"
            )




# 全局數據準備器實例
_stock_preparer = None

def get_stock_preparer(default_period_days: int = 30) -> StockDataPreparer:
    """獲取股票數據準備器實例（單例模式）"""
    global _stock_preparer
    if _stock_preparer is None:
        _stock_preparer = StockDataPreparer(default_period_days)
    return _stock_preparer


def prepare_stock_data(stock_code: str, market_type: str = "auto",
                      period_days: int = None, analysis_date: str = None) -> StockDataPreparationResult:
    """
    便捷函數：預獲取和驗證股票數據（僅支援美股）

    Args:
        stock_code: 股票代碼（美股，1-5位字母）
        market_type: 市場類型 ("美股" 或 "auto")
        period_days: 歷史數據時長（天），默認30天
        analysis_date: 分析日期，默認為今天

    Returns:
        StockDataPreparationResult: 數據準備結果
    """
    preparer = get_stock_preparer()
    return preparer.prepare_stock_data(stock_code, market_type, period_days, analysis_date)


def is_stock_data_ready(stock_code: str, market_type: str = "auto",
                       period_days: int = None, analysis_date: str = None) -> bool:
    """
    便捷函數：檢查股票數據是否準備就緒（僅支援美股）

    Args:
        stock_code: 股票代碼（美股，1-5位字母）
        market_type: 市場類型 ("美股" 或 "auto")
        period_days: 歷史數據時長（天），默認30天
        analysis_date: 分析日期，默認為今天

    Returns:
        bool: 數據是否準備就緒
    """
    result = prepare_stock_data(stock_code, market_type, period_days, analysis_date)
    return result.is_valid


def get_stock_preparation_message(stock_code: str, market_type: str = "auto",
                                 period_days: int = None, analysis_date: str = None) -> str:
    """
    便捷函數：獲取股票數據準備訊息（僅支援美股）

    Args:
        stock_code: 股票代碼（美股，1-5位字母）
        market_type: 市場類型 ("美股" 或 "auto")
        period_days: 歷史數據時長（天），默認30天
        analysis_date: 分析日期，默認為今天

    Returns:
        str: 數據準備訊息
    """
    result = prepare_stock_data(stock_code, market_type, period_days, analysis_date)

    if result.is_valid:
        return f"✅ 數據準備成功: {result.stock_code} ({result.market_type}) - {result.stock_name}\n📊 {result.cache_status}"
    else:
        return f"❌ 數據準備失敗: {result.error_message}\n💡 建議: {result.suggestion}"


# 保持向後兼容的別名
StockValidator = StockDataPreparer
get_stock_validator = get_stock_preparer
validate_stock_exists = prepare_stock_data
is_stock_valid = is_stock_data_ready
get_stock_validation_message = get_stock_preparation_message
