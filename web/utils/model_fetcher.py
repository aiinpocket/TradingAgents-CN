"""
動態模型列表取得模組
從各 LLM 提供商 API 取得可用模型列表，帶快取機制和失敗降級
"""

import os
import time
import logging
import requests
from typing import Optional

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
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
        {"id": "gpt-4", "name": "GPT-4"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
        {"id": "o1", "name": "o1"},
        {"id": "o1-mini", "name": "o1 Mini"},
    ],
    "anthropic": [
        {"id": "claude-sonnet-4-5-20250514", "name": "Claude Sonnet 4.5"},
        {"id": "claude-opus-4-0-20250514", "name": "Claude Opus 4"},
        {"id": "claude-sonnet-4-0-20250514", "name": "Claude Sonnet 4"},
        {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
    ],
    "google": [
        {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
        {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
    ],
    "openrouter": [
        {"id": "openai/gpt-4o", "name": "GPT-4o (OpenAI)"},
        {"id": "anthropic/claude-sonnet-4", "name": "Claude Sonnet 4 (Anthropic)"},
        {"id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro (Google)"},
        {"id": "meta-llama/llama-4-scout", "name": "Llama 4 Scout (Meta)"},
    ],
    "ollama": [
        {"id": "llama3.2", "name": "Llama 3.2"},
        {"id": "mistral", "name": "Mistral"},
    ],
    "custom_openai": [
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
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
            # 排除非聊天模型
            if any(mid.startswith(p) or mid.startswith(f"ft:{p}") for p in exclude_prefixes):
                continue
            # 排除快照版本（保留主要版本）
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

        # 按照模型系列和版本排序，較新的排前面
        # 排序策略：先按系列分組（opus > sonnet > haiku），再按版本號降序
        import re
        tier_order = {"opus": 0, "sonnet": 1, "haiku": 2}

        def _parse_version(model_id: str) -> tuple:
            """從模型 ID 解析主版本和次版本號
            例如: claude-opus-4-6 -> (4, 6)
                  claude-opus-4-5-20251101 -> (4, 5)
                  claude-opus-4-20250514 -> (4, 0)
                  claude-3-haiku-20240307 -> (3, 0)
            """
            # 提取所有數字片段
            nums = re.findall(r'\d+', model_id)
            # 過濾掉日期格式（8 位數字）
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
            # 版本號降序排列（負數）
            return (tier, -major, -minor)

        models.sort(key=sort_key)

        if models:
            _set_cache("anthropic", models)
            logger.info(f"從 Anthropic API 取得 {len(models)} 個模型")
            return models

    except Exception as e:
        logger.warning(f"Anthropic API 模型列表取得失敗: {e}")

    return FALLBACK_MODELS["anthropic"]


def fetch_google_models() -> list[dict]:
    """從 Google AI API 取得可用 Gemini 模型列表"""
    cached = _get_cache("google")
    if cached is not None:
        return cached

    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or api_key.startswith("your_"):
        logger.info("Google API 金鑰未設定，使用預設模型列表")
        return FALLBACK_MODELS["google"]

    try:
        resp = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": api_key},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        models = []
        for m in data.get("models", []):
            # 模型名稱格式: models/gemini-2.5-pro
            full_name = m.get("name", "")
            model_id = full_name.replace("models/", "")
            display_name = m.get("displayName", model_id)

            # 只保留支援 generateContent 的模型（排除純嵌入模型）
            supported_methods = m.get("supportedGenerationMethods", [])
            if "generateContent" not in supported_methods:
                continue

            # 只保留 gemini 系列
            if not model_id.startswith("gemini"):
                continue

            models.append({"id": model_id, "name": display_name})

        # 按版本排序
        priority_prefixes = [
            "gemini-2.5-pro", "gemini-2.5-flash",
            "gemini-2.0", "gemini-1.5-pro", "gemini-1.5-flash"
        ]

        def sort_key(model):
            mid = model["id"]
            for i, prefix in enumerate(priority_prefixes):
                if mid.startswith(prefix):
                    return (i, mid)
            return (len(priority_prefixes), mid)

        models.sort(key=sort_key)

        if models:
            _set_cache("google", models)
            logger.info(f"從 Google API 取得 {len(models)} 個模型")
            return models

    except Exception as e:
        logger.warning(f"Google API 模型列表取得失敗: {e}")

    return FALLBACK_MODELS["google"]


def fetch_openrouter_models() -> list[dict]:
    """從 OpenRouter API 取得可用模型列表"""
    cached = _get_cache("openrouter")
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        models = []
        for m in data.get("data", []):
            mid = m.get("id", "")
            mname = m.get("name", mid)
            models.append({"id": mid, "name": mname})

        # 按提供商分組排序
        provider_order = ["openai/", "anthropic/", "google/", "meta-llama/"]

        def sort_key(model):
            mid = model["id"]
            for i, prefix in enumerate(provider_order):
                if mid.startswith(prefix):
                    return (i, mid)
            return (len(provider_order), mid)

        models.sort(key=sort_key)

        if models:
            _set_cache("openrouter", models)
            logger.info(f"從 OpenRouter API 取得 {len(models)} 個模型")
            return models

    except Exception as e:
        logger.warning(f"OpenRouter API 模型列表取得失敗: {e}")

    return FALLBACK_MODELS["openrouter"]


def fetch_ollama_models() -> list[dict]:
    """從本地 Ollama 服務取得可用模型列表"""
    cached = _get_cache("ollama")
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()

        models = []
        for m in data.get("models", []):
            mname = m.get("name", "")
            models.append({"id": mname, "name": mname})

        if models:
            _set_cache("ollama", models)
            logger.info(f"從 Ollama 取得 {len(models)} 個模型")
            return models

    except Exception as e:
        logger.debug(f"Ollama 服務未啟動或連線失敗: {e}")

    return FALLBACK_MODELS["ollama"]


def fetch_custom_openai_models(base_url: str = None) -> list[dict]:
    """從自定義 OpenAI 相容端點取得模型列表"""
    if not base_url:
        base_url = os.getenv("CUSTOM_OPENAI_BASE_URL", "https://api.openai.com/v1")

    cache_key = f"custom_openai_{base_url}"
    cached = _get_cache(cache_key)
    if cached is not None:
        return cached

    api_key = os.getenv("CUSTOM_OPENAI_API_KEY", "")
    if not api_key:
        return FALLBACK_MODELS["custom_openai"]

    try:
        # 確保 URL 以 /models 結尾
        url = base_url.rstrip("/")
        if not url.endswith("/models"):
            url = f"{url}/models"

        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        models = []
        for m in data.get("data", []):
            mid = m.get("id", "")
            models.append({"id": mid, "name": mid})

        models.sort(key=lambda x: x["id"])

        if models:
            _set_cache(cache_key, models)
            logger.info(f"從自定義端點取得 {len(models)} 個模型")
            return models

    except Exception as e:
        logger.warning(f"自定義 OpenAI 端點模型列表取得失敗: {e}")

    return FALLBACK_MODELS["custom_openai"]


def fetch_models(provider: str, **kwargs) -> list[dict]:
    """統一入口：根據提供商取得模型列表

    回傳格式: [{"id": "model-id", "name": "顯示名稱"}, ...]
    """
    fetchers = {
        "openai": fetch_openai_models,
        "anthropic": fetch_anthropic_models,
        "google": fetch_google_models,
        "openrouter": fetch_openrouter_models,
        "ollama": fetch_ollama_models,
        "custom_openai": lambda: fetch_custom_openai_models(kwargs.get("base_url")),
    }

    fetcher = fetchers.get(provider)
    if fetcher:
        return fetcher()

    logger.warning(f"不支援的提供商: {provider}")
    return []
