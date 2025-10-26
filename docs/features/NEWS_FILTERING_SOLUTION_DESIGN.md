# 新聞過濾方案設計文档

## 🎯 目標

為TradingAgents系統設計並實現一個高效的新聞過濾機制，解決东方財富新聞API返回低质量、不相關新聞的問題，提高新聞分析師的分析质量。

## 🔍 可行方案分析

### 方案1: 基於規則的過濾器 (推薦 - 立即可行)

**優势:**
- ✅ 無需額外依賴，基於現有Python庫
- ✅ 實現簡單，維護成本低
- ✅ 執行速度快，几乎無延迟
- ✅ 可解釋性强，規則透明
- ✅ 資源消耗極低

**實現方案:**
```python
class NewsRelevanceFilter:
    def __init__(self, stock_code: str, company_name: str):
        self.stock_code = stock_code
        self.company_name = company_name
        self.exclude_keywords = [
            'etf', '指數基金', '基金', '指數', 'index', 'fund',
            '權重股', '成分股', '板塊', '概念股'
        ]
        self.include_keywords = [
            '業绩', '財報', '公告', '重組', '並購', '分红',
            '高管', '董事', '股东', '增持', '减持', '回購'
        ]
    
    def calculate_relevance_score(self, title: str, content: str) -> float:
        """計算新聞相關性評分 (0-100)"""
        score = 0
        title_lower = title.lower()
        content_lower = content.lower()
        
        # 直接提及公司 (+40分)
        if self.company_name in title:
            score += 40
        elif self.company_name in content:
            score += 20
            
        # 直接提及股票代碼 (+30分)
        if self.stock_code in title:
            score += 30
        elif self.stock_code in content:
            score += 15
            
        # 包含公司相關關键詞 (+20分)
        for keyword in self.include_keywords:
            if keyword in title_lower:
                score += 10
            elif keyword in content_lower:
                score += 5
                
        # 排除不相關內容 (-30分)
        for keyword in self.exclude_keywords:
            if keyword in title_lower:
                score -= 30
            elif keyword in content_lower:
                score -= 15
                
        return max(0, min(100, score))
    
    def filter_news(self, news_df: pd.DataFrame, min_score: float = 30) -> pd.DataFrame:
        """過濾新聞，返回相關性評分高於阈值的新聞"""
        filtered_news = []
        
        for _, row in news_df.iterrows():
            title = row.get('新聞標題', '')
            content = row.get('新聞內容', '')
            
            score = self.calculate_relevance_score(title, content)
            
            if score >= min_score:
                row_dict = row.to_dict()
                row_dict['relevance_score'] = score
                filtered_news.append(row_dict)
        
        # 按相關性評分排序
        filtered_df = pd.DataFrame(filtered_news)
        if not filtered_df.empty:
            filtered_df = filtered_df.sort_values('relevance_score', ascending=False)
            
        return filtered_df
```

### 方案2: 轻量級本地模型 (中期方案)

**使用sentence-transformers進行語義相似度計算:**

```python
# 需要添加到requirements.txt
# sentence-transformers>=2.2.0

from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticNewsFilter:
    def __init__(self, stock_code: str, company_name: str):
        self.stock_code = stock_code
        self.company_name = company_name
        # 使用中文優化的轻量級模型
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # 定義目標語義
        self.target_semantics = [
            f"{company_name}公司新聞",
            f"{company_name}業绩財報",
            f"{company_name}重大公告",
            f"{stock_code}股票新聞"
        ]
        self.target_embeddings = self.model.encode(self.target_semantics)
    
    def calculate_semantic_similarity(self, text: str) -> float:
        """計算文本与目標語義的相似度"""
        text_embedding = self.model.encode([text])
        similarities = np.dot(text_embedding, self.target_embeddings.T)
        return float(np.max(similarities))
    
    def filter_news_semantic(self, news_df: pd.DataFrame, threshold: float = 0.3) -> pd.DataFrame:
        """基於語義相似度過濾新聞"""
        filtered_news = []
        
        for _, row in news_df.iterrows():
            title = row.get('新聞標題', '')
            content = row.get('新聞內容', '')
            
            # 計算標題和內容的語義相似度
            title_sim = self.calculate_semantic_similarity(title)
            content_sim = self.calculate_semantic_similarity(content[:200])  # 限制內容長度
            
            max_similarity = max(title_sim, content_sim)
            
            if max_similarity >= threshold:
                row_dict = row.to_dict()
                row_dict['semantic_score'] = max_similarity
                filtered_news.append(row_dict)
        
        filtered_df = pd.DataFrame(filtered_news)
        if not filtered_df.empty:
            filtered_df = filtered_df.sort_values('semantic_score', ascending=False)
            
        return filtered_df
```

### 方案3: 本地小模型分類 (長期方案)

**使用transformers庫的中文分類模型:**

