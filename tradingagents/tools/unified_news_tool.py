#!/usr/bin/env python3
"""
統一新聞分析工具
整合美股市場的新聞取得邏輯到一個工具函式中
讓大模型只需要呼叫一個工具就能取得美股的新聞資料
"""

import logging
from datetime import datetime, timedelta
import hashlib
import os

logger = logging.getLogger(__name__)

class UnifiedNewsAnalyzer:
    """統一新聞分析器，整合所有新聞取得邏輯"""

    def __init__(self, toolkit):
        """初始化統一新聞分析器

        Args:
            toolkit: 包含各種新聞取得工具的工具包
        """
        self.toolkit = toolkit
        self.news_cache = {}
        self.cache_hours = int(os.getenv('NEWS_CACHE_HOURS', '4'))
        self.cache_enabled = os.getenv('NEWS_CACHE_ENABLED', 'true').lower() == 'true'
        logger.info(f"[統一新聞工具] 快取已{'啟用' if self.cache_enabled else '禁用'}，快取時間: {self.cache_hours}小時")
        
    def get_stock_news_unified(self, stock_code: str, max_news: int = 10, model_info: str = "") -> str:
        """
        統一新聞取得介面
        根據股票代碼自動識別股票類型並取得相應新聞

        Args:
            stock_code: 股票代碼
            max_news: 最大新聞數量
            model_info: 當前使用的模型資訊，用於特殊處理

        Returns:
            str: 格式化的新聞內容
        """
        logger.info(f"[統一新聞工具] 開始取得 {stock_code} 的新聞，模型: {model_info}")
        logger.info(f"[統一新聞工具] 當前模型資訊: {model_info}")

        if self.cache_enabled:
            cache_key = self._generate_cache_key(stock_code, max_news)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"[統一新聞工具] 從快取返回結果，股票: {stock_code}")
                return cached_result

        stock_type = self._identify_stock_type(stock_code)
        logger.info(f"[統一新聞工具] 股票類型: {stock_type}")
        
        # 統一使用美股新聞取得方法
        result = self._get_us_share_news(stock_code, max_news, model_info)
        
        logger.info(f"[統一新聞工具] 新聞取得完成，結果長度: {len(result)} 字元")
        logger.info(f"[統一新聞工具] 返回結果預覽 (前1000字元): {result[:1000]}")

        if not result or len(result.strip()) < 50:
            logger.warning("[統一新聞工具] 返回結果異常短或為空！")
            logger.warning(f"[統一新聞工具] 完整結果內容: '{result}'")

        if self.cache_enabled and result and len(result.strip()) >= 50:
            cache_key = self._generate_cache_key(stock_code, max_news)
            self._save_to_cache(cache_key, result)
            logger.info(f"[統一新聞工具] 結果已保存到快取，股票: {stock_code}")

        return result

    def _generate_cache_key(self, stock_code: str, max_news: int) -> str:
        """產生快取鍵值"""
        today = datetime.now().strftime("%Y-%m-%d")
        key_str = f"{stock_code}_{max_news}_{today}"
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def _get_from_cache(self, cache_key: str):
        """從快取取得資料"""
        if cache_key in self.news_cache:
            cached_data, cached_time = self.news_cache[cache_key]
            if datetime.now() - cached_time < timedelta(hours=self.cache_hours):
                return cached_data
            else:
                del self.news_cache[cache_key]
        return None

    def _save_to_cache(self, cache_key: str, data: str):
        """將資料保存到快取"""
        self.news_cache[cache_key] = (data, datetime.now())
    
    def _identify_stock_type(self, stock_code: str) -> str:
        """識別股票類型 - 統一視為美股"""
        return "美股"
    
    def _get_us_share_news(self, stock_code: str, max_news: int, model_info: str = "") -> str:
        """取得美股新聞（優先使用無 LLM 的資料來源）"""
        logger.info(f"[統一新聞工具] 取得美股 {stock_code} 新聞")

        curr_date = datetime.now().strftime("%Y-%m-%d")

        # 優先級1: Google 新聞 RSS（無 LLM，速度最快）
        try:
            if hasattr(self.toolkit, 'get_google_news'):
                logger.info("[統一新聞工具] 嘗試Google美股新聞...")
                query = f"{stock_code} stock news earnings financial"
                result = self.toolkit.get_google_news.invoke({"query": query, "curr_date": curr_date})
                if result and len(result.strip()) > 50:
                    logger.info(f"[統一新聞工具] Google美股新聞取得成功: {len(result)} 字元")
                    return self._format_news_result(result, "Google美股新聞", model_info)
        except Exception as e:
            logger.warning(f"[統一新聞工具] Google美股新聞取得失敗: {e}")

        # 優先級2: FinnHub 新聞 API（無 LLM）
        try:
            if hasattr(self.toolkit, 'get_finnhub_news'):
                logger.info("[統一新聞工具] 嘗試FinnHub美股新聞...")
                result = self.toolkit.get_finnhub_news.invoke({"symbol": stock_code, "max_results": min(max_news, 50)})
                if result and len(result.strip()) > 50:
                    logger.info(f"[統一新聞工具] FinnHub美股新聞取得成功: {len(result)} 字元")
                    return self._format_news_result(result, "FinnHub美股新聞", model_info)
        except Exception as e:
            logger.warning(f"[統一新聞工具] FinnHub美股新聞取得失敗: {e}")

        # 優先級3: OpenAI 全球新聞（LLM web_search，最後備選）
        try:
            if hasattr(self.toolkit, 'get_global_news_openai'):
                logger.info("[統一新聞工具] Google/FinnHub 皆失敗，回退到OpenAI...")
                result = self.toolkit.get_global_news_openai.invoke({"curr_date": curr_date})
                if result and len(result.strip()) > 50:
                    logger.info(f"[統一新聞工具] OpenAI美股新聞取得成功: {len(result)} 字元")
                    return self._format_news_result(result, "OpenAI美股新聞", model_info)
        except Exception as e:
            logger.warning(f"[統一新聞工具] OpenAI美股新聞取得失敗: {e}")

        return "無法取得美股新聞資料，所有新聞源均不可用"
    
    def _format_news_result(self, news_content: str, source: str, model_info: str = "") -> str:
        """格式化新聞結果"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"[統一新聞工具] 新聞內容長度: {len(news_content)} 字元")

        formatted_result = f"""
