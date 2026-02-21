"""
登錄組件
提供用戶登錄界面
"""

import streamlit as st
import time
import sys
from pathlib import Path
import base64

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 導入認證管理器 - 使用全局變量確保在整個模塊中可用
auth_manager = None

# 嘗試多種導入路徑
try:
    # 嘗試相對導入（從 web 目錄運行時）
    from ..utils.auth_manager import AuthManager, auth_manager as imported_auth_manager
    auth_manager = imported_auth_manager
except ImportError:
    try:
        # 嘗試從 web.utils 導入（從項目根目錄運行時）
        from web.utils.auth_manager import AuthManager, auth_manager as imported_auth_manager
        auth_manager = imported_auth_manager
    except ImportError:
        try:
            # 嘗試直接從 utils 導入
            from utils.auth_manager import AuthManager, auth_manager as imported_auth_manager
            auth_manager = imported_auth_manager
        except ImportError:
            try:
                # 嘗試絕對路徑導入
                import sys
                from pathlib import Path
                web_utils_path = Path(__file__).parent.parent / "utils"
                sys.path.insert(0, str(web_utils_path))
                from auth_manager import AuthManager, auth_manager as imported_auth_manager
                auth_manager = imported_auth_manager
            except ImportError:
                # 如果都失敗了，創建一個簡單的認證管理器
                class SimpleAuthManager:
                    """後備認證管理器，僅在主認證模組載入失敗時使用"""
                    # 預設帳號的密碼雜湊值（SHA256）
                    _default_credentials = {
                        "admin": {
                            "hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
                            "role": "admin"
                        },
                        "user": {
                            "hash": "e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446",
                            "role": "user"
                        }
                    }

                    def __init__(self):
                        self.authenticated = False
                        self.current_user = None

                    def is_authenticated(self):
                        return st.session_state.get('authenticated', False)

                    def authenticate(self, username, password):
                        import hashlib
                        cred = self._default_credentials.get(username)
                        if cred and hashlib.sha256(password.encode()).hexdigest() == cred["hash"]:
                            return True, {"username": username, "role": cred["role"]}
                        return False, None
                    
                    def logout(self):
                        st.session_state.authenticated = False
                        st.session_state.user_info = None
                    
                    def get_current_user(self):
                        return st.session_state.get('user_info')
                    
                    def require_permission(self, permission):
                        return self.is_authenticated()
                
                auth_manager = SimpleAuthManager()

