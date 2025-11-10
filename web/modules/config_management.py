#!/usr/bin/env python3
"""
配置管理页面
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List

# 添加項目根目錄到路徑
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 導入UI工具函數
sys.path.append(str(Path(__file__).parent.parent))
from utils.ui_utils import apply_hide_deploy_button_css

from tradingagents.config.config_manager import (
    config_manager, ModelConfig, PricingConfig
)


def render_config_management():
    """渲染配置管理页面"""
    # 應用隐藏Deploy按钮的CSS樣式
    apply_hide_deploy_button_css()
    
    st.title("⚙️ 配置管理")

    # 顯示.env配置狀態
    render_env_status()

    # 侧邊栏選擇功能
    st.sidebar.title("配置選項")
    page = st.sidebar.selectbox(
        "選擇功能",
        ["模型配置", "定價設置", "使用統計", "系統設置"]
    )
    
    if page == "模型配置":
        render_model_config()
    elif page == "定價設置":
        render_pricing_config()
    elif page == "使用統計":
        render_usage_statistics()
    elif page == "系統設置":
        render_system_settings()


def render_model_config():
    """渲染模型配置页面"""
    st.markdown("**🤖 模型配置**")

    # 加載現有配置
    models = config_manager.load_models()

    # 顯示當前配置
    st.markdown("**當前模型配置**")
    
    if models:
        # 創建DataFrame顯示
        model_data = []
        env_status = config_manager.get_env_config_status()

        for i, model in enumerate(models):
            # 檢查API密鑰來源
            env_has_key = env_status["api_keys"].get(model.provider.lower(), False)
            api_key_display = "***" + model.api_key[-4:] if model.api_key else "未設置"
            if env_has_key:
                api_key_display += " (.env)"

            model_data.append({
                "序號": i,
                "供應商": model.provider,
                "模型名稱": model.model_name,
                "API密鑰": api_key_display,
                "最大Token": model.max_tokens,
                "溫度": model.temperature,
                "狀態": "✅ 啟用" if model.enabled else "❌ 禁用"
            })
        
        df = pd.DataFrame(model_data)
        st.dataframe(df, use_container_width=True)
        
        # 編辑模型配置
        st.markdown("**編辑模型配置**")
        
        # 選擇要編辑的模型
        model_options = [f"{m.provider} - {m.model_name}" for m in models]
        selected_model_idx = st.selectbox("選擇要編辑的模型", range(len(model_options)),
                                         format_func=lambda x: model_options[x],
                                         key="select_model_to_edit")
        
        if selected_model_idx is not None:
            model = models[selected_model_idx]

            # 檢查是否來自.env
            env_has_key = env_status["api_keys"].get(model.provider.lower(), False)
            if env_has_key:
                st.info(f"💡 此模型的API密鑰來自 .env 文件，修改 .env 文件後需重啟應用生效")

            col1, col2 = st.columns(2)

            with col1:
                new_api_key = st.text_input("API密鑰", value=model.api_key, type="password", key=f"edit_api_key_{selected_model_idx}")
                if env_has_key:
                    st.caption("⚠️ 此密鑰來自 .env 文件，Web修改可能被覆蓋")
                new_max_tokens = st.number_input("最大Token數", value=model.max_tokens, min_value=1000, max_value=32000, key=f"edit_max_tokens_{selected_model_idx}")
                new_temperature = st.slider("溫度參數", 0.0, 2.0, model.temperature, 0.1, key=f"edit_temperature_{selected_model_idx}")

            with col2:
                new_enabled = st.checkbox("啟用模型", value=model.enabled, key=f"edit_enabled_{selected_model_idx}")
                new_base_url = st.text_input("自定義API地址 (可選)", value=model.base_url or "", key=f"edit_base_url_{selected_model_idx}")
            
            if st.button("保存配置", type="primary", key=f"save_model_config_{selected_model_idx}"):
                # 更新模型配置
                models[selected_model_idx] = ModelConfig(
                    provider=model.provider,
                    model_name=model.model_name,
                    api_key=new_api_key,
                    base_url=new_base_url if new_base_url else None,
                    max_tokens=new_max_tokens,
                    temperature=new_temperature,
                    enabled=new_enabled
                )
                
                config_manager.save_models(models)
                st.success("✅ 配置已保存！")
                st.rerun()
    
    else:
        st.warning("没有找到模型配置")
    
    # 添加新模型
    st.markdown("**添加新模型**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_provider = st.selectbox("供應商", ["openai", "google", "anthropic", "other"], key="new_provider")
        new_model_name = st.text_input("模型名稱", placeholder="例如: gpt-4, gemini-2.5-pro", key="new_model_name")
        new_api_key = st.text_input("API密鑰", type="password", key="new_api_key")

    with col2:
        new_max_tokens = st.number_input("最大Token數", value=4000, min_value=1000, max_value=32000, key="new_max_tokens")
        new_temperature = st.slider("溫度參數", 0.0, 2.0, 0.7, 0.1, key="new_temperature")
        new_enabled = st.checkbox("啟用模型", value=True, key="new_enabled")
    
    if st.button("添加模型", key="add_new_model"):
        if new_provider and new_model_name and new_api_key:
            new_model = ModelConfig(
                provider=new_provider,
                model_name=new_model_name,
                api_key=new_api_key,
                max_tokens=new_max_tokens,
                temperature=new_temperature,
                enabled=new_enabled
            )
            
            models.append(new_model)
            config_manager.save_models(models)
            st.success("✅ 新模型已添加！")
            st.rerun()
        else:
            st.error("請填寫所有必需字段")


def render_pricing_config():
    """渲染定價配置页面"""
    st.markdown("**💰 定價設置**")

    # 加載現有定價
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
                "貨币": pricing.currency
            })
        
        df = pd.DataFrame(pricing_data)
        st.dataframe(df, use_container_width=True)
        
        # 編辑定價
        st.markdown("**編辑定價**")
        
        pricing_options = [f"{p.provider} - {p.model_name}" for p in pricing_configs]
        selected_pricing_idx = st.selectbox("選擇要編辑的定價", range(len(pricing_options)),
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
                new_currency = st.selectbox("貨币", ["CNY", "USD", "EUR"],
                                          index=["CNY", "USD", "EUR"].index(pricing.currency),
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
                st.success("✅ 定價已保存！")
                st.rerun()
    
    # 添加新定價
    st.markdown("**添加新定價**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_provider = st.text_input("供應商", placeholder="例如: openai, google, anthropic", key="new_pricing_provider")
        new_model_name = st.text_input("模型名稱", placeholder="例如: gpt-4, gemini-2.5-pro", key="new_pricing_model")
        new_currency = st.selectbox("貨币", ["CNY", "USD", "EUR"], key="new_pricing_currency")

    with col2:
        new_input_price = st.number_input("輸入價格 (每1K token)", min_value=0.0, step=0.001, format="%.6f", key="new_pricing_input")
        new_output_price = st.number_input("輸出價格 (每1K token)", min_value=0.0, step=0.001, format="%.6f", key="new_pricing_output")
    
    if st.button("添加定價", key="add_new_pricing"):
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
            st.success("✅ 新定價已添加！")
            st.rerun()
        else:
            st.error("請填寫供應商和模型名稱")


def render_usage_statistics():
    """渲染使用統計页面"""
    st.markdown("**📊 使用統計**")

    # 時間範围選擇
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("統計時間範围", [7, 30, 90, 365], index=1, key="stats_time_range")
    with col2:
        st.metric("統計周期", f"最近 {days} 天")

    # 獲取統計數據
    stats = config_manager.get_usage_statistics(days)

    if stats["total_requests"] == 0:
        st.info("📝 暂無使用記錄")
        return

    # 总體統計
    st.markdown("**📈 总體統計**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总成本", f"¥{stats['total_cost']:.4f}")
    
    with col2:
        st.metric("总請求數", f"{stats['total_requests']:,}")
    
    with col3:
        st.metric("輸入Token", f"{stats['total_input_tokens']:,}")
    
    with col4:
        st.metric("輸出Token", f"{stats['total_output_tokens']:,}")
    
    # 按供應商統計
    if stats["provider_stats"]:
        st.markdown("**🏢 按供應商統計**")
        
        provider_data = []
        for provider, data in stats["provider_stats"].items():
            provider_data.append({
                "供應商": provider,
                "成本": f"¥{data['cost']:.4f}",
                "請求數": data['requests'],
                "輸入Token": f"{data['input_tokens']:,}",
                "輸出Token": f"{data['output_tokens']:,}",
                "平均成本/請求": f"¥{data['cost']/data['requests']:.6f}" if data['requests'] > 0 else "¥0"
            })
        
        df = pd.DataFrame(provider_data)
        st.dataframe(df, use_container_width=True)
        
        # 成本分布饼圖
        if len(provider_data) > 1:
            fig = px.pie(
                values=[stats["provider_stats"][p]["cost"] for p in stats["provider_stats"]],
                names=list(stats["provider_stats"].keys()),
                title="成本分布"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 使用趋势
    st.markdown("**📈 使用趋势**")
    
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
            except:
                continue
        
        if daily_stats:
            dates = sorted(daily_stats.keys())
            costs = [daily_stats[date]["cost"] for date in dates]
            requests = [daily_stats[date]["requests"] for date in dates]
            
            # 創建雙轴圖表
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=costs,
                mode='lines+markers',
                name='每日成本 (¥)',
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=requests,
                mode='lines+markers',
                name='每日請求數',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='使用趋势',
                xaxis_title='日期',
                yaxis=dict(title='成本 (¥)', side='left'),
                yaxis2=dict(title='請求數', side='right', overlaying='y'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)


def render_system_settings():
    """渲染系統設置页面"""
    st.markdown("**🔧 系統設置**")

    # 加載當前設置
    settings = config_manager.load_settings()

    st.markdown("**基本設置**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        providers = ["openai", "google", "anthropic"]
        default_provider_value = settings.get("default_provider", "openai")
        # 確保預設值在選項中
        if default_provider_value not in providers:
            default_provider_value = "openai"

        default_provider = st.selectbox(
            "默認供應商",
            providers,
            index=providers.index(default_provider_value),
            key="settings_default_provider"
        )

        enable_cost_tracking = st.checkbox(
            "啟用成本跟蹤",
            value=settings.get("enable_cost_tracking", True),
            key="settings_enable_cost_tracking"
        )

        currency_preference = st.selectbox(
            "首選貨币",
            ["CNY", "USD", "EUR"],
            index=["CNY", "USD", "EUR"].index(
                settings.get("currency_preference", "CNY")
            ),
            key="settings_currency_preference"
        )
    
    with col2:
        default_model = st.text_input(
            "默認模型",
            value=settings.get("default_model", "qwen-turbo"),
            key="settings_default_model"
        )

        cost_alert_threshold = st.number_input(
            "成本警告阈值",
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
    
    if st.button("保存設置", type="primary", key="save_system_settings"):
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
        st.success("✅ 設置已保存！")
        st.rerun()
    
    # 數據管理
    st.markdown("**數據管理**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("導出配置", help="導出所有配置到JSON文件", key="export_config"):
            # 這里可以實現配置導出功能
            st.info("配置導出功能開發中...")
    
    with col2:
        if st.button("清空使用記錄", help="清空所有使用記錄", key="clear_usage_records"):
            if st.session_state.get("confirm_clear", False):
                config_manager.save_usage_records([])
                st.success("✅ 使用記錄已清空！")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ 再次點擊確認清空")
    
    with col3:
        if st.button("重置配置", help="重置所有配置到默認值", key="reset_all_config"):
            if st.session_state.get("confirm_reset", False):
                # 刪除配置文件，重新初始化
                import shutil
                if config_manager.config_dir.exists():
                    shutil.rmtree(config_manager.config_dir)
                config_manager._init_default_configs()
                st.success("✅ 配置已重置！")
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ 再次點擊確認重置")


def render_env_status():
    """顯示.env配置狀態"""
    st.markdown("**📋 配置狀態概覽**")

    # 獲取.env配置狀態
    env_status = config_manager.get_env_config_status()

    # 顯示.env文件狀態
    col1, col2 = st.columns(2)

    with col1:
        if env_status["env_file_exists"]:
            st.success("✅ .env 文件已存在")
        else:
            st.error("❌ .env 文件不存在")
            st.info("💡 請複制 .env.example 為 .env 並配置API密鑰")

    with col2:
        # 統計已配置的API密鑰數量
        configured_keys = sum(1 for configured in env_status["api_keys"].values() if configured)
        total_keys = len(env_status["api_keys"])
        st.metric("API密鑰配置", f"{configured_keys}/{total_keys}")

    # 詳細API密鑰狀態
    with st.expander("🔑 API密鑰詳細狀態", expanded=False):
        api_col1, api_col2 = st.columns(2)

        with api_col1:
            st.write("**大模型API密鑰:**")
            for provider, configured in env_status["api_keys"].items():
                if provider in ["openai", "google", "anthropic"]:
                    status = "✅ 已配置" if configured else "❌ 未配置"
                    provider_name = {
                        "openai": "OpenAI",
                        "google": "Google AI",
                        "anthropic": "Anthropic"
                    }.get(provider, provider)
                    st.write(f"- {provider_name}: {status}")

        with api_col2:
            st.write("**其他API密鑰:**")
            finnhub_status = "✅ 已配置" if env_status["api_keys"]["finnhub"] else "❌ 未配置"
            st.write(f"- FinnHub (金融數據): {finnhub_status}")

            reddit_status = "✅ 已配置" if env_status["other_configs"]["reddit_configured"] else "❌ 未配置"
            st.write(f"- Reddit API: {reddit_status}")

    # 配置優先級說明
    st.info("""
    📌 **配置優先級說明:**
    - API密鑰優先從 `.env` 文件讀取
    - Web界面配置作為補充和管理工具
    - 修改 `.env` 文件後需重啟應用生效
    - 推薦使用 `.env` 文件管理敏感信息
    """)

    st.divider()


def main():
    """主函數"""
    st.set_page_config(
        page_title="配置管理 - TradingAgents",
        page_icon="⚙️",
        layout="wide"
    )
    
    render_config_management()

if __name__ == "__main__":
    main()
