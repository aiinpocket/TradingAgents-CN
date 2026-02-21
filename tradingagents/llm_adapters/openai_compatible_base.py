"""
OpenAI 相容適配器基底類別
為所有支援 OpenAI 介面的 LLM 提供商提供統一的基礎實現
"""

import os
import time
from typing import Any, Dict, List, Optional, Union
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import CallbackManagerForLLMRun

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

# 匯入 token 追蹤器
try:
    from tradingagents.config.config_manager import token_tracker
    TOKEN_TRACKING_ENABLED = True
    logger.info("Token 追蹤功能已啟用")
except ImportError:
    TOKEN_TRACKING_ENABLED = False
    logger.warning("Token 追蹤功能未啟用")


class OpenAICompatibleBase(ChatOpenAI):
    """
    OpenAI 相容適配器基底類別
    為所有支援 OpenAI 介面的 LLM 提供商提供統一實現
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
        初始化 OpenAI 相容適配器

        Args:
            provider_name: 提供商名稱 (如: "custom_openai")
            model: 模型名稱
            api_key_env_var: API 金鑰環境變數名
            base_url: API 基底 URL
            api_key: API 金鑰，若未提供則從環境變數取得
            temperature: 溫度參數
            max_tokens: 最大 token 數
            **kwargs: 其他參數
        """

        # 在父類別初始化前先快取元資訊到私有屬性（避免 Pydantic 欄位限制）
        object.__setattr__(self, "_provider_name", provider_name)
        object.__setattr__(self, "_model_name_alias", model)

        # 取得 API 金鑰
        if api_key is None:
            api_key = os.getenv(api_key_env_var)
            if not api_key:
                raise ValueError(
                    f"{provider_name} API 金鑰未找到。"
                    f"請設定 {api_key_env_var} 環境變數或傳入 api_key 參數。"
                )

        # 設定 OpenAI 相容參數
        # 注意：model 參數會被 Pydantic 映射到 model_name 欄位
        openai_kwargs = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        # 根據 LangChain 版本使用不同的參數名
        try:
            # 新版本 LangChain
            openai_kwargs.update({
                "api_key": api_key,
                "base_url": base_url
            })
        except:
            # 舊版本 LangChain
            openai_kwargs.update({
                "openai_api_key": api_key,
                "openai_api_base": base_url
            })

        # 初始化父類別
        super().__init__(**openai_kwargs)

        # 再次確保元資訊存在（某些實現會在 super() 中重置 __dict__）
        object.__setattr__(self, "_provider_name", provider_name)
        object.__setattr__(self, "_model_name_alias", model)

        logger.info(f"{provider_name} OpenAI 相容適配器初始化成功")
        logger.info(f"   模型: {model}")
        logger.info(f"   API Base: {base_url}")

    @property
    def provider_name(self) -> Optional[str]:
        """取得提供商名稱"""
        return getattr(self, "_provider_name", None)

    # 移除 model_name property 定義，使用 Pydantic 欄位
    # model_name 欄位由 ChatOpenAI 基底類別的 Pydantic 欄位提供

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        生成聊天回應，並記錄 token 使用量
        """

        # 記錄開始時間
        start_time = time.time()

        # 呼叫父類別生成方法
        result = super()._generate(messages, stop, run_manager, **kwargs)

        # 記錄 token 使用
        self._track_token_usage(result, kwargs, start_time)

        return result

    def _track_token_usage(self, result: ChatResult, kwargs: Dict, start_time: float):
        """記錄 token 使用量並輸出日誌"""
        if not TOKEN_TRACKING_ENABLED:
            return
        try:
            # 統計 token 資訊
            usage = getattr(result, "usage_metadata", None)
            total_tokens = usage.get("total_tokens") if usage else None
            prompt_tokens = usage.get("input_tokens") if usage else None
            completion_tokens = usage.get("output_tokens") if usage else None

            elapsed = time.time() - start_time
            logger.info(
                f"Token 使用 - Provider: {getattr(self, 'provider_name', 'unknown')}, "
                f"Model: {getattr(self, 'model_name', 'unknown')}, "
                f"總 tokens: {total_tokens}, 提示: {prompt_tokens}, "
                f"補全: {completion_tokens}, 用時: {elapsed:.2f}s"
            )
        except Exception as e:
            logger.warning(f"Token 追蹤記錄失敗: {e}")


class ChatCustomOpenAI(OpenAICompatibleBase):
    """自訂 OpenAI 端點適配器（代理/聚合平台）"""

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


# 支援的 OpenAI 相容模型設定
OPENAI_COMPATIBLE_PROVIDERS = {
    "custom_openai": {
        "adapter_class": ChatCustomOpenAI,
        "base_url": None,  # 由使用者設定
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
    """建立 OpenAI 相容 LLM 實例的統一工廠函式"""
    provider_info = OPENAI_COMPATIBLE_PROVIDERS.get(provider)
    if not provider_info:
        raise ValueError(f"不支援的 OpenAI 相容提供商: {provider}")

    adapter_class = provider_info["adapter_class"]

    # 若呼叫方未提供 base_url，則採用 provider 的預設值（可能為 None）
    if base_url is None:
        base_url = provider_info.get("base_url")

    # 僅當 provider 未內建 base_url（如 custom_openai）時，才將 base_url 傳遞給適配器，
    # 避免與適配器內部的 super().__init__(..., base_url=...) 衝突導致 "multiple values" 錯誤
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
    """快速測試適配器是否能被正確實例化（不發起真實請求）"""
    for provider, info in OPENAI_COMPATIBLE_PROVIDERS.items():
        cls = info["adapter_class"]
        try:
            if provider == "custom_openai":
                cls(model="gpt-3.5-turbo", api_key="test", base_url="https://api.openai.com/v1")
            logger.info(f"適配器實例化成功: {provider}")
        except Exception as e:
            logger.warning(f"適配器實例化失敗（預期或可忽略）: {provider} - {e}")


if __name__ == "__main__":
    test_openai_compatible_adapters()
