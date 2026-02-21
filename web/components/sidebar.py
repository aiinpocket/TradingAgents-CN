"""
側邊欄元件 - 模型配置與系統資訊
模型列表透過 API 動態取得，避免寫死
"""

import streamlit as st
import os
from pathlib import Path

from web.utils.persistence import load_model_selection, save_model_selection
from web.utils.model_fetcher import fetch_models, clear_cache

# 日誌模組
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger('web')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent.parent


@st.cache_data(ttl=3600)
def get_version():
    """從 VERSION 檔案讀取專案版本號"""
    try:
        version_file = project_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        else:
            return "unknown"
    except Exception as e:
        logger.warning(f"無法讀取版本檔案: {e}")
        return "unknown"


def _render_model_selector(provider: str, label: str, help_text: str,
                           select_key: str, **fetch_kwargs) -> str:
    """通用模型選擇器，從 API 動態取得模型列表"""
    models = fetch_models(provider, **fetch_kwargs)

    model_ids = [m["id"] for m in models]
    model_names = {m["id"]: m["name"] for m in models}

    if not model_ids:
        st.warning("無法取得模型列表")
        return st.session_state.get("llm_model", "")

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
    """渲染側邊欄配置面板"""

    with st.sidebar:
        # 載入持久化配置
        saved_config = load_model_selection()

        if "llm_provider" not in st.session_state:
            st.session_state.llm_provider = saved_config["provider"]
        if "model_category" not in st.session_state:
            st.session_state.model_category = saved_config["category"]
        if "llm_model" not in st.session_state:
            st.session_state.llm_model = saved_config["model"]

        # 模型配置區塊
        col_title, col_refresh = st.columns([3, 1])
        with col_title:
            st.markdown("**模型配置**")
        with col_refresh:
            if st.button("↻", key="refresh_models", help="重新取得模型列表"):
                clear_cache()
                st.rerun()

        # LLM 提供商選擇
        providers = ["openai", "anthropic"]
        provider_labels = {
            "openai": "OpenAI",
            "anthropic": "Anthropic (Claude)",
        }

        current_provider = st.session_state.llm_provider
        if current_provider not in providers:
            current_provider = "openai"

        llm_provider = st.selectbox(
            "提供商",
            options=providers,
            index=providers.index(current_provider),
            format_func=lambda x: provider_labels.get(x, x),
            help="選擇模型提供商",
            key="llm_provider_select"
        )

        # 提供商變更處理
        if st.session_state.llm_provider != llm_provider:
            st.session_state.llm_provider = llm_provider
            st.session_state.llm_model = ""
            st.session_state.model_category = "openai"
            save_model_selection(llm_provider, "openai", "")
        else:
            st.session_state.llm_provider = llm_provider

        # 模型選擇
        provider_help = {
            "openai": "從 OpenAI API 動態取得可用模型",
            "anthropic": "從 Anthropic API 動態取得可用 Claude 模型",
        }
        llm_model = _render_model_selector(
            provider=llm_provider,
            label="模型",
            help_text=provider_help.get(llm_provider, "選擇模型"),
            select_key=f"{llm_provider}_model_select"
        )

        # 更新 session state 與持久化
        if st.session_state.llm_model != llm_model:
            logger.debug(f"模型變更: {st.session_state.llm_model} -> {llm_model}")
        st.session_state.llm_model = llm_model
        save_model_selection(
            st.session_state.llm_provider,
            st.session_state.get("model_category", "openai"),
            llm_model
        )

        # 進階設定
        with st.expander("進階設定"):
            enable_memory = st.checkbox(
                "啟用記憶功能",
                value=False,
                help="啟用記憶功能（可能影響效能）"
            )

            enable_debug = st.checkbox(
                "除錯模式",
                value=False,
                help="啟用詳細的除錯資訊輸出"
            )

            max_tokens = st.slider(
                "最大輸出長度",
                min_value=1000,
                max_value=8000,
                value=4000,
                step=500,
                help="模型的最大輸出 token 數量"
            )

        st.markdown("---")

        # API 密鑰狀態
        st.markdown("**API 狀態**")

        def _show_key_status(label: str, env_name: str, prefix: str = "", min_len: int = 20):
            """顯示 API 密鑰配置狀態（只顯示狀態，不洩露密鑰內容）"""
            key_val = os.getenv(env_name, "")
            if not key_val or key_val.startswith("your_") or key_val == "CHANGE_ME":
                st.error(f"{label}: 未配置")
            elif prefix and not key_val.startswith(prefix):
                st.warning(f"{label}: 已配置 (格式異常)")
            elif len(key_val) >= min_len:
                st.success(f"{label}: 已配置")
            else:
                st.warning(f"{label}: 已配置 (格式異常)")

        _show_key_status("OpenAI", "OPENAI_API_KEY", "sk-")
        _show_key_status("Anthropic", "ANTHROPIC_API_KEY", "sk-")
        _show_key_status("FinnHub", "FINNHUB_API_KEY")

        st.markdown("---")

        # 系統資訊
        st.caption(
            f"v{get_version()} | "
            f"{st.session_state.llm_provider.upper()} / {st.session_state.llm_model}"
        )

    # 回傳配置
    return {
        "llm_provider": st.session_state.llm_provider,
        "llm_model": st.session_state.llm_model,
        "enable_memory": enable_memory,
        "enable_debug": enable_debug,
        "max_tokens": max_tokens
    }
