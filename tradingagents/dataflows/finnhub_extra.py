"""
FinnHub 進階資料聚合模組
將多個免費 API 端點聚合為三個工具函式，供分析師智慧體使用
包含：情緒數據、分析師共識、技術訊號
"""

import os
import finnhub
from datetime import datetime, timedelta
from tradingagents.utils.logging_manager import get_logger

logger = get_logger('dataflows')


def _get_finnhub_client():
    """取得 FinnHub 客戶端實例"""
    api_key = os.getenv('FINNHUB_API_KEY', '')
    if not api_key or api_key.startswith('your_') or api_key == 'CHANGE_ME':
        return None
    return finnhub.Client(api_key=api_key)


def get_finnhub_sentiment_report(ticker: str, curr_date: str) -> str:
    """
    情緒數據聚合工具 - 整合新聞情緒量化評分和社交媒體情緒
    包含：News Sentiment + Social Sentiment

    Args:
        ticker: 股票代碼（如 AAPL、TSLA）
        curr_date: 當前日期，格式 YYYY-MM-DD

    Returns:
        str: Markdown 格式的情緒分析報告
    """
    client = _get_finnhub_client()
    if not client:
        return "FinnHub API 金鑰未設定，無法取得情緒數據"

    report_sections = []
    report_sections.append(f"# {ticker} FinnHub 情緒數據報告\n")
    report_sections.append(f"**數據日期**: {curr_date}\n")

    # --- News Sentiment ---
    try:
        news_sentiment = client.news_sentiment(ticker)
        if news_sentiment and news_sentiment.get('sentiment'):
            sent = news_sentiment['sentiment']
            buzz = news_sentiment.get('buzz', {})
            company_news_score = news_sentiment.get('companyNewsScore', 0)
            sector_avg_score = news_sentiment.get('sectorAverageBullishPercent', 0)
            sector_avg_news = news_sentiment.get('sectorAverageNewsScore', 0)

            report_sections.append("## 新聞情緒分析\n")
            report_sections.append("| 指標 | 數值 |")
            report_sections.append("|------|------|")
            report_sections.append(f"| 看多情緒 | {sent.get('bullishPercent', 0):.1%} |")
            report_sections.append(f"| 看空情緒 | {sent.get('bearishPercent', 0):.1%} |")
            report_sections.append(f"| 公司新聞評分 | {company_news_score:.4f} |")
            report_sections.append(f"| 行業平均看多比例 | {sector_avg_score:.1%} |")
            report_sections.append(f"| 行業平均新聞評分 | {sector_avg_news:.4f} |")

            # 新聞熱度
            if buzz:
                articles_this_week = buzz.get('articlesInLastWeek', 0)
                weekly_avg = buzz.get('weeklyAverage', 0)
                buzz_ratio = buzz.get('buzz', 0)
                report_sections.append(f"| 本週文章數 | {articles_this_week} |")
                report_sections.append(f"| 週平均文章數 | {weekly_avg:.1f} |")
                report_sections.append(f"| 熱度比率 | {buzz_ratio:.2f} |")

            report_sections.append("")

            # 情緒摘要
            bullish = sent.get('bullishPercent', 0)
            bearish = sent.get('bearishPercent', 0)
            if bullish > 0.6:
                sentiment_label = "強烈看多"
            elif bullish > 0.5:
                sentiment_label = "偏向看多"
            elif bearish > 0.6:
                sentiment_label = "強烈看空"
            elif bearish > 0.5:
                sentiment_label = "偏向看空"
            else:
                sentiment_label = "中性"

            # 與行業比較
            diff_from_sector = bullish - sector_avg_score if sector_avg_score > 0 else 0
            if diff_from_sector > 0.1:
                sector_comparison = "顯著高於行業平均"
            elif diff_from_sector > 0:
                sector_comparison = "略高於行業平均"
            elif diff_from_sector < -0.1:
                sector_comparison = "顯著低於行業平均"
            else:
                sector_comparison = "接近行業平均"

            report_sections.append(f"**新聞情緒總結**: {sentiment_label}，{sector_comparison}\n")
        else:
            report_sections.append("## 新聞情緒分析\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub News Sentiment 取得失敗 ({ticker}): {e}")
        report_sections.append("## 新聞情緒分析\n數據取得失敗\n")

    # --- Social Sentiment (Twitter/Reddit) ---
    try:
        # 取得近 3 天的社交媒體情緒數據
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=3)

        # Twitter 情緒
        twitter_data = client.stock_social_sentiment(
            ticker,
            _from=start_dt.strftime("%Y-%m-%d"),
            to=end_dt.strftime("%Y-%m-%d")
        )

        has_twitter = twitter_data and twitter_data.get('twitter') and len(twitter_data['twitter']) > 0
        has_reddit = twitter_data and twitter_data.get('reddit') and len(twitter_data['reddit']) > 0

        if has_twitter or has_reddit:
            report_sections.append("## 社交媒體情緒\n")

            if has_twitter:
                tw_entries = twitter_data['twitter']
                # 計算彙總
                total_mention = sum(e.get('mention', 0) for e in tw_entries)
                total_positive = sum(e.get('positiveMention', 0) for e in tw_entries)
                total_negative = sum(e.get('negativeMention', 0) for e in tw_entries)
                avg_score = sum(e.get('score', 0) for e in tw_entries) / max(len(tw_entries), 1)

                report_sections.append("### Twitter/X 情緒")
                report_sections.append("| 指標 | 數值 |")
                report_sections.append("|------|------|")
                report_sections.append(f"| 總提及次數 | {total_mention} |")
                report_sections.append(f"| 正面提及 | {total_positive} |")
                report_sections.append(f"| 負面提及 | {total_negative} |")
                if total_mention > 0:
                    report_sections.append(f"| 正面比例 | {total_positive / total_mention:.1%} |")
                report_sections.append(f"| 平均評分 | {avg_score:.4f} |")
                report_sections.append("")

            if has_reddit:
                rd_entries = twitter_data['reddit']
                total_mention = sum(e.get('mention', 0) for e in rd_entries)
                total_positive = sum(e.get('positiveMention', 0) for e in rd_entries)
                total_negative = sum(e.get('negativeMention', 0) for e in rd_entries)
                avg_score = sum(e.get('score', 0) for e in rd_entries) / max(len(rd_entries), 1)

                report_sections.append("### Reddit 情緒")
                report_sections.append("| 指標 | 數值 |")
                report_sections.append("|------|------|")
                report_sections.append(f"| 總提及次數 | {total_mention} |")
                report_sections.append(f"| 正面提及 | {total_positive} |")
                report_sections.append(f"| 負面提及 | {total_negative} |")
                if total_mention > 0:
                    report_sections.append(f"| 正面比例 | {total_positive / total_mention:.1%} |")
                report_sections.append(f"| 平均評分 | {avg_score:.4f} |")
                report_sections.append("")
        else:
            report_sections.append("## 社交媒體情緒\n近期無社交媒體討論數據\n")
    except Exception as e:
        logger.warning(f"FinnHub Social Sentiment 取得失敗 ({ticker}): {e}")
        report_sections.append("## 社交媒體情緒\n數據取得失敗\n")

    report_sections.append("---\n*數據來源: FinnHub API (免費方案)*")
    return "\n".join(report_sections)


