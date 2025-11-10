#!/usr/bin/env python3
"""
優化的美股數據獲取工具
集成緩存策略，减少API調用，提高響應速度
"""

import os
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import yfinance as yf
import pandas as pd
from .cache_manager import get_cache
from .config import get_config

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class OptimizedUSDataProvider:
    """優化的美股數據提供器 - 集成緩存和API限制處理"""
    
    def __init__(self):
        self.cache = get_cache()
        self.config = get_config()
        self.last_api_call = 0
        self.min_api_interval = 1.0  # 最小API調用間隔（秒）
        
        logger.info(f"📊 優化美股數據提供器初始化完成")
    
    def _wait_for_rate_limit(self):
        """等待API限制"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_api_interval:
            wait_time = self.min_api_interval - time_since_last_call
            logger.info(f"⏳ API限制等待 {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        self.last_api_call = time.time()
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str, 
                      force_refresh: bool = False) -> str:
        """
        獲取美股數據 - 優先使用緩存
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            force_refresh: 是否強制刷新緩存
        
        Returns:
            格式化的股票數據字符串
        """
        logger.info(f"📈 獲取美股數據: {symbol} ({start_date} 到 {end_date})")
        
        # 檢查緩存（除非強制刷新）
        if not force_refresh:
            # 優先查找FINNHUB緩存
            cache_key = self.cache.find_cached_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data_source="finnhub"
            )

            # 如果沒有FINNHUB緩存，查找Yahoo Finance緩存
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
                    logger.info(f"⚡ 從緩存加載美股數據: {symbol}")
                    return cached_data
        
        # 緩存未命中，從API獲取 - 優先使用FINNHUB
        formatted_data = None
        data_source = None

        # 嘗試FINNHUB API（優先）
        try:
            logger.info(f"🌐 從FINNHUB API獲取數據: {symbol}")
            self._wait_for_rate_limit()

            formatted_data = self._get_data_from_finnhub(symbol, start_date, end_date)
            if formatted_data and "❌" not in formatted_data:
                data_source = "finnhub"
                logger.info(f"✅ FINNHUB數據獲取成功: {symbol}")
            else:
                logger.error(f"⚠️ FINNHUB數據獲取失败，嘗試備用方案")
                formatted_data = None

        except Exception as e:
            logger.error(f"❌ FINNHUB API調用失败: {e}")
            formatted_data = None

        # 備用方案：根據股票類型選擇合適的數據源
        if not formatted_data:
            try:
                # 檢測股票類型
                from tradingagents.utils.stock_utils import StockUtils
                market_info = StockUtils.get_market_info(symbol)

                if market_info['is_hk']:
                    # 港股優先使用AKShare數據源
                    logger.info(f"🇭🇰 嘗試使用AKShare獲取港股數據: {symbol}")
                    try:
                        from tradingagents.dataflows.interface import get_hk_stock_data_unified
                        hk_data_text = get_hk_stock_data_unified(symbol, start_date, end_date)

                        if hk_data_text and "❌" not in hk_data_text:
                            formatted_data = hk_data_text
                            data_source = "akshare_hk"
                            logger.info(f"✅ AKShare港股數據獲取成功: {symbol}")
                        else:
                            raise Exception("AKShare港股數據獲取失败")

                    except Exception as e:
                        logger.error(f"⚠️ AKShare港股數據獲取失败: {e}")
                        # 備用方案：Yahoo Finance
                        logger.info(f"🔄 使用Yahoo Finance備用方案獲取港股數據: {symbol}")

                        self._wait_for_rate_limit()
                        ticker = yf.Ticker(symbol)  # 港股代碼保持原格式
                        data = ticker.history(start=start_date, end=end_date)

                        if not data.empty:
                            formatted_data = self._format_stock_data(symbol, data, start_date, end_date)
                            data_source = "yfinance_hk"
                            logger.info(f"✅ Yahoo Finance港股數據獲取成功: {symbol}")
                        else:
                            logger.error(f"❌ Yahoo Finance港股數據為空: {symbol}")
                else:
                    # 美股使用Yahoo Finance
                    logger.info(f"🇺🇸 從Yahoo Finance API獲取美股數據: {symbol}")
                    self._wait_for_rate_limit()

                    # 獲取數據
                    ticker = yf.Ticker(symbol.upper())
                    data = ticker.history(start=start_date, end=end_date)

                    if data.empty:
                        error_msg = f"未找到股票 '{symbol}' 在 {start_date} 到 {end_date} 期間的數據"
                        logger.error(f"❌ {error_msg}")
                    else:
                        # 格式化數據
                        formatted_data = self._format_stock_data(symbol, data, start_date, end_date)
                        data_source = "yfinance"
                        logger.info(f"✅ Yahoo Finance美股數據獲取成功: {symbol}")

            except Exception as e:
                logger.error(f"❌ 數據獲取失败: {e}")
                formatted_data = None

        # 如果所有API都失败，生成備用數據
        if not formatted_data:
            error_msg = "所有美股數據源都不可用"
            logger.error(f"❌ {error_msg}")
            return self._generate_fallback_data(symbol, start_date, end_date, error_msg)

        # 保存到緩存
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
        """格式化股票數據為字符串"""
        
        # 移除時区信息
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # 四舍五入數值
        numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
        for col in numeric_columns:
            if col in data.columns:
                data[col] = data[col].round(2)
        
        # 獲取最新價格和統計信息
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
        result = f"""# {symbol} 美股數據分析

