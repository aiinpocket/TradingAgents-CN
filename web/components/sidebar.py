"""
側邊欄組件 - AI 模型配置與系統資訊
模型列表透過 API 動態取得，避免寫死
"""

import streamlit as st
import os
import logging
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.utils.persistence import load_model_selection, save_model_selection
from web.utils.model_fetcher import fetch_models, clear_cache
from tradingagents.i18n import t, set_language, get_current_language

logger = logging.getLogger(__name__)


def get_version():
    """從 VERSION 文件讀取項目版本號"""
    try:
        version_file = project_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        else:
            return "unknown"
    except Exception as e:
        logger.warning(f"無法讀取版本文件: {e}")
        return "unknown"


def _render_model_selector(provider: str, label: str, help_text: str,
                           select_key: str, **fetch_kwargs) -> str:
    """通用模型選擇器，從 API 動態取得模型列表

    回傳選中的模型 ID
    """
    models = fetch_models(provider, **fetch_kwargs)

    # 建立選項列表
    model_ids = [m["id"] for m in models]
    model_names = {m["id"]: m["name"] for m in models}

    if not model_ids:
        st.warning("無法取得模型列表")
        return st.session_state.get("llm_model", "")

    # 取得目前選中模型的索引
    current_index = 0
    current_model = st.session_state.get("llm_model", "")
    if current_model in model_ids:
        current_index = model_ids.index(current_model)

    selected = st.selectbox(
        label,
        options=model_ids,
        index=current_index,
        format_func=lambda x: f"{model_names.get(x, x)}",
        help=help_text,
        key=select_key
    )

    return selected


