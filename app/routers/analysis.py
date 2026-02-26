"""
股票分析 API 路由
"""

import asyncio
import json
import re
import secrets
import threading
import time
from collections import OrderedDict, deque
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger("analysis")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("analysis")

router = APIRouter(tags=["analysis"])


# ---------------------------------------------------------------------------
# 後端 i18n 錯誤訊息
# ---------------------------------------------------------------------------
_ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "invalid_symbol": {
        "zh-TW": "股票代碼格式錯誤，應為 1-5 位英文字母",
        "en": "Invalid stock symbol. Must be 1-5 alphabetical characters.",
    },
    "invalid_date_format": {
        "zh-TW": "日期格式錯誤，應為 YYYY-MM-DD",
        "en": "Invalid date format. Expected YYYY-MM-DD.",
    },
    "date_too_old": {
        "zh-TW": "分析日期不能早於 2000-01-01",
        "en": "Analysis date cannot be earlier than 2000-01-01.",
    },
    "date_future": {
        "zh-TW": "分析日期不能是未來日期",
        "en": "Analysis date cannot be a future date.",
    },
    "no_analysts": {
        "zh-TW": "必須至少選擇一個分析模組",
        "en": "At least one analysis module must be selected.",
    },
    "invalid_analysts": {
        "zh-TW": "無效的分析師類型: {detail}",
        "en": "Invalid analyst type: {detail}",
    },
    "unsupported_model": {
        "zh-TW": "不支援的模型: {detail}",
        "en": "Unsupported model: {detail}",
    },
    "analyses_limit": {
        "zh-TW": "同時分析數量已達上限，請稍後再試",
        "en": "Maximum concurrent analyses reached. Please try again later.",
    },
    "task_not_found": {
        "zh-TW": "分析任務不存在",
        "en": "Analysis task not found.",
    },
    "analysis_timeout": {
        "zh-TW": "分析超時",
        "en": "Analysis timed out.",
    },
    "unknown_error": {
        "zh-TW": "未知錯誤",
        "en": "Unknown error.",
    },
    "engine_starting": {
        "zh-TW": "啟動分析引擎...",
        "en": "Starting analysis engine...",
    },
    "generating_english": {
        "zh-TW": "正在生成英文版本...",
        "en": "Generating English version...",
    },
    "analysis_complete": {
        "zh-TW": "分析完成",
        "en": "Analysis complete.",
    },
    "analysis_failed": {
        "zh-TW": "分析失敗",
        "en": "Analysis failed.",
    },
    "analysis_error": {
        "zh-TW": "分析過程中發生錯誤",
        "en": "An error occurred during analysis.",
    },
    "internal_error": {
        "zh-TW": "分析過程中發生內部錯誤，請查看伺服器日誌",
        "en": "Internal error during analysis. Please check server logs.",
    },
    "invalid_symbol_short": {
        "zh-TW": "股票代碼格式錯誤",
        "en": "Invalid stock symbol.",
    },
    "stock_context_error": {
        "zh-TW": "取得個股資料失敗，請稍後重試",
        "en": "Failed to fetch stock data. Please try again later.",
    },
}


def _get_lang(request: Request | None = None) -> str:
    """從 query param 或 Accept-Language header 解析語言偏好，預設繁體中文"""
    if request is None:
        return "zh-TW"
    # 優先使用 query param（SSE 不支援自訂 header）
    lang_param = request.query_params.get("lang", "")
    if lang_param == "en":
        return "en"
    if lang_param == "zh-TW":
        return "zh-TW"
    # fallback 到 Accept-Language header
    accept = request.headers.get("accept-language", "")
    if "en" in accept.lower() and "zh" not in accept.lower():
        return "en"
    return "zh-TW"


def _t(key: str, request: Request | None = None, **kwargs) -> str:
    """取得 i18n 錯誤訊息（從 Request header 推斷語言）"""
    lang = _get_lang(request)
    return _t_lang(key, lang, **kwargs)


