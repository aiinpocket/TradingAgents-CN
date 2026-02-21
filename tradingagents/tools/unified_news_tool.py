#!/usr/bin/env python3
"""
統一新聞分析工具
整合美股市場的新聞獲取邏輯到一個工具函數中
讓大模型只需要調用一個工具就能獲取美股的新聞數據
"""

import logging
from datetime import datetime, timedelta
import re
import hashlib
import os

logger = logging.getLogger(__name__)

class UnifiedNewsAnalyzer:
    """統一新聞分析器，整合所有新聞獲取邏輯"""

    def __init__(self, toolkit):
        """初始化統一新聞分析器

        Args:
            toolkit: 包含各種新聞獲取工具的工具包
        """
        self.toolkit = toolkit
        self.news_cache = {}
        self.cache_hours = int(os.getenv('NEWS_CACHE_HOURS', '4'))
        self.cache_enabled = os.getenv('NEWS_CACHE_ENABLED', 'true').lower() == 'true'
        logger.info(f"[統一新聞工具] 快取已{'啟用' if self.cache_enabled else '禁用'}，快取時間: {self.cache_hours}小時")
        
    def get_stock_news_unified(self, stock_code: str, max_news: int = 10, model_info: str = "") -> str:
        """
        統一新聞獲取接口
        根據股票代碼自動識別股票類型並獲取相應新聞

        Args:
            stock_code: 股票代碼
            max_news: 最大新聞數量
            model_info: 當前使用的模型信息，用於特殊處理

        Returns:
            str: 格式化的新聞內容
        """
        logger.info(f"[統一新聞工具] 開始獲取 {stock_code} 的新聞，模型: {model_info}")
        logger.info(f"[統一新聞工具] 當前模型信息: {model_info}")

        if self.cache_enabled:
            cache_key = self._generate_cache_key(stock_code, max_news)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"[統一新聞工具] 從快取返回結果，股票: {stock_code}")
                return cached_result

        stock_type = self._identify_stock_type(stock_code)
        logger.info(f"[統一新聞工具] 股票類型: {stock_type}")
        
        # 統一使用美股新聞獲取方法
        result = self._get_us_share_news(stock_code, max_news, model_info)
        
        logger.info(f"[統一新聞工具] 新聞獲取完成，結果長度: {len(result)} 字符")
        logger.info(f"[統一新聞工具] 返回結果預覽 (前1000字符): {result[:1000]}")

        if not result or len(result.strip()) < 50:
            logger.warning(f"[統一新聞工具] 返回結果異常短或為空！")
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
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str):
        """從快取獲取資料"""
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
        """獲取美股新聞"""
        logger.info(f"[統一新聞工具] 獲取美股 {stock_code} 新聞")
        
        # 獲取當前日期
        curr_date = datetime.now().strftime("%Y-%m-%d")
        
        # 優先級1: OpenAI全球新聞
        try:
            if hasattr(self.toolkit, 'get_global_news_openai'):
                logger.info(f"[統一新聞工具] 嘗試OpenAI美股新聞...")
                # 使用LangChain工具的正確調用方式：.invoke()方法和字典參數
                result = self.toolkit.get_global_news_openai.invoke({"curr_date": curr_date})
                if result and len(result.strip()) > 50:
                    logger.info(f"[統一新聞工具] OpenAI美股新聞獲取成功: {len(result)} 字符")
                    return self._format_news_result(result, "OpenAI美股新聞", model_info)
        except Exception as e:
            logger.warning(f"[統一新聞工具] OpenAI美股新聞獲取失敗: {e}")
        
        # 優先級2: Google新聞（英文搜索）
        try:
            if hasattr(self.toolkit, 'get_google_news'):
                logger.info(f"[統一新聞工具] 嘗試Google美股新聞...")
                query = f"{stock_code} stock news earnings financial"
                # 使用LangChain工具的正確調用方式：.invoke()方法和字典參數
                result = self.toolkit.get_google_news.invoke({"query": query, "curr_date": curr_date})
                if result and len(result.strip()) > 50:
                    logger.info(f"[統一新聞工具] Google美股新聞獲取成功: {len(result)} 字符")
                    return self._format_news_result(result, "Google美股新聞", model_info)
        except Exception as e:
            logger.warning(f"[統一新聞工具] Google美股新聞獲取失敗: {e}")
        
        # 優先級3: FinnHub新聞（如果可用）
        try:
            if hasattr(self.toolkit, 'get_finnhub_news'):
                logger.info(f"[統一新聞工具] 嘗試FinnHub美股新聞...")
                # 使用LangChain工具的正確調用方式：.invoke()方法和字典參數
                result = self.toolkit.get_finnhub_news.invoke({"symbol": stock_code, "max_results": min(max_news, 50)})
                if result and len(result.strip()) > 50:
                    logger.info(f"[統一新聞工具] FinnHub美股新聞獲取成功: {len(result)} 字符")
                    return self._format_news_result(result, "FinnHub美股新聞", model_info)
        except Exception as e:
            logger.warning(f"[統一新聞工具] FinnHub美股新聞獲取失敗: {e}")
        
        return "無法獲取美股新聞數據，所有新聞源均不可用"
    
    def _format_news_result(self, news_content: str, source: str, model_info: str = "") -> str:
        """格式化新聞結果"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 添加調試日誌：打印原始新聞內容
        logger.info(f"[統一新聞工具] 原始新聞內容預覽 (前500字符): {news_content[:500]}")
        logger.info(f"[統一新聞工具] 原始內容長度: {len(news_content)} 字符")
        
        # 檢測是否為Google/Gemini模型
        is_google_model = any(keyword in model_info.lower() for keyword in ['google', 'gemini', 'gemma'])
        original_length = len(news_content)
        google_control_applied = False
        
        # 添加Google模型檢測日誌
        if is_google_model:
            logger.info(f"[統一新聞工具] 檢測到Google模型，啟用特殊處理")
        
        # 對Google模型進行特殊的長度控制
        if is_google_model and len(news_content) > 5000:  # 降低閾值到5000字符
            logger.warning(f"[統一新聞工具] 檢測到Google模型，新聞內容過長({len(news_content)}字符)，進行長度控制...")
            
            # 更嚴格的長度控制策略
            lines = news_content.split('\n')
            important_lines = []
            char_count = 0
            target_length = 3000  # 目標長度設為3000字符
            
            # 第一輪：優先保留包含關鍵詞的重要行
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 檢查是否包含重要關鍵詞
                important_keywords = ['股票', '公司', '財報', '業績', '漲跌', '價格', '市值', '營收', '利潤',
                                    '增長', '下跌', '上漲', '盈利', '虧損', '投資', '分析', '預期', '公告']
                
                is_important = any(keyword in line for keyword in important_keywords)
                
                if is_important and char_count + len(line) < target_length:
                    important_lines.append(line)
                    char_count += len(line)
                elif not is_important and char_count + len(line) < target_length * 0.7:  # 非重要內容更嚴格限制
                    important_lines.append(line)
                    char_count += len(line)
                
                # 如果已達到目標長度，停止添加
                if char_count >= target_length:
                    break
            
            # 如果提取的重要內容仍然過長，進行進一步截斷
            if important_lines:
                processed_content = '\n'.join(important_lines)
                if len(processed_content) > target_length:
                    processed_content = processed_content[:target_length] + "...(內容已智能截斷)"
                
                news_content = processed_content
                google_control_applied = True
                logger.info(f"[統一新聞工具] Google模型智能長度控制完成，從{original_length}字符壓縮至{len(news_content)}字符")
            else:
                # 如果沒有重要行，直接截斷到目標長度
                news_content = news_content[:target_length] + "...(內容已強制截斷)"
                google_control_applied = True
                logger.info(f"[統一新聞工具] Google模型強制截斷至{target_length}字符")
        
        # 計算最終的格式化結果長度，確保總長度合理
        base_format_length = 300  # 格式化模板的大概長度
        if is_google_model and (len(news_content) + base_format_length) > 4000:
            # 如果加上格式化後仍然過長，進一步壓縮新聞內容
            max_content_length = 3500
            if len(news_content) > max_content_length:
                news_content = news_content[:max_content_length] + "...(已優化長度)"
                google_control_applied = True
                logger.info(f"[統一新聞工具] Google模型最終長度優化，內容長度: {len(news_content)}字符")
        
        formatted_result = f"""
