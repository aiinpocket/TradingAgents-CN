"""
TradingAgents FastAPI 應用程式
取代 Streamlit，提供更快速的載入與更現代的介面
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
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
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
)

# CORS - 限制為同源請求，部署時可透過環境變數配置
_cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
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
    return {"status": "ok", "version": "0.2.0"}
