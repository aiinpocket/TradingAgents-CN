#!/usr/bin/env python3
"""
配置管理頁面
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from tradingagents.config.config_manager import (
    config_manager, ModelConfig, PricingConfig
)


def render_config_management():
    """渲染配置管理頁面"""
    st.title("配置管理")

    # 顯示.env配置狀態
    render_env_status()

    # 側邊欄選擇功能
    st.sidebar.title("配置選項")
    page = st.sidebar.selectbox(
        "選擇功能",
        ["模型配置", "定價設定", "使用統計", "系統設定"]
    )
    
    if page == "模型配置":
        render_model_config()
    elif page == "定價設定":
        render_pricing_config()
    elif page == "使用統計":
        render_usage_statistics()
    elif page == "系統設定":
        render_system_settings()


def render_model_config():
    """渲染模型配置頁面"""
    st.markdown("**模型配置**")

    # 載入現有配置
    models = config_manager.load_models()

    # 顯示當前配置
    st.markdown("**當前模型配置**")
    
    if models:
        # 建立DataFrame顯示
        model_data = []
        env_status = config_manager.get_env_config_status()

        for i, model in enumerate(models):
            # 檢查API密鑰來源（只顯示狀態，不洩露密鑰內容）
            env_has_key = env_status["api_keys"].get(model.provider.lower(), False)
            if env_has_key:
                api_key_display = "已配置 (.env)"
            elif model.api_key:
                api_key_display = "已配置"
            else:
                api_key_display = "未設定"

            model_data.append({
                "序號": i,
                "供應商": model.provider,
                "模型名稱": model.model_name,
                "API密鑰": api_key_display,
                "最大Token": model.max_tokens,
                "溫度": model.temperature,
                "狀態": "啟用" if model.enabled else "禁用"
            })
        
        df = pd.DataFrame(model_data)
        st.dataframe(df, use_container_width=True)
        
        # 編輯模型參數（API密鑰不可修改）
        st.markdown("**編輯模型參數**")
        st.info(" **安全提示**: API密鑰只能透過 `.env` 檔案配置，無法在Web介面修改")

        # 選擇要編輯的模型
        model_options = [f"{m.provider} - {m.model_name}" for m in models]
        selected_model_idx = st.selectbox("選擇要編輯的模型", range(len(model_options)),
                                         format_func=lambda x: model_options[x],
                                         key="select_model_to_edit")

        if selected_model_idx is not None:
            model = models[selected_model_idx]

            # 檢查是否來自.env
            env_has_key = env_status["api_keys"].get(model.provider.lower(), False)

            # 顯示API密鑰狀態（只讀）
            if env_has_key:
                st.success(f"API密鑰: 已從 `.env` 檔案載入")
            elif model.api_key:
                st.warning(f"API密鑰: 使用舊配置（建議遷移到 `.env`）")
            else:
                st.error(f"API密鑰: 未配置（請在 `.env` 檔案中設定）")

            col1, col2 = st.columns(2)

            with col1:
                new_max_tokens = st.number_input("最大Token數", value=model.max_tokens, min_value=1000, max_value=32000, key=f"edit_max_tokens_{selected_model_idx}")
                new_temperature = st.slider("溫度參數", 0.0, 2.0, model.temperature, 0.1, key=f"edit_temperature_{selected_model_idx}")

            with col2:
                new_enabled = st.checkbox("啟用模型", value=model.enabled, key=f"edit_enabled_{selected_model_idx}")
                new_base_url = st.text_input("自訂 API 位址 (可選)", value=model.base_url or "", key=f"edit_base_url_{selected_model_idx}")

            if st.button("保存配置", type="primary", key=f"save_model_config_{selected_model_idx}"):
                # 更新模型配置（保留原API密鑰，不允許修改）
                models[selected_model_idx] = ModelConfig(
                    provider=model.provider,
                    model_name=model.model_name,
                    api_key=model.api_key,  # 保留原API密鑰
                    base_url=new_base_url if new_base_url else None,
                    max_tokens=new_max_tokens,
                    temperature=new_temperature,
                    enabled=new_enabled
                )

                config_manager.save_models(models)
                st.success("配置已保存！")
                st.rerun()
    
    else:
        st.warning("沒有找到模型配置")

    # 新增新模型的說明
    st.markdown("**新增新模型**")
    st.info("""
     **如何新增新模型：**

    為了安全起見，新模型的配置（包括API密鑰）只能透過 `.env` 檔案設定。

    **步驟：**
    1. 開啟專案根目錄的 `.env` 檔案
    2. 新增相應的API密鑰環境變數：
       - OpenAI: `OPENAI_API_KEY=your_key`
       - Anthropic: `ANTHROPIC_API_KEY=your_key`
    3. 重新啟動應用程式
    4. 系統會自動檢測並載入新配置的模型

    **注意**: Web 介面不支援直接新增新模型，這是為了保護您的 API 密鑰安全。
    """)


def render_pricing_config():
    """渲染定價配置頁面"""
    st.markdown("**定價設定**")

    # 載入現有定價
    pricing_configs = config_manager.load_pricing()

    # 顯示當前定價
    st.markdown("**當前定價配置**")
    
    if pricing_configs:
        pricing_data = []
        for i, pricing in enumerate(pricing_configs):
            pricing_data.append({
                "序號": i,
                "供應商": pricing.provider,
                "模型名稱": pricing.model_name,
                "輸入價格 (每1K token)": f"{pricing.input_price_per_1k} {pricing.currency}",
                "輸出價格 (每1K token)": f"{pricing.output_price_per_1k} {pricing.currency}",
                "貨幣": pricing.currency
            })
        
        df = pd.DataFrame(pricing_data)
        st.dataframe(df, use_container_width=True)
        
        # 編輯定價
        st.markdown("**編輯定價**")
        
        pricing_options = [f"{p.provider} - {p.model_name}" for p in pricing_configs]
        selected_pricing_idx = st.selectbox("選擇要編輯的定價", range(len(pricing_options)),
                                          format_func=lambda x: pricing_options[x],
                                          key="select_pricing_to_edit")
        
        if selected_pricing_idx is not None:
            pricing = pricing_configs[selected_pricing_idx]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_input_price = st.number_input("輸入價格 (每1K token)",
                                                value=pricing.input_price_per_1k,
                                                min_value=0.0, step=0.001, format="%.6f",
                                                key=f"edit_input_price_{selected_pricing_idx}")

            with col2:
                new_output_price = st.number_input("輸出價格 (每1K token)",
                                                 value=pricing.output_price_per_1k,
                                                 min_value=0.0, step=0.001, format="%.6f",
                                                 key=f"edit_output_price_{selected_pricing_idx}")

            with col3:
                new_currency = st.selectbox("貨幣", ["USD", "EUR"],
                                          index=["USD", "EUR"].index(pricing.currency) if pricing.currency in ["USD", "EUR"] else 0,
                                          key=f"edit_currency_{selected_pricing_idx}")
            
            if st.button("保存定價", type="primary", key=f"save_pricing_config_{selected_pricing_idx}"):
                pricing_configs[selected_pricing_idx] = PricingConfig(
                    provider=pricing.provider,
                    model_name=pricing.model_name,
                    input_price_per_1k=new_input_price,
                    output_price_per_1k=new_output_price,
                    currency=new_currency
                )
                
                config_manager.save_pricing(pricing_configs)
                st.success("定價已保存！")
                st.rerun()
    
    # 新增新定價
    st.markdown("**新增新定價**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_provider = st.text_input("供應商", placeholder="例如: openai, anthropic", key="new_pricing_provider")
        new_model_name = st.text_input("模型名稱", placeholder="例如: gpt-4o, claude-sonnet-4-6", key="new_pricing_model")
        new_currency = st.selectbox("貨幣", ["USD", "EUR"], key="new_pricing_currency")

    with col2:
        new_input_price = st.number_input("輸入價格 (每1K token)", min_value=0.0, step=0.001, format="%.6f", key="new_pricing_input")
        new_output_price = st.number_input("輸出價格 (每1K token)", min_value=0.0, step=0.001, format="%.6f", key="new_pricing_output")
    
    if st.button("新增定價", key="add_new_pricing"):
        if new_provider and new_model_name:
            new_pricing = PricingConfig(
                provider=new_provider,
                model_name=new_model_name,
                input_price_per_1k=new_input_price,
                output_price_per_1k=new_output_price,
                currency=new_currency
            )
            
            pricing_configs.append(new_pricing)
            config_manager.save_pricing(pricing_configs)
            st.success("新定價已新增！")
            st.rerun()
        else:
            st.error("請填寫供應商和模型名稱")


def render_usage_statistics():
    """渲染使用統計頁面"""
    st.markdown("**使用統計**")

    # 時間範圍選擇
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("統計時間範圍", [7, 30, 90, 365], index=1, key="stats_time_range")
    with col2:
        st.metric("統計週期", f"最近 {days} 天")

    # 取得統計資料
    stats = config_manager.get_usage_statistics(days)

    if stats["total_requests"] == 0:
        st.info("暫無使用記錄")
        return

    # 總體統計
    st.markdown("**總體統計**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("總成本", f"${stats['total_cost']:.4f}")
    
    with col2:
        st.metric("總請求數", f"{stats['total_requests']:,}")
    
    with col3:
        st.metric("輸入Token", f"{stats['total_input_tokens']:,}")
    
    with col4:
        st.metric("輸出Token", f"{stats['total_output_tokens']:,}")
    
    # 按供應商統計
    if stats["provider_stats"]:
        st.markdown("**按供應商統計**")
        
        provider_data = []
        for provider, data in stats["provider_stats"].items():
            provider_data.append({
                "供應商": provider,
                "成本": f"${data['cost']:.4f}",
                "請求數": data['requests'],
                "輸入Token": f"{data['input_tokens']:,}",
                "輸出Token": f"{data['output_tokens']:,}",
                "平均成本/請求": f"${data['cost']/data['requests']:.6f}" if data['requests'] > 0 else "$0"
            })
        
        df = pd.DataFrame(provider_data)
        st.dataframe(df, use_container_width=True)
        
        # 成本分布餅圖
        if len(provider_data) > 1:
            fig = px.pie(
                values=[stats["provider_stats"][p]["cost"] for p in stats["provider_stats"]],
                names=list(stats["provider_stats"].keys()),
                title="成本分布"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 使用趨勢
    st.markdown("**使用趨勢**")
    
    records = config_manager.load_usage_records()
    if records:
        # 按日期聚合
        daily_stats = {}
        for record in records:
            try:
                date = datetime.fromisoformat(record.timestamp).date()
                if date not in daily_stats:
                    daily_stats[date] = {"cost": 0, "requests": 0}
                daily_stats[date]["cost"] += record.cost
                daily_stats[date]["requests"] += 1
            except Exception as e:
                continue
        
        if daily_stats:
            dates = sorted(daily_stats.keys())
            costs = [daily_stats[date]["cost"] for date in dates]
            requests = [daily_stats[date]["requests"] for date in dates]
            
            # 建立雙軸圖表
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=costs,
                mode='lines+markers',
                name='每日成本 ($)',
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=requests,
                mode='lines+markers',
                name='每日請求數',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='使用趨勢',
                xaxis_title='日期',
                yaxis=dict(title='成本 ($)', side='left'),
                yaxis2=dict(title='請求數', side='right', overlaying='y'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)


def render_system_settings():
    """渲染系統設定頁面"""
    st.markdown("**系統設定**")

    # 載入當前設定
    settings = config_manager.load_settings()

    st.markdown("**基本設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        providers = ["openai", "anthropic"]
        default_provider_value = settings.get("default_provider", "openai")
        # 確保預設值在選項中
        if default_provider_value not in providers:
            default_provider_value = "openai"

        default_provider = st.selectbox(
            "預設供應商",
            providers,
            index=providers.index(default_provider_value),
            key="settings_default_provider"
        )

        enable_cost_tracking = st.checkbox(
            "啟用成本追蹤",
            value=settings.get("enable_cost_tracking", True),
            key="settings_enable_cost_tracking"
        )

        currency_preference = st.selectbox(
            "首選貨幣",
            ["USD", "EUR"],
            index=["USD", "EUR"].index(
                settings.get("currency_preference", "USD")
            ) if settings.get("currency_preference", "USD") in ["USD", "EUR"] else 0,
            key="settings_currency_preference"
        )
    
    with col2:
        default_model = st.text_input(
            "預設模型",
            value=settings.get("default_model", "gpt-4o-mini"),
            key="settings_default_model"
        )

        cost_alert_threshold = st.number_input(
            "成本警告門檻",
            value=settings.get("cost_alert_threshold", 100.0),
            min_value=0.0,
            step=10.0,
            key="settings_cost_alert_threshold"
        )

        max_usage_records = st.number_input(
            "最大使用記錄數",
            value=settings.get("max_usage_records", 10000),
            min_value=1000,
            max_value=100000,
            step=1000,
            key="settings_max_usage_records"
        )

    auto_save_usage = st.checkbox(
        "自動保存使用記錄",
        value=settings.get("auto_save_usage", True),
        key="settings_auto_save_usage"
    )
    
    if st.button("保存設定", type="primary", key="save_system_settings"):
        new_settings = {
            "default_provider": default_provider,
            "default_model": default_model,
            "enable_cost_tracking": enable_cost_tracking,
            "cost_alert_threshold": cost_alert_threshold,
            "currency_preference": currency_preference,
            "auto_save_usage": auto_save_usage,
            "max_usage_records": max_usage_records
        }
        
        config_manager.save_settings(new_settings)
        st.success("設定已保存！")
        st.rerun()
    
    # 資料管理
    st.markdown("**資料管理**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("匯出配置", help="匯出所有配置到JSON 檔案", key="export_config"):
            # 這裡可以實作配置匯出功能
            st.info("配置匯出功能開發中...")
    
    with col2:
        if st.button("清空使用記錄", help="清空所有使用記錄", key="clear_usage_records"):
            if st.session_state.get("confirm_clear", False):
                config_manager.save_usage_records([])
                st.success("使用記錄已清空！")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("再次點擊確認清空")
    
    with col3:
        if st.button("重置配置", help="重置所有配置到預設值", key="reset_all_config"):
            if st.session_state.get("confirm_reset", False):
                # 刪除配置檔，重新初始化
                import shutil
                if config_manager.config_dir.exists():
                    shutil.rmtree(config_manager.config_dir)
                config_manager._init_default_configs()
                st.success("配置已重置！")
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("再次點擊確認重置")


def render_env_status():
    """顯示.env配置狀態"""
    st.markdown("**配置狀態概覽**")

    # 取得.env配置狀態
    env_status = config_manager.get_env_config_status()

    # 顯示.env 檔案狀態
    col1, col2 = st.columns(2)

    with col1:
        if env_status["env_file_exists"]:
            st.success(" .env 檔案已存在")
        else:
            st.error(" .env 檔案不存在")
            st.info("請複製 .env.example 為 .env 並配置API密鑰")

    with col2:
        # 統計已配置的API密鑰數量
        configured_keys = sum(1 for configured in env_status["api_keys"].values() if configured)
        total_keys = len(env_status["api_keys"])
        st.metric("API密鑰配置", f"{configured_keys}/{total_keys}")

    # 詳細API密鑰狀態
    with st.expander("API密鑰詳細狀態", expanded=False):
        api_col1, api_col2 = st.columns(2)

        with api_col1:
            st.write("**大模型API密鑰:**")
            for provider, configured in env_status["api_keys"].items():
                if provider in ["openai", "anthropic"]:
                    status = "已配置" if configured else "未配置"
                    provider_name = {
                        "openai": "OpenAI",
                        "anthropic": "Anthropic"
                    }.get(provider, provider)
                    st.write(f"- {provider_name}: {status}")

        with api_col2:
            st.write("**其他API密鑰:**")
            finnhub_status = "已配置" if env_status["api_keys"]["finnhub"] else "未配置"
            st.write(f"- FinnHub (金融資料): {finnhub_status}")

    # 配置優先級說明
    st.info("""
     **配置優先級說明:**
    - API密鑰優先從 `.env` 檔案讀取
    - Web介面配置作為補充和管理工具
    - 修改 `.env` 檔案後需重啟應用生效
    - 推薦使用 `.env` 檔案管理敏感資訊
    """)

    st.divider()


if __name__ == "__main__":
    st.set_page_config(
        page_title="配置管理 - TradingAgents",
        page_icon=None,
        layout="wide"
    )
    render_config_management()