def _t_lang(key: str, lang: str = "zh-TW", **kwargs) -> str:
    """取得 i18n 錯誤訊息（直接指定語言）"""
    msgs = _ERROR_MESSAGES.get(key, {})
    msg = msgs.get(lang, msgs.get("zh-TW", key))
    if kwargs:
        msg = msg.format(**kwargs)
    return msg


# 輸入驗證（預編譯正則表達式）
_SYMBOL_RE = re.compile(r"^[A-Z]{1,5}$")
_ANALYSIS_ID_RE = re.compile(r"^analysis_[A-Za-z0-9_-]{22}$")

# 進行中的分析任務（有上限的有序字典）
_MAX_ANALYSES = 100
_SSE_TIMEOUT_SECONDS = 1800  # 30 分鐘
_ANALYSIS_TIMEOUT_SECONDS = 1800  # 分析任務最大執行時間（30 分鐘），防止無限卡住
_ANALYSIS_EXPIRE_SECONDS = 7200  # 2 小時後自動清理已完成的分析
_active_analyses: OrderedDict = OrderedDict()
_analyses_lock = threading.Lock()


def _validate_analysis_id(analysis_id: str) -> bool:
    """驗證 analysis_id 格式（analysis_ + 22 位 URL-safe base64）"""
    return bool(_ANALYSIS_ID_RE.match(analysis_id))


class LLMProvider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"


# 允許的模型白名單
_ALLOWED_MODELS = {
    "openai": {"o4-mini", "gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"},
    "anthropic": {
        "claude-sonnet-4-6", "claude-opus-4-6",
        "claude-haiku-4-5-20251001",
        "claude-sonnet-4-20250514", "claude-opus-4-20250514",
    },
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
    now = time.time()
    with _analyses_lock:
        # 先清理超時的已完成任務
        expired = [
            aid for aid, d in _active_analyses.items()
            if d["status"] in ("completed", "failed")
            and now - d.get("created_at", 0) > _ANALYSIS_EXPIRE_SECONDS
        ]
        for aid in expired:
            _active_analyses.pop(aid, None)

        # 再檢查數量上限
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
async def start_analysis(req: AnalysisRequest, request: Request):
    """啟動股票分析"""
    # 驗證股票代碼
    symbol = req.stock_symbol.upper().strip()
    if not _SYMBOL_RE.match(symbol):
        raise HTTPException(status_code=400, detail=_t("invalid_symbol", request))

    # 驗證日期
    try:
        analysis_date_obj = datetime.strptime(req.analysis_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail=_t("invalid_date_format", request))
    _MIN_DATE = datetime(2000, 1, 1).date()
    if analysis_date_obj.date() < _MIN_DATE:
        raise HTTPException(status_code=400, detail=_t("date_too_old", request))
    if analysis_date_obj.date() > datetime.now().date():
        raise HTTPException(status_code=400, detail=_t("date_future", request))

    # 驗證分析師
    if not req.analysts:
        raise HTTPException(status_code=400, detail=_t("no_analysts", request))
    valid_analysts = {"market", "social", "news", "fundamentals"}
    invalid = set(req.analysts) - valid_analysts
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=_t("invalid_analysts", request, detail=", ".join(invalid)),
        )

    # 驗證模型
    provider = req.llm_provider.value
    llm_model = req.llm_model
    if not llm_model:
        if provider == "openai":
            llm_model = "o4-mini"
        else:
            llm_model = "claude-sonnet-4-20250514"
    elif llm_model not in _ALLOWED_MODELS.get(provider, set()):
        raise HTTPException(
            status_code=400,
            detail=_t("unsupported_model", request, detail=llm_model),
        )

    # 去除重複的分析師（保留順序）
    req_analysts = list(dict.fromkeys(req.analysts))

    # 查詢 MongoDB 快取：24 小時內同一股票同一日期的已完成報告
    try:
        from web.utils.mongodb_report_manager import MongoDBReportManager
        _cache_mgr = MongoDBReportManager()
        cached = _cache_mgr.get_latest_report(symbol, req.analysis_date)
        if cached and cached.get("formatted_result"):
            logger.info(f"分析快取命中: {symbol} @ {req.analysis_date}")
            return {"analysis_id": "cached", "status": "cached",
                    "result": cached["formatted_result"]}
    except Exception as e:
        logger.debug(f"MongoDB 快取查詢失敗（不影響正常流程）: {e}")

    # 清理舊任務 + 原子性地檢查並發限制 + 建立新分析
    _cleanup_old_analyses()

    analysis_id = f"analysis_{secrets.token_urlsafe(16)}"
    lang = _get_lang(request)

    with _analyses_lock:
        running_count = sum(1 for d in _active_analyses.values() if d["status"] == "running")
        if running_count >= 3:
            raise HTTPException(status_code=429, detail=_t("analyses_limit", request))

        _active_analyses[analysis_id] = {
            "status": "pending",
            "stock_symbol": symbol,
            "analysis_date": req.analysis_date,
            "analysts": req_analysts,
            "research_depth": req.research_depth,
            "llm_provider": provider,
            "llm_model": llm_model,
            "progress": deque(maxlen=200),
            "result": None,
            "error": None,
            "created_at": time.time(),
            "lang": lang,
        }

    # 在背景執行分析
    task = asyncio.create_task(_run_analysis(analysis_id))
    with _analyses_lock:
        _active_analyses[analysis_id]["_task"] = task

    return {"analysis_id": analysis_id, "status": "pending"}


