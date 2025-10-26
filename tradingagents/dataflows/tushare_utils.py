#!/usr/bin/env python3
"""
Tushare數據源工具類
提供A股市場數據獲取功能，包括實時行情、歷史數據、財務數據等
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union
import warnings
import time

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')
warnings.filterwarnings('ignore')

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger

# 導入緩存管理器
try:
    from .cache_manager import get_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("⚠️ 緩存管理器不可用")

# 導入Tushare
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    logger.error("❌ Tushare庫未安裝，請運行: pip install tushare")


class TushareProvider:
    """Tushare數據提供器"""
    
    def __init__(self, token: str = None, enable_cache: bool = True):
        """
        初始化Tushare提供器
        
        Args:
            token: Tushare API token
            enable_cache: 是否啟用緩存
        """
        self.connected = False
        self.enable_cache = enable_cache and CACHE_AVAILABLE
        self.api = None
        
        # 初始化緩存管理器
        self.cache_manager = None
        if self.enable_cache:
            try:
                from .cache_manager import get_cache

                self.cache_manager = get_cache()
            except Exception as e:
                logger.warning(f"⚠️ 緩存管理器初始化失败: {e}")
                self.enable_cache = False

        # 獲取API token（使用强健的配置解析）
        if not token:
            try:
                from ..config.env_utils import parse_str_env
                token = parse_str_env('TUSHARE_TOKEN', '')
            except ImportError:
                # 回退到原始方法
                token = os.getenv('TUSHARE_TOKEN', '')

        if not token:
            logger.warning("⚠️ 未找到Tushare API token，請設置TUSHARE_TOKEN環境變量")
            return

        # 初始化Tushare API
        if TUSHARE_AVAILABLE:
            try:
                ts.set_token(token)
                self.api = ts.pro_api()
                self.connected = True
                logger.info("✅ Tushare API連接成功")
            except Exception as e:
                logger.error(f"❌ Tushare API連接失败: {e}")
        else:
            logger.error("❌ Tushare庫不可用")
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        獲取A股股票列表
        
        Returns:
            DataFrame: 股票列表數據
        """
        if not self.connected:
            logger.error(f"❌ Tushare未連接")
            return pd.DataFrame()
        
        try:
            # 嘗試從緩存獲取
            if self.enable_cache:
                cache_key = self.cache_manager.find_cached_stock_data(
                    symbol="tushare_stock_list",
                    max_age_hours=24  # 股票列表緩存24小時
                )
                
                if cache_key:
                    cached_data = self.cache_manager.load_stock_data(cache_key)
                    if cached_data is not None:
                        # 檢查是否為DataFrame且不為空
                        if hasattr(cached_data, 'empty') and not cached_data.empty:
                            logger.info(f"📦 從緩存獲取股票列表: {len(cached_data)}條")
                            return cached_data
                        elif isinstance(cached_data, str) and cached_data.strip():
                            logger.info(f"📦 從緩存獲取股票列表: 字符串格式")
                            return cached_data
            
            logger.info(f"🔄 從Tushare獲取A股股票列表...")
            
            # 獲取股票基本信息
            stock_list = self.api.stock_basic(
                exchange='',
                list_status='L',  # 上市狀態
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            
            if stock_list is not None and not stock_list.empty:
                logger.info(f"✅ 獲取股票列表成功: {len(stock_list)}條")
                
                # 緩存數據
                if self.enable_cache and self.cache_manager:
                    try:
                        cache_key = self.cache_manager.save_stock_data(
                            symbol="tushare_stock_list",
                            data=stock_list,
                            data_source="tushare"
                        )
                        logger.info(f"💾 A股股票列表已緩存: tushare_stock_list (tushare) -> {cache_key}")
                    except Exception as e:
                        logger.error(f"⚠️ 緩存保存失败: {e}")
                
                return stock_list
            else:
                logger.warning(f"⚠️ Tushare返回空數據")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ 獲取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_stock_daily(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        獲取股票日線數據
        
        Args:
            symbol: 股票代碼（如：000001.SZ）
            start_date: 開始日期（YYYYMMDD）
            end_date: 結束日期（YYYYMMDD）
            
        Returns:
            DataFrame: 日線數據
        """
        # 記錄詳細的調用信息
        logger.info(f"🔍 [Tushare詳細日誌] get_stock_daily 開始執行")
        logger.info(f"🔍 [Tushare詳細日誌] 輸入參數: symbol='{symbol}', start_date='{start_date}', end_date='{end_date}'")
        logger.info(f"🔍 [Tushare詳細日誌] 連接狀態: {self.connected}")
        logger.info(f"🔍 [Tushare詳細日誌] API對象: {type(self.api).__name__ if self.api else 'None'}")

        if not self.connected:
            logger.error(f"❌ [Tushare詳細日誌] Tushare未連接，無法獲取數據")
            return pd.DataFrame()

        try:
            # 標準化股票代碼
            logger.info(f"🔍 [股票代碼追蹤] get_stock_daily 調用 _normalize_symbol，傳入參數: '{symbol}'")
            ts_code = self._normalize_symbol(symbol)
            logger.info(f"🔍 [股票代碼追蹤] _normalize_symbol 返回結果: '{ts_code}'")

            # 設置默認日期
            original_start = start_date
            original_end = end_date

            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
                logger.info(f"🔍 [Tushare詳細日誌] 結束日期為空，設置為當前日期: {end_date}")
            else:
                end_date = end_date.replace('-', '')
                logger.info(f"🔍 [Tushare詳細日誌] 結束日期轉換: '{original_end}' -> '{end_date}'")

            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
                logger.info(f"🔍 [Tushare詳細日誌] 開始日期為空，設置為一年前: {start_date}")
            else:
                start_date = start_date.replace('-', '')
                logger.info(f"🔍 [Tushare詳細日誌] 開始日期轉換: '{original_start}' -> '{start_date}'")

            logger.info(f"🔄 從Tushare獲取{ts_code}數據 ({start_date} 到 {end_date})...")
            logger.info(f"🔍 [股票代碼追蹤] 調用 Tushare API daily，傳入參數: ts_code='{ts_code}', start_date='{start_date}', end_date='{end_date}'")

            # 記錄API調用前的狀態
            api_start_time = time.time()
            logger.info(f"🔍 [Tushare詳細日誌] API調用開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")

            # 獲取日線數據
            try:
                data = self.api.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                api_duration = time.time() - api_start_time
                logger.info(f"🔍 [Tushare詳細日誌] API調用完成，耗時: {api_duration:.3f}秒")

            except Exception as api_error:
                api_duration = time.time() - api_start_time
                logger.error(f"❌ [Tushare詳細日誌] API調用異常，耗時: {api_duration:.3f}秒")
                logger.error(f"❌ [Tushare詳細日誌] API異常類型: {type(api_error).__name__}")
                logger.error(f"❌ [Tushare詳細日誌] API異常信息: {str(api_error)}")
                raise api_error

            # 詳細記錄返回數據的信息
            logger.info(f"🔍 [股票代碼追蹤] Tushare API daily 返回數據形狀: {data.shape if data is not None and hasattr(data, 'shape') else 'None'}")
            logger.info(f"🔍 [Tushare詳細日誌] 返回數據類型: {type(data)}")

            if data is not None:
                logger.info(f"🔍 [Tushare詳細日誌] 數據是否為空: {data.empty}")
                if not data.empty:
                    logger.info(f"🔍 [Tushare詳細日誌] 數據列名: {list(data.columns)}")
                    logger.info(f"🔍 [Tushare詳細日誌] 數據索引類型: {type(data.index)}")
                    if 'ts_code' in data.columns:
                        unique_codes = data['ts_code'].unique()
                        logger.info(f"🔍 [股票代碼追蹤] 返回數據中的ts_code: {unique_codes}")
                    if 'trade_date' in data.columns:
                        date_range = f"{data['trade_date'].min()} 到 {data['trade_date'].max()}"
                        logger.info(f"🔍 [Tushare詳細日誌] 數據日期範围: {date_range}")
                else:
                    logger.warning(f"⚠️ [Tushare詳細日誌] 返回的DataFrame為空")
            else:
                logger.warning(f"⚠️ [Tushare詳細日誌] 返回數據為None")

            if data is not None and not data.empty:
                # 數據預處理
                logger.info(f"🔍 [Tushare詳細日誌] 開始數據預處理...")
                data = data.sort_values('trade_date')
                data['trade_date'] = pd.to_datetime(data['trade_date'])

                # 計算前複權價格（基於pct_chg重新計算連续價格）
                logger.info(f"🔍 [Tushare詳細日誌] 開始計算前複權價格...")
                data = self._calculate_forward_adjusted_prices(data)
                logger.info(f"🔍 [Tushare詳細日誌] 前複權價格計算完成")

                logger.info(f"🔍 [Tushare詳細日誌] 數據預處理完成")

                logger.info(f"✅ 獲取{ts_code}數據成功: {len(data)}條")

                # 緩存數據
                if self.enable_cache and self.cache_manager:
                    try:
                        logger.info(f"🔍 [Tushare詳細日誌] 開始緩存數據...")
                        cache_key = self.cache_manager.save_stock_data(
                            symbol=symbol,
                            data=data,
                            data_source="tushare"
                        )
                        logger.info(f"💾 A股歷史數據已緩存: {symbol} (tushare) -> {cache_key}")
                        logger.info(f"🔍 [Tushare詳細日誌] 數據緩存完成")
                    except Exception as cache_error:
                        logger.error(f"⚠️ 緩存保存失败: {cache_error}")
                        logger.error(f"⚠️ [Tushare詳細日誌] 緩存異常類型: {type(cache_error).__name__}")

                logger.info(f"🔍 [Tushare詳細日誌] get_stock_daily 執行成功，返回數據")
                return data
            else:
                logger.warning(f"⚠️ Tushare返回空數據: {ts_code}")
                logger.warning(f"⚠️ [Tushare詳細日誌] 空數據詳情: data={data}, empty={data.empty if data is not None else 'N/A'}")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"❌ 獲取{symbol}數據失败: {e}")
            logger.error(f"❌ [Tushare詳細日誌] 異常類型: {type(e).__name__}")
            logger.error(f"❌ [Tushare詳細日誌] 異常信息: {str(e)}")
            import traceback
            logger.error(f"❌ [Tushare詳細日誌] 異常堆棧: {traceback.format_exc()}")
            return pd.DataFrame()

    def _calculate_forward_adjusted_prices(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        基於pct_chg計算前複權價格

        Tushare的daily接口返回除權價格，在除權日會出現價格跳躍。
        使用pct_chg（涨跌幅）重新計算連续的前複權價格，確保價格序列的連续性。

        Args:
            data: 包含除權價格和pct_chg的DataFrame

        Returns:
            DataFrame: 包含前複權價格的數據
        """
        if data.empty or 'pct_chg' not in data.columns:
            logger.warning("⚠️ 數據為空或缺少pct_chg列，無法計算前複權價格")
            return data

        try:
            # 複制數據避免修改原始數據
            adjusted_data = data.copy()

            # 確保數據按日期排序
            adjusted_data = adjusted_data.sort_values('trade_date').reset_index(drop=True)

            # 保存原始價格列（用於對比）
            adjusted_data['close_raw'] = adjusted_data['close'].copy()
            adjusted_data['open_raw'] = adjusted_data['open'].copy()
            adjusted_data['high_raw'] = adjusted_data['high'].copy()
            adjusted_data['low_raw'] = adjusted_data['low'].copy()

            # 從最新的收盘價開始，向前計算前複權價格
            # 使用最後一天的收盘價作為基準
            latest_close = float(adjusted_data.iloc[-1]['close'])

            # 計算前複權收盘價
            adjusted_closes = [latest_close]

            # 從倒數第二天開始向前計算
            for i in range(len(adjusted_data) - 2, -1, -1):
                pct_change = float(adjusted_data.iloc[i + 1]['pct_chg']) / 100.0  # 轉換為小數

                # 前一天的前複權收盘價 = 今天的前複權收盘價 / (1 + 今天的涨跌幅)
                prev_close = adjusted_closes[0] / (1 + pct_change)
                adjusted_closes.insert(0, prev_close)

            # 更新收盘價
            adjusted_data['close'] = adjusted_closes

            # 計算其他價格的調整比例
            for i in range(len(adjusted_data)):
                if adjusted_data.iloc[i]['close_raw'] != 0:  # 避免除零
                    # 計算調整比例
                    adjustment_ratio = adjusted_data.iloc[i]['close'] / adjusted_data.iloc[i]['close_raw']

                    # 應用調整比例到其他價格
                    adjusted_data.iloc[i, adjusted_data.columns.get_loc('open')] = adjusted_data.iloc[i]['open_raw'] * adjustment_ratio
                    adjusted_data.iloc[i, adjusted_data.columns.get_loc('high')] = adjusted_data.iloc[i]['high_raw'] * adjustment_ratio
                    adjusted_data.iloc[i, adjusted_data.columns.get_loc('low')] = adjusted_data.iloc[i]['low_raw'] * adjustment_ratio

            # 添加標記表示這是前複權價格
            adjusted_data['price_type'] = 'forward_adjusted'

            logger.info(f"✅ 前複權價格計算完成，數據條數: {len(adjusted_data)}")
            logger.info(f"📊 價格調整範围: 最早調整比例 {adjusted_data.iloc[0]['close'] / adjusted_data.iloc[0]['close_raw']:.4f}")

            return adjusted_data

        except Exception as e:
            logger.error(f"❌ 前複權價格計算失败: {e}")
            logger.error(f"❌ 返回原始數據")
            return data
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        獲取股票基本信息
        
        Args:
            symbol: 股票代碼
            
        Returns:
            Dict: 股票基本信息
        """
        if not self.connected:
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'unknown'}
        
        try:
            logger.info(f"🔍 [股票代碼追蹤] get_stock_info 調用 _normalize_symbol，傳入參數: '{symbol}'")
            ts_code = self._normalize_symbol(symbol)
            logger.info(f"🔍 [股票代碼追蹤] _normalize_symbol 返回結果: '{ts_code}'")

            # 獲取股票基本信息
            logger.info(f"🔍 [股票代碼追蹤] 調用 Tushare API stock_basic，傳入參數: ts_code='{ts_code}'")
            basic_info = self.api.stock_basic(
                ts_code=ts_code,
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )

            logger.info(f"🔍 [股票代碼追蹤] Tushare API stock_basic 返回數據形狀: {basic_info.shape if basic_info is not None and hasattr(basic_info, 'shape') else 'None'}")
            if basic_info is not None and not basic_info.empty:
                logger.info(f"🔍 [股票代碼追蹤] 返回數據內容: {basic_info.to_dict('records')}")
            
            if basic_info is not None and not basic_info.empty:
                info = basic_info.iloc[0]
                return {
                    'symbol': symbol,
                    'ts_code': info['ts_code'],
                    'name': info['name'],
                    'area': info.get('area', ''),
                    'industry': info.get('industry', ''),
                    'market': info.get('market', ''),
                    'list_date': info.get('list_date', ''),
                    'source': 'tushare'
                }
            else:
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'unknown'}
                
        except Exception as e:
            logger.error(f"❌ 獲取{symbol}股票信息失败: {e}")
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'unknown'}
    
    def get_financial_data(self, symbol: str, period: str = "20231231") -> Dict:
        """
        獲取財務數據
        
        Args:
            symbol: 股票代碼
            period: 報告期（YYYYMMDD）
            
        Returns:
            Dict: 財務數據
        """
        if not self.connected:
            return {}
        
        try:
            ts_code = self._normalize_symbol(symbol)
            
            financials = {}
            
            # 獲取資產负债表
            try:
                balance_sheet = self.api.balancesheet(
                    ts_code=ts_code,
                    period=period,
                    fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_assets,total_liab,total_hldr_eqy_exc_min_int'
                )
                financials['balance_sheet'] = balance_sheet.to_dict('records') if balance_sheet is not None and not balance_sheet.empty else []
            except Exception as e:
                logger.error(f"⚠️ 獲取資產负债表失败: {e}")
                financials['balance_sheet'] = []
            
            # 獲取利润表
            try:
                income_statement = self.api.income(
                    ts_code=ts_code,
                    period=period,
                    fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_revenue,total_cogs,operate_profit,total_profit,n_income'
                )
                financials['income_statement'] = income_statement.to_dict('records') if income_statement is not None and not income_statement.empty else []
            except Exception as e:
                logger.error(f"⚠️ 獲取利润表失败: {e}")
                financials['income_statement'] = []
            
            # 獲取現金流量表
            try:
                cash_flow = self.api.cashflow(
                    ts_code=ts_code,
                    period=period,
                    fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,net_profit,finan_exp,c_fr_sale_sg,c_paid_goods_s'
                )
                financials['cash_flow'] = cash_flow.to_dict('records') if cash_flow is not None and not cash_flow.empty else []
            except Exception as e:
                logger.error(f"⚠️ 獲取現金流量表失败: {e}")
                financials['cash_flow'] = []
            
            return financials
            
        except Exception as e:
            logger.error(f"❌ 獲取{symbol}財務數據失败: {e}")
            return {}
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        標準化股票代碼為Tushare格式

        Args:
            symbol: 原始股票代碼

        Returns:
            str: Tushare格式的股票代碼
        """
        # 添加詳細的股票代碼追蹤日誌
        logger.info(f"🔍 [股票代碼追蹤] _normalize_symbol 接收到的原始股票代碼: '{symbol}' (類型: {type(symbol)})")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(symbol))}")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(symbol))}")

        original_symbol = symbol

        # 移除可能的前缀
        symbol = symbol.replace('sh.', '').replace('sz.', '')
        if symbol != original_symbol:
            logger.info(f"🔍 [股票代碼追蹤] 移除前缀後: '{original_symbol}' -> '{symbol}'")

        # 如果已經是Tushare格式，直接返回
        if '.' in symbol:
            logger.info(f"🔍 [股票代碼追蹤] 已經是Tushare格式，直接返回: '{symbol}'")
            return symbol

        # 根據代碼判斷交易所
        if symbol.startswith('6'):
            result = f"{symbol}.SH"  # 上海證券交易所
            logger.info(f"🔍 [股票代碼追蹤] 上海證券交易所: '{symbol}' -> '{result}'")
            return result
        elif symbol.startswith(('0', '3')):
            result = f"{symbol}.SZ"  # 深圳證券交易所
            logger.info(f"🔍 [股票代碼追蹤] 深圳證券交易所: '{symbol}' -> '{result}'")
            return result
        elif symbol.startswith('8'):
            result = f"{symbol}.BJ"  # 北京證券交易所
            logger.info(f"🔍 [股票代碼追蹤] 北京證券交易所: '{symbol}' -> '{result}'")
            return result
        else:
            # 默認深圳
            result = f"{symbol}.SZ"
            logger.info(f"🔍 [股票代碼追蹤] 默認深圳證券交易所: '{symbol}' -> '{result}'")
            return result
    
    def search_stocks(self, keyword: str) -> pd.DataFrame:
        """
        搜索股票
        
        Args:
            keyword: 搜索關键詞
            
        Returns:
            DataFrame: 搜索結果
        """
        try:
            stock_list = self.get_stock_list()
            
            if stock_list.empty:
                return pd.DataFrame()
            
            # 按名稱和代碼搜索
            mask = (
                stock_list['name'].str.contains(keyword, na=False) |
                stock_list['symbol'].str.contains(keyword, na=False) |
                stock_list['ts_code'].str.contains(keyword, na=False)
            )
            
            results = stock_list[mask]
            logger.debug(f"🔍 搜索'{keyword}'找到{len(results)}只股票")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 搜索股票失败: {e}")
            return pd.DataFrame()


# 全局提供器實例
_tushare_provider = None

def get_tushare_provider() -> TushareProvider:
    """獲取全局Tushare提供器實例"""
    global _tushare_provider
    if _tushare_provider is None:
        _tushare_provider = TushareProvider()
    return _tushare_provider


def get_china_stock_data_tushare(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    獲取中國股票數據的便捷函數（Tushare數據源）
    
    Args:
        symbol: 股票代碼
        start_date: 開始日期
        end_date: 結束日期
        
    Returns:
        DataFrame: 股票數據
    """
    provider = get_tushare_provider()
    return provider.get_stock_daily(symbol, start_date, end_date)


def get_china_stock_info_tushare(symbol: str) -> Dict:
    """
    獲取中國股票信息的便捷函數（Tushare數據源）
    
    Args:
        symbol: 股票代碼
        
    Returns:
        Dict: 股票信息
    """
    provider = get_tushare_provider()
    return provider.get_stock_info(symbol)
