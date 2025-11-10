#!/usr/bin/env python3
"""
數據源管理器
統一管理中國股票數據源的選擇和切換，支持Tushare、AKShare、BaoStock等
"""

import os
import time
from typing import Dict, List, Optional, Any
from enum import Enum
import warnings
import pandas as pd

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')
warnings.filterwarnings('ignore')

# 導入統一日誌系統
from tradingagents.utils.logging_init import setup_dataflow_logging
logger = setup_dataflow_logging()


class ChinaDataSource(Enum):
    """中國股票數據源枚举"""
    TUSHARE = "tushare"
    AKSHARE = "akshare"
    BAOSTOCK = "baostock"





class DataSourceManager:
    """數據源管理器"""

    def __init__(self):
        """初始化數據源管理器"""
        self.default_source = self._get_default_source()
        self.available_sources = self._check_available_sources()
        self.current_source = self.default_source

        logger.info(f"📊 數據源管理器初始化完成")
        logger.info(f"   默認數據源: {self.default_source.value}")
        logger.info(f"   可用數據源: {[s.value for s in self.available_sources]}")

    def _get_default_source(self) -> ChinaDataSource:
        """獲取默認數據源"""
        # 從環境變量獲取，默認使用AKShare作為第一優先級數據源
        env_source = os.getenv('DEFAULT_CHINA_DATA_SOURCE', 'akshare').lower()

        # 映射到枚举
        source_mapping = {
            'tushare': ChinaDataSource.TUSHARE,
            'akshare': ChinaDataSource.AKSHARE,
            'baostock': ChinaDataSource.BAOSTOCK
        }

        return source_mapping.get(env_source, ChinaDataSource.AKSHARE)

    # ==================== Tushare數據接口 ====================

    def get_china_stock_data_tushare(self, symbol: str, start_date: str, end_date: str) -> str:
        """
        使用Tushare獲取中國A股歷史數據

        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            str: 格式化的股票數據報告
        """
        # 臨時切換到Tushare數據源
        original_source = self.current_source
        self.current_source = ChinaDataSource.TUSHARE

        try:
            result = self._get_tushare_data(symbol, start_date, end_date)
            return result
        finally:
            # 恢複原始數據源
            self.current_source = original_source

    def search_china_stocks_tushare(self, keyword: str) -> str:
        """
        使用Tushare搜索中國股票

        Args:
            keyword: 搜索關键詞

        Returns:
            str: 搜索結果
        """
        try:
            from .tushare_adapter import get_tushare_adapter

            logger.debug(f"🔍 [Tushare] 搜索股票: {keyword}")

            adapter = get_tushare_adapter()
            results = adapter.search_stocks(keyword)

            if results is not None and not results.empty:
                result = f"搜索關键詞: {keyword}\n"
                result += f"找到 {len(results)} 只股票:\n\n"

                # 顯示前10個結果
                for idx, row in results.head(10).iterrows():
                    result += f"代碼: {row.get('symbol', '')}\n"
                    result += f"名稱: {row.get('name', '未知')}\n"
                    result += f"行業: {row.get('industry', '未知')}\n"
                    result += f"地区: {row.get('area', '未知')}\n"
                    result += f"上市日期: {row.get('list_date', '未知')}\n"
                    result += "-" * 30 + "\n"

                return result
            else:
                return f"❌ 未找到匹配'{keyword}'的股票"

        except Exception as e:
            logger.error(f"❌ [Tushare] 搜索股票失败: {e}")
            return f"❌ 搜索股票失败: {e}"

    def get_china_stock_fundamentals_tushare(self, symbol: str) -> str:
        """
        使用Tushare獲取中國股票基本面數據

        Args:
            symbol: 股票代碼

        Returns:
            str: 基本面分析報告
        """
        try:
            from .tushare_adapter import get_tushare_adapter

            logger.debug(f"📊 [Tushare] 獲取{symbol}基本面數據...")

            adapter = get_tushare_adapter()
            fundamentals = adapter.get_fundamentals(symbol)

            if fundamentals:
                return fundamentals
            else:
                return f"❌ 未獲取到{symbol}的基本面數據"

        except Exception as e:
            logger.error(f"❌ [Tushare] 獲取基本面數據失败: {e}")
            return f"❌ 獲取{symbol}基本面數據失败: {e}"

    def get_china_stock_info_tushare(self, symbol: str) -> str:
        """
        使用Tushare獲取中國股票基本信息

        Args:
            symbol: 股票代碼

        Returns:
            str: 股票基本信息
        """
        try:
            from .tushare_adapter import get_tushare_adapter

            logger.debug(f"📊 [Tushare] 獲取{symbol}股票信息...")

            adapter = get_tushare_adapter()
            stock_info = adapter.get_stock_info(symbol)

            if stock_info:
                result = f"📊 {stock_info.get('name', '未知')}({symbol}) - 股票信息\n"
                result += f"股票代碼: {stock_info.get('symbol', symbol)}\n"
                result += f"股票名稱: {stock_info.get('name', '未知')}\n"
                result += f"所屬行業: {stock_info.get('industry', '未知')}\n"
                result += f"所屬地区: {stock_info.get('area', '未知')}\n"
                result += f"上市日期: {stock_info.get('list_date', '未知')}\n"
                result += f"市場類型: {stock_info.get('market', '未知')}\n"
                result += f"交易所: {stock_info.get('exchange', '未知')}\n"
                result += f"貨币單位: {stock_info.get('curr_type', 'CNY')}\n"

                return result
            else:
                return f"❌ 未獲取到{symbol}的股票信息"

        except Exception as e:
            logger.error(f"❌ [Tushare] 獲取股票信息失败: {e}", exc_info=True)
            return f"❌ 獲取{symbol}股票信息失败: {e}"
    
    def _check_available_sources(self) -> List[ChinaDataSource]:
        """檢查可用的數據源"""
        available = []
        
        # 檢查Tushare
        try:
            import tushare as ts
            token = os.getenv('TUSHARE_TOKEN')
            if token:
                available.append(ChinaDataSource.TUSHARE)
                logger.info("✅ Tushare數據源可用")
            else:
                logger.warning("⚠️ Tushare數據源不可用: 未設置TUSHARE_TOKEN")
        except ImportError:
            logger.warning("⚠️ Tushare數據源不可用: 庫未安裝")
        
        # 檢查AKShare
        try:
            import akshare as ak
            available.append(ChinaDataSource.AKSHARE)
            logger.info("✅ AKShare數據源可用")
        except ImportError:
            logger.warning("⚠️ AKShare數據源不可用: 庫未安裝")
        
        # 檢查BaoStock
        try:
            import baostock as bs
            available.append(ChinaDataSource.BAOSTOCK)
            logger.info(f"✅ BaoStock數據源可用")
        except ImportError:
            logger.warning(f"⚠️ BaoStock數據源不可用: 庫未安裝")
        
        return available
    
    def get_current_source(self) -> ChinaDataSource:
        """獲取當前數據源"""
        return self.current_source
    
    def set_current_source(self, source: ChinaDataSource) -> bool:
        """設置當前數據源"""
        if source in self.available_sources:
            self.current_source = source
            logger.info(f"✅ 數據源已切換到: {source.value}")
            return True
        else:
            logger.error(f"❌ 數據源不可用: {source.value}")
            return False
    
    def get_data_adapter(self):
        """獲取當前數據源的適配器"""
        if self.current_source == ChinaDataSource.TUSHARE:
            return self._get_tushare_adapter()
        elif self.current_source == ChinaDataSource.AKSHARE:
            return self._get_akshare_adapter()
        elif self.current_source == ChinaDataSource.BAOSTOCK:
            return self._get_baostock_adapter()
        else:
            raise ValueError(f"不支持的數據源: {self.current_source}")
    
    def _get_tushare_adapter(self):
        """獲取Tushare適配器"""
        try:
            from .tushare_adapter import get_tushare_adapter
            return get_tushare_adapter()
        except ImportError as e:
            logger.error(f"❌ Tushare適配器導入失败: {e}")
            return None
    
    def _get_akshare_adapter(self):
        """獲取AKShare適配器"""
        try:
            from .akshare_utils import get_akshare_provider
            return get_akshare_provider()
        except ImportError as e:
            logger.error(f"❌ AKShare適配器導入失败: {e}")
            return None
    
    def _get_baostock_adapter(self):
        """獲取BaoStock適配器"""
        try:
            from .baostock_utils import get_baostock_provider
            return get_baostock_provider()
        except ImportError as e:
            logger.error(f"❌ BaoStock適配器導入失败: {e}")
            return None
    
    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> str:
        """
        獲取股票數據的統一接口

        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            str: 格式化的股票數據
        """
        # 記錄詳細的輸入參數
        logger.info(f"📊 [數據獲取] 開始獲取股票數據",
                   extra={
                       'symbol': symbol,
                       'start_date': start_date,
                       'end_date': end_date,
                       'data_source': self.current_source.value,
                       'event_type': 'data_fetch_start'
                   })

        # 添加詳細的股票代碼追蹤日誌
        logger.info(f"🔍 [股票代碼追蹤] DataSourceManager.get_stock_data 接收到的股票代碼: '{symbol}' (類型: {type(symbol)})")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(symbol))}")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(symbol))}")
        logger.info(f"🔍 [股票代碼追蹤] 當前數據源: {self.current_source.value}")

        start_time = time.time()

        try:
            # 根據數據源調用相應的獲取方法
            if self.current_source == ChinaDataSource.TUSHARE:
                logger.info(f"🔍 [股票代碼追蹤] 調用 Tushare 數據源，傳入參數: symbol='{symbol}'")
                result = self._get_tushare_data(symbol, start_date, end_date)
            elif self.current_source == ChinaDataSource.AKSHARE:
                result = self._get_akshare_data(symbol, start_date, end_date)
            elif self.current_source == ChinaDataSource.BAOSTOCK:
                result = self._get_baostock_data(symbol, start_date, end_date)
            else:
                result = f"❌ 不支持的數據源: {self.current_source.value}"

            # 記錄詳細的輸出結果
            duration = time.time() - start_time
            result_length = len(result) if result else 0
            is_success = result and "❌" not in result and "錯誤" not in result

            if is_success:
                logger.info(f"✅ [數據獲取] 成功獲取股票數據",
                           extra={
                               'symbol': symbol,
                               'start_date': start_date,
                               'end_date': end_date,
                               'data_source': self.current_source.value,
                               'duration': duration,
                               'result_length': result_length,
                               'result_preview': result[:200] + '...' if result_length > 200 else result,
                               'event_type': 'data_fetch_success'
                           })
                return result
            else:
                logger.warning(f"⚠️ [數據獲取] 數據質量異常，嘗試降級到其他數據源",
                              extra={
                                  'symbol': symbol,
                                  'start_date': start_date,
                                  'end_date': end_date,
                                  'data_source': self.current_source.value,
                                  'duration': duration,
                                  'result_length': result_length,
                                  'result_preview': result[:200] + '...' if result_length > 200 else result,
                                  'event_type': 'data_fetch_warning'
                              })

                # 數據質量異常時也嘗試降級到其他數據源
                fallback_result = self._try_fallback_sources(symbol, start_date, end_date)
                if fallback_result and "❌" not in fallback_result and "錯誤" not in fallback_result:
                    logger.info(f"✅ [數據獲取] 降級成功獲取數據")
                    return fallback_result
                else:
                    logger.error(f"❌ [數據獲取] 所有數據源都無法獲取有效數據")
                    return result  # 返回原始結果（包含錯誤信息）

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ [數據獲取] 異常失败: {e}",
                        extra={
                            'symbol': symbol,
                            'start_date': start_date,
                            'end_date': end_date,
                            'data_source': self.current_source.value,
                            'duration': duration,
                            'error': str(e),
                            'event_type': 'data_fetch_exception'
                        }, exc_info=True)
            return self._try_fallback_sources(symbol, start_date, end_date)
    
    def _get_tushare_data(self, symbol: str, start_date: str, end_date: str) -> str:
        """使用Tushare獲取數據 - 直接調用適配器，避免循環調用"""
        logger.debug(f"📊 [Tushare] 調用參數: symbol={symbol}, start_date={start_date}, end_date={end_date}")

        # 添加詳細的股票代碼追蹤日誌
        logger.info(f"🔍 [股票代碼追蹤] _get_tushare_data 接收到的股票代碼: '{symbol}' (類型: {type(symbol)})")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(symbol))}")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(symbol))}")
        logger.info(f"🔍 [DataSourceManager詳細日誌] _get_tushare_data 開始執行")
        logger.info(f"🔍 [DataSourceManager詳細日誌] 當前數據源: {self.current_source.value}")

        start_time = time.time()
        try:
            # 直接調用適配器，避免循環調用interface
            from .tushare_adapter import get_tushare_adapter
            logger.info(f"🔍 [股票代碼追蹤] 調用 tushare_adapter，傳入參數: symbol='{symbol}'")
            logger.info(f"🔍 [DataSourceManager詳細日誌] 開始調用tushare_adapter...")

            adapter = get_tushare_adapter()
            data = adapter.get_stock_data(symbol, start_date, end_date)

            if data is not None and not data.empty:
                # 獲取股票基本信息
                stock_info = adapter.get_stock_info(symbol)
                stock_name = stock_info.get('name', f'股票{symbol}') if stock_info else f'股票{symbol}'

                # 計算最新價格和涨跌幅
                latest_data = data.iloc[-1]
                latest_price = latest_data.get('close', 0)
                prev_close = data.iloc[-2].get('close', latest_price) if len(data) > 1 else latest_price
                change = latest_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close != 0 else 0

                # 格式化數據報告
                result = f"📊 {stock_name}({symbol}) - Tushare數據\n"
                result += f"數據期間: {start_date} 至 {end_date}\n"
                result += f"數據條數: {len(data)}條\n\n"

                result += f"💰 最新價格: ¥{latest_price:.2f}\n"
                result += f"📈 涨跌額: {change:+.2f} ({change_pct:+.2f}%)\n\n"

                # 添加統計信息
                result += f"📊 價格統計:\n"
                result += f"   最高價: ¥{data['high'].max():.2f}\n"
                result += f"   最低價: ¥{data['low'].min():.2f}\n"
                result += f"   平均價: ¥{data['close'].mean():.2f}\n"
                # 防御性獲取成交量數據
                volume_value = self._get_volume_safely(data)
                result += f"   成交量: {volume_value:,.0f}股\n"

                return result
            else:
                result = f"❌ 未獲取到{symbol}的有效數據"

            duration = time.time() - start_time
            logger.info(f"🔍 [DataSourceManager詳細日誌] interface調用完成，耗時: {duration:.3f}秒")
            logger.info(f"🔍 [股票代碼追蹤] get_china_stock_data_tushare 返回結果前200字符: {result[:200] if result else 'None'}")
            logger.info(f"🔍 [DataSourceManager詳細日誌] 返回結果類型: {type(result)}")
            logger.info(f"🔍 [DataSourceManager詳細日誌] 返回結果長度: {len(result) if result else 0}")

            logger.debug(f"📊 [Tushare] 調用完成: 耗時={duration:.2f}s, 結果長度={len(result) if result else 0}")

            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ [Tushare] 調用失败: {e}, 耗時={duration:.2f}s", exc_info=True)
            logger.error(f"❌ [DataSourceManager詳細日誌] 異常類型: {type(e).__name__}")
            logger.error(f"❌ [DataSourceManager詳細日誌] 異常信息: {str(e)}")
            import traceback
            logger.error(f"❌ [DataSourceManager詳細日誌] 異常堆棧: {traceback.format_exc()}")
            raise
    
    def _get_akshare_data(self, symbol: str, start_date: str, end_date: str) -> str:
        """使用AKShare獲取數據"""
        logger.debug(f"📊 [AKShare] 調用參數: symbol={symbol}, start_date={start_date}, end_date={end_date}")

        start_time = time.time()
        try:
            # 這里需要實現AKShare的統一接口
            from .akshare_utils import get_akshare_provider
            provider = get_akshare_provider()
            data = provider.get_stock_data(symbol, start_date, end_date)

            duration = time.time() - start_time

            if data is not None and not data.empty:
                result = f"股票代碼: {symbol}\n"
                result += f"數據期間: {start_date} 至 {end_date}\n"
                result += f"數據條數: {len(data)}條\n\n"

                # 顯示最新3天數據，確保在各種顯示環境下都能完整顯示
                display_rows = min(3, len(data))
                result += f"最新{display_rows}天數據:\n"

                # 使用pandas選項確保顯示完整數據
                with pd.option_context('display.max_rows', None,
                                     'display.max_columns', None,
                                     'display.width', None,
                                     'display.max_colwidth', None):
                    result += data.tail(display_rows).to_string(index=False)

                # 如果數據超過3天，也顯示一些統計信息
                if len(data) > 3:
                    latest_price = data.iloc[-1]['收盘'] if '收盘' in data.columns else data.iloc[-1].get('close', 'N/A')
                    first_price = data.iloc[0]['收盘'] if '收盘' in data.columns else data.iloc[0].get('close', 'N/A')
                    if latest_price != 'N/A' and first_price != 'N/A':
                        try:
                            change = float(latest_price) - float(first_price)
                            change_pct = (change / float(first_price)) * 100
                            result += f"\n\n📊 期間統計:\n"
                            result += f"期間涨跌: {change:+.2f} ({change_pct:+.2f}%)\n"
                            result += f"最高價: {data['最高'].max() if '最高' in data.columns else data.get('high', pd.Series()).max():.2f}\n"
                            result += f"最低價: {data['最低'].min() if '最低' in data.columns else data.get('low', pd.Series()).min():.2f}"
                        except (ValueError, TypeError):
                            pass

                logger.debug(f"📊 [AKShare] 調用成功: 耗時={duration:.2f}s, 數據條數={len(data)}, 結果長度={len(result)}")
                return result
            else:
                result = f"❌ 未能獲取{symbol}的股票數據"
                logger.warning(f"⚠️ [AKShare] 數據為空: 耗時={duration:.2f}s")
                return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ [AKShare] 調用失败: {e}, 耗時={duration:.2f}s", exc_info=True)
            return f"❌ AKShare獲取{symbol}數據失败: {e}"
    
    def _get_baostock_data(self, symbol: str, start_date: str, end_date: str) -> str:
        """使用BaoStock獲取數據"""
        # 這里需要實現BaoStock的統一接口
        from .baostock_utils import get_baostock_provider
        provider = get_baostock_provider()
        data = provider.get_stock_data(symbol, start_date, end_date)
        
        if data is not None and not data.empty:
            result = f"股票代碼: {symbol}\n"
            result += f"數據期間: {start_date} 至 {end_date}\n"
            result += f"數據條數: {len(data)}條\n\n"

            # 顯示最新3天數據，確保在各種顯示環境下都能完整顯示
            display_rows = min(3, len(data))
            result += f"最新{display_rows}天數據:\n"

            # 使用pandas選項確保顯示完整數據
            with pd.option_context('display.max_rows', None,
                                 'display.max_columns', None,
                                 'display.width', None,
                                 'display.max_colwidth', None):
                result += data.tail(display_rows).to_string(index=False)
            return result
        else:
            return f"❌ 未能獲取{symbol}的股票數據"
    
    def _get_volume_safely(self, data) -> float:
        """安全地獲取成交量數據，支持多種列名"""
        try:
            # 支持多種可能的成交量列名
            volume_columns = ['volume', 'vol', 'turnover', 'trade_volume']

            for col in volume_columns:
                if col in data.columns:
                    logger.info(f"✅ 找到成交量列: {col}")
                    return data[col].sum()

            # 如果都没找到，記錄警告並返回0
            logger.warning(f"⚠️ 未找到成交量列，可用列: {list(data.columns)}")
            return 0

        except Exception as e:
            logger.error(f"❌ 獲取成交量失败: {e}")
            return 0

    def _try_fallback_sources(self, symbol: str, start_date: str, end_date: str) -> str:
        """嘗試備用數據源 - 避免遞歸調用"""
        logger.error(f"🔄 {self.current_source.value}失败，嘗試備用數據源...")

        # 備用數據源優先級: AKShare > Tushare > BaoStock
        fallback_order = [
            ChinaDataSource.AKSHARE,
            ChinaDataSource.TUSHARE,
            ChinaDataSource.BAOSTOCK
        ]

        for source in fallback_order:
            if source != self.current_source and source in self.available_sources:
                try:
                    logger.info(f"🔄 嘗試備用數據源: {source.value}")

                    # 直接調用具體的數據源方法，避免遞歸
                    if source == ChinaDataSource.TUSHARE:
                        result = self._get_tushare_data(symbol, start_date, end_date)
                    elif source == ChinaDataSource.AKSHARE:
                        result = self._get_akshare_data(symbol, start_date, end_date)
                    elif source == ChinaDataSource.BAOSTOCK:
                        result = self._get_baostock_data(symbol, start_date, end_date)
                    else:
                        logger.warning(f"⚠️ 未知數據源: {source.value}")
                        continue

                    if "❌" not in result:
                        logger.info(f"✅ 備用數據源{source.value}獲取成功")
                        return result
                    else:
                        logger.warning(f"⚠️ 備用數據源{source.value}返回錯誤結果")

                except Exception as e:
                    logger.error(f"❌ 備用數據源{source.value}也失败: {e}")
                    continue
        
        return f"❌ 所有數據源都無法獲取{symbol}的數據"
    
    def get_stock_info(self, symbol: str) -> Dict:
        """獲取股票基本信息，支持降級機制"""
        logger.info(f"📊 [股票信息] 開始獲取{symbol}基本信息...")

        # 首先嘗試當前數據源
        try:
            if self.current_source == ChinaDataSource.TUSHARE:
                from .interface import get_china_stock_info_tushare
                info_str = get_china_stock_info_tushare(symbol)
                result = self._parse_stock_info_string(info_str, symbol)

                # 檢查是否獲取到有效信息
                if result.get('name') and result['name'] != f'股票{symbol}':
                    logger.info(f"✅ [股票信息] Tushare成功獲取{symbol}信息")
                    return result
                else:
                    logger.warning(f"⚠️ [股票信息] Tushare返回無效信息，嘗試降級...")
                    return self._try_fallback_stock_info(symbol)
            else:
                adapter = self.get_data_adapter()
                if adapter and hasattr(adapter, 'get_stock_info'):
                    result = adapter.get_stock_info(symbol)
                    if result.get('name') and result['name'] != f'股票{symbol}':
                        logger.info(f"✅ [股票信息] {self.current_source.value}成功獲取{symbol}信息")
                        return result
                    else:
                        logger.warning(f"⚠️ [股票信息] {self.current_source.value}返回無效信息，嘗試降級...")
                        return self._try_fallback_stock_info(symbol)
                else:
                    logger.warning(f"⚠️ [股票信息] {self.current_source.value}不支持股票信息獲取，嘗試降級...")
                    return self._try_fallback_stock_info(symbol)

        except Exception as e:
            logger.error(f"❌ [股票信息] {self.current_source.value}獲取失败: {e}")
            return self._try_fallback_stock_info(symbol)

    def _try_fallback_stock_info(self, symbol: str) -> Dict:
        """嘗試使用備用數據源獲取股票基本信息"""
        logger.info(f"🔄 [股票信息] {self.current_source.value}失败，嘗試備用數據源...")

        # 獲取所有可用數據源
        available_sources = self.available_sources.copy()

        # 移除當前數據源
        if self.current_source.value in available_sources:
            available_sources.remove(self.current_source.value)

        # 嘗試所有備用數據源
        for source_name in available_sources:
            try:
                source = ChinaDataSource(source_name)
                logger.info(f"🔄 [股票信息] 嘗試備用數據源: {source_name}")

                # 根據數據源類型獲取股票信息
                if source == ChinaDataSource.TUSHARE:
                    from .interface import get_china_stock_info_tushare
                    info_str = get_china_stock_info_tushare(symbol)
                    result = self._parse_stock_info_string(info_str, symbol)
                elif source == ChinaDataSource.AKSHARE:
                    result = self._get_akshare_stock_info(symbol)
                elif source == ChinaDataSource.BAOSTOCK:
                    result = self._get_baostock_stock_info(symbol)
                else:
                    # 嘗試通用適配器
                    original_source = self.current_source
                    self.current_source = source
                    adapter = self.get_data_adapter()
                    self.current_source = original_source

                    if adapter and hasattr(adapter, 'get_stock_info'):
                        result = adapter.get_stock_info(symbol)
                    else:
                        logger.warning(f"⚠️ [股票信息] {source_name}不支持股票信息獲取")
                        continue

                # 檢查是否獲取到有效信息
                if result.get('name') and result['name'] != f'股票{symbol}':
                    logger.info(f"✅ [股票信息] 備用數據源{source_name}成功獲取{symbol}信息")
                    return result
                else:
                    logger.warning(f"⚠️ [股票信息] 備用數據源{source_name}返回無效信息")

            except Exception as e:
                logger.error(f"❌ [股票信息] 備用數據源{source_name}失败: {e}")
                continue

        # 所有數據源都失败，返回默認值
        logger.error(f"❌ [股票信息] 所有數據源都無法獲取{symbol}的基本信息")
        return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'unknown'}

    def _get_akshare_stock_info(self, symbol: str) -> Dict:
        """使用AKShare獲取股票基本信息"""
        try:
            import akshare as ak

            # 嘗試獲取個股信息
            stock_info = ak.stock_individual_info_em(symbol=symbol)

            if stock_info is not None and not stock_info.empty:
                # 轉換為字典格式
                info = {'symbol': symbol, 'source': 'akshare'}

                # 提取股票名稱
                name_row = stock_info[stock_info['item'] == '股票簡稱']
                if not name_row.empty:
                    info['name'] = name_row['value'].iloc[0]
                else:
                    info['name'] = f'股票{symbol}'

                # 提取其他信息
                info['area'] = '未知'  # AKShare没有地区信息
                info['industry'] = '未知'  # 可以通過其他API獲取
                info['market'] = '未知'  # 可以根據股票代碼推斷
                info['list_date'] = '未知'  # 可以通過其他API獲取

                return info
            else:
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'akshare'}

        except Exception as e:
            logger.error(f"❌ [股票信息] AKShare獲取失败: {e}")
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'akshare', 'error': str(e)}

    def _get_baostock_stock_info(self, symbol: str) -> Dict:
        """使用BaoStock獲取股票基本信息"""
        try:
            import baostock as bs

            # 轉換股票代碼格式
            if symbol.startswith('6'):
                bs_code = f"sh.{symbol}"
            else:
                bs_code = f"sz.{symbol}"

            # 登錄BaoStock
            lg = bs.login()
            if lg.error_code != '0':
                logger.error(f"❌ [股票信息] BaoStock登錄失败: {lg.error_msg}")
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'baostock'}

            # 查詢股票基本信息
            rs = bs.query_stock_basic(code=bs_code)
            if rs.error_code != '0':
                bs.logout()
                logger.error(f"❌ [股票信息] BaoStock查詢失败: {rs.error_msg}")
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'baostock'}

            # 解析結果
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            # 登出
            bs.logout()

            if data_list:
                # BaoStock返回格式: [code, code_name, ipoDate, outDate, type, status]
                info = {'symbol': symbol, 'source': 'baostock'}
                info['name'] = data_list[0][1]  # code_name
                info['area'] = '未知'  # BaoStock没有地区信息
                info['industry'] = '未知'  # BaoStock没有行業信息
                info['market'] = '未知'  # 可以根據股票代碼推斷
                info['list_date'] = data_list[0][2]  # ipoDate

                return info
            else:
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'baostock'}

        except Exception as e:
            logger.error(f"❌ [股票信息] BaoStock獲取失败: {e}")
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'baostock', 'error': str(e)}

    def _parse_stock_info_string(self, info_str: str, symbol: str) -> Dict:
        """解析股票信息字符串為字典"""
        try:
            info = {'symbol': symbol, 'source': self.current_source.value}
            lines = info_str.split('\n')
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if '股票名稱' in key:
                        info['name'] = value
                    elif '所屬行業' in key:
                        info['industry'] = value
                    elif '所屬地区' in key:
                        info['area'] = value
                    elif '上市市場' in key:
                        info['market'] = value
                    elif '上市日期' in key:
                        info['list_date'] = value
            
            return info
            
        except Exception as e:
            logger.error(f"⚠️ 解析股票信息失败: {e}")
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': self.current_source.value}


