"""
用戶認證管理器
處理用戶登錄、權限驗證等功能
支持前端緩存登錄狀態，10分鐘無操作自動失效
"""

import streamlit as st
import hashlib
import os
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import time

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('auth')

# 導入用戶活動記錄器
try:
    from .user_activity_logger import user_activity_logger
except ImportError:
    user_activity_logger = None
    logger.warning("用戶活動記錄器導入失敗")

class AuthManager:
    """用戶認證管理器"""
    
    def __init__(self):
        self.users_file = Path(__file__).parent.parent / "config" / "users.json"
        # 會話逾時時間（秒），預設 600 秒 = 10 分鐘
        self.session_timeout = 600
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """確保用戶配置文件存在"""
        self.users_file.parent.mkdir(exist_ok=True)
        
        if not self.users_file.exists():
            # 創建默認用戶配置
            default_users = {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "role": "admin",
                    "permissions": ["analysis", "config", "admin"],
                    "created_at": time.time()
                },
                "user": {
                    "password_hash": self._hash_password("user123"),
                    "role": "user", 
                    "permissions": ["analysis"],
                    "created_at": time.time()
                }
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
            
            logger.info(f"用戶認證系統初始化完成")
            logger.info(f"用戶配置文件: {self.users_file}")
    
    def _inject_auth_cache_js(self):
        """註入前端認證緩存JavaScript代碼"""
        js_code = """
        <script>
        // 認證緩存管理
        window.AuthCache = {
            // 保存登錄狀態到localStorage
            saveAuth: function(userInfo) {
                const authData = {
                    userInfo: userInfo,
                    loginTime: Date.now(),
                    lastActivity: Date.now()
                };
                localStorage.setItem('tradingagents_auth', JSON.stringify(authData));
                console.log('登錄狀態已保存到前端緩存');
            },
            
            // 從localStorage獲取登錄狀態
            getAuth: function() {
                try {
                    const authData = localStorage.getItem('tradingagents_auth');
                    if (!authData) return null;
                    
                    const data = JSON.parse(authData);
                    const now = Date.now();
                    const timeout = 10 * 60 * 1000; // 10分鐘
                    
                    // 檢查是否超時
                    if (now - data.lastActivity > timeout) {
                        this.clearAuth();
                        console.log('登錄狀態已過期，自動清除');
                        return null;
                    }
                    
                    // 更新最後活動時間
                    data.lastActivity = now;
                    localStorage.setItem('tradingagents_auth', JSON.stringify(data));
                    
                    return data.userInfo;
                } catch (e) {
                    console.error('讀取登錄狀態失敗:', e);
                    this.clearAuth();
                    return null;
                }
            },
            
            // 清除登錄狀態
            clearAuth: function() {
                localStorage.removeItem('tradingagents_auth');
                console.log('登錄狀態已清除');
            },
            
            // 更新活動時間
            updateActivity: function() {
                const authData = localStorage.getItem('tradingagents_auth');
                if (authData) {
                    try {
                        const data = JSON.parse(authData);
                        data.lastActivity = Date.now();
                        localStorage.setItem('tradingagents_auth', JSON.stringify(data));
                    } catch (e) {
                        console.error('更新活動時間失敗:', e);
                    }
                }
            }
        };
        
        // 監聽用戶活動，更新最後活動時間
        ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
            document.addEventListener(event, function() {
                window.AuthCache.updateActivity();
            }, { passive: true });
        });
        
        // 頁面加載時檢查登錄狀態
        document.addEventListener('DOMContentLoaded', function() {
            const authInfo = window.AuthCache.getAuth();
            if (authInfo) {
                console.log('從前端緩存恢複登錄狀態:', authInfo.username);
                // 通知Streamlit恢複登錄狀態
                window.parent.postMessage({
                    type: 'restore_auth',
                    userInfo: authInfo
                }, '*');
            }
        });
        </script>
        """
        st.components.v1.html(js_code, height=0)
    
    def _hash_password(self, password: str) -> str:
        """密碼哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> Dict:
        """加載用戶配置"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加載用戶配置失敗: {e}")
            return {}
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        用戶認證
        
        Args:
            username: 用戶名
            password: 密碼
            
        Returns:
            (認證成功, 用戶信息)
        """
        users = self._load_users()
        
        if username not in users:
            logger.warning(f"用戶不存在: {username}")
            # 記錄登錄失敗
            if user_activity_logger:
                user_activity_logger.log_login(username, False, "用戶不存在")
            return False, None
        
        user_info = users[username]
        password_hash = self._hash_password(password)
        
        if password_hash == user_info["password_hash"]:
            logger.info(f"用戶登錄成功: {username}")
            # 記錄登錄成功
            if user_activity_logger:
                user_activity_logger.log_login(username, True)
            return True, {
                "username": username,
                "role": user_info["role"],
                "permissions": user_info["permissions"]
            }
        else:
            logger.warning(f"密碼錯誤: {username}")
            # 記錄登錄失敗
            if user_activity_logger:
                user_activity_logger.log_login(username, False, "密碼錯誤")
            return False, None
    
    def check_permission(self, permission: str) -> bool:
        """
        檢查當前用戶權限
        
        Args:
            permission: 權限名稱
            
        Returns:
            是否有權限
        """
        if not self.is_authenticated():
            return False
        
        user_info = st.session_state.get('user_info', {})
        permissions = user_info.get('permissions', [])
        
        return permission in permissions
    
    def is_authenticated(self) -> bool:
        """檢查用戶是否已認證"""
        # 首先檢查session_state中的認證狀態
        authenticated = st.session_state.get('authenticated', False)
        login_time = st.session_state.get('login_time', 0)
        current_time = time.time()
        
        logger.debug(f"[認證檢查] authenticated: {authenticated}, login_time: {login_time}, current_time: {current_time}")
        
        if authenticated:
            # 檢查會話超時
            time_elapsed = current_time - login_time
            logger.debug(f"[認證檢查] 會話時長: {time_elapsed:.1f}秒, 超時限制: {self.session_timeout}秒")
            
            if time_elapsed > self.session_timeout:
                logger.info(f"會話超時，自動登出 (已過時間: {time_elapsed:.1f}秒)")
                self.logout()
                return False
            
            logger.debug(f"[認證檢查] 用戶已認證且未超時")
            return True
        
        logger.debug(f"[認證檢查] 用戶未認證")
        return False
    
    def login(self, username: str, password: str) -> bool:
        """
        用戶登錄
        
        Args:
            username: 用戶名
            password: 密碼
            
        Returns:
            登錄是否成功
        """
        success, user_info = self.authenticate(username, password)
        
        if success:
            st.session_state.authenticated = True
            st.session_state.user_info = user_info
            st.session_state.login_time = time.time()
            
            # 保存到前端緩存 - 使用與前端JavaScript兼容的格式
            current_time_ms = int(time.time() * 1000)  # 轉換為毫秒
            auth_data = {
                "userInfo": user_info,  # 使用userInfo而不是user_info
                "loginTime": time.time(),
                "lastActivity": current_time_ms,  # 添加lastActivity字段
                "authenticated": True
            }
            
            save_to_cache_js = f"""
            <script>
            console.log('保存認證數據到localStorage');
            try {{
                const authData = {json.dumps(auth_data)};
                localStorage.setItem('tradingagents_auth', JSON.stringify(authData));
                console.log('認證數據已保存到localStorage:', authData);
            }} catch (e) {{
                console.error('保存認證數據失敗:', e);
            }}
            </script>
            """
            st.components.v1.html(save_to_cache_js, height=0)
            
            logger.info(f"用戶 {username} 登錄成功，已保存到前端緩存")
            return True
        else:
            st.session_state.authenticated = False
            st.session_state.user_info = None
            return False
    
    def logout(self):
        """用戶登出"""
        username = st.session_state.get('user_info', {}).get('username', 'unknown')
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.login_time = None
        
        # 清除前端緩存
        clear_cache_js = """
        <script>
        console.log('清除認證數據');
        try {
            localStorage.removeItem('tradingagents_auth');
            localStorage.removeItem('tradingagents_last_activity');
            console.log('認證數據已清除');
        } catch (e) {
            console.error('清除認證數據失敗:', e);
        }
        </script>
        """
        st.components.v1.html(clear_cache_js, height=0)
        
        logger.info(f"用戶 {username} 登出，已清除前端緩存")
        
        # 記錄登出活動
        if user_activity_logger:
            user_activity_logger.log_logout(username)
    
    def restore_from_cache(self, user_info: Dict, login_time: float = None) -> bool:
        """
        從前端緩存恢複登錄狀態
        
        Args:
            user_info: 用戶信息
            login_time: 原始登錄時間，如果為None則使用當前時間
            
        Returns:
            恢複是否成功
        """
        try:
            # 驗證用戶信息的有效性
            username = user_info.get('username')
            if not username:
                logger.warning(f"恢複失敗: 用戶信息中沒有用戶名")
                return False
            
            # 檢查用戶是否仍然存在
            users = self._load_users()
            if username not in users:
                logger.warning(f"嘗試恢複不存在的用戶: {username}")
                return False
            
            # 恢複登錄狀態，使用原始登錄時間或當前時間
            restore_time = login_time if login_time is not None else time.time()
            
            st.session_state.authenticated = True
            st.session_state.user_info = user_info
            st.session_state.login_time = restore_time
            
            logger.info(f"從前端緩存恢複用戶 {username} 的登錄狀態")
            logger.debug(f"[恢複狀態] login_time: {restore_time}, current_time: {time.time()}")
            return True
            
        except Exception as e:
            logger.error(f"從前端緩存恢複登錄狀態失敗: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict]:
        """獲取當前用戶信息"""
        if self.is_authenticated():
            return st.session_state.get('user_info')
        return None
    
    def require_permission(self, permission: str) -> bool:
        """
        要求特定權限，如果沒有權限則顯示錯誤信息
        
        Args:
            permission: 權限名稱
            
        Returns:
            是否有權限
        """
        if not self.check_permission(permission):
            st.error(f"您沒有 '{permission}'權限，請聯系管理員")
            return False
        return True

# 全局認證管理器實例
auth_manager = AuthManager()