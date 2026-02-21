"""
基於Redis的會話管理器 - 最可靠的跨頁面重新整理狀態持久化方案
"""

import streamlit as st
import json
import time
import hashlib
import os
from typing import Optional, Dict, Any

class RedisSessionManager:
    """基於Redis的會話管理器"""
    
    def __init__(self):
        self.redis_client = None
        self.use_redis = self._init_redis()
        self.session_prefix = "streamlit_session:"
        self.max_age_hours = 24  # 會話有效期24小時
        
    def _init_redis(self) -> bool:
        """初始化Redis連接"""
        try:
            # 首先檢查REDIS_ENABLED環境變數
            redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower()
            if redis_enabled != 'true':
                return False

            import redis

            # 從環境變數取得Redis配置
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            redis_db = int(os.getenv('REDIS_DB', 0))
            
            # 建立Redis連接
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # 測試連接
            self.redis_client.ping()
            return True
            
        except Exception as e:
            # 只有在Redis啟用時才顯示連接失敗警告
            redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower()
            if redis_enabled == 'true':
                st.warning(f"Redis連接失敗，使用檔案儲存: {e}")
            return False
    
    def _get_session_key(self) -> str:
        """生成會話鍵"""
        try:
            # 嘗試取得Streamlit的session資訊
            if hasattr(st, 'session_state') and hasattr(st.session_state, '_get_session_id'):
                session_id = st.session_state._get_session_id()
                return f"{self.session_prefix}{session_id}"
            
            # 如果無法取得session_id，使用IP+UserAgent的hash
            # 註意：這是一個fallback方案，可能不夠精確
            import streamlit.web.server.websocket_headers as wsh
            headers = wsh.get_websocket_headers()
            
            user_agent = headers.get('User-Agent', 'unknown')
            x_forwarded_for = headers.get('X-Forwarded-For', 'unknown')
            
            # 生成基於使用者資訊的唯一標識
            unique_str = f"{user_agent}_{x_forwarded_for}_{int(time.time() / 3600)}"  # 按小時分組
            session_hash = hashlib.sha256(unique_str.encode()).hexdigest()[:16]
            
            return f"{self.session_prefix}fallback_{session_hash}"
            
        except Exception as e:
            # 最後的fallback：使用時間戳
            timestamp_hash = hashlib.sha256(str(int(time.time() / 3600)).encode()).hexdigest()[:16]
            return f"{self.session_prefix}timestamp_{timestamp_hash}"
    
    def save_analysis_state(self, analysis_id: str, status: str = "running",
                           stock_symbol: str = "", market_type: str = "",
                           form_config: Dict[str, Any] = None):
        """保存分析狀態到 Redis（不含 file fallback，由 SmartSessionManager 處理）"""
        if not self.use_redis:
            return False

        try:
            session_data = {
                "analysis_id": analysis_id,
                "status": status,
                "stock_symbol": stock_symbol,
                "market_type": market_type,
                "timestamp": time.time(),
                "last_update": time.time()
            }

            if form_config:
                session_data["form_config"] = form_config

            session_key = self._get_session_key()
            self.redis_client.setex(
                session_key,
                self.max_age_hours * 3600,
                json.dumps(session_data)
            )

            st.session_state.current_analysis_id = analysis_id
            st.session_state.analysis_running = (status == 'running')
            st.session_state.last_stock_symbol = stock_symbol
            st.session_state.last_market_type = market_type

            return True

        except Exception as e:
            st.warning(f"Redis 保存會話狀態失敗: {e}")
            return False

    def load_analysis_state(self) -> Optional[Dict[str, Any]]:
        """從 Redis 載入分析狀態"""
        if not self.use_redis:
            return None

        try:
            session_key = self._get_session_key()
            data = self.redis_client.get(session_key)
            if data:
                return json.loads(data)
            return None

        except Exception as e:
            st.warning(f"Redis 載入會話狀態失敗: {e}")
            return None

    def clear_analysis_state(self):
        """清除 Redis 中的分析狀態"""
        if not self.use_redis:
            return

        try:
            session_key = self._get_session_key()
            self.redis_client.delete(session_key)

            keys_to_remove = ['current_analysis_id', 'analysis_running', 'last_stock_symbol', 'last_market_type']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]

        except Exception as e:
            st.warning(f"清除 Redis 會話狀態失敗: {e}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """取得除錯資訊"""
        try:
            session_key = self._get_session_key()
            
            debug_info = {
                "use_redis": self.use_redis,
                "session_key": session_key,
                "redis_connected": False,
                "session_state_keys": [k for k in st.session_state.keys() if 'analysis' in k.lower()]
            }
            
            if self.use_redis and self.redis_client:
                try:
                    self.redis_client.ping()
                    debug_info["redis_connected"] = True
                    debug_info["redis_info"] = {
                        "host": os.getenv('REDIS_HOST', 'localhost'),
                        "port": os.getenv('REDIS_PORT', 6379),
                        "db": os.getenv('REDIS_DB', 0)
                    }
                    
                    # 檢查會話資料
                    data = self.redis_client.get(session_key)
                    if data:
                        debug_info["session_data"] = json.loads(data)
                    else:
                        debug_info["session_data"] = None
                        
                except Exception as e:
                    debug_info["redis_error"] = str(e)
            
            return debug_info
            
        except Exception as e:
            return {"error": str(e)}

# 全域 Redis 會話管理器實例（由 SmartSessionManager 使用）
redis_session_manager = RedisSessionManager()
