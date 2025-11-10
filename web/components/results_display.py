"""
分析結果顯示組件
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# 導入導出功能
from utils.report_exporter import render_export_buttons

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

def render_results(results):
    """渲染分析結果"""

    if not results:
        st.warning("暂無分析結果")
        return

    # 添加CSS確保結果內容不被右侧遮挡
    st.markdown("""
    <style>
    /* 確保分析結果內容有足夠的右邊距 */
    .element-container, .stMarkdown, .stExpander {
        margin-right: 1.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* 特別處理展開組件 */
    .streamlit-expanderHeader {
        margin-right: 1rem !important;
    }

    /* 確保文本內容不被截斷 */
    .stMarkdown p, .stMarkdown div {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    </style>
    """, unsafe_allow_html=True)

    stock_symbol = results.get('stock_symbol', 'N/A')
    decision = results.get('decision', {})
    state = results.get('state', {})
    success = results.get('success', False)
    error = results.get('error')

    st.markdown("---")
    st.header(f"📊 {stock_symbol} 分析結果")

    # 如果分析失败，顯示錯誤信息
    if not success and error:
        st.error(f"❌ **分析失败**: {error}")
        st.info("💡 **解決方案**: 請檢查API密鑰配置，確保網絡連接正常，然後重新運行分析。")
        return

    # 投資決策摘要
    render_decision_summary(decision, stock_symbol)

    # 分析配置信息
    render_analysis_info(results)

    # 詳細分析報告
    render_detailed_analysis(state)

    # 風險提示
    render_risk_warning()
    
    # 導出報告功能
    render_export_buttons(results)

def render_analysis_info(results):
    """渲染分析配置信息"""

    with st.expander("📋 分析配置信息", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            llm_provider = results.get('llm_provider', 'dashscope')
            provider_name = {
                'dashscope': '阿里百炼',
                'google': 'Google AI',
                'qianfan': '文心一言（千帆）'
            }.get(llm_provider, llm_provider)

            st.metric(
                label="LLM提供商",
                value=provider_name,
                help="使用的AI模型提供商"
            )

        with col2:
            llm_model = results.get('llm_model', 'N/A')
            logger.debug(f"🔍 [DEBUG] llm_model from results: {llm_model}")
            model_display = {
                'qwen-turbo': 'Qwen Turbo',
                'qwen-plus': 'Qwen Plus',
                'qwen-max': 'Qwen Max',
                'gemini-2.0-flash': 'Gemini 2.0 Flash',
                'gemini-1.5-pro': 'Gemini 1.5 Pro',
                'gemini-1.5-flash': 'Gemini 1.5 Flash',
                'ERNIE-Speed-8K': 'ERNIE Speed 8K',
                'ERNIE-Lite-8K': 'ERNIE Lite 8K'
            }.get(llm_model, llm_model)

            st.metric(
                label="AI模型",
                value=model_display,
                help="使用的具體AI模型"
            )

        with col3:
            analysts = results.get('analysts', [])
            logger.debug(f"🔍 [DEBUG] analysts from results: {analysts}")
            analysts_count = len(analysts) if analysts else 0

            st.metric(
                label="分析師數量",
                value=f"{analysts_count}個",
                help="參与分析的AI分析師數量"
            )

        # 顯示分析師列表
        if analysts:
            st.write("**參与的分析師:**")
            analyst_names = {
                'market': '📈 市場技術分析師',
                'fundamentals': '💰 基本面分析師',
                'news': '📰 新聞分析師',
                'social_media': '💭 社交媒體分析師',
                'risk': '⚠️ 風險評估師'
            }

            analyst_list = [analyst_names.get(analyst, analyst) for analyst in analysts]
            st.write(" • ".join(analyst_list))

def render_decision_summary(decision, stock_symbol=None):
    """渲染投資決策摘要"""

    st.subheader("🎯 投資決策摘要")

    # 如果沒有決策數據，顯示占位符
    if not decision:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    padding: 30px; border-radius: 15px; text-align: center;
                    border: 2px dashed #dee2e6; margin: 20px 0;">
            <h4 style="color: #6c757d; margin-bottom: 15px;">📊 等待投資決策</h4>
            <p style="color: #6c757d; font-size: 16px; margin-bottom: 20px;">
                分析完成後，投資決策将在此處顯示
            </p>
            <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                <span style="background: white; padding: 8px 16px; border-radius: 20px;
                           color: #6c757d; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    📊 投資建議
                </span>
                <span style="background: white; padding: 8px 16px; border-radius: 20px;
                           color: #6c757d; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    💰 目標價位
                </span>
                <span style="background: white; padding: 8px 16px; border-radius: 20px;
                           color: #6c757d; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    ⚖️ 風險評級
                </span>
                <span style="background: white; padding: 8px 16px; border-radius: 20px;
                           color: #6c757d; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🎯 置信度
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        action = decision.get('action', 'N/A')

        # 将英文投資建議轉換為中文
        action_translation = {
            'BUY': '买入',
            'SELL': '卖出',
            'HOLD': '持有',
            '买入': '买入',
            '卖出': '卖出',
            '持有': '持有'
        }

        # 獲取中文投資建議
        chinese_action = action_translation.get(action.upper(), action)

        action_color = {
            'BUY': 'normal',
            'SELL': 'inverse',
            'HOLD': 'off',
            '买入': 'normal',
            '卖出': 'inverse',
            '持有': 'off'
        }.get(action.upper(), 'normal')

        st.metric(
            label="投資建議",
            value=chinese_action,
            help="基於AI分析的投資建議"
        )

    with col2:
        confidence = decision.get('confidence', 0)
        if isinstance(confidence, (int, float)):
            confidence_str = f"{confidence:.1%}"
            confidence_delta = f"{confidence-0.5:.1%}" if confidence != 0 else None
        else:
            confidence_str = str(confidence)
            confidence_delta = None

        st.metric(
            label="置信度",
            value=confidence_str,
            delta=confidence_delta,
            help="AI對分析結果的置信度"
        )

    with col3:
        risk_score = decision.get('risk_score', 0)
        if isinstance(risk_score, (int, float)):
            risk_str = f"{risk_score:.1%}"
            risk_delta = f"{risk_score-0.3:.1%}" if risk_score != 0 else None
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
        logger.debug(f"🔍 [DEBUG] target_price from decision: {target_price}, type: {type(target_price)}")
        logger.debug(f"🔍 [DEBUG] decision keys: {list(decision.keys()) if isinstance(decision, dict) else 'Not a dict'}")

        # 根據股票代碼確定貨币符號
        def is_china_stock(ticker_code):
            import re

            return re.match(r'^\d{6}$', str(ticker_code)) if ticker_code else False

        is_china = is_china_stock(stock_symbol)
        currency_symbol = "¥" if is_china else "$"

        # 處理目標價格顯示
        if target_price is not None and isinstance(target_price, (int, float)) and target_price > 0:
            price_display = f"{currency_symbol}{target_price:.2f}"
            help_text = "AI預測的目標價位"
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
        with st.expander("🧠 AI分析推理", expanded=True):
            st.markdown(decision['reasoning'])

def render_detailed_analysis(state):
    """渲染詳細分析報告"""

    st.subheader("📋 詳細分析報告")

    # 添加自定義CSS樣式美化標簽页
    st.markdown("""
    <style>
    /* 標簽页容器樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* 單個標簽页樣式 */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 8px 16px;
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        color: #495057;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* 標簽页悬停效果 */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e3f2fd;
        border-color: #2196f3;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(33,150,243,0.2);
    }

    /* 選中的標簽页樣式 */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
        box-shadow: 0 4px 12px rgba(102,126,234,0.3) !important;
        transform: translateY(-2px);
    }

    /* 標簽页內容區域 */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e1e5e9;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* 標簽页文字樣式 */
    .stTabs [data-baseweb="tab"] p {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
    }

    /* 選中標簽页的文字樣式 */
    .stTabs [aria-selected="true"] p {
        color: white !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # 調試信息：顯示實际的狀態键
    if st.checkbox("🔍 顯示調試信息", key="debug_state_keys"):
        st.write("**實际狀態中的键：**")
        st.write(list(state.keys()))
        st.write("**各键的數據類型和內容預覽：**")
        for key, value in state.items():
            if isinstance(value, str):
                preview = value[:100] + "..." if len(value) > 100 else value
                st.write(f"- `{key}`: {type(value).__name__} ({len(value)} 字符) - {preview}")
            elif isinstance(value, dict):
                st.write(f"- `{key}`: {type(value).__name__} - 包含键: {list(value.keys())}")
            else:
                st.write(f"- `{key}`: {type(value).__name__} - {str(value)[:100]}")
        st.markdown("---")
    
    # 定義分析模塊 - 包含完整的团隊決策報告，与CLI端保持一致
    analysis_modules = [
        {
            'key': 'market_report',
            'title': '📈 市場技術分析',
            'icon': '📈',
            'description': '技術指標、價格趋势、支撑阻力位分析'
        },
        {
            'key': 'fundamentals_report',
            'title': '💰 基本面分析',
            'icon': '💰',
            'description': '財務數據、估值水平、盈利能力分析'
        },
        {
            'key': 'sentiment_report',
            'title': '💭 市場情绪分析',
            'icon': '💭',
            'description': '投資者情绪、社交媒體情绪指標'
        },
        {
            'key': 'news_report',
            'title': '📰 新聞事件分析',
            'icon': '📰',
            'description': '相關新聞事件、市場動態影響分析'
        },
        {
            'key': 'risk_assessment',
            'title': '⚠️ 風險評估',
            'icon': '⚠️',
            'description': '風險因素识別、風險等級評估'
        },
        {
            'key': 'investment_plan',
            'title': '📋 投資建議',
            'icon': '📋',
            'description': '具體投資策略、仓位管理建議'
        },
        # 添加团隊決策報告模塊
        {
            'key': 'investment_debate_state',
            'title': '🔬 研究团隊決策',
            'icon': '🔬',
            'description': '多头/空头研究員辩論分析，研究經理綜合決策'
        },
        {
            'key': 'trader_investment_plan',
            'title': '💼 交易团隊計劃',
            'icon': '💼',
            'description': '專業交易員制定的具體交易執行計劃'
        },
        {
            'key': 'risk_debate_state',
            'title': '⚖️ 風險管理团隊',
            'icon': '⚖️',
            'description': '激進/保守/中性分析師風險評估，投資組合經理最終決策'
        },
        {
            'key': 'final_trade_decision',
            'title': '🎯 最終交易決策',
            'icon': '🎯',
            'description': '綜合所有团隊分析後的最終投資決策'
        }
    ]
    
    # 過濾出有數據的模塊
    available_modules = []
    for module in analysis_modules:
        if module['key'] in state and state[module['key']]:
            # 檢查字典類型的數據是否有實际內容
            if isinstance(state[module['key']], dict):
                # 對於字典，檢查是否有非空的值
                has_content = any(v for v in state[module['key']].values() if v)
                if has_content:
                    available_modules.append(module)
            else:
                # 對於字符串或其他類型，直接添加
                available_modules.append(module)

    if not available_modules:
        # 顯示占位符而不是演示數據
        render_analysis_placeholder()
        return

    # 只為有數據的模塊創建標簽页 - 移除重複圖標
    tabs = st.tabs([module['title'] for module in available_modules])

    for i, (tab, module) in enumerate(zip(tabs, available_modules)):
        with tab:
            # 在內容區域顯示圖標和描述
            st.markdown(f"## {module['icon']} {module['title']}")
            st.markdown(f"*{module['description']}*")
            st.markdown("---")

            # 格式化顯示內容
            content = state[module['key']]
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, dict):
                # 特殊處理团隊決策報告的字典結構
                if module['key'] == 'investment_debate_state':
                    render_investment_debate_content(content)
                elif module['key'] == 'risk_debate_state':
                    render_risk_debate_content(content)
                else:
                    # 普通字典格式化顯示
                    for key, value in content.items():
                        st.subheader(key.replace('_', ' ').title())
                        st.write(value)
            else:
                st.write(content)

