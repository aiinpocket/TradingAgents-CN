"""
熱門特區 API 路由
提供市場概覽、漲跌幅排行、熱門新聞、AI 趨勢分析等資料
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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
_CACHE_TTL_SECONDS = 600  # 10 分鐘快取（市場資料）
_AI_CACHE_TTL_SECONDS = 7200  # 2 小時快取（AI 分析）
_cache: dict = {}
_cache_lock = threading.Lock()

# 主要美股指數
_INDICES = [
    {"symbol": "^GSPC", "name": "S&P 500", "name_en": "S&P 500"},
    {"symbol": "^DJI", "name": "道瓊工業", "name_en": "Dow Jones"},
    {"symbol": "^IXIC", "name": "那斯達克", "name_en": "Nasdaq"},
    {"symbol": "^VIX", "name": "VIX 恐慌指數", "name_en": "VIX"},
]

# S&P 500 板塊 ETF
_SECTORS = [
    {"symbol": "XLK", "name": "科技", "name_en": "Technology"},
    {"symbol": "XLF", "name": "金融", "name_en": "Financials"},
    {"symbol": "XLE", "name": "能源", "name_en": "Energy"},
    {"symbol": "XLV", "name": "醫療保健", "name_en": "Health Care"},
    {"symbol": "XLY", "name": "非必需消費", "name_en": "Cons. Disc."},
    {"symbol": "XLP", "name": "必需消費", "name_en": "Cons. Staples"},
    {"symbol": "XLI", "name": "工業", "name_en": "Industrials"},
    {"symbol": "XLB", "name": "原物料", "name_en": "Materials"},
    {"symbol": "XLU", "name": "公用事業", "name_en": "Utilities"},
    {"symbol": "XLRE", "name": "不動產", "name_en": "Real Estate"},
    {"symbol": "XLC", "name": "通訊服務", "name_en": "Comm. Services"},
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


def _get_cached(key: str, ttl: int = _CACHE_TTL_SECONDS) -> Optional[dict]:
    """取得快取資料（如果未過期）"""
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() - entry["ts"] < ttl:
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


def _fetch_sectors() -> list[dict]:
    """取得 S&P 500 板塊 ETF 表現"""
    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance 未安裝，無法取得板塊資料")
        return []

    results = []
    symbols = [s["symbol"] for s in _SECTORS]

    try:
        tickers = yf.Tickers(" ".join(symbols))
        for sector_info in _SECTORS:
            sym = sector_info["symbol"]
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

                results.append({
                    "symbol": sym,
                    "name": sector_info["name"],
                    "name_en": sector_info["name_en"],
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                })
            except Exception as e:
                logger.debug(f"取得 {sym} 板塊資料失敗: {e}")
                continue
    except Exception as e:
        logger.error(f"批次取得板塊資料失敗: {e}")

    # 按漲跌幅排序（從高到低）
    results.sort(key=lambda x: x["change_pct"], reverse=True)
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
    """取得市場新聞（相容 yfinance >= 1.0 新格式）"""
    try:
        import yfinance as yf
    except ImportError:
        return []

    news_list = []
    try:
        # 從主要指數和熱門股票取得新聞
        for sym in ["^GSPC", "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL"]:
            try:
                ticker = yf.Ticker(sym)
                news = ticker.news or []
                for item in news[:3]:
                    # yfinance >= 1.0 新格式：{id, content: {title, pubDate, provider, canonicalUrl, ...}}
                    content = item.get("content", {}) if isinstance(item, dict) else {}
                    if content:
                        title = content.get("title", "")
                        canonical = content.get("canonicalUrl", {})
                        link = canonical.get("url", "") if isinstance(canonical, dict) else ""
                        provider = content.get("provider", {})
                        publisher = provider.get("displayName", "") if isinstance(provider, dict) else ""
                        pub_date_str = content.get("pubDate", "")
                    else:
                        # 舊版 yfinance 格式回退
                        title = item.get("title", "")
                        link = item.get("link", "")
                        publisher = item.get("publisher", "")
                        pub_date_ts = item.get("providerPublishTime", 0)
                        pub_date_str = datetime.fromtimestamp(pub_date_ts).strftime(
                            "%Y-%m-%d %H:%M"
                        ) if pub_date_ts else ""

                    if title and link:
                        # 統一日期格式
                        date_display = ""
                        if pub_date_str and "T" in str(pub_date_str):
                            try:
                                dt = datetime.fromisoformat(
                                    str(pub_date_str).replace("Z", "+00:00")
                                )
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
                            "related": sym.replace("^", ""),
                        })
            except Exception as e:
                logger.debug(f"取得 {sym} 新聞失敗: {e}")
                continue

    except Exception as e:
        logger.error(f"取得市場新聞失敗: {e}")

    # 過濾付費新聞來源（使用者無法免費閱讀全文）
    _PAID_SOURCES = {
        "the wall street journal", "wsj", "wall street journal",
        "bloomberg", "financial times", "ft", "barron's", "barrons",
        "the economist", "investor's business daily", "ibd",
    }
    free_news = [
        item for item in news_list
        if item.get("source", "").lower() not in _PAID_SOURCES
    ]

    # 去重（依標題）
    seen_titles = set()
    unique_news = []
    for item in free_news:
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
    sectors_task = loop.run_in_executor(None, _fetch_sectors)

    indices = await indices_task
    movers = await movers_task
    news = await news_task
    sectors = await sectors_task

    result = {
        "indices": indices,
        "movers": movers,
        "news": news,
        "sectors": sectors,
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


# =============================================================
# AI 趨勢分析
# =============================================================

# 分析鎖，避免同時發起多次 LLM 呼叫
_ai_analysis_lock = threading.Lock()


def _get_ai_providers() -> list[tuple[str, str]]:
    """取得所有可用的 LLM 提供商清單（依優先順序排列，快速模型優先）"""
    providers = []
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if openai_key:
        providers.append(("openai", "gpt-4o-mini"))
    if anthropic_key:
        providers.append(("anthropic", "claude-haiku-4-5-20251001"))

    return providers


def _build_market_context(overview: dict) -> str:
    """將市場資料整理成 LLM 可讀的上下文"""
    lines = []
    today = datetime.now().strftime("%Y-%m-%d")
    lines.append(f"Date: {today}\n")

    # 指數行情
    indices = overview.get("indices", [])
    if indices:
        lines.append("## Major Indices")
        for idx in indices:
            direction = "UP" if idx.get("change", 0) >= 0 else "DOWN"
            lines.append(
                f"- {idx['name_en']}: {idx['price']:,.2f} "
                f"({direction} {abs(idx.get('change', 0)):.2f}, "
                f"{idx.get('change_pct', 0):+.2f}%)"
            )
        lines.append("")

    # 板塊表現
    sectors = overview.get("sectors", [])
    if sectors:
        lines.append("## S&P 500 Sector Performance")
        for s in sectors:
            direction = "UP" if s.get("change_pct", 0) >= 0 else "DOWN"
            lines.append(
                f"- {s['name_en']} ({s['symbol']}): "
                f"{direction} {abs(s.get('change_pct', 0)):.2f}%"
            )
        lines.append("")

    # 漲跌幅排行
    movers = overview.get("movers", {})
    gainers = movers.get("gainers", [])
    losers = movers.get("losers", [])

    if gainers:
        lines.append("## Top Gainers (by daily change)")
        for s in gainers[:6]:
            lines.append(
                f"- {s['symbol']} ({s['name']}): ${s['price']:.2f}, "
                f"{s.get('change_pct', 0):+.2f}%"
            )
        lines.append("")

    if losers:
        lines.append("## Top Losers (by daily change)")
        for s in losers[:6]:
            lines.append(
                f"- {s['symbol']} ({s['name']}): ${s['price']:.2f}, "
                f"{s.get('change_pct', 0):+.2f}%"
            )
        lines.append("")

    # 新聞標題
    news = overview.get("news", [])
    if news:
        lines.append("## Recent Market Headlines")
        for n in news[:8]:
            source = n.get("source", "")
            date = n.get("date", "")
            lines.append(f"- [{source}] {n['title']} ({date})")
        lines.append("")

    return "\n".join(lines)


_AI_SYSTEM_PROMPT = """You are a professional financial market analyst providing daily market commentary.
Your analysis should be:
- Objective and data-driven, based on the market data provided
- Focused on identifying themes, sector rotations, and macro-economic implications
- Using a DAILY evaluation horizon (not intraday/minute-level, not monthly/yearly)
- Comprehensive but concise