## 📊 基本信息
- 股票代碼: {symbol}
- 數據期間: {start_date} 至 {end_date}
- 數據條數: {len(data)}條
- 最新價格: ${latest_price:.2f}
- 期間涨跌: ${price_change:+.2f} ({price_change_pct:+.2f}%)

## 📈 價格統計
- 期間最高: ${data['High'].max():.2f}
- 期間最低: ${data['Low'].min():.2f}
- 平均成交量: {data['Volume'].mean():,.0f}

## 🔍 技術指標
- MA5: ${data['MA5'].iloc[-1]:.2f}
- MA10: ${data['MA10'].iloc[-1]:.2f}
- MA20: ${data['MA20'].iloc[-1]:.2f}
- RSI: {rsi.iloc[-1]:.2f}

## 📋 最近5日數據
{data.tail().to_string()}

數據來源: Yahoo Finance API
更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return result
    
    def _try_get_old_cache(self, symbol: str, start_date: str, end_date: str) -> Optional[str]:
        """嘗試獲取過期的緩存數據作為備用"""
        try:
            # 查找任何相關的緩存，不考慮TTL
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
                            return cached_data + "\n\n⚠️ 註意: 使用的是過期緩存數據"
                except Exception:
                    continue
        except Exception:
            pass
        
        return None

    def _get_data_from_finnhub(self, symbol: str, start_date: str, end_date: str) -> str:
        """從FINNHUB API獲取股票數據"""
        try:
            import finnhub
            import os
            from datetime import datetime, timedelta


            # 獲取API密鑰
            api_key = os.getenv('FINNHUB_API_KEY')
            if not api_key:
                return None

            client = finnhub.Client(api_key=api_key)

            # 獲取實時報價
            quote = client.quote(symbol.upper())
            if not quote or 'c' not in quote:
                return None

            # 獲取公司信息
            profile = client.company_profile2(symbol=symbol.upper())
            company_name = profile.get('name', symbol.upper()) if profile else symbol.upper()

            # 格式化數據
            current_price = quote.get('c', 0)
            change = quote.get('d', 0)
            change_percent = quote.get('dp', 0)

            formatted_data = f"""# {symbol.upper()} 美股數據分析

## 📊 實時行情
- 股票名稱: {company_name}
- 當前價格: ${current_price:.2f}
- 涨跌額: ${change:+.2f}
- 涨跌幅: {change_percent:+.2f}%
- 開盘價: ${quote.get('o', 0):.2f}
- 最高價: ${quote.get('h', 0):.2f}
- 最低價: ${quote.get('l', 0):.2f}
- 前收盘: ${quote.get('pc', 0):.2f}
- 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 數據概覽
- 數據期間: {start_date} 至 {end_date}
- 數據來源: FINNHUB API (實時數據)
- 當前價位相對位置: {((current_price - quote.get('l', current_price)) / max(quote.get('h', current_price) - quote.get('l', current_price), 0.01) * 100):.1f}%
- 日內振幅: {((quote.get('h', 0) - quote.get('l', 0)) / max(quote.get('pc', 1), 0.01) * 100):.2f}%

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            return formatted_data

        except Exception as e:
            logger.error(f"❌ FINNHUB數據獲取失败: {e}")
            return None

    def _generate_fallback_data(self, symbol: str, start_date: str, end_date: str, error_msg: str) -> str:
        """生成備用數據"""
        return f"""# {symbol} 美股數據獲取失败

## ❌ 錯誤信息
{error_msg}

## 📊 模擬數據（僅供演示）
- 股票代碼: {symbol}
- 數據期間: {start_date} 至 {end_date}
- 最新價格: ${random.uniform(100, 300):.2f}
- 模擬涨跌: {random.uniform(-5, 5):+.2f}%

## ⚠️ 重要提示
由於API限制或網絡問題，無法獲取實時數據。
建議稍後重試或檢查網絡連接。

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


# 全局實例
_us_data_provider = None

def get_optimized_us_data_provider() -> OptimizedUSDataProvider:
    """獲取全局美股數據提供器實例"""
    global _us_data_provider
    if _us_data_provider is None:
        _us_data_provider = OptimizedUSDataProvider()
    return _us_data_provider


def get_us_stock_data_cached(symbol: str, start_date: str, end_date: str, 
                           force_refresh: bool = False) -> str:
    """
    獲取美股數據的便捷函數
    
    Args:
        symbol: 股票代碼
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        force_refresh: 是否強制刷新緩存
    
    Returns:
        格式化的股票數據字符串
    """
    provider = get_optimized_us_data_provider()
    return provider.get_stock_data(symbol, start_date, end_date, force_refresh)
