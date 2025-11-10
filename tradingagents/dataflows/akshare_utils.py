#!/usr/bin/env python3
"""
AKShare數據源工具
提供AKShare數據獲取的統一接口
"""

import pandas as pd
from typing import Optional, Dict, Any
import warnings
from datetime import datetime

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')
warnings.filterwarnings('ignore')

class AKShareProvider:
    """AKShare數據提供器"""

    def __init__(self):
        """初始化AKShare提供器"""
        try:
            import akshare as ak
            self.ak = ak
            self.connected = True

            # 設置更長的超時時間
            self._configure_timeout()

            logger.info(f"✅ AKShare初始化成功")
        except ImportError:
            self.ak = None
            self.connected = False
            logger.error(f"❌ AKShare未安裝")

    def _configure_timeout(self):
        """配置AKShare的超時設置"""
        try:
            import requests
            import socket

            # 設置更長的超時時間
            socket.setdefaulttimeout(60)  # 60秒超時

            # 如果AKShare使用requests，設置默認超時
            if hasattr(requests, 'adapters'):
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry

                # 創建重試策略
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )

                # 設置適配器
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session = requests.Session()
                session.mount("http://", adapter)
                session.mount("https://", adapter)

                logger.info(f"🔧 AKShare超時配置完成: 60秒超時，3次重試")

        except Exception as e:
            logger.error(f"⚠️ AKShare超時配置失败: {e}")
            logger.info(f"🔧 使用默認超時設置")
    
    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """獲取股票歷史數據"""
        if not self.connected:
            return None
        
        try:
            # 轉換股票代碼格式
            if len(symbol) == 6:
                symbol = symbol
            else:
                symbol = symbol.replace('.SZ', '').replace('.SS', '')
            
            # 獲取數據
            data = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace('-', '') if start_date else "20240101",
                end_date=end_date.replace('-', '') if end_date else "20241231",
                adjust=""
            )
            
            return data
            
        except Exception as e:
            logger.error(f"❌ AKShare獲取股票數據失败: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """獲取股票基本信息"""
        if not self.connected:
            return {}
        
        try:
            # 獲取股票基本信息
            stock_list = self.ak.stock_info_a_code_name()
            stock_info = stock_list[stock_list['code'] == symbol]
            
            if not stock_info.empty:
                return {
                    'symbol': symbol,
                    'name': stock_info.iloc[0]['name'],
                    'source': 'akshare'
                }
            else:
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'akshare'}
                
        except Exception as e:
            logger.error(f"❌ AKShare獲取股票信息失败: {e}")
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'akshare'}

    def get_hk_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        獲取港股歷史數據

        Args:
            symbol: 港股代碼 (如: 00700 或 0700.HK)
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)

        Returns:
            DataFrame: 港股歷史數據
        """
        if not self.connected:
            logger.error(f"❌ AKShare未連接")
            return None

        try:
            # 標準化港股代碼 - AKShare使用5位數字格式
            hk_symbol = self._normalize_hk_symbol_for_akshare(symbol)

            logger.info(f"🇭🇰 AKShare獲取港股數據: {hk_symbol} ({start_date} 到 {end_date})")

            # 格式化日期為AKShare需要的格式
            start_date_formatted = start_date.replace('-', '') if start_date else "20240101"
            end_date_formatted = end_date.replace('-', '') if end_date else "20241231"

            # 使用AKShare獲取港股歷史數據（帶超時保護）
            import threading

            result = [None]
            exception = [None]

            def fetch_hist_data():
                try:
                    result[0] = self.ak.stock_hk_hist(
                        symbol=hk_symbol,
                        period="daily",
                        start_date=start_date_formatted,
                        end_date=end_date_formatted,
                        adjust=""
                    )
                except Exception as e:
                    exception[0] = e

            # 啟動線程
            thread = threading.Thread(target=fetch_hist_data)
            thread.daemon = True
            thread.start()

            # 等待60秒
            thread.join(timeout=60)

            if thread.is_alive():
                # 超時了
                logger.warning(f"⚠️ AKShare港股歷史數據獲取超時（60秒）: {symbol}")
                raise Exception(f"AKShare港股歷史數據獲取超時（60秒）: {symbol}")
            elif exception[0]:
                # 有異常
                raise exception[0]
            else:
                # 成功
                data = result[0]

            if not data.empty:
                # 數據預處理
                data = data.reset_index()
                data['Symbol'] = symbol  # 保持原始格式

                # 重命名列以保持一致性
                column_mapping = {
                    '日期': 'Date',
                    '開盘': 'Open',
                    '收盘': 'Close',
                    '最高': 'High',
                    '最低': 'Low',
                    '成交量': 'Volume',
                    '成交額': 'Amount'
                }

                for old_col, new_col in column_mapping.items():
                    if old_col in data.columns:
                        data = data.rename(columns={old_col: new_col})

                logger.info(f"✅ AKShare港股數據獲取成功: {symbol}, {len(data)}條記錄")
                return data
            else:
                logger.warning(f"⚠️ AKShare港股數據為空: {symbol}")
                return None

        except Exception as e:
            logger.error(f"❌ AKShare獲取港股數據失败: {e}")
            return None

    def get_hk_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        獲取港股基本信息

        Args:
            symbol: 港股代碼

        Returns:
            Dict: 港股基本信息
        """
        if not self.connected:
            return {
                'symbol': symbol,
                'name': f'港股{symbol}',
                'currency': 'HKD',
                'exchange': 'HKG',
                'source': 'akshare_unavailable'
            }

        try:
            hk_symbol = self._normalize_hk_symbol_for_akshare(symbol)

            logger.info(f"🇭🇰 AKShare獲取港股信息: {hk_symbol}")

            # 嘗試獲取港股實時行情數據來獲取基本信息
            # 使用線程超時包裝（兼容Windows）
            import threading
            import time


            result = [None]
            exception = [None]

            def fetch_data():
                try:
                    result[0] = self.ak.stock_hk_spot_em()
                except Exception as e:
                    exception[0] = e

            # 啟動線程
            thread = threading.Thread(target=fetch_data)
            thread.daemon = True
            thread.start()

            # 等待60秒
            thread.join(timeout=60)

            if thread.is_alive():
                # 超時了
                logger.warning(f"⚠️ AKShare港股信息獲取超時（60秒），使用備用方案")
                raise Exception("AKShare港股信息獲取超時（60秒）")
            elif exception[0]:
                # 有異常
                raise exception[0]
            else:
                # 成功
                spot_data = result[0]

            # 查找對應的股票信息
            if not spot_data.empty:
                # 查找匹配的股票
                matching_stocks = spot_data[spot_data['代碼'].str.contains(hk_symbol[:5], na=False)]

                if not matching_stocks.empty:
                    stock_info = matching_stocks.iloc[0]
                    return {
                        'symbol': symbol,
                        'name': stock_info.get('名稱', f'港股{symbol}'),
                        'currency': 'HKD',
                        'exchange': 'HKG',
                        'latest_price': stock_info.get('最新價', None),
                        'source': 'akshare'
                    }

            # 如果没有找到，返回基本信息
            return {
                'symbol': symbol,
                'name': f'港股{symbol}',
                'currency': 'HKD',
                'exchange': 'HKG',
                'source': 'akshare'
            }

        except Exception as e:
            logger.error(f"❌ AKShare獲取港股信息失败: {e}")
            return {
                'symbol': symbol,
                'name': f'港股{symbol}',
                'currency': 'HKD',
                'exchange': 'HKG',
                'source': 'akshare_error',
                'error': str(e)
            }

    def _normalize_hk_symbol_for_akshare(self, symbol: str) -> str:
        """
        標準化港股代碼為AKShare格式

        Args:
            symbol: 原始港股代碼 (如: 0700.HK 或 700)

        Returns:
            str: AKShare格式的港股代碼 (如: 00700)
        """
        if not symbol:
            return symbol

        # 移除.HK後缀
        clean_symbol = symbol.replace('.HK', '').replace('.hk', '')

        # 確保是5位數字格式
        if clean_symbol.isdigit():
            return clean_symbol.zfill(5)

        return clean_symbol

    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        獲取股票財務數據
        
        Args:
            symbol: 股票代碼 (6位數字)
            
        Returns:
            Dict: 包含主要財務指標的財務數據
        """
        if not self.connected:
            logger.error(f"❌ AKShare未連接，無法獲取{symbol}財務數據")
            return {}
        
        try:
            logger.info(f"🔍 開始獲取{symbol}的AKShare財務數據")
            
            financial_data = {}
            
            # 1. 優先獲取主要財務指標
            try:
                logger.debug(f"📊 嘗試獲取{symbol}主要財務指標...")
                main_indicators = self.ak.stock_financial_abstract(symbol=symbol)
                if main_indicators is not None and not main_indicators.empty:
                    financial_data['main_indicators'] = main_indicators
                    logger.info(f"✅ 成功獲取{symbol}主要財務指標: {len(main_indicators)}條記錄")
                    logger.debug(f"主要財務指標列名: {list(main_indicators.columns)}")
                else:
                    logger.warning(f"⚠️ {symbol}主要財務指標為空")
            except Exception as e:
                logger.warning(f"❌ 獲取{symbol}主要財務指標失败: {e}")
            
            # 2. 嘗試獲取資產负债表（可能失败，降級為debug日誌）
            try:
                logger.debug(f"📊 嘗試獲取{symbol}資產负债表...")
                balance_sheet = self.ak.stock_balance_sheet_by_report_em(symbol=symbol)
                if balance_sheet is not None and not balance_sheet.empty:
                    financial_data['balance_sheet'] = balance_sheet
                    logger.debug(f"✅ 成功獲取{symbol}資產负债表: {len(balance_sheet)}條記錄")
                else:
                    logger.debug(f"⚠️ {symbol}資產负债表為空")
            except Exception as e:
                logger.debug(f"❌ 獲取{symbol}資產负债表失败: {e}")
            
            # 3. 嘗試獲取利润表（可能失败，降級為debug日誌）
            try:
                logger.debug(f"📊 嘗試獲取{symbol}利润表...")
                income_statement = self.ak.stock_profit_sheet_by_report_em(symbol=symbol)
                if income_statement is not None and not income_statement.empty:
                    financial_data['income_statement'] = income_statement
                    logger.debug(f"✅ 成功獲取{symbol}利润表: {len(income_statement)}條記錄")
                else:
                    logger.debug(f"⚠️ {symbol}利润表為空")
            except Exception as e:
                logger.debug(f"❌ 獲取{symbol}利润表失败: {e}")
            
            # 4. 嘗試獲取現金流量表（可能失败，降級為debug日誌）
            try:
                logger.debug(f"📊 嘗試獲取{symbol}現金流量表...")
                cash_flow = self.ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
                if cash_flow is not None and not cash_flow.empty:
                    financial_data['cash_flow'] = cash_flow
                    logger.debug(f"✅ 成功獲取{symbol}現金流量表: {len(cash_flow)}條記錄")
                else:
                    logger.debug(f"⚠️ {symbol}現金流量表為空")
            except Exception as e:
                logger.debug(f"❌ 獲取{symbol}現金流量表失败: {e}")
            
            # 記錄最終結果
            if financial_data:
                logger.info(f"✅ AKShare財務數據獲取完成: {symbol}, 包含{len(financial_data)}個數據集")
                for key, value in financial_data.items():
                    if hasattr(value, '__len__'):
                        logger.info(f"  - {key}: {len(value)}條記錄")
            else:
                logger.warning(f"⚠️ 未能獲取{symbol}的任何AKShare財務數據")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"❌ AKShare獲取{symbol}財務數據失败: {e}")
            return {}

