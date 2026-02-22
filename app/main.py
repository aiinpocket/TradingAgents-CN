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
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from dotenv import load_dotenv

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    logger.info("TradingAgents API 啟動中...")
    yield
    logger.info("TradingAgents API 關閉")


app = FastAPI(
    title="TradingAgents",
    description="AI 驅動的美股交易分析系統",
    version="0.2.3",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
)


# 速率限制中介層
class RateLimitMiddleware(BaseHTTPMiddleware):
    """簡易 IP 速率限制"""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        # 只限制 API 路徑
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits[client_ip]

        # 清除過期紀錄
        cutoff = now - self.window
        self._hits[client_ip] = [t for t in hits if t > cutoff]
        hits = self._hits[client_ip]

        if len(hits) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "請求過於頻繁，請稍後再試"},
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
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        # HSTS - 強制 HTTPS（部署在 TLS 後時生效）
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        # CSP - 允許自身資源 + 特定 CDN（需與 HTML 中 SRI 配合）
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        return response


# 請求大小限制中介層
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """限制請求 body 大小"""

    MAX_BODY_SIZE = 64 * 1024  # 64 KB

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.MAX_BODY_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "請求內容過大"},
                    )
            except (ValueError, TypeError):
                pass
        return await call_next(request)


# 全域例外處理器（防止洩漏內部錯誤細節）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未預期的錯誤: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "伺服器內部錯誤，請查看日誌"},
    )


# 中介層順序：外層先執行
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

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
from app.routers import analysis, config as config_router

app.include_router(analysis.router, prefix="/api")
app.include_router(config_router.router, prefix="/api")


@app.get("/")
async def index(request: Request):
    """主頁面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """健康檢查"""
    return {"status": "ok", "version": "0.2.3"}


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    """robots.txt for SEO"""
    return FileResponse(Path(__file__).parent / "static" / "robots.txt", media_type="text/plain")
