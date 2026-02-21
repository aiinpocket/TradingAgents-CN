#!/usr/bin/env python3
"""
熱門特區模組

找出近一週熱門話題相關的股票，並使用多維度資料分析呈現市場趨勢。
包含宏觀經濟指標、產業板塊熱力圖、個股趨勢卡片等功能。
分析週期以「日」為單位，聚焦短中期市場動態。

注意：本模組所有內容僅供資訊參考，不構成任何投資建議。
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 導入UI工具函數
sys.path.append(str(Path(__file__).parent.parent))
from utils.ui_utils import apply_hide_deploy_button_css

# 導入日誌模組
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger('hot_topics')
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('hot_topics')

# 嘗試導入yfinance
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    logger.warning("yfinance 未安裝，熱門特區功能將受限")


# ---------------------------------------------------------------------------
# 常數定義
# ---------------------------------------------------------------------------

# 免責聲明文字
DISCLAIMER_TEXT = (
    "免責聲明：本頁面所有內容僅供資訊參考與教育目的，不構成任何形式的投資建議、"
    "推薦或誘導。所有分析基於公開市場資料，過去的表現不代表未來的結果。投資涉及風險，"
    "請在做出任何投資決定前諮詢專業的財務顧問。本平台不對因使用本頁面資訊而產生的任何損失承擔責任。"
)

# 主要指數清單（代號: 顯示名稱）
MAJOR_INDICES = {
    "^GSPC": "S&P 500",
    "^DJI": "道瓊工業",
    "^IXIC": "那斯達克",
    "^VIX": "VIX 恐慌指數",
}

# 國際指數
INTERNATIONAL_INDICES = {
    "^FTSE": "英國富時100",
    "^N225": "日經225",
    "^HSI": "恆生指數",
    "^GDAXI": "德國DAX",
}

# 其他重要指標
OTHER_INDICATORS = {
    "^TNX": "美國10年期公債殖利率",
    "GC=F": "黃金",
    "CL=F": "原油 (WTI)",
    "BTC-USD": "比特幣",
    "DX-Y.NYB": "美元指數",
}

# 產業板塊ETF（代號: 顯示名稱）
SECTOR_ETFS = {
    "XLK": "科技",
    "XLF": "金融",
    "XLE": "能源",
    "XLV": "醫療保健",
    "XLC": "通訊服務",
    "XLI": "工業",
    "XLP": "必需消費品",
    "XLU": "公用事業",
    "XLRE": "房地產",
    "XLB": "原物料",
    "XLY": "非必需消費品",
}

# 追蹤的熱門股票池（按類別分組）
WATCHLIST = {
    "科技巨頭": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
    "半導體": ["TSM", "AMD", "INTC", "AVGO", "QCOM", "MU"],
    "AI 與雲端": ["PLTR", "SNOW", "CRM", "NOW", "AI", "SMCI"],
    "金融": ["JPM", "BAC", "GS", "V", "MA"],
    "能源": ["XOM", "CVX", "COP", "SLB"],
    "醫療": ["UNH", "JNJ", "PFE", "ABBV", "LLY"],
    "消費": ["WMT", "COST", "NKE", "SBUX", "MCD"],
}


# ---------------------------------------------------------------------------
# 資料擷取函數（帶快取）
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ticker_data(symbol: str, period: str = "5d") -> Optional[pd.DataFrame]:
    """擷取單一股票的歷史資料

    使用 yfinance 下載指定股票在給定期間內的日K資料。
    快取有效期為 1 小時，避免重複呼叫 API。

    Args:
        symbol: 股票代碼（例如 AAPL, ^GSPC）
        period: 資料期間（例如 5d, 1mo）

    Returns:
        包含 OHLCV 資料的 DataFrame，若擷取失敗則回傳 None
    """
    if not YF_AVAILABLE:
        return None
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df is not None and not df.empty:
            return df
    except Exception as e:
        logger.warning(f"擷取 {symbol} 資料失敗: {e}")
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ticker_info(symbol: str) -> Dict[str, Any]:
    """擷取股票基本資訊

    包含公司名稱、產業、市值等資訊。
    快取有效期為 1 小時。

    Args:
        symbol: 股票代碼

    Returns:
        包含股票基本資訊的字典
    """
    if not YF_AVAILABLE:
        return {}
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if info else {}
    except Exception as e:
        logger.warning(f"擷取 {symbol} 資訊失敗: {e}")
        return {}


@st.cache_data(ttl=3600, show_spinner=False)
def get_macro_indicators() -> Dict[str, Dict[str, Any]]:
    """取得宏觀經濟指標

    彙整美股主要指數、國際指數、債券殖利率、商品價格、加密貨幣
    以及美元指數等關鍵宏觀指標的最新數據與近一週變化。

    Returns:
        巢狀字典，第一層為類別名稱，第二層為各指標的數據
    """
    results = {}

    all_indicators = {
        "美股主要指數": MAJOR_INDICES,
        "國際指數": INTERNATIONAL_INDICES,
        "其他指標": OTHER_INDICATORS,
    }

    for category, indicators in all_indicators.items():
        category_data = {}
        for symbol, name in indicators.items():
            df = fetch_ticker_data(symbol, "5d")
            if df is not None and len(df) >= 1:
                latest_close = df["Close"].iloc[-1]
                # 計算日漲跌幅
                if len(df) >= 2:
                    prev_close = df["Close"].iloc[-2]
                    daily_change_pct = ((latest_close - prev_close) / prev_close) * 100
                else:
                    daily_change_pct = 0.0

                # 計算週漲跌幅
                first_close = df["Close"].iloc[0]
                weekly_change_pct = ((latest_close - first_close) / first_close) * 100

                category_data[symbol] = {
                    "name": name,
                    "price": latest_close,
                    "daily_change_pct": daily_change_pct,
                    "weekly_change_pct": weekly_change_pct,
                }
        results[category] = category_data

    return results


@st.cache_data(ttl=3600, show_spinner=False)
def get_sector_trends() -> List[Dict[str, Any]]:
    """取得產業板塊趨勢

    分析各主要板塊 ETF 的近一週表現，包含漲跌幅和成交量變化。

    Returns:
        各板塊趨勢資料的列表，依週漲跌幅排序
    """
    sector_data = []

    for symbol, name in SECTOR_ETFS.items():
        df = fetch_ticker_data(symbol, "1mo")
        if df is not None and len(df) >= 2:
            latest_close = df["Close"].iloc[-1]
            # 取最近5個交易日的資料計算週表現
            recent_df = df.tail(6)  # 多取一筆作為基準
            if len(recent_df) >= 2:
                week_open = recent_df["Close"].iloc[0]
                weekly_change_pct = ((latest_close - week_open) / week_open) * 100
            else:
                weekly_change_pct = 0.0

            # 日漲跌幅
            if len(df) >= 2:
                prev_close = df["Close"].iloc[-2]
                daily_change_pct = ((latest_close - prev_close) / prev_close) * 100
            else:
                daily_change_pct = 0.0

            # 成交量與平均成交量比較
            avg_volume = df["Volume"].tail(20).mean() if len(df) >= 20 else df["Volume"].mean()
            latest_volume = df["Volume"].iloc[-1]
            volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1.0

            sector_data.append({
                "symbol": symbol,
                "name": name,
                "price": latest_close,
                "daily_change_pct": daily_change_pct,
                "weekly_change_pct": weekly_change_pct,
                "volume_ratio": volume_ratio,
                "latest_volume": latest_volume,
            })

    # 依週漲跌幅排序（由高到低）
    sector_data.sort(key=lambda x: x["weekly_change_pct"], reverse=True)
    return sector_data


@st.cache_data(ttl=3600, show_spinner=False)
def get_trending_stocks() -> List[Dict[str, Any]]:
    """取得近一週熱門股票

    從預設的股票觀察清單中，篩選出近一週表現突出的股票。
    篩選條件包含：週漲跌幅絕對值較大、成交量異常放大等。

    Returns:
        熱門股票資料列表，依週漲跌幅絕對值排序
    """
    all_stocks = []

    for category, symbols in WATCHLIST.items():
        for symbol in symbols:
            df = fetch_ticker_data(symbol, "1mo")
            if df is None or len(df) < 5:
                continue

            latest_close = df["Close"].iloc[-1]

            # 週漲跌幅（取最近5個交易日）
            recent_df = df.tail(6)
            if len(recent_df) >= 2:
                week_open = recent_df["Close"].iloc[0]
                weekly_change_pct = ((latest_close - week_open) / week_open) * 100
            else:
                weekly_change_pct = 0.0

            # 日漲跌幅
            if len(df) >= 2:
                prev_close = df["Close"].iloc[-2]
                daily_change_pct = ((latest_close - prev_close) / prev_close) * 100
            else:
                daily_change_pct = 0.0

            # 成交量分析
            avg_volume = df["Volume"].tail(20).mean() if len(df) >= 20 else df["Volume"].mean()
            latest_volume = df["Volume"].iloc[-1]
            volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1.0

            # 月漲跌幅
            month_open = df["Close"].iloc[0]
            monthly_change_pct = ((latest_close - month_open) / month_open) * 100

            all_stocks.append({
                "symbol": symbol,
                "category": category,
                "price": latest_close,
                "daily_change_pct": daily_change_pct,
                "weekly_change_pct": weekly_change_pct,
                "monthly_change_pct": monthly_change_pct,
                "volume_ratio": volume_ratio,
                "latest_volume": latest_volume,
                "avg_volume": avg_volume,
            })

    # 依週漲跌幅絕對值排序，取前20名
    all_stocks.sort(key=lambda x: abs(x["weekly_change_pct"]), reverse=True)
    return all_stocks[:20]


# ---------------------------------------------------------------------------
# UI 渲染函數
# ---------------------------------------------------------------------------

def render_disclaimer():
    """渲染免責聲明

    使用醒目的紅色區塊顯示免責聲明，確保使用者在瀏覽前先閱讀。
    """
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
            border: 2px solid #fc8181;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            line-height: 1.6;
            color: #742a2a;
        ">
            <strong style="font-size: 1rem;">!! 重要聲明</strong><br/>
            {DISCLAIMER_TEXT}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_change(value: float, suffix: str = "%") -> str:
    """格式化漲跌幅數值為帶正負號的字串

    Args:
        value: 漲跌幅數值
        suffix: 後綴字元

    Returns:
        格式化後的字串，例如 "+2.35%" 或 "-1.20%"
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}{suffix}"


