"""
Cookie管理器 - 解決Streamlit session state頁面刷新丟失的問題
"""

import streamlit as st
import json
import os
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

try:
    from streamlit_cookies_manager import EncryptedCookieManager
    COOKIES_AVAILABLE = True
except ImportError:
    COOKIES_AVAILABLE = False
    st.warning("streamlit-cookies-manager 未安裝，Cookie功能不可用")

class CookieManager:
    """Cookie管理器，用於持久化儲存分析狀態"""

    def __init__(self):
        self.cookie_name = "tradingagents_analysis_state"
        self.max_age_days = 7  # Cookie有效期7天

        # 初始化Cookie管理器
        if COOKIES_AVAILABLE:
            try:
                # 從環境變數讀取加密密鑰，若未設定則使用隨機生成的預設值
                cookie_secret = os.environ.get(
                    "COOKIE_SECRET_KEY",
                    "change_this_to_a_random_secret_key"
                )
                self.cookies = EncryptedCookieManager(
                    prefix="tradingagents_",
                    password=cookie_secret
                )

                # 檢查Cookie管理器是否準備就緒
                if not self.cookies.ready():
                    # 如果沒有準備就緒，先顯示等待信息，然後停止執行
                    st.info("正在初始化Cookie管理器，請稍候...")
                    st.stop()

            except Exception as e:
                st.warning(f"Cookie管理器初始化失敗: {e}")
                self.cookies = None
        else:
            self.cookies = None
    
    def set_analysis_state(self, analysis_id: str, status: str = "running",
                          stock_symbol: str = "", market_type: str = ""):
        """設置分析狀態到cookie"""
        try:
            state_data = {
                "analysis_id": analysis_id,
                "status": status,
                "stock_symbol": stock_symbol,
                "market_type": market_type,
                "timestamp": time.time(),
                "created_at": datetime.now().isoformat()
            }

            # 儲存到session state（作為備份）
            st.session_state[f"cookie_{self.cookie_name}"] = state_data

            # 使用專業的Cookie管理器設置cookie
            if self.cookies:
                self.cookies[self.cookie_name] = json.dumps(state_data)
                self.cookies.save()

            return True

        except Exception as e:
            st.error(f"設置分析狀態失敗: {e}")
            return False
    
    def get_analysis_state(self) -> Optional[Dict[str, Any]]:
        """從cookie獲取分析狀態"""
        try:
            # 首先嘗試從session state獲取（如果存在）
            session_data = st.session_state.get(f"cookie_{self.cookie_name}")
            if session_data:
                return session_data

            # 嘗試從cookie獲取
            if self.cookies and self.cookie_name in self.cookies:
                cookie_data = self.cookies[self.cookie_name]
                if cookie_data:
                    state_data = json.loads(cookie_data)

                    # 檢查是否過期（7天）
                    timestamp = state_data.get("timestamp", 0)
                    if time.time() - timestamp < (self.max_age_days * 24 * 3600):
                        # 恢複到session state
                        st.session_state[f"cookie_{self.cookie_name}"] = state_data
                        return state_data
                    else:
                        # 過期了，清除cookie
                        self.clear_analysis_state()

            return None

        except Exception as e:
            st.warning(f"獲取分析狀態失敗: {e}")
            return None
    
    def clear_analysis_state(self):
        """清除分析狀態"""
        try:
            # 清除session state
            if f"cookie_{self.cookie_name}" in st.session_state:
                del st.session_state[f"cookie_{self.cookie_name}"]

            # 清除cookie
            if self.cookies and self.cookie_name in self.cookies:
                del self.cookies[self.cookie_name]
                self.cookies.save()

        except Exception as e:
            st.warning(f"清除分析狀態失敗: {e}")

    def get_debug_info(self) -> Dict[str, Any]:
        """獲取調試信息"""
        debug_info = {
            "cookies_available": COOKIES_AVAILABLE,
            "cookies_ready": self.cookies.ready() if self.cookies else False,
            "cookies_object": self.cookies is not None,
            "session_state_keys": [k for k in st.session_state.keys() if 'cookie' in k.lower() or 'analysis' in k.lower()]
        }

        if self.cookies:
            try:
                debug_info["cookie_keys"] = list(self.cookies.keys())
                debug_info["cookie_count"] = len(self.cookies)
            except Exception as e:
                debug_info["cookie_error"] = str(e)

        return debug_info
    


# 全局cookie管理器實例
cookie_manager = CookieManager()

def get_persistent_analysis_id() -> Optional[str]:
    """獲取持久化的分析ID（優先級：session state > cookie > Redis/文件）"""
    try:
        # 1. 首先檢查session state
        if st.session_state.get('current_analysis_id'):
            return st.session_state.current_analysis_id
        
        # 2. 檢查cookie
        cookie_state = cookie_manager.get_analysis_state()
        if cookie_state:
            analysis_id = cookie_state.get('analysis_id')
            if analysis_id:
                # 恢複到session state
                st.session_state.current_analysis_id = analysis_id
                st.session_state.analysis_running = (cookie_state.get('status') == 'running')
                return analysis_id
        
        # 3. 最後從Redis/文件恢複
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
        
        # 設置到cookie
        cookie_manager.set_analysis_state(analysis_id, status, stock_symbol, market_type)
        
    except Exception as e:
        st.warning(f"設置持久化分析ID失敗: {e}")
