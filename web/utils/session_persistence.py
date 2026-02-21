"""
會話持久化管理器 - 不依賴Cookie的解決方案
使用Redis/文件儲存 + 瀏覽器指紋來實現跨頁面刷新的狀態持久化
"""

import streamlit as st
import hashlib
import time
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path

class SessionPersistenceManager:
    """會話持久化管理器"""
    
    def __init__(self):
        self.session_file_prefix = "session_"
        self.max_age_hours = 24  # 會話有效期24小時
        
    def _get_browser_fingerprint(self) -> str:
        """生成瀏覽器指紋（基於可用信息）"""
        try:
            # 獲取Streamlit的session信息
            session_id = st.runtime.get_instance().get_client(st.session_state._get_session_id()).session.id
            
            # 使用session_id作為指紋
            fingerprint = hashlib.md5(session_id.encode()).hexdigest()[:12]
            return f"browser_{fingerprint}"
            
        except Exception:
            # 如果無法獲取session_id，使用時間戳作為fallback
            timestamp = str(int(time.time() / 3600))  # 按小時分組
            fingerprint = hashlib.md5(timestamp.encode()).hexdigest()[:12]
            return f"fallback_{fingerprint}"
    
    def _get_session_file_path(self, fingerprint: str) -> str:
        """獲取會話文件路徑"""
        return f"./data/{self.session_file_prefix}{fingerprint}.json"
    
    def save_analysis_state(self, analysis_id: str, status: str = "running", 
                           stock_symbol: str = "", market_type: str = ""):
        """保存分析狀態到持久化儲存"""
        try:
            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            
            session_data = {
                "analysis_id": analysis_id,
                "status": status,
                "stock_symbol": stock_symbol,
                "market_type": market_type,
                "timestamp": time.time(),
                "fingerprint": fingerprint,
                "last_update": time.time()
            }
            
            # 保存到文件
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # 同時保存到session state
            st.session_state.current_analysis_id = analysis_id
            st.session_state.analysis_running = (status == 'running')
            st.session_state.last_stock_symbol = stock_symbol
            st.session_state.last_market_type = market_type
            
            return True
            
        except Exception as e:
            st.warning(f"保存會話狀態失敗: {e}")
            return False
    
    def load_analysis_state(self) -> Optional[Dict[str, Any]]:
        """從持久化儲存加載分析狀態"""
        try:
            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)
            
            # 檢查文件是否存在
            if not os.path.exists(session_file):
                return None
            
            # 讀取會話數據
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 檢查是否過期
            timestamp = session_data.get("timestamp", 0)
            if time.time() - timestamp > (self.max_age_hours * 3600):
                # 過期了，刪除文件
                os.remove(session_file)
                return None
            
            return session_data
            
        except Exception as e:
            st.warning(f"加載會話狀態失敗: {e}")
            return None
    
    def clear_analysis_state(self):
        """清除分析狀態"""
        try:
            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)
            
            # 刪除文件
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # 清除session state
            keys_to_remove = ['current_analysis_id', 'analysis_running', 'last_stock_symbol', 'last_market_type']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            
        except Exception as e:
            st.warning(f"清除會話狀態失敗: {e}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """獲取調試信息"""
        try:
            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)
            
            debug_info = {
                "fingerprint": fingerprint,
                "session_file": session_file,
                "file_exists": os.path.exists(session_file),
                "session_state_keys": [k for k in st.session_state.keys() if 'analysis' in k.lower()]
            }
            
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    debug_info["session_data"] = session_data
                    debug_info["age_hours"] = (time.time() - session_data.get("timestamp", 0)) / 3600
                except Exception as e:
                    debug_info["file_error"] = str(e)
            
            return debug_info
            
        except Exception as e:
            return {"error": str(e)}

# 全局會話持久化管理器實例
session_persistence = SessionPersistenceManager()

def get_persistent_analysis_id() -> Optional[str]:
    """獲取持久化的分析ID（優先級：session state > 會話文件 > Redis/文件）"""
    try:
        # 1. 首先檢查session state
        if st.session_state.get('current_analysis_id'):
            return st.session_state.current_analysis_id
        
        # 2. 檢查會話文件
        session_data = session_persistence.load_analysis_state()
        if session_data:
            analysis_id = session_data.get('analysis_id')
            if analysis_id:
                # 恢複到session state
                st.session_state.current_analysis_id = analysis_id
                st.session_state.analysis_running = (session_data.get('status') == 'running')
                st.session_state.last_stock_symbol = session_data.get('stock_symbol', '')
                st.session_state.last_market_type = session_data.get('market_type', '')
                return analysis_id
        
        # 3. 最後從Redis/文件恢複最新分析
        from .async_progress_tracker import get_latest_analysis_id
        latest_id = get_latest_analysis_id()
        if latest_id:
            st.session_state.current_analysis_id = latest_id
            return latest_id
        
        return None
        
    except Exception as e:
        st.warning(f"獲取持久化分析ID失敗: {e}")
        return None

def set_persistent_analysis_id(analysis_id: str, status: str = "running", 
                              stock_symbol: str = "", market_type: str = ""):
    """設置持久化的分析ID"""
    try:
        # 設置到session state
        st.session_state.current_analysis_id = analysis_id
        st.session_state.analysis_running = (status == 'running')
        st.session_state.last_stock_symbol = stock_symbol
        st.session_state.last_market_type = market_type
        
        # 保存到會話文件
        session_persistence.save_analysis_state(analysis_id, status, stock_symbol, market_type)
        
    except Exception as e:
        st.warning(f"設置持久化分析ID失敗: {e}")