=== 新聞資料來源: {source} ===
取得時間: {timestamp}
資料長度: {len(news_content)} 字元

=== 新聞內容 ===
{news_content}

=== 資料狀態 ===
狀態: 成功取得
來源: {source}
時間戳: {timestamp}
"""
        return formatted_result.strip()


def create_unified_news_tool(toolkit):
    """建立統一新聞工具函式"""
    analyzer = UnifiedNewsAnalyzer(toolkit)
    
    def get_stock_news_unified(stock_code: str, max_news: int = 100, model_info: str = ""):
        """
        統一新聞取得工具

        Args:
            stock_code (str): 美股股票代碼 (如 AAPL、TSLA、NVDA)
            max_news (int): 最大新聞數量，預設100
            model_info (str): 當前使用的模型資訊，用於特殊處理

        Returns:
            str: 格式化的新聞內容
        """
        if not stock_code:
            return "錯誤: 未提供股票代碼"
        
        return analyzer.get_stock_news_unified(stock_code, max_news, model_info)
    
    # 設定工具屬性
    get_stock_news_unified.name = "get_stock_news_unified"
    get_stock_news_unified.description = """
統一新聞取得工具 - 取得美股市場的新聞

功能:
- 專注於美股新聞取得
- 優先 Google News RSS -> FinnHub API -> OpenAI（備選）
- 預設使用無 LLM 呼叫的資料來源，加速資料取得
- 返回格式化的新聞內容
"""
    
    return get_stock_news_unified