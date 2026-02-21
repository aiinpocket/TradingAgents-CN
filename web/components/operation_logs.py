"""
操作日誌管理組件
提供用戶操作日誌的查看和管理功能
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
    """獲取操作日誌目錄"""
    logs_dir = Path(__file__).parent.parent / "data" / "operation_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_user_activities_dir():
    """獲取用戶活動日誌目錄"""
    logs_dir = Path(__file__).parent.parent / "data" / "user_activities"
    return logs_dir

def load_operation_logs(start_date=None, end_date=None, username=None, action_type=None, limit=1000):
    """加載操作日誌（包含用戶活動日誌）"""
    all_logs = []
    
    # 1. 加載新的操作日誌（operation_logs目錄）
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
            st.error(f"讀取日誌文件失敗: {log_file.name} - {e}")
    
    for log_file in logs_dir.glob("*.jsonl"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        log_entry = json.loads(line.strip())
                        all_logs.append(log_entry)
        except Exception as e:
            st.error(f"讀取JSONL日誌文件失敗: {log_file.name} - {e}")
    
    # 2. 加載用戶活動日誌（user_activities目錄）
    user_activities_dir = get_user_activities_dir()
    if user_activities_dir.exists():
        for log_file in user_activities_dir.glob("*.jsonl"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            log_entry = json.loads(line.strip())
                            # 轉換用戶活動日誌格式以兼容操作日誌格式
                            converted_log = {
                                'timestamp': log_entry.get('timestamp'),
                                'username': log_entry.get('username'),
                                'user_role': log_entry.get('user_role'),
                                'action_type': log_entry.get('action_type'),
                                'action': log_entry.get('action_name'),
                                'details': log_entry.get('details', {}),
                                'success': log_entry.get('success', True),
                                'error_message': log_entry.get('error_message'),
                                'session_id': log_entry.get('session_id'),
                                'ip_address': log_entry.get('ip_address'),
                                'user_agent': log_entry.get('user_agent'),
                                'page_url': log_entry.get('page_url'),
                                'duration_ms': log_entry.get('duration_ms'),
                                'datetime': log_entry.get('datetime')
                            }
                            all_logs.append(converted_log)
            except Exception as e:
                st.error(f"讀取用戶活動日誌文件失敗: {log_file.name} - {e}")
    
    # 過濾日誌
    filtered_logs = []
    for log in all_logs:
        # 時間過濾
        if start_date or end_date:
            try:
                # 處理時間戳，支持字符串和數字格式
                timestamp = log.get('timestamp', 0)
                if isinstance(timestamp, str):
                    # 如果是字符串，嘗試轉換為浮點數
                    try:
                        timestamp = float(timestamp)
                    except (ValueError, TypeError):
                        # 如果轉換失敗，嘗試解析ISO格式的日期時間
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.timestamp()
                        except:
                            timestamp = 0
                
                log_date = datetime.fromtimestamp(timestamp).date()
                if start_date and log_date < start_date:
                    continue
                if end_date and log_date > end_date:
                    continue
            except Exception as e:
                # 如果時間戳處理失敗，跳過時間過濾
                pass
        
        # 用戶名過濾
        if username and log.get('username', '').lower() != username.lower():
            continue
        
        # 操作類型過濾
        if action_type and log.get('action_type', '') != action_type:
            continue
        
        filtered_logs.append(log)
    
    # 定義安全的時間戳轉換函數
    def safe_timestamp(log_entry):
        """安全地獲取時間戳，確保返回數字類型"""
        timestamp = log_entry.get('timestamp', 0)
        if isinstance(timestamp, str):
            try:
                return float(timestamp)
            except (ValueError, TypeError):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    return dt.timestamp()
                except:
                    return 0
        return timestamp if isinstance(timestamp, (int, float)) else 0
    
    # 按時間戳排序（最新的在前）
    filtered_logs.sort(key=safe_timestamp, reverse=True)
    
    # 限制數量
    return filtered_logs[:limit]

def render_operation_logs():
    """渲染操作日誌管理界面"""
    
    # 檢查權限
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from utils.auth_manager import auth_manager
        
        if not auth_manager or not auth_manager.check_permission("admin"):
            st.error("❌ 您沒有權限訪問操作日誌")
            st.info("💡 提示：操作日誌功能需要 'admin' 權限")
            return
    except Exception as e:
        st.error(f"❌ 權限檢查失敗: {e}")
        return
    
    st.title("📋 操作日誌管理")
    
    # 側邊欄過濾選項
    with st.sidebar:
        st.header("🔍 過濾選項")
        
        # 日期範围選擇
        date_range = st.selectbox(
            "📅 時間範围",
            ["最近1天", "最近3天", "最近7天", "最近30天", "自定義"],
            index=2
        )
        
        if date_range == "自定義":
            start_date = st.date_input("開始日期", datetime.now() - timedelta(days=7))
            end_date = st.date_input("結束日期", datetime.now())
        else:
            days_map = {"最近1天": 1, "最近3天": 3, "最近7天": 7, "最近30天": 30}
            days = days_map[date_range]
            end_date = datetime.now().date()
            start_date = (datetime.now() - timedelta(days=days)).date()
        
        # 用戶過濾
        username_filter = st.text_input("👤 用戶名過濾", placeholder="留空顯示所有用戶")
        
        # 操作類型過濾
        action_type_filter = st.selectbox(
            "🔧 操作類型",
            ["全部", "auth", "analysis", "navigation", "config", "data_export", "user_management", "system", "login", "logout", "export", "admin"]
        )
        
        if action_type_filter == "全部":
            action_type_filter = None
    
    # 加載操作日誌
    logs = load_operation_logs(
        start_date=start_date,
        end_date=end_date,
        username=username_filter if username_filter else None,
        action_type=action_type_filter,
        limit=1000
    )
    
    if not logs:
        st.warning("📭 未找到符合條件的操作日誌")
        return
    
    # 顯示統計概覽
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 總操作數", len(logs))
    
    with col2:
        unique_users = len(set(log.get('username', 'unknown') for log in logs))
        st.metric("👥 活躍用戶", unique_users)
    
    with col3:
        successful_ops = sum(1 for log in logs if log.get('success', True))
        success_rate = (successful_ops / len(logs) * 100) if logs else 0
        st.metric("✅ 成功率", f"{success_rate:.1f}%")
    
    with col4:
        # 安全處理近1小時的日誌統計
        recent_logs = []
        for log in logs:
            try:
                timestamp = log.get('timestamp', 0)
                if isinstance(timestamp, str):
                    try:
                        timestamp = float(timestamp)
                    except (ValueError, TypeError):
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.timestamp()
                        except:
                            continue
                if datetime.fromtimestamp(timestamp) > datetime.now() - timedelta(hours=1):
                    recent_logs.append(log)
            except:
                continue
        st.metric("🕐 近1小時", len(recent_logs))
    
    # 標簽页
    tab1, tab2, tab3 = st.tabs(["📈 統計圖表", "📋 日誌列表", "📤 導出數據"])
    
    with tab1:
        render_logs_charts(logs)
    
    with tab2:
        render_logs_list(logs)
    
    with tab3:
        render_logs_export(logs)

def render_logs_charts(logs: List[Dict[str, Any]]):
    """渲染日誌統計圖表"""
    
    # 按操作類型統計
    st.subheader("📊 按操作類型統計")
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
    st.subheader("📅 按時間統計")
    daily_logs = {}
    for log in logs:
        # 安全處理時間戳
        try:
            timestamp = log.get('timestamp', 0)
            if isinstance(timestamp, str):
                try:
                    timestamp = float(timestamp)
                except (ValueError, TypeError):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.timestamp()
                    except:
                        timestamp = 0
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except:
            date_str = 'unknown'
        
        if date_str != 'unknown':
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
    
    # 按用戶統計
    st.subheader("👥 按用戶統計")
    user_logs = {}
    for log in logs:
        username = log.get('username', 'unknown')
        user_logs[username] = user_logs.get(username, 0) + 1
    
    if user_logs:
        # 只顯示前10個最活躍的用戶
        top_users = sorted(user_logs.items(), key=lambda x: x[1], reverse=True)[:10]
        usernames = [item[0] for item in top_users]
        counts = [item[1] for item in top_users]
        
        fig_bar = px.bar(
            x=counts,
            y=usernames,
            orientation='h',
            title="用戶操作排行榜 (前10名)",
            labels={'x': '操作數量', 'y': '用戶名'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

def render_logs_list(logs: List[Dict[str, Any]]):
    """渲染日誌列表"""
    
    st.subheader("📋 操作日誌列表")
    
    # 分页設置
    page_size = st.selectbox("每页顯示", [10, 25, 50, 100], index=1)
    total_pages = (len(logs) + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.number_input("页碼", min_value=1, max_value=total_pages, value=1) - 1
    else:
        page = 0
    
    # 獲取當前页數據
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(logs))
    page_logs = logs[start_idx:end_idx]
    
    # 轉換為DataFrame顯示
    if page_logs:
        df_data = []
        for log in page_logs:
            # 獲取操作描述，兼容不同格式
            action_desc = log.get('action') or log.get('action_name', 'unknown')
            
            # 處理時間戳顯示
            try:
                timestamp = log.get('timestamp', 0)
                if isinstance(timestamp, str):
                    try:
                        timestamp = float(timestamp)
                    except (ValueError, TypeError):
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.timestamp()
                        except:
                            timestamp = 0
                time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = 'unknown'
            
            df_data.append({
                '時間': time_str,
                '用戶': log.get('username', 'unknown'),
                '角色': log.get('user_role', 'unknown'),
                '操作類型': log.get('action_type', 'unknown'),
                '操作描述': action_desc,
                '狀態': '✅ 成功' if log.get('success', True) else '❌ 失敗',
                '詳情': str(log.get('details', ''))[:50] + '...' if len(str(log.get('details', ''))) > 50 else str(log.get('details', ''))
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # 顯示分页信息
        if total_pages > 1:
            st.info(f"第 {page + 1} 页，共 {total_pages} 页，總計 {len(logs)} 條記錄")
    else:
        st.info("當前页沒有數據")

def render_logs_export(logs: List[Dict[str, Any]]):
    """渲染日誌導出功能"""
    
    st.subheader("📤 導出操作日誌")
    
    if not logs:
        st.warning("沒有可導出的日誌數據")
        return
    
    # 導出格式選擇
    export_format = st.selectbox("選擇導出格式", ["CSV", "JSON", "Excel"])
    
    if st.button("📥 導出日誌"):
        try:
            if export_format == "CSV":
                # 轉換為DataFrame
                df_data = []
                for log in logs:
                    # 獲取操作描述，兼容不同格式
                    action_desc = log.get('action') or log.get('action_name', 'unknown')
                    
                    # 處理時間戳顯示
                    try:
                        timestamp = log.get('timestamp', 0)
                        if isinstance(timestamp, str):
                            try:
                                timestamp = float(timestamp)
                            except (ValueError, TypeError):
                                try:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    timestamp = dt.timestamp()
                                except:
                                    timestamp = 0
                        time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        time_str = 'unknown'
                    
                    df_data.append({
                        '時間': time_str,
                        '用戶': log.get('username', 'unknown'),
                        '角色': log.get('user_role', 'unknown'),
                        '操作類型': log.get('action_type', 'unknown'),
                        '操作描述': action_desc,
                        '狀態': '成功' if log.get('success', True) else '失敗',
                        '詳情': str(log.get('details', ''))
                    })
                
                df = pd.DataFrame(df_data)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="下載 CSV 文件",
                    data=csv_data,
                    file_name=f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            elif export_format == "JSON":
                json_data = json.dumps(logs, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="下載 JSON 文件",
                    data=json_data,
                    file_name=f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            elif export_format == "Excel":
                # 轉換為DataFrame
                df_data = []
                for log in logs:
                    # 獲取操作描述，兼容不同格式
                    action_desc = log.get('action') or log.get('action_name', 'unknown')
                    
                    # 處理時間戳顯示
                    try:
                        timestamp = log.get('timestamp', 0)
                        if isinstance(timestamp, str):
                            try:
                                timestamp = float(timestamp)
                            except (ValueError, TypeError):
                                try:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    timestamp = dt.timestamp()
                                except:
                                    timestamp = 0
                        time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        time_str = 'unknown'
                    
                    df_data.append({
                        '時間': time_str,
                        '用戶': log.get('username', 'unknown'),
                        '角色': log.get('user_role', 'unknown'),
                        '操作類型': log.get('action_type', 'unknown'),
                        '操作描述': action_desc,
                        '狀態': '成功' if log.get('success', True) else '失敗',
                        '詳情': str(log.get('details', ''))
                    })
                
                df = pd.DataFrame(df_data)
                
                # 使用BytesIO創建Excel文件
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='操作日誌')
                
                excel_data = output.getvalue()
                
                st.download_button(
                    label="下載 Excel 文件",
                    data=excel_data,
                    file_name=f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"✅ {export_format} 文件準備完成，請點擊下載按鈕")
            
        except Exception as e:
            st.error(f"❌ 導出失敗: {e}")

def log_operation(username: str, action_type: str, action: str, details: Dict = None, success: bool = True):
    """記錄操作日誌"""
    try:
        logs_dir = get_operation_logs_dir()
        
        # 按日期創建日誌文件
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = logs_dir / f"operations_{today}.json"
        
        # 創建日誌條目
        log_entry = {
            'timestamp': datetime.now().timestamp(),
            'username': username,
            'action_type': action_type,
            'action': action,
            'details': details or {},
            'success': success,
            'ip_address': None,  # 可以後續添加IP地址記錄
            'user_agent': None   # 可以後續添加用戶代理記錄
        }
        
        # 讀取現有日誌
        existing_logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            except:
                existing_logs = []
        
        # 添加新日誌
        existing_logs.append(log_entry)
        
        # 寫入文件
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"記錄操作日誌失敗: {e}")
        return False