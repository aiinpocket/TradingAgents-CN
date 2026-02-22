"""
股票分析 API 路由
"""

import asyncio
import json
import secrets
import threading
import time
from collections import OrderedDict
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(tags=["analysis"])

# 進行中的分析任務（有上限的有序字典）
_MAX_ANALYSES = 100
_SSE_TIMEOUT_SECONDS = 1800  # 30 分鐘
_active_analyses: OrderedDict = OrderedDict()
_analyses_lock = threading.Lock()


class LLMProvider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"


# 允許的模型白名單
_ALLOWED_MODELS = {
    "openai": {"o4-mini", "gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"},
    "anthropic": {"claude-sonnet-4-20250514", "claude-haiku-4-20250514", "claude-opus-4-20250514"},
}


class AnalysisRequest(BaseModel):
    """分析請求"""
    stock_symbol: str = Field(..., min_length=1, max_length=5, pattern=r"^[A-Za-z]+$")
    analysis_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    analysts: list[str] = Field(default=["market", "social", "news", "fundamentals"])
    research_depth: int = Field(default=3, ge=1, le=5)
    llm_provider: LLMProvider = Field(default=LLMProvider.openai)
    llm_model: Optional[str] = None


class AnalysisStatus(BaseModel):
    """分析狀態"""
    analysis_id: str
    status: str
    stock_symbol: str
    progress: list[str] = []
    result: Optional[dict] = None
    error: Optional[str] = None


def _cleanup_old_analyses():
    """清理已完成的舊分析，保持在上限以下"""
    with _analyses_lock:
        while len(_active_analyses) >= _MAX_ANALYSES:
            # 移除最舊的已完成任務
            removed = False
            for aid in list(_active_analyses.keys()):
                if _active_analyses[aid]["status"] in ("completed", "failed"):
                    _active_analyses.pop(aid, None)
                    removed = True
                    break
            if not removed:
                # 如果沒有已完成的任務，移除最舊的
                _active_analyses.popitem(last=False)


