"""
TradingAgents FastAPI 應用程式
提供快速載入與現代化的金融分析介面
"""

import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from dotenv import load_dotenv

# 應用程式版本（唯一來源：FastAPI、health endpoint 共用）
_APP_VERSION = "0.4.5"
# 靜態檔案快取版本戳（唯一來源：CSS/JS 改動時遞增字母後綴以強制 CDN 更新）
_CACHE_VERSION = "0.5.0g"

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 載入環境變數
load_dotenv(PROJECT_ROOT / ".env", override=True)

# 日誌
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger("api")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("api")


# ---------------------------------------------------------------------------
# 中介層用 i18n 錯誤訊息
# ---------------------------------------------------------------------------
_MW_ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "rate_limit": {
        "zh-TW": "請求過於頻繁，請稍後再試",
        "en": "Too many requests. Please try again later.",
    },
    "request_too_large": {
        "zh-TW": "請求內容過大",
        "en": "Request payload too large.",
    },
    "server_error": {
        "zh-TW": "伺服器內部錯誤，請查看日誌",
        "en": "Internal server error. Please check logs.",
    },
}


def _mw_lang(request: Request) -> str:
    """從 Accept-Language header 快速判斷語言（中介層專用）"""
    accept = (request.headers.get("accept-language") or "").lower()
    if "en" in accept and "zh" not in accept:
        return "en"
    return "zh-TW"


def _mw_t(key: str, request: Request) -> str:
    """取得中介層 i18n 錯誤訊息"""
    lang = _mw_lang(request)
    msgs = _MW_ERROR_MESSAGES.get(key, {})
    return msgs.get(lang, msgs.get("zh-TW", key))


# ---------------------------------------------------------------------------
# CSP（Content Security Policy）共用構建器
# 中介層預設 CSP 與首頁 nonce CSP 共用相同的指令集，避免維護兩份重複字串
# ---------------------------------------------------------------------------
_CSP_DIRECTIVES: dict[str, str] = {
    "default-src": "'self'",
    "script-src": "'self' 'unsafe-eval' https://cdn.jsdelivr.net https://www.googletagmanager.com https://www.google-analytics.com",
    "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src": "'self' https://fonts.gstatic.com",
    "img-src": "'self' data: https://www.googletagmanager.com https://www.google-analytics.com",
    "connect-src": "'self' https://cdn.jsdelivr.net https://www.google-analytics.com https://analytics.google.com https://www.googletagmanager.com",
    "frame-ancestors": "'none'",
    "base-uri": "'self'",
    "form-action": "'self'",
    "object-src": "'none'",
    "worker-src": "'self'",
}


# 預設 CSP（無 nonce/hash），啟動時組裝一次，API 路由直接使用
_DEFAULT_CSP = "; ".join(
    [f"{d} {v}" for d, v in _CSP_DIRECTIVES.items()] + ["upgrade-insecure-requests"]
)