@router.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str, request: Request):
    """取得分析狀態"""
    if not _validate_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail=_t("task_not_found", request))
    with _analyses_lock:
        data = _active_analyses.get(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail=_t("task_not_found", request))

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
    if not _validate_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail=_t("task_not_found", request))
    lang = _get_lang(request)
    with _analyses_lock:
        if analysis_id not in _active_analyses:
            raise HTTPException(status_code=404, detail=_t("task_not_found", request))

    async def event_generator():
        last_idx = 0
        start_time = time.time()
        last_heartbeat = time.time()
        while True:
            if await request.is_disconnected():
                break

            if time.time() - start_time > _SSE_TIMEOUT_SECONDS:
                yield f"data: {json.dumps({'type': 'failed', 'error': _t('analysis_timeout', request)}, ensure_ascii=False)}\n\n"
                break

            data = _active_analyses.get(analysis_id)
            if not data:
                break

            # 在鎖內快照 progress，避免 deque 旋轉導致 IndexError
            with _analyses_lock:
                progress_snapshot = list(data["progress"])
            current_len = len(progress_snapshot)
            if current_len > last_idx:
                for i in range(last_idx, current_len):
                    msg = progress_snapshot[i]
                    yield f"data: {json.dumps({'type': 'progress', 'message': msg}, ensure_ascii=False)}\n\n"
                last_idx = current_len
                last_heartbeat = time.time()

            # 檢查完成狀態
            if data["status"] == "completed":
                yield f"data: {json.dumps({'type': 'completed', 'result': data.get('result', {})}, ensure_ascii=False)}\n\n"
                break
            elif data["status"] == "failed":
                fallback_err = _t("unknown_error", request)
                yield f"data: {json.dumps({'type': 'failed', 'error': data.get('error', fallback_err)}, ensure_ascii=False)}\n\n"
                break

            # SSE heartbeat：每 15 秒發送一次，防止 proxy 因閒置斷線
            if time.time() - last_heartbeat > 15:
                yield ": heartbeat\n\n"
                last_heartbeat = time.time()

            await asyncio.sleep(0.5)

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


def _update_analysis_state(analysis_id: str, **updates):
    """執行緒安全地更新分析狀態"""
    with _analyses_lock:
        data = _active_analyses.get(analysis_id)
        if data:
            for key, value in updates.items():
                data[key] = value
    return data


