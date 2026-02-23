"""
熱門特區 API 路由
提供市場概覽、漲跌幅排行、熱門新聞、AI 趨勢分析等資料
"""

import asyncio
import os
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
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
_CACHE_TTL_SECONDS = 600  # 10 分鐘快取（市場資料）
_AI_CACHE_TTL_SECONDS = 7200  # 2 小時快取（AI 分析）
_BG_REFRESH_INTERVAL = 300  # 背景刷新間隔：5 分鐘
_MAX_CACHE_ENTRIES = 20  # 快取條目上限，防止記憶體膨脹
_cache: dict = {}
_cache_lock = threading.Lock()

# 專用執行緒池（放在模組頂部，確保所有函式可引用）
_TRENDING_EXECUTOR = ThreadPoolExecutor(max_workers=12, thread_name_prefix="trending")

# 公司名稱快取（由 _STOCK_UNIVERSE 限制，約 50 筆；加上 200 上限防護）
_MAX_COMPANY_NAMES = 200
_company_names: dict[str, str] = {}
_company_names_lock = threading.Lock()

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


def get_cached_overview() -> Optional[dict]:
    """取得快取的市場概覽資料（供首頁 SSR 預渲染用）"""
    return _get_cached("overview")


def _set_cache(key: str, data: dict):
    """設定快取（超過上限時清理過期條目）"""
    now = time.time()
    with _cache_lock:
        _cache[key] = {"data": data, "ts": now}
        # 超過條目上限時，清理過期條目
        if len(_cache) > _MAX_CACHE_ENTRIES:
            expired = [
                k for k, v in _cache.items()
                if now - v["ts"] > _AI_CACHE_TTL_SECONDS
            ]
            for k in expired:
                del _cache[k]


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


