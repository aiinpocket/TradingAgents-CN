"""
增强新聞過濾器 - 集成本地小模型和規則過濾
支持多種過濾策略：規則過濾、語義相似度、本地分類模型
"""

import pandas as pd
import re
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import numpy as np

# 導入基础過濾器
from .news_filter import NewsRelevanceFilter, create_news_filter, get_company_name

logger = logging.getLogger(__name__)

class EnhancedNewsFilter(NewsRelevanceFilter):
    """增强新聞過濾器，集成本地模型和多種過濾策略"""
    
    def __init__(self, stock_code: str, company_name: str, use_semantic: bool = True, use_local_model: bool = False):
        """
        初始化增强過濾器
        
        Args:
            stock_code: 股票代碼
            company_name: 公司名稱
            use_semantic: 是否使用語義相似度過濾
            use_local_model: 是否使用本地分類模型
        """
        super().__init__(stock_code, company_name)
        self.use_semantic = use_semantic
        self.use_local_model = use_local_model
        
        # 語義模型相關
        self.sentence_model = None
        self.company_embedding = None
        
        # 本地分類模型相關
        self.classification_model = None
        self.tokenizer = None
        
        # 初始化模型
        if use_semantic:
            self._init_semantic_model()
        if use_local_model:
            self._init_classification_model()
    
    def _init_semantic_model(self):
        """初始化語義相似度模型"""
        try:
            logger.info("[增强過濾器] 正在加載語義相似度模型...")
            
            # 嘗試使用sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
                
                # 使用轻量級中文模型
                model_name = "paraphrase-multilingual-MiniLM-L12-v2"  # 支持中文的轻量級模型
                self.sentence_model = SentenceTransformer(model_name)
                
                # 預計算公司相關的embedding
                company_texts = [
                    self.company_name,
                    f"{self.company_name}股票",
                    f"{self.company_name}公司",
                    f"{self.stock_code}",
                    f"{self.company_name}業绩",
                    f"{self.company_name}財報"
                ]
                
                self.company_embedding = self.sentence_model.encode(company_texts)
                logger.info(f"[增强過濾器] ✅ 語義模型加載成功: {model_name}")
                
            except ImportError:
                logger.warning("[增强過濾器] sentence-transformers未安裝，跳過語義過濾")
                self.use_semantic = False
                
        except Exception as e:
            logger.error(f"[增强過濾器] 語義模型初始化失败: {e}")
            self.use_semantic = False
    
    def _init_classification_model(self):
        """初始化本地分類模型"""
        try:
            logger.info("[增强過濾器] 正在加載本地分類模型...")
            
            # 嘗試使用transformers庫的中文分類模型
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch
                
                # 使用轻量級中文文本分類模型
                model_name = "uer/roberta-base-finetuned-chinanews-chinese"
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.classification_model = AutoModelForSequenceClassification.from_pretrained(model_name)
                
                logger.info(f"[增强過濾器] ✅ 分類模型加載成功: {model_name}")
                
            except ImportError:
                logger.warning("[增强過濾器] transformers未安裝，跳過本地模型分類")
                self.use_local_model = False
                
        except Exception as e:
            logger.error(f"[增强過濾器] 本地分類模型初始化失败: {e}")
            self.use_local_model = False
    
    def calculate_semantic_similarity(self, title: str, content: str) -> float:
        """
        計算語義相似度評分
        
        Args:
            title: 新聞標題
            content: 新聞內容
            
        Returns:
            float: 語義相似度評分 (0-100)
        """
        if not self.use_semantic or self.sentence_model is None:
            return 0
        
        try:
            # 組合標題和內容的前200字符
            text = f"{title} {content[:200]}"
            
            # 計算文本embedding
            text_embedding = self.sentence_model.encode([text])
            
            # 計算与公司相關文本的相似度
            similarities = []
            for company_emb in self.company_embedding:
                similarity = np.dot(text_embedding[0], company_emb) / (
                    np.linalg.norm(text_embedding[0]) * np.linalg.norm(company_emb)
                )
                similarities.append(similarity)
            
            # 取最高相似度
            max_similarity = max(similarities)
            
            # 轉換為0-100評分
            semantic_score = max(0, min(100, max_similarity * 100))
            
            logger.debug(f"[增强過濾器] 語義相似度評分: {semantic_score:.1f}")
            return semantic_score
            
        except Exception as e:
            logger.error(f"[增强過濾器] 語義相似度計算失败: {e}")
            return 0
    
    def classify_news_relevance(self, title: str, content: str) -> float:
        """
        使用本地模型分類新聞相關性
        
        Args:
            title: 新聞標題
            content: 新聞內容
            
        Returns:
            float: 分類相關性評分 (0-100)
        """
        if not self.use_local_model or self.classification_model is None:
            return 0
        
        try:
            import torch
            
            # 構建分類文本
            text = f"{title} {content[:300]}"
            
            # 添加公司信息作為上下文
            context_text = f"關於{self.company_name}({self.stock_code})的新聞: {text}"
            
            # 分詞和編碼
            inputs = self.tokenizer(
                context_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # 模型推理
            with torch.no_grad():
                outputs = self.classification_model(**inputs)
                logits = outputs.logits
                
                # 使用softmax獲取概率分布
                probabilities = torch.softmax(logits, dim=-1)
                
                # 假設第一個類別是"相關"，第二個是"不相關"
                # 這里需要根據具體模型調整
                relevance_prob = probabilities[0][0].item()  # 相關性概率
                
                # 轉換為0-100評分
                classification_score = relevance_prob * 100
                
                logger.debug(f"[增强過濾器] 分類模型評分: {classification_score:.1f}")
                return classification_score
                
        except Exception as e:
            logger.error(f"[增强過濾器] 本地模型分類失败: {e}")
            return 0
    
    def calculate_enhanced_relevance_score(self, title: str, content: str) -> Dict[str, float]:
        """
        計算增强相關性評分（综合多種方法）
        
        Args:
            title: 新聞標題
            content: 新聞內容
            
        Returns:
            Dict: 包含各種評分的字典
        """
        scores = {}
        
        # 1. 基础規則評分
        rule_score = super().calculate_relevance_score(title, content)
        scores['rule_score'] = rule_score
        
        # 2. 語義相似度評分
        if self.use_semantic:
            semantic_score = self.calculate_semantic_similarity(title, content)
            scores['semantic_score'] = semantic_score
        else:
            scores['semantic_score'] = 0
        
        # 3. 本地模型分類評分
        if self.use_local_model:
            classification_score = self.classify_news_relevance(title, content)
            scores['classification_score'] = classification_score
        else:
            scores['classification_score'] = 0
        
        # 4. 综合評分（加權平均）
        weights = {
            'rule': 0.4,      # 規則過濾權重40%
            'semantic': 0.35,  # 語義相似度權重35%
            'classification': 0.25  # 分類模型權重25%
        }
        
        final_score = (
            weights['rule'] * rule_score +
            weights['semantic'] * scores['semantic_score'] +
            weights['classification'] * scores['classification_score']
        )
        
        scores['final_score'] = final_score
        
        logger.debug(f"[增强過濾器] 综合評分 - 規則:{rule_score:.1f}, 語義:{scores['semantic_score']:.1f}, "
                    f"分類:{scores['classification_score']:.1f}, 最终:{final_score:.1f}")
        
        return scores
    
    def filter_news_enhanced(self, news_df: pd.DataFrame, min_score: float = 40) -> pd.DataFrame:
        """
        增强新聞過濾
        
        Args:
            news_df: 原始新聞DataFrame
            min_score: 最低综合評分阈值
            
        Returns:
            pd.DataFrame: 過濾後的新聞DataFrame，包含詳細評分信息
        """
        if news_df.empty:
            logger.warning("[增强過濾器] 輸入新聞DataFrame為空")
            return news_df
        
        logger.info(f"[增强過濾器] 開始增强過濾，原始數量: {len(news_df)}條，最低評分阈值: {min_score}")
        
        filtered_news = []
        
        for idx, row in news_df.iterrows():
            title = row.get('新聞標題', row.get('標題', ''))
            content = row.get('新聞內容', row.get('內容', ''))
            
            # 計算增强評分
            scores = self.calculate_enhanced_relevance_score(title, content)
            
            if scores['final_score'] >= min_score:
                row_dict = row.to_dict()
                row_dict.update(scores)  # 添加所有評分信息
                filtered_news.append(row_dict)
                
                logger.debug(f"[增强過濾器] 保留新聞 (综合評分: {scores['final_score']:.1f}): {title[:50]}...")
            else:
                logger.debug(f"[增强過濾器] 過濾新聞 (综合評分: {scores['final_score']:.1f}): {title[:50]}...")
        
        # 創建過濾後的DataFrame
        if filtered_news:
            filtered_df = pd.DataFrame(filtered_news)
            # 按综合評分排序
            filtered_df = filtered_df.sort_values('final_score', ascending=False)
            logger.info(f"[增强過濾器] 增强過濾完成，保留 {len(filtered_df)}條 新聞")
        else:
            filtered_df = pd.DataFrame()
            logger.warning(f"[增强過濾器] 所有新聞都被過濾，無符合條件的新聞")
            
        return filtered_df


def create_enhanced_news_filter(ticker: str, use_semantic: bool = True, use_local_model: bool = False) -> EnhancedNewsFilter:
    """
    創建增强新聞過濾器的便捷函數
    
    Args:
        ticker: 股票代碼
        use_semantic: 是否使用語義相似度過濾
        use_local_model: 是否使用本地分類模型
        
    Returns:
        EnhancedNewsFilter: 配置好的增强過濾器實例
    """
    company_name = get_company_name(ticker)
    return EnhancedNewsFilter(ticker, company_name, use_semantic, use_local_model)


# 使用示例
if __name__ == "__main__":
    # 測試增强過濾器
    import pandas as pd
    
    # 模擬新聞數據
    test_news = pd.DataFrame([
        {
            '新聞標題': '招商銀行發布2024年第三季度業绩報告',
            '新聞內容': '招商銀行今日發布第三季度財報，净利润同比增長8%，資產质量持续改善...'
        },
        {
            '新聞標題': '上證180ETF指數基金（530280）自帶杠铃策略',
            '新聞內容': '數據顯示，上證180指數前十大權重股分別為贵州茅台、招商銀行600036...'
        },
        {
            '新聞標題': '銀行ETF指數(512730)多只成分股上涨',
            '新聞內容': '銀行板塊今日表現强势，招商銀行、工商銀行等多只成分股上涨...'
        },
        {
            '新聞標題': '招商銀行与某科技公司簽署战略合作協议',
            '新聞內容': '招商銀行宣布与知名科技公司達成战略合作，将在數字化轉型方面深度合作...'
        }
    ])
    
    print("=== 測試增强新聞過濾器 ===")
    
    # 創建增强過濾器（仅使用規則過濾，避免模型依賴）
    enhanced_filter = create_enhanced_news_filter('600036', use_semantic=False, use_local_model=False)
    
    # 過濾新聞
    filtered_news = enhanced_filter.filter_news_enhanced(test_news, min_score=30)
    
    print(f"原始新聞: {len(test_news)}條")
    print(f"過濾後新聞: {len(filtered_news)}條")
    
    if not filtered_news.empty:
        print("\n過濾後的新聞:")
        for _, row in filtered_news.iterrows():
            print(f"- {row['新聞標題']} (综合評分: {row['final_score']:.1f})")
            print(f"  規則評分: {row['rule_score']:.1f}, 語義評分: {row['semantic_score']:.1f}, 分類評分: {row['classification_score']:.1f}")