CRITICAL RULES:
- NEVER make specific buy/sell/hold recommendations for individual stocks
- NEVER provide price targets or suggest entry/exit points
- NEVER use language that could be interpreted as investment solicitation
- Always include a disclaimer that this is for informational purposes only
- Focus on explaining WHY the market is moving, not WHAT investors should do

Respond in the language specified by the user."""


def _build_user_prompt(market_context: str, lang: str) -> str:
    """建構使用者提示詞"""
    if lang == "zh-TW":
        return f"""以下是今日美股市場資料：

{market_context}

請用繁體中文撰寫一份今日市場趨勢分析報告，包含以下幾個部分：

1. **今日市場概況** - 整體市場表現摘要、主要指數走勢
2. **熱門主題與板塊分析** - 根據漲跌幅排行，分析哪些板塊/主題受到關注，以及可能的驅動因素
3. **宏觀經濟與國際趨勢** - 可能影響市場的宏觀因素，包括利率政策、通膨數據、地緣政治、國際市場連動等
4. **重要新聞解讀** - 對重要新聞標題進行背景脈絡分析
5. **風險與關注重點** - 未來幾日值得關注的事件或風險因素

注意：不要有任何個股買賣建議或投資誘導，純粹以客觀資訊分析為主。"""
    else:
        return f"""Here is today's US stock market data:

