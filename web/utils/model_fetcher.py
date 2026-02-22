"""
動態模型列表取得模組
從 OpenAI 和 Anthropic API 取得可用模型列表，帶快取機制和失敗降級
"""

import os
import time
import requests
from typing import Optional

# 日誌模組
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger('web')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# 模型列表快取（模組層級，跨 Streamlit rerun 保持）
_model_cache: dict = {}
# 快取有效期（秒）
CACHE_TTL = 300


def _is_cache_valid(provider: str) -> bool:
    """檢查指定提供商的快取是否仍然有效"""
    if provider not in _model_cache:
        return False
    cached_time = _model_cache[provider].get("timestamp", 0)
    return (time.time() - cached_time) < CACHE_TTL


def _set_cache(provider: str, models: list[dict]) -> None:
    """儲存模型列表到快取"""
    _model_cache[provider] = {
        "models": models,
        "timestamp": time.time()
    }


def _get_cache(provider: str) -> Optional[list[dict]]:
    """從快取取得模型列表"""
    if _is_cache_valid(provider):
        return _model_cache[provider]["models"]
    return None


def clear_cache(provider: str = None) -> None:
    """清除模型快取，不指定 provider 則清除全部"""
    if provider:
        _model_cache.pop(provider, None)
    else:
        _model_cache.clear()


# 各提供商的降級預設模型列表（API 呼叫失敗時使用）
FALLBACK_MODELS = {
    "openai": [
        {"id": "o4-mini", "name": "o4-mini"},
        {"id": "gpt-4.1", "name": "GPT-4.1"},
        {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini"},
        {"id": "gpt-4.1-nano", "name": "GPT-4.1 Nano"},
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
    ],
    "anthropic": [
        {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6"},
        {"id": "claude-opus-4-6", "name": "Claude Opus 4.6"},
        {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5"},
        {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
        {"id": "claude-opus-4-20250514", "name": "Claude Opus 4"},
    ],
}


def fetch_openai_models() -> list[dict]:
    """從 OpenAI API 取得可用的聊天模型列表"""
    cached = _get_cache("openai")
    if cached is not None:
        return cached

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("your_"):
        logger.info("OpenAI API 金鑰未設定，使用預設模型列表")
        return FALLBACK_MODELS["openai"]

    try:
        resp = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        # 篩選聊天相關模型，排除嵌入、TTS、whisper 等非聊天模型
        exclude_prefixes = (
            "text-embedding", "embedding", "tts-", "whisper-",
            "dall-e", "davinci", "babbage", "curie", "ada",
            "ft:", "chatgpt-4o-latest"
        )
        # 優先排序的前綴（越前面越優先）
        priority_prefixes = [
            "o4-mini", "o3-", "o1",
            "gpt-5", "gpt-4.1", "gpt-4o", "gpt-4.5",
            "gpt-4-turbo", "gpt-4", "gpt-3.5"
        ]

        models = []
        for m in data.get("data", []):
            mid = m.get("id", "")
            if any(mid.startswith(p) or mid.startswith(f"ft:{p}") for p in exclude_prefixes):
                continue
            models.append({"id": mid, "name": mid})

        # 根據優先順序排序
        def sort_key(model):
            mid = model["id"]
            for i, prefix in enumerate(priority_prefixes):
                if mid.startswith(prefix):
                    return (i, mid)
            return (len(priority_prefixes), mid)

        models.sort(key=sort_key)

        if models:
            _set_cache("openai", models)
            logger.info(f"從 OpenAI API 取得 {len(models)} 個模型")
            return models

    except Exception as e:
        logger.warning(f"OpenAI API 模型列表取得失敗: {e}")

    return FALLBACK_MODELS["openai"]


def fetch_anthropic_models() -> list[dict]:
    """從 Anthropic API 取得可用模型列表"""
    cached = _get_cache("anthropic")
    if cached is not None:
        return cached

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("your_"):
        logger.info("Anthropic API 金鑰未設定，使用預設模型列表")
        return FALLBACK_MODELS["anthropic"]

    try:
        resp = requests.get(
            "https://api.anthropic.com/v1/models",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        models = []
        for m in data.get("data", []):
            mid = m.get("id", "")
            display_name = m.get("display_name", mid)
            models.append({"id": mid, "name": display_name})

        # 按照模型系列和版本排序
        import re
        tier_order = {"opus": 0, "sonnet": 1, "haiku": 2}

        def _parse_version(model_id: str) -> tuple:
            """從模型 ID 解析主版本和次版本號"""
            nums = re.findall(r'\d+', model_id)
            version_nums = [int(n) for n in nums if len(n) <= 2]
            if len(version_nums) >= 2:
                return (version_nums[0], version_nums[1])
            elif len(version_nums) == 1:
                return (version_nums[0], 0)
            return (0, 0)

        def sort_key(model):
            mid = model["id"]
            tier = 9
            for name, order in tier_order.items():
                if name in mid:
                    tier = order
                    break
            major, minor = _parse_version(mid)
            return (tier, -major, -minor)

        models.sort(key=sort_key)

        if models:
            _set_cache("anthropic", models)
            logger.info(f"從 Anthropic API 取得 {len(models)} 個模型")
            return models

    except Exception as e:
        logger.warning(f"Anthropic API 模型列表取得失敗: {e}")

    return FALLBACK_MODELS["anthropic"]


def fetch_models(provider: str, **kwargs) -> list[dict]:
    """統一入口：根據提供商取得模型列表

    回傳格式: [{"id": "model-id", "name": "顯示名稱"}, ...]
    """
    fetchers = {
        "openai": fetch_openai_models,
        "anthropic": fetch_anthropic_models,
    }

    fetcher = fetchers.get(provider)
    if fetcher:
        return fetcher()

    logger.warning(f"不支援的提供商: {provider}")
    return []
