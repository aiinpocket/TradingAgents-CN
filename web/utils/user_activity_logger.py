"""
用戶操作行為記錄器
記錄用戶在系統中的各種操作行為，並保存到獨立的日誌文件中
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import streamlit as st
from dataclasses import dataclass, asdict
import threading
import os

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('user_activity')

@dataclass
class UserActivity:
    """用戶活動記錄"""
    timestamp: float
    username: str
    user_role: str
    action_type: str
    action_name: str
    details: Dict[str, Any]
    session_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    page_url: Optional[str] = None
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None

class UserActivityLogger:
    """用戶操作行為記錄器"""
    
    def __init__(self):
        self.activity_dir = Path(__file__).parent.parent / "data" / "user_activities"
        self.activity_dir.mkdir(parents=True, exist_ok=True)
        
        # 線程鎖，確保文件寫入安全
        self._lock = threading.Lock()
        
        # 活動類型定義
        self.activity_types = {
            "auth": "認證相關",
            "analysis": "股票分析",
            "config": "配置管理", 
            "navigation": "页面導航",
            "data_export": "數據導出",
            "user_management": "用戶管理",
            "system": "系統操作"
        }
        
        logger.info(f"✅ 用戶活動記錄器初始化完成")
        logger.info(f"📁 活動記錄目錄: {self.activity_dir}")
    
    def _get_activity_file_path(self, date: str = None) -> Path:
        """獲取活動記錄文件路徑"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.activity_dir / f"user_activities_{date}.jsonl"
    
    def _get_session_id(self) -> str:
        """獲取會話ID"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"session_{int(time.time())}_{id(st.session_state)}"
        return st.session_state.session_id
    
    def _get_user_info(self) -> Dict[str, str]:
        """獲取當前用戶信息"""
        user_info = st.session_state.get('user_info')
        if user_info is None:
            user_info = {}
        return {
            "username": user_info.get('username', 'anonymous'),
            "role": user_info.get('role', 'guest')
        }
    
    def _get_request_info(self) -> Dict[str, Optional[str]]:
        """獲取請求信息"""
        try:
            # 嘗試獲取請求信息（在Streamlit中可能有限）
            headers = st.context.headers if hasattr(st.context, 'headers') else {}
            return {
                "ip_address": headers.get('x-forwarded-for', headers.get('remote-addr')),
                "user_agent": headers.get('user-agent'),
                "page_url": st.session_state.get('current_page', 'unknown')
            }
        except:
            return {
                "ip_address": None,
                "user_agent": None, 
                "page_url": None
            }
    
    def log_activity(self, 
                    action_type: str,
                    action_name: str,
                    details: Dict[str, Any] = None,
                    success: bool = True,
                    error_message: str = None,
                    duration_ms: int = None) -> None:
        """
        記錄用戶活動
        
        Args:
            action_type: 活動類型 (auth, analysis, config, navigation, etc.)
            action_name: 活動名稱
            details: 活動詳細信息
            success: 操作是否成功
            error_message: 錯誤信息（如果有）
            duration_ms: 操作耗時（毫秒）
        """
        try:
            user_info = self._get_user_info()
            request_info = self._get_request_info()
            
            activity = UserActivity(
                timestamp=time.time(),
                username=user_info["username"],
                user_role=user_info["role"],
                action_type=action_type,
                action_name=action_name,
                details=details or {},
                session_id=self._get_session_id(),
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"],
                page_url=request_info["page_url"],
                duration_ms=duration_ms,
                success=success,
                error_message=error_message
            )
            
            self._write_activity(activity)
            
        except Exception as e:
            logger.error(f"❌ 記錄用戶活動失败: {e}")
    
    def _write_activity(self, activity: UserActivity) -> None:
        """寫入活動記錄到文件"""
        with self._lock:
            try:
                activity_file = self._get_activity_file_path()
                
                # 轉換為JSON格式
                activity_dict = asdict(activity)
                activity_dict['datetime'] = datetime.fromtimestamp(activity.timestamp).isoformat()
                
                # 追加寫入JSONL格式
                with open(activity_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(activity_dict, ensure_ascii=False) + '\n')
                
            except Exception as e:
                logger.error(f"❌ 寫入活動記錄失败: {e}")
    
    def log_login(self, username: str, success: bool, error_message: str = None) -> None:
        """記錄登錄活動"""
        self.log_activity(
            action_type="auth",
            action_name="user_login",
            details={"username": username},
            success=success,
            error_message=error_message
        )
    
    def log_logout(self, username: str) -> None:
        """記錄登出活動"""
        self.log_activity(
            action_type="auth",
            action_name="user_logout",
            details={"username": username}
        )
    
    def log_analysis_request(self, stock_code: str, analysis_type: str, success: bool = True, 
                           duration_ms: int = None, error_message: str = None) -> None:
        """記錄股票分析請求"""
        self.log_activity(
            action_type="analysis",
            action_name="stock_analysis",
            details={
                "stock_code": stock_code,
                "analysis_type": analysis_type
            },
            success=success,
            duration_ms=duration_ms,
            error_message=error_message
        )
    
    def log_page_visit(self, page_name: str, page_params: Dict[str, Any] = None) -> None:
        """記錄页面訪問"""
        self.log_activity(
            action_type="navigation",
            action_name="page_visit",
            details={
                "page_name": page_name,
                "page_params": page_params or {}
            }
        )
    
    def log_config_change(self, config_type: str, changes: Dict[str, Any]) -> None:
        """記錄配置更改"""
        self.log_activity(
            action_type="config",
            action_name="config_update",
            details={
                "config_type": config_type,
                "changes": changes
            }
        )
    
    def log_data_export(self, export_type: str, data_info: Dict[str, Any], 
                       success: bool = True, error_message: str = None) -> None:
        """記錄數據導出"""
        self.log_activity(
            action_type="data_export",
            action_name="export_data",
            details={
                "export_type": export_type,
                "data_info": data_info
            },
            success=success,
            error_message=error_message
        )
    
    def log_user_management(self, operation: str, target_user: str, 
                          success: bool = True, error_message: str = None) -> None:
        """記錄用戶管理操作"""
        self.log_activity(
            action_type="user_management",
            action_name=operation,
            details={"target_user": target_user},
            success=success,
            error_message=error_message
        )
    
    def get_user_activities(self, username: str = None, 
                          start_date: datetime = None,
                          end_date: datetime = None,
                          action_type: str = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        獲取用戶活動記錄
        
        Args:
            username: 用戶名過濾
            start_date: 開始日期
            end_date: 結束日期  
            action_type: 活動類型過濾
            limit: 返回記錄數限制
            
        Returns:
            活動記錄列表
        """
        activities = []
        
        try:
            # 確定要查詢的日期範围
            if start_date is None:
                start_date = datetime.now() - timedelta(days=7)  # 默認查詢最近7天
            if end_date is None:
                end_date = datetime.now()
            
            # 遍歷日期範围內的所有文件
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                date_str = current_date.strftime("%Y-%m-%d")
                activity_file = self._get_activity_file_path(date_str)
                
                if activity_file.exists():
                    activities.extend(self._read_activities_from_file(
                        activity_file, username, action_type, start_date, end_date
                    ))
                
                current_date += timedelta(days=1)
            
            # 按時間戳倒序排序
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # 應用限制
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"❌ 獲取用戶活動記錄失败: {e}")
            return []
    
    def _read_activities_from_file(self, file_path: Path, username: str = None,
                                 action_type: str = None, start_date: datetime = None,
                                 end_date: datetime = None) -> List[Dict[str, Any]]:
        """從文件讀取活動記錄"""
        activities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        activity = json.loads(line.strip())
                        
                        # 應用過濾條件
                        if username and activity.get('username') != username:
                            continue
                        
                        if action_type and activity.get('action_type') != action_type:
                            continue
                        
                        activity_time = datetime.fromtimestamp(activity['timestamp'])
                        if start_date and activity_time < start_date:
                            continue
                        if end_date and activity_time > end_date:
                            continue
                        
                        activities.append(activity)
                        
        except Exception as e:
            logger.error(f"❌ 讀取活動文件失败 {file_path}: {e}")
        
        return activities
    
    def get_activity_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        獲取活動統計信息
        
        Args:
            days: 統計天數
            
        Returns:
            統計信息字典
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        activities = self.get_user_activities(
            start_date=start_date,
            end_date=end_date,
            limit=10000  # 獲取更多記錄用於統計
        )
        
        # 統計分析
        stats = {
            "total_activities": len(activities),
            "unique_users": len(set(a['username'] for a in activities)),
            "activity_types": {},
            "daily_activities": {},
            "user_activities": {},
            "success_rate": 0,
            "average_duration": 0
        }
        
        # 按類型統計
        for activity in activities:
            action_type = activity.get('action_type', 'unknown')
            stats["activity_types"][action_type] = stats["activity_types"].get(action_type, 0) + 1
            
            # 按用戶統計
            username = activity.get('username', 'unknown')
            stats["user_activities"][username] = stats["user_activities"].get(username, 0) + 1
            
            # 按日期統計
            date_str = datetime.fromtimestamp(activity['timestamp']).strftime('%Y-%m-%d')
            stats["daily_activities"][date_str] = stats["daily_activities"].get(date_str, 0) + 1
        
        # 成功率統計
        successful_activities = sum(1 for a in activities if a.get('success', True))
        if activities:
            stats["success_rate"] = successful_activities / len(activities) * 100
        
        # 平均耗時統計
        durations = [a.get('duration_ms', 0) for a in activities if a.get('duration_ms')]
        if durations:
            stats["average_duration"] = sum(durations) / len(durations)
        
        return stats
    
    def cleanup_old_activities(self, days_to_keep: int = 90) -> int:
        """
        清理旧的活動記錄
        
        Args:
            days_to_keep: 保留天數
            
        Returns:
            刪除的文件數量
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        try:
            for activity_file in self.activity_dir.glob("user_activities_*.jsonl"):
                # 從文件名提取日期
                try:
                    date_str = activity_file.stem.replace("user_activities_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    if file_date < cutoff_date:
                        activity_file.unlink()
                        deleted_count += 1
                        logger.info(f"🗑️ 刪除旧活動記錄: {activity_file.name}")
                        
                except ValueError:
                    # 文件名格式不正確，跳過
                    continue
                    
        except Exception as e:
            logger.error(f"❌ 清理旧活動記錄失败: {e}")
        
        return deleted_count

# 全局用戶活動記錄器實例
user_activity_logger = UserActivityLogger()