{market_context}

Please write a daily market trend analysis report covering:

1. **Market Overview** - Overall market performance summary, major index movements
2. **Trending Themes & Sector Analysis** - Which sectors/themes are in focus based on movers, and likely drivers
3. **Macro Economics & Global Trends** - Macro factors potentially affecting markets (interest rates, inflation, geopolitics, global market correlations)
4. **Key News Analysis** - Background context for notable news headlines
5. **Risks & Key Events Ahead** - Events or risk factors to watch in the coming days

Note: Do NOT provide any buy/sell recommendations for individual stocks. Keep the analysis purely objective and informational."""


def _generate_ai_analysis(market_context: str, lang: str) -> tuple[str, str, str]:
    """呼叫 LLM 生成市場趨勢分析（支援自動 fallback）。

    回傳 (content, error, actual_provider)。
    如果第一個 provider 失敗，會自動嘗試下一個。
    """
    providers = _get_ai_providers()
    if not providers:
        return "", "no_provider", ""

    from langchain_core.messages import SystemMessage, HumanMessage
    messages = [
        SystemMessage(content=_AI_SYSTEM_PROMPT),
        HumanMessage(content=_build_user_prompt(market_context, lang)),
    ]

    last_error = ""
    for provider, model in providers:
        try:
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model=model, temperature=0.3, max_tokens=2000)
            else:
                from langchain_anthropic import ChatAnthropic
                llm = ChatAnthropic(model=model, temperature=0.3, max_tokens=2000)

            response = llm.invoke(messages)
            logger.info(f"AI 趨勢分析生成成功 (provider={provider}, model={model})")
            return response.content, "", provider

        except Exception as e:
            last_error = str(e)[:200]
            logger.warning(
                f"AI 趨勢分析 {provider}/{model} 失敗，嘗試下一個: {last_error}"
            )
            continue

    logger.error(f"所有 LLM 提供商均失敗，最後錯誤: {last_error}")
    return "", last_error, ""


@router.get("/trending/ai-analysis")
async def get_ai_analysis(lang: str = "zh-TW"):
    """取得 AI 市場趨勢分析（每 2 小時更新一次）"""
    # 驗證語言參數
    if lang not in ("zh-TW", "en"):
        lang = "zh-TW"

    cache_key = f"ai_analysis_{lang}"
    cached = _get_cached(cache_key, ttl=_AI_CACHE_TTL_SECONDS)
    if cached:
        return cached

    # 檢查是否有可用的 LLM
    providers = _get_ai_providers()
    if not providers:
        return {
            "available": False,
            "content": "",
            "updated_at": "",
            "provider": "",
        }

    # 先取得市場資料（可能來自快取）
    overview = _get_cached("overview")
    if not overview:
        import asyncio
        loop = asyncio.get_event_loop()
        indices = await loop.run_in_executor(None, _fetch_indices)
        movers = await loop.run_in_executor(None, _fetch_movers)
        news = await loop.run_in_executor(None, _fetch_market_news)
        overview = {
            "indices": indices,
            "movers": movers,
            "news": news,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        _set_cache("overview", overview)

    market_context = _build_market_context(overview)

    # 使用 run_in_executor 避免阻塞
    import asyncio
    loop = asyncio.get_event_loop()

    # 用鎖避免並發多次 LLM 呼叫
    acquired = _ai_analysis_lock.acquire(blocking=False)
    if not acquired:
        # 另一個請求正在生成中，等待快取
        for _ in range(30):
            await asyncio.sleep(1)
            cached = _get_cached(cache_key, ttl=_AI_CACHE_TTL_SECONDS)
            if cached:
                return cached
        return {
            "available": True,
            "content": "",
            "updated_at": "",
            "provider": providers[0][0] if providers else "",
            "error": "Analysis generation in progress, please retry",
        }

    try:
        content, error, actual_provider = await loop.run_in_executor(
            None, _generate_ai_analysis, market_context, lang
        )

        result = {
            "available": True,
            "content": content,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "provider": actual_provider or providers[0][0],
        }

        if error:
            result["error"] = error

        if content:
            _set_cache(cache_key, result)

        return result
    finally:
        _ai_analysis_lock.release()
