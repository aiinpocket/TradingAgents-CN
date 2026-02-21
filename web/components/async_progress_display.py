#!/usr/bin/env python3
"""
非同步進度顯示元件
從 Redis 或檔案取得進度狀態，使用非阻塞式自動重新整理
"""

import streamlit as st
import time

from web.utils.async_progress_tracker import format_time

from tradingagents.utils.logging_manager import get_logger
logger = get_logger('async_display')

# 自動重新整理間隔（秒）
AUTO_REFRESH_INTERVAL = 3


def display_unified_progress(analysis_id: str, show_refresh_controls: bool = True) -> bool:
    """
    統一的進度顯示函式
    返回 True 表示分析已完成/失敗，False 表示仍在進行中
    """
    from web.utils.async_progress_tracker import get_progress_by_id

    progress_data = get_progress_by_id(analysis_id)

    # 無進度資料時顯示初始狀態
    if not progress_data:
        st.info("**當前狀態**: 準備開始分析...")
        _render_refresh_controls(analysis_id, 'initializing', show_refresh_controls)
        return False

    # 解析進度資料
    status = progress_data.get('status', 'running')
    current_step = progress_data.get('current_step', 0)
    current_step_name = progress_data.get('current_step_name', '準備階段')
    progress_percentage = progress_data.get('progress_percentage', 0.0)
    current_step_description = progress_data.get('current_step_description', '初始化分析引擎')
    last_message = progress_data.get('last_message', '準備開始分析')

    # 計算已用時間
    elapsed_time = _calculate_elapsed_time(progress_data, status)
    estimated_total_time = progress_data.get('estimated_total_time', 0)
    remaining_time = max(estimated_total_time - elapsed_time, 0)

    # 渲染進度 UI
    st.write(f"**當前步驟**: {current_step_name}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("進度", f"{progress_percentage:.1f}%")
    with col2:
        st.metric("已用時間", format_time(elapsed_time))
    with col3:
        if status == 'completed':
            st.metric("預計剩餘", "已完成")
        elif status == 'failed':
            st.metric("預計剩餘", "已中斷")
        else:
            st.metric("預計剩餘", format_time(remaining_time))

    st.progress(min(progress_percentage / 100.0, 1.0))
    st.write(f"**當前任務**: {current_step_description}")

    # 狀態訊息
    status_label = {'running': '[進行中]', 'completed': '[完成]', 'failed': '[失敗]'}.get(status, '[進行中]')

    if status == 'completed':
        st.success(f"{status_label} **當前狀態**: {last_message}")
        _render_view_report_button(analysis_id, progress_data)
    elif status == 'failed':
        st.error(f"{status_label} **當前狀態**: {last_message}")
    else:
        st.info(f"{status_label} **當前狀態**: {last_message}")

    # 重新整理控件
    if show_refresh_controls and status in ('running', 'initializing'):
        _render_refresh_controls(analysis_id, status, show_refresh_controls)

    return status in ['completed', 'failed']


def _calculate_elapsed_time(progress_data: dict, status: str) -> float:
    """統一計算已用時間"""
    if status == 'completed':
        return progress_data.get('elapsed_time', 0)

    start_time = progress_data.get('start_time', 0)
    if start_time > 0:
        return time.time() - start_time

    return progress_data.get('elapsed_time', 0)


def _render_view_report_button(analysis_id: str, progress_data: dict):
    """渲染「查看分析報告」按鈕"""
    if st.button("查看分析報告", key=f"view_report_unified_{analysis_id}", type="primary"):
        if not st.session_state.get('analysis_results'):
            try:
                from web.utils.analysis_runner import format_analysis_results
                raw_results = progress_data.get('raw_results')
                if raw_results:
                    formatted_results = format_analysis_results(raw_results)
                    if formatted_results:
                        st.session_state.analysis_results = formatted_results
                        st.session_state.analysis_running = False
            except Exception as e:
                st.error(f"恢復分析結果失敗: {e}")

        st.session_state.show_analysis_results = True
        st.session_state.current_analysis_id = analysis_id
        st.rerun()


def _render_refresh_controls(analysis_id: str, status: str, show_controls: bool):
    """渲染重新整理控件（非阻塞式自動重新整理）"""
    if not show_controls:
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("重新整理進度", key=f"refresh_unified_{analysis_id}"):
            st.rerun()
    with col2:
        auto_refresh_key = f"auto_refresh_unified_{analysis_id}"
        default_value = st.session_state.get(auto_refresh_key, True)
        auto_refresh = st.checkbox("自動重新整理", value=default_value, key=auto_refresh_key)

        if auto_refresh and status == 'running':
            # 使用非阻塞方式：記錄上次重新整理時間，只在間隔到達時 rerun
            last_refresh_key = f"_last_refresh_ts_{analysis_id}"
            last_refresh = st.session_state.get(last_refresh_key, 0)
            now = time.time()

            if now - last_refresh >= AUTO_REFRESH_INTERVAL:
                st.session_state[last_refresh_key] = now
                st.rerun()
        elif auto_refresh and status in ('completed', 'failed'):
            st.session_state[auto_refresh_key] = False
