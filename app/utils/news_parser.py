"""
yfinance 新聞解析共用工具
提供統一的新聞項目解析、付費來源過濾與去重功能，
供 trending.py 和 analysis.py 共用，避免重複程式碼。
"""

from datetime import datetime
from typing import Optional

# 付費新聞來源（使用者無法免費閱讀全文）
PAID_NEWS_SOURCES: frozenset[str] = frozenset({
    "the wall street journal", "wsj", "wall street journal",
    "bloomberg", "financial times", "ft", "barron's", "barrons",
    "barrons.com", "the economist", "investor's business daily", "ibd",
})


def parse_news_item(item: dict, symbol: str = "") -> Optional[dict]:
    """統一解析 yfinance 新聞項目（相容新 / 舊格式）

    yfinance >= 1.0 新格式：{id, content: {title, pubDate, provider, canonicalUrl, ...}}
    舊版格式：{title, link, publisher, providerPublishTime, ...}

    Args:
        item: yfinance 原始新聞項目
        symbol: 股票代碼（非空時加入 related 欄位）

    Returns:
        解析後的字典 {title, url, source, date, related?} 或 None（無效項目）
    """
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
        return None

    # 統一日期格式
    date_display = ""
    if pub_date_str and "T" in str(pub_date_str):
        try:
            dt = datetime.fromisoformat(str(pub_date_str).replace("Z", "+00:00"))
            date_display = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            date_display = str(pub_date_str)[:16]
    elif pub_date_str:
        date_display = str(pub_date_str)

    result = {
        "title": title,
        "url": link,
        "source": publisher,
        "date": date_display,
    }
    if symbol:
        result["related"] = symbol.replace("^", "")
    return result


def filter_paid_sources(news_list: list[dict]) -> list[dict]:
    """過濾付費新聞來源（使用者無法免費閱讀全文的來源）"""
    return [
        item for item in news_list
        if item.get("source", "").lower() not in PAID_NEWS_SOURCES
    ]


def deduplicate_news(news_list: list[dict]) -> list[dict]:
    """依標題去重（保留首次出現的項目，忽略空標題）"""
    seen: set[str] = set()
    unique = []
    for item in news_list:
        t = item.get("title", "").strip()
        if t and t not in seen:
            seen.add(t)
            unique.append(item)
    return unique
