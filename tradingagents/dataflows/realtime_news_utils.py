#!/usr/bin/env python3
"""
實時新聞數據獲取工具
解決新聞滯後性問題
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import os
from dataclasses import dataclass

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')



@dataclass
class NewsItem:
    """新聞項目數據結構"""
    title: str
    content: str
    source: str
    publish_time: datetime
    url: str
    urgency: str  # high, medium, low
    relevance_score: float


class RealtimeNewsAggregator:
    """實時新聞聚合器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'TradingAgents-CN/1.0'
        }
        
        # API密鑰配置
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        
    def get_realtime_stock_news(self, ticker: str, hours_back: int = 6, max_news: int = 10) -> List[NewsItem]:
        """
        獲取實時股票新聞
        優先級：專業API > 新聞API > 搜索引擎
        
        Args:
            ticker: 股票代碼
            hours_back: 回溯小時數
            max_news: 最大新聞數量，默認10條
        """
        logger.info(f"[新聞聚合器] 開始獲取 {ticker} 的實時新聞，回溯時間: {hours_back}小時")
        start_time = datetime.now()
        all_news = []
        
        # 1. FinnHub實時新聞 (最高優先級)
        logger.info(f"[新聞聚合器] 嘗試從 FinnHub 獲取 {ticker} 的新聞")
        finnhub_start = datetime.now()
        finnhub_news = self._get_finnhub_realtime_news(ticker, hours_back)
        finnhub_time = (datetime.now() - finnhub_start).total_seconds()
        
        if finnhub_news:
            logger.info(f"[新聞聚合器] 成功從 FinnHub 獲取 {len(finnhub_news)} 條新聞，耗時: {finnhub_time:.2f}秒")
        else:
            logger.info(f"[新聞聚合器] FinnHub 未返回新聞，耗時: {finnhub_time:.2f}秒")
            
        all_news.extend(finnhub_news)
        
        # 2. Alpha Vantage新聞
        logger.info(f"[新聞聚合器] 嘗試從 Alpha Vantage 獲取 {ticker} 的新聞")
        av_start = datetime.now()
        av_news = self._get_alpha_vantage_news(ticker, hours_back)
        av_time = (datetime.now() - av_start).total_seconds()
        
        if av_news:
            logger.info(f"[新聞聚合器] 成功從 Alpha Vantage 獲取 {len(av_news)} 條新聞，耗時: {av_time:.2f}秒")
        else:
            logger.info(f"[新聞聚合器] Alpha Vantage 未返回新聞，耗時: {av_time:.2f}秒")
            
        all_news.extend(av_news)
        
        # 3. NewsAPI (如果配置了)
        if self.newsapi_key:
            logger.info(f"[新聞聚合器] 嘗試從 NewsAPI 獲取 {ticker} 的新聞")
            newsapi_start = datetime.now()
            newsapi_news = self._get_newsapi_news(ticker, hours_back)
            newsapi_time = (datetime.now() - newsapi_start).total_seconds()
            
            if newsapi_news:
                logger.info(f"[新聞聚合器] 成功從 NewsAPI 獲取 {len(newsapi_news)} 條新聞，耗時: {newsapi_time:.2f}秒")
            else:
                logger.info(f"[新聞聚合器] NewsAPI 未返回新聞，耗時: {newsapi_time:.2f}秒")
                
            all_news.extend(newsapi_news)
        else:
            logger.info(f"[新聞聚合器] NewsAPI 密鑰未配置，跳過此新聞源")
        
        # 去重和排序
        logger.info(f"[新聞聚合器] 開始對 {len(all_news)} 條新聞進行去重和排序")
        dedup_start = datetime.now()
        unique_news = self._deduplicate_news(all_news)
        sorted_news = sorted(unique_news, key=lambda x: x.publish_time, reverse=True)
        dedup_time = (datetime.now() - dedup_start).total_seconds()
        
        # 記錄去重結果
        removed_count = len(all_news) - len(unique_news)
        logger.info(f"[新聞聚合器] 新聞去重完成，移除了 {removed_count} 條重複新聞，剩餘 {len(sorted_news)} 條，耗時: {dedup_time:.2f}秒")
        
        # 記錄總體情況
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[新聞聚合器] {ticker} 的新聞聚合完成，總共獲取 {len(sorted_news)} 條新聞，總耗時: {total_time:.2f}秒")
        
        # 限制新聞數量為最新的max_news條
        if len(sorted_news) > max_news:
            original_count = len(sorted_news)
            sorted_news = sorted_news[:max_news]
            logger.info(f"[新聞聚合器] 新聞數量限制: 從{original_count}條限制為{max_news}條最新新聞")
        
        # 記錄一些新聞標題示例
        if sorted_news:
            sample_titles = [item.title for item in sorted_news[:3]]
            logger.info(f"[新聞聚合器] 新聞標題示例: {', '.join(sample_titles)}")
        
        return sorted_news
    
    def _get_finnhub_realtime_news(self, ticker: str, hours_back: int) -> List[NewsItem]:
        """獲取FinnHub實時新聞"""
        if not self.finnhub_key:
            return []
        
        try:
            # 計算時間範圍
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # FinnHub API調用
            url = "https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': ticker,
                'from': start_time.strftime('%Y-%m-%d'),
                'to': end_time.strftime('%Y-%m-%d'),
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            news_data = response.json()
            news_items = []
            
            for item in news_data:
                # 檢查新聞時效性
                publish_time = datetime.fromtimestamp(item.get('datetime', 0))
                if publish_time < start_time:
                    continue
                
                # 評估緊急程度
                urgency = self._assess_news_urgency(item.get('headline', ''), item.get('summary', ''))
                
                news_items.append(NewsItem(
                    title=item.get('headline', ''),
                    content=item.get('summary', ''),
                    source=item.get('source', 'FinnHub'),
                    publish_time=publish_time,
                    url=item.get('url', ''),
                    urgency=urgency,
                    relevance_score=self._calculate_relevance(item.get('headline', ''), ticker)
                ))
            
            return news_items
            
        except Exception as e:
            logger.error(f"FinnHub新聞獲取失敗: {e}")
            return []
    
    def _get_alpha_vantage_news(self, ticker: str, hours_back: int) -> List[NewsItem]:
        """獲取Alpha Vantage新聞"""
        if not self.alpha_vantage_key:
            return []
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker,
                'apikey': self.alpha_vantage_key,
                'limit': 50
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            news_items = []
            
            if 'feed' in data:
                for item in data['feed']:
                    # 解析時間
                    time_str = item.get('time_published', '')
                    try:
                        publish_time = datetime.strptime(time_str, '%Y%m%dT%H%M%S')
                    except Exception:
                        continue
                    
                    # 檢查時效性
                    if publish_time < datetime.now() - timedelta(hours=hours_back):
                        continue
                    
                    urgency = self._assess_news_urgency(item.get('title', ''), item.get('summary', ''))
                    
                    news_items.append(NewsItem(
                        title=item.get('title', ''),
                        content=item.get('summary', ''),
                        source=item.get('source', 'Alpha Vantage'),
                        publish_time=publish_time,
                        url=item.get('url', ''),
                        urgency=urgency,
                        relevance_score=self._calculate_relevance(item.get('title', ''), ticker)
                    ))
            
            return news_items
            
        except Exception as e:
            logger.error(f"Alpha Vantage新聞獲取失敗: {e}")
            return []
    
    def _get_newsapi_news(self, ticker: str, hours_back: int) -> List[NewsItem]:
        """獲取NewsAPI新聞"""
        try:
            # 構建搜索查詢
            company_names = {
                'AAPL': 'Apple',
                'TSLA': 'Tesla', 
                'NVDA': 'NVIDIA',
                'MSFT': 'Microsoft',
                'GOOGL': 'Google'
            }
            
            query = f"{ticker} OR {company_names.get(ticker, ticker)}"
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': (datetime.now() - timedelta(hours=hours_back)).isoformat(),
                'apiKey': self.newsapi_key
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            news_items = []
            
            for item in data.get('articles', []):
                # 解析時間
                time_str = item.get('publishedAt', '')
                try:
                    publish_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                except Exception:
                    continue
                
                urgency = self._assess_news_urgency(item.get('title', ''), item.get('description', ''))
                
                news_items.append(NewsItem(
                    title=item.get('title', ''),
                    content=item.get('description', ''),
                    source=item.get('source', {}).get('name', 'NewsAPI'),
                    publish_time=publish_time,
                    url=item.get('url', ''),
                    urgency=urgency,
                    relevance_score=self._calculate_relevance(item.get('title', ''), ticker)
                ))
            
            return news_items
            
        except Exception as e:
            logger.error(f"NewsAPI新聞獲取失敗: {e}")
            return []
    
    def _assess_news_urgency(self, title: str, content: str) -> str:
        """評估新聞緊急程度"""
        text = (title + ' ' + content).lower()
        
        # 高緊急度關鍵詞
        high_urgency_keywords = [
            'breaking', 'urgent', 'alert', 'emergency', 'halt', 'suspend',
            '突發', '緊急', '暫停', '停牌', '重大'
        ]
        
        # 中等緊急度關鍵詞
        medium_urgency_keywords = [
            'earnings', 'report', 'announce', 'launch', 'merger', 'acquisition',
            '財報', '發布', '宣布', '並購', '收購'
        ]
        
        # 檢查高緊急度關鍵詞
        for keyword in high_urgency_keywords:
            if keyword in text:
                logger.debug(f"[緊急度評估] 檢測到高緊急度關鍵詞 '{keyword}' 在新聞中: {title[:50]}...")
                return 'high'
        
        # 檢查中等緊急度關鍵詞
        for keyword in medium_urgency_keywords:
            if keyword in text:
                logger.debug(f"[緊急度評估] 檢測到中等緊急度關鍵詞 '{keyword}' 在新聞中: {title[:50]}...")
                return 'medium'
        
        logger.debug(f"[緊急度評估] 未檢測到緊急關鍵詞，評估為低緊急度: {title[:50]}...")
        return 'low'
    
    def _calculate_relevance(self, title: str, ticker: str) -> float:
        """計算新聞相關性分數"""
        text = title.lower()
        ticker_lower = ticker.lower()
        
        # 基礎相關性 - 股票代碼直接出現在標題中
        if ticker_lower in text:
            logger.debug(f"[相關性計算] 股票代碼 {ticker} 直接出現在標題中，相關性評分: 1.0，標題: {title[:50]}...")
            return 1.0
        
        # 公司名稱匹配
        company_names = {
            'aapl': ['apple', 'iphone', 'ipad', 'mac'],
            'tsla': ['tesla', 'elon musk', 'electric vehicle'],
            'nvda': ['nvidia', 'gpu', 'ai chip'],
            'msft': ['microsoft', 'windows', 'azure'],
            'googl': ['google', 'alphabet', 'search']
        }
        
        # 檢查公司相關關鍵詞
        if ticker_lower in company_names:
            for name in company_names[ticker_lower]:
                if name in text:
                    logger.debug(f"[相關性計算] 檢測到公司相關關鍵詞 '{name}' 在標題中，相關性評分: 0.8，標題: {title[:50]}...")
                    return 0.8
        
        # 提取股票代碼的純數字部分
        pure_code = ''.join(filter(str.isdigit, ticker))
        if pure_code and pure_code in text:
            logger.debug(f"[相關性計算] 股票代碼數字部分 {pure_code} 出現在標題中，相關性評分: 0.9，標題: {title[:50]}...")
            return 0.9
        
        logger.debug(f"[相關性計算] 未檢測到明確相關性，使用默認評分: 0.3，標題: {title[:50]}...")
        return 0.3  # 默認相關性
    
    def _deduplicate_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """去重新聞"""
        logger.info(f"[新聞去重] 開始對 {len(news_items)} 條新聞進行去重處理")
        start_time = datetime.now()
        
        seen_titles = set()
        unique_news = []
        duplicate_count = 0
        short_title_count = 0
        
        for item in news_items:
            # 簡單的標題去重
            title_key = item.title.lower().strip()
            
            # 檢查標題長度
            if len(title_key) <= 10:
                logger.debug(f"[新聞去重] 跳過標題過短的新聞: '{item.title}'，來源: {item.source}")
                short_title_count += 1
                continue
                
            # 檢查是否重複
            if title_key in seen_titles:
                logger.debug(f"[新聞去重] 檢測到重複新聞: '{item.title[:50]}...'，來源: {item.source}")
                duplicate_count += 1
                continue
                
            # 添加到結果集
            seen_titles.add(title_key)
            unique_news.append(item)
        
        # 記錄去重結果
        time_taken = (datetime.now() - start_time).total_seconds()
        logger.info(f"[新聞去重] 去重完成，原始新聞: {len(news_items)}條，去重後: {len(unique_news)}條，")
        logger.info(f"[新聞去重] 去除重複: {duplicate_count}條，標題過短: {short_title_count}條，耗時: {time_taken:.2f}秒")
        
        return unique_news
    
    def format_news_report(self, news_items: List[NewsItem], ticker: str) -> str:
        """格式化新聞報告"""
        logger.info(f"[新聞報告] 開始為 {ticker} 生成新聞報告")
        start_time = datetime.now()
        
        if not news_items:
            logger.warning(f"[新聞報告] 未獲取到 {ticker} 的實時新聞數據")
            return f"未獲取到{ticker}的實時新聞數據。"
        
        # 按緊急程度分組
        high_urgency = [n for n in news_items if n.urgency == 'high']
        medium_urgency = [n for n in news_items if n.urgency == 'medium']
        low_urgency = [n for n in news_items if n.urgency == 'low']
        
        # 記錄新聞分類情況
        logger.info(f"[新聞報告] {ticker} 新聞分類統計: 高緊急度 {len(high_urgency)}條, 中緊急度 {len(medium_urgency)}條, 低緊急度 {len(low_urgency)}條")
        
        # 記錄新聞來源分布
        news_sources = {}
        for item in news_items:
            source = item.source
            if source in news_sources:
                news_sources[source] += 1
            else:
                news_sources[source] = 1
        
        sources_info = ", ".join([f"{source}: {count}條" for source, count in news_sources.items()])
        logger.info(f"[新聞報告] {ticker} 新聞來源分布: {sources_info}")
        
        report = f"# {ticker} 實時新聞分析報告\n\n"
        report += f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"新聞總數: {len(news_items)}條\n\n"
        
        if high_urgency:
            report += "## 緊急新聞\n\n"
            for news in high_urgency[:3]:  # 最多顯示3條
                report += f"### {news.title}\n"
                report += f"**來源**: {news.source} | **時間**: {news.publish_time.strftime('%H:%M')}\n"
                report += f"{news.content}\n\n"
        
        if medium_urgency:
            report += "## 重要新聞\n\n"
            for news in medium_urgency[:5]:  # 最多顯示5條
                report += f"### {news.title}\n"
                report += f"**來源**: {news.source} | **時間**: {news.publish_time.strftime('%H:%M')}\n"
                report += f"{news.content}\n\n"
        
        # 添加時效性說明
        latest_news = max(news_items, key=lambda x: x.publish_time)
        time_diff = datetime.now() - latest_news.publish_time
        
        report += f"\n## 數據時效性\n"
        report += f"最新新聞發布於: {time_diff.total_seconds() / 60:.0f}分鐘前\n"
        
        if time_diff.total_seconds() < 1800:  # 30分鐘內
            report += "數據時效性: 優秀 (30分鐘內)\n"
        elif time_diff.total_seconds() < 3600:  # 1小時內
            report += "數據時效性: 良好 (1小時內)\n"
        else:
            report += "數據時效性: 一般 (超過1小時)\n"
        
        # 記錄報告生成完成信息
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        report_length = len(report)
        
        logger.info(f"[新聞報告] {ticker} 新聞報告生成完成，耗時: {time_taken:.2f}秒，報告長度: {report_length}字符")
        
        # 記錄時效性信息
        time_diff_minutes = time_diff.total_seconds() / 60
        logger.info(f"[新聞報告] {ticker} 新聞時效性: 最新新聞發布於 {time_diff_minutes:.1f}分鐘前")
        
        return report