def get_akshare_provider() -> AKShareProvider:
    """獲取AKShare提供器實例"""
    return AKShareProvider()


# 便捷函數
def get_hk_stock_data_akshare(symbol: str, start_date: str = None, end_date: str = None) -> str:
    """
    使用AKShare獲取港股數據的便捷函數

    Args:
        symbol: 港股代碼
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        str: 格式化的港股數據
    """
    try:
        provider = get_akshare_provider()
        data = provider.get_hk_stock_data(symbol, start_date, end_date)

        if data is not None and not data.empty:
            return format_hk_stock_data_akshare(symbol, data, start_date, end_date)
        else:
            return f"❌ 無法獲取港股 {symbol} 的AKShare數據"

    except Exception as e:
        return f"❌ AKShare港股數據獲取失败: {e}"


def get_hk_stock_info_akshare(symbol: str) -> Dict[str, Any]:
    """
    使用AKShare獲取港股信息的便捷函數

    Args:
        symbol: 港股代碼

    Returns:
        Dict: 港股信息
    """
    try:
        provider = get_akshare_provider()
        return provider.get_hk_stock_info(symbol)
    except Exception as e:
        return {
            'symbol': symbol,
            'name': f'港股{symbol}',
            'currency': 'HKD',
            'exchange': 'HKG',
            'source': 'akshare_error',
            'error': str(e)
        }


