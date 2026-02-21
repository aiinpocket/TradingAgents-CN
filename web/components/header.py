"""
頁面頭部組件
"""

import streamlit as st

def render_header():
    """渲染頁面頭部"""
    
    # 主標題
    st.markdown("""
    <div class="main-header">
        <h1>TradingAgents-CN 股票分析平台</h1>
        <p>基於多智能體大語言模型的中文金融交易決策框架</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能特性展示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>智能體協作</h4>
            <p>專業分析師團隊協同工作</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>中文優化</h4>
            <p>针對中文用戶優化的模型</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>實時數據</h4>
            <p>獲取最新的股票市場數據</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4>專業建議</h4>
            <p>基於AI的投資決策建議</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 分隔線
    st.markdown("---")
