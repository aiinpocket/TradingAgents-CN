#!/usr/bin/env python3
"""
異步進度顯示組件
支持定時刷新，從Redis或文件獲取進度狀態
"""

import streamlit as st
import time
from typing import Optional, Dict, Any
from web.utils.async_progress_tracker import get_progress_by_id, format_time

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('async_display')

class AsyncProgressDisplay:
    """異步進度顯示組件"""
    
    def __init__(self, container, analysis_id: str, refresh_interval: float = 1.0):
        self.container = container
        self.analysis_id = analysis_id
        self.refresh_interval = refresh_interval
        
        # 創建顯示組件
        with self.container:
            self.progress_bar = st.progress(0)
            self.status_text = st.empty()
            self.step_info = st.empty()
            self.time_info = st.empty()
            self.refresh_button = st.empty()
        
        # 初始化狀態
        self.last_update = 0
        self.is_completed = False
        
        logger.info(f"[異步顯示] 初始化: {analysis_id}, 刷新間隔: {refresh_interval}s")
    
    def update_display(self) -> bool:
        """更新顯示，返回是否需要繼續刷新"""
        current_time = time.time()
        
        # 檢查是否需要刷新
        if current_time - self.last_update < self.refresh_interval and not self.is_completed:
            return not self.is_completed
        
        # 獲取進度數據
        progress_data = get_progress_by_id(self.analysis_id)
        
        if not progress_data:
            self.status_text.error("無法獲取分析進度，請檢查分析是否正在運行")
            return False
        
        # 更新顯示
        self._render_progress(progress_data)
        self.last_update = current_time
        
        # 檢查是否完成
        status = progress_data.get('status', 'running')
        self.is_completed = status in ['completed', 'failed']
        
        return not self.is_completed
    
    def _render_progress(self, progress_data: Dict[str, Any]):
        """渲染進度顯示"""
        try:
            # 基本信息
            current_step = progress_data.get('current_step', 0)
            total_steps = progress_data.get('total_steps', 8)
            progress_percentage = progress_data.get('progress_percentage', 0.0)
            status = progress_data.get('status', 'running')
            
            # 更新進度條
            self.progress_bar.progress(min(progress_percentage / 100, 1.0))
            
            # 狀態信息
            step_name = progress_data.get('current_step_name', '未知')
            step_description = progress_data.get('current_step_description', '')
            last_message = progress_data.get('last_message', '')
            
            # 狀態圖標
            status_icon = {
                'running': '[進行中]',
                'completed': '[完成]',
                'failed': '[失敗]'
            }.get(status, '[進行中]')
            
            # 顯示當前狀態
            self.status_text.info(f"{status_icon} **當前狀態**: {last_message}")
            
            # 顯示步驟信息
            if status == 'failed':
                self.step_info.error(f"**分析失敗**: {last_message}")
            elif status == 'completed':
                self.step_info.success(f"**分析完成**: 所有步驟已完成")

                # 添加查看報告按鈕
                with self.step_info:
                    if st.button("查看分析報告", key=f"view_report_{progress_data.get('analysis_id', 'unknown')}", type="primary"):
                        analysis_id = progress_data.get('analysis_id')
                        # 嘗試恢複分析結果（如果還沒有的話）
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
                                st.error(f"恢複分析結果失敗: {e}")

                        # 觸發顯示報告
                        st.session_state.show_analysis_results = True
                        st.session_state.current_analysis_id = analysis_id
                        st.rerun()
            else:
                self.step_info.info(f"**進度**: 第 {current_step + 1} 步，共 {total_steps} 步 ({progress_percentage:.1f}%)\n\n"
                                  f"**當前步驟**: {step_name}\n\n"
                                  f"**步驟說明**: {step_description}")
            
            # 時間信息 - 實時計算已用時間
            start_time = progress_data.get('start_time', 0)
            estimated_total_time = progress_data.get('estimated_total_time', 0)

            # 計算已用時間
            import time
            if status == 'completed':
                # 已完成的分析使用儲存的最終耗時
                real_elapsed_time = progress_data.get('elapsed_time', 0)
            elif start_time > 0:
                # 進行中的分析使用實時計算
                real_elapsed_time = time.time() - start_time
            else:
                # 備用方案
                real_elapsed_time = progress_data.get('elapsed_time', 0)

            # 重新計算剩餘時間
            remaining_time = max(estimated_total_time - real_elapsed_time, 0)
            
            if status == 'completed':
                self.time_info.success(f"**已用時間**: {format_time(real_elapsed_time)} | **總耗時**: {format_time(real_elapsed_time)}")
            elif status == 'failed':
                self.time_info.error(f"**已用時間**: {format_time(real_elapsed_time)} | **分析中斷**")
            else:
                self.time_info.info(f"**已用時間**: {format_time(real_elapsed_time)} | **預計剩餘**: {format_time(remaining_time)}")
            
            # 刷新按鈕（僅在運行時顯示）
            if status == 'running':
                with self.refresh_button:
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("手動刷新", key=f"refresh_{self.analysis_id}"):
                            st.rerun()
            else:
                self.refresh_button.empty()
                
        except Exception as e:
            logger.error(f"[異步顯示] 渲染失敗: {e}")
            self.status_text.error(f"顯示更新失敗: {str(e)}")

