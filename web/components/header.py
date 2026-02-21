"""
頁面頭部元件 - 簡潔的導航標題列
"""

import streamlit as st


def render_header():
    """渲染頁面頭部 - 簡潔的平台名稱"""

    st.markdown("""
    <div style="
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
        padding: 0.5rem 0 0.625rem 0;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #DEE2E6;
    ">
        <h1 style="
            font-size: 1.25rem;
            font-weight: 600;
            color: #212529;
            margin: 0;
            letter-spacing: -0.02em;
        ">TradingAgents</h1>
        <span style="
            font-size: 0.75rem;
            color: #ADB5BD;
            font-weight: 400;
        ">US Equities</span>
    </div>
    """, unsafe_allow_html=True)
