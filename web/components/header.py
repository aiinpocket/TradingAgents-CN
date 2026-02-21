"""
頁面頭部元件 - 簡潔的導航標題列
"""

import streamlit as st


def render_header():
    """渲染頁面頭部 - 簡潔的平台名稱和狀態列"""

    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #E2E8F0;
    ">
        <div>
            <h1 style="
                font-size: 1.5rem;
                font-weight: 600;
                color: #0F172A;
                margin: 0;
                letter-spacing: -0.025em;
            ">TradingAgents</h1>
            <p style="
                font-size: 0.813rem;
                color: #64748B;
                margin: 0.125rem 0 0 0;
            ">多智慧體股票分析系統</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
