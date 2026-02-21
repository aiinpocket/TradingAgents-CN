"""
智慧會話管理器 - 自動選擇最佳儲存方案
優先級：Redis > 檔案儲存
"""

import logging
import streamlit as st
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SmartSessionManager:
    """智慧會話管理器"""
    
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
        """初始化檔案管理器"""
        try:
            from .file_session_manager import file_session_manager
            self.file_manager = file_session_manager
        except Exception as e:
            st.error(f"檔案會話管理器初始化失敗: {e}")
    
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
                st.warning(f"Redis保存失敗，切換到檔案儲存: {e}")
                self.use_redis = False

        # 使用檔案儲存作為fallback
        if self.file_manager:
            try:
                success = self.file_manager.save_analysis_state(analysis_id, status, stock_symbol, market_type, form_config)
                return success
            except Exception as e:
                st.error(f"檔案儲存也失敗了: {e}")
                return False
        
        return False
    
    def load_analysis_state(self) -> Optional[Dict[str, Any]]:
        """載入分析狀態"""
        # 優先從Redis載入
        if self.use_redis and self.redis_manager:
            try:
                data = self.redis_manager.load_analysis_state()
                if data:
                    return data
            except Exception as e:
                st.warning(f"Redis載入失敗，切換到檔案儲存: {e}")
                self.use_redis = False
        
        # 從檔案儲存載入
        if self.file_manager:
            try:
                return self.file_manager.load_analysis_state()
            except Exception as e:
                st.error(f"檔案儲存載入失敗: {e}")
                return None
        
        return None
    
    def clear_analysis_state(self):
        """清除分析狀態"""
        # 清除Redis中的資料
        if self.use_redis and self.redis_manager:
            try:
                self.redis_manager.clear_analysis_state()
            except Exception as e:
                logger.debug(f"清除Redis分析狀態失敗: {e}")

        # 清除檔案中的資料
        if self.file_manager:
            try:
                self.file_manager.clear_analysis_state()
            except Exception as e:
                logger.debug(f"清除檔案分析狀態失敗: {e}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """取得除錯資訊"""
        debug_info = {
            "storage_type": "Redis" if self.use_redis else "檔案儲存",
            "redis_available": self.redis_manager is not None,
            "file_manager_available": self.file_manager is not None,
            "use_redis": self.use_redis
        }
        
        # 取得當前使用的管理器的除錯資訊
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

# 全局智慧會話管理器實例
smart_session_manager = SmartSessionManager()

def get_persistent_analysis_id() -> Optional[str]:
    """取得持久化的分析ID"""
    try:
        # 1. 首先檢查session state
        if st.session_state.get('current_analysis_id'):
            return st.session_state.current_analysis_id
        
        # 2. 從會話儲存載入
        session_data = smart_session_manager.load_analysis_state()
        if session_data:
            analysis_id = session_data.get('analysis_id')
            if analysis_id:
                # 恢復到session state
                st.session_state.current_analysis_id = analysis_id
                st.session_state.analysis_running = (session_data.get('status') == 'running')
                st.session_state.last_stock_symbol = session_data.get('stock_symbol', '')
                st.session_state.last_market_type = session_data.get('market_type', '')
                return analysis_id
        
        # 3. 最後從分析資料恢復最新分析
        try:
            from .async_progress_tracker import get_latest_analysis_id
            latest_id = get_latest_analysis_id()
            if latest_id:
                st.session_state.current_analysis_id = latest_id
                return latest_id
        except Exception as e:
            logger.debug(f"從分析資料恢復最新分析失敗: {e}")

        return None

    except Exception as e:
        st.warning(f"取得持久化分析ID失敗: {e}")
        return None

def set_persistent_analysis_id(analysis_id: str, status: str = "running",
                              stock_symbol: str = "", market_type: str = "",
                              form_config: Dict[str, Any] = None):
    """設定持久化的分析ID和表單配置"""
    try:
        # 設定到session state
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
        st.warning(f"設定持久化分析ID失敗: {e}")

