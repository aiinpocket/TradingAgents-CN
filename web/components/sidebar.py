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


def _render_openrouter_section() -> str:
    """OpenRouter 專用區塊：按提供商分類篩選模型"""

    # 模型類別選擇
    categories = ["openai", "anthropic", "meta", "google", "custom"]
    category_labels = {
        "openai": "OpenAI (GPT / o 系列)",
        "anthropic": "Anthropic (Claude 系列)",
        "meta": "Meta (Llama 系列)",
        "google": "Google (Gemini 系列)",
        "custom": "自定義模型 ID"
    }

    current_cat = st.session_state.get("model_category", "openai")
    if current_cat not in categories:
        current_cat = "openai"

    model_category = st.selectbox(
        "模型類別",
        options=categories,
        index=categories.index(current_cat),
        format_func=lambda x: category_labels.get(x, x),
        help="選擇模型廠商類別或自定義輸入",
        key="model_category_select"
    )

    # 類別變更時清空模型選擇
    if st.session_state.get("model_category") != model_category:
        logger.debug(f"[Persistence] 模型類別變更: {st.session_state.get('model_category')} -> {model_category}")
        st.session_state.llm_model = ""
    st.session_state.model_category = model_category

    save_model_selection(st.session_state.llm_provider, model_category, st.session_state.get("llm_model", ""))

    if model_category == "custom":
        # 自定義模型 ID 輸入
        st.markdown("### 自定義模型")
        default_val = st.session_state.get("llm_model", "") or "anthropic/claude-sonnet-4"
        llm_model = st.text_input(
            "輸入模型 ID",
            value=default_val,
            placeholder="例如: anthropic/claude-sonnet-4",
            help="輸入 OpenRouter 支持的任何模型 ID，查看 https://openrouter.ai/models",
            key="custom_model_input"
        )
        return llm_model

    # 從 OpenRouter 取得全部模型後按類別篩選
    all_models = fetch_models("openrouter")

    # 按前綴篩選
    prefix_map = {
        "openai": "openai/",
        "anthropic": "anthropic/",
        "meta": "meta-llama/",
        "google": "google/",
    }
    prefix = prefix_map.get(model_category, "")
    filtered = [m for m in all_models if m["id"].startswith(prefix)]

    if not filtered:
        st.warning(f"未找到 {category_labels.get(model_category, model_category)} 的模型")
        return st.session_state.get("llm_model", "")

    model_ids = [m["id"] for m in filtered]
    model_names = {m["id"]: m["name"] for m in filtered}

    current_index = 0
    current_model = st.session_state.get("llm_model", "")
    if current_model in model_ids:
        current_index = model_ids.index(current_model)

    selected = st.selectbox(
        f"選擇{category_labels.get(model_category, '')}模型",
        options=model_ids,
        index=current_index,
        format_func=lambda x: model_names.get(x, x),
        help=f"{category_labels.get(model_category, '')}的可用模型",
        key=f"{model_category}_openrouter_model_select"
    )

    return selected


