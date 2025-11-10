"""
侧邊栏組件
"""

import streamlit as st
import os
import logging
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.utils.persistence import load_model_selection, save_model_selection
from web.utils.auth_manager import auth_manager

logger = logging.getLogger(__name__)

def get_version():
    """從VERSION文件讀取項目版本號"""
    try:
        version_file = project_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        else:
            return "unknown"
    except Exception as e:
        logger.warning(f"無法讀取版本文件: {e}")
        return "unknown"

def render_sidebar():
    """渲染侧邊栏配置"""

    # 添加localStorage支持的JavaScript
    st.markdown("""
    <script>
    // 保存到localStorage
    function saveToLocalStorage(key, value) {
        localStorage.setItem('tradingagents_' + key, value);
        console.log('Saved to localStorage:', key, value);
    }

    // 從localStorage讀取
    function loadFromLocalStorage(key, defaultValue) {
        const value = localStorage.getItem('tradingagents_' + key);
        console.log('Loaded from localStorage:', key, value || defaultValue);
        return value || defaultValue;
    }

    // 页面加載時恢複設置
    window.addEventListener('load', function() {
        console.log('Page loaded, restoring settings...');
    });
    </script>
    """, unsafe_allow_html=True)

    # 侧邊栏特定樣式（全局樣式在global_sidebar.css中）
    st.markdown("""
    <style>
    /* 侧邊栏宽度和基础樣式已在global_sidebar.css中定義 */

    /* 侧邊栏特定的內邊距和組件樣式 */
    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] > div > div,
    .css-1d391kg,
    .css-1lcbmhc,
    .css-1cypcdb {
        padding-top: 0.2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-bottom: 0.75rem !important;
    }

    /* 優化selectbox容器 */
    section[data-testid="stSidebar"] .stSelectbox {
        margin-bottom: 0.4rem !important;
        width: 100% !important;
    }

    /* 優化下拉框選項文本 */
    section[data-testid="stSidebar"] .stSelectbox label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.2rem !important;
    }

    /* 優化文本輸入框 */
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        font-size: 0.8rem !important;
        padding: 0.3rem 0.5rem !important;
        width: 100% !important;
    }

    /* 優化按钮樣式 */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 0.5rem !important;
        margin: 0.1rem 0 !important;
        border-radius: 0.3rem !important;
    }

    /* 優化標題樣式 */
    section[data-testid="stSidebar"] h3 {
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0rem !important;
        padding: 0 !important;
    }

    /* 優化info框樣式 */
    section[data-testid="stSidebar"] .stAlert {
        padding: 0.4rem !important;
        margin: 0.3rem 0 !important;
        font-size: 0.75rem !important;
    }

    /* 優化markdown文本 */
    section[data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.3rem !important;
        padding: 0 !important;
    }

    /* 優化分隔線 */
    section[data-testid="stSidebar"] hr {
        margin: 0.75rem 0 !important;
    }

    /* 確保下拉框選項完全可见 - 調整為適合320px */
    .stSelectbox [data-baseweb="select"] {
        min-width: 260px !important;
        max-width: 280px !important;
    }

    /* 優化下拉框選項列表 */
    .stSelectbox [role="listbox"] {
        min-width: 260px !important;
        max-width: 290px !important;
    }

    /* 額外的邊距控制 - 確保左右邊距减小 */
    .sidebar .element-container {
        padding: 0 !important;
        margin: 0.2rem 0 !important;
    }

    /* 強制覆蓋默認樣式 */
    .css-1d391kg .element-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* 减少侧邊栏顶部空白 */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* 减少第一個元素的顶部邊距 */
    section[data-testid="stSidebar"] .element-container:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 减少標題的顶部邊距 */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # 使用組件來從localStorage讀取並初始化session state
        st.markdown("""
        <div id="localStorage-reader" style="display: none;">
            <script>
            // 從localStorage讀取設置並發送給Streamlit
            const provider = loadFromLocalStorage('llm_provider', 'dashscope');
            const category = loadFromLocalStorage('model_category', 'openai');
            const model = loadFromLocalStorage('llm_model', '');

            // 通過自定義事件發送數據
            window.parent.postMessage({
                type: 'localStorage_data',
                provider: provider,
                category: category,
                model: model
            }, '*');
            </script>
        </div>
        """, unsafe_allow_html=True)

        # 從持久化存储加載配置
        saved_config = load_model_selection()

        # 初始化session state，優先使用保存的配置
        if 'llm_provider' not in st.session_state:
            st.session_state.llm_provider = saved_config['provider']
            logger.debug(f"🔧 [Persistence] 恢複 llm_provider: {st.session_state.llm_provider}")
        if 'model_category' not in st.session_state:
            st.session_state.model_category = saved_config['category']
            logger.debug(f"🔧 [Persistence] 恢複 model_category: {st.session_state.model_category}")
        if 'llm_model' not in st.session_state:
            st.session_state.llm_model = saved_config['model']
            logger.debug(f"🔧 [Persistence] 恢複 llm_model: {st.session_state.llm_model}")

        # 顯示當前session state狀態（調試用）
        logger.debug(f"🔍 [Session State] 當前狀態 - provider: {st.session_state.llm_provider}, category: {st.session_state.model_category}, model: {st.session_state.llm_model}")

        # AI模型配置
        st.markdown("### 🧠 AI模型配置")

        # LLM提供商選擇
        llm_provider = st.selectbox(
            "LLM提供商",
            options=["google", "openai", "openrouter", "custom_openai", "anthropic", "ollama"],
            index=["google", "openai", "openrouter", "custom_openai", "anthropic", "ollama"].index(st.session_state.llm_provider) if st.session_state.llm_provider in ["google", "openai", "openrouter", "custom_openai", "anthropic", "ollama"] else 0,
            format_func=lambda x: {
                "google": "🌟 Google AI",
                "openai": "🤖 OpenAI",
                "openrouter": "🌐 OpenRouter",
                "custom_openai": "🔧 自定義OpenAI端點",
                "anthropic": "🤖 Anthropic (Claude)",
                "ollama": "💻 Ollama (本地)"
            }[x],
            help="選擇AI模型提供商",
            key="llm_provider_select"
        )

        # 更新session state和持久化存储
        if st.session_state.llm_provider != llm_provider:
            logger.info(f"🔄 [Persistence] 提供商變更: {st.session_state.llm_provider} → {llm_provider}")
            st.session_state.llm_provider = llm_provider
            # 提供商變更時清空模型選擇
            st.session_state.llm_model = ""
            st.session_state.model_category = "openai"  # 重置為默認類別
            logger.info(f"🔄 [Persistence] 清空模型選擇")

            # 保存到持久化存储
            save_model_selection(llm_provider, st.session_state.model_category, "")
        else:
            st.session_state.llm_provider = llm_provider

        # 根據提供商顯示不同的模型選項
        if llm_provider == "google":
            google_options = [
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.5-pro-002",
                "gemini-2.5-flash-002",
                "gemini-2.5-flash-preview-05-20",
                "gemini-2.5-flash-lite-preview-06-17",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-2.0-pro-experimental",
                "gemini-1.5-pro",
                "gemini-1.5-flash"
            ]

            # 獲取當前選擇的索引
            current_index = 0
            if st.session_state.llm_model in google_options:
                current_index = google_options.index(st.session_state.llm_model)

            llm_model = st.selectbox(
                "選擇Google模型",
                options=google_options,
                index=current_index,
                format_func=lambda x: {
                    "gemini-2.5-pro": "🚀 Gemini 2.5 Pro - 最新旗艦模型（自適應思維）",
                    "gemini-2.5-flash": "⚡ Gemini 2.5 Flash - 最新快速模型（SWE-Bench 54%）",
                    "gemini-2.5-flash-lite": "💡 Gemini 2.5 Flash Lite - 輕量快速",
                    "gemini-2.5-pro-002": "🔧 Gemini 2.5 Pro-002 - 優化版本",
                    "gemini-2.5-flash-002": "⚡ Gemini 2.5 Flash-002 - 優化快速版",
                    "gemini-2.5-flash-preview-05-20": "🧪 Gemini 2.5 Flash Preview - 預覽版（推理強化）",
                    "gemini-2.5-flash-lite-preview-06-17": "⚡ Gemini 2.5 Flash Lite Preview - 超快響應",
                    "gemini-2.0-flash": "🚀 Gemini 2.0 Flash - 推薦使用",
                    "gemini-2.0-flash-lite": "💡 Gemini 2.0 Flash Lite - 輕量版",
                    "gemini-2.0-pro-experimental": "🧪 Gemini 2.0 Pro Experimental - 實驗版本",
                    "gemini-1.5-pro": "Gemini 1.5 Pro - 強大性能",
                    "gemini-1.5-flash": "Gemini 1.5 Flash - 快速響應"
                }[x],
                help="選擇用於分析的Google Gemini模型（包含2025年最新的2.5和2.0系列）",
                key="google_model_select"
            )

            # 更新session state和持久化存储
            if st.session_state.llm_model != llm_model:
                logger.debug(f"🔄 [Persistence] Google模型變更: {st.session_state.llm_model} → {llm_model}")
            st.session_state.llm_model = llm_model
            logger.debug(f"💾 [Persistence] Google模型已保存: {llm_model}")

            # 保存到持久化存储
            save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)
        elif llm_provider == "openai":
             openai_options = [
                 "gpt-5",
                 "gpt-5-mini",
                 "gpt-5-nano",
                 "o1",
                 "o1-mini",
                 "o1-preview",
                 "gpt-4o",
                 "gpt-4o-mini",
                 "gpt-4-turbo",
                 "gpt-4",
                 "gpt-3.5-turbo"
             ]

             # 獲取當前選擇的索引
             current_index = 6  # 默認選擇 gpt-4o
             if st.session_state.llm_model in openai_options:
                 current_index = openai_options.index(st.session_state.llm_model)

             llm_model = st.selectbox(
                 "選擇OpenAI模型",
                 options=openai_options,
                 index=current_index,
                 format_func=lambda x: {
                     "gpt-5": "🚀 GPT-5 - 2025最新旗艦模型",
                     "gpt-5-mini": "⚡ GPT-5 Mini - 輕量版GPT-5",
                     "gpt-5-nano": "💡 GPT-5 Nano - 超輕量版",
                     "o1": "🧠 o1 - 最新推理模型",
                     "o1-mini": "🧠 o1-mini - 輕量推理模型",
                     "o1-preview": "🧪 o1-preview - 推理模型預覽版",
                     "gpt-4o": "GPT-4o - 旗艦模型",
                     "gpt-4o-mini": "GPT-4o Mini - 輕量旗艦",
                     "gpt-4-turbo": "GPT-4 Turbo - 強化版",
                     "gpt-4": "GPT-4 - 經典版",
                     "gpt-3.5-turbo": "GPT-3.5 Turbo - 經濟版"
                 }[x],
                 help="選擇用於分析的OpenAI模型（包含2025年8月發布的GPT-5系列）",
                 key="openai_model_select"
             )

             # 快速選擇按钮
             st.markdown("**快速選擇:**")
             
             col1, col2 = st.columns(2)
             with col1:
                 if st.button("🚀 GPT-4o", key="quick_gpt4o", use_container_width=True):
                     model_id = "gpt-4o"
                     st.session_state.llm_model = model_id
                     save_model_selection(st.session_state.llm_provider, st.session_state.model_category, model_id)
                     logger.debug(f"💾 [Persistence] 快速選擇GPT-4o: {model_id}")
                     st.rerun()
             
             with col2:
                 if st.button("⚡ GPT-4o Mini", key="quick_gpt4o_mini", use_container_width=True):
                     model_id = "gpt-4o-mini"
                     st.session_state.llm_model = model_id
                     save_model_selection(st.session_state.llm_provider, st.session_state.model_category, model_id)
                     logger.debug(f"💾 [Persistence] 快速選擇GPT-4o Mini: {model_id}")
                     st.rerun()

             # 更新session state和持久化存储
             if st.session_state.llm_model != llm_model:
                 logger.debug(f"🔄 [Persistence] OpenAI模型變更: {st.session_state.llm_model} → {llm_model}")
             st.session_state.llm_model = llm_model
             logger.debug(f"💾 [Persistence] OpenAI模型已保存: {llm_model}")

             # 保存到持久化存储
             save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)

             # OpenAI特殊提示
             st.info("💡 **OpenAI配置**: 在.env文件中設置OPENAI_API_KEY")
        elif llm_provider == "custom_openai":
            st.markdown("### 🔧 自定義OpenAI端點配置")
            
            # 初始化session state
            if 'custom_openai_base_url' not in st.session_state:
                st.session_state.custom_openai_base_url = "https://api.openai.com/v1"
            if 'custom_openai_api_key' not in st.session_state:
                st.session_state.custom_openai_api_key = ""
            
            # API端點URL配置
            base_url = st.text_input(
                "API端點URL",
                value=st.session_state.custom_openai_base_url,
                placeholder="https://api.openai.com/v1",
                help="輸入OpenAI兼容的API端點URL，例如中轉服務或本地部署的API",
                key="custom_openai_base_url_input"
            )
            
            # 更新session state
            st.session_state.custom_openai_base_url = base_url
            
            # API密鑰配置
            api_key = st.text_input(
                "API密鑰",
                value=st.session_state.custom_openai_api_key,
                type="password",
                placeholder="sk-...",
                help="輸入API密鑰，也可以在.env文件中設置CUSTOM_OPENAI_API_KEY",
                key="custom_openai_api_key_input"
            )
            
            # 更新session state
            st.session_state.custom_openai_api_key = api_key
            
            # 模型選擇
            custom_openai_options = [
                "gpt-4o",
                "gpt-4o-mini", 
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "claude-3.5-sonnet",
                "claude-3-opus",
                "claude-3-sonnet",
                "claude-3-haiku",
                "gemini-pro",
                "gemini-1.5-pro",
                "llama-3.1-8b",
                "llama-3.1-70b",
                "llama-3.1-405b",
                "custom-model"
            ]
            
            # 獲取當前選擇的索引
            current_index = 0
            if st.session_state.llm_model in custom_openai_options:
                current_index = custom_openai_options.index(st.session_state.llm_model)
            
            llm_model = st.selectbox(
                "選擇模型",
                options=custom_openai_options,
                index=current_index,
                format_func=lambda x: {
                    "gpt-4o": "GPT-4o - OpenAI最新旗舰",
                    "gpt-4o-mini": "GPT-4o Mini - 轻量旗舰",
                    "gpt-4-turbo": "GPT-4 Turbo - 强化版",
                    "gpt-4": "GPT-4 - 經典版",
                    "gpt-3.5-turbo": "GPT-3.5 Turbo - 經濟版",
                    "claude-3.5-sonnet": "Claude 3.5 Sonnet - Anthropic旗舰",
                    "claude-3-opus": "Claude 3 Opus - 強大性能",
                    "claude-3-sonnet": "Claude 3 Sonnet - 平衡版",
                    "claude-3-haiku": "Claude 3 Haiku - 快速版",
                    "gemini-pro": "Gemini Pro - Google AI",
                    "gemini-1.5-pro": "Gemini 1.5 Pro - 增强版",
                    "llama-3.1-8b": "Llama 3.1 8B - Meta開源",
                    "llama-3.1-70b": "Llama 3.1 70B - 大型開源",
                    "llama-3.1-405b": "Llama 3.1 405B - 超大開源",
                    "custom-model": "自定義模型名稱"
                }[x],
                help="選擇要使用的模型，支持各種OpenAI兼容的模型",
                key="custom_openai_model_select"
            )
            
            # 如果選擇了自定義模型，顯示輸入框
            if llm_model == "custom-model":
                custom_model_name = st.text_input(
                    "自定義模型名稱",
                    value="",
                    placeholder="例如: gpt-4-custom, claude-3.5-sonnet-custom",
                    help="輸入自定義的模型名稱",
                    key="custom_model_name_input"
                )
                if custom_model_name:
                    llm_model = custom_model_name
            
            # 更新session state和持久化存储
            if st.session_state.llm_model != llm_model:
                logger.debug(f"🔄 [Persistence] 自定義OpenAI模型變更: {st.session_state.llm_model} → {llm_model}")
            st.session_state.llm_model = llm_model
            logger.debug(f"💾 [Persistence] 自定義OpenAI模型已保存: {llm_model}")
            
            # 保存到持久化存储
            save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)
            
            # 常用端點快速配置
            st.markdown("**🚀 常用端點快速配置:**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🌐 OpenAI官方", key="quick_openai_official", use_container_width=True):
                    st.session_state.custom_openai_base_url = "https://api.openai.com/v1"
                    st.rerun()
                
                if st.button("🇨🇳 OpenAI中轉1", key="quick_openai_relay1", use_container_width=True):
                    st.session_state.custom_openai_base_url = "https://api.openai-proxy.com/v1"
                    st.rerun()
            
            with col2:
                if st.button("🏠 本地部署", key="quick_local_deploy", use_container_width=True):
                    st.session_state.custom_openai_base_url = "http://localhost:8000/v1"
                    st.rerun()
                
                if st.button("🇨🇳 OpenAI中轉2", key="quick_openai_relay2", use_container_width=True):
                    st.session_state.custom_openai_base_url = "https://api.openai-sb.com/v1"
                    st.rerun()
            
            # 配置驗證
            if base_url and api_key:
                st.success(f"✅ 配置完成")
                st.info(f"**端點**: `{base_url}`")
                st.info(f"**模型**: `{llm_model}`")
            elif base_url:
                st.warning("⚠️ 請輸入API密鑰")
            else:
                st.warning("⚠️ 請配置API端點URL和密鑰")
            
            # 配置說明
            st.markdown("""
            **📖 配置說明:**
            - **API端點URL**: OpenAI兼容的API服務地址
            - **API密鑰**: 對應服務的API密鑰
            - **模型**: 選擇或自定義模型名稱
            
            **🔧 支持的服務類型:**
            - OpenAI官方API
            - OpenAI中轉服務
            - 本地部署的OpenAI兼容服務
            - 其他兼容OpenAI格式的API服務
            """)
        else:  # openrouter
            # OpenRouter模型分類選擇
            model_category = st.selectbox(
                "模型類別",
                options=["openai", "anthropic", "meta", "google", "custom"],
                index=["openai", "anthropic", "meta", "google", "custom"].index(st.session_state.model_category) if st.session_state.model_category in ["openai", "anthropic", "meta", "google", "custom"] else 0,
                format_func=lambda x: {
                    "openai": "🤖 OpenAI (GPT系列)",
                    "anthropic": "🧠 Anthropic (Claude系列)",
                    "meta": "🦙 Meta (Llama系列)",
                    "google": "🌟 Google (Gemini系列)",
                    "custom": "✏️ 自定義模型"
                }[x],
                help="選擇模型廠商類別或自定義輸入",
                key="model_category_select"
            )

            # 更新session state和持久化存储
            if st.session_state.model_category != model_category:
                logger.debug(f"🔄 [Persistence] 模型類別變更: {st.session_state.model_category} → {model_category}")
                st.session_state.llm_model = ""  # 類別變更時清空模型選擇
            st.session_state.model_category = model_category

            # 保存到持久化存储
            save_model_selection(st.session_state.llm_provider, model_category, st.session_state.llm_model)

            # 根據廠商顯示不同的模型
            if model_category == "openai":
                openai_options = [
                    "openai/o4-mini-high",
                    "openai/o3-pro",
                    "openai/o3-mini-high",
                    "openai/o3-mini",
                    "openai/o1-pro",
                    "openai/o1-mini",
                    "openai/gpt-4o-2024-11-20",
                    "openai/gpt-4o-mini",
                    "openai/gpt-4-turbo",
                    "openai/gpt-3.5-turbo"
                ]

                # 獲取當前選擇的索引
                current_index = 0
                if st.session_state.llm_model in openai_options:
                    current_index = openai_options.index(st.session_state.llm_model)

                llm_model = st.selectbox(
                    "選擇OpenAI模型",
                    options=openai_options,
                    index=current_index,
                    format_func=lambda x: {
                        "openai/o4-mini-high": "🚀 o4 Mini High - 最新o4系列",
                        "openai/o3-pro": "🚀 o3 Pro - 最新推理專業版",
                        "openai/o3-mini-high": "o3 Mini High - 高性能推理",
                        "openai/o3-mini": "o3 Mini - 推理模型",
                        "openai/o1-pro": "o1 Pro - 專業推理",
                        "openai/o1-mini": "o1 Mini - 轻量推理",
                        "openai/gpt-4o-2024-11-20": "GPT-4o (2024-11-20) - 最新版",
                        "openai/gpt-4o-mini": "GPT-4o Mini - 轻量旗舰",
                        "openai/gpt-4-turbo": "GPT-4 Turbo - 經典强化",
                        "openai/gpt-3.5-turbo": "GPT-3.5 Turbo - 經濟實用"
                    }[x],
                    help="OpenAI公司的GPT和o系列模型，包含最新o4",
                    key="openai_model_select"
                )

                # 更新session state和持久化存储
                if st.session_state.llm_model != llm_model:
                    logger.debug(f"🔄 [Persistence] OpenAI模型變更: {st.session_state.llm_model} → {llm_model}")
                st.session_state.llm_model = llm_model
                logger.debug(f"💾 [Persistence] OpenAI模型已保存: {llm_model}")

                # 保存到持久化存储
                save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)
            elif model_category == "anthropic":
                anthropic_options = [
                    "anthropic/claude-opus-4.1",
                    "anthropic/claude-sonnet-4.5",
                    "anthropic/claude-haiku-4.5",
                    "anthropic/claude-opus-4",
                    "anthropic/claude-sonnet-4",
                    "anthropic/claude-haiku-4",
                    "anthropic/claude-3.5-sonnet",
                    "anthropic/claude-3.5-haiku",
                    "anthropic/claude-3.5-sonnet-20241022",
                    "anthropic/claude-3.5-haiku-20241022",
                    "anthropic/claude-3-opus",
                    "anthropic/claude-3-sonnet",
                    "anthropic/claude-3-haiku"
                ]

                # 獲取當前選擇的索引
                current_index = 0
                if st.session_state.llm_model in anthropic_options:
                    current_index = anthropic_options.index(st.session_state.llm_model)

                llm_model = st.selectbox(
                    "選擇Anthropic模型",
                    options=anthropic_options,
                    index=current_index,
                    format_func=lambda x: {
                        "anthropic/claude-opus-4.1": "🚀 Claude Opus 4.1 - 最強模型（2025-08）",
                        "anthropic/claude-sonnet-4.5": "💻 Claude Sonnet 4.5 - 世界最強編碼模型（2025-09）",
                        "anthropic/claude-haiku-4.5": "⚡ Claude Haiku 4.5 - 高性價比（2025-10）",
                        "anthropic/claude-opus-4": "🚀 Claude Opus 4 - 頂級模型",
                        "anthropic/claude-sonnet-4": "🚀 Claude Sonnet 4 - 平衡模型",
                        "anthropic/claude-haiku-4": "🚀 Claude Haiku 4 - 快速模型",
                        "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet - 當前旗艦",
                        "anthropic/claude-3.5-haiku": "Claude 3.5 Haiku - 快速響應",
                        "anthropic/claude-3.5-sonnet-20241022": "Claude 3.5 Sonnet (2024-10-22)",
                        "anthropic/claude-3.5-haiku-20241022": "Claude 3.5 Haiku (2024-10-22)",
                        "anthropic/claude-3-opus": "Claude 3 Opus - 強大性能",
                        "anthropic/claude-3-sonnet": "Claude 3 Sonnet - 平衡版",
                        "anthropic/claude-3-haiku": "Claude 3 Haiku - 經濟版"
                    }[x],
                    help="Anthropic公司的Claude系列模型，包含2025年最新Claude 4.5系列",
                    key="anthropic_model_select"
                )

                # 更新session state和持久化存储
                if st.session_state.llm_model != llm_model:
                    logger.debug(f"🔄 [Persistence] Anthropic模型變更: {st.session_state.llm_model} → {llm_model}")
                st.session_state.llm_model = llm_model
                logger.debug(f"💾 [Persistence] Anthropic模型已保存: {llm_model}")

                # 保存到持久化存储
                save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)
            elif model_category == "meta":
                meta_options = [
                    "meta-llama/llama-4-maverick",
                    "meta-llama/llama-4-scout",
                    "meta-llama/llama-3.3-70b-instruct",
                    "meta-llama/llama-3.2-90b-vision-instruct",
                    "meta-llama/llama-3.1-405b-instruct",
                    "meta-llama/llama-3.1-70b-instruct",
                    "meta-llama/llama-3.2-11b-vision-instruct",
                    "meta-llama/llama-3.1-8b-instruct",
                    "meta-llama/llama-3.2-3b-instruct",
                    "meta-llama/llama-3.2-1b-instruct"
                ]

                # 獲取當前選擇的索引
                current_index = 0
                if st.session_state.llm_model in meta_options:
                    current_index = meta_options.index(st.session_state.llm_model)

                llm_model = st.selectbox(
                    "選擇Meta模型",
                    options=meta_options,
                    index=current_index,
                    format_func=lambda x: {
                        "meta-llama/llama-4-maverick": "🚀 Llama 4 Maverick - 最新旗舰",
                        "meta-llama/llama-4-scout": "🚀 Llama 4 Scout - 最新預覽",
                        "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B - 強大性能",
                        "meta-llama/llama-3.2-90b-vision-instruct": "Llama 3.2 90B Vision - 多模態",
                        "meta-llama/llama-3.1-405b-instruct": "Llama 3.1 405B - 超大模型",
                        "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B - 平衡性能",
                        "meta-llama/llama-3.2-11b-vision-instruct": "Llama 3.2 11B Vision - 轻量多模態",
                        "meta-llama/llama-3.1-8b-instruct": "Llama 3.1 8B - 高效模型",
                        "meta-llama/llama-3.2-3b-instruct": "Llama 3.2 3B - 轻量級",
                        "meta-llama/llama-3.2-1b-instruct": "Llama 3.2 1B - 超轻量"
                    }[x],
                    help="Meta公司的Llama系列模型，包含最新Llama 4",
                    key="meta_model_select"
                )

                # 更新session state和持久化存储
                if st.session_state.llm_model != llm_model:
                    logger.debug(f"🔄 [Persistence] Meta模型變更: {st.session_state.llm_model} → {llm_model}")
                st.session_state.llm_model = llm_model
                logger.debug(f"💾 [Persistence] Meta模型已保存: {llm_model}")

                # 保存到持久化存储
                save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)
            elif model_category == "google":
                google_openrouter_options = [
                    "google/gemini-2.5-pro",
                    "google/gemini-2.5-flash",
                    "google/gemini-2.5-flash-lite",
                    "google/gemini-2.5-pro-002",
                    "google/gemini-2.5-flash-002",
                    "google/gemini-2.0-flash-001",
                    "google/gemini-2.0-flash-lite-001",
                    "google/gemini-1.5-pro",
                    "google/gemini-1.5-flash",
                    "google/gemma-3-27b-it",
                    "google/gemma-3-12b-it",
                    "google/gemma-2-27b-it"
                ]

                # 獲取當前選擇的索引
                current_index = 0
                if st.session_state.llm_model in google_openrouter_options:
                    current_index = google_openrouter_options.index(st.session_state.llm_model)

                llm_model = st.selectbox(
                    "選擇Google模型",
                    options=google_openrouter_options,
                    index=current_index,
                    format_func=lambda x: {
                        "google/gemini-2.5-pro": "🚀 Gemini 2.5 Pro - 最新旗舰",
                        "google/gemini-2.5-flash": "⚡ Gemini 2.5 Flash - 最新快速",
                        "google/gemini-2.5-flash-lite": "💡 Gemini 2.5 Flash Lite - 轻量版",
                        "google/gemini-2.5-pro-002": "🔧 Gemini 2.5 Pro-002 - 優化版",
                        "google/gemini-2.5-flash-002": "⚡ Gemini 2.5 Flash-002 - 優化快速版",
                        "google/gemini-2.0-flash-001": "Gemini 2.0 Flash - 穩定版",
                        "google/gemini-2.0-flash-lite-001": "Gemini 2.0 Flash Lite",
                        "google/gemini-1.5-pro": "Gemini 1.5 Pro - 專業版",
                        "google/gemini-1.5-flash": "Gemini 1.5 Flash - 快速版",
                        "google/gemma-3-27b-it": "Gemma 3 27B - 最新開源大模型",
                        "google/gemma-3-12b-it": "Gemma 3 12B - 開源中型模型",
                        "google/gemma-2-27b-it": "Gemma 2 27B - 開源經典版"
                    }[x],
                    help="Google公司的Gemini/Gemma系列模型，包含最新Gemini 2.5",
                    key="google_openrouter_model_select"
                )

                # 更新session state和持久化存储
                if st.session_state.llm_model != llm_model:
                    logger.debug(f"🔄 [Persistence] Google OpenRouter模型變更: {st.session_state.llm_model} → {llm_model}")
                st.session_state.llm_model = llm_model
                logger.debug(f"💾 [Persistence] Google OpenRouter模型已保存: {llm_model}")

                # 保存到持久化存储
                save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)

            else:  # custom
                st.markdown("### ✏️ 自定義模型")

                # 初始化自定義模型session state
                if 'custom_model' not in st.session_state:
                    st.session_state.custom_model = ""

                # 自定義模型輸入 - 使用session state作為默認值
                default_value = st.session_state.custom_model if st.session_state.custom_model else "anthropic/claude-3.7-sonnet"

                llm_model = st.text_input(
                    "輸入模型ID",
                    value=default_value,
                    placeholder="例如: anthropic/claude-3.7-sonnet",
                    help="輸入OpenRouter支持的任何模型ID",
                    key="custom_model_input"
                )

                # 常用模型快速選擇
                st.markdown("**快速選擇常用模型:**")

                # 長條形按钮，每個占一行
                if st.button("🧠 Claude 3.7 Sonnet - 最新對話模型", key="claude37", use_container_width=True):
                    model_id = "anthropic/claude-3.7-sonnet"
                    st.session_state.custom_model = model_id
                    st.session_state.llm_model = model_id
                    save_model_selection(st.session_state.llm_provider, st.session_state.model_category, model_id)
                    logger.debug(f"💾 [Persistence] 快速選擇Claude 3.7 Sonnet: {model_id}")
                    st.rerun()

                if st.button("💎 Claude 4 Opus - 顶級性能模型", key="claude4opus", use_container_width=True):
                    model_id = "anthropic/claude-opus-4"
                    st.session_state.custom_model = model_id
                    st.session_state.llm_model = model_id
                    save_model_selection(st.session_state.llm_provider, st.session_state.model_category, model_id)
                    logger.debug(f"💾 [Persistence] 快速選擇Claude 4 Opus: {model_id}")
                    st.rerun()

                if st.button("🤖 GPT-4o - OpenAI旗舰模型", key="gpt4o", use_container_width=True):
                    model_id = "openai/gpt-4o"
                    st.session_state.custom_model = model_id
                    st.session_state.llm_model = model_id
                    save_model_selection(st.session_state.llm_provider, st.session_state.model_category, model_id)
                    logger.debug(f"💾 [Persistence] 快速選擇GPT-4o: {model_id}")
                    st.rerun()

                if st.button("🦙 Llama 4 Scout - Meta最新模型", key="llama4", use_container_width=True):
                    model_id = "meta-llama/llama-4-scout"
                    st.session_state.custom_model = model_id
                    st.session_state.llm_model = model_id
                    save_model_selection(st.session_state.llm_provider, st.session_state.model_category, model_id)
                    logger.debug(f"💾 [Persistence] 快速選擇Llama 4 Scout: {model_id}")
                    st.rerun()

                if st.button("🌟 Gemini 2.5 Pro - Google多模態", key="gemini25", use_container_width=True):
                    model_id = "google/gemini-2.5-pro"
                    st.session_state.custom_model = model_id
                    st.session_state.llm_model = model_id
                    save_model_selection(st.session_state.llm_provider, st.session_state.model_category, model_id)
                    logger.debug(f"💾 [Persistence] 快速選擇Gemini 2.5 Pro: {model_id}")
                    st.rerun()

                # 更新session state和持久化存储
                if st.session_state.llm_model != llm_model:
                    logger.debug(f"🔄 [Persistence] 自定義模型變更: {st.session_state.llm_model} → {llm_model}")
                st.session_state.custom_model = llm_model
                st.session_state.llm_model = llm_model
                logger.debug(f"💾 [Persistence] 自定義模型已保存: {llm_model}")

                # 保存到持久化存储
                save_model_selection(st.session_state.llm_provider, st.session_state.model_category, llm_model)

                # 模型驗證提示
                if llm_model:
                    st.success(f"✅ 當前模型: `{llm_model}`")

                    # 提供模型查找鏈接
                    st.markdown("""
                    **📚 查找更多模型:**
                    - [OpenRouter模型列表](https://openrouter.ai/models)
                    - [Anthropic模型文檔](https://docs.anthropic.com/claude/docs/models-overview)
                    - [OpenAI模型文檔](https://platform.openai.com/docs/models)
                    """)
                else:
                    st.warning("⚠️ 請輸入有效的模型ID")

            # OpenRouter特殊提示
            st.info("💡 **OpenRouter配置**: 在.env文件中設置OPENROUTER_API_KEY，或者如果只用OpenRouter可以設置OPENAI_API_KEY")
        
        # 高級設置
        with st.expander("⚙️ 高級設置"):
            enable_memory = st.checkbox(
                "啟用記忆功能",
                value=False,
                help="啟用智能體記忆功能（可能影響性能）"
            )
            
            enable_debug = st.checkbox(
                "調試模式",
                value=False,
                help="啟用詳細的調試信息輸出"
            )
            
            max_tokens = st.slider(
                "最大輸出長度",
                min_value=1000,
                max_value=8000,
                value=4000,
                step=500,
                help="AI模型的最大輸出token數量"
            )
        
        st.markdown("---")

        # 系統配置
        st.markdown("**🔧 系統配置**")

        # API密鑰狀態
        st.markdown("**🔑 API密鑰狀態**")

        def validate_api_key(key, expected_format):
            """驗證API密鑰格式"""
            if not key:
                return "未配置", "error"

            if expected_format == "dashscope" and key.startswith("sk-") and len(key) >= 32:
                return f"{key[:8]}...", "success"
            elif expected_format == "deepseek" and key.startswith("sk-") and len(key) >= 32:
                return f"{key[:8]}...", "success"
            elif expected_format == "finnhub" and len(key) >= 20:
                return f"{key[:8]}...", "success"
            elif expected_format == "tushare" and len(key) >= 32:
                return f"{key[:8]}...", "success"
            elif expected_format == "google" and key.startswith("AIza") and len(key) >= 32:
                return f"{key[:8]}...", "success"
            elif expected_format == "openai" and key.startswith("sk-") and len(key) >= 40:
                return f"{key[:8]}...", "success"
            elif expected_format == "anthropic" and key.startswith("sk-") and len(key) >= 40:
                return f"{key[:8]}...", "success"
            elif expected_format == "reddit" and len(key) >= 10:
                return f"{key[:8]}...", "success"
            else:
                return f"{key[:8]}... (格式異常)", "warning"

        # 必需的API密鑰
        st.markdown("*必需配置:*")

        # FinnHub
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        status, level = validate_api_key(finnhub_key, "finnhub")
        if level == "success":
            st.success(f"✅ FinnHub: {status}")
        elif level == "warning":
            st.warning(f"⚠️ FinnHub: {status}")
        else:
            st.error("❌ FinnHub: 未配置")

        # 可選的API密鑰
        st.markdown("*可選配置:*")

        # Google AI
        google_key = os.getenv("GOOGLE_API_KEY")
        status, level = validate_api_key(google_key, "google")
        if level == "success":
            st.success(f"✅ Google AI: {status}")
        elif level == "warning":
            st.warning(f"⚠️ Google AI: {status}")
        else:
            st.info("ℹ️ Google AI: 未配置")

        # OpenAI (如果配置了且不是默認值)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            status, level = validate_api_key(openai_key, "openai")
            if level == "success":
                st.success(f"✅ OpenAI: {status}")
            elif level == "warning":
                st.warning(f"⚠️ OpenAI: {status}")

        # Anthropic (如果配置了且不是默認值)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
            status, level = validate_api_key(anthropic_key, "anthropic")
            if level == "success":
                st.success(f"✅ Anthropic: {status}")
            elif level == "warning":
                st.warning(f"⚠️ Anthropic: {status}")

        st.markdown("---")

        # 系統信息
        st.markdown("**ℹ️ 系統信息**")
        
        st.info(f"""
        **版本**: {get_version()}
        **框架**: Streamlit + LangGraph
        **AI模型**: {st.session_state.llm_provider.upper()} - {st.session_state.llm_model}
        **數據源**: Tushare + FinnHub API
        """)
        
        # 管理員功能
        if auth_manager and auth_manager.check_permission("admin"):
            st.markdown("---")
            st.markdown("### 🔧 管理功能")
            
            if st.button("📊 用戶活動記錄", key="user_activity_btn", use_container_width=True):
                st.session_state.page = "user_activity"
            
            if st.button("⚙️ 系統設置", key="system_settings_btn", use_container_width=True):
                st.session_state.page = "system_settings"
        
        # 幫助鏈接
        st.markdown("**📚 幫助資源**")
        
        st.markdown("""
        - [📖 使用文檔](https://github.com/TauricResearch/TradingAgents)
        - [🐛 問題反饋](https://github.com/TauricResearch/TradingAgents/issues)
        - [💬 討論社區](https://github.com/TauricResearch/TradingAgents/discussions)
        - [🔧 API密鑰配置](../docs/security/api_keys_security.md)
        """)
    
    # 確保返回session state中的值，而不是局部變量
    final_provider = st.session_state.llm_provider
    final_model = st.session_state.llm_model

    logger.debug(f"🔄 [Session State] 返回配置 - provider: {final_provider}, model: {final_model}")

    return {
        'llm_provider': final_provider,
        'llm_model': final_model,
        'enable_memory': enable_memory,
        'enable_debug': enable_debug,
        'max_tokens': max_tokens
    }