=== 新聞數據來源: {source} ===
獲取時間: {timestamp}
數據長度: {len(news_content)} 字符
{f"模型類型: {model_info}" if model_info else ""}
{f"Google模型長度控制已應用 (原長度: {original_length} 字符)" if google_control_applied else ""}

=== 新聞內容 ===
{news_content}

=== 數據狀態 ===
狀態: 成功獲取
來源: {source}
時間戳: {timestamp}
"""
        return formatted_result.strip()


def create_unified_news_tool(toolkit):
    """創建統一新聞工具函數"""
    analyzer = UnifiedNewsAnalyzer(toolkit)
    
    def get_stock_news_unified(stock_code: str, max_news: int = 100, model_info: str = ""):
        """
        統一新聞獲取工具

        Args:
            stock_code (str): 美股股票代碼 (如 AAPL、TSLA、NVDA)
            max_news (int): 最大新聞數量，默認100
            model_info (str): 當前使用的模型信息，用於特殊處理

        Returns:
            str: 格式化的新聞內容
        """
        if not stock_code:
            return "錯誤: 未提供股票代碼"
        
        return analyzer.get_stock_news_unified(stock_code, max_news, model_info)
    
    # 設置工具屬性
    get_stock_news_unified.name = "get_stock_news_unified"
    get_stock_news_unified.description = """
統一新聞獲取工具 - 獲取美股市場的新聞

功能:
- 專注於美股新聞獲取
- 優先OpenAI -> Google英文 -> FinnHub
- 返回格式化的新聞內容
- 支持Google模型的特殊長度控制
"""
    
    return get_stock_news_unified