# 全局數據源管理器實例
_data_source_manager = None

def get_data_source_manager() -> DataSourceManager:
    """獲取全局數據源管理器實例"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager


def get_china_stock_data_unified(symbol: str, start_date: str, end_date: str) -> str:
    """
    統一的中國股票數據獲取接口
    自動使用配置的數據源，支持備用數據源

    Args:
        symbol: 股票代碼
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        str: 格式化的股票數據
    """
    from tradingagents.utils.logging_init import get_logger


    # 添加詳細的股票代碼追蹤日誌
    logger.info(f"🔍 [股票代碼追蹤] data_source_manager.get_china_stock_data_unified 接收到的股票代碼: '{symbol}' (類型: {type(symbol)})")
    logger.info(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(symbol))}")
    logger.info(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(symbol))}")

    manager = get_data_source_manager()
    logger.info(f"🔍 [股票代碼追蹤] 調用 manager.get_stock_data，傳入參數: symbol='{symbol}', start_date='{start_date}', end_date='{end_date}'")
    result = manager.get_stock_data(symbol, start_date, end_date)
    # 分析返回結果的詳細信息
    if result:
        lines = result.split('\n')
        data_lines = [line for line in lines if '2025-' in line and symbol in line]
        logger.info(f"🔍 [股票代碼追蹤] 返回結果統計: 总行數={len(lines)}, 數據行數={len(data_lines)}, 結果長度={len(result)}字符")
        logger.info(f"🔍 [股票代碼追蹤] 返回結果前500字符: {result[:500]}")
        if len(data_lines) > 0:
            logger.info(f"🔍 [股票代碼追蹤] 數據行示例: 第1行='{data_lines[0][:100]}', 最後1行='{data_lines[-1][:100]}'")
    else:
        logger.info(f"🔍 [股票代碼追蹤] 返回結果: None")
    return result


def get_china_stock_info_unified(symbol: str) -> Dict:
    """
    統一的中國股票信息獲取接口
    
    Args:
        symbol: 股票代碼
        
    Returns:
        Dict: 股票基本信息
    """
    manager = get_data_source_manager()
    return manager.get_stock_info(symbol)


# 全局數據源管理器實例
_data_source_manager = None

def get_data_source_manager() -> DataSourceManager:
    """獲取全局數據源管理器實例"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager
