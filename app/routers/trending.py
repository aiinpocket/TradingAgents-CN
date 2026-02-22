"""
熱門特區 API 路由
提供市場概覽、漲跌幅排行、熱門新聞等資料
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter

# 日誌
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger("trending")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("trending")

router = APIRouter(tags=["trending"])

# 快取設定
_CACHE_TTL_SECONDS = 600  # 10 分鐘快取
_cache: dict = {}
_cache_lock = threading.Lock()

# 主要美股指數
_INDICES = [
    {"symbol": "^GSPC", "name": "S&P 500", "name_en": "S&P 500"},
    {"symbol": "^DJI", "name": "道瓊工業", "name_en": "Dow Jones"},
    {"symbol": "^IXIC", "name": "那斯達克", "name_en": "Nasdaq"},
    {"symbol": "^VIX", "name": "VIX 恐慌指數", "name_en": "VIX"},
]

# 追蹤的熱門股票池（用於計算漲跌幅排行）
_STOCK_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "UNH", "JNJ", "WMT", "PG", "MA", "HD", "DIS", "BAC",
    "XOM", "CVX", "PFE", "ABBV", "KO", "PEP", "MRK", "AVGO",
    "COST", "CSCO", "ACN", "ABT", "MCD", "NKE", "ORCL", "AMD", "INTC",
    "CRM", "ADBE", "NFLX", "QCOM", "TXN", "AMAT", "PYPL", "UBER",
    "COIN", "PLTR", "ARM", "SMCI", "MSTR", "SNOW",
]


def _get_cached(key: str) -> Optional[dict]:
    """取得快取資料（如果未過期）"""
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() - entry["ts"] < _CACHE_TTL_SECONDS:
            return entry["data"]
    return None


def _set_cache(key: str, data: dict):
    """設定快取"""
    with _cache_lock:
        _cache[key] = {"data": data, "ts": time.time()}


def _fetch_indices() -> list[dict]:
    """取得主要指數行情"""
    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance 未安裝，無法取得指數資料")
        return []

    results = []
    symbols = [idx["symbol"] for idx in _INDICES]

    try:
        tickers = yf.Tickers(" ".join(symbols))
        for idx_info in _INDICES:
            sym = idx_info["symbol"]
            try:
                ticker = tickers.tickers.get(sym)
                if not ticker:
                    continue
                hist = ticker.history(period="2d")
                if hist.empty or len(hist) < 1:
                    continue

                current_price = float(hist["Close"].iloc[-1])
                if len(hist) >= 2:
                    prev_price = float(hist["Close"].iloc[-2])
                    change = current_price - prev_price
                    change_pct = (change / prev_price) * 100 if prev_price else 0
                else:
                    change = 0
                    change_pct = 0

                results.append({
                    "symbol": sym,
                    "name": idx_info["name"],
                    "name_en": idx_info["name_en"],
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                })
            except Exception as e:
                logger.debug(f"取得 {sym} 指數資料失敗: {e}")
                continue
    except Exception as e:
        logger.error(f"批次取得指數資料失敗: {e}")

    return results


def _fetch_movers() -> dict:
    """取得漲跌幅排行"""
    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance 未安裝，無法取得股票資料")
        return {"gainers": [], "losers": []}

    stock_data = []

    try:
        # 分批取得，避免一次請求太多
        batch_size = 25
        for i in range(0, len(_STOCK_UNIVERSE), batch_size):
            batch = _STOCK_UNIVERSE[i:i + batch_size]
            try:
                tickers = yf.Tickers(" ".join(batch))
                for sym in batch:
                    try:
                        ticker = tickers.tickers.get(sym)
                        if not ticker:
                            continue
                        hist = ticker.history(period="2d")
                        if hist.empty or len(hist) < 2:
                            continue

                        current_price = float(hist["Close"].iloc[-1])
                        prev_price = float(hist["Close"].iloc[-2])
                        change = current_price - prev_price
                        change_pct = (change / prev_price) * 100 if prev_price else 0

                        # 取得公司名稱
                        info = ticker.info or {}
                        short_name = info.get("shortName", sym)

                        stock_data.append({
                            "symbol": sym,
                            "name": short_name,
                            "price": round(current_price, 2),
                            "change": round(change, 2),
                            "change_pct": round(change_pct, 2),
                        })
                    except Exception as e:
                        logger.debug(f"取得 {sym} 資料失敗: {e}")
                        continue
            except Exception as e:
                logger.debug(f"批次取得股票資料失敗: {e}")
                continue

    except Exception as e:
        logger.error(f"取得漲跌幅資料失敗: {e}")

    # 按漲跌幅排序
    sorted_data = sorted(stock_data, key=lambda x: x["change_pct"], reverse=True)

    return {
        "gainers": sorted_data[:8],
        "losers": sorted_data[-8:][::-1],  # 跌幅最大的反轉排列
    }


def _fetch_market_news() -> list[dict]:
    """取得市場新聞"""
    try:
        import yfinance as yf
    except ImportError:
        return []

    news_list = []
    try:
        # 從主要指數和熱門股票取得新聞
        for sym in ["^GSPC", "AAPL", "NVDA", "TSLA"]:
            try:
                ticker = yf.Ticker(sym)
                news = ticker.news or []
                for item in news[:3]:
                    # yfinance 新聞格式
                    title = item.get("title", "")
                    link = item.get("link", "")
                    publisher = item.get("publisher", "")
                    pub_date = item.get("providerPublishTime", 0)

                    if title and link:
                        news_list.append({
                            "title": title,
                            "url": link,
                            "source": publisher,
                            "date": datetime.fromtimestamp(pub_date).strftime(
                                "%Y-%m-%d %H:%M"
                            ) if pub_date else "",
                            "related": sym.replace("^", ""),
                        })
            except Exception as e:
                logger.debug(f"取得 {sym} 新聞失敗: {e}")
                continue

    except Exception as e:
        logger.error(f"取得市場新聞失敗: {e}")

    # 去重（依標題）
    seen_titles = set()
    unique_news = []
    for item in news_list:
        if item["title"] not in seen_titles:
            seen_titles.add(item["title"])
            unique_news.append(item)

    return unique_news[:12]


@router.get("/trending/overview")
async def get_market_overview():
    """取得市場概覽（主要指數 + 漲跌幅排行 + 新聞）"""
    cached = _get_cached("overview")
    if cached:
        return cached

    import asyncio
    loop = asyncio.get_event_loop()

    # 並行取得各項資料
    indices_task = loop.run_in_executor(None, _fetch_indices)
    movers_task = loop.run_in_executor(None, _fetch_movers)
    news_task = loop.run_in_executor(None, _fetch_market_news)

    indices = await indices_task
    movers = await movers_task
    news = await news_task

    result = {
        "indices": indices,
        "movers": movers,
        "news": news,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    _set_cache("overview", result)
    return result


@router.get("/trending/indices")
async def get_indices():
    """取得主要指數行情"""
    cached = _get_cached("indices")
    if cached:
        return cached

    import asyncio
    loop = asyncio.get_event_loop()
    indices = await loop.run_in_executor(None, _fetch_indices)
    result = {"indices": indices, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    _set_cache("indices", result)
    return result