def create_async_progress_display(container, analysis_id: str, refresh_interval: float = 1.0) -> AsyncProgressDisplay:
    """創建異步進度顯示組件"""
    return AsyncProgressDisplay(container, analysis_id, refresh_interval)

def auto_refresh_progress(display: AsyncProgressDisplay, max_duration: float = 1800):
    """自動刷新進度顯示"""
    start_time = time.time()
    
    # 使用Streamlit的自動刷新機制
    placeholder = st.empty()
    
    while True:
        # 檢查超時
        if time.time() - start_time > max_duration:
            with placeholder:
                st.warning("分析時間過長，已停止自動刷新。請手動刷新頁面查看最新狀態。")
            break
        
        # 更新顯示
        should_continue = display.update_display()
        
        if not should_continue:
            # 分析完成或失敗，停止刷新
            break
        
        # 等待刷新間隔
        time.sleep(display.refresh_interval)
    
    logger.info(f"[異步顯示] 自動刷新結束: {display.analysis_id}")

# Streamlit專用的自動刷新組件
def streamlit_auto_refresh_progress(analysis_id: str, refresh_interval: int = 2):
    """Streamlit專用的自動刷新進度顯示"""

    # 獲取進度數據
    progress_data = get_progress_by_id(analysis_id)

    if not progress_data:
        st.error("無法獲取分析進度，請檢查分析是否正在運行")
        return False

    status = progress_data.get('status', 'running')

    # 基本信息
    current_step = progress_data.get('current_step', 0)
    total_steps = progress_data.get('total_steps', 8)
    progress_percentage = progress_data.get('progress_percentage', 0.0)

    # 進度條
    st.progress(min(progress_percentage / 100, 1.0))

    # 狀態信息
    step_name = progress_data.get('current_step_name', '未知')
    step_description = progress_data.get('current_step_description', '')
    last_message = progress_data.get('last_message', '')

    # 狀態圖標
    status_icon = {
        'running': '[進行中]',
        'completed': '[完成]',
        'failed': '[失敗]'
    }.get(status, '[進行中]')

    # 顯示信息
    st.info(f"{status_icon} **當前狀態**: {last_message}")

    if status == 'failed':
        st.error(f"**分析失敗**: {last_message}")
    elif status == 'completed':
        st.success(f"**分析完成**: 所有步驟已完成")

        # 添加查看報告按鈕
        if st.button("查看分析報告", key=f"view_report_streamlit_{progress_data.get('analysis_id', 'unknown')}", type="primary"):
            analysis_id = progress_data.get('analysis_id')
            # 嘗試恢複分析結果（如果還沒有的話）
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
                    st.error(f"恢複分析結果失敗: {e}")

            # 觸發顯示報告
            st.session_state.show_analysis_results = True
            st.session_state.current_analysis_id = analysis_id
            st.rerun()
    else:
        st.info(f"**進度**: 第 {current_step + 1} 步，共 {total_steps} 步 ({progress_percentage:.1f}%)\n\n"
               f"**當前步驟**: {step_name}\n\n"
               f"**步驟說明**: {step_description}")

    # 時間信息 - 實時計算已用時間
    start_time = progress_data.get('start_time', 0)
    estimated_total_time = progress_data.get('estimated_total_time', 0)

    # 計算已用時間
    import time
    if status == 'completed':
        # 已完成的分析使用儲存的最終耗時
        elapsed_time = progress_data.get('elapsed_time', 0)
    elif start_time > 0:
        # 進行中的分析使用實時計算
        elapsed_time = time.time() - start_time
    else:
        # 備用方案
        elapsed_time = progress_data.get('elapsed_time', 0)

    # 重新計算剩餘時間
    remaining_time = max(estimated_total_time - elapsed_time, 0)

    if status == 'completed':
        st.success(f"**總耗時**: {format_time(elapsed_time)}")
    elif status == 'failed':
        st.error(f"**已用時間**: {format_time(elapsed_time)} | **分析中斷**")
    else:
        st.info(f"**已用時間**: {format_time(elapsed_time)} | **預計剩餘**: {format_time(remaining_time)}")

    # 添加刷新控制（僅在運行時顯示）
    if status == 'running':
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("刷新進度", key=f"refresh_streamlit_{analysis_id}"):
                st.rerun()
        with col2:
            auto_refresh_key = f"auto_refresh_streamlit_{analysis_id}"
            # 獲取默認值，如果是新分析則默認為True
            default_value = st.session_state.get(auto_refresh_key, True) # 默認為True
            auto_refresh = st.checkbox("自動刷新", value=default_value, key=auto_refresh_key)
            if auto_refresh and status == 'running': # 只在運行時自動刷新
                import time
                time.sleep(3) # 等待3秒
                st.rerun()
            elif auto_refresh and status in ['completed', 'failed']:
                # 分析完成後自動關閉自動刷新
                st.session_state[auto_refresh_key] = False

    return status in ['completed', 'failed']