async def _run_analysis(analysis_id: str):
    """背景執行分析"""
    with _analyses_lock:
        data = _active_analyses.get(analysis_id)
    if not data:
        return

    lang = data.get("lang", "zh-TW")
    _update_analysis_state(analysis_id, status="running")
    data["progress"].append(_t_lang("engine_starting", lang))

    try:
        loop = asyncio.get_running_loop()
        # 超時保護：防止分析任務無限卡住佔用執行緒池
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                _sync_run_analysis,
                analysis_id,
                data["stock_symbol"],
                data["analysis_date"],
                data["analysts"],
                data["research_depth"],
                data["llm_provider"],
                data["llm_model"],
                lang,
            ),
            timeout=_ANALYSIS_TIMEOUT_SECONDS,
        )

        if result.get("success"):
            from web.utils.analysis_runner import format_analysis_results
            formatted = format_analysis_results(result, lang=lang)

            # 台灣術語確定性校正（中文報告欄位）
            try:
                from app.routers.trending import _normalize_tw_terminology
                state_zh = formatted.get("state", {})
                for sk, sv in state_zh.items():
                    if isinstance(sv, str):
                        state_zh[sk] = _normalize_tw_terminology(sv)
                    elif isinstance(sv, dict):
                        for dk, dv in sv.items():
                            if isinstance(dv, str):
                                sv[dk] = _normalize_tw_terminology(dv)
                dec = formatted.get("decision", {})
                for dk in ("action", "reasoning"):
                    if isinstance(dec.get(dk), str):
                        dec[dk] = _normalize_tw_terminology(dec[dk])
            except Exception:
                pass  # 術語校正非關鍵路徑

            # 翻譯成英文版本
            data["progress"].append(_t_lang("generating_english", lang))
            try:
                translation = await loop.run_in_executor(
                    None, _translate_result_to_english, formatted
                )
                if translation:
                    if translation.get("state_en"):
                        formatted["state_en"] = translation["state_en"]
                    if translation.get("decision_en"):
                        formatted["decision_en"] = translation["decision_en"]
            except Exception as e:
                logger.warning(f"翻譯步驟失敗（不影響主流程）: {e}")

            data["progress"].append(_t_lang("analysis_complete", lang))
            _update_analysis_state(analysis_id, status="completed", result=formatted)

            # 儲存格式化結果到 MongoDB 供後續快取查詢
            try:
                from web.utils.mongodb_report_manager import MongoDBReportManager
                _save_mgr = MongoDBReportManager()
                _save_mgr.save_analysis_report(
                    stock_symbol=data["stock_symbol"],
                    analysis_results=result,
                    reports={},
                    analysis_date=data.get("analysis_date", ""),
                    formatted_result=formatted,
                )
            except Exception as e:
                logger.warning(f"MongoDB 快取儲存失敗（不影響主流程）: {e}")

        else:
            error_msg = result.get("error", _t_lang("analysis_failed", lang))
            data["progress"].append(f"{_t_lang('analysis_failed', lang)}: {error_msg}")
            _update_analysis_state(analysis_id, status="failed", error=error_msg)

    except asyncio.TimeoutError:
        timeout_min = _ANALYSIS_TIMEOUT_SECONDS // 60
        data["progress"].append(_t_lang("analysis_error", lang))
        _update_analysis_state(
            analysis_id,
            status="failed",
            error=_t_lang("internal_error", lang),
        )
        logger.warning(f"分析 ...{analysis_id[-4:]} 超時（{timeout_min} 分鐘），已強制終止")

    except Exception as e:
        data["progress"].append(_t_lang("analysis_error", lang))
        _update_analysis_state(
            analysis_id,
            status="failed",
            error=_t_lang("internal_error", lang),
        )
        logger.error(f"分析 ...{analysis_id[-4:]} 異常: {e}", exc_info=True)

    finally:
        # 清理 asyncio.Task 引用，釋放記憶體
        with _analyses_lock:
            entry = _active_analyses.get(analysis_id)
            if entry:
                entry.pop("_task", None)


