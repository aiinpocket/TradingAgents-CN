"""
基於Redis的會話管理器 - 最可靠的跨頁面刷新狀態持久化方案
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
            # 首先檢查REDIS_ENABLED環境變量
            redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower()
            if redis_enabled != 'true':
                return False

            import redis

            # 從環境變量獲取Redis配置
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            redis_db = int(os.getenv('REDIS_DB', 0))
            
            # 創建Redis連接
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
                st.warning(f"⚠️ Redis連接失敗，使用文件儲存: {e}")
            return False
    
    def _get_session_key(self) -> str:
        """生成會話鍵"""
        try:
            # 嘗試獲取Streamlit的session信息
            if hasattr(st, 'session_state') and hasattr(st.session_state, '_get_session_id'):
                session_id = st.session_state._get_session_id()
                return f"{self.session_prefix}{session_id}"
            
            # 如果無法獲取session_id，使用IP+UserAgent的hash
            # 註意：這是一個fallback方案，可能不夠精確
            import streamlit.web.server.websocket_headers as wsh
            headers = wsh.get_websocket_headers()
            
            user_agent = headers.get('User-Agent', 'unknown')
            x_forwarded_for = headers.get('X-Forwarded-For', 'unknown')
            
            # 生成基於用戶信息的唯一標識
            unique_str = f"{user_agent}_{x_forwarded_for}_{int(time.time() / 3600)}"  # 按小時分組
            session_hash = hashlib.md5(unique_str.encode()).hexdigest()[:16]
            
            return f"{self.session_prefix}fallback_{session_hash}"
            
        except Exception:
            # 最後的fallback：使用時間戳
            timestamp_hash = hashlib.md5(str(int(time.time() / 3600)).encode()).hexdigest()[:16]
            return f"{self.session_prefix}timestamp_{timestamp_hash}"
    
    def save_analysis_state(self, analysis_id: str, status: str = "running",
                           stock_symbol: str = "", market_type: str = "",
                           form_config: Dict[str, Any] = None):
        """保存分析狀態和表單配置"""
        try:
            session_data = {
                "analysis_id": analysis_id,
                "status": status,
                "stock_symbol": stock_symbol,
                "market_type": market_type,
                "timestamp": time.time(),
                "last_update": time.time()
            }

            # 添加表單配置
            if form_config:
                session_data["form_config"] = form_config
            
            session_key = self._get_session_key()
            
            if self.use_redis:
                # 保存到Redis，設置過期時間
                self.redis_client.setex(
                    session_key,
                    self.max_age_hours * 3600,  # 過期時間（秒）
                    json.dumps(session_data)
                )
            else:
                # 保存到文件（fallback）
                self._save_to_file(session_key, session_data)
            
            # 同時保存到session state
            st.session_state.current_analysis_id = analysis_id
            st.session_state.analysis_running = (status == 'running')
            st.session_state.last_stock_symbol = stock_symbol
            st.session_state.last_market_type = market_type
            
            return True
            
        except Exception as e:
            st.warning(f"⚠️ 保存會話狀態失敗: {e}")
            return False
    
    def load_analysis_state(self) -> Optional[Dict[str, Any]]:
        """加載分析狀態"""
        try:
            session_key = self._get_session_key()
            
            if self.use_redis:
                # 從Redis加載
                data = self.redis_client.get(session_key)
                if data:
                    return json.loads(data)
            else:
                # 從文件加載（fallback）
                return self._load_from_file(session_key)
            
            return None
            
        except Exception as e:
            st.warning(f"⚠️ 加載會話狀態失敗: {e}")
            return None
    
    def clear_analysis_state(self):
        """清除分析狀態"""
        try:
            session_key = self._get_session_key()
            
            if self.use_redis:
                # 從Redis刪除
                self.redis_client.delete(session_key)
            else:
                # 從文件刪除（fallback）
                self._delete_file(session_key)
            
            # 清除session state
            keys_to_remove = ['current_analysis_id', 'analysis_running', 'last_stock_symbol', 'last_market_type']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            
        except Exception as e:
            st.warning(f"⚠️ 清除會話狀態失敗: {e}")
    
    def _save_to_file(self, session_key: str, session_data: Dict[str, Any]):
        """保存到文件（fallback方案）"""
        try:
            import os
            os.makedirs("./data", exist_ok=True)
            
            filename = f"./data/{session_key.replace(':', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            st.warning(f"⚠️ 文件保存失敗: {e}")
    
    def _load_from_file(self, session_key: str) -> Optional[Dict[str, Any]]:
        """從文件加載（fallback方案）"""
        try:
            filename = f"./data/{session_key.replace(':', '_')}.json"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 檢查是否過期
                timestamp = data.get("timestamp", 0)
                if time.time() - timestamp < (self.max_age_hours * 3600):
                    return data
                else:
                    # 過期了，刪除文件
                    os.remove(filename)
            
            return None
            
        except Exception as e:
            st.warning(f"⚠️ 文件加載失敗: {e}")
            return None
    
    def _delete_file(self, session_key: str):
        """刪除文件（fallback方案）"""
        try:
            filename = f"./data/{session_key.replace(':', '_')}.json"
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            st.warning(f"⚠️ 文件刪除失敗: {e}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """獲取調試信息"""
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
                    
                    # 檢查會話數據
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

# 全局Redis會話管理器實例
redis_session_manager = RedisSessionManager()

def get_persistent_analysis_id() -> Optional[str]:
    """獲取持久化的分析ID（優先級：session state > Redis會話 > Redis分析數據）"""
    try:
        # 1. 首先檢查session state
        if st.session_state.get('current_analysis_id'):
            return st.session_state.current_analysis_id
        
        # 2. 檢查Redis會話數據
        session_data = redis_session_manager.load_analysis_state()
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
        st.warning(f"⚠️ 獲取持久化分析ID失敗: {e}")
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
        
        # 保存到Redis會話
        redis_session_manager.save_analysis_state(analysis_id, status, stock_symbol, market_type)
        
    except Exception as e:
        st.warning(f"⚠️ 設置持久化分析ID失敗: {e}")