def _render_custom_openai_section() -> str:
    """自定義 OpenAI 端點配置區塊"""
    st.markdown("### 自定義 OpenAI 端點配置")

    # API 端點 URL 配置
    if "custom_openai_base_url" not in st.session_state:
        st.session_state.custom_openai_base_url = os.getenv(
            "CUSTOM_OPENAI_BASE_URL", "https://api.openai.com/v1"
        )

    base_url = st.text_input(
        "API 端點 URL",
        value=st.session_state.custom_openai_base_url,
        placeholder="https://api.openai.com/v1",
        help="輸入 OpenAI 相容的 API 端點 URL",
        key="custom_openai_base_url_input"
    )
    st.session_state.custom_openai_base_url = base_url

    # API 密鑰狀態（只讀顯示）
    custom_api_key = os.getenv("CUSTOM_OPENAI_API_KEY", "")
    if custom_api_key:
        st.success("API 密鑰: 已透過 .env 檔案配置")
    else:
        st.warning("API 密鑰: 未配置，請在 .env 檔案中設定 CUSTOM_OPENAI_API_KEY")

    # 動態取得模型列表
    selected = _render_model_selector(
        provider="custom_openai",
        label="選擇模型",
        help_text="從端點動態取得的可用模型",
        select_key="custom_openai_model_select",
        base_url=base_url
    )

    # 自定義模型名稱輸入
    use_custom = st.checkbox("使用自定義模型名稱", key="use_custom_model_name")
    if use_custom:
        custom_name = st.text_input(
            "自定義模型名稱",
            placeholder="例如: gpt-4-custom",
            key="custom_model_name_input"
        )
        if custom_name:
            selected = custom_name

    # 常用端點快速配置
    st.markdown("**常用端點快速配置:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("OpenAI 官方", key="quick_openai_official", use_container_width=True):
            st.session_state.custom_openai_base_url = "https://api.openai.com/v1"
            clear_cache("custom_openai")
            st.rerun()
    with col2:
        if st.button("本地部署", key="quick_local_deploy", use_container_width=True):
            st.session_state.custom_openai_base_url = "http://localhost:8000/v1"
            clear_cache("custom_openai")
            st.rerun()

    # 配置說明
    if base_url and custom_api_key:
        st.success(f"配置完成")
        st.info(f"**端點**: `{base_url}`  **模型**: `{selected}`")
    elif base_url:
        st.warning("請在 .env 檔案中設定 CUSTOM_OPENAI_API_KEY")

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

        # LLM 提供商選擇
        providers = ["openai", "google", "anthropic", "openrouter", "custom_openai", "ollama"]
        provider_labels = {
            "openai": "OpenAI",
            "google": "Google AI",
            "anthropic": "Anthropic (Claude)",
            "openrouter": "OpenRouter",
            "custom_openai": "自定義 OpenAI 端點",
            "ollama": "Ollama (本地)"
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

        # 根據提供商渲染對應的模型選擇區塊
        if llm_provider == "openrouter":
            llm_model = _render_openrouter_section()
        elif llm_provider == "custom_openai":
            llm_model = _render_custom_openai_section()
        else:
            # OpenAI / Google / Anthropic / Ollama 共用邏輯
            provider_help = {
                "openai": "從 OpenAI API 動態取得的可用模型",
                "google": "從 Google AI API 動態取得的可用 Gemini 模型",
                "anthropic": "從 Anthropic API 動態取得的可用 Claude 模型",
                "ollama": "從本地 Ollama 服務取得的已下載模型",
            }
            llm_model = _render_model_selector(
                provider=llm_provider,
                label=f"選擇{provider_labels.get(llm_provider, '')}模型",
                help_text=provider_help.get(llm_provider, "選擇模型"),
                select_key=f"{llm_provider}_model_select"
            )

            # 提供商特定提示
            env_keys = {
                "openai": "OPENAI_API_KEY",
                "google": "GOOGLE_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
            }
            env_key = env_keys.get(llm_provider)
            if env_key:
                st.info(f"**{provider_labels.get(llm_provider, '')}配置**: 在 .env 檔案中設定 {env_key}")

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
        _show_key_status("FinnHub", "FINNHUB_API_KEY")

        st.markdown("*可選配置:*")
        # 只顯示已設定的密鑰
        optional_keys = [
            ("Google AI", "GOOGLE_API_KEY", "AIza"),
            ("OpenAI", "OPENAI_API_KEY", "sk-"),
            ("Anthropic", "ANTHROPIC_API_KEY", "sk-"),
            ("OpenRouter", "OPENROUTER_API_KEY", ""),
        ]
        for label, env_name, prefix in optional_keys:
            val = os.getenv(env_name, "")
            if val and not val.startswith("your_") and val != "CHANGE_ME":
                _show_key_status(label, env_name, prefix)

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