def _change_color(value: float) -> str:
    """根據漲跌幅回傳對應的顏色代碼

    Args:
        value: 漲跌幅數值

    Returns:
        CSS 顏色字串
    """
    if value > 0:
        return "#16a34a"  # 綠色（上漲）
    elif value < 0:
        return "#dc2626"  # 紅色（下跌）
    else:
        return "#6b7280"  # 灰色（持平）


def render_macro_overview(macro_data: Dict[str, Dict[str, Any]]):
    """渲染宏觀經濟概覽

    以分類方式呈現各項宏觀經濟指標的即時數據，
    使用顏色標記漲跌方向，方便快速掃描市場全貌。

    Args:
        macro_data: 由 get_macro_indicators() 回傳的宏觀指標資料
    """
    st.markdown("### 宏觀經濟概覽")
    st.caption("資料來源：Yahoo Finance | 以下數據僅供參考，不構成投資建議")

    for category, indicators in macro_data.items():
        if not indicators:
            continue

        st.markdown(f"**{category}**")
        cols = st.columns(len(indicators))
        for i, (symbol, data) in enumerate(indicators.items()):
            with cols[i]:
                price = data["price"]
                daily_pct = data["daily_change_pct"]
                weekly_pct = data["weekly_change_pct"]

                # 根據指標類型決定價格格式
                if symbol == "^VIX":
                    price_str = f"{price:.2f}"
                elif symbol == "^TNX":
                    price_str = f"{price:.3f}%"
                elif price >= 1000:
                    price_str = f"{price:,.2f}"
                else:
                    price_str = f"{price:.2f}"

                st.metric(
                    label=data["name"],
                    value=price_str,
                    delta=f"{_format_change(daily_pct)} (日) | {_format_change(weekly_pct)} (週)",
                )
        st.markdown("")  # 增加間距


