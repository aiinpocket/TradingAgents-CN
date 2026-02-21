"""
新聞相關性過濾器
用於過濾與特定股票/公司不相關的新聞，提高新聞分析質量
"""

import pandas as pd
import re
from typing import List, Dict, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NewsRelevanceFilter:
    """基於規則的新聞相關性過濾器"""
    
    def __init__(self, stock_code: str, company_name: str):
        """
        初始化過濾器
        
        Args:
            stock_code: 股票代碼，如 "600036"
            company_name: 公司名稱，如 "招商銀行"
        """
        self.stock_code = stock_code.upper()
        self.company_name = company_name
        
        # 排除關鍵詞 - 這些詞出現時降低相關性
        self.exclude_keywords = [
            'etf', '指數基金', '基金', '指數', 'index', 'fund',
            '權重股', '成分股', '板塊', '概念股', '主題基金',
            '跟蹤指數', '被動投資', '指數投資', '基金持倉'
        ]
        
        # 包含關鍵詞 - 這些詞出現時提高相關性
        self.include_keywords = [
            '業績', '財報', '公告', '重組', '並購', '分紅', '派息',
            '高管', '董事', '股東', '增持', '減持', '回購',
            '年報', '季報', '半年報', '業績預告', '業績快報',
            '股東大會', '董事會', '監事會', '重大合同',
            '投資', '收購', '出售', '轉讓', '合作', '協議'
        ]
        
        # 強相關關鍵詞 - 這些詞出現時大幅提高相關性
        self.strong_keywords = [
            '停牌', '複牌', '漲停', '跌停', '限售解禁',
            '股權激勵', '員工持股', '定增', '配股', '送股',
            '資產重組', '借殼上市', '退市', '摘帽', 'ST'
        ]
    
    def calculate_relevance_score(self, title: str, content: str) -> float:
        """
        計算新聞相關性評分
        
        Args:
            title: 新聞標題
            content: 新聞內容
            
        Returns:
            float: 相關性評分 (0-100)
        """
        score = 0
        title_lower = title.lower()
        content_lower = content.lower()
        
        # 1. 直接提及公司名稱
        if self.company_name in title:
            score += 50  # 標題中出現公司名稱，高分
            logger.debug(f"[過濾器] 標題包含公司名稱 '{self.company_name}': +50分")
        elif self.company_name in content:
            score += 25  # 內容中出現公司名稱，中等分
            logger.debug(f"[過濾器] 內容包含公司名稱 '{self.company_name}': +25分")
            
        # 2. 直接提及股票代碼
        if self.stock_code in title:
            score += 40  # 標題中出現股票代碼，高分
            logger.debug(f"[過濾器] 標題包含股票代碼 '{self.stock_code}': +40分")
        elif self.stock_code in content:
            score += 20  # 內容中出現股票代碼，中等分
            logger.debug(f"[過濾器] 內容包含股票代碼 '{self.stock_code}': +20分")
            
        # 3. 強相關關鍵詞檢查
        strong_matches = []
        for keyword in self.strong_keywords:
            if keyword in title_lower:
                score += 30
                strong_matches.append(keyword)
            elif keyword in content_lower:
                score += 15
                strong_matches.append(keyword)
        
        if strong_matches:
            logger.debug(f"[過濾器] 強相關關鍵詞匹配: {strong_matches}")
            
        # 4. 包含關鍵詞檢查
        include_matches = []
        for keyword in self.include_keywords:
            if keyword in title_lower:
                score += 15
                include_matches.append(keyword)
            elif keyword in content_lower:
                score += 8
                include_matches.append(keyword)
        
        if include_matches:
            logger.debug(f"[過濾器] 相關關鍵詞匹配: {include_matches[:3]}...")  # 只顯示前3個
            
        # 5. 排除關鍵詞檢查（減分）
        exclude_matches = []
        for keyword in self.exclude_keywords:
            if keyword in title_lower:
                score -= 40  # 標題中出現排除詞，大幅減分
                exclude_matches.append(keyword)
            elif keyword in content_lower:
                score -= 20  # 內容中出現排除詞，中等減分
                exclude_matches.append(keyword)
        
        if exclude_matches:
            logger.debug(f"[過濾器] 排除關鍵詞匹配: {exclude_matches[:3]}...")
            
        # 6. 特殊規則：如果標題完全不包含公司信息但包含排除詞，嚴重減分
        if (self.company_name not in title and self.stock_code not in title and 
            any(keyword in title_lower for keyword in self.exclude_keywords)):
            score -= 30
            logger.debug(f"[過濾器] 標題無公司信息但含排除詞: -30分")
        
        # 確保評分在0-100範圍內
        final_score = max(0, min(100, score))
        
        logger.debug(f"[過濾器] 最終評分: {final_score}分 - 標題: {title[:30]}...")
        
        return final_score
    
    def filter_news(self, news_df: pd.DataFrame, min_score: float = 30) -> pd.DataFrame:
        """
        過濾新聞DataFrame
        
        Args:
            news_df: 原始新聞DataFrame
            min_score: 最低相關性評分閾值
            
        Returns:
            pd.DataFrame: 過濾後的新聞DataFrame，按相關性評分排序
        """
        if news_df.empty:
            logger.warning("[過濾器] 輸入新聞DataFrame為空")
            return news_df
        
        logger.info(f"[過濾器] 開始過濾新聞，原始數量: {len(news_df)}條，最低評分閾值: {min_score}")
        
        filtered_news = []
        
        for idx, row in news_df.iterrows():
            title = row.get('新聞標題', row.get('標題', ''))
            content = row.get('新聞內容', row.get('內容', ''))
            
            # 計算相關性評分
            score = self.calculate_relevance_score(title, content)
            
            if score >= min_score:
                row_dict = row.to_dict()
                row_dict['relevance_score'] = score
                filtered_news.append(row_dict)
                
                logger.debug(f"[過濾器] 保留新聞 (評分: {score:.1f}): {title[:50]}...")
            else:
                logger.debug(f"[過濾器] 過濾新聞 (評分: {score:.1f}): {title[:50]}...")
        
        # 創建過濾後的DataFrame
        if filtered_news:
            filtered_df = pd.DataFrame(filtered_news)
            # 按相關性評分排序
            filtered_df = filtered_df.sort_values('relevance_score', ascending=False)
            logger.info(f"[過濾器] 過濾完成，保留 {len(filtered_df)}條 新聞")
        else:
            filtered_df = pd.DataFrame()
            logger.warning(f"[過濾器] 所有新聞都被過濾，無符合條件的新聞")
            
        return filtered_df
    
    def get_filter_statistics(self, original_df: pd.DataFrame, filtered_df: pd.DataFrame) -> Dict:
        """
        獲取過濾統計信息
        
        Args:
            original_df: 原始新聞DataFrame
            filtered_df: 過濾後新聞DataFrame
            
        Returns:
            Dict: 統計信息
        """
        stats = {
            'original_count': len(original_df),
            'filtered_count': len(filtered_df),
            'filter_rate': (len(original_df) - len(filtered_df)) / len(original_df) * 100 if len(original_df) > 0 else 0,
            'avg_score': filtered_df['relevance_score'].mean() if not filtered_df.empty else 0,
            'max_score': filtered_df['relevance_score'].max() if not filtered_df.empty else 0,
            'min_score': filtered_df['relevance_score'].min() if not filtered_df.empty else 0
        }
        
        return stats


