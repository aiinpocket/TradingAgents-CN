import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os
import threading
import hashlib
from typing import Dict, Optional

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger("agents.utils.memory")


class ChromaDBManager:
    """單例ChromaDB管理器，避免並發創建集合的衝突"""

    _instance = None
    _lock = threading.Lock()
    _collections: Dict[str, any] = {}
    _client = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ChromaDBManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            try:
                # 自動檢測作業系統版本並使用最優配置
                import platform
                system = platform.system()
                
                if system == "Windows":
                    # 使用改進的Windows 11檢測
                    from .chromadb_win11_config import is_windows_11
                    if is_windows_11():
                        # Windows 11 或更新版本，使用優化配置
                        from .chromadb_win11_config import get_win11_chromadb_client
                        self._client = get_win11_chromadb_client()
                        logger.info(f"[ChromaDB] Windows 11優化配置初始化完成 (構建號: {platform.version()})")
                    else:
                        # Windows 10 或更老版本，使用兼容配置
                        from .chromadb_win10_config import get_win10_chromadb_client
                        self._client = get_win10_chromadb_client()
                        logger.info("[ChromaDB] Windows 10兼容配置初始化完成")
                else:
                    # 非Windows系統，使用標準配置
                    settings = Settings(
                        allow_reset=True,
                        anonymized_telemetry=False,
                        is_persistent=False
                    )
                    self._client = chromadb.Client(settings)
                    logger.info(f"[ChromaDB] {system}標準配置初始化完成")
                
                self._initialized = True
            except Exception as e:
                logger.error(f"[ChromaDB] 初始化失敗: {e}")
                # 使用最簡單的配置作為備用
                try:
                    settings = Settings(
                        allow_reset=True,
                        anonymized_telemetry=False,  # 關鍵：禁用遙測
                        is_persistent=False
                    )
                    self._client = chromadb.Client(settings)
                    logger.info("[ChromaDB] 使用備用配置初始化完成")
                except Exception as backup_error:
                    # 最後的備用方案
                    self._client = chromadb.Client()
                    logger.warning(f"[ChromaDB] 使用最簡配置初始化: {backup_error}")
                self._initialized = True

    def get_or_create_collection(self, name: str):
        """線程安全地獲取或創建集合"""
        with self._lock:
            if name in self._collections:
                logger.info(f"[ChromaDB] 使用快取集合: {name}")
                return self._collections[name]

            try:
                # 嘗試獲取現有集合
                collection = self._client.get_collection(name=name)
                logger.info(f"[ChromaDB] 獲取現有集合: {name}")
            except Exception as e:
                try:
                    # 創建新集合
                    collection = self._client.create_collection(name=name)
                    logger.info(f"[ChromaDB] 創建新集合: {name}")
                except Exception as e:
                    # 可能是並發創建，再次嘗試獲取
                    try:
                        collection = self._client.get_collection(name=name)
                        logger.info(f"[ChromaDB] 並發創建後獲取集合: {name}")
                    except Exception as final_error:
                        logger.error(f"[ChromaDB] 集合操作失敗: {name}, 錯誤: {final_error}")
                        raise final_error

            # 快取集合
            self._collections[name] = collection
            return collection


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.config = config
        self.llm_provider = config.get("llm_provider", "openai").lower()

        # 配置向量快取的長度限制（向量快取預設啟用長度檢查）
        self.max_embedding_length = int(os.getenv('MAX_EMBEDDING_CONTENT_LENGTH', '50000'))  # 預設50K字符
        self.enable_embedding_length_check = os.getenv('ENABLE_EMBEDDING_LENGTH_CHECK', 'true').lower() == 'true'  # 向量快取預設啟用
        
        # 根據LLM提供商選擇嵌入模型和客戶端
        # 統一使用 OpenAI embedding
        # 初始化降級選項標誌
        self.fallback_available = False

        # 統一使用 OpenAI embedding
        if config["backend_url"] == "http://localhost:11434/v1":
            self.embedding = "nomic-embed-text"
            self.client = OpenAI(base_url=config["backend_url"])
        else:
            self.embedding = "text-embedding-3-small"
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.client = OpenAI(
                    api_key=openai_key,
                    base_url=config["backend_url"]
                )
            else:
                self.client = "DISABLED"
                logger.warning("未找到OPENAI_API_KEY，記憶功能已禁用")

        # 使用單例ChromaDB管理器
        self.chroma_manager = ChromaDBManager()
        self.situation_collection = self.chroma_manager.get_or_create_collection(name)

    def _smart_text_truncation(self, text, max_length=8192):
        """智能文本截斷，保持語義完整性和快取兼容性"""
        if len(text) <= max_length:
            return text, False  # 返回原文本和是否截斷的標誌
        
        # 嘗試在句子邊界截斷
        sentences = text.split('。')
        if len(sentences) > 1:
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + '。') <= max_length - 50:  # 留50字符餘量
                    truncated += sentence + '。'
                else:
                    break
            if len(truncated) > max_length // 2:  # 至少保留一半內容
                logger.info(f"智能截斷：在句子邊界截斷，保留{len(truncated)}/{len(text)}字符")
                return truncated, True
        
        # 嘗試在段落邊界截斷
        paragraphs = text.split('\n')
        if len(paragraphs) > 1:
            truncated = ""
            for paragraph in paragraphs:
                if len(truncated + paragraph + '\n') <= max_length - 50:
                    truncated += paragraph + '\n'
                else:
                    break
            if len(truncated) > max_length // 2:
                logger.info(f"智能截斷：在段落邊界截斷，保留{len(truncated)}/{len(text)}字符")
                return truncated, True
        
        # 最後選擇：保留前半部分和後半部分的關鍵資訊
        front_part = text[:max_length//2]
        back_part = text[-(max_length//2-100):]  # 留100字符給連接符
        truncated = front_part + "\n...[內容截斷]...\n" + back_part
        logger.warning(f"強制截斷：保留首尾關鍵資訊，{len(text)}字符截斷為{len(truncated)}字符")
        return truncated, True

    def get_embedding(self, text):
        """Get embedding for a text using the configured provider"""

        # 檢查記憶功能是否被禁用
        if self.client == "DISABLED":
            # 內存功能已禁用，返回空向量
            logger.debug("記憶功能已禁用，返回空向量")
            return [0.0] * 1024  # 返回1024維的零向量

        # 驗證輸入文本
        if not text or not isinstance(text, str):
            logger.warning("輸入文本為空或無效，返回空向量")
            return [0.0] * 1024

        text_length = len(text)
        if text_length == 0:
            logger.warning("輸入文本長度為0，返回空向量")
            return [0.0] * 1024
        
        # 檢查是否啟用長度限制
        if self.enable_embedding_length_check and text_length > self.max_embedding_length:
            logger.warning(f"文本過長({text_length:,}字符 > {self.max_embedding_length:,}字符)，跳過向量化")
            # 儲存跳過資訊
            self._last_text_info = {
                'original_length': text_length,
                'processed_length': 0,
                'was_truncated': False,
                'was_skipped': True,
                'provider': self.llm_provider,
                'strategy': 'length_limit_skip',
                'max_length': self.max_embedding_length
            }
            return [0.0] * 1024
        
        # 記錄文本資訊（不進行任何截斷）
        if text_length > 8192:
            logger.info(f"處理長文本: {text_length}字符，提供商: {self.llm_provider}")
        
        # 儲存文本處理資訊
        self._last_text_info = {
            'original_length': text_length,
            'processed_length': text_length,  # 不截斷，保持原長度
            'was_truncated': False,  # 永不截斷
            'was_skipped': False,
            'provider': self.llm_provider,
            'strategy': 'no_truncation_with_fallback'  # 標記策略
        }

        if True:
            # 使用OpenAI兼容的嵌入模型
            if self.client is None:
                logger.warning("嵌入客戶端未初始化，返回空向量")
                return [0.0] * 1024  # 返回空向量
            elif self.client == "DISABLED":
                # 內存功能已禁用，返回空向量
                logger.debug("內存功能已禁用，返回空向量")
                return [0.0] * 1024  # 返回1024維的零向量

            # 嘗試調用OpenAI兼容的embedding API
            try:
                response = self.client.embeddings.create(
                    model=self.embedding,
                    input=text
                )
                embedding = response.data[0].embedding
                logger.debug(f"{self.llm_provider} embedding成功，維度: {len(embedding)}")
                return embedding

            except Exception as e:
                error_str = str(e).lower()
                
                # 檢查是否為長度限制錯誤
                length_error_keywords = [
                    'token', 'length', 'too long', 'exceed', 'maximum', 'limit',
                    'context', 'input too large', 'request too large'
                ]
                
                is_length_error = any(keyword in error_str for keyword in length_error_keywords)
                
                if is_length_error:
                    # 長度限制錯誤：直接降級，不截斷重試
                    logger.warning(f"{self.llm_provider}長度限制: {str(e)}")
                    logger.info("為保證分析準確性，不截斷文本，記憶功能降級")
                else:
                    # 其他類型的錯誤
                    if 'attributeerror' in error_str:
                        logger.error(f"{self.llm_provider} API調用錯誤: {str(e)}")
                    elif 'connectionerror' in error_str or 'connection' in error_str:
                        logger.error(f"{self.llm_provider}網絡連接錯誤: {str(e)}")
                    elif 'timeout' in error_str:
                        logger.error(f"{self.llm_provider}請求超時: {str(e)}")
                    elif 'keyerror' in error_str:
                        logger.error(f"{self.llm_provider}響應格式錯誤: {str(e)}")
                    else:
                        logger.error(f"{self.llm_provider} embedding異常: {str(e)}")
                
                logger.warning("記憶功能降級，返回空向量")
                return [0.0] * 1024

    def get_embedding_config_status(self):
        """獲取向量快取配置狀態"""
        return {
            'enabled': self.enable_embedding_length_check,
            'max_embedding_length': self.max_embedding_length,
            'max_embedding_length_formatted': f"{self.max_embedding_length:,}字符",
            'provider': self.llm_provider,
            'client_status': 'DISABLED' if self.client == "DISABLED" else 'ENABLED'
        }

    def get_last_text_info(self):
        """獲取最後處理的文本資訊"""
        return getattr(self, '_last_text_info', None)

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using embeddings with smart truncation handling"""
        
        # 獲取當前情況的embedding
        query_embedding = self.get_embedding(current_situation)
        
        # 檢查是否為空向量（記憶功能被禁用或出錯）
        if all(x == 0.0 for x in query_embedding):
            logger.debug("查詢embedding為空向量，返回空結果")
            return []
        
        # 檢查是否有足夠的資料進行查詢
        collection_count = self.situation_collection.count()
        if collection_count == 0:
            logger.debug("記憶庫為空，返回空結果")
            return []
        
        # 調整查詢數量，不能超過集合中的文檔數量
        actual_n_matches = min(n_matches, collection_count)
        
        try:
            # 執行相似度查詢
            results = self.situation_collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_n_matches
            )
            
            # 處理查詢結果
            memories = []
            if results and 'documents' in results and results['documents']:
                documents = results['documents'][0]
                metadatas = results.get('metadatas', [[]])[0]
                distances = results.get('distances', [[]])[0]
                
                for i, doc in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    distance = distances[i] if i < len(distances) else 1.0
                    
                    memory_item = {
                        'situation': doc,
                        'recommendation': metadata.get('recommendation', ''),
                        'similarity': 1.0 - distance,  # 轉換為相似度分數
                        'distance': distance
                    }
                    memories.append(memory_item)
                
                # 記錄查詢資訊
                if hasattr(self, '_last_text_info') and self._last_text_info.get('was_truncated'):
                    logger.info(f"截斷文本查詢完成，找到{len(memories)}個相關記憶")
                    logger.debug(f"原文長度: {self._last_text_info['original_length']}, "
                               f"處理後長度: {self._last_text_info['processed_length']}")
                else:
                    logger.debug(f"記憶查詢完成，找到{len(memories)}個相關記憶")
            
            return memories
            
        except Exception as e:
            logger.error(f"記憶查詢失敗: {str(e)}")
            return []

    def get_cache_info(self):
        """獲取快取相關資訊，用於調試和監控"""
        info = {
            'collection_count': self.situation_collection.count(),
            'client_status': 'enabled' if self.client != "DISABLED" else 'disabled',
            'embedding_model': self.embedding,
            'provider': self.llm_provider
        }
        
        # 添加最後一次文本處理資訊
        if hasattr(self, '_last_text_info'):
            info['last_text_processing'] = self._last_text_info
            
        return info


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            logger.info(f"\nMatch {i}:")
            logger.info(f"Similarity Score: {rec.get('similarity', 0):.2f}")
            logger.info(f"Matched Situation: {rec.get('situation', '')}")
            logger.info(f"Recommendation: {rec.get('recommendation', '')}")

    except Exception as e:
        logger.error(f"Error during recommendation: {str(e)}")