def render_sidebar():
    """渲染側邊欄配置"""

    # 側邊欄樣式
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] > div > div {
        padding-top: 0.2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-bottom: 0.75rem !important;
    }
    section[data-testid="stSidebar"] .stSelectbox {
        margin-bottom: 0.4rem !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.2rem !important;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        font-size: 0.8rem !important;
        padding: 0.3rem 0.5rem !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 0.5rem !important;
        margin: 0.1rem 0 !important;
        border-radius: 0.3rem !important;
    }
    section[data-testid="stSidebar"] h3 {
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0rem !important;
    }
    section[data-testid="stSidebar"] .stAlert {
        padding: 0.4rem !important;
        margin: 0.3rem 0 !important;
        font-size: 0.75rem !important;
    }
    section[data-testid="stSidebar"] hr {
        margin: 0.75rem 0 !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # 從持久化存儲載入配置
        saved_config = load_model_selection()

        if "llm_provider" not in st.session_state:
            st.session_state.llm_provider = saved_config["provider"]
        if "model_category" not in st.session_state:
            st.session_state.model_category = saved_config["category"]
        if "llm_model" not in st.session_state:
            st.session_state.llm_model = saved_config["model"]

        # AI 模型配置標題與重新整理按鈕
        col_title, col_refresh = st.columns([3, 1])
        with col_title:
            st.markdown("### AI 模型配置")
        with col_refresh:
            if st.button("↻", key="refresh_models", help="重新取得模型列表"):
                clear_cache()
                st.rerun()

        # LLM 提供商選擇（僅啟用已配置 API 金鑰的提供商）
        providers = ["openai", "anthropic"]
        provider_labels = {
            "openai": "OpenAI",
            "anthropic": "Anthropic (Claude)",
        }

        current_provider = st.session_state.llm_provider
        if current_provider not in providers:
            current_provider = "openai"

        llm_provider = st.selectbox(
            "LLM 提供商",
            options=providers,
            index=providers.index(current_provider),
            format_func=lambda x: provider_labels.get(x, x),
            help="選擇 AI 模型提供商",
            key="llm_provider_select"
        )

        # 提供商變更處理
        if st.session_state.llm_provider != llm_provider:
            logger.info(f"[Persistence] 提供商變更: {st.session_state.llm_provider} -> {llm_provider}")
            st.session_state.llm_provider = llm_provider
            st.session_state.llm_model = ""
            st.session_state.model_category = "openai"
            save_model_selection(llm_provider, "openai", "")
        else:
            st.session_state.llm_provider = llm_provider

        # 根據提供商渲染對應的模型選擇區塊（僅 OpenAI 和 Anthropic）
        provider_help = {
            "openai": "從 OpenAI API 動態取得的可用模型",
            "anthropic": "從 Anthropic API 動態取得的可用 Claude 模型",
        }
        llm_model = _render_model_selector(
            provider=llm_provider,
            label=f"選擇{provider_labels.get(llm_provider, '')}模型",
            help_text=provider_help.get(llm_provider, "選擇模型"),
            select_key=f"{llm_provider}_model_select"
        )

        # 更新 session state 與持久化
        if st.session_state.llm_model != llm_model:
            logger.debug(f"[Persistence] 模型變更: {st.session_state.llm_model} -> {llm_model}")
        st.session_state.llm_model = llm_model
        save_model_selection(
            st.session_state.llm_provider,
            st.session_state.get("model_category", "openai"),
            llm_model
        )

        # 高級設置
        with st.expander("高級設置"):
            enable_memory = st.checkbox(
                "啟用記憶功能",
                value=False,
                help="啟用智能體記憶功能（可能影響性能）"
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
                help="AI 模型的最大輸出 token 數量"
            )

        st.markdown("---")

        # API 密鑰狀態
        st.markdown("**API 密鑰狀態**")

        def _show_key_status(label: str, env_name: str, prefix: str = "", min_len: int = 20):
            """顯示 API 密鑰配置狀態"""
            key_val = os.getenv(env_name, "")
            if not key_val or key_val.startswith("your_") or key_val == "CHANGE_ME":
                st.error(f"{label}: 未配置")
            elif prefix and not key_val.startswith(prefix):
                st.warning(f"{label}: {key_val[:8]}... (格式異常)")
            elif len(key_val) >= min_len:
                st.success(f"{label}: {key_val[:8]}...")
            else:
                st.warning(f"{label}: {key_val[:8]}... (格式異常)")

        st.markdown("*必需配置:*")
        _show_key_status("OpenAI", "OPENAI_API_KEY", "sk-")
        _show_key_status("Anthropic", "ANTHROPIC_API_KEY", "sk-")
        _show_key_status("FinnHub", "FINNHUB_API_KEY")

        st.markdown("---")

        # 系統資訊
        st.markdown("**系統資訊**")
        st.info(f"""
        **版本**: {get_version()}
        **框架**: Streamlit + LangGraph
        **AI 模型**: {st.session_state.llm_provider.upper()} - {st.session_state.llm_model}
        **數據源**: FinnHub + Yahoo Finance
        """)

        # 管理功能
        st.markdown("---")
        st.markdown("### 管理功能")

        if st.button("系統設置", key="system_settings_btn", use_container_width=True):
            st.session_state.page = "system_settings"

        # 語言切換
        st.markdown(f"**{t('language.switch_language')}**")
        lang_options = {"zh_TW": "繁體中文", "en": "English"}
        current_lang = get_current_language()
        selected_lang = st.selectbox(
            t("language.current_language"),
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=list(lang_options.keys()).index(current_lang),
            key="language_selector",
            label_visibility="collapsed"
        )
        if selected_lang != current_lang:
            set_language(selected_lang)
            st.session_state.language = selected_lang
            st.rerun()

        # 幫助連結
        st.markdown(f"**{t('sidebar.help_resources')}**")
        st.markdown(f"""
        - [{t('sidebar.user_docs')}](https://github.com/TauricResearch/TradingAgents)
        - [{t('sidebar.issue_feedback')}](https://github.com/TauricResearch/TradingAgents/issues)
        - [{t('sidebar.discussion')}](https://github.com/TauricResearch/TradingAgents/discussions)
        """)

    # 回傳 session state 中的值
    final_provider = st.session_state.llm_provider
    final_model = st.session_state.llm_model

    logger.debug(f"[Session State] 回傳配置 - provider: {final_provider}, model: {final_model}")

    return {
        "llm_provider": final_provider,
        "llm_model": final_model,
        "enable_memory": enable_memory,
        "enable_debug": enable_debug,
        "max_tokens": max_tokens
    }