# 股票代碼到公司名稱的映射（美股）
STOCK_COMPANY_MAPPING = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.',
    'TSLA': 'Tesla Inc.',
    'BRK.B': 'Berkshire Hathaway',
    'JPM': 'JPMorgan Chase',
    'V': 'Visa Inc.',
    'JNJ': 'Johnson & Johnson',
    'WMT': 'Walmart Inc.',
    'PG': 'Procter & Gamble',
    'MA': 'Mastercard Inc.',
    'UNH': 'UnitedHealth Group',
    'HD': 'The Home Depot',
    'DIS': 'The Walt Disney Company',
    'NFLX': 'Netflix Inc.',
    'AMD': 'Advanced Micro Devices',
    'INTC': 'Intel Corporation',
}

def get_company_name(ticker: str) -> str:
    """
    獲取股票代碼對應的公司名稱
    
    Args:
        ticker: 股票代碼
        
    Returns:
        str: 公司名稱
    """
    # 清理股票代碼（移除後缀）
    clean_ticker = ticker.split('.')[0]
    
    company_name = STOCK_COMPANY_MAPPING.get(clean_ticker)
    
    if company_name:
        logger.debug(f"[公司映射] {ticker} -> {company_name}")
        return company_name
    else:
        # 如果沒有映射，返回默認名稱
        default_name = f"股票{clean_ticker}"
        logger.warning(f"[公司映射] 未找到 {ticker} 的公司名稱映射，使用默認: {default_name}")
        return default_name


def create_news_filter(ticker: str) -> NewsRelevanceFilter:
    """
    創建新聞過濾器的便捷函數
    
    Args:
        ticker: 股票代碼
        
    Returns:
        NewsRelevanceFilter: 配置好的過濾器實例
    """
    company_name = get_company_name(ticker)
    return NewsRelevanceFilter(ticker, company_name)


# 使用示例
if __name__ == "__main__":
    # 測試過濾器
    import pandas as pd
    
    # 模擬新聞數據
    test_news = pd.DataFrame([
        {
            '新聞標題': '招商銀行發布2024年第三季度業績報告',
            '新聞內容': '招商銀行今日發布第三季度財報，淨利潤同比增長8%...'
        },
        {
            '新聞標題': '上證180ETF指數基金（530280）自帶槓鈴策略',
            '新聞內容': '數據顯示，上證180指數前十大權重股分別為貴州茅台、招商銀行600036...'
        },
        {
            '新聞標題': '銀行ETF指數(512730多只成分股上漲',
            '新聞內容': '銀行板塊今日表現強勢，招商銀行、工商銀行等多只成分股上漲...'
        }
    ])
    
    # 創建過濾器
    filter = create_news_filter('600036')
    
    # 過濾新聞
    filtered_news = filter.filter_news(test_news, min_score=30)
    
    print(f"原始新聞: {len(test_news)}條")
    print(f"過濾後新聞: {len(filtered_news)}條")
    
    if not filtered_news.empty:
        print("\n過濾後的新聞:")
        for _, row in filtered_news.iterrows():
            print(f"- {row['新聞標題']} (評分: {row['relevance_score']:.1f})")