#!/usr/bin/env python3
"""
UI工具函數
提供通用的UI組件和樣式
"""

import streamlit as st

def apply_hide_deploy_button_css():
    """
    應用隱藏Deploy按钮和工具栏的CSS樣式
    在所有页面中調用此函數以確保一致的UI體驗
    """
    st.markdown("""
    <style>
        /* 隱藏Streamlit顶部工具栏和Deploy按钮 - 多種選擇器確保兼容性 */
        .stAppToolbar {
            display: none !important;
        }
        
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        .stDeployButton {
            display: none !important;
        }
        
        /* 新版本Streamlit的Deploy按钮選擇器 */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        [data-testid="stDecoration"] {
            display: none !important;
        }
        
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        
        /* 隱藏整個顶部區域 */
        .stApp > header {
            display: none !important;
        }
        
        .stApp > div[data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* 隱藏主菜單按钮 */
        #MainMenu {
            visibility: hidden !important;
            display: none !important;
        }
        
        /* 隱藏页腳 */
        footer {
            visibility: hidden !important;
            display: none !important;
        }
        
        /* 隱藏"Made with Streamlit"標识 */
        .viewerBadge_container__1QSob {
            display: none !important;
        }
        
        /* 隱藏所有可能的工具栏元素 */
        div[data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* 隱藏右上角的所有按钮 */
        .stApp > div > div > div > div > section > div {
            padding-top: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_common_styles():
    """
    應用通用的页面樣式
    包括隱藏Deploy按钮和其他美化樣式
    """
    # 隱藏Deploy按钮
    apply_hide_deploy_button_css()
    
    # 其他通用樣式
    st.markdown("""
    <style>
        /* 應用樣式 */
        .main-header {
            background: linear-gradient(90deg, #1f77b4, #ff7f0e);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        
        .metric-card {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
            margin: 0.5rem 0;
        }
        
        .analysis-section {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .success-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .error-box {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)