# 新增：靜態進度顯示（不會觸發頁面刷新）
def display_static_progress(analysis_id: str) -> bool:
    """
    顯示靜態進度（不自動刷新）
    返回是否已完成
    """
    import streamlit as st

    # 使用session state避免重複創建組件
    progress_key = f"progress_display_{analysis_id}"
    if progress_key not in st.session_state:
        st.session_state[progress_key] = True

    # 獲取進度數據
    progress_data = get_progress_by_id(analysis_id)

    if not progress_data:
        st.error("無法獲取分析進度，請檢查分析是否正在運行")
        return False

    status = progress_data.get('status', 'running')

    # 調試信息（可以在生產環境中移除）
    import datetime
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    logger.debug(f"[進度顯示] {current_time} - 狀態: {status}, 進度: {progress_data.get('progress_percentage', 0):.1f}%")

    # 顯示基本信息（移除分析ID顯示）
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        step_name = progress_data.get('current_step_name', '未知')
        st.write(f"**當前步驟**: {step_name}")

    with col2:
        progress_percentage = progress_data.get('progress_percentage', 0.0)
        st.metric("進度", f"{progress_percentage:.1f}%")

    with col3:
        # 計算已用時間
        start_time = progress_data.get('start_time', 0)
        import time
        if status == 'completed':
            # 已完成的分析使用儲存的最終耗時
            elapsed_time = progress_data.get('elapsed_time', 0)
        elif start_time > 0:
            # 進行中的分析使用實時計算
            elapsed_time = time.time() - start_time
        else:
            # 備用方案
            elapsed_time = progress_data.get('elapsed_time', 0)
        st.metric("已用時間", format_time(elapsed_time))

    with col4:
        remaining_time = progress_data.get('remaining_time', 0)
        if status == 'completed':
            st.metric("預計剩餘", "已完成")
        elif status == 'failed':
            st.metric("預計剩餘", "已中斷")
        elif remaining_time > 0 and status == 'running':
            st.metric("預計剩餘", format_time(remaining_time))
        else:
            st.metric("預計剩餘", "計算中...")

    # 進度條
    st.progress(min(progress_percentage / 100, 1.0))

    # 步驟詳情
    step_description = progress_data.get('current_step_description', '正在處理...')
    st.write(f"**當前任務**: {step_description}")

    # 狀態信息
    last_message = progress_data.get('last_message', '')

    # 狀態圖標
    status_icon = {
        'running': '[進行中]',
        'completed': '[完成]',
        'failed': '[失敗]'
    }.get(status, '[進行中]')

    # 顯示狀態
    if status == 'failed':
        st.error(f"**分析失敗**: {last_message}")
    elif status == 'completed':
        st.success(f"**分析完成**: {last_message}")

        # 添加查看報告按鈕
        if st.button("查看分析報告", key=f"view_report_static_{analysis_id}", type="primary"):
            # 嘗試恢複分析結果（如果還沒有的話）
            if not st.session_state.get('analysis_results'):
                try:
                    from web.utils.async_progress_tracker import get_progress_by_id
                    from web.utils.analysis_runner import format_analysis_results
                    progress_data = get_progress_by_id(analysis_id)
                    if progress_data and progress_data.get('raw_results'):
                        formatted_results = format_analysis_results(progress_data['raw_results'])
                        if formatted_results:
                            st.session_state.analysis_results = formatted_results
                            st.session_state.analysis_running = False
                except Exception as e:
                    st.error(f"恢複分析結果失敗: {e}")

            # 觸發顯示報告
            st.session_state.show_analysis_results = True
            st.session_state.current_analysis_id = analysis_id
            st.rerun()
    else:
        st.info(f"{status_icon} **當前狀態**: {last_message}")

        # 添加刷新控制（僅在運行時顯示）
        if status == 'running':
            # 使用唯一的容器避免重複
            refresh_container_key = f"refresh_container_{analysis_id}"
            if refresh_container_key not in st.session_state:
                st.session_state[refresh_container_key] = True

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("刷新進度", key=f"refresh_static_{analysis_id}"):
                    st.rerun()
            with col2:
                auto_refresh_key = f"auto_refresh_static_{analysis_id}"
                # 獲取默認值，如果是新分析則默認為True
                default_value = st.session_state.get(auto_refresh_key, True) # 默認為True
                auto_refresh = st.checkbox("自動刷新", value=default_value, key=auto_refresh_key)
                if auto_refresh and status == 'running': # 只在運行時自動刷新
                    import time
                    time.sleep(3) # 等待3秒
                    st.rerun()
                elif auto_refresh and status in ['completed', 'failed']:
                    # 分析完成後自動關閉自動刷新
                    st.session_state[auto_refresh_key] = False

    # 清理session state（分析完成後）
    if status in ['completed', 'failed']:
        progress_key = f"progress_display_{analysis_id}"
        refresh_container_key = f"refresh_container_{analysis_id}"
        if progress_key in st.session_state:
            del st.session_state[progress_key]
        if refresh_container_key in st.session_state:
            del st.session_state[refresh_container_key]

    return status in ['completed', 'failed']