def _fetch_movers_batch(batch: list[str]) -> list[dict]:
    """取得單批股票的漲跌幅資料（由執行緒池並行呼叫）"""
    import yfinance as yf

    results = []
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

                # 從快取取得公司名稱（避免昂貴的 ticker.info 呼叫）
                with _company_names_lock:
                    cached_name = _company_names.get(sym)

                if cached_name:
                    short_name = cached_name
                else:
                    try:
                        info = ticker.info or {}
                        short_name = info.get("shortName", sym)
                    except Exception:
                        short_name = sym
                    with _company_names_lock:
                        if len(_company_names) < _MAX_COMPANY_NAMES:
                            _company_names[sym] = short_name

                results.append({
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

    return results


def _fetch_movers() -> dict:
    """取得漲跌幅排行（使用臨時執行緒池並行處理批次，避免巢狀提交 _TRENDING_EXECUTOR 的死鎖風險）"""
    try:
        import yfinance as yf  # noqa: F401 確保已安裝
    except ImportError:
        logger.warning("yfinance 未安裝，無法取得股票資料")
        return {"gainers": [], "losers": []}

    stock_data = []
    batch_size = 25

    try:
        batches = [
            _STOCK_UNIVERSE[i:i + batch_size]
            for i in range(0, len(_STOCK_UNIVERSE), batch_size)
        ]
        # 使用臨時小型執行緒池並行處理批次，
        # 不提交到 _TRENDING_EXECUTOR（避免巢狀死鎖）
        from concurrent.futures import ThreadPoolExecutor as _TP, as_completed as _ac
        with _TP(max_workers=len(batches), thread_name_prefix="movers") as pool:
            futures = {pool.submit(_fetch_movers_batch, batch): batch for batch in batches}
            for future in _ac(futures, timeout=15):
                try:
                    batch_results = future.result(timeout=10)
                    stock_data.extend(batch_results)
                except Exception as e:
                    logger.debug(f"批次取得股票資料失敗: {e}")

    except Exception as e:
        logger.error(f"取得漲跌幅資料失敗: {e}")

    sorted_data = sorted(stock_data, key=lambda x: x["change_pct"], reverse=True)

    return {
        "gainers": sorted_data[:8],
        "losers": sorted_data[-8:][::-1],
    }


def _fetch_news_for_symbol(sym: str) -> list[dict]:
    """取得單一股票的新聞（由執行緒池並行呼叫）"""
    import yfinance as yf

    items = []
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

                items.append({
                    "title": title,
                    "url": link,
                    "source": publisher,
                    "date": date_display,
                    "related": sym.replace("^", ""),
                })
    except Exception as e:
        logger.debug(f"取得 {sym} 新聞失敗: {e}")

    return items


# 付費新聞來源（使用者無法免費閱讀全文）
_PAID_SOURCES = frozenset({
    "the wall street journal", "wsj", "wall street journal",
    "bloomberg", "financial times", "ft", "barron's", "barrons",
    "the economist", "investor's business daily", "ibd",
})

# 新聞來源股票清單
_NEWS_SYMBOLS = ["^GSPC", "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL"]


def _fetch_market_news() -> list[dict]:
    """取得市場新聞（臨時執行緒池並行抓取，避免巢狀提交 _TRENDING_EXECUTOR）"""
    try:
        import yfinance as yf  # noqa: F401 確保已安裝
    except ImportError:
        return []

    news_list = []
    try:
        from concurrent.futures import ThreadPoolExecutor as _TP, as_completed as _ac
        with _TP(max_workers=len(_NEWS_SYMBOLS), thread_name_prefix="news") as pool:
            futures = {pool.submit(_fetch_news_for_symbol, sym): sym for sym in _NEWS_SYMBOLS}
            for future in _ac(futures, timeout=15):
                try:
                    items = future.result(timeout=10)
                    news_list.extend(items)
                except Exception as e:
                    sym = futures[future]
                    logger.debug(f"取得 {sym} 新聞失敗: {e}")
    except Exception as e:
        logger.error(f"取得市場新聞失敗: {e}")

    # 過濾付費新聞來源
    free_news = [
        item for item in news_list
        if item.get("source", "").lower() not in _PAID_SOURCES
    ]

    # 去重（依標題）
    seen_titles: set[str] = set()
    unique_news = []
    for item in free_news:
        if item["title"] not in seen_titles:
            seen_titles.add(item["title"])
            unique_news.append(item)

    return unique_news[:12]


def _translate_news_titles(news_items: list[dict]) -> list[dict]:
    """批次翻譯新聞標題為繁體中文（使用 LLM，失敗時保留原文）"""
    if not news_items:
        return news_items

    titles = [item["title"] for item in news_items]
    providers = _get_ai_providers()
    if not providers:
        return news_items

    import json as _json
    from langchain_core.messages import SystemMessage, HumanMessage

    system_msg = (
        "You are a professional financial news translator for Taiwanese readers. "
        "Translate the following English news headlines into Traditional Chinese (繁體中文). "
        "IMPORTANT: Use Taiwanese terminology, NOT mainland Chinese terminology. "
        "Examples: Trump=川普 (NOT 特朗普), Nvidia=輝達 (NOT 英偉達), "
        "Samsung=三星, Apple=蘋果, Google=Google, Amazon=Amazon. "
        "Keep stock tickers (like AAPL, NVDA) in English. "
        "Respond ONLY with a JSON array of translated strings, in the same order as input. "
        "Example: [\"翻譯一\", \"翻譯二\"]"
    )
    user_msg = _json.dumps(titles, ensure_ascii=False)

    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=user_msg),
    ]

    for provider, model in providers:
        try:
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model=model, temperature=0, max_tokens=2000)
            else:
                from langchain_anthropic import ChatAnthropic
                llm = ChatAnthropic(model=model, temperature=0, max_tokens=2000)

            response = llm.invoke(messages)
            text = response.content.strip()

            # 解析 JSON（支援 markdown code fence 變體）
            import re
            fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
            if fence_match:
                text = fence_match.group(1).strip()

            translated = _json.loads(text)
            if isinstance(translated, list) and len(translated) == len(news_items):
                for i, item in enumerate(news_items):
                    item["title_zh"] = translated[i]
                logger.info(f"新聞標題翻譯完成 ({len(translated)} 則，provider={provider})")
                return news_items

            logger.warning(f"新聞翻譯結果長度不符: {len(translated)} vs {len(news_items)}")
        except Exception as e:
            logger.warning(f"新聞標題翻譯失敗 ({provider}): {str(e)[:100]}")
            continue

    return news_items


