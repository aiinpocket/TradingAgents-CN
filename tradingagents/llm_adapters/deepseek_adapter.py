"""
DeepSeek LLM適配器，支持Token使用統計
"""

import os
import time
from typing import Any, Dict, List, Optional, Union
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import CallbackManagerForLLMRun

# 導入統一日誌系統
from tradingagents.utils.logging_init import setup_llm_logging

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger, get_logger_manager
logger = get_logger('agents')
logger = setup_llm_logging()

# 導入token跟蹤器
try:
    from tradingagents.config.config_manager import token_tracker
    TOKEN_TRACKING_ENABLED = True
    logger.info("✅ Token跟蹤功能已啟用")
except ImportError:
    TOKEN_TRACKING_ENABLED = False
    logger.warning("⚠️ Token跟蹤功能未啟用")


class ChatDeepSeek(ChatOpenAI):
    """
    DeepSeek聊天模型適配器，支持Token使用統計
    
    繼承自ChatOpenAI，添加了Token使用量統計功能
    """
    
    def __init__(
        self,
        model: str = "deepseek-chat",
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        初始化DeepSeek適配器
        
        Args:
            model: 模型名稱，默認為deepseek-chat
            api_key: API密鑰，如果不提供則從環境變量DEEPSEEK_API_KEY獲取
            base_url: API基础URL
            temperature: 溫度參數
            max_tokens: 最大token數
            **kwargs: 其他參數
        """
        
        # 獲取API密鑰
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DeepSeek API密鑰未找到。請設置DEEPSEEK_API_KEY環境變量或傳入api_key參數。")
        
        # 初始化父類
        super().__init__(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        self.model_name = model
        
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        生成聊天響應，並記錄token使用量
        """

        # 記錄開始時間
        start_time = time.time()

        # 提取並移除自定義參數，避免傳遞給父類
        session_id = kwargs.pop('session_id', None)
        analysis_type = kwargs.pop('analysis_type', None)

        try:
            # 調用父類方法生成響應
            result = super()._generate(messages, stop, run_manager, **kwargs)
            
            # 提取token使用量
            input_tokens = 0
            output_tokens = 0
            
            # 嘗試從響應中提取token使用量
            if hasattr(result, 'llm_output') and result.llm_output:
                token_usage = result.llm_output.get('token_usage', {})
                if token_usage:
                    input_tokens = token_usage.get('prompt_tokens', 0)
                    output_tokens = token_usage.get('completion_tokens', 0)
            
            # 如果没有獲取到token使用量，進行估算
            if input_tokens == 0 and output_tokens == 0:
                input_tokens = self._estimate_input_tokens(messages)
                output_tokens = self._estimate_output_tokens(result)
                logger.debug(f"🔍 [DeepSeek] 使用估算token: 輸入={input_tokens}, 輸出={output_tokens}")
            else:
                logger.info(f"📊 [DeepSeek] 實际token使用: 輸入={input_tokens}, 輸出={output_tokens}")
            
            # 記錄token使用量
            if TOKEN_TRACKING_ENABLED and (input_tokens > 0 or output_tokens > 0):
                try:
                    # 使用提取的參數或生成默認值
                    if session_id is None:
                        session_id = f"deepseek_{hash(str(messages))%10000}"
                    if analysis_type is None:
                        analysis_type = 'stock_analysis'

                    # 記錄使用量
                    usage_record = token_tracker.track_usage(
                        provider="deepseek",
                        model_name=self.model_name,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        session_id=session_id,
                        analysis_type=analysis_type
                    )

                    if usage_record:
                        if usage_record.cost == 0.0:
                            logger.warning(f"⚠️ [DeepSeek] 成本計算為0，可能配置有問題")
                        else:
                            logger.info(f"💰 [DeepSeek] 本次調用成本: ¥{usage_record.cost:.6f}")

                        # 使用統一日誌管理器的Token記錄方法
                        logger_manager = get_logger_manager()
                        logger_manager.log_token_usage(
                            logger, "deepseek", self.model_name,
                            input_tokens, output_tokens, usage_record.cost,
                            session_id
                        )
                    else:
                        logger.warning(f"⚠️ [DeepSeek] 未創建使用記錄")

                except Exception as track_error:
                    logger.error(f"⚠️ [DeepSeek] Token統計失败: {track_error}", exc_info=True)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [DeepSeek] 調用失败: {e}", exc_info=True)
            raise
    
    def _estimate_input_tokens(self, messages: List[BaseMessage]) -> int:
        """
        估算輸入token數量
        
        Args:
            messages: 輸入消息列表
            
        Returns:
            估算的輸入token數量
        """
        total_chars = 0
        for message in messages:
            if hasattr(message, 'content'):
                total_chars += len(str(message.content))
        
        # 粗略估算：中文約1.5字符/token，英文約4字符/token
        # 這里使用保守估算：2字符/token
        estimated_tokens = max(1, total_chars // 2)
        return estimated_tokens
    
    def _estimate_output_tokens(self, result: ChatResult) -> int:
        """
        估算輸出token數量
        
        Args:
            result: 聊天結果
            
        Returns:
            估算的輸出token數量
        """
        total_chars = 0
        for generation in result.generations:
            if hasattr(generation, 'message') and hasattr(generation.message, 'content'):
                total_chars += len(str(generation.message.content))
        
        # 粗略估算：2字符/token
        estimated_tokens = max(1, total_chars // 2)
        return estimated_tokens
    
    def invoke(
        self,
        input: Union[str, List[BaseMessage]],
        config: Optional[Dict] = None,
        **kwargs: Any,
    ) -> AIMessage:
        """
        調用模型生成響應
        
        Args:
            input: 輸入消息
            config: 配置參數
            **kwargs: 其他參數（包括session_id和analysis_type）
            
        Returns:
            AI消息響應
        """
        
        # 處理輸入
        if isinstance(input, str):
            messages = [HumanMessage(content=input)]
        else:
            messages = input
        
        # 調用生成方法
        result = self._generate(messages, **kwargs)
        
        # 返回第一個生成結果的消息
        if result.generations:
            return result.generations[0].message
        else:
            return AIMessage(content="")


def create_deepseek_llm(
    model: str = "deepseek-chat",
    temperature: float = 0.1,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatDeepSeek:
    """
    創建DeepSeek LLM實例的便捷函數
    
    Args:
        model: 模型名稱
        temperature: 溫度參數
        max_tokens: 最大token數
        **kwargs: 其他參數
        
    Returns:
        ChatDeepSeek實例
    """
    return ChatDeepSeek(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


# 為了向後兼容，提供別名
DeepSeekLLM = ChatDeepSeek
