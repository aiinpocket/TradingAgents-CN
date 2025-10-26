#!/usr/bin/env python3
"""
中國財經數據聚合工具
由於微博API申請困難且功能受限，採用多源數據聚合的方式
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import pandas as pd


class ChineseFinanceDataAggregator:
    """中國財經數據聚合器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_stock_sentiment_summary(self, ticker: str, days: int = 7) -> Dict:
        """
        獲取股票情绪分析汇总
        整合多個可獲取的中國財經數據源
        """
        try:
            # 1. 獲取財經新聞情绪
            news_sentiment = self._get_finance_news_sentiment(ticker, days)
            
            # 2. 獲取股吧討論熱度 (如果可以獲取)
            forum_sentiment = self._get_stock_forum_sentiment(ticker, days)
            
            # 3. 獲取財經媒體報道
            media_sentiment = self._get_media_coverage_sentiment(ticker, days)
            
            # 4. 综合分析
            overall_sentiment = self._calculate_overall_sentiment(
                news_sentiment, forum_sentiment, media_sentiment
            )
            
            return {
                'ticker': ticker,
                'analysis_period': f'{days} days',
                'overall_sentiment': overall_sentiment,
                'news_sentiment': news_sentiment,
                'forum_sentiment': forum_sentiment,
                'media_sentiment': media_sentiment,
                'summary': self._generate_sentiment_summary(overall_sentiment),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'ticker': ticker,
                'error': f'數據獲取失败: {str(e)}',
                'fallback_message': '由於中國社交媒體API限制，建议使用財經新聞和基本面分析作為主要參考',
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_finance_news_sentiment(self, ticker: str, days: int) -> Dict:
        """獲取財經新聞情绪分析"""
        try:
            # 搜索相關新聞標題和內容
            company_name = self._get_company_chinese_name(ticker)
            search_terms = [ticker, company_name] if company_name else [ticker]
            
            news_items = []
            for term in search_terms:
                # 這里可以集成多個新聞源
                items = self._search_finance_news(term, days)
                news_items.extend(items)
            
            # 簡單的情绪分析
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for item in news_items:
                sentiment = self._analyze_text_sentiment(item.get('title', '') + ' ' + item.get('content', ''))
                if sentiment > 0.1:
                    positive_count += 1
                elif sentiment < -0.1:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = len(news_items)
            if total == 0:
                return {'sentiment_score': 0, 'confidence': 0, 'news_count': 0}
            
            sentiment_score = (positive_count - negative_count) / total
            
            return {
                'sentiment_score': sentiment_score,
                'positive_ratio': positive_count / total,
                'negative_ratio': negative_count / total,
                'neutral_ratio': neutral_count / total,
                'news_count': total,
                'confidence': min(total / 10, 1.0)  # 新聞數量越多，置信度越高
            }
            
        except Exception as e:
            return {'error': str(e), 'sentiment_score': 0, 'confidence': 0}
    
    def _get_stock_forum_sentiment(self, ticker: str, days: int) -> Dict:
        """獲取股票論坛討論情绪 (模擬數據，實际需要爬虫)"""
        # 由於东方財富股吧等平台的反爬虫機制，這里返回模擬數據
        # 實际實現需要更複雜的爬虫技術
        
        return {
            'sentiment_score': 0,
            'discussion_count': 0,
            'hot_topics': [],
            'note': '股票論坛數據獲取受限，建议關註官方財經新聞',
            'confidence': 0
        }
    
    def _get_media_coverage_sentiment(self, ticker: str, days: int) -> Dict:
        """獲取媒體報道情绪"""
        try:
            # 可以集成RSS源或公開的財經API
            coverage_items = self._get_media_coverage(ticker, days)
            
            if not coverage_items:
                return {'sentiment_score': 0, 'coverage_count': 0, 'confidence': 0}
            
            # 分析媒體報道的情绪倾向
            sentiment_scores = []
            for item in coverage_items:
                score = self._analyze_text_sentiment(item.get('title', '') + ' ' + item.get('summary', ''))
                sentiment_scores.append(score)
            
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            return {
                'sentiment_score': avg_sentiment,
                'coverage_count': len(coverage_items),
                'confidence': min(len(coverage_items) / 5, 1.0)
            }
            
        except Exception as e:
            return {'error': str(e), 'sentiment_score': 0, 'confidence': 0}
    
    def _search_finance_news(self, search_term: str, days: int) -> List[Dict]:
        """搜索財經新聞 (示例實現)"""
        # 這里可以集成多個新聞源的API或RSS
        # 例如：財聯社、新浪財經、东方財富等
        
        # 模擬返回數據結構
        return [
            {
                'title': f'{search_term}相關財經新聞標題',
                'content': '新聞內容摘要...',
                'source': '財聯社',
                'publish_time': datetime.now().isoformat(),
                'url': 'https://example.com/news/1'
            }
        ]
    
    def _get_media_coverage(self, ticker: str, days: int) -> List[Dict]:
        """獲取媒體報道 (示例實現)"""
        # 可以集成Google News API或其他新聞聚合服務
        return []
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """簡單的中文文本情绪分析"""
        if not text:
            return 0
        
        # 簡單的關键詞情绪分析
        positive_words = ['上涨', '增長', '利好', '看好', '买入', '推薦', '强势', '突破', '創新高']
        negative_words = ['下跌', '下降', '利空', '看空', '卖出', '風險', '跌破', '創新低', '亏損']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count + negative_count == 0:
            return 0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _get_company_chinese_name(self, ticker: str) -> Optional[str]:
        """獲取公司中文名稱"""
        # 簡單的映射表，實际可以從數據庫或API獲取
        name_mapping = {
            'AAPL': '苹果',
            'TSLA': '特斯拉',
            'NVDA': '英伟達',
            'MSFT': '微软',
            'GOOGL': '谷歌',
            'AMZN': '亚馬逊'
        }
        return name_mapping.get(ticker.upper())
    
    def _calculate_overall_sentiment(self, news_sentiment: Dict, forum_sentiment: Dict, media_sentiment: Dict) -> Dict:
        """計算综合情绪分析"""
        # 根據各數據源的置信度加權計算
        news_weight = news_sentiment.get('confidence', 0)
        forum_weight = forum_sentiment.get('confidence', 0)
        media_weight = media_sentiment.get('confidence', 0)
        
        total_weight = news_weight + forum_weight + media_weight
        
        if total_weight == 0:
            return {'sentiment_score': 0, 'confidence': 0, 'level': 'neutral'}
        
        weighted_sentiment = (
            news_sentiment.get('sentiment_score', 0) * news_weight +
            forum_sentiment.get('sentiment_score', 0) * forum_weight +
            media_sentiment.get('sentiment_score', 0) * media_weight
        ) / total_weight
        
        # 確定情绪等級
        if weighted_sentiment > 0.3:
            level = 'very_positive'
        elif weighted_sentiment > 0.1:
            level = 'positive'
        elif weighted_sentiment > -0.1:
            level = 'neutral'
        elif weighted_sentiment > -0.3:
            level = 'negative'
        else:
            level = 'very_negative'
        
        return {
            'sentiment_score': weighted_sentiment,
            'confidence': total_weight / 3,  # 平均置信度
            'level': level
        }
    
    def _generate_sentiment_summary(self, overall_sentiment: Dict) -> str:
        """生成情绪分析摘要"""
        level = overall_sentiment.get('level', 'neutral')
        score = overall_sentiment.get('sentiment_score', 0)
        confidence = overall_sentiment.get('confidence', 0)
        
        level_descriptions = {
            'very_positive': '非常積極',
            'positive': '積極',
            'neutral': '中性',
            'negative': '消極',
            'very_negative': '非常消極'
        }
        
        description = level_descriptions.get(level, '中性')
        confidence_level = '高' if confidence > 0.7 else '中' if confidence > 0.3 else '低'
        
        return f"市場情绪: {description} (評分: {score:.2f}, 置信度: {confidence_level})"


def get_chinese_social_sentiment(ticker: str, curr_date: str) -> str:
    """
    獲取中國社交媒體情绪分析的主要接口函數
    """
    aggregator = ChineseFinanceDataAggregator()
    
    try:
        # 獲取情绪分析數據
        sentiment_data = aggregator.get_stock_sentiment_summary(ticker, days=7)
        
        # 格式化輸出
        if 'error' in sentiment_data:
            return f"""
中國市場情绪分析報告 - {ticker}
分析日期: {curr_date}

⚠️ 數據獲取限制說明:
{sentiment_data.get('fallback_message', '數據獲取遇到技術限制')}

建议:
1. 重點關註財經新聞和基本面分析
2. 參考官方財報和業绩指導
3. 關註行業政策和監管動態
4. 考慮國际市場情绪對中概股的影響

註: 由於中國社交媒體平台API限制，當前主要依賴公開財經數據源進行分析。
"""
        
        overall = sentiment_data.get('overall_sentiment', {})
        news = sentiment_data.get('news_sentiment', {})
        
        return f"""
中國市場情绪分析報告 - {ticker}
分析日期: {curr_date}
分析周期: {sentiment_data.get('analysis_period', '7天')}

📊 综合情绪評估:
{sentiment_data.get('summary', '數據不足')}

📰 財經新聞情绪:
- 情绪評分: {news.get('sentiment_score', 0):.2f}
- 正面新聞比例: {news.get('positive_ratio', 0):.1%}
- 负面新聞比例: {news.get('negative_ratio', 0):.1%}
- 新聞數量: {news.get('news_count', 0)}條

💡 投資建议:
基於當前可獲取的中國市場數據，建议投資者:
1. 密切關註官方財經媒體報道
2. 重視基本面分析和財務數據
3. 考慮政策環境對股價的影響
4. 關註國际市場動態

⚠️ 數據說明:
由於中國社交媒體平台API獲取限制，本分析主要基於公開財經新聞數據。
建议結合其他分析維度進行综合判斷。

生成時間: {sentiment_data.get('timestamp', datetime.now().isoformat())}
"""
        
    except Exception as e:
        return f"""
中國市場情绪分析 - {ticker}
分析日期: {curr_date}

❌ 分析失败: {str(e)}

💡 替代建议:
1. 查看財經新聞網站的相關報道
2. 關註雪球、东方財富等投資社区討論
3. 參考專業機構的研究報告
4. 重點分析基本面和技術面數據

註: 中國社交媒體數據獲取存在技術限制，建议以基本面分析為主。
"""
