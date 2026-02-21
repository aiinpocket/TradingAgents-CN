#!/usr/bin/env python3
"""
UI工具函數
提供通用的UI組件和樣式，統一管理所有 Streamlit 隱藏元素的 CSS
"""

import streamlit as st


def apply_hide_deploy_button_css():
    """
    隱藏 Streamlit 預設 UI 元素（工具列、Deploy 按鈕、頁腳等）
    在子頁面（config_management, cache_management, token_statistics）中調用
    主頁面 app.py 已在全域樣式中包含這些規則，無需重複調用
    """
    st.markdown("""
    <style>
        .stAppToolbar,
        header[data-testid="stHeader"],
        .stDeployButton,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stApp > header,
        #MainMenu,
        footer,
        .viewerBadge_container__1QSob {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)