```python
# 需要添加到requirements.txt
# transformers>=4.30.0
# torch>=2.0.0

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

class LocalModelNewsClassifier:
    def __init__(self):
        # 使用中文文本分類模型
        self.classifier = pipeline(
            "text-classification",
            model="uer/roberta-base-finetuned-chinanews-chinese",
            tokenizer="uer/roberta-base-finetuned-chinanews-chinese"
        )
    
    def classify_news_relevance(self, title: str, content: str, company_name: str) -> dict:
        """分類新聞相關性"""
        # 構建分類文本
        text = f"公司：{company_name}。新聞：{title}。{content[:100]}"
        
        # 進行分類
        result = self.classifier(text)
        
        return {
            'is_relevant': result[0]['label'] == 'RELEVANT',
            'confidence': result[0]['score'],
            'classification': result[0]['label']
        }
```

### 方案4: 混合過濾策略 (最優方案)

**結合規則過濾和語義分析:**

```python
class HybridNewsFilter:
    def __init__(self, stock_code: str, company_name: str):
        self.rule_filter = NewsRelevanceFilter(stock_code, company_name)
        self.semantic_filter = SemanticNewsFilter(stock_code, company_name)
    
    def comprehensive_filter(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """综合過濾策略"""
        # 第一步：規則過濾（快速筛選）
        rule_filtered = self.rule_filter.filter_news(news_df, min_score=20)
        
        if rule_filtered.empty:
            return rule_filtered
        
        # 第二步：語義過濾（精確筛選）
        semantic_filtered = self.semantic_filter.filter_news_semantic(
            rule_filtered, threshold=0.25
        )
        
        # 第三步：综合評分
        if not semantic_filtered.empty:
            semantic_filtered['final_score'] = (
                semantic_filtered['relevance_score'] * 0.6 + 
                semantic_filtered['semantic_score'] * 100 * 0.4
            )
            semantic_filtered = semantic_filtered.sort_values('final_score', ascending=False)
        
        return semantic_filtered
```

## 🚀 實施計劃

### 階段1: 立即實施 (1-2天)
1. **實現基於規則的過濾器**
2. **集成到現有新聞獲取流程**
3. **添加過濾日誌和統計**

### 階段2: 中期優化 (1周)
1. **添加sentence-transformers依賴**
2. **實現語義相似度過濾**
3. **混合過濾策略測試**

### 階段3: 長期改進 (2-3周)
1. **本地分類模型集成**
2. **過濾效果評估體系**
3. **自適應阈值調整**

## 📊 性能對比

| 方案 | 實施難度 | 資源消耗 | 過濾精度 | 執行速度 | 推薦度 |
|------|----------|----------|----------|----------|--------|
| 規則過濾 | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 語義相似度 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 本地分類模型 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 混合策略 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🔧 集成方案

### 修改現有代碼

**1. 修改 `realtime_news_utils.py`:**
```python
# 在get_realtime_stock_news函數中添加過濾逻辑
def get_realtime_stock_news(ticker: str, curr_date: str, hours_back: int = 6):
    # ... 現有代碼 ...
    
    # 獲取新聞後添加過濾
    if news_df is not None and not news_df.empty:
        # 獲取公司名稱
        company_name = get_company_name(ticker)  # 需要實現
        
        # 創建過濾器
        filter = NewsRelevanceFilter(ticker, company_name)
        
        # 過濾新聞
        filtered_df = filter.filter_news(news_df, min_score=30)
        
        logger.info(f"[新聞過濾] 原始新聞: {len(news_df)}條, 過濾後: {len(filtered_df)}條")
        
        if not filtered_df.empty:
            news_df = filtered_df
        else:
            logger.warning(f"[新聞過濾] 所有新聞被過濾，保留原始數據")
    
    # ... 繼续現有逻辑 ...
```

**2. 添加公司名稱映射:**
```python
# 創建股票代碼到公司名稱的映射
STOCK_COMPANY_MAPPING = {
    '600036': '招商銀行',
    '000858': '五粮液',
    '000001': '平安銀行',
    # ... 更多映射
}

def get_company_name(ticker: str) -> str:
    """獲取股票對應的公司名稱"""
    return STOCK_COMPANY_MAPPING.get(ticker, f"股票{ticker}")
```

## 📈 預期效果

### 過濾前 (招商銀行600036)
```
新聞標題:
1. 上證180ETF指數基金（530280）自帶杠铃策略
2. A500ETF基金(512050多股涨停
3. 銀行ETF指數(512730多只成分股上涨
```

### 過濾後 (預期)
```
新聞標題:
1. 招商銀行發布2024年第三季度業绩報告
2. 招商銀行董事會決议公告
3. 招商銀行獲得監管批準設立理財子公司
```

## 🎯 总結

**推薦方案**: 先實施**基於規則的過濾器**，後续逐步添加**語義相似度過濾**，最终形成**混合過濾策略**。

**核心優势**:
- 🚀 立即可用，無需額外依賴
- 💰 資源消耗低，執行速度快
- 🎯 针對性强，解決當前問題
- 🔧 易於維護和調試
- 📈 顯著提升新聞分析质量

這個方案可以有效解決當前东方財富新聞质量問題，让新聞分析師生成真正的"新聞分析報告"而非"综合投資分析報告"。