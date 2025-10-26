"""
OpenAI兼容適配器基類
為所有支持OpenAI接口的LLM提供商提供統一的基础實現
"""

import os
import time
from typing import Any, Dict, List, Optional, Union
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
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


class OpenAICompatibleBase(ChatOpenAI):
    """
    OpenAI兼容適配器基類
    為所有支持OpenAI接口的LLM提供商提供統一實現
    """
    
    def __init__(
        self,
        provider_name: str,
        model: str,
        api_key_env_var: str,
        base_url: str,
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        初始化OpenAI兼容適配器
        
        Args:
            provider_name: 提供商名稱 (如: "deepseek", "dashscope")
            model: 模型名稱
            api_key_env_var: API密鑰環境變量名
            base_url: API基础URL
            api_key: API密鑰，如果不提供則從環境變量獲取
            temperature: 溫度參數
            max_tokens: 最大token數
            **kwargs: 其他參數
        """
        
        # 在父類初始化前先緩存元信息到私有屬性（避免Pydantic字段限制）
        object.__setattr__(self, "_provider_name", provider_name)
        object.__setattr__(self, "_model_name_alias", model)
        
        # 獲取API密鑰
        if api_key is None:
            api_key = os.getenv(api_key_env_var)
            if not api_key:
                raise ValueError(
                    f"{provider_name} API密鑰未找到。"
                    f"請設置{api_key_env_var}環境變量或傳入api_key參數。"
                )
        
        # 設置OpenAI兼容參數
        # 註意：model參數會被Pydantic映射到model_name字段
        openai_kwargs = {
            "model": model,  # 這會被映射到model_name字段
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # 根據LangChain版本使用不同的參數名
        try:
            # 新版本LangChain
            openai_kwargs.update({
                "api_key": api_key,
                "base_url": base_url
            })
        except:
            # 旧版本LangChain
            openai_kwargs.update({
                "openai_api_key": api_key,
                "openai_api_base": base_url
            })
        
        # 初始化父類
        super().__init__(**openai_kwargs)

        # 再次確保元信息存在（有些實現會在super()中重置__dict__）
        object.__setattr__(self, "_provider_name", provider_name)
        object.__setattr__(self, "_model_name_alias", model)

        logger.info(f"✅ {provider_name} OpenAI兼容適配器初始化成功")
        logger.info(f"   模型: {model}")
        logger.info(f"   API Base: {base_url}")

    @property
    def provider_name(self) -> Optional[str]:
        return getattr(self, "_provider_name", None)

    # 移除model_name property定義，使用Pydantic字段
    # model_name字段由ChatOpenAI基類的Pydantic字段提供
    
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
        
        # 調用父類生成方法
        result = super()._generate(messages, stop, run_manager, **kwargs)
        
        # 記錄token使用
        self._track_token_usage(result, kwargs, start_time)
        
        return result

    def _track_token_usage(self, result: ChatResult, kwargs: Dict, start_time: float):
        """記錄token使用量並輸出日誌"""
        if not TOKEN_TRACKING_ENABLED:
            return
        try:
            # 統計token信息
            usage = getattr(result, "usage_metadata", None)
            total_tokens = usage.get("total_tokens") if usage else None
            prompt_tokens = usage.get("input_tokens") if usage else None
            completion_tokens = usage.get("output_tokens") if usage else None

            elapsed = time.time() - start_time
            logger.info(
                f"📊 Token使用 - Provider: {getattr(self, 'provider_name', 'unknown')}, Model: {getattr(self, 'model_name', 'unknown')}, "
                f"总tokens: {total_tokens}, 提示: {prompt_tokens}, 補全: {completion_tokens}, 用時: {elapsed:.2f}s"
            )
        except Exception as e:
            logger.warning(f"⚠️ Token跟蹤記錄失败: {e}")


class ChatDeepSeekOpenAI(OpenAICompatibleBase):
    """DeepSeek OpenAI兼容適配器"""
    
    def __init__(
        self,
        model: str = "deepseek-chat",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            provider_name="deepseek",
            model=model,
            api_key_env_var="DEEPSEEK_API_KEY",
            base_url="https://api.deepseek.com",
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


class ChatDashScopeOpenAIUnified(OpenAICompatibleBase):
    """阿里百炼 DashScope OpenAI兼容適配器"""
    
    def __init__(
        self,
        model: str = "qwen-turbo",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            provider_name="dashscope",
            model=model,
            api_key_env_var="DASHSCOPE_API_KEY",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


class ChatQianfanOpenAI(OpenAICompatibleBase):
    """文心一言千帆平台 OpenAI兼容適配器"""
    
    def __init__(
        self,
        model: str = "ernie-3.5-8k",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        # 千帆新一代API使用單一API Key認證
        # 格式: bce-v3/ALTAK-xxx/xxx
        
        qianfan_api_key = api_key or os.getenv('QIANFAN_API_KEY')
        
        if not qianfan_api_key:
            raise ValueError(
                "千帆模型需要設置QIANFAN_API_KEY環境變量，格式為: bce-v3/ALTAK-xxx/xxx"
            )
        
        if not qianfan_api_key.startswith('bce-v3/'):
            raise ValueError(
                "QIANFAN_API_KEY格式錯誤，應為: bce-v3/ALTAK-xxx/xxx"
            )
        
        super().__init__(
            provider_name="qianfan",
            model=model,
            api_key_env_var="QIANFAN_API_KEY",
            base_url="https://qianfan.baidubce.com/v2",
            api_key=qianfan_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token數量（千帆模型專用）"""
        # 千帆模型的token估算：中文約1.5字符/token，英文約4字符/token
        # 保守估算：2字符/token
        return max(1, len(text) // 2)
    
    def _truncate_messages(self, messages: List[BaseMessage], max_tokens: int = 4500) -> List[BaseMessage]:
        """截斷消息以適應千帆模型的token限制"""
        # 為千帆模型預留一些token空間，使用4500而不是5120
        truncated_messages = []
        total_tokens = 0
        
        # 從最後一條消息開始，向前保留消息
        for message in reversed(messages):
            content = str(message.content) if hasattr(message, 'content') else str(message)
            message_tokens = self._estimate_tokens(content)
            
            if total_tokens + message_tokens <= max_tokens:
                truncated_messages.insert(0, message)
                total_tokens += message_tokens
            else:
                # 如果是第一條消息且超長，進行內容截斷
                if not truncated_messages:
                    remaining_tokens = max_tokens - 100  # 預留100個token
                    max_chars = remaining_tokens * 2  # 2字符/token
                    truncated_content = content[:max_chars] + "...(內容已截斷)"
                    
                    # 創建截斷後的消息
                    if hasattr(message, 'content'):
                        message.content = truncated_content
                    truncated_messages.insert(0, message)
                break
        
        if len(truncated_messages) < len(messages):
            logger.warning(f"⚠️ 千帆模型輸入過長，已截斷 {len(messages) - len(truncated_messages)} 條消息")
        
        return truncated_messages
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天響應，包含千帆模型的token截斷逻辑"""
        
        # 對千帆模型進行輸入token截斷
        truncated_messages = self._truncate_messages(messages)
        
        # 調用父類的_generate方法
        return super()._generate(truncated_messages, stop, run_manager, **kwargs)


class ChatCustomOpenAI(OpenAICompatibleBase):
    """自定義OpenAI端點適配器（代理/聚合平台）"""
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        if base_url is None:
            base_url = os.getenv("CUSTOM_OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        super().__init__(
            provider_name="custom_openai",
            model=model,
            api_key_env_var="CUSTOM_OPENAI_API_KEY",
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


# 支持的OpenAI兼容模型配置
OPENAI_COMPATIBLE_PROVIDERS = {
    "deepseek": {
        "adapter_class": ChatDeepSeekOpenAI,
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "models": {
            "deepseek-chat": {"context_length": 32768, "supports_function_calling": True},
            "deepseek-coder": {"context_length": 16384, "supports_function_calling": True}
        }
    },
    "dashscope": {
        "adapter_class": ChatDashScopeOpenAIUnified,
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "DASHSCOPE_API_KEY",
        "models": {
            "qwen-turbo": {"context_length": 8192, "supports_function_calling": True},
            "qwen-plus": {"context_length": 32768, "supports_function_calling": True},
            "qwen-plus-latest": {"context_length": 32768, "supports_function_calling": True},
            "qwen-max": {"context_length": 32768, "supports_function_calling": True},
            "qwen-max-latest": {"context_length": 32768, "supports_function_calling": True}
        }
    },
    "qianfan": {
        "adapter_class": ChatQianfanOpenAI,
        "base_url": "https://qianfan.baidubce.com/v2",
        "api_key_env": "QIANFAN_API_KEY",
        "models": {
            "ernie-3.5-8k": {"context_length": 5120, "supports_function_calling": True},
            "ernie-4.0-turbo-8k": {"context_length": 5120, "supports_function_calling": True},
            "ERNIE-Speed-8K": {"context_length": 5120, "supports_function_calling": True},
            "ERNIE-Lite-8K": {"context_length": 5120, "supports_function_calling": True}
        }
    },
    "custom_openai": {
        "adapter_class": ChatCustomOpenAI,
        "base_url": None,  # 将由用戶配置
        "api_key_env": "CUSTOM_OPENAI_API_KEY",
        "models": {
            "gpt-3.5-turbo": {"context_length": 16384, "supports_function_calling": True},
            "gpt-4": {"context_length": 8192, "supports_function_calling": True},
            "gpt-4-turbo": {"context_length": 128000, "supports_function_calling": True},
            "gpt-4o": {"context_length": 128000, "supports_function_calling": True},
            "gpt-4o-mini": {"context_length": 128000, "supports_function_calling": True},
            "claude-3-haiku": {"context_length": 200000, "supports_function_calling": True},
            "claude-3-sonnet": {"context_length": 200000, "supports_function_calling": True},
            "claude-3-opus": {"context_length": 200000, "supports_function_calling": True},
            "claude-3.5-sonnet": {"context_length": 200000, "supports_function_calling": True},
            "gemini-pro": {"context_length": 32768, "supports_function_calling": True},
            "gemini-1.5-pro": {"context_length": 1000000, "supports_function_calling": True},
            "llama-3.1-8b": {"context_length": 128000, "supports_function_calling": True},
            "llama-3.1-70b": {"context_length": 128000, "supports_function_calling": True},
            "llama-3.1-405b": {"context_length": 128000, "supports_function_calling": True},
            "custom-model": {"context_length": 32768, "supports_function_calling": True}
        }
    }
}


def create_openai_compatible_llm(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: Optional[int] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> OpenAICompatibleBase:
    """創建OpenAI兼容LLM實例的統一工厂函數"""
    provider_info = OPENAI_COMPATIBLE_PROVIDERS.get(provider)
    if not provider_info:
        raise ValueError(f"不支持的OpenAI兼容提供商: {provider}")

    adapter_class = provider_info["adapter_class"]

    # 如果調用未提供 base_url，則採用 provider 的默認值（可能為 None）
    if base_url is None:
        base_url = provider_info.get("base_url")

    # 仅當 provider 未內置 base_url（如 custom_openai）時，才将 base_url 傳遞給適配器，
    # 避免与適配器內部的 super().__init__(..., base_url=...) 冲突導致 "multiple values" 錯誤。
    init_kwargs = dict(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
    if provider_info.get("base_url") is None and base_url:
        init_kwargs["base_url"] = base_url

    return adapter_class(**init_kwargs)


def test_openai_compatible_adapters():
    """快速測試所有適配器是否能被正確實例化（不發起真實請求）"""
    for provider, info in OPENAI_COMPATIBLE_PROVIDERS.items():
        cls = info["adapter_class"]
        try:
            if provider == "custom_openai":
                cls(model="gpt-3.5-turbo", api_key="test", base_url="https://api.openai.com/v1")
            elif provider == "qianfan":
                # 千帆新一代API仅需QIANFAN_API_KEY，格式: bce-v3/ALTAK-xxx/xxx
                cls(model="ernie-3.5-8k", api_key="bce-v3/test-key/test-secret")
            else:
                cls(model=list(info["models"].keys())[0], api_key="test")
            logger.info(f"✅ 適配器實例化成功: {provider}")
        except Exception as e:
            logger.warning(f"⚠️ 適配器實例化失败（預期或可忽略）: {provider} - {e}")


if __name__ == "__main__":
    test_openai_compatible_adapters()
