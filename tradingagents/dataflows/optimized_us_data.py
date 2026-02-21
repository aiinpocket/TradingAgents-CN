#!/usr/bin/env python3
"""
優化的美股資料取得工具
整合快取策略，減少API呼叫，提高回應速度
"""

import time
import random
from datetime import datetime
from typing import Optional
import yfinance as yf
import pandas as pd
from .cache_manager import get_cache
from .config import get_config

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class OptimizedUSDataProvider:
    """優化的美股資料提供器 - 整合快取和API限制處理"""
    
    def __init__(self):
        self.cache = get_cache()
        self.config = get_config()
        self.last_api_call = 0
        self.min_api_interval = 1.0  # 最小API呼叫間隔（秒）
        
        logger.info("優化美股資料提供器初始化完成")
    
    def _wait_for_rate_limit(self):
        """等待API限制"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_api_interval:
            wait_time = self.min_api_interval - time_since_last_call
            logger.info(f"API限制等待 {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        self.last_api_call = time.time()
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str, 
                      force_refresh: bool = False) -> str:
        """
        取得美股資料 - 優先使用快取
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            force_refresh: 是否強制重新整理快取
        
        Returns:
            格式化的股票資料字串
        """
        logger.info(f"取得美股資料: {symbol} ({start_date} 到 {end_date})")
        
        # 檢查快取（除非強制重新整理）
        if not force_refresh:
            # 優先查找FINNHUB快取
            cache_key = self.cache.find_cached_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data_source="finnhub"
            )

            # 如果沒有FINNHUB快取，查找Yahoo Finance快取
            if not cache_key:
                cache_key = self.cache.find_cached_stock_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    data_source="yfinance"
                )

            if cache_key:
                cached_data = self.cache.load_stock_data(cache_key)
                if cached_data:
                    logger.info(f"從快取載入美股資料: {symbol}")
                    return cached_data
        
        # 快取未命中，從API取得 - 優先使用FINNHUB
        formatted_data = None
        data_source = None

        # 嘗試FINNHUB API（優先）
        try:
            logger.info(f"從FINNHUB API取得資料: {symbol}")
            self._wait_for_rate_limit()

            formatted_data = self._get_data_from_finnhub(symbol, start_date, end_date)
            if formatted_data and "錯誤訊息" not in formatted_data:
                data_source = "finnhub"
                logger.info(f"FINNHUB資料取得成功: {symbol}")
            else:
                logger.error("FINNHUB資料取得失敗，嘗試備用方案")
                formatted_data = None

        except Exception as e:
            logger.error(f"FINNHUB API呼叫失敗: {e}")
            formatted_data = None

        # 備用方案：使用 Yahoo Finance 取得資料
        if not formatted_data:
            try:
                logger.info(f"從Yahoo Finance API取得資料: {symbol}")
                self._wait_for_rate_limit()

                ticker = yf.Ticker(symbol.upper())
                data = ticker.history(start=start_date, end=end_date)

                if data.empty:
                    error_msg = f"未找到股票 '{symbol}' 在 {start_date} 到 {end_date} 期間的資料"
                    logger.error(f"{error_msg}")
                else:
                    formatted_data = self._format_stock_data(symbol, data, start_date, end_date)
                    data_source = "yfinance"
                    logger.info(f"Yahoo Finance資料取得成功: {symbol}")

            except Exception as e:
                logger.error(f"資料取得失敗: {e}")
                formatted_data = None

        # 如果所有API都失敗，生成備用資料
        if not formatted_data:
            error_msg = "所有美股資料來源都不可用"
            logger.error(f"{error_msg}")
            return self._generate_fallback_data(symbol, start_date, end_date, error_msg)

        # 保存到快取
        self.cache.save_stock_data(
            symbol=symbol,
            data=formatted_data,
            start_date=start_date,
            end_date=end_date,
            data_source=data_source
        )

        return formatted_data
    
    def _format_stock_data(self, symbol: str, data: pd.DataFrame, 
                          start_date: str, end_date: str) -> str:
        """格式化股票資料為字串"""
        
        # 移除時區資訊
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # 四舍五入數值
        numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
        for col in numeric_columns:
            if col in data.columns:
                data[col] = data[col].round(2)
        
        # 取得最新價格和統計資訊
        latest_price = data['Close'].iloc[-1]
        price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
        price_change_pct = (price_change / data['Close'].iloc[0]) * 100
        
        # 計算技術指標
        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA10'] = data['Close'].rolling(window=10).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        
        # 計算RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 格式化輸出
        result = f"""# {symbol} 美股資料分析

## 基本資訊
- 股票代碼: {symbol}
- 資料期間: {start_date} 至 {end_date}
- 資料條數: {len(data)}條
- 最新價格: ${latest_price:.2f}
- 期間漲跌: ${price_change:+.2f} ({price_change_pct:+.2f}%)