def format_hk_stock_data_akshare(symbol: str, data: pd.DataFrame, start_date: str, end_date: str) -> str:
    """
    格式化AKShare港股數據為文本格式

    Args:
        symbol: 股票代碼
        data: 股票數據DataFrame
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        str: 格式化的股票數據文本
    """
    if data is None or data.empty:
        return f"❌ 無法獲取港股 {symbol} 的AKShare數據"

    try:
        # 獲取股票基本信息（允許失败）
        stock_name = f'港股{symbol}'  # 默認名稱
        try:
            provider = get_akshare_provider()
            stock_info = provider.get_hk_stock_info(symbol)
            stock_name = stock_info.get('name', f'港股{symbol}')
            logger.info(f"✅ 港股信息獲取成功: {stock_name}")
        except Exception as info_error:
            logger.error(f"⚠️ 港股信息獲取失败，使用默認信息: {info_error}")
            # 繼续處理，使用默認信息

        # 計算統計信息
        latest_price = data['Close'].iloc[-1]
        price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
        price_change_pct = (price_change / data['Close'].iloc[0]) * 100

        avg_volume = data['Volume'].mean() if 'Volume' in data.columns else 0
        max_price = data['High'].max()
        min_price = data['Low'].min()

        # 格式化輸出
        formatted_text = f"""
🇭🇰 港股數據報告 (AKShare)
================

股票信息:
- 代碼: {symbol}
- 名稱: {stock_name}
- 貨币: 港币 (HKD)
- 交易所: 香港交易所 (HKG)

價格信息:
- 最新價格: HK${latest_price:.2f}
- 期間涨跌: HK${price_change:+.2f} ({price_change_pct:+.2f}%)
- 期間最高: HK${max_price:.2f}
- 期間最低: HK${min_price:.2f}

交易信息:
- 數據期間: {start_date} 至 {end_date}
- 交易天數: {len(data)}天
- 平均成交量: {avg_volume:,.0f}股

最近5個交易日:
"""

        # 添加最近5天的數據
        recent_data = data.tail(5)
        for _, row in recent_data.iterrows():
            date = row['Date'].strftime('%Y-%m-%d') if 'Date' in row else row.name.strftime('%Y-%m-%d')
            volume = row.get('Volume', 0)
            formatted_text += f"- {date}: 開盘HK${row['Open']:.2f}, 收盘HK${row['Close']:.2f}, 成交量{volume:,.0f}\n"

        formatted_text += f"\n數據來源: AKShare (港股)\n"

        return formatted_text

    except Exception as e:
        logger.error(f"❌ 格式化AKShare港股數據失败: {e}")
        return f"❌ AKShare港股數據格式化失败: {symbol}"