def get_finnhub_analyst_report(ticker: str, curr_date: str) -> str:
    """
    分析師共識數據聚合工具 - 整合華爾街分析師評級和預測
    包含：Recommendation Trends + Price Target + Upgrade/Downgrade +
          EPS Estimates + Revenue Estimates + Earnings Calendar + Peers

    Args:
        ticker: 股票代碼（如 AAPL、TSLA）
        curr_date: 當前日期，格式 YYYY-MM-DD

    Returns:
        str: Markdown 格式的分析師共識報告
    """
    client = _get_finnhub_client()
    if not client:
        return "FinnHub API 金鑰未設定，無法取得分析師數據"

    report_sections = []
    report_sections.append(f"# {ticker} 華爾街分析師共識報告\n")
    report_sections.append(f"**數據日期**: {curr_date}\n")

    # --- Recommendation Trends ---
    try:
        recs = client.recommendation_trends(ticker)
        if recs and len(recs) > 0:
            report_sections.append("## 分析師評級分布\n")
            report_sections.append("| 期間 | 強力買入 | 買入 | 持有 | 賣出 | 強力賣出 |")
            report_sections.append("|------|---------|------|------|------|---------|")
            for rec in recs[:4]:
                period = rec.get('period', 'N/A')
                sb = rec.get('strongBuy', 0)
                b = rec.get('buy', 0)
                h = rec.get('hold', 0)
                s = rec.get('sell', 0)
                ss = rec.get('strongSell', 0)
                report_sections.append(f"| {period} | {sb} | {b} | {h} | {s} | {ss} |")
            report_sections.append("")

            # 最新一期的共識
            latest = recs[0]
            total = sum([
                latest.get('strongBuy', 0), latest.get('buy', 0),
                latest.get('hold', 0), latest.get('sell', 0),
                latest.get('strongSell', 0)
            ])
            if total > 0:
                buy_pct = (latest.get('strongBuy', 0) + latest.get('buy', 0)) / total
                if buy_pct > 0.7:
                    consensus = "強力買入共識"
                elif buy_pct > 0.5:
                    consensus = "偏向買入"
                elif buy_pct < 0.3:
                    consensus = "偏向賣出"
                else:
                    consensus = "意見分歧"
                report_sections.append(f"**最新共識**: {consensus}（買入類佔比 {buy_pct:.0%}）\n")
        else:
            report_sections.append("## 分析師評級分布\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub Recommendation Trends 取得失敗 ({ticker}): {e}")
        report_sections.append("## 分析師評級分布\n數據取得失敗\n")

    # --- Price Target ---
    try:
        pt = client.price_target(ticker)
        if pt and pt.get('targetMean'):
            report_sections.append("## 目標價共識\n")
            report_sections.append("| 指標 | 價格 (USD) |")
            report_sections.append("|------|-----------|")
            report_sections.append(f"| 最高目標價 | ${pt.get('targetHigh', 0):.2f} |")
            report_sections.append(f"| 平均目標價 | ${pt.get('targetMean', 0):.2f} |")
            report_sections.append(f"| 中位數目標價 | ${pt.get('targetMedian', 0):.2f} |")
            report_sections.append(f"| 最低目標價 | ${pt.get('targetLow', 0):.2f} |")
            report_sections.append(f"| 分析師數量 | {pt.get('lastUpdated', 'N/A')} |")
            report_sections.append("")
        else:
            report_sections.append("## 目標價共識\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub Price Target 取得失敗 ({ticker}): {e}")
        report_sections.append("## 目標價共識\n數據取得失敗\n")

    # --- Upgrade/Downgrade ---
    try:
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=90)
        upgrades = client.upgrade_downgrade(
            symbol=ticker,
            _from=start_dt.strftime("%Y-%m-%d"),
            to=end_dt.strftime("%Y-%m-%d")
        )
        if upgrades and len(upgrades) > 0:
            report_sections.append("## 近期評級變動\n")
            report_sections.append("| 日期 | 公司 | 動作 | 原評級 | 新評級 |")
            report_sections.append("|------|------|------|--------|--------|")
            for ug in upgrades[:10]:
                grade_date = ug.get('gradeDate', 'N/A')
                company = ug.get('company', 'N/A')
                action = ug.get('action', 'N/A')
                from_grade = ug.get('fromGrade', 'N/A')
                to_grade = ug.get('toGrade', 'N/A')
                report_sections.append(f"| {grade_date} | {company} | {action} | {from_grade} | {to_grade} |")
            report_sections.append("")
        else:
            report_sections.append("## 近期評級變動\n近 90 天無評級變動\n")
    except Exception as e:
        logger.warning(f"FinnHub Upgrade/Downgrade 取得失敗 ({ticker}): {e}")
        report_sections.append("## 近期評級變動\n數據取得失敗\n")

    # --- EPS Estimates ---
    try:
        eps_est = client.company_eps_estimates(ticker, freq='quarterly')
        if eps_est and eps_est.get('data') and len(eps_est['data']) > 0:
            report_sections.append("## EPS 預測（季度）\n")
            report_sections.append("| 期間 | 平均預測 | 最高預測 | 最低預測 | 分析師數 |")
            report_sections.append("|------|---------|---------|---------|---------|")
            for est in eps_est['data'][:4]:
                period = est.get('period', 'N/A')
                avg_est = est.get('epsAvg', 0)
                high_est = est.get('epsHigh', 0)
                low_est = est.get('epsLow', 0)
                num = est.get('numberAnalysts', 0)
                report_sections.append(
                    f"| {period} | ${avg_est:.2f} | ${high_est:.2f} | ${low_est:.2f} | {num} |"
                )
            report_sections.append("")
        else:
            report_sections.append("## EPS 預測\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub EPS Estimates 取得失敗 ({ticker}): {e}")
        report_sections.append("## EPS 預測\n數據取得失敗\n")

    # --- Revenue Estimates ---
    try:
        rev_est = client.company_revenue_estimates(ticker, freq='quarterly')
        if rev_est and rev_est.get('data') and len(rev_est['data']) > 0:
            report_sections.append("## 營收預測（季度）\n")
            report_sections.append("| 期間 | 平均預測 | 最高預測 | 最低預測 | 分析師數 |")
            report_sections.append("|------|---------|---------|---------|---------|")
            for est in rev_est['data'][:4]:
                period = est.get('period', 'N/A')
                avg_rev = est.get('revenueAvg', 0) or 0
                high_rev = est.get('revenueHigh', 0) or 0
                low_rev = est.get('revenueLow', 0) or 0
                num = est.get('numberAnalysts', 0)
                # 營收用百萬美元表示
                report_sections.append(
                    f"| {period} | ${avg_rev / 1e6:.1f}M | ${high_rev / 1e6:.1f}M | ${low_rev / 1e6:.1f}M | {num} |"
                )
            report_sections.append("")
        else:
            report_sections.append("## 營收預測\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub Revenue Estimates 取得失敗 ({ticker}): {e}")
        report_sections.append("## 營收預測\n數據取得失敗\n")

    # --- Earnings Calendar ---
    try:
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        future_dt = end_dt + timedelta(days=90)
        earnings_cal = client.earnings_calendar(
            _from=curr_date,
            to=future_dt.strftime("%Y-%m-%d"),
            symbol=ticker
        )
        if earnings_cal and earnings_cal.get('earningsCalendar') and len(earnings_cal['earningsCalendar']) > 0:
            next_earning = earnings_cal['earningsCalendar'][0]
            report_sections.append("## 下次財報日期\n")
            report_sections.append(f"- **日期**: {next_earning.get('date', 'N/A')}")
            report_sections.append(f"- **EPS 預測**: ${next_earning.get('epsEstimate', 'N/A')}")
            report_sections.append(f"- **營收預測**: ${next_earning.get('revenueEstimate', 'N/A')}")
            hour = next_earning.get('hour', '')
            if hour == 'bmo':
                report_sections.append("- **時段**: 盤前")
            elif hour == 'amc':
                report_sections.append("- **時段**: 盤後")
            report_sections.append("")
        else:
            report_sections.append("## 下次財報日期\n近 90 天內無預定財報發布\n")
    except Exception as e:
        logger.warning(f"FinnHub Earnings Calendar 取得失敗 ({ticker}): {e}")
        report_sections.append("## 下次財報日期\n數據取得失敗\n")

    # --- Peers ---
    try:
        peers = client.company_peers(ticker)
        if peers and len(peers) > 0:
            # 過濾掉自己
            peer_list = [p for p in peers if p != ticker][:10]
            if peer_list:
                report_sections.append("## 同業公司\n")
                report_sections.append(f"同業股票代碼: {', '.join(peer_list)}\n")
        else:
            report_sections.append("## 同業公司\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub Peers 取得失敗 ({ticker}): {e}")
        report_sections.append("## 同業公司\n數據取得失敗\n")

    report_sections.append("---\n*數據來源: FinnHub API (免費方案)*")
    return "\n".join(report_sections)