def display_unified_progress(analysis_id: str, show_refresh_controls: bool = True) -> bool:
    """
    統一的進度顯示函數，避免重複元素
    返回是否已完成
    """
    import streamlit as st

    # 簡化邏輯：直接調用顯示函數，通過參數控制是否顯示刷新按鈕
    # 調用方負責確保只在需要的地方傳入show_refresh_controls=True
    return display_static_progress_with_controls(analysis_id, show_refresh_controls)


def display_static_progress_with_controls(analysis_id: str, show_refresh_controls: bool = True) -> bool:
    """
    顯示靜態進度，可控制是否顯示刷新控件
    """
    import streamlit as st
    from web.utils.async_progress_tracker import get_progress_by_id

    # 獲取進度數據
    progress_data = get_progress_by_id(analysis_id)

    if not progress_data:
        # 如果沒有進度數據，顯示默認的準備狀態
        st.info("**當前狀態**: 準備開始分析...")
        
        # 設置默認狀態為initializing
        status = 'initializing'

        # 如果需要顯示刷新控件，仍然顯示
        if show_refresh_controls:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("刷新進度", key=f"refresh_unified_default_{analysis_id}"):
                    st.rerun()
            with col2:
                auto_refresh_key = f"auto_refresh_unified_default_{analysis_id}"
                # 獲取默認值，如果是新分析則默認為True
                default_value = st.session_state.get(auto_refresh_key, True) # 默認為True
                auto_refresh = st.checkbox("自動刷新", value=default_value, key=auto_refresh_key)
                if auto_refresh and status == 'running': # 只在運行時自動刷新
                    import time
                    time.sleep(3) # 等待3秒
                    st.rerun()
                elif auto_refresh and status in ['completed', 'failed']:
                    # 分析完成後自動關閉自動刷新
                    st.session_state[auto_refresh_key] = False

        return False # 返回False表示還未完成

    # 解析進度數據（修複字段名稱匹配）
    status = progress_data.get('status', 'running')
    current_step = progress_data.get('current_step', 0)
    current_step_name = progress_data.get('current_step_name', '準備階段')
    progress_percentage = progress_data.get('progress_percentage', 0.0)

    # 計算已用時間
    start_time = progress_data.get('start_time', 0)
    estimated_total_time = progress_data.get('estimated_total_time', 0)
    import time
    if status == 'completed':
        # 已完成的分析使用儲存的最終耗時
        elapsed_time = progress_data.get('elapsed_time', 0)
    elif start_time > 0:
        # 進行中的分析使用實時計算
        elapsed_time = time.time() - start_time
    else:
        # 備用方案
        elapsed_time = progress_data.get('elapsed_time', 0)

    # 重新計算剩餘時間
    remaining_time = max(estimated_total_time - elapsed_time, 0)
    current_step_description = progress_data.get('current_step_description', '初始化分析引擎')
    last_message = progress_data.get('last_message', '準備開始分析')

    # 顯示當前步驟
    st.write(f"**當前步驟**: {current_step_name}")

    # 顯示進度條和統計信息
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

    # 顯示進度條
    st.progress(min(progress_percentage / 100.0, 1.0))

    # 顯示當前任務
    st.write(f"**當前任務**: {current_step_description}")

    # 顯示當前狀態
    status_icon = {
        'running': '[進行中]',
        'completed': '[完成]',
        'failed': '[失敗]'
    }.get(status, '[進行中]')

    if status == 'completed':
        st.success(f"{status_icon} **當前狀態**: {last_message}")

        # 添加查看報告按鈕
        if st.button("查看分析報告", key=f"view_report_unified_{analysis_id}", type="primary"):
            # 嘗試恢複分析結果（如果還沒有的話）
            if not st.session_state.get('analysis_results'):
                try:
                    from web.utils.async_progress_tracker import get_progress_by_id
                    from web.utils.analysis_runner import format_analysis_results
                    progress_data = get_progress_by_id(analysis_id)
                    if progress_data and progress_data.get('raw_results'):
                        formatted_results = format_analysis_results(progress_data['raw_results'])
                        if formatted_results:
                            st.session_state.analysis_results = formatted_results
                            st.session_state.analysis_running = False
                except Exception as e:
                    st.error(f"恢複分析結果失敗: {e}")

            # 觸發顯示報告
            st.session_state.show_analysis_results = True
            st.session_state.current_analysis_id = analysis_id
            st.rerun()
    elif status == 'failed':
        st.error(f"{status_icon} **當前狀態**: {last_message}")
    else:
        st.info(f"{status_icon} **當前狀態**: {last_message}")

    # 顯示刷新控制的條件：
    # 1. 需要顯示刷新控件 AND
    # 2. (分析正在運行 OR 分析剛開始還沒有狀態)
    if show_refresh_controls and (status == 'running'or status == 'initializing'):
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("刷新進度", key=f"refresh_unified_{analysis_id}"):
                st.rerun()
        with col2:
            auto_refresh_key = f"auto_refresh_unified_{analysis_id}"
            # 獲取默認值，如果是新分析則默認為True
            default_value = st.session_state.get(auto_refresh_key, True) # 默認為True
            auto_refresh = st.checkbox("自動刷新", value=default_value, key=auto_refresh_key)
            if auto_refresh and status == 'running': # 只在運行時自動刷新
                import time
                time.sleep(3) # 等待3秒
                st.rerun()
            elif auto_refresh and status in ['completed', 'failed']:
                # 分析完成後自動關閉自動刷新
                st.session_state[auto_refresh_key] = False

    # 不需要清理session state，因為我們通過參數控制顯示

    return status in ['completed', 'failed']
