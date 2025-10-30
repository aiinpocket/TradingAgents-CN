import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os
import threading
import hashlib
from typing import Dict, Optional

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("agents.utils.memory")


class ChromaDBManager:
    """單例ChromaDB管理器，避免並發創建集合的冲突"""

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
                # 自動檢測操作系統版本並使用最優配置
                import platform
                system = platform.system()
                
                if system == "Windows":
                    # 使用改進的Windows 11檢測
                    from .chromadb_win11_config import is_windows_11
                    if is_windows_11():
                        # Windows 11 或更新版本，使用優化配置
                        from .chromadb_win11_config import get_win11_chromadb_client
                        self._client = get_win11_chromadb_client()
                        logger.info(f"📚 [ChromaDB] Windows 11優化配置初始化完成 (構建號: {platform.version()})")
                    else:
                        # Windows 10 或更老版本，使用兼容配置
                        from .chromadb_win10_config import get_win10_chromadb_client
                        self._client = get_win10_chromadb_client()
                        logger.info(f"📚 [ChromaDB] Windows 10兼容配置初始化完成")
                else:
                    # 非Windows系統，使用標準配置
                    settings = Settings(
                        allow_reset=True,
                        anonymized_telemetry=False,
                        is_persistent=False
                    )
                    self._client = chromadb.Client(settings)
                    logger.info(f"📚 [ChromaDB] {system}標準配置初始化完成")
                
                self._initialized = True
            except Exception as e:
                logger.error(f"❌ [ChromaDB] 初始化失败: {e}")
                # 使用最簡單的配置作為备用
                try:
                    settings = Settings(
                        allow_reset=True,
                        anonymized_telemetry=False,  # 關键：禁用遥測
                        is_persistent=False
                    )
                    self._client = chromadb.Client(settings)
                    logger.info(f"📚 [ChromaDB] 使用备用配置初始化完成")
                except Exception as backup_error:
                    # 最後的备用方案
                    self._client = chromadb.Client()
                    logger.warning(f"⚠️ [ChromaDB] 使用最簡配置初始化: {backup_error}")
                self._initialized = True

    def get_or_create_collection(self, name: str):
        """線程安全地獲取或創建集合"""
        with self._lock:
            if name in self._collections:
                logger.info(f"📚 [ChromaDB] 使用緩存集合: {name}")
                return self._collections[name]

            try:
                # 嘗試獲取現有集合
                collection = self._client.get_collection(name=name)
                logger.info(f"📚 [ChromaDB] 獲取現有集合: {name}")
            except Exception:
                try:
                    # 創建新集合
                    collection = self._client.create_collection(name=name)
                    logger.info(f"📚 [ChromaDB] 創建新集合: {name}")
                except Exception as e:
                    # 可能是並發創建，再次嘗試獲取
                    try:
                        collection = self._client.get_collection(name=name)
                        logger.info(f"📚 [ChromaDB] 並發創建後獲取集合: {name}")
                    except Exception as final_error:
                        logger.error(f"❌ [ChromaDB] 集合操作失败: {name}, 錯誤: {final_error}")
                        raise final_error

            # 緩存集合
            self._collections[name] = collection
            return collection


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.config = config
        self.llm_provider = config.get("llm_provider", "openai").lower()

        # 配置向量緩存的長度限制（向量緩存默認啟用長度檢查）
        self.max_embedding_length = int(os.getenv('MAX_EMBEDDING_CONTENT_LENGTH', '50000'))  # 默認50K字符
        self.enable_embedding_length_check = os.getenv('ENABLE_EMBEDDING_LENGTH_CHECK', 'true').lower() == 'true'  # 向量緩存默認啟用
        
        # 根據LLM提供商選擇嵌入模型和客戶端
        # 初始化降級選項標誌
        self.fallback_available = False
        
        if self.llm_provider == "dashscope" or self.llm_provider == "alibaba":
            self.embedding = "text-embedding-v3"
            self.client = None  # DashScope不需要OpenAI客戶端

            # 設置DashScope API密鑰
            dashscope_key = os.getenv('DASHSCOPE_API_KEY')
            if dashscope_key:
                try:
                    # 嘗試導入和初始化DashScope
                    import dashscope
                    from dashscope import TextEmbedding

                    dashscope.api_key = dashscope_key
                    logger.info(f"✅ DashScope API密鑰已配置，啟用記忆功能")

                    # 可選：測試API連接（簡單驗證）
                    # 這里不做實际調用，只驗證導入和密鑰設置

                except ImportError as e:
                    # DashScope包未安裝
                    logger.error(f"❌ DashScope包未安裝: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ 記忆功能已禁用")

                except Exception as e:
                    # 其他初始化錯誤
                    logger.error(f"❌ DashScope初始化失败: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ 記忆功能已禁用")
            else:
                # 没有DashScope密鑰，禁用記忆功能
                self.client = "DISABLED"
                logger.warning(f"⚠️ 未找到DASHSCOPE_API_KEY，記忆功能已禁用")
                logger.info(f"💡 系統将繼续運行，但不會保存或檢索歷史記忆")
        elif self.llm_provider == "qianfan":
            # 千帆（文心一言）embedding配置
            # 千帆目前没有獨立的embedding API，使用阿里百炼作為降級選項
            dashscope_key = os.getenv('DASHSCOPE_API_KEY')
            if dashscope_key:
                try:
                    # 使用阿里百炼嵌入服務作為千帆的embedding解決方案
                    import dashscope
                    from dashscope import TextEmbedding

                    dashscope.api_key = dashscope_key
                    self.embedding = "text-embedding-v3"
                    self.client = None
                    logger.info(f"💡 千帆使用阿里百炼嵌入服務")
                except ImportError as e:
                    logger.error(f"❌ DashScope包未安裝: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ 千帆記忆功能已禁用")
                except Exception as e:
                    logger.error(f"❌ 千帆嵌入初始化失败: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ 千帆記忆功能已禁用")
            else:
                # 没有DashScope密鑰，禁用記忆功能
                self.client = "DISABLED"
                logger.warning(f"⚠️ 千帆未找到DASHSCOPE_API_KEY，記忆功能已禁用")
                logger.info(f"💡 系統将繼续運行，但不會保存或檢索歷史記忆")
        elif self.llm_provider == "deepseek":
            # 檢查是否强制使用OpenAI嵌入
            force_openai = os.getenv('FORCE_OPENAI_EMBEDDING', 'false').lower() == 'true'

            if not force_openai:
                # 嘗試使用阿里百炼嵌入
                dashscope_key = os.getenv('DASHSCOPE_API_KEY')
                if dashscope_key:
                    try:
                        # 測試阿里百炼是否可用
                        import dashscope
                        from dashscope import TextEmbedding

                        dashscope.api_key = dashscope_key
                        # 驗證TextEmbedding可用性（不需要實际調用）
                        self.embedding = "text-embedding-v3"
                        self.client = None
                        logger.info(f"💡 DeepSeek使用阿里百炼嵌入服務")
                    except ImportError as e:
                        logger.error(f"⚠️ DashScope包未安裝: {e}")
                        dashscope_key = None  # 强制降級
                    except Exception as e:
                        logger.error(f"⚠️ 阿里百炼嵌入初始化失败: {e}")
                        dashscope_key = None  # 强制降級
            else:
                dashscope_key = None  # 跳過阿里百炼

            if not dashscope_key or force_openai:
                # 降級到OpenAI嵌入
                self.embedding = "text-embedding-3-small"
                openai_key = os.getenv('OPENAI_API_KEY')
                if openai_key:
                    self.client = OpenAI(
                        api_key=openai_key,
                        base_url=config.get("backend_url", "https://api.openai.com/v1")
                    )
                    logger.warning(f"⚠️ DeepSeek回退到OpenAI嵌入服務")
                else:
                    # 最後嘗試DeepSeek自己的嵌入
                    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
                    if deepseek_key:
                        try:
                            self.client = OpenAI(
                                api_key=deepseek_key,
                                base_url="https://api.deepseek.com"
                            )
                            logger.info(f"💡 DeepSeek使用自己的嵌入服務")
                        except Exception as e:
                            logger.error(f"❌ DeepSeek嵌入服務不可用: {e}")
                            # 禁用內存功能
                            self.client = "DISABLED"
                            logger.info(f"🚨 內存功能已禁用，系統将繼续運行但不保存歷史記忆")
                    else:
                        # 禁用內存功能而不是抛出異常
                        self.client = "DISABLED"
                        logger.info(f"🚨 未找到可用的嵌入服務，內存功能已禁用")
        elif self.llm_provider == "google":
            # Google AI使用阿里百炼嵌入（如果可用），否則禁用記忆功能
            dashscope_key = os.getenv('DASHSCOPE_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if dashscope_key:
                try:
                    # 嘗試初始化DashScope
                    import dashscope
                    from dashscope import TextEmbedding

                    self.embedding = "text-embedding-v3"
                    self.client = None
                    dashscope.api_key = dashscope_key
                    
                    # 檢查是否有OpenAI密鑰作為降級選項
                    if openai_key:
                        logger.info(f"💡 Google AI使用阿里百炼嵌入服務（OpenAI作為降級選項）")
                        self.fallback_available = True
                        self.fallback_client = OpenAI(api_key=openai_key, base_url=config["backend_url"])
                        self.fallback_embedding = "text-embedding-3-small"
                    else:
                        logger.info(f"💡 Google AI使用阿里百炼嵌入服務（無降級選項）")
                        self.fallback_available = False
                        
                except ImportError as e:
                    logger.error(f"❌ DashScope包未安裝: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ Google AI記忆功能已禁用")
                except Exception as e:
                    logger.error(f"❌ DashScope初始化失败: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ Google AI記忆功能已禁用")
            else:
                # 没有DashScope密鑰，禁用記忆功能
                self.client = "DISABLED"
                self.fallback_available = False
                logger.warning(f"⚠️ Google AI未找到DASHSCOPE_API_KEY，記忆功能已禁用")
                logger.info(f"💡 系統将繼续運行，但不會保存或檢索歷史記忆")
        elif self.llm_provider == "openrouter":
            # OpenRouter支持：優先使用阿里百炼嵌入，否則禁用記忆功能
            dashscope_key = os.getenv('DASHSCOPE_API_KEY')
            if dashscope_key:
                try:
                    # 嘗試使用阿里百炼嵌入
                    import dashscope
                    from dashscope import TextEmbedding

                    self.embedding = "text-embedding-v3"
                    self.client = None
                    dashscope.api_key = dashscope_key
                    logger.info(f"💡 OpenRouter使用阿里百炼嵌入服務")
                except ImportError as e:
                    logger.error(f"❌ DashScope包未安裝: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ OpenRouter記忆功能已禁用")
                except Exception as e:
                    logger.error(f"❌ DashScope初始化失败: {e}")
                    self.client = "DISABLED"
                    logger.warning(f"⚠️ OpenRouter記忆功能已禁用")
            else:
                # 没有DashScope密鑰，禁用記忆功能
                self.client = "DISABLED"
                logger.warning(f"⚠️ OpenRouter未找到DASHSCOPE_API_KEY，記忆功能已禁用")
                logger.info(f"💡 系統将繼续運行，但不會保存或檢索歷史記忆")
        elif config["backend_url"] == "http://localhost:11434/v1":
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
                logger.warning(f"⚠️ 未找到OPENAI_API_KEY，記忆功能已禁用")

        # 使用單例ChromaDB管理器
        self.chroma_manager = ChromaDBManager()
        self.situation_collection = self.chroma_manager.get_or_create_collection(name)

    def _smart_text_truncation(self, text, max_length=8192):
        """智能文本截斷，保持語義完整性和緩存兼容性"""
        if len(text) <= max_length:
            return text, False  # 返回原文本和是否截斷的標誌
        
        # 嘗試在句子邊界截斷
        sentences = text.split('。')
        if len(sentences) > 1:
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + '。') <= max_length - 50:  # 留50字符余量
                    truncated += sentence + '。'
                else:
                    break
            if len(truncated) > max_length // 2:  # 至少保留一半內容
                logger.info(f"📝 智能截斷：在句子邊界截斷，保留{len(truncated)}/{len(text)}字符")
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
                logger.info(f"📝 智能截斷：在段落邊界截斷，保留{len(truncated)}/{len(text)}字符")
                return truncated, True
        
        # 最後選擇：保留前半部分和後半部分的關键信息
        front_part = text[:max_length//2]
        back_part = text[-(max_length//2-100):]  # 留100字符給連接符
        truncated = front_part + "\n...[內容截斷]...\n" + back_part
        logger.warning(f"⚠️ 强制截斷：保留首尾關键信息，{len(text)}字符截斷為{len(truncated)}字符")
        return truncated, True

    def get_embedding(self, text):
        """Get embedding for a text using the configured provider"""

        # 檢查記忆功能是否被禁用
        if self.client == "DISABLED":
            # 內存功能已禁用，返回空向量
            logger.debug(f"⚠️ 記忆功能已禁用，返回空向量")
            return [0.0] * 1024  # 返回1024維的零向量

        # 驗證輸入文本
        if not text or not isinstance(text, str):
            logger.warning(f"⚠️ 輸入文本為空或無效，返回空向量")
            return [0.0] * 1024

        text_length = len(text)
        if text_length == 0:
            logger.warning(f"⚠️ 輸入文本長度為0，返回空向量")
            return [0.0] * 1024
        
        # 檢查是否啟用長度限制
        if self.enable_embedding_length_check and text_length > self.max_embedding_length:
            logger.warning(f"⚠️ 文本過長({text_length:,}字符 > {self.max_embedding_length:,}字符)，跳過向量化")
            # 存储跳過信息
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
        
        # 記錄文本信息（不進行任何截斷）
        if text_length > 8192:
            logger.info(f"📝 處理長文本: {text_length}字符，提供商: {self.llm_provider}")
        
        # 存储文本處理信息
        self._last_text_info = {
            'original_length': text_length,
            'processed_length': text_length,  # 不截斷，保持原長度
            'was_truncated': False,  # 永不截斷
            'was_skipped': False,
            'provider': self.llm_provider,
            'strategy': 'no_truncation_with_fallback'  # 標記策略
        }

        if (self.llm_provider == "dashscope" or
            self.llm_provider == "alibaba" or
            self.llm_provider == "qianfan" or
            (self.llm_provider == "google" and self.client is None) or
            (self.llm_provider == "deepseek" and self.client is None) or
            (self.llm_provider == "openrouter" and self.client is None)):
            # 使用阿里百炼的嵌入模型
            try:
                # 導入DashScope模塊
                import dashscope
                from dashscope import TextEmbedding

                # 檢查DashScope API密鑰是否可用
                if not hasattr(dashscope, 'api_key') or not dashscope.api_key:
                    logger.warning(f"⚠️ DashScope API密鑰未設置，記忆功能降級")
                    return [0.0] * 1024  # 返回空向量

                # 嘗試調用DashScope API
                response = TextEmbedding.call(
                    model=self.embedding,
                    input=text
                )

                # 檢查響應狀態
                if response.status_code == 200:
                    # 成功獲取embedding
                    embedding = response.output['embeddings'][0]['embedding']
                    logger.debug(f"✅ DashScope embedding成功，維度: {len(embedding)}")
                    return embedding
                else:
                    # API返回錯誤狀態碼
                    error_msg = f"{response.code} - {response.message}"
                    
                    # 檢查是否為長度限制錯誤
                    if any(keyword in error_msg.lower() for keyword in ['length', 'token', 'limit', 'exceed']):
                        logger.warning(f"⚠️ DashScope長度限制: {error_msg}")
                        
                        # 檢查是否有降級選項
                        if hasattr(self, 'fallback_available') and self.fallback_available:
                            logger.info(f"💡 嘗試使用OpenAI降級處理長文本")
                            try:
                                response = self.fallback_client.embeddings.create(
                                    model=self.fallback_embedding,
                                    input=text
                                )
                                embedding = response.data[0].embedding
                                logger.info(f"✅ OpenAI降級成功，維度: {len(embedding)}")
                                return embedding
                            except Exception as fallback_error:
                                logger.error(f"❌ OpenAI降級失败: {str(fallback_error)}")
                                logger.info(f"💡 所有降級選項失败，記忆功能降級")
                                return [0.0] * 1024
                        else:
                            logger.info(f"💡 無可用降級選項，記忆功能降級")
                            return [0.0] * 1024
                    else:
                        logger.error(f"❌ DashScope API錯誤: {error_msg}")
                        return [0.0] * 1024  # 返回空向量而不是抛出異常

            except Exception as e:
                error_str = str(e).lower()
                
                # 檢查是否為長度限制錯誤
                if any(keyword in error_str for keyword in ['length', 'token', 'limit', 'exceed', 'too long']):
                    logger.warning(f"⚠️ DashScope長度限制異常: {str(e)}")
                    
                    # 檢查是否有降級選項
                    if hasattr(self, 'fallback_available') and self.fallback_available:
                        logger.info(f"💡 嘗試使用OpenAI降級處理長文本")
                        try:
                            response = self.fallback_client.embeddings.create(
                                model=self.fallback_embedding,
                                input=text
                            )
                            embedding = response.data[0].embedding
                            logger.info(f"✅ OpenAI降級成功，維度: {len(embedding)}")
                            return embedding
                        except Exception as fallback_error:
                            logger.error(f"❌ OpenAI降級失败: {str(fallback_error)}")
                            logger.info(f"💡 所有降級選項失败，記忆功能降級")
                            return [0.0] * 1024
                    else:
                        logger.info(f"💡 無可用降級選項，記忆功能降級")
                        return [0.0] * 1024
                elif 'import' in error_str:
                    logger.error(f"❌ DashScope包未安裝: {str(e)}")
                elif 'connection' in error_str:
                    logger.error(f"❌ DashScope網絡連接錯誤: {str(e)}")
                elif 'timeout' in error_str:
                    logger.error(f"❌ DashScope請求超時: {str(e)}")
                else:
                    logger.error(f"❌ DashScope embedding異常: {str(e)}")
                
                logger.warning(f"⚠️ 記忆功能降級，返回空向量")
                return [0.0] * 1024
        else:
            # 使用OpenAI兼容的嵌入模型
            if self.client is None:
                logger.warning(f"⚠️ 嵌入客戶端未初始化，返回空向量")
                return [0.0] * 1024  # 返回空向量
            elif self.client == "DISABLED":
                # 內存功能已禁用，返回空向量
                logger.debug(f"⚠️ 內存功能已禁用，返回空向量")
                return [0.0] * 1024  # 返回1024維的零向量

            # 嘗試調用OpenAI兼容的embedding API
            try:
                response = self.client.embeddings.create(
                    model=self.embedding,
                    input=text
                )
                embedding = response.data[0].embedding
                logger.debug(f"✅ {self.llm_provider} embedding成功，維度: {len(embedding)}")
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
                    logger.warning(f"⚠️ {self.llm_provider}長度限制: {str(e)}")
                    logger.info(f"💡 為保證分析準確性，不截斷文本，記忆功能降級")
                else:
                    # 其他類型的錯誤
                    if 'attributeerror' in error_str:
                        logger.error(f"❌ {self.llm_provider} API調用錯誤: {str(e)}")
                    elif 'connectionerror' in error_str or 'connection' in error_str:
                        logger.error(f"❌ {self.llm_provider}網絡連接錯誤: {str(e)}")
                    elif 'timeout' in error_str:
                        logger.error(f"❌ {self.llm_provider}請求超時: {str(e)}")
                    elif 'keyerror' in error_str:
                        logger.error(f"❌ {self.llm_provider}響應格式錯誤: {str(e)}")
                    else:
                        logger.error(f"❌ {self.llm_provider} embedding異常: {str(e)}")
                
                logger.warning(f"⚠️ 記忆功能降級，返回空向量")
                return [0.0] * 1024

    def get_embedding_config_status(self):
        """獲取向量緩存配置狀態"""
        return {
            'enabled': self.enable_embedding_length_check,
            'max_embedding_length': self.max_embedding_length,
            'max_embedding_length_formatted': f"{self.max_embedding_length:,}字符",
            'provider': self.llm_provider,
            'client_status': 'DISABLED' if self.client == "DISABLED" else 'ENABLED'
        }

    def get_last_text_info(self):
        """獲取最後處理的文本信息"""
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
        
        # 獲取當前情况的embedding
        query_embedding = self.get_embedding(current_situation)
        
        # 檢查是否為空向量（記忆功能被禁用或出錯）
        if all(x == 0.0 for x in query_embedding):
            logger.debug(f"⚠️ 查詢embedding為空向量，返回空結果")
            return []
        
        # 檢查是否有足夠的數據進行查詢
        collection_count = self.situation_collection.count()
        if collection_count == 0:
            logger.debug(f"📭 記忆庫為空，返回空結果")
            return []
        
        # 調整查詢數量，不能超過集合中的文档數量
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
                
                # 記錄查詢信息
                if hasattr(self, '_last_text_info') and self._last_text_info.get('was_truncated'):
                    logger.info(f"🔍 截斷文本查詢完成，找到{len(memories)}個相關記忆")
                    logger.debug(f"📊 原文長度: {self._last_text_info['original_length']}, "
                               f"處理後長度: {self._last_text_info['processed_length']}")
                else:
                    logger.debug(f"🔍 記忆查詢完成，找到{len(memories)}個相關記忆")
            
            return memories
            
        except Exception as e:
            logger.error(f"❌ 記忆查詢失败: {str(e)}")
            return []

    def get_cache_info(self):
        """獲取緩存相關信息，用於調試和監控"""
        info = {
            'collection_count': self.situation_collection.count(),
            'client_status': 'enabled' if self.client != "DISABLED" else 'disabled',
            'embedding_model': self.embedding,
            'provider': self.llm_provider
        }
        
        # 添加最後一次文本處理信息
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
