"""
基本面分析師 - 統一工具架構版本
使用統一工具自動識別股票類型並調用相應數據源
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage

# 導入分析模塊日誌裝飾器
from tradingagents.utils.tool_logging import log_analyst_module

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

# 導入Google工具調用處理器
from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler


def _get_company_name_for_fundamentals(ticker: str, market_info: dict) -> str:
    """
    為基本面分析師獲取公司名稱

    Args:
        ticker: 股票代碼
        market_info: 市場信息字典

    Returns:
        str: 公司名稱
    """
    try:
        us_stock_names = {
            'AAPL': '蘋果公司',
            'TSLA': '特斯拉',
            'NVDA': '輝達',
            'MSFT': '微軟',
            'GOOGL': '谷歌',
            'AMZN': '亞馬遜',
            'META': 'Meta',
            'NFLX': 'Netflix'
        }

        company_name = us_stock_names.get(ticker.upper(), ticker)
        logger.debug(f"[基本面分析師] 美股名稱映射: {ticker} -> {company_name}")
        return company_name

    except Exception as e:
        logger.error(f"[基本面分析師] 獲取公司名稱失敗: {e}")
        return ticker


def create_fundamentals_analyst(llm, toolkit):
    @log_analyst_module("fundamentals")
    def fundamentals_analyst_node(state):
        logger.debug(f"📊 [DEBUG] ===== 基本面分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        start_date = '2025-05-28'

        logger.debug(f"📊 [DEBUG] 輸入參數: ticker={ticker}, date={current_date}")
        logger.debug(f"📊 [DEBUG] 當前狀態中的訊息數量: {len(state.get('messages', []))}")
        logger.debug(f"📊 [DEBUG] 現有基本面報告: {state.get('fundamentals_report', 'None')}")

        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info
        logger.info(f"[基本面分析師] 正在分析股票: {ticker}")

        # 股票代碼追蹤日誌
        logger.info(f"[股票代碼追蹤] 基本面分析師接收到的股票代碼: '{ticker}' (類型: {type(ticker)})")

        market_info = get_stock_market_info(ticker)
        logger.info(f"[股票代碼追蹤] get_stock_market_info 返回的市場資訊: {market_info}")

        logger.debug(f"[DEBUG] 股票類型檢查: {ticker} -> {market_info['market_name']} ({market_info['currency_name']})")
        logger.debug(f"[DEBUG] 市場資訊: is_us={market_info['is_us']}")
        logger.debug(f"📊 [DEBUG] 工具配置檢查: online_tools={toolkit.config['online_tools']}")

        # 獲取公司名稱
        company_name = _get_company_name_for_fundamentals(ticker, market_info)
        logger.debug(f"📊 [DEBUG] 公司名稱: {ticker} -> {company_name}")

        # 選擇工具
        if toolkit.config["online_tools"]:
            # 使用統一的基本面分析工具，工具內部會自動識別股票類型
            logger.info(f"📊 [基本面分析師] 使用統一基本面分析工具，自動識別股票類型")
            tools = [toolkit.get_stock_fundamentals_unified]
            # 安全地獲取工具名稱用於調試
            tool_names_debug = []
            for tool in tools:
                if hasattr(tool, 'name'):
                    tool_names_debug.append(tool.name)
                elif hasattr(tool, '__name__'):
                    tool_names_debug.append(tool.__name__)
                else:
                    tool_names_debug.append(str(tool))
            logger.debug(f"📊 [DEBUG] 選擇的工具: {tool_names_debug}")
            logger.debug(f"📊 [DEBUG] 🔧 統一工具將自動處理: {market_info['market_name']}")
        else:
            # 離線模式：使用 FinnHub 和 SimFin 數據
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
            ]

        # 統一的系統提示，適用於所有股票類型
        system_message = (
            f"你是一位專業的股票基本面分析師。"
            f"\n\n**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**\n"
            f"⚠️ 絕對強制要求：你必須調用工具獲取真實數據！不允許任何假設或編造！"
            f"任務：分析{company_name}（股票代碼：{ticker}，{market_info['market_name']}）"
            f"🔴 立即調用 get_stock_fundamentals_unified 工具"
            f"參數：ticker='{ticker}', start_date='{start_date}', end_date='{current_date}', curr_date='{current_date}'"
            "📊 分析要求："
            "- 基於真實數據進行深度基本面分析"
            f"- 計算並提供合理價位區間（使用{market_info['currency_name']}{market_info['currency_symbol']}）"
            "- 分析當前股價是否被低估或高估"
            "- 提供基於基本面的目標價位建議"
            "- 包含PE、PB、PEG等估值指標分析"
            "- 結合市場特點進行分析"
            "🌍 語言和貨幣要求："
            "- 所有分析內容必須使用中文"
            "- 投資建議必須使用中文：買入、持有、賣出"
            "- 絕對不允許使用英文：buy、hold、sell"
            f"- 貨幣單位使用：{market_info['currency_name']}（{market_info['currency_symbol']}）"
            "🚫 嚴格禁止："
            "- 不允許說'我將調用工具'"
            "- 不允許假設任何數據"
            "- 不允許編造公司信息"
            "- 不允許直接回答而不調用工具"
            "- 不允許回覆'無法確定價位'或'需要更多信息'"
            "- 不允許使用英文投資建議（buy/hold/sell）"
            "✅ 你必須："
            "- 立即調用統一基本面分析工具"
            "- 等待工具返回真實數據"
            "- 基於真實數據進行分析"
            "- 提供具體的價位區間和目標價"
            "- 使用中文投資建議（買入/持有/賣出）"
            "現在立即開始調用工具！不要說任何其他話！"
        )

        # 系統提示模板
        system_prompt = (
            "🔴 強制要求：你必須調用工具獲取真實數據！"
            "🚫 絕對禁止：不允許假設、編造或直接回答任何問題！"
            "✅ 你必須：立即調用提供的工具獲取真實數據，然後基於真實數據進行分析。"
            "可用工具：{tool_names}。\n{system_message}"
            "當前日期：{current_date}。"
            "分析目標：{company_name}（股票代碼：{ticker}）。"
            "請確保在分析中正確區分公司名稱和股票代碼。"
        )

        # 創建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        prompt = prompt.partial(system_message=system_message)
        # 安全地獲取工具名稱，處理函數和工具對象
        tool_names = []
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                tool_names.append(tool.__name__)
            else:
                tool_names.append(str(tool))

        prompt = prompt.partial(tool_names=", ".join(tool_names))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=company_name)

        fresh_llm = llm

        logger.debug(f"📊 [DEBUG] 創建LLM鏈，工具數量: {len(tools)}")
        # 安全地獲取工具名稱用於調試
        debug_tool_names = []
        for tool in tools:
            if hasattr(tool, 'name'):
                debug_tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                debug_tool_names.append(tool.__name__)
            else:
                debug_tool_names.append(str(tool))
        logger.debug(f"📊 [DEBUG] 綁定的工具列表: {debug_tool_names}")
        logger.debug(f"📊 [DEBUG] 創建工具鏈，讓模型自主決定是否調用工具")

        try:
            chain = prompt | fresh_llm.bind_tools(tools)
            logger.debug(f"📊 [DEBUG] ✅ 工具綁定成功，綁定了 {len(tools)} 個工具")
        except Exception as e:
            logger.error(f"📊 [DEBUG] ❌ 工具綁定失敗: {e}")
            raise e

        logger.debug(f"📊 [DEBUG] 調用LLM鏈...")

        # 添加詳細的股票代碼追蹤日誌
        logger.info(f"🔍 [股票代碼追蹤] LLM調用前，ticker參數: '{ticker}'")
        logger.info(f"🔍 [股票代碼追蹤] 傳遞給LLM的訊息數量: {len(state['messages'])}")

        # 檢查訊息內容中是否有其他股票代碼
        for i, msg in enumerate(state["messages"]):
            if hasattr(msg, 'content') and msg.content:
                content = str(msg.content)
                if "002021" in content:
                    logger.warning(f"🔍 [股票代碼追蹤] 警告：訊息 {i} 中包含錯誤股票代碼 002021")
                    logger.warning(f"🔍 [股票代碼追蹤] 訊息內容: {content[:200]}...")
                if "002027" in content:
                    logger.info(f"🔍 [股票代碼追蹤] 訊息 {i} 中包含正確股票代碼 002027")

        result = chain.invoke(state["messages"])
        logger.debug(f"📊 [DEBUG] LLM調用完成")

        # 使用統一的Google工具調用處理器
        if GoogleToolCallHandler.is_google_model(fresh_llm):
            logger.info(f"📊 [基本面分析師] 檢測到Google模型，使用統一工具調用處理器")
            
            # 創建分析提示詞
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="基本面分析",
                specific_requirements="重點關注財務數據、盈利能力、估值指標、行業地位等基本面因素。"
            )
            
            # 處理Google模型工具調用
            report, messages = GoogleToolCallHandler.handle_google_tool_calls(
                result=result,
                llm=fresh_llm,
                tools=tools,
                state=state,
                analysis_prompt_template=analysis_prompt_template,
                analyst_name="基本面分析師"
            )
            
            return {"fundamentals_report": report}
        else:
            # 非Google模型的處理邏輯
            logger.debug(f"📊 [DEBUG] 非Google模型 ({fresh_llm.__class__.__name__})，使用標準處理邏輯")
            
            # 檢查工具調用情況
            tool_call_count = len(result.tool_calls) if hasattr(result, 'tool_calls') else 0
            logger.debug(f"📊 [DEBUG] 工具調用數量: {tool_call_count}")
            
            if tool_call_count > 0:
                # 有工具調用，返回狀態讓工具執行
                tool_calls_info = []
                for tc in result.tool_calls:
                    tool_calls_info.append(tc['name'])
                    logger.debug(f"📊 [DEBUG] 工具調用 {len(tool_calls_info)}: {tc}")
                
                logger.info(f"📊 [基本面分析師] 工具調用: {tool_calls_info}")
                return {
                    "messages": [result],
                    "fundamentals_report": result.content if hasattr(result, 'content') else str(result)
                }
            else:
                # 沒有工具調用，使用強制工具調用修複
                logger.debug(f"📊 [DEBUG] 檢測到模型未調用工具，啟用強制工具調用模式")
                
                # 強制調用統一基本面分析工具
                try:
                    logger.debug(f"📊 [DEBUG] 強制調用 get_stock_fundamentals_unified...")
                    # 安全地查找統一基本面分析工具
                    unified_tool = None
                    for tool in tools:
                        tool_name = None
                        if hasattr(tool, 'name'):
                            tool_name = tool.name
                        elif hasattr(tool, '__name__'):
                            tool_name = tool.__name__

                        if tool_name == 'get_stock_fundamentals_unified':
                            unified_tool = tool
                            break
                    if unified_tool:
                        logger.info(f"🔍 [股票代碼追蹤] 強制調用統一工具，傳入ticker: '{ticker}'")
                        combined_data = unified_tool.invoke({
                            'ticker': ticker,
                            'start_date': start_date,
                            'end_date': current_date,
                            'curr_date': current_date
                        })
                        logger.debug(f"📊 [DEBUG] 統一工具數據獲取成功，長度: {len(combined_data)}字符")
                    else:
                        combined_data = "統一基本面分析工具不可用"
                        logger.debug(f"📊 [DEBUG] 統一工具未找到")
                except Exception as e:
                    combined_data = f"統一基本面分析工具調用失敗: {e}"
                    logger.debug(f"📊 [DEBUG] 統一工具調用異常: {e}")
                
                currency_info = f"{market_info['currency_name']}（{market_info['currency_symbol']}）"
                
                # 生成基於真實數據的分析報告
                analysis_prompt = f"""基於以下真實數據，對{company_name}（股票代碼：{ticker}）進行詳細的基本面分析：