def _build_csp(*, nonce: str = "", script_hash: str = "") -> str:
    """組合 CSP header 值（需 nonce/hash 時動態組裝，否則回傳預快取常數）

    Args:
        nonce: 可選的 CSP nonce（首頁 FOUC 防護內聯腳本用）
        script_hash: 可選的 script hash（配合 nonce 使用）
    """
    if not nonce and not script_hash:
        return _DEFAULT_CSP
    parts = []
    for directive, value in _CSP_DIRECTIVES.items():
        if directive == "script-src":
            extras = []
            if nonce:
                extras.append(f"'nonce-{nonce}'")
            if script_hash:
                extras.append(f"'sha256-{script_hash}'")
            value = value.replace("'unsafe-eval'", f"'unsafe-eval' {' '.join(extras)}")
        parts.append(f"{directive} {value}")
    parts.append("upgrade-insecure-requests")
    return "; ".join(parts)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    import asyncio

    logger.info("TradingAgents API 啟動中...")

    # 預初始化常用 LLM 客戶端，避免首次翻譯/分析時的冷啟動延遲
    try:
        from app.routers.trending import _get_llm, _get_ai_providers
        for provider, model in _get_ai_providers():
            _get_llm(provider, model, temperature=0)
            logger.info(f"LLM 客戶端預初始化完成: {provider}/{model}")
    except Exception as e:
        logger.warning(f"LLM 客戶端預初始化失敗（不影響正常運作）: {e}")

    # 背景預熱趨勢資料快取，讓第一位使用者不需等待白螢幕
    async def _prewarm_trending():
        try:
            from app.routers.trending import get_market_overview, _pregenerate_ai_analysis
            await asyncio.wait_for(get_market_overview(), timeout=45)
            logger.info("趨勢資料快取預熱完成")
            # AI 分析不阻塞啟動，改為 fire-and-forget
            asyncio.create_task(_safe_pregenerate_ai())
        except asyncio.TimeoutError:
            logger.warning("趨勢資料預熱逾時 45 秒（不影響正常運作）")
        except Exception as e:
            logger.warning(f"趨勢資料預熱失敗（不影響正常運作）: {e}")

    async def _safe_pregenerate_ai():
        """平行執行 AI 分析預產生 + Top 股票快照預快取"""
        async def _ai():
            try:
                from app.routers.trending import _pregenerate_ai_analysis
                await _pregenerate_ai_analysis()
                logger.info("AI 趨勢分析預產生完成")
            except Exception as e:
                logger.warning(f"AI 趨勢分析預產生失敗: {e}")

        async def _precache():
            try:
                from app.routers.trending import _precache_top_movers_context
                await _precache_top_movers_context()
            except Exception as e:
                logger.warning(f"Top 股票快照預快取失敗: {e}")

        await asyncio.gather(_ai(), _precache())

    # 等待預熱完成（最多 50 秒），確保首頁有 SSR 資料
    prewarm_task = asyncio.create_task(_prewarm_trending())
    try:
        await asyncio.wait_for(asyncio.shield(prewarm_task), timeout=50)
    except asyncio.TimeoutError:
        logger.warning("預熱逾時 50 秒，首頁 SSR 可能為空（不阻塞啟動）")
    except Exception as e:
        logger.warning(f"預熱失敗（不阻塞啟動）: {e}")

    # 啟動背景定時刷新（每 5 分鐘自動更新市場資料）
    from app.routers.trending import start_background_refresh
    refresh_task = asyncio.create_task(start_background_refresh())

    yield

    # 優雅關閉背景任務：先取消再等待實際終止（設超時避免阻塞關閉流程）
    prewarm_task.cancel()
    refresh_task.cancel()
    try:
        await asyncio.wait_for(
            asyncio.gather(prewarm_task, refresh_task, return_exceptions=True),
            timeout=10.0,
        )
    except asyncio.TimeoutError:
        logger.warning("背景任務清理超時（10s），強制繼續關閉")
    except Exception as e:
        logger.warning(f"背景任務清理異常: {e}")
    # 關閉所有執行緒池，避免資源洩漏（wait=False 避免阻塞關閉）
    from app.routers.trending import _TRENDING_EXECUTOR, _SUBTASK_EXECUTOR
    _TRENDING_EXECUTOR.shutdown(wait=False, cancel_futures=True)
    _SUBTASK_EXECUTOR.shutdown(wait=False, cancel_futures=True)
    try:
        from app.routers.analysis import _ANALYSIS_EXECUTOR, _CONTEXT_EXECUTOR
        _ANALYSIS_EXECUTOR.shutdown(wait=False, cancel_futures=True)
        _CONTEXT_EXECUTOR.shutdown(wait=False, cancel_futures=True)
    except (ImportError, AttributeError):
        pass
    logger.info("TradingAgents API 關閉")


# 安全預設：非 development 環境一律關閉 Swagger UI，防止 API 結構資訊洩漏
_is_production = os.getenv("ENVIRONMENT", "").lower() != "development"

app = FastAPI(
    title="TradingAgents",
    description="AI 驅動的美股交易分析系統",
    version=_APP_VERSION,
    lifespan=lifespan,
    docs_url=None if _is_production else "/api/docs",
    openapi_url=None if _is_production else "/openapi.json",
    redoc_url=None,
)


# 速率限制中介層
class RateLimitMiddleware(BaseHTTPMiddleware):
    """簡易 IP 速率限制"""

    # 最大追蹤 IP 數量，防止記憶體耗盡攻擊
    _MAX_TRACKED_IPS = 10_000

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _evict_stale_ips(self, now: float) -> None:
        """移除無活躍記錄的 IP，防止字典無限增長"""
        cutoff = now - self.window
        stale = [ip for ip, ts in self._hits.items() if not ts or ts[-1] <= cutoff]
        for ip in stale:
            del self._hits[ip]

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """取得真實客戶端 IP（Cloudflare -> Nginx Ingress -> Uvicorn 架構）

        優先順序：
        1. CF-Connecting-IP — Cloudflare 注入，不可偽造
        2. X-Real-IP — Nginx Ingress 從最後一跳提取
        3. request.client.host — 直連時的 socket 對端 IP
        """
        ip = (
            request.headers.get("cf-connecting-ip")
            or request.headers.get("x-real-ip")
            or (request.client.host if request.client else "unknown")
        )
        # 正規化 IPv4-mapped IPv6（::ffff:1.2.3.4 -> 1.2.3.4）
        if ip.startswith("::ffff:"):
            ip = ip[7:]
        return ip

    async def dispatch(self, request: Request, call_next) -> Response:
        # 只限制 API 路徑
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.monotonic()

        # 當追蹤 IP 數量超過上限時，清理過期條目
        if len(self._hits) > self._MAX_TRACKED_IPS:
            self._evict_stale_ips(now)

        # 以下讀取-檢查-寫入區段全部為同步操作（無 await），
        # 在 asyncio 單線程事件迴圈中不會發生協程切換，因此不需要 Lock
        hits = self._hits[client_ip]
        cutoff = now - self.window
        self._hits[client_ip] = [t for t in hits if t > cutoff]
        hits = self._hits[client_ip]

        if len(hits) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": _mw_t("rate_limit", request)},
                headers={"Retry-After": str(self.window)},
            )

        hits.append(now)
        return await call_next(request)


