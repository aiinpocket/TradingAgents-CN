#!/usr/bin/env python3
"""
TradingAgents-CN Streamlit Web界面
基於Streamlit的股票分析Web應用程序
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
import datetime
import time
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 導入日誌模組
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger('web')
except ImportError:
    # 如果無法導入，使用標準logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('web')

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

# 導入國際化模組
from tradingagents.i18n import t, set_language, get_current_language

# 初始化語言設定（從 session_state 讀取使用者偏好）
if 'language' not in st.session_state:
    st.session_state.language = 'zh_TW'
set_language(st.session_state.language)

# 導入自定義組件
from components.sidebar import render_sidebar
from components.header import render_header
from components.analysis_form import render_analysis_form
from components.results_display import render_results
from components.login import render_login_form, check_authentication, render_user_info, render_sidebar_user_info, render_sidebar_logout, require_permission
from components.user_activity_dashboard import render_user_activity_dashboard, render_activity_summary_widget
from utils.api_checker import check_api_keys
from utils.analysis_runner import run_stock_analysis, validate_analysis_params, format_analysis_results
from utils.progress_tracker import SmartStreamlitProgressDisplay, create_smart_progress_callback
from utils.async_progress_tracker import AsyncProgressTracker
from components.async_progress_display import display_unified_progress
from utils.smart_session_manager import get_persistent_analysis_id, set_persistent_analysis_id
from utils.auth_manager import auth_manager
from utils.user_activity_logger import user_activity_logger

# 設置頁面配置
st.set_page_config(
    page_title="TradingAgents-CN 股票分析平台",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# 自定義CSS樣式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 隱藏Streamlit頂部工具列和Deploy按鈕 - 多種選擇器確保兼容性 */
    .stAppToolbar {
        display: none !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .stDeployButton {
        display: none !important;
    }
    
    /* 新版本Streamlit的Deploy按鈕選擇器 */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* 隱藏整個頂部區域 */
    .stApp > header {
        display: none !important;
    }
    
    .stApp > div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 隱藏主菜單按鈕 */
    #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 隱藏頁腳 */
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 隱藏"Made with Streamlit"標識 */
    .viewerBadge_container__1QSob {
        display: none !important;
    }
    
    /* 隱藏所有可能的工具列元素 */
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 隱藏右上角的所有按鈕 */
    .stApp > div > div > div > div > section > div {
        padding-top: 0 !important;
    }
    
    /* 全局樣式 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 主容器樣式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 主標題樣式 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* 卡片樣式 */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .metric-card h4 {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .metric-card p {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin: 0;
        font-size: 0.9rem;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .analysis-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(20px);
    }
    
    /* 按鈕樣式 */
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
    
    /* 輸入框樣式 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    /* 側邊欄樣式 */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
    }
    
    /* 狀態框樣式 */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #9ae6b4;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(154, 230, 180, 0.3);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #f6d55c;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 234, 167, 0.3);
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f1556c;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(245, 198, 203, 0.3);
    }
    
    /* 進度條樣式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* 標籤頁樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 0.5rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 數據框樣式 */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* 圖表容器樣式 */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """初始化會話狀態"""
    # 初始化認證相關狀態
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    
    # 初始化分析相關狀態
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'last_analysis_time' not in st.session_state:
        st.session_state.last_analysis_time = None
    if 'current_analysis_id' not in st.session_state:
        st.session_state.current_analysis_id = None
    if 'form_config' not in st.session_state:
        st.session_state.form_config = None

    # 嘗試從最新完成的分析中恢複結果
    if not st.session_state.analysis_results:
        try:
            from utils.async_progress_tracker import get_latest_analysis_id, get_progress_by_id
            from utils.analysis_runner import format_analysis_results

            latest_id = get_latest_analysis_id()
            if latest_id:
                progress_data = get_progress_by_id(latest_id)
                if (progress_data and
                    progress_data.get('status') == 'completed' and
                    'raw_results' in progress_data):

                    # 恢複分析結果
                    raw_results = progress_data['raw_results']
                    formatted_results = format_analysis_results(raw_results)

                    if formatted_results:
                        st.session_state.analysis_results = formatted_results
                        st.session_state.current_analysis_id = latest_id
                        # 檢查分析狀態
                        analysis_status = progress_data.get('status', 'completed')
                        st.session_state.analysis_running = (analysis_status == 'running')
                        # 恢複股票信息
                        if 'stock_symbol' in raw_results:
                            st.session_state.last_stock_symbol = raw_results.get('stock_symbol', '')
                        if 'market_type' in raw_results:
                            st.session_state.last_market_type = raw_results.get('market_type', '')
                        logger.info(f"[結果恢複] 從分析 {latest_id} 恢複結果，狀態: {analysis_status}")

        except Exception as e:
            logger.warning(f"[結果恢複] 恢複失敗: {e}")

    # 使用cookie管理器恢複分析ID（優先級：session state > cookie > Redis/文件）
    try:
        persistent_analysis_id = get_persistent_analysis_id()
        if persistent_analysis_id:
            # 使用線程檢測來檢查分析狀態
            from utils.thread_tracker import check_analysis_status
            actual_status = check_analysis_status(persistent_analysis_id)

            # 只在狀態變化時記錄日誌，避免重複
            current_session_status = st.session_state.get('last_logged_status')
            if current_session_status != actual_status:
                logger.info(f"[狀態檢查] 分析 {persistent_analysis_id} 實際狀態: {actual_status}")
                st.session_state.last_logged_status = actual_status

            if actual_status == 'running':
                st.session_state.analysis_running = True
                st.session_state.current_analysis_id = persistent_analysis_id
            elif actual_status in ['completed', 'failed']:
                st.session_state.analysis_running = False
                st.session_state.current_analysis_id = persistent_analysis_id
            else:  # not_found
                logger.warning(f"[狀態檢查] 分析 {persistent_analysis_id} 未找到，清理狀態")
                st.session_state.analysis_running = False
                st.session_state.current_analysis_id = None
    except Exception as e:
        # 如果恢複失敗，保持默認值
        logger.warning(f"[狀態恢複] 恢複分析狀態失敗: {e}")
        st.session_state.analysis_running = False
        st.session_state.current_analysis_id = None

    # 恢複表單配置
    try:
        from utils.smart_session_manager import smart_session_manager
        session_data = smart_session_manager.load_analysis_state()

        if session_data and 'form_config' in session_data:
            st.session_state.form_config = session_data['form_config']
            # 只在沒有分析運行時記錄日誌，避免重複
            if not st.session_state.get('analysis_running', False):
                logger.info("[配置恢複] 表單配置已恢複")
    except Exception as e:
        logger.warning(f"[配置恢複] 表單配置恢複失敗: {e}")

def check_frontend_auth_cache():
    """檢查前端緩存並嘗試恢複登錄狀態"""
    from utils.auth_manager import auth_manager
    
    logger.info("開始檢查前端緩存恢複")
    logger.info(f"當前認證狀態: {st.session_state.get('authenticated', False)}")
    logger.info(f"URL參數: {dict(st.query_params)}")
    
    # 如果已經認證，確保狀態同步
    if st.session_state.get('authenticated', False):
        # 確保auth_manager也知道用戶已認證
        if not auth_manager.is_authenticated() and st.session_state.get('user_info'):
            logger.info("同步認證狀態到auth_manager")
            try:
                auth_manager.login_user(
                    st.session_state.user_info, 
                    st.session_state.get('login_time', time.time())
                )
                logger.info("認證狀態同步成功")
            except Exception as e:
                logger.warning(f"認證狀態同步失敗: {e}")
        else:
            logger.info("用戶已認證，跳過緩存檢查")
        return
    
    # 檢查URL參數中是否有恢複信息
    try:
        import base64
        restore_data = st.query_params.get('restore_auth')
        
        if restore_data:
            logger.info("發現URL中的恢複參數，開始恢複登錄狀態")
            # 解碼認證數據
            auth_data = json.loads(base64.b64decode(restore_data).decode())
            
            # 兼容舊格式（直接是用戶信息）和新格式（包含loginTime）
            if 'userInfo' in auth_data:
                user_info = auth_data['userInfo']
                # 使用當前時間作為新的登錄時間，避免超時問題
                # 因為前端已經驗證了lastActivity沒有超時
                login_time = time.time()
            else:
                # 舊格式兼容
                user_info = auth_data
                login_time = time.time()
                
            logger.info(f"成功解碼用戶信息: {user_info.get('username', 'Unknown')}")
            logger.info(f"使用當前時間作為登錄時間: {login_time}")
            
            # 恢複登錄狀態
            if auth_manager.restore_from_cache(user_info, login_time):
                # 清除URL參數
                del st.query_params['restore_auth']
                logger.info(f"從前端緩存成功恢複用戶 {user_info['username']} 的登錄狀態")
                logger.info("已清除URL恢複參數")
                # 立即重新運行以應用恢複的狀態
                logger.info("觸發頁面重新運行")
                st.rerun()
            else:
                logger.error("恢複登錄狀態失敗")
                # 恢複失敗，清除URL參數
                del st.query_params['restore_auth']
        else:
            # 如果沒有URL參數，註入前端檢查腳本
            logger.info("沒有URL恢複參數，註入前端檢查腳本")
            inject_frontend_cache_check()
    except Exception as e:
        logger.warning(f"處理前端緩存恢複失敗: {e}")
        # 如果恢複失敗，清除可能損壞的URL參數
        if 'restore_auth' in st.query_params:
            del st.query_params['restore_auth']

def inject_frontend_cache_check():
    """註入前端緩存檢查腳本"""
    logger.info("準備註入前端緩存檢查腳本")
    
    # 如果已經註入過，不重複註入
    if st.session_state.get('cache_script_injected', False):
        logger.info("前端腳本已註入，跳過重複註入")
        return
    
    # 標記已註入
    st.session_state.cache_script_injected = True
    logger.info("標記前端腳本已註入")
    
    cache_check_js = """
    <script>
    // 前端緩存檢查和恢複
    function checkAndRestoreAuth() {
        console.log('開始執行前端緩存檢查');
        console.log('當前URL:', window.location.href);
        
        try {
            // 檢查URL中是否已經有restore_auth參數
            const currentUrl = new URL(window.location);
            if (currentUrl.searchParams.has('restore_auth')) {
                console.log('URL中已有restore_auth參數，跳過前端檢查');
                return;
            }
            
            const authData = localStorage.getItem('tradingagents_auth');
            console.log('檢查localStorage中的認證數據:', authData ? '存在' : '不存在');
            
            if (!authData) {
                console.log('前端緩存中沒有登錄狀態');
                return;
            }
            
            const data = JSON.parse(authData);
            console.log('解析的認證數據:', data);
            
            // 驗證數據結構
            if (!data.userInfo || !data.userInfo.username) {
                console.log('認證數據結構無效，清除緩存');
                localStorage.removeItem('tradingagents_auth');
                return;
            }
            
            const now = Date.now();
            const timeout = 10 * 60 * 1000; // 10分鐘
            const timeSinceLastActivity = now - data.lastActivity;
            
            console.log('時間檢查:', {
                now: new Date(now).toLocaleString(),
                lastActivity: new Date(data.lastActivity).toLocaleString(),
                timeSinceLastActivity: Math.round(timeSinceLastActivity / 1000) + '秒',
                timeout: Math.round(timeout / 1000) + '秒'
            });
            
            // 檢查是否超時
            if (timeSinceLastActivity > timeout) {
                localStorage.removeItem('tradingagents_auth');
                console.log('登錄狀態已過期，自動清除');
                return;
            }
            
            // 更新最後活動時間
            data.lastActivity = now;
            localStorage.setItem('tradingagents_auth', JSON.stringify(data));
            console.log('更新最後活動時間');
            
            console.log('從前端緩存恢複登錄狀態:', data.userInfo.username);
            
            // 保留現有的URL參數，只添加restore_auth參數
            // 傳遞完整的認證數據，包括原始登錄時間
            const restoreData = {
                userInfo: data.userInfo,
                loginTime: data.loginTime
            };
            const restoreParam = btoa(JSON.stringify(restoreData));
            console.log('生成恢複參數:', restoreParam);
            
            // 保留所有現有參數
            const existingParams = new URLSearchParams(currentUrl.search);
            existingParams.set('restore_auth', restoreParam);
            
            // 構建新URL，保留現有參數
            const newUrl = currentUrl.origin + currentUrl.pathname + '?' + existingParams.toString();
            console.log('準備跳轉到:', newUrl);
            console.log('保留的URL參數:', Object.fromEntries(existingParams));
            
            window.location.href = newUrl;
            
        } catch (e) {
            console.error('前端緩存恢複失敗:', e);
            localStorage.removeItem('tradingagents_auth');
        }
    }
    
    // 延遲執行，確保頁面完全加載
    console.log('設置1000ms延遲執行前端緩存檢查');
    setTimeout(checkAndRestoreAuth, 1000);
    </script>
    """
    
    st.components.v1.html(cache_check_js, height=0)

def main():
    """主應用程序"""

    # 初始化會話狀態
    initialize_session_state()

    # 檢查前端緩存恢複
    check_frontend_auth_cache()

    # 檢查用戶認證狀態
    if not auth_manager.is_authenticated():
        # 最後一次嘗試從session state恢複認證狀態
        if (st.session_state.get('authenticated', False) and 
            st.session_state.get('user_info') and 
            st.session_state.get('login_time')):
            logger.info("從session state恢複認證狀態")
            try:
                auth_manager.login_user(
                    st.session_state.user_info, 
                    st.session_state.login_time
                )
                logger.info(f"成功從session state恢複用戶 {st.session_state.user_info.get('username', 'Unknown')} 的認證狀態")
            except Exception as e:
                logger.warning(f"從session state恢複認證狀態失敗: {e}")
        
        # 如果仍然未認證，顯示登錄頁面
        if not auth_manager.is_authenticated():
            render_login_form()
            return

    # 全局側邊欄CSS樣式 - 確保所有頁面一致
    st.markdown("""
    <style>
    /* 統一側邊欄寬度為320px */
    section[data-testid="stSidebar"] {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }

    /* 側邊欄內容容器 */
    section[data-testid="stSidebar"] > div {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }

    /* 主內容區域適配320px側邊欄 */
    .main .block-container {
        width: calc(100vw - 336px) !important;
        max-width: calc(100vw - 336px) !important;
    }

    /* 選擇框寬度適配320px側邊欄 */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        width: 100% !important;
        min-width: 260px !important;
        max-width: 280px !important;
    }

    /* 側邊欄標題樣式 */
    section[data-testid="stSidebar"] h1 {
        font-size: 1.2rem !important;
        line-height: 1.3 !important;
        margin-bottom: 1rem !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }

    /* 隱藏側邊欄的隱藏按鈕 - 更全面的選擇器 */
    button[kind="header"],
    button[data-testid="collapsedControl"],
    .css-1d391kg,
    .css-1rs6os,
    .css-17eq0hr,
    .css-1lcbmhc,
    .css-1y4p8pa,
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"],
    [data-testid="collapsedControl"],
    .stSidebar button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* 隱藏側邊欄頂部區域的特定按鈕（更精確的選擇器，避免影響表單按鈕） */
    section[data-testid="stSidebar"] > div:first-child > button[kind="header"],
    section[data-testid="stSidebar"] > div:first-child > div > button[kind="header"],
    section[data-testid="stSidebar"] .css-1lcbmhc > button[kind="header"],
    section[data-testid="stSidebar"] .css-1y4p8pa > button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 調整側邊欄內容的padding */
    section[data-testid="stSidebar"] > div {
        padding-top: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* 調整主內容區域，設置8px邊距 - 使用更強的選擇器 */
    .main .block-container,
    section.main .block-container,
    div.main .block-container,
    .stApp .main .block-container {
        padding-left: 8px !important;
        padding-right: 8px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
        max-width: none !important;
        width: calc(100% - 16px) !important;
    }

    /* 確保內容不被捲動條遮擋 */
    .stApp > div {
        overflow-x: auto !important;
    }

    /* 調整詳細分析報告的右邊距 */
    .element-container {
        margin-right: 8px !important;
    }

    /* 優化側邊欄標題和元素間距 */
    .sidebar .sidebar-content {
        padding: 0.5rem 0.3rem !important;
    }

    /* 調整側邊欄內所有元素的間距 */
    section[data-testid="stSidebar"] .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* 調整側邊欄分隔線的間距 */
    section[data-testid="stSidebar"] hr {
        margin: 0.8rem 0 !important;
    }

    /* 簡化功能選擇區域樣式 */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* 這些樣式已在global_sidebar.css中定義 */

    /* 防止水平捲動條出現 */
    .main .block-container {
        overflow-x: visible !important;
    }

    /* 強制設置8px邊距給所有可能的容器 */
    .stApp,
    .stApp > div,
    .stApp > div > div,
    .main,
    .main > div,
    .main > div > div,
    div[data-testid="stAppViewContainer"],
    div[data-testid="stAppViewContainer"] > div,
    section[data-testid="stMain"],
    section[data-testid="stMain"] > div {
        padding-left: 8px !important;
        padding-right: 8px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
    }

    /* 特別處理列容器 */
    div[data-testid="column"],
    .css-1d391kg,
    .css-1r6slb0,
    .css-12oz5g7,
    .css-1lcbmhc {
        padding-left: 8px !important;
        padding-right: 8px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
    }

    /* 容器寬度已在global_sidebar.css中定義 */

    /* 優化使用指南區域的樣式 */
    div[data-testid="column"]:last-child {
        background-color: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin-left: 8px !important;
        border: 1px solid #e9ecef !important;
    }

    /* 使用指南內的展開器樣式 */
    div[data-testid="column"]:last-child .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 6px !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 500 !important;
    }

    /* 使用指南內的文本樣式 */
    div[data-testid="column"]:last-child .stMarkdown {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }

    /* 使用指南標題樣式 */
    div[data-testid="column"]:last-child h1 {
        font-size: 1.3rem !important;
        color: #495057 !important;
        margin-bottom: 1rem !important;
    }
    </style>

    <script>
    // JavaScript來強制隱藏側邊欄按鈕
    function hideSidebarButtons() {
        // 隱藏所有可能的側邊欄控制按鈕
        const selectors = [
            'button[kind="header"]',
            'button[data-testid="collapsedControl"]',
            'button[aria-label="Close sidebar"]',
            'button[aria-label="Open sidebar"]',
            '[data-testid="collapsedControl"]',
            '.css-1d391kg',
            '.css-1rs6os',
            '.css-17eq0hr',
            '.css-1lcbmhc button',
            '.css-1y4p8pa button'
        ];

        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.style.opacity = '0';
                el.style.pointerEvents = 'none';
            });
        });
    }

    // 頁面加載後執行
    document.addEventListener('DOMContentLoaded', hideSidebarButtons);

    // 定期檢查並隱藏按鈕（防止動態生成）
    setInterval(hideSidebarButtons, 1000);

    // 強制修改頁面邊距為8px
    function forceOptimalPadding() {
        const selectors = [
            '.main .block-container',
            '.stApp',
            '.stApp > div',
            '.main',
            '.main > div',
            'div[data-testid="stAppViewContainer"]',
            'section[data-testid="stMain"]',
            'div[data-testid="column"]'
        ];

        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                el.style.paddingLeft = '8px';
                el.style.paddingRight = '8px';
                el.style.marginLeft = '0px';
                el.style.marginRight = '0px';
            });
        });

        // 特別處理主容器寬度
        const mainContainer = document.querySelector('.main .block-container');
        if (mainContainer) {
            mainContainer.style.width = 'calc(100vw - 336px)';
            mainContainer.style.maxWidth = 'calc(100vw - 336px)';
        }
    }

    // 頁面加載後執行
    document.addEventListener('DOMContentLoaded', forceOptimalPadding);

    // 定期強制應用樣式
    setInterval(forceOptimalPadding, 500);
    </script>
    """, unsafe_allow_html=True)

    # 添加調試按鈕（僅在調試模式下顯示）
    if os.getenv('DEBUG_MODE') == 'true':
        if st.button("清除會話狀態"):
            st.session_state.clear()
            st.rerun()

    # 渲染頁面頭部
    render_header()

    # 側邊欄布局 - 標題在最頂部
    st.sidebar.title("TradingAgents-CN")
    st.sidebar.markdown("---")
    
    # 頁面導航 - 在標題下方顯示用戶信息
    render_sidebar_user_info()

    # 在用戶信息和功能導航之間添加分隔線
    st.sidebar.markdown("---")

    # 添加功能切換標題
    st.sidebar.markdown("**功能導航**")

    page = st.sidebar.selectbox(
        "切換功能模組",
        ["股票分析", "熱門特區", "配置管理", "快取管理", "Token統計", "操作日誌", "分析結果", "系統狀態"],
        label_visibility="collapsed"
    )
    
    # 記錄頁面訪問活動
    try:
        user_activity_logger.log_page_visit(
            page_name=page,
            page_params={
                "page_url": f"/app?page={page.split(' ')[1] if ' ' in page else page}",
                "page_type": "main_navigation",
                "access_method": "sidebar_selectbox"
            }
        )
    except Exception as e:
        logger.warning(f"記錄頁面訪問活動失敗: {e}")

    # 在功能選擇和AI模型配置之間添加分隔線
    st.sidebar.markdown("---")

    # 根據選擇的頁面渲染不同內容
    if page == "熱門特區":
        # 熱門特區 - 所有使用者皆可瀏覽
        try:
            from modules.hot_topics import render_hot_topics
            render_hot_topics()
        except ImportError as e:
            st.error(f"熱門特區模組載入失敗: {e}")
            st.info("請確保已安裝所有依賴套件")
        return
    elif page == "配置管理":
        # 檢查配置權限
        if not require_permission("config"):
            return
        try:
            from modules.config_management import render_config_management
            render_config_management()
        except ImportError as e:
            st.error(f"配置管理模組載入失敗: {e}")
            st.info("請確保已安裝所有依賴包")
        return
    elif page == "快取管理":
        # 檢查管理員權限
        if not require_permission("admin"):
            return
        try:
            from modules.cache_management import main as cache_main
            cache_main()
        except ImportError as e:
            st.error(f"快取管理頁面載入失敗: {e}")
        return
    elif page == "Token統計":
        # 檢查配置權限
        if not require_permission("config"):
            return
        try:
            from modules.token_statistics import render_token_statistics
            render_token_statistics()
        except ImportError as e:
            st.error(f"Token統計頁面載入失敗: {e}")
            st.info("請確保已安裝所有依賴包")
        return
    elif page == "操作日誌":
        # 檢查管理員權限
        if not require_permission("admin"):
            return
        try:
            from components.operation_logs import render_operation_logs
            render_operation_logs()
        except ImportError as e:
            st.error(f"操作日誌模組載入失敗: {e}")
            st.info("請確保已安裝所有依賴包")
        return
    elif page == "分析結果":
        # 檢查分析權限
        if not require_permission("analysis"):
            return
        try:
            from components.analysis_results import render_analysis_results
            render_analysis_results()
        except ImportError as e:
            st.error(f"分析結果模組載入失敗: {e}")
            st.info("請確保已安裝所有依賴包")
        return
    elif page == "系統狀態":
        # 檢查管理員權限
        if not require_permission("admin"):
            return
        st.header("系統狀態")
        st.info("系統狀態功能開發中...")
        return

    # 默認顯示股票分析頁面
    # 檢查分析權限
    if not require_permission("analysis"):
        return
        
    # 檢查API密鑰
    api_status = check_api_keys()
    
    if not api_status['all_configured']:
        st.error("API密鑰配置不完整，請先配置必要的API密鑰")
        
        with st.expander("API密鑰配置指南", expanded=True):
            st.markdown("""
            ### 必需的API密鑰（至少配置一個 LLM 提供商）

            1. **OpenAI API密鑰** (OPENAI_API_KEY)
               - 獲取地址: https://platform.openai.com/
               - 用途: GPT-4、GPT-3.5 等模型

            2. **Google AI API密鑰** (GOOGLE_API_KEY)
               - 獲取地址: https://ai.google.dev/
               - 用途: Gemini 模型系列

            3. **Anthropic API密鑰** (ANTHROPIC_API_KEY)
               - 獲取地址: https://console.anthropic.com/
               - 用途: Claude 模型系列

            4. **金融數據API密鑰** (FINNHUB_API_KEY，可選)
               - 獲取地址: https://finnhub.io/
               - 用途: 美股數據（若無則部分功能受限）

            ### 配置方法

            1. 複制項目根目錄的 `.env.example` 為 `.env`
            2. 編輯 `.env` 文件，填入您的真實API密鑰
            3. 重啟Web應用

            ```bash
            # .env 文件示例
            OPENAI_API_KEY=sk-your-openai-key
            GOOGLE_API_KEY=your-google-key
            FINNHUB_API_KEY=your-finnhub-key
            ```
            """)
        
        # 顯示當前API密鑰狀態
        st.subheader("當前API密鑰狀態")
        for key, status in api_status['details'].items():
            if status['configured']:
                st.success(f"{key}: {status['display']}")
            else:
                st.error(f"{key}: 未配置")
        
        return
    
    # 渲染側邊欄
    config = render_sidebar()
    
    # 添加使用指南顯示切換
    # 如果正在分析或有分析結果，默認隱藏使用指南
    default_show_guide = not (st.session_state.get('analysis_running', False) or st.session_state.get('analysis_results') is not None)
    
    # 如果用戶沒有手動設置過，使用默認值
    if 'user_set_guide_preference' not in st.session_state:
        st.session_state.user_set_guide_preference = False
        st.session_state.show_guide_preference = default_show_guide
    
    show_guide = st.sidebar.checkbox(
        "顯示使用指南",
        value=st.session_state.get('show_guide_preference', default_show_guide), 
        help="顯示/隱藏右側使用指南",
        key="guide_checkbox"
    )
    
    # 記錄用戶的選擇
    if show_guide != st.session_state.get('show_guide_preference', default_show_guide):
        st.session_state.user_set_guide_preference = True
        st.session_state.show_guide_preference = show_guide

    # 添加狀態清理按鈕
    st.sidebar.markdown("---")
    if st.sidebar.button("清理分析狀態", help="清理僵屍分析狀態，解決頁面持續刷新問題"):
        # 清理session state
        st.session_state.analysis_running = False
        st.session_state.current_analysis_id = None
        st.session_state.analysis_results = None

        # 清理所有自動刷新狀態
        keys_to_remove = []
        for key in st.session_state.keys():
            if 'auto_refresh' in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del st.session_state[key]

        # 清理死亡線程
        from utils.thread_tracker import cleanup_dead_analysis_threads
        cleanup_dead_analysis_threads()

        st.sidebar.success("分析狀態已清理")
        st.rerun()

    # 在側邊欄底部添加退出按鈕
    render_sidebar_logout()

    # 主內容區域 - 根據是否顯示指南調整布局
    if show_guide:
        col1, col2 = st.columns([2, 1])  # 2:1比例，使用指南占三分之一
    else:
        col1 = st.container()
        col2 = None
    
    with col1:
        # 1. 分析配置區域

        st.header("分析配置")

        # 渲染分析表單
        try:
            form_data = render_analysis_form()

            # 驗證表單數據格式
            if not isinstance(form_data, dict):
                st.error(f"表單數據格式異常: {type(form_data)}")
                form_data = {'submitted': False}

        except Exception as e:
            st.error(f"表單渲染失敗: {e}")
            form_data = {'submitted': False}

        # 避免顯示調試信息
        if form_data and form_data != {'submitted': False}:
            # 只在調試模式下顯示表單數據
            if os.getenv('DEBUG_MODE') == 'true':
                st.write("Debug - Form data:", form_data)

        # 添加接收日誌
        if form_data.get('submitted', False):
            logger.debug(f"[APP DEBUG] ===== 主應用接收表單數據 =====")
            logger.debug(f"[APP DEBUG] 接收到的form_data: {form_data}")
            logger.debug(f"[APP DEBUG] 股票代碼: '{form_data['stock_symbol']}'")
            logger.debug(f"[APP DEBUG] 市場類型: '{form_data['market_type']}'")

        # 檢查是否提交了表單
        if form_data.get('submitted', False) and not st.session_state.get('analysis_running', False):
            # 只有在沒有分析運行時才處理新的提交
            # 驗證分析參數
            is_valid, validation_errors = validate_analysis_params(
                stock_symbol=form_data['stock_symbol'],
                analysis_date=form_data['analysis_date'],
                analysts=form_data['analysts'],
                research_depth=form_data['research_depth']
            )

            if not is_valid:
                # 顯示驗證錯誤
                for error in validation_errors:
                    st.error(error)
            else:
                # 執行分析
                st.session_state.analysis_running = True

                # 清空舊的分析結果
                st.session_state.analysis_results = None
                logger.info("[新分析] 清空舊的分析結果")
                
                # 自動隱藏使用指南（除非用戶明確設置要顯示）
                if not st.session_state.get('user_set_guide_preference', False):
                    st.session_state.show_guide_preference = False
                    logger.info("[界面] 開始分析，自動隱藏使用指南")

                # 生成分析ID
                import uuid
                analysis_id = f"analysis_{uuid.uuid4().hex[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # 保存分析ID和表單配置到session state和cookie
                form_config = st.session_state.get('form_config', {})
                set_persistent_analysis_id(
                    analysis_id=analysis_id,
                    status="running",
                    stock_symbol=form_data['stock_symbol'],
                    market_type=form_data.get('market_type', '美股'),
                    form_config=form_config
                )

                # 創建異步進度跟蹤器
                async_tracker = AsyncProgressTracker(
                    analysis_id=analysis_id,
                    analysts=form_data['analysts'],
                    research_depth=form_data['research_depth'],
                    llm_provider=config['llm_provider']
                )

                # 創建進度回調函數
                def progress_callback(message: str, step: int = None, total_steps: int = None):
                    async_tracker.update_progress(message, step)

                # 顯示啟動成功訊息和加載動效
                st.success(f"分析已啟動！分析ID: {analysis_id}")

                # 添加加載動效
                with st.spinner("正在初始化分析..."):
                    time.sleep(1.5)  # 讓用戶看到反饋

                st.info(f"正在分析: {form_data.get('market_type', '美股')} {form_data['stock_symbol']}")
                st.info("""
                頁面將在6秒後自動刷新...

                **查看分析進度：**
                刷新後請向下捲動到 "股票分析" 部分查看實時進度
                """)

                # 確保AsyncProgressTracker已經保存初始狀態
                time.sleep(0.1)  # 等待100毫秒確保數據已寫入

                # 設置分析狀態
                st.session_state.analysis_running = True
                st.session_state.current_analysis_id = analysis_id
                st.session_state.last_stock_symbol = form_data['stock_symbol']
                st.session_state.last_market_type = form_data.get('market_type', '美股')

                # 自動啟用自動刷新選項（設置所有可能的key）
                auto_refresh_keys = [
                    f"auto_refresh_unified_{analysis_id}",
                    f"auto_refresh_unified_default_{analysis_id}",
                    f"auto_refresh_static_{analysis_id}",
                    f"auto_refresh_streamlit_{analysis_id}"
                ]
                for key in auto_refresh_keys:
                    st.session_state[key] = True

                # 在背景執行緒中運行分析（立即啟動，不等待倒計時）
                import threading

                def run_analysis_in_background():
                    try:
                        results = run_stock_analysis(
                            stock_symbol=form_data['stock_symbol'],
                            analysis_date=form_data['analysis_date'],
                            analysts=form_data['analysts'],
                            research_depth=form_data['research_depth'],
                            llm_provider=config['llm_provider'],
                            market_type=form_data.get('market_type', '美股'),
                            llm_model=config['llm_model'],
                            progress_callback=progress_callback
                        )

                        # 標記分析完成並保存結果（不訪問session state）
                        async_tracker.mark_completed("分析成功完成！", results=results)

                        # 自動保存分析結果到歷史記錄
                        try:
                            from components.analysis_results import save_analysis_result
                            
                            save_success = save_analysis_result(
                                analysis_id=analysis_id,
                                stock_symbol=form_data['stock_symbol'],
                                analysts=form_data['analysts'],
                                research_depth=form_data['research_depth'],
                                result_data=results,
                                status="completed"
                            )
                            
                            if save_success:
                                logger.info(f"[後台保存] 分析結果已保存到歷史記錄: {analysis_id}")
                            else:
                                logger.warning(f"[後台保存] 保存失敗: {analysis_id}")
                                
                        except Exception as save_error:
                            logger.error(f"[後台保存] 保存異常: {save_error}")

                        logger.info(f"[分析完成] 股票分析成功完成: {analysis_id}")

                    except Exception as e:
                        # 標記分析失敗（不訪問session state）
                        async_tracker.mark_failed(str(e))
                        
                        # 保存失敗的分析記錄
                        try:
                            from components.analysis_results import save_analysis_result
                            
                            save_analysis_result(
                                analysis_id=analysis_id,
                                stock_symbol=form_data['stock_symbol'],
                                analysts=form_data['analysts'],
                                research_depth=form_data['research_depth'],
                                result_data={"error": str(e)},
                                status="failed"
                            )
                            logger.info(f"[失敗記錄] 分析失敗記錄已保存: {analysis_id}")
                            
                        except Exception as save_error:
                            logger.error(f"[失敗記錄] 保存異常: {save_error}")
                        
                        logger.error(f"[分析失敗] {analysis_id}: {e}")

                    finally:
                        # 分析結束後註銷線程
                        from utils.thread_tracker import unregister_analysis_thread
                        unregister_analysis_thread(analysis_id)
                        logger.info(f"[線程清理] 分析線程已註銷: {analysis_id}")

                # 啟動後台分析線程
                analysis_thread = threading.Thread(target=run_analysis_in_background)
                analysis_thread.daemon = True  # 設置為守護線程，這樣主程序退出時線程也會退出
                analysis_thread.start()

                # 註冊線程到跟蹤器
                from utils.thread_tracker import register_analysis_thread
                register_analysis_thread(analysis_id, analysis_thread)

                logger.info(f"[後台分析] 分析線程已啟動: {analysis_id}")

                # 分析已在背景執行緒中啟動，顯示啟動信息並刷新頁面
                st.success("分析已啟動！正在後台運行...")

                # 顯示啟動信息
                st.info("頁面將自動刷新顯示分析進度...")

                # 等待2秒讓用戶看到啟動信息，然後刷新頁面
                time.sleep(2)
                st.rerun()

        # 2. 股票分析區域（只有在有分析ID時才顯示）
        current_analysis_id = st.session_state.get('current_analysis_id')
        if current_analysis_id:
            st.markdown("---")

            st.header("股票分析")

            # 使用線程檢測來獲取真實狀態
            from utils.thread_tracker import check_analysis_status
            actual_status = check_analysis_status(current_analysis_id)
            is_running = (actual_status == 'running')

            # 同步session state狀態
            if st.session_state.get('analysis_running', False) != is_running:
                st.session_state.analysis_running = is_running
                logger.info(f"[狀態同步] 更新分析狀態: {is_running} (基於線程檢測: {actual_status})")

            # 獲取進度數據用於顯示
            from utils.async_progress_tracker import get_progress_by_id
            progress_data = get_progress_by_id(current_analysis_id)

            # 顯示分析信息
            if is_running:
                st.info(f"正在分析: {current_analysis_id}")
            else:
                if actual_status == 'completed':
                    st.success(f"分析完成: {current_analysis_id}")

                elif actual_status == 'failed':
                    st.error(f"分析失敗: {current_analysis_id}")
                else:
                    st.warning(f"分析狀態未知: {current_analysis_id}")

            # 顯示進度（根據狀態決定是否顯示刷新控件）
            progress_col1, progress_col2 = st.columns([4, 1])
            with progress_col1:
                st.markdown("### 分析進度")

            is_completed = display_unified_progress(current_analysis_id, show_refresh_controls=is_running)

            # 如果分析正在進行，顯示提示信息（不添加額外的自動刷新）
            if is_running:
                st.info("分析正在進行中，可以使用下方的自動刷新功能查看進度更新...")

            # 如果分析剛完成，嘗試恢複結果
            if is_completed and not st.session_state.get('analysis_results') and progress_data:
                if 'raw_results' in progress_data:
                    try:
                        from utils.analysis_runner import format_analysis_results
                        raw_results = progress_data['raw_results']
                        formatted_results = format_analysis_results(raw_results)
                        if formatted_results:
                            st.session_state.analysis_results = formatted_results
                            st.session_state.analysis_running = False
                            logger.info(f"[結果同步] 恢複分析結果: {current_analysis_id}")

                            # 自動保存分析結果到歷史記錄
                            try:
                                from components.analysis_results import save_analysis_result
                                
                                # 從進度數據中獲取分析參數
                                stock_symbol = progress_data.get('stock_symbol', st.session_state.get('last_stock_symbol', 'unknown'))
                                analysts = progress_data.get('analysts', [])
                                research_depth = progress_data.get('research_depth', 3)
                                
                                # 保存分析結果
                                save_success = save_analysis_result(
                                    analysis_id=current_analysis_id,
                                    stock_symbol=stock_symbol,
                                    analysts=analysts,
                                    research_depth=research_depth,
                                    result_data=raw_results,
                                    status="completed"
                                )
                                
                                if save_success:
                                    logger.info(f"[結果保存] 分析結果已保存到歷史記錄: {current_analysis_id}")
                                else:
                                    logger.warning(f"[結果保存] 保存失敗: {current_analysis_id}")
                                    
                            except Exception as save_error:
                                logger.error(f"[結果保存] 保存異常: {save_error}")

                            # 檢查是否已經刷新過，避免重複刷新
                            refresh_key = f"results_refreshed_{current_analysis_id}"
                            if not st.session_state.get(refresh_key, False):
                                st.session_state[refresh_key] = True
                                st.success("分析結果已恢複並保存，正在刷新頁面...")
                                # 使用st.rerun()代替meta refresh，保持側邊欄狀態
                                time.sleep(1)
                                st.rerun()
                            else:
                                # 已經刷新過，不再刷新
                                st.success("分析結果已恢複並保存！")
                    except Exception as e:
                        logger.warning(f"[結果同步] 恢複失敗: {e}")

            if is_completed and st.session_state.get('analysis_running', False):
                # 分析剛完成，更新狀態
                st.session_state.analysis_running = False
                st.success("分析完成！正在刷新頁面顯示報告...")

                # 使用st.rerun()代替meta refresh，保持側邊欄狀態
                time.sleep(1)
                st.rerun()



        # 3. 分析報告區域（只有在有結果且分析完成時才顯示）

        current_analysis_id = st.session_state.get('current_analysis_id')
        analysis_results = st.session_state.get('analysis_results')
        analysis_running = st.session_state.get('analysis_running', False)

        # 檢查是否應該顯示分析報告
        # 1. 有分析結果且不在運行中
        # 2. 或者用戶點擊了"查看報告"按鈕
        show_results_button_clicked = st.session_state.get('show_analysis_results', False)

        should_show_results = (
            (analysis_results and not analysis_running and current_analysis_id) or
            (show_results_button_clicked and analysis_results)
        )

        # 調試日誌
        logger.info(f"[布局調試] 分析報告顯示檢查:")
        logger.info(f"  - analysis_results存在: {bool(analysis_results)}")
        logger.info(f"  - analysis_running: {analysis_running}")
        logger.info(f"  - current_analysis_id: {current_analysis_id}")
        logger.info(f"  - show_results_button_clicked: {show_results_button_clicked}")
        logger.info(f"  - should_show_results: {should_show_results}")

        if should_show_results:
            st.markdown("---")
            st.header("分析報告")
            render_results(analysis_results)
            logger.info(f"[布局] 分析報告已顯示")

            # 清除查看報告按鈕狀態，避免重複觸發
            if show_results_button_clicked:
                st.session_state.show_analysis_results = False
    
    # 只有在顯示指南時才渲染右側內容
    if show_guide and col2 is not None:
        with col2:
            st.markdown("### 使用指南")
        
            # 快速開始指南
            with st.expander("快速開始", expanded=True):
                st.markdown("""
                ### 操作步驟

                1. **輸入股票代碼**
                   - 美股示例: `AAPL` (蘋果), `TSLA` (特斯拉), `MSFT` (微軟)

                   **重要提示**: 輸入股票代碼後，請按 **回車鍵** 確認輸入！

                2. **選擇分析日期**
                   - 默認為今天
                   - 可選擇歷史日期進行回測分析

                3. **選擇分析師團隊**
                   - 至少選擇一個分析師
                   - 建議選擇多個分析師獲得全面分析

                4. **設置研究深度**
                   - 1-2級: 快速概覽
                   - 3級: 標準分析 (推薦)
                   - 4-5級: 深度研究

                5. **點擊開始分析**
                   - 等待AI分析完成
                   - 查看詳細分析報告

                ### 使用技巧

                - **美股默認**: 系統默認分析美股，無需特殊設置
                - **實時數據**: 獲取最新的市場數據和新聞
                - **多維分析**: 結合技術面、基本面、情緒面分析
                """)

            # 分析師說明
            with st.expander("分析師團隊說明"):
                st.markdown("""
                ### 專業分析師團隊

                - **市場分析師**:
                  - 技術指標分析 (K線、均線、MACD等)
                  - 價格趨勢預測
                  - 支撐阻力位分析

                - **社交媒體分析師**:
                  - 投資者情緒監測
                  - 社交媒體熱度分析
                  - 市場情緒指標

                - **新聞分析師**:
                  - 重大新聞事件影響
                  - 政策解讀分析
                  - 行業動態跟蹤

                - **基本面分析師**:
                  - 財務報表分析
                  - 估值模型計算
                  - 行業對比分析
                  - 盈利能力評估

                **建議**: 選擇多個分析師可獲得更全面的投資建議
                """)

            # 模型選擇說明
            with st.expander("AI模型說明"):
                st.markdown("""
                ### AI 模型選擇指南

                **OpenAI 系列**:
                - `gpt-4o-mini`: 快速響應，適合日常分析，成本較低
                - `gpt-4o`: 平衡性能，推薦日常使用
                - `o1-mini` / `o1`: 深度推理，適合複雜分析

                **Google Gemini 系列**:
                - `gemini-2.0-flash`: 快速響應，適合即時查詢
                - `gemini-2.5-pro`: 強大的分析與推理能力

                **Anthropic Claude 系列**:
                - `claude-haiku-4-5`: 快速且經濟
                - `claude-sonnet-4-6`: 平衡性能與成本

                請在側邊欄的配置中選擇適合的模型提供商和模型名稱。
                """)

            # 常見問題
            with st.expander("常見問題"):
                st.markdown("""
                ### 常見問題解答

                **Q: 為什麼輸入股票代碼沒有反應？**
                A: 請確保輸入代碼後按 **回車鍵** 確認，這是Streamlit的默認行為。

                **Q: 美股代碼格式是什麼？**
                A: 美股使用字母代碼，如 `AAPL`、`TSLA`、`MSFT` 等。

                **Q: 分析需要多長時間？**
                A: 根據研究深度和模型選擇，通常需要30秒到2分鐘不等。

                **Q: 歷史數據可以追溯多久？**
                A: 通常可以獲取近5年的歷史數據進行分析。
                """)

            # 風險提示
            st.warning("""
            **投資風險提示**

            - 本系統提供的分析結果僅供參考，不構成投資建議
            - 投資有風險，入市需謹慎，請理性投資
            - 請結合多方信息和專業建議進行投資決策
            - 重大投資決策建議咨詢專業的投資顧問
            - AI分析存在局限性，市場變化難以完全預測
            """)
        
        # 顯示系統狀態
        if st.session_state.last_analysis_time:
            st.info(f"上次分析時間: {st.session_state.last_analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