{combined_data}

請提供：
1. 公司基本信息分析（{company_name}，股票代碼：{ticker}）
2. 財務狀況評估
3. 盈利能力分析
4. 估值分析（使用{currency_info}）
5. 投資建議（買入/持有/賣出）

要求：
- 基於提供的真實數據進行分析
- 正確使用公司名稱"{company_name}"和股票代碼"{ticker}"
- 價格使用{currency_info}
- 投資建議使用中文
- 分析要詳細且專業"""

                try:
                    # 創建簡單的分析鏈
                    analysis_prompt_template = ChatPromptTemplate.from_messages([
                        ("system", "你是專業的股票基本面分析師，基於提供的真實數據進行分析。"),
                        ("human", "{analysis_request}")
                    ])
                    
                    analysis_chain = analysis_prompt_template | fresh_llm
                    analysis_result = analysis_chain.invoke({"analysis_request": analysis_prompt})
                    
                    if hasattr(analysis_result, 'content'):
                        report = analysis_result.content
                    else:
                        report = str(analysis_result)

                    logger.info(f"📊 [基本面分析師] 強制工具調用完成，報告長度: {len(report)}")
                    
                except Exception as e:
                    logger.error(f"❌ [DEBUG] 強制工具調用分析失敗: {e}")
                    report = f"基本面分析失敗：{str(e)}"
                
                return {"fundamentals_report": report}

        # 這裡不應該到達，但作為備用
        logger.debug(f"📊 [DEBUG] 返回狀態: fundamentals_report長度={len(result.content) if hasattr(result, 'content') else 0}")
        return {
            "messages": [result],
            "fundamentals_report": result.content if hasattr(result, 'content') else str(result)
        }

    return fundamentals_analyst_node