@router.get("/trending/overview")
async def get_market_overview():
    """取得市場概覽（主要指數 + 漲跌幅排行 + 新聞）"""
    cached = _get_cached("overview")
    if cached:
        return cached

    loop = asyncio.get_running_loop()

    # 並行取得各項資料（使用專用執行緒池 + 超時保護）
    async def _safe_exec(fn, fallback):
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(_TRENDING_EXECUTOR, fn), timeout=15.0
            )
        except (asyncio.TimeoutError, Exception) as exc:
            logger.warning(f"{fn.__name__} 執行逾時或失敗: {exc}")
            return fallback

    indices, movers, news, sectors = await asyncio.gather(
        _safe_exec(_fetch_indices, []),
        _safe_exec(_fetch_movers, {"gainers": [], "losers": []}),
        _safe_exec(_fetch_market_news, []),
        _safe_exec(_fetch_sectors, []),
    )

    # 批次翻譯新聞標題（背景執行，不阻塞回應）
    if news:
        try:
            news = await asyncio.wait_for(
                loop.run_in_executor(_TRENDING_EXECUTOR, _translate_news_titles, news),
                timeout=30.0,
            )
        except (asyncio.TimeoutError, Exception) as exc:
            logger.warning(f"新聞標題翻譯逾時或失敗: {exc}")

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

    loop = asyncio.get_running_loop()
    indices = await loop.run_in_executor(_TRENDING_EXECUTOR, _fetch_indices)
    result = {"indices": indices, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    _set_cache("indices", result)
    return result


# =============================================================
# AI 趨勢分析
# =============================================================

# AI 分析鎖，保證同一時間只有一個 coroutine 呼叫 LLM
_ai_analysis_lock = asyncio.Lock()


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


# ---------------------------------------------------------------------------
# i18n 錯誤訊息
# ---------------------------------------------------------------------------
_TRENDING_MESSAGES: dict[str, dict[str, str]] = {
    "ai_in_progress": {
        "zh-TW": "AI 分析正在生成中，請稍後重試",
        "en": "AI analysis generation in progress, please retry shortly.",
    },
    "ai_timeout": {
        "zh-TW": "AI 分析生成逾時，請稍後重試",
        "en": "AI analysis generation timed out. Please try again later.",
    },
    "no_provider": {
        "zh-TW": "未配置 LLM API 金鑰",
        "en": "No LLM API key configured.",
    },
}


def _t_trending(key: str, lang: str) -> str:
    """取得 trending 模組 i18n 訊息"""
    msgs = _TRENDING_MESSAGES.get(key, {})
    return msgs.get(lang, msgs.get("zh-TW", key))


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

When writing in Traditional Chinese, use TAIWANESE terminology:
- Trump = 川普 (NOT 特朗普), Nvidia = 輝達 (NOT 英偉達)
- Use 標普500 or S&P 500 (NOT 標準普爾500)
- Use 聯準會 (NOT 聯邦儲備/美聯儲), 那斯達克 (NOT 納斯達克)

Respond in the language specified by the user."""


def _build_user_prompt(market_context: str, lang: str) -> str:
    """建構使用者提示詞"""
    if lang == "zh-TW":
        return f"""以下是今日美股市場資料：

{market_context}

請用繁體中文（台灣用語）撰寫一份今日市場趨勢分析報告，包含以下幾個部分：

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
    """取得 AI 市場趨勢分析（每 2 小時更新一次）

    使用 asyncio.Lock 保證同一時間只有一個 coroutine 執行 LLM 呼叫，
    後續請求會在鎖內做 double-check 快取，避免重複生成。
    """
    if lang not in ("zh-TW", "en"):
        lang = "zh-TW"

    cache_key = f"ai_analysis_{lang}"
    cached = _get_cached(cache_key, ttl=_AI_CACHE_TTL_SECONDS)
    if cached:
        return cached

    providers = _get_ai_providers()
    if not providers:
        return {"available": False, "content": "", "updated_at": "", "provider": ""}

    # 嘗試取得鎖；等待最多 120 秒（涵蓋一次完整 LLM 呼叫）
    try:
        acquired = await asyncio.wait_for(_ai_analysis_lock.acquire(), timeout=120.0)
    except asyncio.TimeoutError:
        return {
            "available": True,
            "content": "",
            "updated_at": "",
            "provider": providers[0][0],
            "error": _t_trending("ai_in_progress", lang),
        }

    try:
        # double-check: 前一個請求可能已填入快取
        cached = _get_cached(cache_key, ttl=_AI_CACHE_TTL_SECONDS)
        if cached:
            return cached

        # 取得市場資料（帶容錯的並行抓取）
        overview = _get_cached("overview")
        if not overview:
            loop = asyncio.get_running_loop()

            async def _safe_fetch(fn, fallback):
                try:
                    return await asyncio.wait_for(
                        loop.run_in_executor(_TRENDING_EXECUTOR, fn), timeout=15.0
                    )
                except (asyncio.TimeoutError, Exception) as exc:
                    logger.warning(f"AI 分析取得市場資料失敗 ({fn.__name__}): {exc}")
                    return fallback

            indices, movers, news, sectors = await asyncio.gather(
                _safe_fetch(_fetch_indices, []),
                _safe_fetch(_fetch_movers, {"gainers": [], "losers": []}),
                _safe_fetch(_fetch_market_news, []),
                _safe_fetch(_fetch_sectors, []),
            )
            overview = {
                "indices": indices,
                "movers": movers,
                "news": news,
                "sectors": sectors,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            _set_cache("overview", overview)

        market_context = _build_market_context(overview)
        loop = asyncio.get_running_loop()

        content, error, actual_provider = await asyncio.wait_for(
            loop.run_in_executor(
                _TRENDING_EXECUTOR, _generate_ai_analysis, market_context, lang
            ),
            timeout=120.0,
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

    except asyncio.TimeoutError:
        logger.error("AI 分析生成逾時（120 秒）")
        return {
            "available": True,
            "content": "",
            "updated_at": "",
            "provider": providers[0][0],
            "error": _t_trending("ai_timeout", lang),
        }
    finally:
        _ai_analysis_lock.release()


# =============================================================
# 背景定時刷新
# =============================================================

async def _pregenerate_ai_analysis():
    """預先產生中英文 AI 趨勢分析（背景呼叫）"""
    overview = _get_cached("overview")
    if not overview:
        return

    providers = _get_ai_providers()
    if not providers:
        return

    market_context = _build_market_context(overview)
    loop = asyncio.get_running_loop()

    for lang in ("zh-TW", "en"):
        cache_key = f"ai_analysis_{lang}"
        # 已有快取且未過期，跳過
        if _get_cached(cache_key, ttl=_AI_CACHE_TTL_SECONDS):
            continue

        try:
            content, error, actual_provider = await asyncio.wait_for(
                loop.run_in_executor(
                    _TRENDING_EXECUTOR, _generate_ai_analysis, market_context, lang
                ),
                timeout=120.0,
            )
            if content:
                result = {
                    "available": True,
                    "content": content,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "provider": actual_provider or providers[0][0],
                }
                _set_cache(cache_key, result)
                logger.info(f"AI 趨勢分析預產生完成 (lang={lang})")
            elif error:
                logger.warning(f"AI 趨勢分析預產生失敗 (lang={lang}): {error}")
        except asyncio.TimeoutError:
            logger.warning(f"AI 趨勢分析預產生逾時 (lang={lang})")
        except Exception as e:
            logger.warning(f"AI 趨勢分析預產生錯誤 (lang={lang}): {e}")


async def start_background_refresh():
    """啟動背景定時刷新趨勢資料。

    每 5 分鐘（_BG_REFRESH_INTERVAL）+ 隨機 jitter 重新抓取市場概覽，
    確保快取始終有熱資料，使用者不需等待冷啟動。
    每次刷新後，若 AI 分析快取已過期，自動預產生中英文版本。
    應在 FastAPI lifespan 中呼叫。
    """
    logger.info(f"背景趨勢刷新已啟動（基礎間隔 {_BG_REFRESH_INTERVAL} 秒）")
    consecutive_failures = 0
    while True:
        # exponential backoff：連續失敗時逐步拉長間隔（上限 30 分鐘）
        backoff = min(_BG_REFRESH_INTERVAL * (2 ** consecutive_failures), 1800)
        jitter = random.uniform(0, 30)
        await asyncio.sleep(backoff + jitter)
        try:
            with _cache_lock:
                _cache.pop("overview", None)
            await asyncio.wait_for(get_market_overview(), timeout=60.0)
            logger.info("背景趨勢刷新完成")
            consecutive_failures = 0

            # 市場資料更新後，背景預產生 AI 分析（不阻塞下次刷新）
            try:
                await _pregenerate_ai_analysis()
            except Exception as e:
                logger.warning(f"AI 分析預產生失敗（不影響正常運作）: {e}")

        except asyncio.TimeoutError:
            consecutive_failures += 1
            logger.warning(
                f"背景趨勢刷新逾時 60 秒"
                f"（連續第 {consecutive_failures} 次，下次間隔 {backoff:.0f}s）"
            )
        except Exception as e:
            consecutive_failures += 1
            logger.warning(
                f"背景趨勢刷新失敗"
                f"（連續第 {consecutive_failures} 次，下次間隔 {backoff:.0f}s）: {e}"
            )