@router.post("/analysis/start")
async def start_analysis(req: AnalysisRequest):
    """啟動股票分析"""
    import re

    # 驗證股票代碼
    symbol = req.stock_symbol.upper().strip()
    if not re.match(r"^[A-Z]{1,5}$", symbol):
        raise HTTPException(status_code=400, detail="股票代碼格式錯誤，應為 1-5 位英文字母")

    # 驗證日期
    try:
        datetime.strptime(req.analysis_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式錯誤，應為 YYYY-MM-DD")

    # 驗證分析師
    valid_analysts = {"market", "social", "news", "fundamentals"}
    invalid = set(req.analysts) - valid_analysts
    if invalid:
        raise HTTPException(status_code=400, detail=f"無效的分析師類型: {', '.join(invalid)}")

    # 驗證模型
    provider = req.llm_provider.value
    llm_model = req.llm_model
    if not llm_model:
        if provider == "openai":
            llm_model = "o4-mini"
        else:
            llm_model = "claude-sonnet-4-20250514"
    elif llm_model not in _ALLOWED_MODELS.get(provider, set()):
        raise HTTPException(status_code=400, detail=f"不支援的模型: {llm_model}")

    # 限制並行分析數量
    with _analyses_lock:
        running_count = sum(1 for d in _active_analyses.values() if d["status"] == "running")
    if running_count >= 3:
        raise HTTPException(status_code=429, detail="同時分析數量已達上限，請稍後再試")

    # 清理舊任務
    _cleanup_old_analyses()

    # 使用安全隨機 ID
    analysis_id = f"analysis_{secrets.token_urlsafe(16)}"

    with _analyses_lock:
        _active_analyses[analysis_id] = {
            "status": "pending",
            "stock_symbol": symbol,
            "analysis_date": req.analysis_date,
            "analysts": req.analysts,
            "research_depth": req.research_depth,
            "llm_provider": provider,
            "llm_model": llm_model,
            "progress": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
        }

    # 在背景執行分析
    task = asyncio.create_task(_run_analysis(analysis_id))
    with _analyses_lock:
        _active_analyses[analysis_id]["_task"] = task

    return {"analysis_id": analysis_id, "status": "pending"}


@router.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """取得分析狀態"""
    with _analyses_lock:
        data = _active_analyses.get(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="分析任務不存在")

    return AnalysisStatus(
        analysis_id=analysis_id,
        status=data["status"],
        stock_symbol=data["stock_symbol"],
        progress=list(data["progress"]),
        result=data.get("result"),
        error=data.get("error"),
    )


@router.get("/analysis/{analysis_id}/stream")
async def stream_analysis(analysis_id: str, request: Request):
    """SSE 串流分析進度"""
    with _analyses_lock:
        if analysis_id not in _active_analyses:
            raise HTTPException(status_code=404, detail="分析任務不存在")

    async def event_generator():
        last_idx = 0
        start_time = time.time()
        while True:
            # 偵測客戶端斷線
            if await request.is_disconnected():
                break

            # SSE 超時保護
            if time.time() - start_time > _SSE_TIMEOUT_SECONDS:
                yield f"data: {json.dumps({'type': 'failed', 'error': '分析超時'}, ensure_ascii=False)}\n\n"
                break

            data = _active_analyses.get(analysis_id)
            if not data:
                break

            # 發送新的進度訊息
            progress = data["progress"]
            if len(progress) > last_idx:
                for msg in progress[last_idx:]:
                    yield f"data: {json.dumps({'type': 'progress', 'message': msg}, ensure_ascii=False)}\n\n"
                last_idx = len(progress)

            # 檢查完成狀態
            if data["status"] == "completed":
                yield f"data: {json.dumps({'type': 'completed', 'result': data.get('result', {})}, ensure_ascii=False)}\n\n"
                break
            elif data["status"] == "failed":
                yield f"data: {json.dumps({'type': 'failed', 'error': data.get('error', '未知錯誤')}, ensure_ascii=False)}\n\n"
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/analysis/history")
async def get_analysis_history():
    """取得分析歷史"""
    with _analyses_lock:
        snapshot = list(_active_analyses.items())
    history = []
    for aid, data in snapshot:
        history.append({
            "analysis_id": aid,
            "status": data["status"],
            "stock_symbol": data["stock_symbol"],
            "analysis_date": data.get("analysis_date", ""),
            "created_at": data.get("created_at", 0),
            "llm_provider": data.get("llm_provider", ""),
            "research_depth": data.get("research_depth", 3),
        })
    # 按建立時間排序，最新的在後面
    history.sort(key=lambda x: x["created_at"])
    return {"analyses": history[-20:]}


async def _run_analysis(analysis_id: str):
    """背景執行分析"""
    with _analyses_lock:
        data = _active_analyses.get(analysis_id)
    if not data:
        return

    data["status"] = "running"
    data["progress"].append("啟動分析引擎...")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            _sync_run_analysis,
            analysis_id,
            data["stock_symbol"],
            data["analysis_date"],
            data["analysts"],
            data["research_depth"],
            data["llm_provider"],
            data["llm_model"],
        )

        if result.get("success"):
            data["status"] = "completed"
            from web.utils.analysis_runner import format_analysis_results
            formatted = format_analysis_results(result)
            data["result"] = formatted
            data["progress"].append("分析完成")
        else:
            data["status"] = "failed"
            error_msg = result.get("error", "分析失敗")
            data["error"] = error_msg
            data["progress"].append(f"分析失敗: {error_msg}")

    except Exception as e:
        data["status"] = "failed"
        # 不洩漏內部錯誤細節給前端
        data["error"] = "分析過程中發生內部錯誤，請查看伺服器日誌"
        data["progress"].append("分析過程中發生錯誤")
        try:
            from tradingagents.utils.logging_manager import get_logger
            get_logger("api").error(f"分析 {analysis_id} 異常: {e}", exc_info=True)
        except ImportError:
            pass


def _sync_run_analysis(analysis_id, symbol, date, analysts, depth, provider, model):
    """同步執行分析（在執行緒池中執行）"""
    data = _active_analyses.get(analysis_id)

    def progress_callback(message, step=None, total_steps=None):
        if data:
            # 限制單條訊息長度，防止記憶體濫用
            if len(message) > 1000:
                message = message[:1000] + "..."
            data["progress"].append(message)

    from web.utils.analysis_runner import run_stock_analysis

    return run_stock_analysis(
        stock_symbol=symbol,
        analysis_date=date,
        analysts=analysts,
        research_depth=depth,
        llm_provider=provider,
        llm_model=model,
        progress_callback=progress_callback,
    )
