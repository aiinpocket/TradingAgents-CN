#!/usr/bin/env python3
"""
Tushare數據適配器
提供統一的中國股票數據接口，支持緩存和錯誤處理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

# 導入Tushare工具
try:
    from .tushare_utils import get_tushare_provider
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    logger.warning("❌ Tushare工具不可用")

# 導入緩存管理器
try:
    from .cache_manager import get_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("⚠️ 緩存管理器不可用")


class TushareDataAdapter:
    """Tushare數據適配器"""
    
    def __init__(self, enable_cache: bool = True):
        """
        初始化Tushare數據適配器
        
        Args:
            enable_cache: 是否啟用緩存
        """
        self.enable_cache = enable_cache and CACHE_AVAILABLE
        self.provider = None
        
        # 初始化緩存管理器
        self.cache_manager = None
        if self.enable_cache:
            try:
                from .cache_manager import get_cache
                self.cache_manager = get_cache()
            except Exception as e:
                logger.warning(f"⚠️ 緩存管理器初始化失败: {e}")
                self.enable_cache = False

        # 初始化Tushare提供器
        if TUSHARE_AVAILABLE:
            try:
                self.provider = get_tushare_provider()
                if self.provider.connected:
                    logger.info("📊 Tushare數據適配器初始化完成")
                else:
                    logger.warning("⚠️ Tushare連接失败，數據適配器功能受限")
            except Exception as e:
                logger.warning(f"⚠️ Tushare提供器初始化失败: {e}")
        else:
            logger.error("❌ Tushare不可用")
    
    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None, 
                      data_type: str = "daily") -> pd.DataFrame:
        """
        獲取股票數據
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            data_type: 數據類型 ("daily", "realtime")
            
        Returns:
            DataFrame: 股票數據
        """
        if not self.provider or not self.provider.connected:
            logger.error("❌ Tushare數據源不可用")
            return pd.DataFrame()

        try:
            logger.debug(f"🔄 獲取{symbol}數據 (類型: {data_type})...")

            # 添加詳細的股票代碼追蹤日誌
            logger.info(f"🔍 [股票代碼追蹤] TushareAdapter.get_stock_data 接收到的股票代碼: '{symbol}' (類型: {type(symbol)})")
            logger.info(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(symbol))}")
            logger.info(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(symbol))}")

            if data_type == "daily":
                logger.info(f"🔍 [股票代碼追蹤] 調用 _get_daily_data，傳入參數: symbol='{symbol}'")
                return self._get_daily_data(symbol, start_date, end_date)
            elif data_type == "realtime":
                return self._get_realtime_data(symbol)
            else:
                logger.error(f"❌ 不支持的數據類型: {data_type}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ 獲取{symbol}數據失败: {e}")
            return pd.DataFrame()
    
    def _get_daily_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """獲取日線數據"""

        # 記錄詳細的調用信息
        logger.info(f"🔍 [TushareAdapter詳細日誌] _get_daily_data 開始執行")
        logger.info(f"🔍 [TushareAdapter詳細日誌] 輸入參數: symbol='{symbol}', start_date='{start_date}', end_date='{end_date}'")
        logger.info(f"🔍 [TushareAdapter詳細日誌] 緩存啟用狀態: {self.enable_cache}")

        # 1. 嘗試從緩存獲取
        if self.enable_cache:
            try:
                logger.info(f"🔍 [TushareAdapter詳細日誌] 開始查找緩存數據...")
                cache_key = self.cache_manager.find_cached_stock_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    max_age_hours=24  # 日線數據緩存24小時
                )

                if cache_key:
                    logger.info(f"🔍 [TushareAdapter詳細日誌] 找到緩存键: {cache_key}")
                    cached_data = self.cache_manager.load_stock_data(cache_key)
                    if cached_data is not None:
                        # 檢查是否為DataFrame且不為空
                        if hasattr(cached_data, 'empty') and not cached_data.empty:
                            logger.debug(f"📦 從緩存獲取{symbol}數據: {len(cached_data)}條")
                            logger.info(f"🔍 [TushareAdapter詳細日誌] 緩存數據有效，確保標準化後返回")
                            # 確保緩存數據也經過標準化驗證（修複KeyError: 'volume'問題）
                            return self._validate_and_standardize_data(cached_data)
                        elif isinstance(cached_data, str) and cached_data.strip():
                            logger.debug(f"📦 從緩存獲取{symbol}數據: 字符串格式")
                            logger.info(f"🔍 [TushareAdapter詳細日誌] 緩存數據為字符串格式")
                            return cached_data
                        else:
                            logger.info(f"🔍 [TushareAdapter詳細日誌] 緩存數據無效: {type(cached_data)}")
                    else:
                        logger.info(f"🔍 [TushareAdapter詳細日誌] 緩存數據為None")
                else:
                    logger.info(f"🔍 [TushareAdapter詳細日誌] 未找到有效緩存")
            except Exception as e:
                logger.warning(f"⚠️ 緩存獲取失败: {e}")
                logger.warning(f"⚠️ [TushareAdapter詳細日誌] 緩存異常類型: {type(e).__name__}")
        else:
            logger.info(f"🔍 [TushareAdapter詳細日誌] 緩存未啟用，直接從API獲取")

        # 2. 從Tushare獲取數據
        logger.info(f"🔍 [股票代碼追蹤] _get_daily_data 調用 provider.get_stock_daily，傳入參數: symbol='{symbol}'")
        logger.info(f"🔍 [TushareAdapter詳細日誌] 開始調用Tushare Provider...")

        import time
        provider_start_time = time.time()
        data = self.provider.get_stock_daily(symbol, start_date, end_date)
        provider_duration = time.time() - provider_start_time

        logger.info(f"🔍 [TushareAdapter詳細日誌] Provider調用完成，耗時: {provider_duration:.3f}秒")
        logger.info(f"🔍 [股票代碼追蹤] adapter.get_stock_data 返回數據形狀: {data.shape if data is not None and hasattr(data, 'shape') else 'None'}")

        if data is not None and not data.empty:
            logger.debug(f"✅ 從Tushare獲取{symbol}數據成功: {len(data)}條")
            logger.info(f"🔍 [股票代碼追蹤] provider.get_stock_daily 返回數據形狀: {data.shape}")
            logger.info(f"🔍 [TushareAdapter詳細日誌] 數據獲取成功，開始檢查數據內容...")

            # 檢查數據中的股票代碼列
            if 'ts_code' in data.columns:
                unique_codes = data['ts_code'].unique()
                logger.info(f"🔍 [股票代碼追蹤] 返回數據中的股票代碼: {unique_codes}")
            if 'symbol' in data.columns:
                unique_symbols = data['symbol'].unique()
                logger.info(f"🔍 [股票代碼追蹤] 返回數據中的symbol: {unique_symbols}")

            logger.info(f"🔍 [TushareAdapter詳細日誌] 開始標準化數據...")
            standardized_data = self._standardize_data(data)
            logger.info(f"🔍 [TushareAdapter詳細日誌] 數據標準化完成")
            return standardized_data
        else:
            logger.warning(f"⚠️ Tushare返回空數據")
            logger.warning(f"⚠️ [TushareAdapter詳細日誌] 空數據詳情: data={data}, type={type(data)}")
            if data is not None:
                logger.warning(f"⚠️ [TushareAdapter詳細日誌] DataFrame為空: {data.empty}")
            return pd.DataFrame()
    
    def _get_realtime_data(self, symbol: str) -> pd.DataFrame:
        """獲取實時數據（使用最新日線數據）"""
        
        # Tushare免費版不支持實時數據，使用最新日線數據
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        data = self.provider.get_stock_daily(symbol, start_date, end_date)
        
        if data is not None and not data.empty:
            # 返回最新一條數據
            latest_data = data.tail(1)
            logger.debug(f"✅ 從Tushare獲取{symbol}最新數據")
            return self._standardize_data(latest_data)
        else:
            logger.warning(f"⚠️ 無法獲取{symbol}實時數據")
            return pd.DataFrame()
    
    def _validate_and_standardize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """驗證並標準化數據格式，增强版本（修複KeyError: 'volume'問題）"""
        if data.empty:
            logger.info("🔍 [數據標準化] 輸入數據為空，直接返回")
            return data

        try:
            logger.info(f"🔍 [數據標準化] 開始標準化數據，輸入列名: {list(data.columns)}")

            # 複制數據避免修改原始數據
            standardized = data.copy()

            # 列名映射
            column_mapping = {
                'trade_date': 'date',
                'ts_code': 'code',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume',  # 關键映射：vol -> volume
                'amount': 'amount',
                'pct_chg': 'pct_change',
                'change': 'change'
            }

            # 記錄映射過程
            mapped_columns = []

            # 重命名列
            for old_col, new_col in column_mapping.items():
                if old_col in standardized.columns:
                    standardized = standardized.rename(columns={old_col: new_col})
                    mapped_columns.append(f"{old_col}->{new_col}")
                    logger.debug(f"🔄 [數據標準化] 列映射: {old_col} -> {new_col}")

            logger.info(f"🔍 [數據標準化] 完成列映射: {mapped_columns}")

            # 驗證關键列是否存在，添加备用處理
            required_columns = ['volume', 'close', 'high', 'low']
            missing_columns = [col for col in required_columns if col not in standardized.columns]
            if missing_columns:
                logger.warning(f"⚠️ [數據標準化] 缺少關键列: {missing_columns}")
                self._add_fallback_columns(standardized, missing_columns, data)

            # 確保日期列存在且格式正確
            if 'date' in standardized.columns:
                standardized['date'] = pd.to_datetime(standardized['date'])
                standardized = standardized.sort_values('date')
                logger.debug("✅ [數據標準化] 日期列格式化完成")

            # 添加股票代碼列（如果不存在）
            if 'code' in standardized.columns and '股票代碼' not in standardized.columns:
                standardized['股票代碼'] = standardized['code'].str.replace('.SH', '').str.replace('.SZ', '').str.replace('.BJ', '')
                logger.debug("✅ [數據標準化] 股票代碼列添加完成")

            # 添加涨跌幅列（如果不存在）
            if 'pct_change' in standardized.columns and '涨跌幅' not in standardized.columns:
                standardized['涨跌幅'] = standardized['pct_change']
                logger.debug("✅ [數據標準化] 涨跌幅列添加完成")

            logger.info("✅ [數據標準化] 數據標準化完成")
            return standardized

        except Exception as e:
            logger.error(f"❌ [數據標準化] 數據標準化失败: {e}", exc_info=True)
            logger.error(f"❌ [數據標準化] 原始數據列名: {list(data.columns) if not data.empty else '空數據'}")
            return data

    def _add_fallback_columns(self, standardized: pd.DataFrame, missing_columns: list, original_data: pd.DataFrame):
        """為缺失的關键列添加备用值"""
        try:
            import numpy as np
            for col in missing_columns:
                if col == 'volume':
                    # 嘗試寻找可能的成交量列名
                    volume_candidates = ['vol', 'volume', 'turnover', 'trade_volume']
                    for candidate in volume_candidates:
                        if candidate in original_data.columns:
                            standardized['volume'] = original_data[candidate]
                            logger.info(f"✅ [數據標準化] 使用备用列 {candidate} 作為 volume")
                            break
                    else:
                        # 如果找不到任何成交量列，設置為0
                        standardized['volume'] = 0
                        logger.warning(f"⚠️ [數據標準化] 未找到成交量數據，設置為0")

                elif col in ['close', 'high', 'low', 'open']:
                    # 對於價格列，如果缺失則設置為NaN
                    if col not in standardized.columns:
                        standardized[col] = np.nan
                        logger.warning(f"⚠️ [數據標準化] 缺失價格列 {col}，設置為NaN")

        except Exception as e:
            logger.error(f"❌ [數據標準化] 添加备用列失败: {e}")

    def _standardize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """標準化數據格式 - 保持向後兼容性，調用增强版本"""
        return self._validate_and_standardize_data(data)
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        獲取股票基本信息
        
        Args:
            symbol: 股票代碼
            
        Returns:
            Dict: 股票基本信息
        """
        if not self.provider or not self.provider.connected:
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'unknown'}
        
        try:
            info = self.provider.get_stock_info(symbol)
            if info and info.get('name') and info.get('name') != f'股票{symbol}':
                logger.debug(f"✅ 從Tushare獲取{symbol}基本信息成功")
                return info
            else:
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'unknown'}

        except Exception as e:
            logger.error(f"❌ 獲取{symbol}股票信息失败: {e}")
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'unknown'}
    
    def search_stocks(self, keyword: str) -> pd.DataFrame:
        """
        搜索股票
        
        Args:
            keyword: 搜索關键詞
            
        Returns:
            DataFrame: 搜索結果
        """
        if not self.provider or not self.provider.connected:
            logger.error("❌ Tushare數據源不可用")
            return pd.DataFrame()

        try:
            results = self.provider.search_stocks(keyword)

            if results is not None and not results.empty:
                logger.debug(f"✅ 搜索'{keyword}'成功: {len(results)}條結果")
                return results
            else:
                logger.warning(f"⚠️ 未找到匹配'{keyword}'的股票")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"❌ 搜索股票失败: {e}")
            return pd.DataFrame()
    
    def get_fundamentals(self, symbol: str) -> str:
        """
        獲取基本面數據
        
        Args:
            symbol: 股票代碼
            
        Returns:
            str: 基本面分析報告
        """
        if not self.provider or not self.provider.connected:
            return f"❌ Tushare數據源不可用，無法獲取{symbol}基本面數據"
        
        try:
            logger.debug(f"📊 獲取{symbol}基本面數據...")

            # 獲取股票基本信息
            stock_info = self.get_stock_info(symbol)
            
            # 獲取財務數據
            financial_data = self.provider.get_financial_data(symbol)
            
            # 生成基本面分析報告
            report = self._generate_fundamentals_report(symbol, stock_info, financial_data)
            
            # 緩存基本面數據
            if self.enable_cache and self.cache_manager:
                try:
                    cache_key = self.cache_manager.save_fundamentals_data(
                        symbol=symbol,
                        fundamentals_data=report,
                        data_source="tushare_analysis"
                    )
                    logger.debug(f"💼 A股基本面數據已緩存: {symbol} (tushare_analysis) -> {cache_key}")
                except Exception as e:
                    logger.warning(f"⚠️ 基本面數據緩存失败: {e}")

            return report

        except Exception as e:
            logger.error(f"❌ 獲取{symbol}基本面數據失败: {e}")
            return f"❌ 獲取{symbol}基本面數據失败: {e}"
    
    def _generate_fundamentals_report(self, symbol: str, stock_info: Dict, financial_data: Dict) -> str:
        """生成基本面分析報告"""
        
        report = f"📊 {symbol} 基本面分析報告 (Tushare數據源)\n"
        report += "=" * 50 + "\n\n"
        
        # 基本信息
        report += "📋 基本信息\n"
        report += f"股票代碼: {symbol}\n"
        report += f"股票名稱: {stock_info.get('name', '未知')}\n"
        report += f"所屬地区: {stock_info.get('area', '未知')}\n"
        report += f"所屬行業: {stock_info.get('industry', '未知')}\n"
        report += f"上市市場: {stock_info.get('market', '未知')}\n"
        report += f"上市日期: {stock_info.get('list_date', '未知')}\n\n"
        
        # 財務數據
        if financial_data:
            report += "💰 財務數據\n"
            
            # 資產负债表
            balance_sheet = financial_data.get('balance_sheet', [])
            if balance_sheet:
                latest_balance = balance_sheet[0] if balance_sheet else {}
                report += f"总資產: {latest_balance.get('total_assets', 'N/A')}\n"
                report += f"总负债: {latest_balance.get('total_liab', 'N/A')}\n"
                report += f"股东權益: {latest_balance.get('total_hldr_eqy_exc_min_int', 'N/A')}\n"
            
            # 利润表
            income_statement = financial_data.get('income_statement', [])
            if income_statement:
                latest_income = income_statement[0] if income_statement else {}
                report += f"營業收入: {latest_income.get('total_revenue', 'N/A')}\n"
                report += f"營業利润: {latest_income.get('operate_profit', 'N/A')}\n"
                report += f"净利润: {latest_income.get('n_income', 'N/A')}\n"
            
            # 現金流量表
            cash_flow = financial_data.get('cash_flow', [])
            if cash_flow:
                latest_cash = cash_flow[0] if cash_flow else {}
                report += f"經營活動現金流: {latest_cash.get('c_fr_sale_sg', 'N/A')}\n"
        else:
            report += "💰 財務數據: 暂無數據\n"
        
        report += f"\n📅 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"📊 數據來源: Tushare\n"
        
        return report


# 全局適配器實例
_tushare_adapter = None

def get_tushare_adapter() -> TushareDataAdapter:
    """獲取全局Tushare數據適配器實例"""
    global _tushare_adapter
    if _tushare_adapter is None:
        _tushare_adapter = TushareDataAdapter()
    return _tushare_adapter


def get_china_stock_data_tushare_adapter(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    獲取中國股票數據的便捷函數（Tushare適配器）
    
    Args:
        symbol: 股票代碼
        start_date: 開始日期
        end_date: 結束日期
        
    Returns:
        DataFrame: 股票數據
    """
    adapter = get_tushare_adapter()
    return adapter.get_stock_data(symbol, start_date, end_date)


def get_china_stock_info_tushare_adapter(symbol: str) -> Dict:
    """
    獲取中國股票信息的便捷函數（Tushare適配器）
    
    Args:
        symbol: 股票代碼
        
    Returns:
        Dict: 股票信息
    """
    adapter = get_tushare_adapter()
    return adapter.get_stock_info(symbol)