def _sync_run_analysis(analysis_id, symbol, date, analysts, depth, provider, model, lang="zh-TW"):
    """同步執行分析（在執行緒池中執行）"""
    data = _active_analyses.get(analysis_id)

    def progress_callback(message, step=None, total_steps=None):
        if data:
            # 限制單條訊息長度，防止記憶體濫用
            if len(message) > 1000:
                logger.warning(
                    f"分析 ...{analysis_id[-4:]} 進度訊息被截斷（{len(message)} 字元）"
                )
                message = message[:1000] + "..."
            # deque(maxlen=200) 自動丟棄最舊訊息
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
        lang=lang,
    )


# ---------------------------------------------------------------------------
# 分析結果翻譯（中文 -> 英文）
# ---------------------------------------------------------------------------

_TRANSLATE_SYSTEM_PROMPT = (
    "You are a professional financial translator. "
    "Translate the following JSON values from Traditional Chinese to English. "
    "Rules:\n"
    "1. Preserve all Markdown formatting (headers, tables, bullet points, bold)\n"
    "2. Use accurate financial terminology\n"
    "3. Keep stock symbols, numbers, dates, and percentages unchanged\n"
    "4. Return valid JSON with the exact same keys\n"
    "5. Only translate the values, not the keys"
)

# 翻譯用 LLM 客戶端快取（避免每次翻譯都重新初始化）
_translate_clients: dict = {}
_translate_clients_lock = threading.Lock()


def _get_translate_client(provider: str):
    """取得或建立翻譯用 LLM 客戶端（執行緒安全懶初始化）"""
    import os
    with _translate_clients_lock:
        if provider not in _translate_clients:
            if provider == "openai":
                from openai import OpenAI
                _translate_clients[provider] = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            else:
                from anthropic import Anthropic
                _translate_clients[provider] = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        return _translate_clients[provider]