def get_base64_image(image_path):
    """將圖片轉換為base64編碼"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def render_login_form():
    """渲染登錄表單"""
    
    # 現代化登錄頁面樣式
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .login-container {
        max-width: 550px;
        margin: 0.5rem auto;
        padding: 2.5rem 2rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .login-title {
        color: #2d3748;
        margin-bottom: 0.5rem;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        white-space: nowrap;
        overflow: visible;
        text-overflow: clip;
    }
    
    .login-subtitle {
        color: #718096;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 0;
    }
    
    .login-form {
        margin-top: 1rem;
    }
    
    .stTextInput > div > div > input {
        background: rgba(247, 250, 252, 0.8);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .login-tips {
        background: linear-gradient(135deg, #e6fffa 0%, #f0fff4 100%);
        border: 1px solid #9ae6b4;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1.5rem;
        text-align: center;
    }
    
    .login-tips-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.7);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #718096;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 主登錄容器
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <h1 class="login-title"> TradingAgents-CN</h1>
            <p class="login-subtitle">AI驅動的股票交易分析平台 · 讓投資更智能</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 登錄表單
    with st.container():
        st.markdown('<div class="login-form">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 用戶登錄")

            # 使用表單防止每次輸入都觸發頁面重新渲染
            with st.form(key="login_form", clear_on_submit=False):
                username = st.text_input(
                    "用戶名",
                    placeholder="請輸入您的用戶名（首次使用：admin）",
                    key="username_input",
                    label_visibility="collapsed"
                )
                password = st.text_input(
                    "密碼",
                    type="password",
                    placeholder="請輸入您的密碼（首次使用：admin123）",
                    key="password_input",
                    label_visibility="collapsed"
                )

                st.markdown("<br>", unsafe_allow_html=True)

                submit_button = st.form_submit_button("立即登錄", use_container_width=True)

                if submit_button:
                    if username and password:
                        # 使用auth_manager.login()方法來確保前端緩存被正確保存
                        if auth_manager.login(username, password):
                            st.success("登錄成功！正在為您跳轉...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("用戶名或密碼錯誤，請重試")
                    else:
                        st.warning("請輸入完整的登錄信息")

        st.markdown('</div>', unsafe_allow_html=True)
    
    # 功能特色展示
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon"></div>
            <div class="feature-title">智能分析</div>
            <div class="feature-desc">AI驅動的股票分析</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon"></div>
            <div class="feature-title">深度研究</div>
            <div class="feature-desc">全方位市場洞察</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon"></div>
            <div class="feature-title">實時數據</div>
            <div class="feature-desc">最新市場信息</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon"></div>
            <div class="feature-title">風險控制</div>
            <div class="feature-desc">智能風險評估</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_user_info():
    """在側邊欄渲染用戶信息"""
    
    if not auth_manager.is_authenticated():
        return
    
    user_info = auth_manager.get_current_user()
    if not user_info:
        return
    
    # 側邊欄用戶信息樣式
    st.sidebar.markdown("""
    <style>
    .sidebar-user-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .sidebar-user-name {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        text-align: center;
    }
    
    .sidebar-user-role {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 0.5rem;
        backdrop-filter: blur(10px);
    }
    
    .sidebar-user-status {
        font-size: 0.8rem;
        opacity: 0.9;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    
    .sidebar-logout-btn {
        width: 100% !important;
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .sidebar-logout-btn:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 獲取用戶角色的中文顯示
    role_display = {
        'admin': '管理員',
        'user': '普通用戶'
    }.get(user_info.get('role', 'user'), '用戶')
    
    # 獲取登錄時間
    login_time = st.session_state.get('login_time')
    login_time_str = ""
    if login_time:
        import datetime
        login_dt = datetime.datetime.fromtimestamp(login_time)
        login_time_str = login_dt.strftime("%H:%M")
    
    # 渲染用戶信息
    st.sidebar.markdown(f"""
    <div class="sidebar-user-info">
        <div class="sidebar-user-name"> {user_info['username']}</div>
        <div class="sidebar-user-role">{role_display}</div>
        <div class="sidebar-user-status">
             在線中 {f'· {login_time_str}登錄' if login_time_str else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_logout():
    """在側邊欄底部渲染退出按鈕"""
    
    if not auth_manager.is_authenticated():
        return
    
    # 退出按鈕樣式
    st.sidebar.markdown("""
    <style>
    .sidebar-logout-container {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-logout-btn {
        width: 100% !important;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 10px rgba(255, 107, 107, 0.3) !important;
    }
    
    .sidebar-logout-btn:hover {
        background: linear-gradient(135deg, #ff5252 0%, #d32f2f 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 添加分隔線和退出按鈕
    st.sidebar.markdown('<div class="sidebar-logout-container">', unsafe_allow_html=True)
    if st.sidebar.button("安全退出", use_container_width=True, key="sidebar_logout_btn"):
        auth_manager.logout()
        st.sidebar.success("已安全退出，感謝使用！")
        time.sleep(1)
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def render_user_info():
    """渲染用戶信息欄"""
    
    if not auth_manager.is_authenticated():
        return
    
    user_info = auth_manager.get_current_user()
    if not user_info:
        return
    
    # 現代化用戶信息欄樣式
    st.markdown("""
    <style>
    .user-info-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .user-welcome {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .user-name {
        font-size: 1.4rem;
        font-weight: 600;
        margin: 0;
    }
    
    .user-role {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }
    
    .user-details {
        display: flex;
        align-items: center;
        gap: 1rem;
        opacity: 0.9;
        font-size: 0.95rem;
    }
    
    .logout-btn {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .logout-btn:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 獲取用戶角色的中文顯示
    role_display = {
        'admin': '管理員',
        'user': '普通用戶'
    }.get(user_info.get('role', 'user'), '用戶')
    
    # 獲取登錄時間
    login_time = st.session_state.get('login_time')
    login_time_str = ""
    if login_time:
        import datetime
        login_dt = datetime.datetime.fromtimestamp(login_time)
        login_time_str = login_dt.strftime("%H:%M")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
        <div class="user-info-container">
            <div class="user-welcome">
                <div>
                    <h3 class="user-name"> 歡迎回來，{user_info['username']}</h3>
                    <div class="user-details">
                        <span> {role_display}</span>
                        {f'<span> {login_time_str} 登錄</span>' if login_time_str else ''}
                        <span> 在線中</span>
                    </div>
                </div>
                <div class="user-role">{role_display}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("安全退出", use_container_width=True, type="secondary", key="logout_btn"):
            auth_manager.logout()
            st.success("已安全退出，感謝使用！")
            time.sleep(1)
            st.rerun()

def check_authentication():
    """檢查用戶認證狀態"""
    global auth_manager
    if auth_manager is None:
        return False
    return auth_manager.is_authenticated()

def require_permission(permission: str):
    """要求特定權限"""
    global auth_manager
    if auth_manager is None:
        return False
    return auth_manager.require_permission(permission)