def get_stock_news_em(symbol: str, max_news: int = 10) -> pd.DataFrame:
    """
    使用AKShare獲取东方財富個股新聞

    Args:
        symbol: 股票代碼，如 "600000" 或 "300059"
        max_news: 最大新聞數量，默認10條

    Returns:
        pd.DataFrame: 包含新聞標題、內容、日期和鏈接的DataFrame
    """
    start_time = datetime.now()
    logger.info(f"[东方財富新聞] 開始獲取股票 {symbol} 的东方財富新聞數據")
    
    try:
        provider = get_akshare_provider()
        if not provider.connected:
            logger.error(f"[东方財富新聞] ❌ AKShare未連接，無法獲取东方財富新聞")
            return pd.DataFrame()

        logger.info(f"[东方財富新聞] 📰 準备調用AKShare API獲取個股新聞: {symbol}")

        # 使用線程超時包裝（兼容Windows）
        import threading
        import time

        result = [None]
        exception = [None]

        def fetch_news():
            try:
                logger.debug(f"[东方財富新聞] 線程開始執行 stock_news_em API調用: {symbol}")
                thread_start = time.time()
                result[0] = provider.ak.stock_news_em(symbol=symbol)
                thread_end = time.time()
                logger.debug(f"[东方財富新聞] 線程執行完成，耗時: {thread_end - thread_start:.2f}秒")
            except Exception as e:
                logger.error(f"[东方財富新聞] 線程執行異常: {e}")
                exception[0] = e

        # 啟動線程
        thread = threading.Thread(target=fetch_news)
        thread.daemon = True
        logger.debug(f"[东方財富新聞] 啟動線程獲取新聞數據")
        thread.start()

        # 等待30秒
        logger.debug(f"[东方財富新聞] 等待線程完成，最長等待30秒")
        thread.join(timeout=30)

        if thread.is_alive():
            # 超時了
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.warning(f"[东方財富新聞] ⚠️ 獲取超時（30秒）: {symbol}，总耗時: {elapsed_time:.2f}秒")
            raise Exception(f"东方財富個股新聞獲取超時（30秒）: {symbol}")
        elif exception[0]:
            # 有異常
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"[东方財富新聞] ❌ API調用異常: {exception[0]}，总耗時: {elapsed_time:.2f}秒")
            raise exception[0]
        else:
            # 成功
            news_df = result[0]

        if news_df is not None and not news_df.empty:
            # 限制新聞數量為最新的max_news條
            if len(news_df) > max_news:
                news_df = news_df.head(max_news)
                logger.info(f"[东方財富新聞] 📰 新聞數量限制: 從{len(news_df)}條限制為{max_news}條最新新聞")
            
            news_count = len(news_df)
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            # 記錄一些新聞標題示例
            sample_titles = [row.get('標題', '無標題') for _, row in news_df.head(3).iterrows()]
            logger.info(f"[东方財富新聞] 新聞標題示例: {', '.join(sample_titles)}")
            
            logger.info(f"[东方財富新聞] ✅ 獲取成功: {symbol}, 共{news_count}條記錄，耗時: {elapsed_time:.2f}秒")
            return news_df
        else:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.warning(f"[东方財富新聞] ⚠️ 數據為空: {symbol}，API返回成功但無數據，耗時: {elapsed_time:.2f}秒")
            return pd.DataFrame()

    except Exception as e:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"[东方財富新聞] ❌ 獲取失败: {symbol}, 錯誤: {e}, 耗時: {elapsed_time:.2f}秒")
        return pd.DataFrame()
