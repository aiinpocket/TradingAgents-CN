"""
智能會話管理器 - 自動選擇最佳儲存方案
優先級：Redis > 文件儲存
"""

import streamlit as st
import os
from typing import Optional, Dict, Any

class SmartSessionManager:
    """智能會話管理器"""
    
    def __init__(self):
        self.redis_manager = None
        self.file_manager = None
        self.use_redis = self._init_redis_manager()
        self._init_file_manager()
        
    def _init_redis_manager(self) -> bool:
        """嘗試初始化Redis管理器"""
        try:
            from .redis_session_manager import redis_session_manager
            
            # 測試Redis連接
            if redis_session_manager.use_redis:
                self.redis_manager = redis_session_manager
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def _init_file_manager(self):
        """初始化文件管理器"""
        try:
            from .file_session_manager import file_session_manager
            self.file_manager = file_session_manager
        except Exception as e:
            st.error(f"文件會話管理器初始化失敗: {e}")
    
    def save_analysis_state(self, analysis_id: str, status: str = "running",
                           stock_symbol: str = "", market_type: str = "",
                           form_config: Dict[str, Any] = None):
        """保存分析狀態和表單配置"""
        success = False
        
        # 優先使用Redis
        if self.use_redis and self.redis_manager:
            try:
                success = self.redis_manager.save_analysis_state(analysis_id, status, stock_symbol, market_type, form_config)
                if success:
                    return True
            except Exception as e:
                st.warning(f"Redis保存失敗，切換到文件儲存: {e}")
                self.use_redis = False

        # 使用文件儲存作為fallback
        if self.file_manager:
            try:
                success = self.file_manager.save_analysis_state(analysis_id, status, stock_symbol, market_type, form_config)
                return success
            except Exception as e:
                st.error(f"文件儲存也失敗了: {e}")
                return False
        
        return False
    
    def load_analysis_state(self) -> Optional[Dict[str, Any]]:
        """加載分析狀態"""
        # 優先從Redis加載
        if self.use_redis and self.redis_manager:
            try:
                data = self.redis_manager.load_analysis_state()
                if data:
                    return data
            except Exception as e:
                st.warning(f"Redis加載失敗，切換到文件儲存: {e}")
                self.use_redis = False
        
        # 從文件儲存加載
        if self.file_manager:
            try:
                return self.file_manager.load_analysis_state()
            except Exception as e:
                st.error(f"文件儲存加載失敗: {e}")
                return None
        
        return None
    
    def clear_analysis_state(self):
        """清除分析狀態"""
        # 清除Redis中的數據
        if self.use_redis and self.redis_manager:
            try:
                self.redis_manager.clear_analysis_state()
            except Exception as e:
                pass
        
        # 清除文件中的數據
        if self.file_manager:
            try:
                self.file_manager.clear_analysis_state()
            except Exception as e:
                pass
    
    def get_debug_info(self) -> Dict[str, Any]:
        """獲取調試信息"""
        debug_info = {
            "storage_type": "Redis" if self.use_redis else "文件儲存",
            "redis_available": self.redis_manager is not None,
            "file_manager_available": self.file_manager is not None,
            "use_redis": self.use_redis
        }
        
        # 獲取當前使用的管理器的調試信息
        if self.use_redis and self.redis_manager:
            try:
                redis_debug = self.redis_manager.get_debug_info()
                debug_info.update({"redis_debug": redis_debug})
            except Exception as e:
                debug_info["redis_debug_error"] = str(e)
        
        if self.file_manager:
            try:
                file_debug = self.file_manager.get_debug_info()
                debug_info.update({"file_debug": file_debug})
            except Exception as e:
                debug_info["file_debug_error"] = str(e)
        
        return debug_info

# 全局智能會話管理器實例
smart_session_manager = SmartSessionManager()

def get_persistent_analysis_id() -> Optional[str]:
    """獲取持久化的分析ID"""
    try:
        # 1. 首先檢查session state
        if st.session_state.get('current_analysis_id'):
            return st.session_state.current_analysis_id
        
        # 2. 從會話儲存加載
        session_data = smart_session_manager.load_analysis_state()
        if session_data:
            analysis_id = session_data.get('analysis_id')
            if analysis_id:
                # 恢複到session state
                st.session_state.current_analysis_id = analysis_id
                st.session_state.analysis_running = (session_data.get('status') == 'running')
                st.session_state.last_stock_symbol = session_data.get('stock_symbol', '')
                st.session_state.last_market_type = session_data.get('market_type', '')
                return analysis_id
        
        # 3. 最後從分析數據恢複最新分析
        try:
            from .async_progress_tracker import get_latest_analysis_id
            latest_id = get_latest_analysis_id()
            if latest_id:
                st.session_state.current_analysis_id = latest_id
                return latest_id
        except Exception as e:
            pass
        
        return None
        
    except Exception as e:
        st.warning(f"獲取持久化分析ID失敗: {e}")
        return None

def set_persistent_analysis_id(analysis_id: str, status: str = "running",
                              stock_symbol: str = "", market_type: str = "",
                              form_config: Dict[str, Any] = None):
    """設置持久化的分析ID和表單配置"""
    try:
        # 設置到session state
        st.session_state.current_analysis_id = analysis_id
        st.session_state.analysis_running = (status == 'running')
        st.session_state.last_stock_symbol = stock_symbol
        st.session_state.last_market_type = market_type

        # 保存表單配置到session state
        if form_config:
            st.session_state.form_config = form_config

        # 保存到會話儲存
        smart_session_manager.save_analysis_state(analysis_id, status, stock_symbol, market_type, form_config)

    except Exception as e:
        st.warning(f"設置持久化分析ID失敗: {e}")

def get_session_debug_info() -> Dict[str, Any]:
    """獲取會話管理器調試信息"""
    return smart_session_manager.get_debug_info()
