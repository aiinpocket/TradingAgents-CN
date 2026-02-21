"""
頁面頭部元件 - 簡潔的導航標題列
"""

import streamlit as st


def render_header():
    """渲染頁面頭部 - 簡潔的平台名稱"""

    st.markdown("""
    <div class="ta-header">
        <h1>TradingAgents</h1>
        <span class="ta-subtitle">US Equities</span>
    </div>
    """, unsafe_allow_html=True)
