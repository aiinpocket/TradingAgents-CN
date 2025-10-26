"""
LLM 適配器模板 - 適用於 OpenAI 兼容提供商

使用方式：複制本文件為 tradingagents/llm_adapters/{provider}_adapter.py，
並根據目標提供商修改 provider_name、base_url、API Key 環境變量等信息。
"""

from typing import Any, Dict
import os
import logging

from tradingagents.llm_adapters.openai_compatible_base import OpenAICompatibleBase

logger = logging.getLogger(__name__)


class ChatProviderTemplate(OpenAICompatibleBase):
    """{ProviderDisplayName} OpenAI 兼容適配器"""

    def __init__(
        self,
        model: str = "{default-model-name}",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 120,
        **kwargs: Any,
    ) -> None:
        """初始化 {ProviderDisplayName} OpenAI 兼容客戶端"""
        super().__init__(
            provider_name="{provider}",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key_env_var="{PROVIDER_API_KEY}",
            base_url="{https://api.provider.com/v1}",
            request_timeout=timeout,
            **kwargs,
        )
        logger.info("✅ {ProviderDisplayName} OpenAI 兼容適配器初始化成功")


# 供 openai_compatible_base.py 註冊參考
PROVIDER_TEMPLATE_MODELS: Dict[str, Dict[str, Any]] = {
    "{default-model-name}": {"context_length": 8192, "supports_function_calling": True},
    "{advanced-model-name}": {"context_length": 32768, "supports_function_calling": True},
}