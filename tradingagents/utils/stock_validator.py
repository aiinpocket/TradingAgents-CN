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
        預獲取和驗證股票數據

        Args:
            stock_code: 股票代碼
            market_type: 市場類型 ("A股", "港股", "美股", "auto")
            period_days: 歷史數據時長（天），默認使用類初始化時的值
            analysis_date: 分析日期，默認為今天

        Returns:
            StockDataPreparationResult: 數據準备結果
        """
        if period_days is None:
            period_days = self.default_period_days

        if analysis_date is None:
            analysis_date = datetime.now().strftime('%Y-%m-%d')

        logger.info(f"📊 [數據準备] 開始準备股票數據: {stock_code} (市場: {market_type}, 時長: {period_days}天)")

        # 1. 基本格式驗證
        format_result = self._validate_format(stock_code, market_type)
        if not format_result.is_valid:
            return format_result

        # 2. 自動檢測市場類型
        if market_type == "auto":
            market_type = self._detect_market_type(stock_code)
            logger.debug(f"📊 [數據準备] 自動檢測市場類型: {market_type}")

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
        
        # 根據市場類型驗證格式
        if market_type == "A股":
            if not re.match(r'^\d{6}$', stock_code):
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=stock_code,
                    market_type="A股",
                    error_message="A股代碼格式錯誤，應為6位數字",
                    suggestion="請輸入6位數字的A股代碼，如：000001、600519"
                )
        elif market_type == "港股":
            stock_code_upper = stock_code.upper()
            hk_format = re.match(r'^\d{4,5}\.HK$', stock_code_upper)
            digit_format = re.match(r'^\d{4,5}$', stock_code)

            if not (hk_format or digit_format):
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=stock_code,
                    market_type="港股",
                    error_message="港股代碼格式錯誤",
                    suggestion="請輸入4-5位數字.HK格式（如：0700.HK）或4-5位數字（如：0700）"
                )
        elif market_type == "美股":
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
        """自動檢測市場類型"""
        stock_code = stock_code.strip().upper()
        
        # A股：6位數字
        if re.match(r'^\d{6}$', stock_code):
            return "A股"
        
        # 港股：4-5位數字.HK 或 純4-5位數字
        if re.match(r'^\d{4,5}\.HK$', stock_code) or re.match(r'^\d{4,5}$', stock_code):
            return "港股"
        
        # 美股：1-5位字母
        if re.match(r'^[A-Z]{1,5}$', stock_code):
            return "美股"
        
        return "未知"

    def _get_hk_network_limitation_suggestion(self) -> str:
        """獲取港股網絡限制的詳細建議"""
        suggestions = [
            "🌐 港股數據獲取受到網絡API限制，這是常見的臨時問題",
            "",
            "💡 解決方案：",
            "1. 等待5-10分鐘後重試（API限制通常會自動解除）",
            "2. 檢查網絡連接是否穩定",
            "3. 如果是知名港股（如腾讯0700.HK、阿里9988.HK），代碼格式通常正確",
            "4. 可以嘗試使用其他時間段進行分析",
            "",
            "📋 常見港股代碼格式：",
            "• 腾讯控股：0700.HK",
            "• 阿里巴巴：9988.HK",
            "• 美团：3690.HK",
            "• 小米集团：1810.HK",
            "",
            "⏰ 建議稍後重試，或聯系技術支持獲取幫助"
        ]
        return "\n".join(suggestions)

    def _extract_hk_stock_name(self, stock_info, stock_code: str) -> str:
        """從港股信息中提取股票名稱，支持多種格式"""
        if not stock_info:
            return "未知"

        # 處理不同類型的返回值
        if isinstance(stock_info, dict):
            # 如果是字典，嘗試從常見字段提取名稱
            name_fields = ['name', 'longName', 'shortName', 'companyName', '公司名稱', '股票名稱']
            for field in name_fields:
                if field in stock_info and stock_info[field]:
                    name = str(stock_info[field]).strip()
                    if name and name != "未知":
                        return name

            # 如果字典包含有效信息但沒有名稱字段，使用股票代碼
            if len(stock_info) > 0:
                return stock_code
            return "未知"

        # 轉換為字符串處理
        stock_info_str = str(stock_info)

        # 方法1: 標準格式 "公司名稱: XXX"
        if "公司名稱:" in stock_info_str:
            lines = stock_info_str.split('\n')
            for line in lines:
                if "公司名稱:" in line:
                    name = line.split(':')[1].strip()
                    if name and name != "未知":
                        return name

        # 方法2: Yahoo Finance格式檢測
        # 日誌顯示: "✅ Yahoo Finance成功獲取港股信息: 0700.HK -> TENCENT"
        if "Yahoo Finance成功獲取港股信息" in stock_info_str:
            # 從日誌中提取名稱
            if " -> " in stock_info_str:
                parts = stock_info_str.split(" -> ")
                if len(parts) > 1:
                    name = parts[-1].strip()
                    if name and name != "未知":
                        return name

        # 方法3: 檢查是否包含常見的公司名稱關键詞
        company_indicators = [
            "Limited", "Ltd", "Corporation", "Corp", "Inc", "Group",
            "Holdings", "Company", "Co", "集团", "控股", "有限公司"
        ]

        lines = stock_info_str.split('\n')
        for line in lines:
            line = line.strip()
            if any(indicator in line for indicator in company_indicators):
                # 嘗試提取公司名稱
                if ":" in line:
                    potential_name = line.split(':')[-1].strip()
                    if potential_name and len(potential_name) > 2:
                        return potential_name
                elif len(line) > 2 and len(line) < 100:  # 合理的公司名稱長度
                    return line

        # 方法4: 如果信息看起來有效但無法解析名稱，使用股票代碼
        if len(stock_info_str) > 50 and "❌" not in stock_info_str:
            # 信息看起來有效，但無法解析名稱，使用代碼作為名稱
            return stock_code

        return "未知"

    def _prepare_data_by_market(self, stock_code: str, market_type: str,
                               period_days: int, analysis_date: str) -> StockDataPreparationResult:
        """根據市場類型預獲取數據"""
        logger.debug(f"📊 [數據準备] 開始為{market_type}股票{stock_code}準备數據")

        try:
            if market_type == "A股":
                return self._prepare_china_stock_data(stock_code, period_days, analysis_date)
            elif market_type == "港股":
                return self._prepare_hk_stock_data(stock_code, period_days, analysis_date)
            elif market_type == "美股":
                return self._prepare_us_stock_data(stock_code, period_days, analysis_date)
            else:
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=stock_code,
                    market_type=market_type,
                    error_message=f"不支持的市場類型: {market_type}",
                    suggestion="請選擇支持的市場類型：A股、港股、美股"
                )
        except Exception as e:
            logger.error(f"❌ [數據準备] 數據準备異常: {e}")
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=stock_code,
                market_type=market_type,
                error_message=f"數據準备過程中發生錯誤: {str(e)}",
                suggestion="請檢查網絡連接或稍後重試"
            )

    def _prepare_china_stock_data(self, stock_code: str, period_days: int,
                                 analysis_date: str) -> StockDataPreparationResult:
        """預獲取A股數據"""
        logger.info(f"📊 [A股數據] 開始準备{stock_code}的數據 (時長: {period_days}天)")

        # 計算日期範围
        end_date = datetime.strptime(analysis_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=period_days)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        has_historical_data = False
        has_basic_info = False
        stock_name = "未知"
        cache_status = ""

        try:
            # 1. 獲取基本信息
            logger.debug(f"📊 [A股數據] 獲取{stock_code}基本信息...")
            from tradingagents.dataflows.interface import get_china_stock_info_unified

            stock_info = get_china_stock_info_unified(stock_code)

            if stock_info and "❌" not in stock_info and "未能獲取" not in stock_info:
                # 解析股票名稱
                if "股票名稱:" in stock_info:
                    lines = stock_info.split('\n')
                    for line in lines:
                        if "股票名稱:" in line:
                            stock_name = line.split(':')[1].strip()
                            break

                # 檢查是否為有效的股票名稱
                if stock_name != "未知" and not stock_name.startswith(f"股票{stock_code}"):
                    has_basic_info = True
                    logger.info(f"✅ [A股數據] 基本信息獲取成功: {stock_code} - {stock_name}")
                    cache_status += "基本信息已緩存; "
                else:
                    logger.warning(f"⚠️ [A股數據] 基本信息無效: {stock_code}")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=stock_code,
                        market_type="A股",
                        error_message=f"股票代碼 {stock_code} 不存在或信息無效",
                        suggestion="請檢查股票代碼是否正確，或確認该股票是否已上市"
                    )
            else:
                logger.warning(f"⚠️ [A股數據] 無法獲取基本信息: {stock_code}")
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=stock_code,
                    market_type="A股",
                    error_message=f"無法獲取股票 {stock_code} 的基本信息",
                    suggestion="請檢查股票代碼是否正確，或確認该股票是否已上市"
                )

            # 2. 獲取歷史數據
            logger.debug(f"📊 [A股數據] 獲取{stock_code}歷史數據 ({start_date_str} 到 {end_date_str})...")
            from tradingagents.dataflows.interface import get_china_stock_data_unified

            historical_data = get_china_stock_data_unified(stock_code, start_date_str, end_date_str)

            if historical_data and "❌" not in historical_data and "獲取失败" not in historical_data:
                # 更宽松的數據有效性檢查
                data_indicators = [
                    "開盘價", "收盘價", "最高價", "最低價", "成交量",
                    "open", "close", "high", "low", "volume",
                    "日期", "date", "時間", "time"
                ]

                has_valid_data = (
                    len(historical_data) > 50 and  # 降低長度要求
                    any(indicator in historical_data for indicator in data_indicators)
                )

                if has_valid_data:
                    has_historical_data = True
                    logger.info(f"✅ [A股數據] 歷史數據獲取成功: {stock_code} ({period_days}天)")
                    cache_status += f"歷史數據已緩存({period_days}天); "
                else:
                    logger.warning(f"⚠️ [A股數據] 歷史數據無效: {stock_code}")
                    logger.debug(f"🔍 [A股數據] 數據內容預覽: {historical_data[:200]}...")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=stock_code,
                        market_type="A股",
                        stock_name=stock_name,
                        has_basic_info=has_basic_info,
                        error_message=f"股票 {stock_code} 的歷史數據無效或不足",
                        suggestion="该股票可能為新上市股票或數據源暂時不可用，請稍後重試"
                    )
            else:
                logger.warning(f"⚠️ [A股數據] 無法獲取歷史數據: {stock_code}")
                return StockDataPreparationResult(
                    is_valid=False,
                    stock_code=stock_code,
                    market_type="A股",
                    stock_name=stock_name,
                    has_basic_info=has_basic_info,
                    error_message=f"無法獲取股票 {stock_code} 的歷史數據",
                    suggestion="請檢查網絡連接或數據源配置，或稍後重試"
                )

            # 3. 數據準备成功
            logger.info(f"🎉 [A股數據] 數據準备完成: {stock_code} - {stock_name}")
            return StockDataPreparationResult(
                is_valid=True,
                stock_code=stock_code,
                market_type="A股",
                stock_name=stock_name,
                has_historical_data=has_historical_data,
                has_basic_info=has_basic_info,
                data_period_days=period_days,
                cache_status=cache_status.rstrip('; ')
            )

        except Exception as e:
            logger.error(f"❌ [A股數據] 數據準备失败: {e}")
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=stock_code,
                market_type="A股",
                stock_name=stock_name,
                has_basic_info=has_basic_info,
                has_historical_data=has_historical_data,
                error_message=f"數據準备失败: {str(e)}",
                suggestion="請檢查網絡連接或數據源配置"
            )

    def _prepare_hk_stock_data(self, stock_code: str, period_days: int,
                              analysis_date: str) -> StockDataPreparationResult:
        """預獲取港股數據"""
        logger.info(f"📊 [港股數據] 開始準备{stock_code}的數據 (時長: {period_days}天)")

        # 標準化港股代碼格式
        if not stock_code.upper().endswith('.HK'):
            formatted_code = f"{stock_code.zfill(4)}.HK"
        else:
            formatted_code = stock_code.upper()

        # 計算日期範围
        end_date = datetime.strptime(analysis_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=period_days)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        has_historical_data = False
        has_basic_info = False
        stock_name = "未知"
        cache_status = ""

        try:
            # 1. 獲取基本信息
            logger.debug(f"📊 [港股數據] 獲取{formatted_code}基本信息...")
            from tradingagents.dataflows.interface import get_hk_stock_info_unified

            stock_info = get_hk_stock_info_unified(formatted_code)

            if stock_info and "❌" not in stock_info and "未找到" not in stock_info:
                # 解析股票名稱 - 支持多種格式
                stock_name = self._extract_hk_stock_name(stock_info, formatted_code)

                if stock_name and stock_name != "未知":
                    has_basic_info = True
                    logger.info(f"✅ [港股數據] 基本信息獲取成功: {formatted_code} - {stock_name}")
                    cache_status += "基本信息已緩存; "
                else:
                    logger.warning(f"⚠️ [港股數據] 基本信息無效: {formatted_code}")
                    logger.debug(f"🔍 [港股數據] 信息內容: {stock_info[:200]}...")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=formatted_code,
                        market_type="港股",
                        error_message=f"港股代碼 {formatted_code} 不存在或信息無效",
                        suggestion="請檢查港股代碼是否正確，格式如：0700.HK"
                    )
            else:
                # 檢查是否為網絡限制問題
                network_error_indicators = [
                    "Too Many Requests", "Rate limited", "Connection aborted",
                    "Remote end closed connection", "網絡連接", "超時", "限制"
                ]

                is_network_issue = any(indicator in str(stock_info) for indicator in network_error_indicators)

                if is_network_issue:
                    logger.warning(f"🌐 [港股數據] 網絡限制影響: {formatted_code}")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=formatted_code,
                        market_type="港股",
                        error_message=f"港股數據獲取受到網絡限制影響",
                        suggestion=self._get_hk_network_limitation_suggestion()
                    )
                else:
                    logger.warning(f"⚠️ [港股數據] 無法獲取基本信息: {formatted_code}")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=formatted_code,
                        market_type="港股",
                        error_message=f"港股代碼 {formatted_code} 可能不存在或數據源暂時不可用",
                        suggestion="請檢查港股代碼是否正確，格式如：0700.HK，或稍後重試"
                    )

            # 2. 獲取歷史數據
            logger.debug(f"📊 [港股數據] 獲取{formatted_code}歷史數據 ({start_date_str} 到 {end_date_str})...")
            from tradingagents.dataflows.interface import get_hk_stock_data_unified

            historical_data = get_hk_stock_data_unified(formatted_code, start_date_str, end_date_str)

            if historical_data and "❌" not in historical_data and "獲取失败" not in historical_data:
                # 更宽松的數據有效性檢查
                data_indicators = [
                    "開盘價", "收盘價", "最高價", "最低價", "成交量",
                    "open", "close", "high", "low", "volume",
                    "日期", "date", "時間", "time"
                ]

                has_valid_data = (
                    len(historical_data) > 50 and  # 降低長度要求
                    any(indicator in historical_data for indicator in data_indicators)
                )

                if has_valid_data:
                    has_historical_data = True
                    logger.info(f"✅ [港股數據] 歷史數據獲取成功: {formatted_code} ({period_days}天)")
                    cache_status += f"歷史數據已緩存({period_days}天); "
                else:
                    logger.warning(f"⚠️ [港股數據] 歷史數據無效: {formatted_code}")
                    logger.debug(f"🔍 [港股數據] 數據內容預覽: {historical_data[:200]}...")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=formatted_code,
                        market_type="港股",
                        stock_name=stock_name,
                        has_basic_info=has_basic_info,
                        error_message=f"港股 {formatted_code} 的歷史數據無效或不足",
                        suggestion="该股票可能為新上市股票或數據源暂時不可用，請稍後重試"
                    )
            else:
                # 檢查是否為網絡限制問題
                network_error_indicators = [
                    "Too Many Requests", "Rate limited", "Connection aborted",
                    "Remote end closed connection", "網絡連接", "超時", "限制"
                ]

                is_network_issue = any(indicator in str(historical_data) for indicator in network_error_indicators)

                if is_network_issue:
                    logger.warning(f"🌐 [港股數據] 歷史數據獲取受網絡限制: {formatted_code}")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=formatted_code,
                        market_type="港股",
                        stock_name=stock_name,
                        has_basic_info=has_basic_info,
                        error_message=f"港股歷史數據獲取受到網絡限制影響",
                        suggestion=self._get_hk_network_limitation_suggestion()
                    )
                else:
                    logger.warning(f"⚠️ [港股數據] 無法獲取歷史數據: {formatted_code}")
                    return StockDataPreparationResult(
                        is_valid=False,
                        stock_code=formatted_code,
                        market_type="港股",
                        stock_name=stock_name,
                        has_basic_info=has_basic_info,
                        error_message=f"無法獲取港股 {formatted_code} 的歷史數據",
                        suggestion="數據源可能暂時不可用，請稍後重試或聯系技術支持"
                    )

            # 3. 數據準备成功
            logger.info(f"🎉 [港股數據] 數據準备完成: {formatted_code} - {stock_name}")
            return StockDataPreparationResult(
                is_valid=True,
                stock_code=formatted_code,
                market_type="港股",
                stock_name=stock_name,
                has_historical_data=has_historical_data,
                has_basic_info=has_basic_info,
                data_period_days=period_days,
                cache_status=cache_status.rstrip('; ')
            )

        except Exception as e:
            logger.error(f"❌ [港股數據] 數據準备失败: {e}")
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=formatted_code,
                market_type="港股",
                stock_name=stock_name,
                has_basic_info=has_basic_info,
                has_historical_data=has_historical_data,
                error_message=f"數據準备失败: {str(e)}",
                suggestion="請檢查網絡連接或數據源配置"
            )

    def _prepare_us_stock_data(self, stock_code: str, period_days: int,
                              analysis_date: str) -> StockDataPreparationResult:
        """預獲取美股數據"""
        logger.info(f"📊 [美股數據] 開始準备{stock_code}的數據 (時長: {period_days}天)")

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
                # 更宽松的數據有效性檢查
                data_indicators = [
                    "開盘價", "收盘價", "最高價", "最低價", "成交量",
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

                    # 數據準备成功
                    logger.info(f"🎉 [美股數據] 數據準备完成: {formatted_code}")
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
                        suggestion="该股票可能為新上市股票或數據源暂時不可用，請稍後重試"
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
            logger.error(f"❌ [美股數據] 數據準备失败: {e}")
            return StockDataPreparationResult(
                is_valid=False,
                stock_code=formatted_code,
                market_type="美股",
                error_message=f"數據準备失败: {str(e)}",
                suggestion="請檢查網絡連接或數據源配置"
            )




# 全局數據準备器實例
_stock_preparer = None

def get_stock_preparer(default_period_days: int = 30) -> StockDataPreparer:
    """獲取股票數據準备器實例（單例模式）"""
    global _stock_preparer
    if _stock_preparer is None:
        _stock_preparer = StockDataPreparer(default_period_days)
    return _stock_preparer


def prepare_stock_data(stock_code: str, market_type: str = "auto",
                      period_days: int = None, analysis_date: str = None) -> StockDataPreparationResult:
    """
    便捷函數：預獲取和驗證股票數據

    Args:
        stock_code: 股票代碼
        market_type: 市場類型 ("A股", "港股", "美股", "auto")
        period_days: 歷史數據時長（天），默認30天
        analysis_date: 分析日期，默認為今天

    Returns:
        StockDataPreparationResult: 數據準备結果
    """
    preparer = get_stock_preparer()
    return preparer.prepare_stock_data(stock_code, market_type, period_days, analysis_date)


def is_stock_data_ready(stock_code: str, market_type: str = "auto",
                       period_days: int = None, analysis_date: str = None) -> bool:
    """
    便捷函數：檢查股票數據是否準备就绪

    Args:
        stock_code: 股票代碼
        market_type: 市場類型 ("A股", "港股", "美股", "auto")
        period_days: 歷史數據時長（天），默認30天
        analysis_date: 分析日期，默認為今天

    Returns:
        bool: 數據是否準备就绪
    """
    result = prepare_stock_data(stock_code, market_type, period_days, analysis_date)
    return result.is_valid


def get_stock_preparation_message(stock_code: str, market_type: str = "auto",
                                 period_days: int = None, analysis_date: str = None) -> str:
    """
    便捷函數：獲取股票數據準备消息

    Args:
        stock_code: 股票代碼
        market_type: 市場類型 ("A股", "港股", "美股", "auto")
        period_days: 歷史數據時長（天），默認30天
        analysis_date: 分析日期，默認為今天

    Returns:
        str: 數據準备消息
    """
    result = prepare_stock_data(stock_code, market_type, period_days, analysis_date)

    if result.is_valid:
        return f"✅ 數據準备成功: {result.stock_code} ({result.market_type}) - {result.stock_name}\n📊 {result.cache_status}"
    else:
        return f"❌ 數據準备失败: {result.error_message}\n💡 建議: {result.suggestion}"


# 保持向後兼容的別名
StockValidator = StockDataPreparer
get_stock_validator = get_stock_preparer
validate_stock_exists = prepare_stock_data
is_stock_valid = is_stock_data_ready
get_stock_validation_message = get_stock_preparation_message