def _translate_result_to_english(formatted_result: dict) -> dict | None:
    """將分析結果翻譯成英文，支援 OpenAI / Anthropic 自動 fallback。

    嘗試順序：OpenAI gpt-4o-mini -> Anthropic claude-haiku-4-5-20251001
    回傳 {state_en, decision_en} 或 None（翻譯不影響主流程）。
    """
    import os

    state = formatted_result.get("state", {})
    decision = formatted_result.get("decision", {})

    # 收集需要翻譯的文字欄位
    payload: dict = {}

    # state 中的報告文字（字串型）
    report_keys = [
        "market_report", "fundamentals_report", "sentiment_report",
        "news_report", "risk_assessment",
    ]
    for k in report_keys:
        v = state.get(k)
        if isinstance(v, str) and v.strip():
            payload[f"state.{k}"] = v

    # investment_debate_state（可能是字串或 dict）
    debate = state.get("investment_debate_state")
    if isinstance(debate, str) and debate.strip():
        payload["state.investment_debate_state"] = debate
    elif isinstance(debate, dict):
        for dk in ("bull_history", "bear_history", "judge_decision"):
            dv = debate.get(dk)
            if isinstance(dv, str) and dv.strip():
                payload[f"state.investment_debate_state.{dk}"] = dv

    # risk_debate_state（風險辯論，可能是字串或 dict）
    risk_debate = state.get("risk_debate_state")
    if isinstance(risk_debate, str) and risk_debate.strip():
        payload["state.risk_debate_state"] = risk_debate
    elif isinstance(risk_debate, dict):
        for rk in ("risky_history", "safe_history", "neutral_history", "judge_decision"):
            rv = risk_debate.get(rk)
            if isinstance(rv, str) and rv.strip():
                payload[f"state.risk_debate_state.{rk}"] = rv

    # decision 欄位
    if decision.get("action"):
        payload["decision.action"] = str(decision["action"])
    if decision.get("reasoning"):
        payload["decision.reasoning"] = str(decision["reasoning"])

    if not payload:
        return None

    # 組裝 LLM 提供商列表（按優先順序）
    providers: list[tuple[str, str]] = []
    if os.environ.get("OPENAI_API_KEY", ""):
        providers.append(("openai", "gpt-4o-mini"))
    if os.environ.get("ANTHROPIC_API_KEY", ""):
        providers.append(("anthropic", "claude-haiku-4-5-20251001"))
    if not providers:
        logger.info("翻譯跳過：無可用的 LLM API 金鑰")
        return None

    user_content = json.dumps(payload, ensure_ascii=False)
    translated: dict | None = None
    last_error = ""

    for provider, model in providers:
        try:
            if provider == "openai":
                client = _get_translate_client("openai")
                resp = client.chat.completions.create(
                    model=model,
                    temperature=0.3,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": _TRANSLATE_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                )
                translated = json.loads(resp.choices[0].message.content)
            else:
                client = _get_translate_client("anthropic")
                resp = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    temperature=0.3,
                    system=_TRANSLATE_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_content}],
                )
                # 從回應文字中解析 JSON（穩健處理 code fence 變體）
                raw = resp.content[0].text.strip()
                fence_match = re.search(r"```(?:json)?[ \t]*\n([\s\S]*?)\n[ \t]*```", raw)
                if fence_match:
                    raw = fence_match.group(1)
                translated = json.loads(raw)

            logger.info(f"翻譯成功 (provider={provider}, model={model})")
            break

        except Exception as e:
            last_error = str(e)[:200]
            logger.warning(f"翻譯 {provider}/{model} 失敗，嘗試下一個: {last_error}")
            continue

    if translated is None:
        logger.warning(f"所有翻譯提供商失敗，最後錯誤: {last_error}")
        return None

    # 重新組裝成 state_en / decision_en
    state_en: dict = {}
    decision_en: dict = {}

    for k in report_keys:
        tv = translated.get(f"state.{k}")
        if tv:
            state_en[k] = tv

    # debate
    if isinstance(debate, str):
        tv = translated.get("state.investment_debate_state")
        if tv:
            state_en["investment_debate_state"] = tv
    elif isinstance(debate, dict):
        debate_en_parts: dict = {}
        for dk in ("bull_history", "bear_history", "judge_decision"):
            tv = translated.get(f"state.investment_debate_state.{dk}")
            if tv:
                debate_en_parts[dk] = tv
        if debate_en_parts:
            state_en["investment_debate_state"] = {**debate, **debate_en_parts}

    # risk_debate
    if isinstance(risk_debate, str):
        tv = translated.get("state.risk_debate_state")
        if tv:
            state_en["risk_debate_state"] = tv
    elif isinstance(risk_debate, dict):
        risk_en_parts: dict = {}
        for rk in ("risky_history", "safe_history", "neutral_history", "judge_decision"):
            tv = translated.get(f"state.risk_debate_state.{rk}")
            if tv:
                risk_en_parts[rk] = tv
        if risk_en_parts:
            state_en["risk_debate_state"] = {**risk_debate, **risk_en_parts}

    # decision
    if translated.get("decision.action"):
        decision_en["action"] = translated["decision.action"]
    if translated.get("decision.reasoning"):
        decision_en["reasoning"] = translated["decision.reasoning"]
    # 數值欄位直接複製
    for nk in ("confidence", "risk_score", "target_price"):
        if decision.get(nk) is not None:
            decision_en[nk] = decision[nk]

    return {"state_en": state_en or None, "decision_en": decision_en or None}


# ---------------------------------------------------------------------------
# 個股快照 API（即時行情 + 新聞）
# ---------------------------------------------------------------------------
_CONTEXT_CACHE: dict = {}
_CONTEXT_CACHE_TTL = 600  # 10 分鐘
_MAX_CONTEXT_CACHE = 200  # 快取條目上限

_PAID_NEWS_SOURCES = {
    "the wall street journal", "wsj", "wall street journal",
    "bloomberg", "financial times", "ft", "barron's", "barrons",
    "barrons.com", "the economist", "investor's business daily", "ibd",
}