def get_realtime_stock_news(ticker: str, curr_date: str, hours_back: int = 6) -> str:
    """
    獲取實時股票新聞的主要接口函數
    """
    logger.info(f"[新聞分析] ========== 函數入口 ==========")
    logger.info(f"[新聞分析] 函數: get_realtime_stock_news")
    logger.info(f"[新聞分析] 參數: ticker={ticker}, curr_date={curr_date}, hours_back={hours_back}")
    logger.info(f"[新聞分析] 開始獲取 {ticker} 的實時新聞，日期: {curr_date}, 回溯時間: {hours_back}小時")
    start_total_time = datetime.now()
    logger.info(f"[新聞分析] 開始時間: {start_total_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    
    # 股票類型判斷 - 美股
    logger.info(f"[新聞分析] ========== 步驟1: 股票類型判斷 ==========")
    stock_type = "美股"
    logger.info(f"[新聞分析] 原始ticker: {ticker}")
    logger.info(f"[新聞分析] 股票 {ticker} 類型: {stock_type}")
    
    # 使用實時新聞聚合器
    logger.info(f"[新聞分析] ========== 步驟3: 實時新聞聚合器 ==========")
    aggregator = RealtimeNewsAggregator()
    logger.info(f"[新聞分析] 成功創建實時新聞聚合器實例")
    try:
        logger.info(f"[新聞分析] 嘗試使用實時新聞聚合器獲取 {ticker} 的新聞")
        start_time = datetime.now()
        logger.info(f"[新聞分析] 聚合器調用開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        # 獲取實時新聞
        news_items = aggregator.get_realtime_stock_news(ticker, hours_back, max_news=10)
        
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        logger.info(f"[新聞分析] 聚合器調用結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        logger.info(f"[新聞分析] 聚合器調用耗時: {time_taken:.2f}秒")
        logger.info(f"[新聞分析] 聚合器返回數據類型: {type(news_items)}")
        logger.info(f"[新聞分析] 聚合器返回數據: {news_items}")
        
        # 如果成功獲取到新聞
        if news_items and len(news_items) > 0:
            news_count = len(news_items)
            logger.info(f"[新聞分析] 實時新聞聚合器成功獲取 {news_count} 條 {ticker} 的新聞，耗時 {time_taken:.2f} 秒")
            
            # 記錄一些新聞標題示例
            sample_titles = [item.title for item in news_items[:3]]
            logger.info(f"[新聞分析] 新聞標題示例: {', '.join(sample_titles)}")
            
            # 格式化報告
            logger.info(f"[新聞分析] 開始格式化新聞報告")
            report = aggregator.format_news_report(news_items, ticker)
            logger.info(f"[新聞分析] 報告格式化完成，長度: {len(report)} 字符")
            
            total_time_taken = (datetime.now() - start_total_time).total_seconds()
            logger.info(f"[新聞分析] 成功生成 {ticker} 的新聞報告，總耗時 {total_time_taken:.2f} 秒，新聞來源: 實時新聞聚合器")
            logger.info(f"[新聞分析] ========== 實時新聞聚合器獲取成功，函數即將返回 ==========")
            return report
        else:
            logger.warning(f"[新聞分析] 實時新聞聚合器未獲取到 {ticker} 的新聞，耗時 {time_taken:.2f} 秒，嘗試使用備用新聞源")
            # 如果沒有獲取到新聞，繼續嘗試備用方案
    except Exception as e:
        logger.error(f"[新聞分析] 實時新聞聚合器獲取失敗: {e}，將嘗試備用新聞源")
        logger.error(f"[新聞分析] 異常詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[新聞分析] 異常堆棧: {traceback.format_exc()}")
        # 發生異常時，繼續嘗試備用方案
    
    # 備用方案：嘗試使用 Google 新聞
    try:
        from tradingagents.dataflows.interface import get_google_news
        
        # 美股使用英文關鍵詞進行搜索
        search_query = f"{ticker} stock news"
        logger.info(f"[新聞分析] 開始從Google獲取 {ticker} 的新聞數據，查詢: {search_query}")
        
        start_time = datetime.now()
        google_news = get_google_news(search_query, curr_date, 1)
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        
        if google_news and len(google_news.strip()) > 0:
            # 估算獲取的新聞數量
            news_lines = google_news.strip().split('\n')
            news_count = sum(1 for line in news_lines if line.startswith('###'))
            
            logger.info(f"[新聞分析] 成功獲取 Google 新聞，估計 {news_count} 條新聞，耗時 {time_taken:.2f} 秒")
            
            # 記錄一些新聞標題示例
            sample_titles = [line.replace('### ', '') for line in news_lines if line.startswith('### ')][:3]
            if sample_titles:
                logger.info(f"[新聞分析] 新聞標題示例: {', '.join(sample_titles)}")
                
            logger.info(f"[新聞分析] 成功生成 Google 新聞報告，新聞來源: Google")
            return google_news
        else:
            logger.warning(f"[新聞分析] Google 新聞未獲取到 {ticker} 的新聞數據，耗時 {time_taken:.2f} 秒")
    except Exception as e:
        logger.error(f"[新聞分析] Google 新聞獲取失敗: {e}，所有備用方案均已嘗試")
    
    # 所有方法都失敗，返回錯誤信息
    total_time_taken = (datetime.now() - start_total_time).total_seconds()
    logger.error(f"[新聞分析] {ticker} 的所有新聞獲取方法均已失敗，總耗時 {total_time_taken:.2f} 秒")
    
    # 記錄詳細的失敗信息
    failure_details = {
        "股票代碼": ticker,
        "股票類型": stock_type,
        "分析日期": curr_date,
        "回溯時間": f"{hours_back}小時",
        "總耗時": f"{total_time_taken:.2f}秒"
    }
    logger.error(f"[新聞分析] 新聞獲取失敗詳情: {failure_details}")
    
    return f"""
實時新聞獲取失敗 - {ticker}
分析日期: {curr_date}

錯誤信息: 所有可用的新聞源都未能獲取到相關新聞

備用建議:
1. 檢查網絡連接和API密鑰配置
2. 使用基礎新聞分析作為備選
3. 關注官方財經媒體的最新報道
4. 考慮使用專業金融終端獲取實時新聞

注: 實時新聞獲取依賴外部 API 服務的可用性。
"""