def render_sector_heatmap(sector_data: List[Dict[str, Any]]):
    """渲染產業板塊熱力圖

    使用 Plotly 繪製產業板塊的週漲跌幅熱力圖，
    以顏色深淺表示漲跌程度，面積固定相同大小。

    Args:
        sector_data: 由 get_sector_trends() 回傳的板塊趨勢資料
    """
    st.markdown("### 產業板塊一週表現")
    st.caption("以下板塊數據基於各產業 ETF 近一週表現，僅供參考")

    if not sector_data:
        st.info("暫無板塊資料")
        return

    # 使用 Plotly Treemap 繪製熱力圖
    labels = []
    values = []
    colors = []
    hover_texts = []

    for s in sector_data:
        change = s["weekly_change_pct"]
        labels.append(f"{s['name']}<br>{_format_change(change)}")
        values.append(1)  # 等面積
        colors.append(change)
        hover_text = (
            f"<b>{s['name']} ({s['symbol']})</b><br>"
            f"價格: ${s['price']:.2f}<br>"
            f"日漲跌: {_format_change(s['daily_change_pct'])}<br>"
            f"週漲跌: {_format_change(change)}<br>"
            f"成交量比: {s['volume_ratio']:.1f}x"
        )
        hover_texts.append(hover_text)

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=[""] * len(labels),
        values=values,
        marker=dict(
            colors=colors,
            colorscale=[
                [0, "#dc2626"],
                [0.35, "#fca5a5"],
                [0.5, "#f3f4f6"],
                [0.65, "#86efac"],
                [1, "#16a34a"],
            ],
            cmid=0,
            showscale=True,
            colorbar=dict(
                title="週漲跌 %",
                thickness=15,
                len=0.6,
            ),
        ),
        hovertext=hover_texts,
        hoverinfo="text",
        textfont=dict(size=14),
    ))

    fig.update_layout(
        height=400,
        margin=dict(t=10, l=10, r=10, b=10),
    )

    st.plotly_chart(fig, use_container_width=True)

    # 額外用表格呈現詳細資料
    with st.expander("查看板塊詳細數據"):
        df = pd.DataFrame(sector_data)
        df = df.rename(columns={
            "symbol": "代碼",
            "name": "板塊名稱",
            "price": "最新價格",
            "daily_change_pct": "日漲跌(%)",
            "weekly_change_pct": "週漲跌(%)",
            "volume_ratio": "成交量倍數",
        })
        df = df[["代碼", "板塊名稱", "最新價格", "日漲跌(%)", "週漲跌(%)", "成交量倍數"]]
        df["最新價格"] = df["最新價格"].apply(lambda x: f"${x:.2f}")
        df["日漲跌(%)"] = df["日漲跌(%)"].apply(lambda x: f"{x:+.2f}%")
        df["週漲跌(%)"] = df["週漲跌(%)"].apply(lambda x: f"{x:+.2f}%")
        df["成交量倍數"] = df["成交量倍數"].apply(lambda x: f"{x:.1f}x")
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_stock_card(stock: Dict[str, Any], col):
    """渲染單一股票的資訊卡片

    在指定的 Streamlit 欄位中顯示一張股票資訊卡片，
    包含價格、日/週漲跌幅、成交量比率等關鍵數據。

    Args:
        stock: 單一股票資料字典
        col: Streamlit 欄位物件
    """
    with col:
        symbol = stock["symbol"]
        price = stock["price"]
        daily_pct = stock["daily_change_pct"]
        weekly_pct = stock["weekly_change_pct"]
        vol_ratio = stock["volume_ratio"]
        category = stock.get("category", "")

        # 決定卡片邊框顏色
        if weekly_pct > 0:
            border_color = "#16a34a"
            bg_gradient = "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)"
        elif weekly_pct < 0:
            border_color = "#dc2626"
            bg_gradient = "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
        else:
            border_color = "#9ca3af"
            bg_gradient = "linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)"

        # 成交量標籤
        vol_label = ""
        if vol_ratio >= 2.0:
            vol_label = '<span style="color:#b45309;font-weight:600;"> | 量能爆發</span>'
        elif vol_ratio >= 1.5:
            vol_label = '<span style="color:#d97706;font-weight:600;"> | 量能放大</span>'

        st.markdown(
            f"""
            <div style="
                background: {bg_gradient};
                border-left: 4px solid {border_color};
                border-radius: 12px;
                padding: 1rem 1.2rem;
                margin-bottom: 0.8rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            ">
                <div style="display:flex;justify-content:space-between;align-items:baseline;">
                    <span style="font-size:1.1rem;font-weight:700;">{symbol}</span>
                    <span style="font-size:0.78rem;color:#6b7280;">{category}</span>
                </div>
                <div style="font-size:1.3rem;font-weight:700;margin:0.3rem 0;">
                    ${price:,.2f}
                </div>
                <div style="font-size:0.85rem;margin-bottom:0.2rem;">
                    <span style="color:{_change_color(daily_pct)};font-weight:600;">
                        日 {_format_change(daily_pct)}
                    </span>
                    &nbsp;&nbsp;
                    <span style="color:{_change_color(weekly_pct)};font-weight:600;">
                        週 {_format_change(weekly_pct)}
                    </span>
                </div>
                <div style="font-size:0.78rem;color:#6b7280;">
                    成交量: {vol_ratio:.1f}x 均量{vol_label}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_trending_stocks(stocks: List[Dict[str, Any]]):
    """渲染熱門股票列表

    以卡片網格方式呈現近一週波動最大的股票，
    每行顯示三張卡片。

    Args:
        stocks: 由 get_trending_stocks() 回傳的熱門股票列表
    """
    st.markdown("### 近一週熱門個股")
    st.caption("依週漲跌幅絕對值排序 | 高波動不代表投資機會，僅供觀察參考")

    if not stocks:
        st.info("暫無熱門股票資料")
        return

    # 分為上漲和下跌兩組
    gainers = [s for s in stocks if s["weekly_change_pct"] > 0]
    losers = [s for s in stocks if s["weekly_change_pct"] < 0]

    tab_up, tab_down, tab_all = st.tabs(["週漲幅排行", "週跌幅排行", "全部"])

    with tab_up:
        if gainers:
            gainers_sorted = sorted(gainers, key=lambda x: x["weekly_change_pct"], reverse=True)
            _render_stock_grid(gainers_sorted)
        else:
            st.info("本週暫無明顯上漲的觀察標的")

    with tab_down:
        if losers:
            losers_sorted = sorted(losers, key=lambda x: x["weekly_change_pct"])
            _render_stock_grid(losers_sorted)
        else:
            st.info("本週暫無明顯下跌的觀察標的")

    with tab_all:
        _render_stock_grid(stocks)


def _render_stock_grid(stocks: List[Dict[str, Any]]):
    """以三欄網格渲染股票卡片列表

    Args:
        stocks: 股票資料列表
    """
    for i in range(0, len(stocks), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(stocks):
                render_stock_card(stocks[idx], cols[j])


def render_volume_anomalies(stocks: List[Dict[str, Any]]):
    """渲染成交量異常股票

    篩選出成交量明顯偏離均值的股票，
    成交量異常往往暗示著重要的市場動態。

    Args:
        stocks: 全部股票資料列表
    """
    # 篩選成交量超過 1.5 倍均量的股票
    anomalies = [s for s in stocks if s["volume_ratio"] >= 1.5]
    if not anomalies:
        return

    anomalies.sort(key=lambda x: x["volume_ratio"], reverse=True)

    st.markdown("### 成交量異常觀察")
    st.caption("成交量超過20日均量1.5倍的股票 | 量能變化不代表方向性判斷，僅供參考")

    # 使用 Plotly 柱狀圖顯示
    symbols = [s["symbol"] for s in anomalies]
    ratios = [s["volume_ratio"] for s in anomalies]
    changes = [s["weekly_change_pct"] for s in anomalies]
    bar_colors = [_change_color(c) for c in changes]

    fig = go.Figure(go.Bar(
        x=symbols,
        y=ratios,
        marker_color=bar_colors,
        text=[f"{r:.1f}x" for r in ratios],
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "成交量倍數: %{y:.1f}x<br>"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        yaxis_title="成交量 / 20日均量",
        height=350,
        margin=dict(t=20, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#e5e7eb"),
    )

    # 添加 1.0x 基準線
    fig.add_hline(y=1.0, line_dash="dash", line_color="#9ca3af",
                  annotation_text="均量基準", annotation_position="bottom right")

    st.plotly_chart(fig, use_container_width=True)


def render_market_summary_bar(macro_data: Dict[str, Dict[str, Any]]):
    """渲染頂部市場摘要列

    在頁面最上方以精簡的方式顯示幾個核心指數的最新狀態，
    讓使用者一眼掌握市場大方向。

    Args:
        macro_data: 宏觀指標資料
    """
    us_indices = macro_data.get("美股主要指數", {})
    if not us_indices:
        return

    # 取出 S&P 500, 道瓊, 那斯達克, VIX
    key_symbols = ["^GSPC", "^DJI", "^IXIC", "^VIX"]
    display_data = []
    for sym in key_symbols:
        if sym in us_indices:
            display_data.append(us_indices[sym])

    if not display_data:
        return

    cols = st.columns(len(display_data))
    for i, data in enumerate(display_data):
        with cols[i]:
            daily_pct = data["daily_change_pct"]
            price = data["price"]

            if price >= 1000:
                price_str = f"{price:,.0f}"
            else:
                price_str = f"{price:.2f}"

            delta_str = _format_change(daily_pct)
            st.metric(label=data["name"], value=price_str, delta=delta_str)


def render_data_freshness():
    """渲染資料更新時間說明

    顯示資料的最後更新時間，以及自動更新機制的說明。
    """
    now = datetime.now()
    st.markdown(
        f"""
        <div style="
            text-align: center;
            color: #9ca3af;
            font-size: 0.78rem;
            margin-top: 2rem;
            padding: 0.5rem;
            border-top: 1px solid #e5e7eb;
        ">
            資料快取時間：{now.strftime('%Y-%m-%d %H:%M')} | 快取有效期 1 小時 |
            資料來源：Yahoo Finance |
            所有內容僅供資訊參考，不構成投資建議
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 主要渲染函數
# ---------------------------------------------------------------------------

def render_hot_topics():
    """渲染熱門特區頁面

    作為本模組的主入口函數，依序渲染以下區塊：
    1. 免責聲明
    2. 市場摘要列
    3. 宏觀經濟概覽
    4. 產業板塊熱力圖
    5. 熱門個股卡片
    6. 成交量異常觀察
    7. 資料更新時間
    """
    # 應用通用UI樣式
    apply_hide_deploy_button_css()

    # 頁面標題
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            color: white;
            text-align: center;
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
        ">
            <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.3rem;">
                 熱門特區
            </div>
            <div style="font-size: 1rem; opacity: 0.9;">
                近一週市場動態速覽 | 以日為觀察單位
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 免責聲明（置頂）
    render_disclaimer()

    # 檢查 yfinance 是否可用
    if not YF_AVAILABLE:
        st.error(
            "yfinance 套件未安裝，無法載入市場資料。"
            "請執行 `pip install yfinance` 安裝後重啟應用程式。"
        )
        return

    # 載入資料（帶載入動畫）
    with st.spinner("正在載入市場資料，請稍候..."):
        macro_data = get_macro_indicators()
        sector_data = get_sector_trends()
        trending_stocks = get_trending_stocks()

    # 頂部市場摘要
    render_market_summary_bar(macro_data)

    st.markdown("---")

    # 宏觀經濟概覽
    render_macro_overview(macro_data)

    st.markdown("---")

    # 產業板塊熱力圖
    render_sector_heatmap(sector_data)

    st.markdown("---")

    # 熱門個股
    render_trending_stocks(trending_stocks)

    st.markdown("---")

    # 成交量異常
    render_volume_anomalies(trending_stocks)

    # 頁尾免責聲明與資料時間
    st.markdown("---")
    render_disclaimer()
    render_data_freshness()


# ---------------------------------------------------------------------------
# 獨立運行入口
# ---------------------------------------------------------------------------

def main():
    """獨立運行時的主函數"""
    st.set_page_config(
        page_title="熱門特區 - TradingAgents-CN",
        page_icon="",
        layout="wide",
    )
    render_hot_topics()


if __name__ == "__main__":
    main()