def _fetch_stock_context(symbol: str) -> dict:
    """取得個股即時行情、關鍵指標和近期新聞（同步，在 executor 中執行）"""
    try:
        import yfinance as yf
    except ImportError:
        return {"error": "yfinance not installed"}

    result: dict = {"symbol": symbol}

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}

        # 基本行情
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
        change = round(price - prev_close, 2) if price and prev_close else 0
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0

        result.update({
            "name": info.get("shortName") or info.get("longName", symbol),
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "volume": info.get("volume") or info.get("regularMarketVolume", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "week52_high": info.get("fiftyTwoWeekHigh"),
            "week52_low": info.get("fiftyTwoWeekLow"),
            "beta": info.get("beta"),
        })

        # 近期新聞
        news_list = []
        try:
            raw_news = ticker.news or []
            for item in raw_news[:12]:
                content = item.get("content", {}) if isinstance(item, dict) else {}
                if content:
                    title = content.get("title", "")
                    canonical = content.get("canonicalUrl", {})
                    link = canonical.get("url", "") if isinstance(canonical, dict) else ""
                    provider = content.get("provider", {})
                    publisher = provider.get("displayName", "") if isinstance(provider, dict) else ""
                    pub_date_str = content.get("pubDate", "")
                else:
                    title = item.get("title", "")
                    link = item.get("link", "")
                    publisher = item.get("publisher", "")
                    pub_date_ts = item.get("providerPublishTime", 0)
                    pub_date_str = (
                        datetime.fromtimestamp(pub_date_ts).strftime("%Y-%m-%d %H:%M")
                        if pub_date_ts else ""
                    )

                if not title or not link:
                    continue
                if publisher.lower() in _PAID_NEWS_SOURCES:
                    continue

                date_display = ""
                if pub_date_str and "T" in str(pub_date_str):
                    try:
                        dt = datetime.fromisoformat(str(pub_date_str).replace("Z", "+00:00"))
                        date_display = dt.strftime("%Y-%m-%d %H:%M")
                    except (ValueError, TypeError):
                        date_display = str(pub_date_str)[:16]
                elif pub_date_str:
                    date_display = str(pub_date_str)

                news_list.append({
                    "title": title,
                    "url": link,
                    "source": publisher,
                    "date": date_display,
                })

            # 去重
            seen = set()
            unique_news = []
            for n in news_list:
                if n["title"] not in seen:
                    seen.add(n["title"])
                    unique_news.append(n)
            news_list = unique_news[:8]

        except Exception as e:
            logger.debug(f"取得 {symbol} 新聞失敗: {e}")

        result["news"] = news_list

    except Exception as e:
        logger.error(f"取得 {symbol} 個股快照失敗: {e}")
        result["error"] = "Failed to fetch stock data"

    return result


@router.get("/analysis/stock-context/{symbol}")
async def get_stock_context(symbol: str, request: Request):
    """取得個股即時快照（行情 + 指標 + 新聞）"""
    symbol = symbol.upper().strip()
    if not _SYMBOL_RE.match(symbol):
        raise HTTPException(status_code=400, detail=_t("invalid_symbol_short", request))

    # 快取檢查
    cache_key = f"ctx_{symbol}"
    cached = _CONTEXT_CACHE.get(cache_key)
    if cached and time.time() - cached["_ts"] < _CONTEXT_CACHE_TTL:
        return cached["data"]

    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, _fetch_stock_context, symbol)

    # 寫入快取
    now = time.time()
    _CONTEXT_CACHE[cache_key] = {"data": data, "_ts": now}

    # 清理過期快取 + 超過上限時淘汰最舊的條目
    expired = [k for k, v in _CONTEXT_CACHE.items() if now - v["_ts"] > _CONTEXT_CACHE_TTL * 2]
    for k in expired:
        _CONTEXT_CACHE.pop(k, None)
    if len(_CONTEXT_CACHE) > _MAX_CONTEXT_CACHE:
        sorted_keys = sorted(_CONTEXT_CACHE.keys(), key=lambda k: _CONTEXT_CACHE[k]["_ts"])
        for k in sorted_keys[:len(_CONTEXT_CACHE) - _MAX_CONTEXT_CACHE]:
            _CONTEXT_CACHE.pop(k, None)

    return data
