#!/usr/bin/env python3
"""
TradingAgents Web 介面
基於 Streamlit 的股票分析應用程式
"""

import streamlit as st
import os
import sys
import uuid
import threading
from pathlib import Path
import datetime
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
from components.analysis_results import save_analysis_result
from components.async_progress_display import display_unified_progress
from utils.api_checker import check_api_keys
from utils.analysis_runner import run_stock_analysis, validate_analysis_params, format_analysis_results
from utils.async_progress_tracker import AsyncProgressTracker, get_latest_analysis_id, get_progress_by_id
from utils.smart_session_manager import get_persistent_analysis_id, set_persistent_analysis_id
from utils.thread_tracker import (
    check_analysis_status, register_analysis_thread,
    unregister_analysis_thread, cleanup_dead_analysis_threads
)

# 頁面設定
st.set_page_config(
    page_title="TradingAgents",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# 載入外部 CSS 樣式
_css_path = Path(__file__).parent / "styles" / "main.css"
if _css_path.exists():
    st.markdown(f"<style>{_css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
else:
    logger.warning(f"CSS 檔案不存在: {_css_path}")

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

    # 嘗試從最新完成的分析中恢復結果
    if not st.session_state.analysis_results:
        try:
            latest_id = get_latest_analysis_id()
            if latest_id:
                progress_data = get_progress_by_id(latest_id)
                if progress_data and progress_data.get('status') == 'completed':
                    if _restore_results_from_progress(progress_data, latest_id):
                        logger.info(f"[結果恢復] 從分析 {latest_id} 恢復結果")
        except Exception as e:
            logger.warning(f"[結果恢復] 恢復失敗: {e}")

    # 使用cookie管理器恢復分析ID（優先級：session state > cookie > Redis/檔案）
    try:
        persistent_analysis_id = get_persistent_analysis_id()
        if persistent_analysis_id:
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
        # 如果恢復失敗，保持預設值
        logger.warning(f"[狀態恢復] 恢復分析狀態失敗: {e}")
        st.session_state.analysis_running = False
        st.session_state.current_analysis_id = None

    # 恢復表單配置
    try:
        from utils.smart_session_manager import smart_session_manager
        session_data = smart_session_manager.load_analysis_state()

        if session_data and 'form_config' in session_data:
            st.session_state.form_config = session_data['form_config']
            # 只在沒有分析執行時記錄日誌，避免重複
            if not st.session_state.get('analysis_running', False):
                logger.info("[配置恢復] 表單配置已恢復")
    except Exception as e:
        logger.warning(f"[配置恢復] 表單配置恢復失敗: {e}")


def _save_result_safe(analysis_id: str, stock_symbol: str,
                      analysts: list, research_depth: int,
                      result_data, status: str):
    """安全保存分析結果，統一異常處理"""
    try:
        save_analysis_result(
            analysis_id=analysis_id,
            stock_symbol=stock_symbol,
            analysts=analysts,
            research_depth=research_depth,
            result_data=result_data,
            status=status
        )
    except Exception as e:
        logger.error(f"保存分析結果異常: {e}")


def _restore_results_from_progress(progress_data: dict, analysis_id: str) -> bool:
    """從進度資料恢復分析結果至 session_state，成功回傳 True"""
    if not progress_data or 'raw_results' not in progress_data:
        return False
    try:
        raw_results = progress_data['raw_results']
        formatted_results = format_analysis_results(raw_results)
        if not formatted_results:
            return False
        st.session_state.analysis_results = formatted_results
        st.session_state.current_analysis_id = analysis_id
        st.session_state.analysis_running = (progress_data.get('status') == 'running')
        if 'stock_symbol' in raw_results:
            st.session_state.last_stock_symbol = raw_results.get('stock_symbol', '')
        if 'market_type' in raw_results:
            st.session_state.last_market_type = raw_results.get('market_type', '')
        return True
    except Exception as e:
        logger.warning(f"[結果恢復] 恢復失敗: {e}")
        return False


def main():
    """主應用程式"""

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

    # 狀態清理按鈕（僅除錯模式顯示）
    if config.get("enable_debug"):
        if st.sidebar.button("清理分析狀態", help="清理僵屍分析狀態"):
            st.session_state.analysis_running = False
            st.session_state.current_analysis_id = None
            st.session_state.analysis_results = None
            keys_to_remove = [k for k in st.session_state.keys() if 'auto_refresh' in k]
            for key in keys_to_remove:
                del st.session_state[key]
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

            st.info(f"正在啟動 {form_data['stock_symbol']} 分析...")

            st.session_state.current_analysis_id = analysis_id
            st.session_state.last_stock_symbol = form_data['stock_symbol']
            st.session_state.last_market_type = form_data.get('market_type', '美股')

            st.session_state[f"auto_refresh_unified_{analysis_id}"] = True

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
                    _save_result_safe(
                        analysis_id, form_data['stock_symbol'],
                        form_data['analysts'], form_data['research_depth'],
                        results, "completed"
                    )
                    logger.info(f"分析完成: {analysis_id}")

                except Exception as e:
                    async_tracker.mark_failed(str(e))
                    _save_result_safe(
                        analysis_id, form_data['stock_symbol'],
                        form_data['analysts'], form_data['research_depth'],
                        {"error": str(e)}, "failed"
                    )
                    logger.error(f"分析失敗 {analysis_id}: {e}")

                finally:
                    unregister_analysis_thread(analysis_id)

            analysis_thread = threading.Thread(target=run_analysis_in_background)
            analysis_thread.daemon = True
            analysis_thread.start()

            register_analysis_thread(analysis_id, analysis_thread)

            logger.info(f"分析執行緒已啟動: {analysis_id}")

            st.rerun()

    # 分析進度顯示
    current_analysis_id = st.session_state.get('current_analysis_id')
    if current_analysis_id:
        st.markdown("---")

        actual_status = check_analysis_status(current_analysis_id)
        is_running = (actual_status == 'running')

        if st.session_state.get('analysis_running', False) != is_running:
            st.session_state.analysis_running = is_running

        progress_data = get_progress_by_id(current_analysis_id)

        # 取得股票代碼作為顯示名稱
        display_symbol = st.session_state.get('last_stock_symbol', '')

        if is_running:
            st.info(f"正在分析 {display_symbol}..." if display_symbol else "分析進行中...")
        elif actual_status == 'completed':
            st.success(f"{display_symbol} 分析完成" if display_symbol else "分析完成")
        elif actual_status == 'failed':
            st.error(f"{display_symbol} 分析失敗" if display_symbol else "分析失敗")

        is_completed = display_unified_progress(current_analysis_id, show_refresh_controls=is_running)

        if is_running:
            st.caption("分析進行中，可使用自動重新整理查看進度...")

        # 分析完成後恢復結果
        if is_completed and not st.session_state.get('analysis_results') and progress_data:
            if _restore_results_from_progress(progress_data, current_analysis_id):
                st.session_state.analysis_running = False
                stock_symbol = progress_data.get(
                    'stock_symbol', st.session_state.get('last_stock_symbol', 'unknown')
                )
                _save_result_safe(
                    current_analysis_id, stock_symbol,
                    progress_data.get('analysts', []),
                    progress_data.get('research_depth', 3),
                    progress_data.get('raw_results', {}), "completed"
                )
                refresh_key = f"results_refreshed_{current_analysis_id}"
                if not st.session_state.get(refresh_key, False):
                    st.session_state[refresh_key] = True
                    st.rerun()

        if is_completed and st.session_state.get('analysis_running', False):
            st.session_state.analysis_running = False
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
