#!/usr/bin/env python3
"""
TradingAgents Web 介面
基於 Streamlit 的股票分析應用程式
"""

import streamlit as st
import os
import sys
from pathlib import Path
import datetime
import time
from dotenv import load_dotenv

# 專案根目錄
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 日誌模組
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger('web')
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('web')

# 載入環境變數
load_dotenv(project_root / ".env", override=True)

# 自訂元件
from components.sidebar import render_sidebar
from components.header import render_header
from components.analysis_form import render_analysis_form
from components.results_display import render_results
from utils.api_checker import check_api_keys
from utils.analysis_runner import run_stock_analysis, validate_analysis_params, format_analysis_results
from utils.async_progress_tracker import AsyncProgressTracker
from components.async_progress_display import display_unified_progress
from utils.smart_session_manager import get_persistent_analysis_id, set_persistent_analysis_id

# 頁面設定
st.set_page_config(
    page_title="TradingAgents",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# 全域樣式 - 專業金融介面
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* 隱藏 Streamlit 預設元素 */
    .stAppToolbar,
    header[data-testid="stHeader"],
    .stDeployButton,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    .stApp > header,
    #MainMenu,
    footer,
    .viewerBadge_container__1QSob {
        display: none !important;
    }

    /* 全域字型與背景 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #F9FAFB;
        color: #1F2937;
    }

    /* 主容器 */
    .main .block-container {
        padding: 1.5rem 2rem;
        max-width: 1200px;
    }

    /* 按鈕 - 沉穩的深色調 */
    .stButton > button {
        background-color: #1E293B;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.25rem;
        font-size: 0.875rem;
        font-weight: 500;
        transition: background-color 0.15s ease;
    }

    .stButton > button:hover {
        background-color: #334155;
    }

    /* Primary 按鈕保持強調色 */
    .stButton > button[kind="primary"] {
        background-color: #0F766E;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #115E59;
    }

    /* 輸入框 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #6B7280;
        box-shadow: 0 0 0 2px rgba(107, 114, 128, 0.1);
    }

    /* 進度條 - 深青綠色 */
    .stProgress > div > div > div > div {
        background-color: #0F766E;
        border-radius: 4px;
    }

    /* 標籤頁 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #E5E7EB;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        border-bottom: 2px solid transparent;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        color: #6B7280;
    }

    .stTabs [aria-selected="true"] {
        border-bottom-color: #1E293B;
        color: #111827;
        font-weight: 500;
    }

    /* 側邊欄 */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    /* 展開器 */
    .streamlit-expanderHeader {
        font-size: 0.875rem;
        font-weight: 500;
    }

    /* 數據框 */
    .dataframe {
        border-radius: 6px;
        border: 1px solid #E5E7EB;
    }

    /* 圖表 */
    .js-plotly-plot {
        border-radius: 6px;
    }

    /* Metric 數值 - 更專業的顯示 */
    [data-testid="stMetricValue"] {
        font-weight: 600;
        color: #111827;
    }

    /* 隱藏側邊欄收合按鈕 */
    button[kind="header"],
    button[data-testid="collapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """初始化會話狀態"""
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



def main():
    """主應用程序"""

    # 初始化會話狀態
    initialize_session_state()

    # 除錯模式清除按鈕
    if os.getenv('DEBUG_MODE') == 'true':
        if st.button("清除會話狀態"):
            st.session_state.clear()
            st.rerun()

    # 渲染頁面頭部
    render_header()

    # 側邊欄標題和導航
    st.sidebar.markdown("**TradingAgents**")
    st.sidebar.markdown("---")

    page = st.sidebar.selectbox(
        "功能",
        ["股票分析", "分析結果", "配置管理", "快取管理", "Token統計"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")

    # 頁面路由 - 非分析頁面直接渲染後返回
    if page == "配置管理":
        try:
            from modules.config_management import render_config_management
            render_config_management()
        except ImportError as e:
            st.error(f"配置管理模組載入失敗: {e}")
        return
    elif page == "快取管理":
        try:
            from modules.cache_management import main as cache_main
            cache_main()
        except ImportError as e:
            st.error(f"快取管理頁面載入失敗: {e}")
        return
    elif page == "Token統計":
        try:
            from modules.token_statistics import render_token_statistics
            render_token_statistics()
        except ImportError as e:
            st.error(f"Token 統計頁面載入失敗: {e}")
        return
    elif page == "分析結果":
        try:
            from components.analysis_results import render_analysis_results
            render_analysis_results()
        except ImportError as e:
            st.error(f"分析結果模組載入失敗: {e}")
        return

    # 以下為「股票分析」頁面
    # 檢查 API 密鑰
    api_status = check_api_keys()

    if not api_status['all_configured']:
        st.warning("API 密鑰未配置")
        st.markdown(
            "請在專案根目錄的 `.env` 檔案中配置至少一個提供商的密鑰，然後重啟應用。\n\n"
            "- **OpenAI**: `OPENAI_API_KEY` ([取得](https://platform.openai.com/))\n"
            "- **Anthropic**: `ANTHROPIC_API_KEY` ([取得](https://console.anthropic.com/))\n"
            "- **FinnHub**: `FINNHUB_API_KEY` 可選 ([取得](https://finnhub.io/))"
        )
        return

    # 渲染側邊欄模型配置
    config = render_sidebar()

    # 狀態清理按鈕
    if st.sidebar.button("清理分析狀態", help="清理僵屍分析狀態"):
        st.session_state.analysis_running = False
        st.session_state.current_analysis_id = None
        st.session_state.analysis_results = None
        keys_to_remove = [k for k in st.session_state.keys() if 'auto_refresh' in k]
        for key in keys_to_remove:
            del st.session_state[key]
        from utils.thread_tracker import cleanup_dead_analysis_threads
        cleanup_dead_analysis_threads()
        st.sidebar.success("已清理")
        st.rerun()

    # -- 股票分析主頁面 --

    # 分析配置
    st.markdown("#### 分析配置")

    try:
        form_data = render_analysis_form()
        if not isinstance(form_data, dict):
            form_data = {'submitted': False}
    except Exception as e:
        st.error(f"表單渲染失敗: {e}")
        form_data = {'submitted': False}

    # 處理表單提交
    if form_data.get('submitted', False) and not st.session_state.get('analysis_running', False):
        is_valid, validation_errors = validate_analysis_params(
            stock_symbol=form_data['stock_symbol'],
            analysis_date=form_data['analysis_date'],
            analysts=form_data['analysts'],
            research_depth=form_data['research_depth']
        )

        if not is_valid:
            for error in validation_errors:
                st.error(error)
        else:
            st.session_state.analysis_running = True
            st.session_state.analysis_results = None

            import uuid
            analysis_id = f"analysis_{uuid.uuid4().hex[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            form_config = st.session_state.get('form_config', {})
            set_persistent_analysis_id(
                analysis_id=analysis_id,
                status="running",
                stock_symbol=form_data['stock_symbol'],
                market_type=form_data.get('market_type', '美股'),
                form_config=form_config
            )

            async_tracker = AsyncProgressTracker(
                analysis_id=analysis_id,
                analysts=form_data['analysts'],
                research_depth=form_data['research_depth'],
                llm_provider=config['llm_provider']
            )

            def progress_callback(message: str, step: int = None, total_steps: int = None):
                async_tracker.update_progress(message, step)

            st.info(f"正在分析 {form_data['stock_symbol']}...")

            st.session_state.current_analysis_id = analysis_id
            st.session_state.last_stock_symbol = form_data['stock_symbol']
            st.session_state.last_market_type = form_data.get('market_type', '美股')

            auto_refresh_keys = [
                f"auto_refresh_unified_{analysis_id}",
                f"auto_refresh_unified_default_{analysis_id}",
                f"auto_refresh_static_{analysis_id}",
                f"auto_refresh_streamlit_{analysis_id}"
            ]
            for key in auto_refresh_keys:
                st.session_state[key] = True

            import threading

            def run_analysis_in_background():
                """背景執行緒執行分析"""
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
                    async_tracker.mark_completed("分析成功完成", results=results)

                    try:
                        from components.analysis_results import save_analysis_result
                        save_analysis_result(
                            analysis_id=analysis_id,
                            stock_symbol=form_data['stock_symbol'],
                            analysts=form_data['analysts'],
                            research_depth=form_data['research_depth'],
                            result_data=results,
                            status="completed"
                        )
                    except Exception as save_error:
                        logger.error(f"保存分析結果異常: {save_error}")

                    logger.info(f"分析完成: {analysis_id}")

                except Exception as e:
                    async_tracker.mark_failed(str(e))
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
                    except Exception as save_error:
                        logger.error(f"保存失敗記錄異常: {save_error}")
                    logger.error(f"分析失敗 {analysis_id}: {e}")

                finally:
                    from utils.thread_tracker import unregister_analysis_thread
                    unregister_analysis_thread(analysis_id)

            analysis_thread = threading.Thread(target=run_analysis_in_background)
            analysis_thread.daemon = True
            analysis_thread.start()

            from utils.thread_tracker import register_analysis_thread
            register_analysis_thread(analysis_id, analysis_thread)

            logger.info(f"分析執行緒已啟動: {analysis_id}")

            time.sleep(2)
            st.rerun()

    # 分析進度顯示
    current_analysis_id = st.session_state.get('current_analysis_id')
    if current_analysis_id:
        st.markdown("---")

        from utils.thread_tracker import check_analysis_status
        actual_status = check_analysis_status(current_analysis_id)
        is_running = (actual_status == 'running')

        if st.session_state.get('analysis_running', False) != is_running:
            st.session_state.analysis_running = is_running

        from utils.async_progress_tracker import get_progress_by_id
        progress_data = get_progress_by_id(current_analysis_id)

        if is_running:
            st.info(f"分析進行中: {current_analysis_id}")
        elif actual_status == 'completed':
            st.success(f"分析完成: {current_analysis_id}")
        elif actual_status == 'failed':
            st.error(f"分析失敗: {current_analysis_id}")

        is_completed = display_unified_progress(current_analysis_id, show_refresh_controls=is_running)

        if is_running:
            st.caption("分析進行中，可使用自動重新整理查看進度...")

        # 分析完成後恢復結果
        if is_completed and not st.session_state.get('analysis_results') and progress_data:
            if 'raw_results' in progress_data:
                try:
                    raw_results = progress_data['raw_results']
                    formatted_results = format_analysis_results(raw_results)
                    if formatted_results:
                        st.session_state.analysis_results = formatted_results
                        st.session_state.analysis_running = False

                        try:
                            from components.analysis_results import save_analysis_result
                            stock_symbol = progress_data.get('stock_symbol', st.session_state.get('last_stock_symbol', 'unknown'))
                            save_analysis_result(
                                analysis_id=current_analysis_id,
                                stock_symbol=stock_symbol,
                                analysts=progress_data.get('analysts', []),
                                research_depth=progress_data.get('research_depth', 3),
                                result_data=raw_results,
                                status="completed"
                            )
                        except Exception as save_error:
                            logger.error(f"保存結果異常: {save_error}")

                        refresh_key = f"results_refreshed_{current_analysis_id}"
                        if not st.session_state.get(refresh_key, False):
                            st.session_state[refresh_key] = True
                            time.sleep(1)
                            st.rerun()
                except Exception as e:
                    logger.warning(f"恢復結果失敗: {e}")

        if is_completed and st.session_state.get('analysis_running', False):
            st.session_state.analysis_running = False
            time.sleep(1)
            st.rerun()

    # 分析報告
    analysis_results = st.session_state.get('analysis_results')
    analysis_running = st.session_state.get('analysis_running', False)
    show_results_button_clicked = st.session_state.get('show_analysis_results', False)

    should_show_results = (
        (analysis_results and not analysis_running and current_analysis_id) or
        (show_results_button_clicked and analysis_results)
    )

    if should_show_results:
        st.markdown("---")
        st.markdown("#### 分析報告")
        render_results(analysis_results)

        if show_results_button_clicked:
            st.session_state.show_analysis_results = False

    # 風險提示
    st.caption("分析結果僅供研究參考，不構成投資建議。")


if __name__ == "__main__":
    main()