def render_investment_debate_content(content):
    """渲染研究团隊決策內容"""
    if content.get('bull_history'):
        st.subheader("📈 多头研究員分析")
        st.markdown(content['bull_history'])
        st.markdown("---")

    if content.get('bear_history'):
        st.subheader("📉 空头研究員分析")
        st.markdown(content['bear_history'])
        st.markdown("---")

    if content.get('judge_decision'):
        st.subheader("🎯 研究經理綜合決策")
        st.markdown(content['judge_decision'])

def render_risk_debate_content(content):
    """渲染風險管理团隊決策內容"""
    if content.get('risky_history'):
        st.subheader("🚀 激進分析師評估")
        st.markdown(content['risky_history'])
        st.markdown("---")

    if content.get('safe_history'):
        st.subheader("🛡️ 保守分析師評估")
        st.markdown(content['safe_history'])
        st.markdown("---")

    if content.get('neutral_history'):
        st.subheader("⚖️ 中性分析師評估")
        st.markdown(content['neutral_history'])
        st.markdown("---")

    if content.get('judge_decision'):
        st.subheader("🎯 投資組合經理最終決策")
        st.markdown(content['judge_decision'])

def render_analysis_placeholder():
    """渲染分析占位符"""

    st.markdown("""
    <div style="text-align: center; padding: 40px; background-color: #f8f9fa; border-radius: 10px; border: 2px dashed #dee2e6;">
        <h3 style="color: #6c757d; margin-bottom: 20px;">📊 等待分析數據</h3>
        <p style="color: #6c757d; font-size: 16px; margin-bottom: 30px;">
            請先配置API密鑰並運行股票分析，分析完成後詳細報告将在此處顯示
        </p>

        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 150px;">
                <div style="font-size: 24px; margin-bottom: 8px;">📈</div>
                <div style="font-weight: bold; color: #495057;">技術分析</div>
                <div style="font-size: 12px; color: #6c757d;">價格趋势、支撑阻力</div>
            </div>

            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 150px;">
                <div style="font-size: 24px; margin-bottom: 8px;">💰</div>
                <div style="font-weight: bold; color: #495057;">基本面分析</div>
                <div style="font-size: 12px; color: #6c757d;">財務數據、估值分析</div>
            </div>

            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 150px;">
                <div style="font-size: 24px; margin-bottom: 8px;">📰</div>
                <div style="font-weight: bold; color: #495057;">新聞分析</div>
                <div style="font-size: 12px; color: #6c757d;">市場情绪、事件影響</div>
            </div>

            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 150px;">
                <div style="font-size: 24px; margin-bottom: 8px;">⚖️</div>
                <div style="font-weight: bold; color: #495057;">風險評估</div>
                <div style="font-size: 12px; color: #6c757d;">風險控制、投資建議</div>
            </div>
        </div>

        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="color: #1976d2; margin: 0; font-size: 14px;">
                💡 <strong>提示</strong>: 配置API密鑰後，系統将生成包含多個智能體团隊分析的詳細投資報告
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_risk_warning():
    """渲染風險提示"""

    st.markdown("---")
    st.subheader("⚠️ 重要風險提示")

    # 移除演示數據相關的提示，因為我們不再顯示演示數據
    st.error("""
    **投資風險提示**:
    - **僅供參考**: 本分析結果僅供參考，不構成投資建議
    - **投資風險**: 股票投資有風險，可能導致本金損失
    - **理性決策**: 請結合多方信息進行理性投資決策
    - **專業咨詢**: 重大投資決策建議咨詢專業財務顧問
    - **自擔風險**: 投資決策及其後果由投資者自行承擔
    """)

    # 添加時間戳
    st.caption(f"分析生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def create_price_chart(price_data):
    """創建價格走势圖"""
    
    if not price_data:
        return None
    
    fig = go.Figure()
    
    # 添加價格線
    fig.add_trace(go.Scatter(
        x=price_data['date'],
        y=price_data['price'],
        mode='lines',
        name='股價',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # 設置圖表樣式
    fig.update_layout(
        title="股價走势圖",
        xaxis_title="日期",
        yaxis_title="價格 ($)",
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_sentiment_gauge(sentiment_score):
    """創建情绪指標儀表盘"""
    
    if sentiment_score is None:
        return None
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = sentiment_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "市場情绪指數"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "lightgray"},
                {'range': [25, 50], 'color': "gray"},
                {'range': [50, 75], 'color': "lightgreen"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    return fig
