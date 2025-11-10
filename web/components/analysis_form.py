"""
分析表單組件
"""

import streamlit as st
import datetime

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger

# 導入用戶活動記錄器
try:
    from ..utils.user_activity_logger import user_activity_logger
except ImportError:
    user_activity_logger = None

logger = get_logger('web')


def render_analysis_form():
    """渲染股票分析表單"""

    st.subheader("📋 分析配置")

    # 獲取緩存的表單配置（確保不為None）
    cached_config = st.session_state.get('form_config') or {}

    # 調試信息（只在沒有分析運行時記錄，避免重複）
    if not st.session_state.get('analysis_running', False):
        if cached_config:
            logger.debug(f"📊 [配置恢複] 使用緩存配置: {cached_config}")
        else:
            logger.debug("📊 [配置恢複] 使用默認配置")

    # 創建表單
    with st.form("analysis_form", clear_on_submit=False):

        # 在表單開始時保存當前配置（用於檢測變化）
        initial_config = cached_config.copy() if cached_config else {}
        col1, col2 = st.columns(2)
        
        with col1:
            # 市場選擇（固定為美股）
            market_type = "美股"
            st.info("📊 目前僅支援美股分析")

            # 根據市場類型顯示不同的輸入提示
            cached_stock = cached_config.get('stock_symbol', '') if cached_config else ''

            stock_symbol = st.text_input(
                "股票代碼 📈",
                value=cached_stock if (cached_config and cached_config.get('market_type') == '美股') else '',
                placeholder="輸入美股代碼，如 AAPL, TSLA, MSFT，然後按回車確認",
                help="輸入要分析的美股代碼，輸入完成後請按回車键確認",
                key="us_stock_input",
                autocomplete="off"
            ).upper().strip()

            logger.debug(f"🔍 [FORM DEBUG] 美股text_input返回值: '{stock_symbol}'")
            
            # 分析日期
            analysis_date = st.date_input(
                "分析日期 📅",
                value=datetime.date.today(),
                help="選擇分析的基準日期"
            )
        
        with col2:
            # 研究深度（使用緩存的值）
            cached_depth = cached_config.get('research_depth', 3) if cached_config else 3
            research_depth = st.select_slider(
                "研究深度 🔍",
                options=[1, 2, 3, 4, 5],
                value=cached_depth,
                format_func=lambda x: {
                    1: "1級 - 快速分析",
                    2: "2級 - 基础分析",
                    3: "3級 - 標準分析",
                    4: "4級 - 深度分析",
                    5: "5級 - 全面分析"
                }[x],
                help="選擇分析的深度級別，級別越高分析越詳細但耗時更長"
            )
        
        # 分析師团隊選擇
        st.markdown("### 👥 選擇分析師团隊")

        col1, col2 = st.columns(2)

        # 獲取緩存的分析師選擇和市場類型
        cached_analysts = cached_config.get('selected_analysts', ['market', 'fundamentals']) if cached_config else ['market', 'fundamentals']
        cached_market_type = cached_config.get('market_type', 'A股') if cached_config else 'A股'

        with col1:
            market_analyst = st.checkbox(
                "📈 市場分析師",
                value='market' in cached_analysts,
                help="專註於技術面分析、價格趋势、技術指標"
            )

            social_analyst = st.checkbox(
                "💭 社交媒體分析師",
                value='social' in cached_analysts,
                help="分析社交媒體情绪、投資者情绪指標"
            )

        with col2:
            news_analyst = st.checkbox(
                "📰 新聞分析師",
                value='news' in cached_analysts,
                help="分析相關新聞事件、市場動態影響"
            )

            fundamentals_analyst = st.checkbox(
                "💰 基本面分析師",
                value='fundamentals' in cached_analysts,
                help="分析財務數據、公司基本面、估值水平"
            )

        # 收集選中的分析師
        selected_analysts = []
        if market_analyst:
            selected_analysts.append(("market", "市場分析師"))
        if social_analyst:
            selected_analysts.append(("social", "社交媒體分析師"))
        if news_analyst:
            selected_analysts.append(("news", "新聞分析師"))
        if fundamentals_analyst:
            selected_analysts.append(("fundamentals", "基本面分析師"))
        
        # 顯示選擇摘要
        if selected_analysts:
            st.success(f"已選擇 {len(selected_analysts)} 個分析師: {', '.join([a[1] for a in selected_analysts])}")
        else:
            st.warning("請至少選擇一個分析師")
        
        # 高級選項
        with st.expander("🔧 高級選項"):
            include_sentiment = st.checkbox(
                "包含情绪分析",
                value=True,
                help="是否包含市場情绪和投資者情绪分析"
            )
            
            include_risk_assessment = st.checkbox(
                "包含風險評估",
                value=True,
                help="是否包含詳細的風險因素評估"
            )
            
            custom_prompt = st.text_area(
                "自定義分析要求",
                placeholder="輸入特定的分析要求或關註點...",
                help="可以輸入特定的分析要求，AI會在分析中重點關註"
            )

        # 顯示輸入狀態提示
        if not stock_symbol:
            st.info("💡 請在上方輸入股票代碼，輸入完成後按回車键確認")
        else:
            st.success(f"✅ 已輸入股票代碼: {stock_symbol}")

        # 添加JavaScript來改善用戶體驗
        st.markdown("""
        <script>
        // 監聽輸入框的變化，提供更好的用戶反饋
        document.addEventListener('DOMContentLoaded', function() {
            const inputs = document.querySelectorAll('input[type="text"]');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    if (this.value.trim()) {
                        this.style.borderColor = '#00ff00';
                        this.title = '按回車键確認輸入';
                    } else {
                        this.style.borderColor = '';
                        this.title = '';
                    }
                });
            });
        });
        </script>
        """, unsafe_allow_html=True)

        # 在提交按钮前檢測配置變化並保存
        current_config = {
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'research_depth': research_depth,
            'selected_analysts': [a[0] for a in selected_analysts],
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }

        # 如果配置發生變化，立即保存（即使沒有提交）
        if current_config != initial_config:
            st.session_state.form_config = current_config
            try:
                from utils.smart_session_manager import smart_session_manager
                current_analysis_id = st.session_state.get('current_analysis_id', 'form_config_only')
                smart_session_manager.save_analysis_state(
                    analysis_id=current_analysis_id,
                    status=st.session_state.get('analysis_running', False) and 'running' or 'idle',
                    stock_symbol=stock_symbol,
                    market_type=market_type,
                    form_config=current_config
                )
                logger.debug(f"📊 [配置自動保存] 表單配置已更新")
            except Exception as e:
                logger.warning(f"⚠️ [配置自動保存] 保存失败: {e}")

        # 提交按钮（不禁用，让用戶可以點擊）
        submitted = st.form_submit_button(
            "🚀 開始分析",
            type="primary",
            use_container_width=True
        )

    # 只有在提交時才返回數據
    if submitted and stock_symbol:  # 確保有股票代碼才提交
        # 添加詳細日誌
        logger.debug(f"🔍 [FORM DEBUG] ===== 分析表單提交 =====")
        logger.debug(f"🔍 [FORM DEBUG] 用戶輸入的股票代碼: '{stock_symbol}'")
        logger.debug(f"🔍 [FORM DEBUG] 市場類型: '{market_type}'")
        logger.debug(f"🔍 [FORM DEBUG] 分析日期: '{analysis_date}'")
        logger.debug(f"🔍 [FORM DEBUG] 選擇的分析師: {[a[0] for a in selected_analysts]}")
        logger.debug(f"🔍 [FORM DEBUG] 研究深度: {research_depth}")

        form_data = {
            'submitted': True,
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'analysis_date': str(analysis_date),
            'analysts': [a[0] for a in selected_analysts],
            'research_depth': research_depth,
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }

        # 保存表單配置到緩存和持久化存储
        form_config = {
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'research_depth': research_depth,
            'selected_analysts': [a[0] for a in selected_analysts],
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }
        st.session_state.form_config = form_config

        # 保存到持久化存储
        try:
            from utils.smart_session_manager import smart_session_manager
            # 獲取當前分析ID（如果有的話）
            current_analysis_id = st.session_state.get('current_analysis_id', 'form_config_only')
            smart_session_manager.save_analysis_state(
                analysis_id=current_analysis_id,
                status=st.session_state.get('analysis_running', False) and 'running' or 'idle',
                stock_symbol=stock_symbol,
                market_type=market_type,
                form_config=form_config
            )
        except Exception as e:
            logger.warning(f"⚠️ [配置持久化] 保存失败: {e}")

        # 記錄用戶分析請求活動
        if user_activity_logger:
            try:
                user_activity_logger.log_analysis_request(
                    symbol=stock_symbol,
                    market=market_type,
                    analysis_date=str(analysis_date),
                    research_depth=research_depth,
                    analyst_team=[a[0] for a in selected_analysts],
                    details={
                        'include_sentiment': include_sentiment,
                        'include_risk_assessment': include_risk_assessment,
                        'has_custom_prompt': bool(custom_prompt),
                        'form_source': 'analysis_form'
                    }
                )
                logger.debug(f"📊 [用戶活動] 已記錄分析請求: {stock_symbol}")
            except Exception as e:
                logger.warning(f"⚠️ [用戶活動] 記錄失败: {e}")

        logger.info(f"📊 [配置緩存] 表單配置已保存: {form_config}")

        logger.debug(f"🔍 [FORM DEBUG] 返回的表單數據: {form_data}")
        logger.debug(f"🔍 [FORM DEBUG] ===== 表單提交結束 =====")

        return form_data
    elif submitted and not stock_symbol:
        # 用戶點擊了提交但沒有輸入股票代碼
        logger.error(f"🔍 [FORM DEBUG] 提交失败：股票代碼為空")
        st.error("❌ 請輸入股票代碼後再提交")
        return {'submitted': False}
    else:
        return {'submitted': False}