def get_finnhub_technical_report(ticker: str, resolution: str = 'D') -> str:
    """
    技術訊號聚合工具 - 整合技術分析指標和支撐壓力位
    包含：Aggregate Indicators + Support Resistance

    Args:
        ticker: 股票代碼（如 AAPL、TSLA）
        resolution: 時間解析度，預設 D（日線）

    Returns:
        str: Markdown 格式的技術訊號報告
    """
    client = _get_finnhub_client()
    if not client:
        return "FinnHub API 金鑰未設定，無法取得技術訊號"

    report_sections = []
    report_sections.append(f"# {ticker} FinnHub 技術訊號報告\n")
    report_sections.append(f"**時間解析度**: {resolution}\n")

    # --- Aggregate Indicators ---
    try:
        indicators = client.aggregate_indicator(ticker, resolution)
        if indicators and indicators.get('technicalAnalysis'):
            ta = indicators['technicalAnalysis']
            trend = indicators.get('trend', {})

            report_sections.append("## 綜合技術訊號\n")
            report_sections.append("| 指標 | 數值 |")
            report_sections.append("|------|------|")

            # 訊號統計
            signal = ta.get('signal', 'N/A')
            buy_count = ta.get('buy', 0)
            sell_count = ta.get('sell', 0)
            neutral_count = ta.get('neutral', 0)
            report_sections.append(f"| 綜合訊號 | **{signal}** |")
            report_sections.append(f"| 買入訊號數 | {buy_count} |")
            report_sections.append(f"| 賣出訊號數 | {sell_count} |")
            report_sections.append(f"| 中性訊號數 | {neutral_count} |")

            # 趨勢資訊
            if trend:
                adx = trend.get('adx', 0)
                trending = trend.get('trending', False)
                report_sections.append(f"| ADX 趨勢強度 | {adx:.2f} |")
                trend_label = "趨勢明確" if trending else "盤整中"
                report_sections.append(f"| 趨勢狀態 | {trend_label} |")

            report_sections.append("")

            # 訊號摘要
            total_signals = buy_count + sell_count + neutral_count
            if total_signals > 0:
                buy_pct = buy_count / total_signals
                if buy_pct > 0.6:
                    signal_summary = "多數指標偏多"
                elif buy_pct < 0.4:
                    signal_summary = "多數指標偏空"
                else:
                    signal_summary = "指標意見分歧"
                report_sections.append(
                    f"**訊號摘要**: {signal_summary}（買入 {buy_count}/{total_signals}）\n"
                )
        else:
            report_sections.append("## 綜合技術訊號\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub Aggregate Indicators 取得失敗 ({ticker}): {e}")
        report_sections.append("## 綜合技術訊號\n數據取得失敗\n")

    # --- Support Resistance ---
    try:
        sr = client.support_resistance(ticker, resolution)
        if sr and sr.get('levels') and len(sr['levels']) > 0:
            levels = sorted(sr['levels'])
            report_sections.append("## 支撐與壓力位\n")
            report_sections.append("| 類型 | 價位 (USD) |")
            report_sections.append("|------|-----------|")

            # 找出支撐位和壓力位（需要當前價格來區分）
            # 沒有當前價格時，取中間值作為分界
            mid_idx = len(levels) // 2
            for i, level in enumerate(levels):
                if i < mid_idx:
                    label = "支撐位"
                elif i == mid_idx:
                    label = "關鍵價位"
                else:
                    label = "壓力位"
                report_sections.append(f"| {label} | ${level:.2f} |")
            report_sections.append("")
        else:
            report_sections.append("## 支撐與壓力位\n無可用數據\n")
    except Exception as e:
        logger.warning(f"FinnHub Support Resistance 取得失敗 ({ticker}): {e}")
        report_sections.append("## 支撐與壓力位\n數據取得失敗\n")

    report_sections.append("---\n*數據來源: FinnHub API (免費方案)*")
    return "\n".join(report_sections)
