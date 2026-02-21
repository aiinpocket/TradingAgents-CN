"""
用戶活動記錄查看組件
為管理員提供查看和分析用戶操作行為的Web界面
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# 導入用戶活動記錄器
try:
    from ..utils.user_activity_logger import user_activity_logger
    from ..utils.auth_manager import auth_manager
except ImportError:
    user_activity_logger = None
    auth_manager = None

def render_user_activity_dashboard():
    """渲染用戶活動儀表板"""
    
    # 檢查權限
    if not auth_manager or not auth_manager.check_permission("admin"):
        st.error("您沒有權限訪問用戶活動記錄")
        return
    
    if not user_activity_logger:
        st.error("用戶活動記錄器未初始化")
        return
    
    st.title("用戶活動記錄儀表板")
    
    # 側邊欄過濾選項
    with st.sidebar:
        st.header("過濾選項")
        
        # 日期範圍選擇
        date_range = st.selectbox(
            "時間範圍",
            ["最近1天", "最近3天", "最近7天", "最近30天", "自定義"],
            index=2
        )
        
        if date_range == "自定義":
            start_date = st.date_input("開始日期", datetime.now() - timedelta(days=7))
            end_date = st.date_input("結束日期", datetime.now())
        else:
            days_map = {"最近1天": 1, "最近3天": 3, "最近7天": 7, "最近30天": 30}
            days = days_map[date_range]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
        
        # 用戶過濾
        username_filter = st.text_input("用戶名過濾", placeholder="留空顯示所有用戶")
        
        # 活動類型過濾
        action_type_filter = st.selectbox(
            "活動類型",
            ["全部", "auth", "analysis", "config", "navigation", "data_export", "user_management", "system"]
        )
        
        if action_type_filter == "全部":
            action_type_filter = None
    
    # 獲取活動數據
    activities = user_activity_logger.get_user_activities(
        username=username_filter if username_filter else None,
        start_date=start_date,
        end_date=end_date,
        action_type=action_type_filter,
        limit=1000
    )
    
    if not activities:
        st.warning("未找到符合條件的活動記錄")
        return
    
    # 顯示統計概覽
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("總活動數", len(activities))

    with col2:
        unique_users = len(set(a['username'] for a in activities))
        st.metric("活躍用戶", unique_users)

    with col3:
        successful_activities = sum(1 for a in activities if a.get('success', True))
        success_rate = (successful_activities / len(activities) * 100) if activities else 0
        st.metric("成功率", f"{success_rate:.1f}%")

    with col4:
        durations = [a.get('duration_ms', 0) for a in activities if a.get('duration_ms')]
        avg_duration = sum(durations) / len(durations) if durations else 0
        st.metric("平均耗時", f"{avg_duration:.0f}ms")
    
    # 標籤頁
    tab1, tab2, tab3, tab4 = st.tabs(["統計圖表", "活動列表", "用戶分析", "導出數據"])
    
    with tab1:
        render_activity_charts(activities)
    
    with tab2:
        render_activity_list(activities)
    
    with tab3:
        render_user_analysis(activities)
    
    with tab4:
        render_export_options(activities)

def render_activity_charts(activities: List[Dict[str, Any]]):
    """渲染活動統計圖表"""
    
    # 按活動類型統計
    st.subheader("按活動類型統計")
    activity_types = {}
    for activity in activities:
        action_type = activity.get('action_type', 'unknown')
        activity_types[action_type] = activity_types.get(action_type, 0) + 1
    
    if activity_types:
        fig_pie = px.pie(
            values=list(activity_types.values()),
            names=list(activity_types.keys()),
            title="活動類型分布"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # 按時間統計
    st.subheader("按時間統計")
    daily_activities = {}
    for activity in activities:
        date_str = datetime.fromtimestamp(activity['timestamp']).strftime('%Y-%m-%d')
        daily_activities[date_str] = daily_activities.get(date_str, 0) + 1
    
    if daily_activities:
        dates = sorted(daily_activities.keys())
        counts = [daily_activities[date] for date in dates]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='每日活動數',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))
        fig_line.update_layout(
            title="每日活動趨勢",
            xaxis_title="日期",
            yaxis_title="活動數量"
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    # 按用戶統計
    st.subheader("按用戶統計")
    user_activities = {}
    for activity in activities:
        username = activity.get('username', 'unknown')
        user_activities[username] = user_activities.get(username, 0) + 1
    
    if user_activities:
        # 只顯示前10個最活躍的用戶
        top_users = sorted(user_activities.items(), key=lambda x: x[1], reverse=True)[:10]
        usernames = [item[0] for item in top_users]
        counts = [item[1] for item in top_users]
        
        fig_bar = px.bar(
            x=counts,
            y=usernames,
            orientation='h',
            title="用戶活動排行榜 (前10名)",
            labels={'x': '活動數量', 'y': '用戶名'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

def render_activity_list(activities: List[Dict[str, Any]]):
    """渲染活動列表"""
    
    st.subheader("活動記錄列表")
    
    # 分頁設置
    page_size = st.selectbox("每頁顯示", [10, 25, 50, 100], index=1)
    total_pages = (len(activities) + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.number_input("頁碼", min_value=1, max_value=total_pages, value=1) - 1
    else:
        page = 0
    
    # 獲取當前頁數據
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(activities))
    page_activities = activities[start_idx:end_idx]
    
    # 轉換為DataFrame顯示
    df_data = []
    for activity in page_activities:
        timestamp = datetime.fromtimestamp(activity['timestamp'])
        df_data.append({
            "時間": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "用戶": activity.get('username', 'unknown'),
            "角色": activity.get('user_role', 'unknown'),
            "活動類型": activity.get('action_type', 'unknown'),
            "活動名稱": activity.get('action_name', 'unknown'),
            "成功": "是" if activity.get('success', True) else "否",
            "耗時(ms)": activity.get('duration_ms', ''),
            "詳情": json.dumps(activity.get('details', {}), ensure_ascii=False)[:100] + "..." if activity.get('details') else ""
        })
    
    if df_data:
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # 顯示分頁信息
        if total_pages > 1:
            st.info(f"第 {page + 1} 頁，共 {total_pages} 頁 | 顯示 {start_idx + 1}-{end_idx} 條，共 {len(activities)} 條記錄")
    else:
        st.info("當前頁沒有數據")

def render_user_analysis(activities: List[Dict[str, Any]]):
    """渲染用戶分析"""
    
    st.subheader("用戶行為分析")
    
    # 用戶選擇
    usernames = sorted(set(a['username'] for a in activities))
    selected_user = st.selectbox("選擇用戶", usernames)
    
    if selected_user:
        user_activities = [a for a in activities if a['username'] == selected_user]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("總活動數", len(user_activities))

            # 成功率
            successful = sum(1 for a in user_activities if a.get('success', True))
            success_rate = (successful / len(user_activities) * 100) if user_activities else 0
            st.metric("成功率", f"{success_rate:.1f}%")
        
        with col2:
            # 最常用功能
            action_counts = {}
            for activity in user_activities:
                action = activity.get('action_name', 'unknown')
                action_counts[action] = action_counts.get(action, 0) + 1
            
            if action_counts:
                most_used = max(action_counts.items(), key=lambda x: x[1])
                st.metric("最常用功能", most_used[0])
                st.metric("使用次數", most_used[1])
        
        # 用戶活動時間線
        st.subheader(f"{selected_user} 的活動時間線")
        
        timeline_data = []
        for activity in user_activities[-20:]:  # 顯示最近20條
            timestamp = datetime.fromtimestamp(activity['timestamp'])
            timeline_data.append({
                "時間": timestamp.strftime('%m-%d %H:%M'),
                "活動": f"{activity.get('action_type', 'unknown')} - {activity.get('action_name', 'unknown')}",
                "狀態": "成功" if activity.get('success', True) else "失敗"
            })
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            st.dataframe(df_timeline, use_container_width=True)

def render_export_options(activities: List[Dict[str, Any]]):
    """渲染導出選項"""
    
    st.subheader("導出數據")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("導出格式", ["CSV", "JSON", "Excel"])
    
    with col2:
        include_details = st.checkbox("包含詳細信息", value=True)
    
    if st.button("導出數據", type="primary"):
        try:
            # 準備導出數據
            export_data = []
            for activity in activities:
                timestamp = datetime.fromtimestamp(activity['timestamp'])
                row = {
                    "時間戳": activity['timestamp'],
                    "日期時間": timestamp.isoformat(),
                    "用戶名": activity.get('username', ''),
                    "用戶角色": activity.get('user_role', ''),
                    "活動類型": activity.get('action_type', ''),
                    "活動名稱": activity.get('action_name', ''),
                    "會話ID": activity.get('session_id', ''),
                    "IP地址": activity.get('ip_address', ''),
                    "頁面URL": activity.get('page_url', ''),
                    "耗時(ms)": activity.get('duration_ms', ''),
                    "成功": activity.get('success', True),
                    "錯誤信息": activity.get('error_message', '')
                }
                
                if include_details:
                    row["詳細信息"] = json.dumps(activity.get('details', {}), ensure_ascii=False)
                
                export_data.append(row)
            
            # 生成文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format == "CSV":
                df = pd.DataFrame(export_data)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="下載 CSV 文件",
                    data=csv_data,
                    file_name=f"user_activities_{timestamp}.csv",
                    mime="text/csv"
                )
            
            elif export_format == "JSON":
                json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="下載 JSON 文件",
                    data=json_data,
                    file_name=f"user_activities_{timestamp}.json",
                    mime="application/json"
                )
            
            elif export_format == "Excel":
                df = pd.DataFrame(export_data)
                # 註意：這裡需要安裝 openpyxl 庫
                excel_buffer = df.to_excel(index=False, engine='openpyxl')
                st.download_button(
                    label="下載 Excel 文件",
                    data=excel_buffer,
                    file_name=f"user_activities_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"成功準備 {len(activities)} 條記錄的導出文件")
            
        except Exception as e:
            st.error(f"導出失敗: {e}")

def render_activity_summary_widget():
    """渲染活動摘要小部件（用於主頁面）"""
    
    if not user_activity_logger or not auth_manager:
        return
    
    # 只有管理員才能看到
    if not auth_manager.check_permission("admin"):
        return
    
    st.subheader("用戶活動概覽")
    
    # 獲取最近24小時的活動
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)
    
    activities = user_activity_logger.get_user_activities(
        start_date=start_date,
        end_date=end_date,
        limit=500
    )
    
    if activities:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("24小時活動", len(activities))

        with col2:
            unique_users = len(set(a['username'] for a in activities))
            st.metric("活躍用戶", unique_users)

        with col3:
            successful = sum(1 for a in activities if a.get('success', True))
            success_rate = (successful / len(activities) * 100) if activities else 0
            st.metric("成功率", f"{success_rate:.1f}%")
        
        # 顯示最近的几條活動
        st.write("最近活動:")
        recent_activities = activities[:5]
        for activity in recent_activities:
            timestamp = datetime.fromtimestamp(activity['timestamp'])
            success_icon = "[OK]" if activity.get('success', True) else "[FAIL]"
            st.write(f"{success_icon} {timestamp.strftime('%H:%M')} - {activity.get('username', 'unknown')}: {activity.get('action_name', 'unknown')}")
    else:
        st.info("最近24小時無活動記錄")