## 價格統計
- 期間最高: ${data['High'].max():.2f}
- 期間最低: ${data['Low'].min():.2f}
- 平均成交量: {data['Volume'].mean():,.0f}

## 技術指標
- MA5: ${data['MA5'].iloc[-1]:.2f}
- MA10: ${data['MA10'].iloc[-1]:.2f}
- MA20: ${data['MA20'].iloc[-1]:.2f}
- RSI: {rsi.iloc[-1]:.2f}

## 最近5日資料
{data.tail().to_string()}

資料來源: Yahoo Finance API
更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return result
    
    def _try_get_old_cache(self, symbol: str, start_date: str, end_date: str) -> Optional[str]:
        """嘗試取得過期的快取資料作為備用"""
        try:
            # 查找任何相關的快取，不考慮TTL
            for metadata_file in self.cache.metadata_dir.glob(f"*_meta.json"):
                try:
                    import json
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    if (metadata.get('symbol') == symbol and 
                        metadata.get('data_type') == 'stock_data' and
                        metadata.get('market_type') == 'us'):
                        
                        cache_key = metadata_file.stem.replace('_meta', '')
                        cached_data = self.cache.load_stock_data(cache_key)
                        if cached_data:
                            return cached_data + "\n\n註意: 使用的是過期快取資料"
                except (json.JSONDecodeError, KeyError, IOError):
                    continue
        except OSError as e:
            logger.debug(f"讀取快取目錄失敗: {e}")

        return None

    def _get_data_from_finnhub(self, symbol: str, start_date: str, end_date: str) -> str:
        """從FINNHUB API取得股票資料"""
        try:
            import finnhub
            import os
            from datetime import datetime


            # 取得API密鑰
            api_key = os.getenv('FINNHUB_API_KEY')
            if not api_key:
                return None

            client = finnhub.Client(api_key=api_key)

            # 取得實時報價
            quote = client.quote(symbol.upper())
            if not quote or 'c' not in quote:
                return None

            # 取得公司資訊
            profile = client.company_profile2(symbol=symbol.upper())
            company_name = profile.get('name', symbol.upper()) if profile else symbol.upper()

            # 格式化資料
            current_price = quote.get('c', 0)
            change = quote.get('d', 0)
            change_percent = quote.get('dp', 0)

            formatted_data = f"""# {symbol.upper()} 美股資料分析

## 實時行情
- 股票名稱: {company_name}
- 當前價格: ${current_price:.2f}
- 漲跌額: ${change:+.2f}
- 漲跌幅: {change_percent:+.2f}%
- 開盤價: ${quote.get('o', 0):.2f}
- 最高價: ${quote.get('h', 0):.2f}
- 最低價: ${quote.get('l', 0):.2f}
- 前收盤: ${quote.get('pc', 0):.2f}
- 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 資料概覽
- 資料期間: {start_date} 至 {end_date}
- 資料來源: FINNHUB API (即時資料)
- 當前價位相對位置: {((current_price - quote.get('l', current_price)) / max(quote.get('h', current_price) - quote.get('l', current_price), 0.01) * 100):.1f}%
- 日內振幅: {((quote.get('h', 0) - quote.get('l', 0)) / max(quote.get('pc', 1), 0.01) * 100):.2f}%

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            return formatted_data

        except Exception as e:
            logger.error(f"FINNHUB資料取得失敗: {e}")
            return None

    def _generate_fallback_data(self, symbol: str, start_date: str, end_date: str, error_msg: str) -> str:
        """生成備用資料"""
        return f"""# {symbol} 美股資料取得失敗

## 錯誤訊息
{error_msg}

## 模擬資料（僅供演示）
- 股票代碼: {symbol}
- 資料期間: {start_date} 至 {end_date}
- 最新價格: ${random.uniform(100, 300):.2f}
- 模擬漲跌: {random.uniform(-5, 5):+.2f}%

## 重要提示
由於API限制或網路問題，無法取得即時資料。
建議稍後重試或檢查網路連接。

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


# 全局實例
_us_data_provider = None

def get_optimized_us_data_provider() -> OptimizedUSDataProvider:
    """取得全局美股資料提供器實例"""
    global _us_data_provider
    if _us_data_provider is None:
        _us_data_provider = OptimizedUSDataProvider()
    return _us_data_provider


def get_us_stock_data_cached(symbol: str, start_date: str, end_date: str, 
                           force_refresh: bool = False) -> str:
    """
    取得美股資料的便捷函式
    
    Args:
        symbol: 股票代碼
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        force_refresh: 是否強制重新整理快取
    
    Returns:
        格式化的股票資料字串
    """
    provider = get_optimized_us_data_provider()
    return provider.get_stock_data(symbol, start_date, end_date, force_refresh)
