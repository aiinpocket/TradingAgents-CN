"""
分析表單組件
"""

import streamlit as st
import datetime

from tradingagents.utils.logging_manager import get_logger

logger = get_logger('web')


def render_analysis_form():
    """渲染股票分析表單，收集使用者輸入的分析參數"""

    # 取得緩存的表單配置
    cached_config = st.session_state.get('form_config') or {}

    # 建立表單
    with st.form("analysis_form", clear_on_submit=False):

        initial_config = cached_config.copy() if cached_config else {}
        col1, col2 = st.columns(2)

        with col1:
            # 市場選擇（固定為美股）
            market_type = "美股"
            st.caption("支援美股 (NYSE/NASDAQ)")

            cached_stock = cached_config.get('stock_symbol', '') if cached_config else ''

            stock_symbol = st.text_input(
                "股票代碼",
                value=cached_stock if (cached_config and cached_config.get('market_type') in ('美股', 'US Market')) else '',
                placeholder="輸入美股代碼，如 AAPL, TSLA, MSFT，然後按回車確認",
                help="輸入要分析的美股代碼，輸入完成後請按回車鍵確認",
                key="us_stock_input",
                autocomplete="off").upper().strip()

            # 分析日期
            analysis_date = st.date_input(
                "分析日期",
                value=datetime.date.today(),
                help="選擇分析的基準日期"
            )

        with col2:
            # 研究深度
            cached_depth = cached_config.get('research_depth', 3) if cached_config else 3
            research_depth = st.select_slider(
                "研究深度",
                options=[1, 2, 3, 4, 5],
                value=cached_depth,
                format_func=lambda x: {
                    1: "1級 - 快速分析",
                    2: "2級 - 基礎分析",
                    3: "3級 - 標準分析",
                    4: "4級 - 深度分析",
                    5: "5級 - 全面分析"
                }[x],
                help="選擇分析的深度級別，級別越高分析越詳細但耗時更長"
            )

        # 分析師團隊選擇
        st.markdown("**分析師團隊**")

        col1, col2 = st.columns(2)

        cached_analysts = cached_config.get('selected_analysts', ['market', 'fundamentals']) if cached_config else ['market', 'fundamentals']

        with col1:
            market_analyst = st.checkbox(
                "市場分析師",
                value='market' in cached_analysts,
                help="專注於技術面分析、價格趨勢、技術指標"
            )

            social_analyst = st.checkbox(
                "社交媒體分析師",
                value='social' in cached_analysts,
                help="分析社交媒體情緒、投資者情緒指標"
            )

        with col2:
            news_analyst = st.checkbox(
                "新聞分析師",
                value='news' in cached_analysts,
                help="分析相關新聞事件、市場動態影響"
            )

            fundamentals_analyst = st.checkbox(
                "基本面分析師",
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

        # 提示至少選擇一個分析師
        if not selected_analysts:
            st.warning("請至少選擇一個分析師")

        # 高級選項
        with st.expander("高級選項"):
            include_sentiment = st.checkbox(
                "包含情緒分析",
                value=True,
                help="是否包含市場情緒和投資者情緒分析"
            )

            include_risk_assessment = st.checkbox(
                "包含風險評估",
                value=True,
                help="是否包含詳細的風險因素評估"
            )

            custom_prompt = st.text_area(
                "自定義分析要求",
                placeholder="輸入特定的分析要求或關注點...",
                help="輸入特定的分析要求，系統會重點關注"
            )

        # 顯示輸入提示（僅在未輸入時）
        if not stock_symbol:
            st.caption("請輸入股票代碼後按回車確認")

        # 在提交按鈕前檢測配置變化並保存
        current_config = {
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'research_depth': research_depth,
            'selected_analysts': [a[0] for a in selected_analysts],
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }

        # 配置變化時自動保存
        if current_config != initial_config:
            st.session_state.form_config = current_config
            try:
                from utils.smart_session_manager import smart_session_manager
                current_analysis_id = st.session_state.get('current_analysis_id', 'form_config_only')
                smart_session_manager.save_analysis_state(
                    analysis_id=current_analysis_id,
                    status='running' if st.session_state.get('analysis_running', False) else 'idle',
                    stock_symbol=stock_symbol,
                    market_type=market_type,
                    form_config=current_config
                )
            except Exception as e:
                logger.warning(f"配置自動保存失敗: {e}")

        # 提交按鈕
        submitted = st.form_submit_button(
            "開始分析",
            type="primary",
            use_container_width=True
        )

    # 提交時返回表單數據
    if submitted and stock_symbol:
        logger.info(f"分析表單提交: {stock_symbol} ({market_type})")

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

        # 保存表單配置到緩存和持久化儲存（複用已建構的 current_config）
        st.session_state.form_config = current_config

        try:
            from utils.smart_session_manager import smart_session_manager
            current_analysis_id = st.session_state.get('current_analysis_id', 'form_config_only')
            smart_session_manager.save_analysis_state(
                analysis_id=current_analysis_id,
                status='running' if st.session_state.get('analysis_running', False) else 'idle',
                stock_symbol=stock_symbol,
                market_type=market_type,
                form_config=current_config
            )
        except Exception as e:
            logger.warning(f"配置持久化保存失敗: {e}")

        return form_data
    elif submitted and not stock_symbol:
        st.error("請輸入股票代碼後再提交")
        return {'submitted': False}
    else:
        return {'submitted': False}
