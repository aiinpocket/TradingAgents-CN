"""
操作日誌管理組件
提供系統操作日誌的查看和管理功能
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import os
from pathlib import Path

def get_operation_logs_dir():
    """取得操作日誌目錄"""
    logs_dir = Path(__file__).parent.parent / "data" / "operation_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def load_operation_logs(start_date=None, end_date=None, action_type=None, limit=1000):
    """載入操作日誌"""
    all_logs = []

    # 載入操作日誌（operation_logs 目錄）
    logs_dir = get_operation_logs_dir()
    for log_file in logs_dir.glob("*.json"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                if isinstance(logs, list):
                    all_logs.extend(logs)
                elif isinstance(logs, dict):
                    all_logs.append(logs)
        except Exception as e:
            st.error(f"讀取日誌檔案失敗: {log_file.name} - {e}")

    for log_file in logs_dir.glob("*.jsonl"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        log_entry = json.loads(line.strip())
                        all_logs.append(log_entry)
        except Exception as e:
            st.error(f"讀取 JSONL 日誌檔案失敗: {log_file.name} - {e}")

    # 過濾日誌
    filtered_logs = []
    for log in all_logs:
        # 時間過濾
        if start_date or end_date:
            try:
                timestamp = _parse_timestamp(log.get('timestamp', 0))
                log_date = datetime.fromtimestamp(timestamp).date()
                if start_date and log_date < start_date:
                    continue
                if end_date and log_date > end_date:
                    continue
            except Exception:
                pass

        # 操作類型過濾
        if action_type and log.get('action_type', '') != action_type:
            continue

        filtered_logs.append(log)

    # 按時間戳排序（最新的在前）
    filtered_logs.sort(key=lambda x: _parse_timestamp(x.get('timestamp', 0)), reverse=True)

    # 限制數量
    return filtered_logs[:limit]


def _parse_timestamp(timestamp) -> float:
    """安全地解析時間戳，確保回傳數字類型"""
    if isinstance(timestamp, (int, float)):
        return float(timestamp)
    if isinstance(timestamp, str):
        try:
            return float(timestamp)
        except (ValueError, TypeError):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.timestamp()
            except Exception:
                return 0
    return 0


def render_operation_logs():
    """渲染操作日誌管理介面"""

    st.title("操作日誌管理")

    # 側邊欄過濾選項
    with st.sidebar:
        st.header("過濾選項")

        # 日期範圍選擇
        date_range = st.selectbox(
            "時間範圍",
            ["最近1天", "最近3天", "最近7天", "最近30天", "自訂"],
            index=2
        )

        if date_range == "自訂":
            start_date = st.date_input("開始日期", datetime.now() - timedelta(days=7))
            end_date = st.date_input("結束日期", datetime.now())
        else:
            days_map = {"最近1天": 1, "最近3天": 3, "最近7天": 7, "最近30天": 30}
            days = days_map[date_range]
            end_date = datetime.now().date()
            start_date = (datetime.now() - timedelta(days=days)).date()

        # 操作類型過濾
        action_type_filter = st.selectbox(
            "操作類型",
            ["全部", "analysis", "navigation", "config", "data_export", "system", "export"]
        )

        if action_type_filter == "全部":
            action_type_filter = None

    # 載入操作日誌
    logs = load_operation_logs(
        start_date=start_date,
        end_date=end_date,
        action_type=action_type_filter,
        limit=1000
    )

    if not logs:
        st.warning("未找到符合條件的操作日誌")
        return

    # 顯示統計概覽
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("總操作數", len(logs))

    with col2:
        successful_ops = sum(1 for log in logs if log.get('success', True))
        success_rate = (successful_ops / len(logs) * 100) if logs else 0
        st.metric("成功率", f"{success_rate:.1f}%")

    with col3:
        # 近1小時的日誌統計
        recent_count = 0
        one_hour_ago = datetime.now() - timedelta(hours=1)
        for log in logs:
            try:
                ts = _parse_timestamp(log.get('timestamp', 0))
                if datetime.fromtimestamp(ts) > one_hour_ago:
                    recent_count += 1
            except Exception:
                continue
        st.metric("近1小時", recent_count)

    # 標籤頁
    tab1, tab2, tab3 = st.tabs(["統計圖表", "日誌列表", "匯出資料"])

    with tab1:
        render_logs_charts(logs)

    with tab2:
        render_logs_list(logs)

    with tab3:
        render_logs_export(logs)

def render_logs_charts(logs: List[Dict[str, Any]]):
    """渲染日誌統計圖表"""

    # 按操作類型統計
    st.subheader("按操作類型統計")
    action_types = {}
    for log in logs:
        action_type = log.get('action_type', 'unknown')
        action_types[action_type] = action_types.get(action_type, 0) + 1

    if action_types:
        fig_pie = px.pie(
            values=list(action_types.values()),
            names=list(action_types.keys()),
            title="操作類型分布"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # 按時間統計
    st.subheader("按時間統計")
    daily_logs = {}
    for log in logs:
        try:
            ts = _parse_timestamp(log.get('timestamp', 0))
            date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        except Exception:
            continue
        daily_logs[date_str] = daily_logs.get(date_str, 0) + 1

    if daily_logs:
        dates = sorted(daily_logs.keys())
        counts = [daily_logs[date] for date in dates]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='每日操作數',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))
        fig_line.update_layout(
            title="每日操作趨勢",
            xaxis_title="日期",
            yaxis_title="操作數量"
        )
        st.plotly_chart(fig_line, use_container_width=True)

def render_logs_list(logs: List[Dict[str, Any]]):
    """渲染日誌列表"""

    st.subheader("操作日誌列表")

    # 分頁設定
    page_size = st.selectbox("每頁顯示", [10, 25, 50, 100], index=1)
    total_pages = (len(logs) + page_size - 1) // page_size

    if total_pages > 1:
        page = st.number_input("頁碼", min_value=1, max_value=total_pages, value=1) - 1
    else:
        page = 0

    # 取得當前頁資料
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(logs))
    page_logs = logs[start_idx:end_idx]

    # 轉換為 DataFrame 顯示
    if page_logs:
        df_data = []
        for log in page_logs:
            action_desc = log.get('action') or log.get('action_name', 'unknown')
            try:
                ts = _parse_timestamp(log.get('timestamp', 0))
                time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                time_str = 'unknown'

            df_data.append({
                '時間': time_str,
                '操作類型': log.get('action_type', 'unknown'),
                '操作描述': action_desc,
                '狀態': '成功' if log.get('success', True) else '失敗',
                '詳情': str(log.get('details', ''))[:50] + '...' if len(str(log.get('details', ''))) > 50 else str(log.get('details', ''))
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

        # 顯示分頁資訊
        if total_pages > 1:
            st.info(f"第 {page + 1} 頁，共 {total_pages} 頁，總計 {len(logs)} 筆記錄")
    else:
        st.info("當前頁沒有資料")

def render_logs_export(logs: List[Dict[str, Any]]):
    """渲染日誌匯出功能"""

    st.subheader("匯出操作日誌")

    if not logs:
        st.warning("沒有可匯出的日誌資料")
        return

    # 匯出格式選擇
    export_format = st.selectbox("選擇匯出格式", ["CSV", "JSON", "Excel"])

    if st.button("匯出日誌"):
        try:
            df_data = _logs_to_df_data(logs)

            if export_format == "CSV":
                df = pd.DataFrame(df_data)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="下載 CSV 檔案",
                    data=csv_data,
                    file_name=f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            elif export_format == "JSON":
                json_data = json.dumps(logs, ensure_ascii=False, indent=2)
                st.download_button(
                    label="下載 JSON 檔案",
                    data=json_data,
                    file_name=f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

            elif export_format == "Excel":
                df = pd.DataFrame(df_data)
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='操作日誌')
                excel_data = output.getvalue()
                st.download_button(
                    label="下載 Excel 檔案",
                    data=excel_data,
                    file_name=f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.success(f"{export_format} 檔案準備完成，請點擊下載按鈕")

        except Exception as e:
            st.error(f"匯出失敗: {e}")


def _logs_to_df_data(logs: List[Dict[str, Any]]) -> List[Dict]:
    """將日誌轉換為 DataFrame 格式資料"""
    df_data = []
    for log in logs:
        action_desc = log.get('action') or log.get('action_name', 'unknown')
        try:
            ts = _parse_timestamp(log.get('timestamp', 0))
            time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            time_str = 'unknown'

        df_data.append({
            '時間': time_str,
            '操作類型': log.get('action_type', 'unknown'),
            '操作描述': action_desc,
            '狀態': '成功' if log.get('success', True) else '失敗',
            '詳情': str(log.get('details', ''))
        })
    return df_data


def log_operation(action_type: str, action: str, details: Dict = None, success: bool = True):
    """記錄操作日誌"""
    try:
        logs_dir = get_operation_logs_dir()

        # 按日期建立日誌檔案
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = logs_dir / f"operations_{today}.json"

        # 建立日誌條目
        log_entry = {
            'timestamp': datetime.now().timestamp(),
            'action_type': action_type,
            'action': action,
            'details': details or {},
            'success': success,
        }

        # 讀取現有日誌
        existing_logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            except Exception:
                existing_logs = []

        # 新增日誌
        existing_logs.append(log_entry)

        # 寫入檔案
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        # 使用 logging 而非 print
        import logging
        logging.getLogger(__name__).warning(f"記錄操作日誌失敗: {e}")
        return False
