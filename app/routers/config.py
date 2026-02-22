"""
配置管理 API 路由
"""

import os
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(tags=["config"])

PROJECT_ROOT = Path(__file__).parent.parent.parent


@router.get("/config/status")
async def get_config_status():
    """取得 API 配置狀態"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    finnhub_key = os.getenv("FINNHUB_API_KEY", "")

    providers = []
    if openai_key:
        providers.append("openai")
    if anthropic_key:
        providers.append("anthropic")

    return {
        "configured": bool(openai_key or anthropic_key),
        "available_providers": providers,
        "keys": {
            "openai": {"configured": bool(openai_key)},
            "anthropic": {"configured": bool(anthropic_key)},
            "finnhub": {"configured": bool(finnhub_key)},
        },
    }


@router.get("/config/models")
async def get_available_models():
    """取得可用模型列表"""
    models = {
        "openai": [
            {"id": "o4-mini", "name": "o4-mini", "tier": "deep"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "tier": "quick"},
            {"id": "gpt-4o", "name": "GPT-4o", "tier": "deep"},
            {"id": "gpt-4.1", "name": "GPT-4.1", "tier": "deep"},
            {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini", "tier": "quick"},
            {"id": "gpt-4.1-nano", "name": "GPT-4.1 Nano", "tier": "quick"},
        ],
        "anthropic": [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "tier": "deep"},
            {"id": "claude-opus-4-20250514", "name": "Claude Opus 4", "tier": "deep"},
            {"id": "claude-haiku-4-20250514", "name": "Claude Haiku 4", "tier": "quick"},
        ],
    }

    # 只返回已配置的提供商
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    result = {}
    if openai_key:
        result["openai"] = models["openai"]
    if anthropic_key:
        result["anthropic"] = models["anthropic"]

    return {"models": result}
