"""
分析結果顯示組件
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from utils.report_exporter import render_export_buttons
from tradingagents.utils.logging_manager import get_logger

logger = get_logger('web')


def render_results(results):
    """渲染分析結果主入口"""

    if not results:
        st.warning("暫無分析結果")
        return

    stock_symbol = results.get('stock_symbol', 'N/A')
    decision = results.get('decision', {})
    state = results.get('state', {})
    success = results.get('success', False)
    error = results.get('error')

    st.markdown("---")
    st.header(f"{stock_symbol} 分析結果")

    # 分析失敗時顯示錯誤
    if not success and error:
        st.error(f"**分析失敗**: {error}")
        st.info("**解決方案**: 請檢查 API 密鑰配置，確保網絡連接正常，然後重新運行分析。")
        return

    # 投資決策摘要
    render_decision_summary(decision, stock_symbol)

    # 分析配置信息
    render_analysis_info(results)

    # 詳細分析報告
    render_detailed_analysis(state)

    # 風險提示
    render_risk_warning()

    # 導出報告
    render_export_buttons(results)


def render_analysis_info(results):
    """渲染分析配置信息"""

    with st.expander("分析配置信息", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            llm_provider = results.get('llm_provider', 'openai')
            provider_name = {
                'openai': 'OpenAI',
                'anthropic': 'Anthropic',
            }.get(llm_provider, llm_provider)

            st.metric(
                label="LLM 提供商",
                value=provider_name,
                help="使用的 AI 模型提供商"
            )

        with col2:
            llm_model = results.get('llm_model', 'N/A')
            model_display = {
                'gpt-4o': 'GPT-4o',
                'gpt-4o-mini': 'GPT-4o Mini',
                'o1-mini': 'o1 Mini',
                'o1': 'o1',
                'claude-opus-4-6': 'Claude Opus 4.6',
                'claude-sonnet-4-6': 'Claude Sonnet 4.6',
                'claude-sonnet-4-5-20250514': 'Claude Sonnet 4.5',
                'claude-haiku-4-5-20251001': 'Claude Haiku 4.5',
            }.get(llm_model, llm_model)

            st.metric(
                label="AI 模型",
                value=model_display,
                help="使用的具體 AI 模型"
            )

        with col3:
            analysts = results.get('analysts', [])
            analysts_count = len(analysts) if analysts else 0

            st.metric(
                label="分析師數量",
                value=f"{analysts_count} 個",
                help="參與分析的 AI 分析師數量"
            )

        # 顯示分析師列表
        if analysts:
            st.write("**參與的分析師:**")
            analyst_names = {
                'market': '市場技術分析師',
                'fundamentals': '基本面分析師',
                'news': '新聞分析師',
                'social_media': '社交媒體分析師',
                'risk': '風險評估師'
            }

            analyst_list = [analyst_names.get(analyst, analyst) for analyst in analysts]
            st.write(" / ".join(analyst_list))


def render_decision_summary(decision, stock_symbol=None):
    """渲染投資決策摘要"""

    st.subheader("投資決策摘要")

    # 沒有決策數據時顯示提示
    if not decision:
        st.info("分析完成後，投資決策將在此處顯示。包含投資建議、目標價位、風險評級和置信度等關鍵指標。")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        action = decision.get('action', 'N/A')

        action_translation = {
            'BUY': '買入',
            'SELL': '賣出',
            'HOLD': '持有',
            '買入': '買入',
            '賣出': '賣出',
            '持有': '持有'
        }

        chinese_action = action_translation.get(action.upper(), action)

        st.metric(
            label="投資建議",
            value=chinese_action,
            help="基於 AI 分析的投資建議"
        )

    with col2:
        confidence = decision.get('confidence', 0)
        if isinstance(confidence, (int, float)):
            confidence_str = f"{confidence:.1%}"
            confidence_delta = f"{confidence - 0.5:.1%}" if confidence != 0 else None
        else:
            confidence_str = str(confidence)
            confidence_delta = None

        st.metric(
            label="置信度",
            value=confidence_str,
            delta=confidence_delta,
            help="AI 對分析結果的置信度"
        )

    with col3:
        risk_score = decision.get('risk_score', 0)
        if isinstance(risk_score, (int, float)):
            risk_str = f"{risk_score:.1%}"
            risk_delta = f"{risk_score - 0.3:.1%}" if risk_score != 0 else None
        else:
            risk_str = str(risk_score)
            risk_delta = None

        st.metric(
            label="風險評分",
            value=risk_str,
            delta=risk_delta,
            delta_color="inverse",
            help="投資風險評估分數"
        )

    with col4:
        target_price = decision.get('target_price')
        currency_symbol = "$"

        if target_price is not None and isinstance(target_price, (int, float)) and target_price > 0:
            price_display = f"{currency_symbol}{target_price:.2f}"
            help_text = "AI 預測的目標價位"
        else:
            price_display = "待分析"
            help_text = "目標價位需要更詳細的分析才能確定"

        st.metric(
            label="目標價位",
            value=price_display,
            help=help_text
        )

    # 分析推理
    if 'reasoning' in decision and decision['reasoning']:
        with st.expander("AI 分析推理", expanded=True):
            st.markdown(decision['reasoning'])


def render_detailed_analysis(state):
    """渲染詳細分析報告"""

    st.subheader("詳細分析報告")

    # 定義分析模塊
    analysis_modules = [
        {
            'key': 'market_report',
            'title': '市場技術分析',
            'description': '技術指標、價格趨勢、支撐阻力位分析'
        },
        {
            'key': 'fundamentals_report',
            'title': '基本面分析',
            'description': '財務數據、估值水平、盈利能力分析'
        },
        {
            'key': 'sentiment_report',
            'title': '市場情緒分析',
            'description': '投資者情緒、社交媒體情緒指標'
        },
        {
            'key': 'news_report',
            'title': '新聞事件分析',
            'description': '相關新聞事件、市場動態影響分析'
        },
        {
            'key': 'risk_assessment',
            'title': '風險評估',
            'description': '風險因素識別、風險等級評估'
        },
        {
            'key': 'investment_plan',
            'title': '投資建議',
            'description': '具體投資策略、倉位管理建議'
        },
        {
            'key': 'investment_debate_state',
            'title': '研究團隊決策',
            'description': '多頭/空頭研究員辯論分析，研究經理綜合決策'
        },
        {
            'key': 'trader_investment_plan',
            'title': '交易團隊計劃',
            'description': '專業交易員制定的具體交易執行計劃'
        },
        {
            'key': 'risk_debate_state',
            'title': '風險管理團隊',
            'description': '激進/保守/中性分析師風險評估，投資組合經理最終決策'
        },
        {
            'key': 'final_trade_decision',
            'title': '最終交易決策',
            'description': '綜合所有團隊分析後的最終投資決策'
        }
    ]

    # 過濾出有數據的模塊
    available_modules = []
    for module in analysis_modules:
        if module['key'] in state and state[module['key']]:
            if isinstance(state[module['key']], dict):
                has_content = any(v for v in state[module['key']].values() if v)
                if has_content:
                    available_modules.append(module)
            else:
                available_modules.append(module)

    if not available_modules:
        render_analysis_placeholder()
        return

    # 建立標籤頁
    tabs = st.tabs([module['title'] for module in available_modules])

    for i, (tab, module) in enumerate(zip(tabs, available_modules)):
        with tab:
            st.markdown(f"**{module['description']}**")
            st.markdown("---")

            content = state[module['key']]
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, dict):
                if module['key'] == 'investment_debate_state':
                    render_investment_debate_content(content)
                elif module['key'] == 'risk_debate_state':
                    render_risk_debate_content(content)
                else:
                    for key, value in content.items():
                        st.subheader(key.replace('_', ' ').title())
                        st.write(value)
            else:
                st.write(content)


def render_investment_debate_content(content):
    """渲染研究團隊決策內容"""
    if content.get('bull_history'):
        st.subheader("多頭研究員分析")
        st.markdown(content['bull_history'])
        st.markdown("---")

    if content.get('bear_history'):
        st.subheader("空頭研究員分析")
        st.markdown(content['bear_history'])
        st.markdown("---")

    if content.get('judge_decision'):
        st.subheader("研究經理綜合決策")
        st.markdown(content['judge_decision'])


def render_risk_debate_content(content):
    """渲染風險管理團隊決策內容"""
    if content.get('risky_history'):
        st.subheader("激進分析師評估")
        st.markdown(content['risky_history'])
        st.markdown("---")

    if content.get('safe_history'):
        st.subheader("保守分析師評估")
        st.markdown(content['safe_history'])
        st.markdown("---")

    if content.get('neutral_history'):
        st.subheader("中性分析師評估")
        st.markdown(content['neutral_history'])
        st.markdown("---")

    if content.get('judge_decision'):
        st.subheader("投資組合經理最終決策")
        st.markdown(content['judge_decision'])


def render_analysis_placeholder():
    """渲染分析數據等待提示"""

    st.info(
        "請先配置 API 密鑰並運行股票分析。"
        "分析完成後，系統將生成包含多個智能體團隊分析的詳細投資報告，"
        "涵蓋技術分析、基本面分析、新聞分析和風險評估。"
    )


def render_risk_warning():
    """渲染風險提示"""

    st.markdown("---")
    st.subheader("重要風險提示")

    st.error("""
    **投資風險提示**:
    - **僅供參考**: 本分析結果僅供參考，不構成投資建議
    - **投資風險**: 股票投資有風險，可能導致本金損失
    - **理性決策**: 請結合多方信息進行理性投資決策
    - **專業諮詢**: 重大投資決策建議諮詢專業財務顧問
    - **自擔風險**: 投資決策及其後果由投資者自行承擔
    """)

    st.caption(f"分析生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def create_price_chart(price_data):
    """建立價格走勢圖"""

    if not price_data:
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=price_data['date'],
        y=price_data['price'],
        mode='lines',
        name='股價',
        line=dict(color='#0369A1', width=2)
    ))

    fig.update_layout(
        title="股價走勢圖",
        xaxis_title="日期",
        yaxis_title="價格 ($)",
        hovermode='x unified',
        showlegend=True
    )

    return fig


def create_sentiment_gauge(sentiment_score):
    """建立情緒指標儀表盤"""

    if sentiment_score is None:
        return None

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sentiment_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "市場情緒指數"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#0369A1"},
            'steps': [
                {'range': [0, 25], 'color': "#F1F5F9"},
                {'range': [25, 50], 'color': "#E2E8F0"},
                {'range': [50, 75], 'color': "#BAE6FD"},
                {'range': [75, 100], 'color': "#7DD3FC"}
            ],
            'threshold': {
                'line': {'color': "#DC2626", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    return fig
