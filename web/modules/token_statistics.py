#!/usr/bin/env python3
"""
Token使用統計頁面

展示Token使用情況、成本分析和統計圖表
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any

# 添加項目根目錄到路徑
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 導入UI工具函數
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.ui_utils import apply_hide_deploy_button_css

from tradingagents.config.config_manager import config_manager, token_tracker, UsageRecord

def render_token_statistics():
    """渲染Token統計頁面"""
    # 應用隱藏Deploy按鈕的CSS樣式
    apply_hide_deploy_button_css()
    
    st.markdown("**💰 Token使用統計與成本分析**")
    
    # 側邊欄控制
    with st.sidebar:
        st.subheader("📊 統計設置")
        
        # 時間範圍選擇
        time_range = st.selectbox(
            "統計時間範圍",
            ["今天", "最近7天", "最近30天", "最近90天", "全部"],
            index=2
        )
        
        # 轉換為天數
        days_map = {
            "今天": 1,
            "最近7天": 7,
            "最近30天": 30,
            "最近90天": 90,
            "全部": 365  # 使用一年作為"全部"
        }
        days = days_map[time_range]
        
        # 刷新按鈕
        if st.button("🔄 刷新數據", use_container_width=True):
            st.rerun()
        
        # 導出數據按鈕
        if st.button("📥 導出統計數據", use_container_width=True):
            export_statistics_data(days)
    
    # 獲取統計數據
    try:
        stats = config_manager.get_usage_statistics(days)
        records = load_detailed_records(days)
        
        if not stats or stats.get('total_requests', 0) == 0:
            st.info(f"📊 {time_range}內暫無Token使用記錄")
            st.markdown("""
            ### 💡 如何開始記錄Token使用？
            
            1. **進行股票分析**: 使用主頁面的股票分析功能
            2. **確保API配置**: 檢查 LLM API 密鑰是否已在 .env 檔案中正確配置
            3. **啟用成本跟蹤**: 在配置管理中啟用Token成本跟蹤
            
            系統會自動記錄所有LLM調用的Token使用情況。
            """)
            return
        
        # 顯示概覽統計
        render_overview_metrics(stats, time_range)
        
        # 顯示詳細圖表
        if records:
            render_detailed_charts(records, stats)
        
        # 顯示供應商統計
        render_provider_statistics(stats)
        
        # 顯示成本趨勢
        if records:
            render_cost_trends(records)
        
        # 顯示詳細記錄表
        render_detailed_records_table(records)
        
    except Exception as e:
        st.error(f"❌ 獲取統計數據失敗: {str(e)}")
        st.info("請檢查配置文件和數據儲存是否正常")

def render_overview_metrics(stats: Dict[str, Any], time_range: str):
    """渲染概覽指標"""
    st.markdown(f"**📈 {time_range}概覽**")
    
    # 創建指標卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 總成本",
            value=f"¥{stats['total_cost']:.4f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="🔢 總調用次數",
            value=f"{stats['total_requests']:,}",
            delta=None
        )
    
    with col3:
        total_tokens = stats['total_input_tokens'] + stats['total_output_tokens']
        st.metric(
            label="📊 總Token數",
            value=f"{total_tokens:,}",
            delta=None
        )
    
    with col4:
        avg_cost = stats['total_cost'] / stats['total_requests'] if stats['total_requests'] > 0 else 0
        st.metric(
            label="📊 平均每次成本",
            value=f"¥{avg_cost:.4f}",
            delta=None
        )
    
    # Token使用分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="📥 輸入Token",
            value=f"{stats['total_input_tokens']:,}",
            delta=f"{stats['total_input_tokens']/(stats['total_input_tokens']+stats['total_output_tokens'])*100:.1f}%"
        )
    
    with col2:
        st.metric(
            label="📤 輸出Token",
            value=f"{stats['total_output_tokens']:,}",
            delta=f"{stats['total_output_tokens']/(stats['total_input_tokens']+stats['total_output_tokens'])*100:.1f}%"
        )

def render_detailed_charts(records: List[UsageRecord], stats: Dict[str, Any]):
    """渲染詳細圖表"""
    st.markdown("**📊 詳細分析圖表**")
    
    # Token使用分布饼圖
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🥧 Token使用分布**")
        
        # 創建饼圖數據
        token_data = {
            'Token類型': ['輸入Token', '輸出Token'],
            '數量': [stats['total_input_tokens'], stats['total_output_tokens']]
        }
        
        fig_pie = px.pie(
            values=token_data['數量'],
            names=token_data['Token類型'],
            title="Token使用分布",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("**📈 成本vs Token關系**")
        
        # 創建散點圖
        df_records = pd.DataFrame([
            {
                'total_tokens': record.input_tokens + record.output_tokens,
                'cost': record.cost,
                'provider': record.provider,
                'model': record.model_name
            }
            for record in records
        ])
        
        if not df_records.empty:
            fig_scatter = px.scatter(
                df_records,
                x='total_tokens',
                y='cost',
                color='provider',
                hover_data=['model'],
                title="成本與Token使用量關系",
                labels={'total_tokens': 'Token總數', 'cost': '成本(¥)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

def render_provider_statistics(stats: Dict[str, Any]):
    """渲染供應商統計"""
    st.markdown("**🏢 供應商統計**")
    
    provider_stats = stats.get('provider_stats', {})
    
    if not provider_stats:
        st.info("暫無供應商統計數據")
        return
    
    # 創建供應商對比表
    provider_df = pd.DataFrame([
        {
            '供應商': provider,
            '成本(¥)': f"{data['cost']:.4f}",
            '調用次數': data['requests'],
            '輸入Token': f"{data['input_tokens']:,}",
            '輸出Token': f"{data['output_tokens']:,}",
            '平均成本(¥)': f"{data['cost']/data['requests']:.4f}" if data['requests'] > 0 else "0.0000"
        }
        for provider, data in provider_stats.items()
    ])
    
    st.dataframe(provider_df, use_container_width=True)
    
    # 供應商成本對比圖
    col1, col2 = st.columns(2)
    
    with col1:
        # 成本對比柱狀圖
        cost_data = {provider: data['cost'] for provider, data in provider_stats.items()}
        fig_bar = px.bar(
            x=list(cost_data.keys()),
            y=list(cost_data.values()),
            title="各供應商成本對比",
            labels={'x': '供應商', 'y': '成本(¥)'},
            color=list(cost_data.values()),
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # 調用次數對比
        requests_data = {provider: data['requests'] for provider, data in provider_stats.items()}
        fig_requests = px.bar(
            x=list(requests_data.keys()),
            y=list(requests_data.values()),
            title="各供應商調用次數對比",
            labels={'x': '供應商', 'y': '調用次數'},
            color=list(requests_data.values()),
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig_requests, use_container_width=True)

def render_cost_trends(records: List[UsageRecord]):
    """渲染成本趨勢圖"""
    st.markdown("**📈 成本趨勢分析**")
    
    # 按日期聚合數據
    df_records = pd.DataFrame([
        {
            'date': datetime.fromisoformat(record.timestamp).date(),
            'cost': record.cost,
            'tokens': record.input_tokens + record.output_tokens,
            'provider': record.provider
        }
        for record in records
    ])
    
    if df_records.empty:
        st.info("暫無趨勢數據")
        return
    
    # 按日期聚合
    daily_stats = df_records.groupby('date').agg({
        'cost': 'sum',
        'tokens': 'sum'
    }).reset_index()
    
    # 創建雙轴圖表
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        subplot_titles=["每日成本和Token使用趨勢"]
    )
    
    # 添加成本趨勢線
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['cost'],
            mode='lines+markers',
            name='每日成本(¥)',
            line=dict(color='#FF6B6B', width=3)
        ),
        secondary_y=False,
    )
    
    # 添加Token使用趨勢線
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['tokens'],
            mode='lines+markers',
            name='每日Token數',
            line=dict(color='#4ECDC4', width=3)
        ),
        secondary_y=True,
    )
    
    # 設置轴標簽
    fig.update_xaxes(title_text="日期")
    fig.update_yaxes(title_text="成本(¥)", secondary_y=False)
    fig.update_yaxes(title_text="Token數量", secondary_y=True)
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def render_detailed_records_table(records: List[UsageRecord]):
    """渲染詳細記錄表"""
    st.markdown("**📋 詳細使用記錄**")
    
    if not records:
        st.info("暫無詳細記錄")
        return
    
    # 創建記錄表格
    records_df = pd.DataFrame([
        {
            '時間': datetime.fromisoformat(record.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            '供應商': record.provider,
            '模型': record.model_name,
            '輸入Token': record.input_tokens,
            '輸出Token': record.output_tokens,
            '總Token': record.input_tokens + record.output_tokens,
            '成本(¥)': f"{record.cost:.4f}",
            '會話ID': record.session_id[:12] + '...' if len(record.session_id) > 12 else record.session_id,
            '分析類型': record.analysis_type
        }
        for record in sorted(records, key=lambda x: x.timestamp, reverse=True)
    ])
    
    # 分页顯示
    page_size = 20
    total_records = len(records_df)
    total_pages = (total_records + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.selectbox(f"頁面 (共{total_pages}页, {total_records}條記錄)", range(1, total_pages + 1))
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_records)
        display_df = records_df.iloc[start_idx:end_idx]
    else:
        display_df = records_df
    
    st.dataframe(display_df, use_container_width=True)

def load_detailed_records(days: int) -> List[UsageRecord]:
    """加載詳細記錄"""
    try:
        all_records = config_manager.load_usage_records()
        
        # 過濾時間範圍
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_records = []
        
        for record in all_records:
            try:
                record_date = datetime.fromisoformat(record.timestamp)
                if record_date >= cutoff_date:
                    filtered_records.append(record)
            except:
                continue
        
        return filtered_records
    except Exception as e:
        st.error(f"加載記錄失敗: {e}")
        return []

def export_statistics_data(days: int):
    """導出統計數據"""
    try:
        stats = config_manager.get_usage_statistics(days)
        records = load_detailed_records(days)
        
        # 創建導出數據
        export_data = {
            'summary': stats,
            'detailed_records': [
                {
                    'timestamp': record.timestamp,
                    'provider': record.provider,
                    'model_name': record.model_name,
                    'input_tokens': record.input_tokens,
                    'output_tokens': record.output_tokens,
                    'cost': record.cost,
                    'session_id': record.session_id,
                    'analysis_type': record.analysis_type
                }
                for record in records
            ]
        }
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"token_statistics_{timestamp}.json"
        
        # 提供下載
        st.download_button(
            label="📥 下載統計數據",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=filename,
            mime="application/json"
        )
        
        st.success(f"✅ 統計數據已準備好下載: {filename}")
        
    except Exception as e:
        st.error(f"❌ 導出失敗: {str(e)}")

def main():
    """主函數"""
    st.set_page_config(
        page_title="Token統計 - TradingAgents",
        page_icon="💰",
        layout="wide"
    )
    
    render_token_statistics()

if __name__ == "__main__":
    main()