# 安全 Headers 中介層
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """新增安全相關 HTTP Headers"""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), "
            "accelerometer=(), gyroscope=(), magnetometer=(), usb=(), "
            "bluetooth=(), screen-wake-lock=(), interest-cohort=()"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["X-DNS-Prefetch-Control"] = "on"
        # 快取策略：HTML 頁面與 API 不快取，靜態資源允許帶 query 快取
        path = request.url.path
        if path == "/" or path.endswith(".html") or path.startswith("/api/") or path == "/health":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        # 多語言 API 需要 Vary 確保 CDN 不混用不同語言快取
        if path.startswith("/api/"):
            response.headers["Vary"] = "Accept-Language"
        elif path.startswith("/static/"):
            # 帶版本戳的靜態檔案可長期快取（URL 變化即失效）
            if request.url.query:
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            else:
                response.headers["Cache-Control"] = "public, max-age=86400"
        # HSTS - 強制 HTTPS（部署在 TLS 後時生效）
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        # CSP - 允許自身資源 + 特定 CDN（需與 HTML 中 SRI 配合）
        # 若路由已設定 CSP（如首頁帶 nonce），不覆蓋
        if "content-security-policy" not in response.headers:
            response.headers["Content-Security-Policy"] = _build_csp()
        return response


# 請求大小限制中介層
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """限制請求 body 大小（同時防護 Content-Length 和 chunked transfer encoding）"""

    MAX_BODY_SIZE = 64 * 1024  # 64 KB

    async def dispatch(self, request: Request, call_next) -> Response:
        # 快速路徑：透過 Content-Length header 檢查（涵蓋大多數正常請求）
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.MAX_BODY_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": _mw_t("request_too_large", request)},
                    )
            except (ValueError, TypeError):
                pass
        elif request.method in ("POST", "PUT", "PATCH"):
            # 防護 chunked transfer encoding 繞過：無 Content-Length 時讀取實際 body 驗證大小
            # BaseHTTPMiddleware 已將 body 緩衝至記憶體，此處讀取不會增加額外開銷
            body = await request.body()
            if len(body) > self.MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": _mw_t("request_too_large", request)},
                )
        return await call_next(request)


# 全域例外處理器（防止洩漏內部錯誤細節）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未預期的錯誤: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": _mw_t("server_error", request)},
    )


# 中介層順序：外層先執行
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
# GZip 壓縮：500 bytes 以上自動壓縮，大幅降低傳輸量（CSS/JS 壓縮率 ~60-70%）
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS（拒絕萬用字元以防止設定錯誤）
_cors_env = os.getenv("CORS_ORIGINS", "").strip()
_cors_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] if _cors_env else []
if "*" in _cors_origins:
    logger.warning("CORS_ORIGINS 包含萬用字元 '*'，已忽略以防止安全風險")
    _cors_origins = []
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# 靜態檔案與模板
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# 註冊路由
from app.routers import analysis, config as config_router, trending

app.include_router(analysis.router, prefix="/api")
app.include_router(config_router.router, prefix="/api")
app.include_router(trending.router, prefix="/api")


@app.get("/")
async def index(request: Request):
    """主頁面（含趨勢資料 SSR 預渲染以消除 CLS）"""
    import secrets
    from app.routers.trending import get_cached_overview_json
    # 使用預序列化快取（背景刷新時已完成 JSON 序列化 + XSS 防護跳脫）
    ssr_json = get_cached_overview_json()
    # 產生 CSP nonce 用於內聯腳本（FOUC 防護）
    csp_nonce = secrets.token_urlsafe(24)
    response = templates.TemplateResponse("index.html", {
        "request": request,
        "ssr_trending": ssr_json,
        "csp_nonce": csp_nonce,
        "v": _CACHE_VERSION,
    })
    # 覆蓋中介層的 CSP，加入此請求專屬的 nonce
    response.headers["Content-Security-Policy"] = _build_csp(
        nonce=csp_nonce,
        script_hash="Cz8u6Qpk4sdHHM6HYSSZ61d2aJotmFL2ax7qE4n0xDk=",
    )
    return response


@app.get("/health")
async def health():
    """健康檢查"""
    return {"status": "ok", "version": _APP_VERSION}


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    """robots.txt for SEO"""
    return FileResponse(Path(__file__).parent / "static" / "robots.txt", media_type="text/plain")
