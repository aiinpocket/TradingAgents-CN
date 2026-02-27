"""
配置管理 API 路由
"""

import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["config"])


@router.get("/config/status")
async def get_config_status():
    """取得 API 配置狀態（僅回傳前端必要資訊，避免過度揭露）"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    providers = []
    if openai_key:
        providers.append("openai")
    if anthropic_key:
        providers.append("anthropic")

    # 精簡回應：只回傳前端所需的 configured + available_providers
    content = {
        "configured": bool(providers),
        "available_providers": providers,
    }
    return JSONResponse(
        content=content,
        headers={"Cache-Control": "no-store"},
    )


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
            {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6", "tier": "deep"},
            {"id": "claude-opus-4-6", "name": "Claude Opus 4.6", "tier": "deep"},
            {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5", "tier": "quick"},
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "tier": "deep"},
            {"id": "claude-opus-4-20250514", "name": "Claude Opus 4", "tier": "deep"},
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
