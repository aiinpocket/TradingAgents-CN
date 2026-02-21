from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
import time
import json
import traceback

# 導入分析模塊日誌裝飾器
from tradingagents.utils.tool_logging import log_analyst_module

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

# 導入Google工具調用處理器
from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler


def _get_company_name(ticker: str, market_info: dict) -> str:
    """
    根據股票代碼獲取公司名稱

    Args:
        ticker: 股票代碼
        market_info: 市場信息字典

    Returns:
        str: 公司名稱
    """
    try:
        # 美股：使用簡單映射或返回代碼
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
        logger.debug(f"[DEBUG] 美股名稱映射: {ticker} -> {company_name}")
        return company_name

    except Exception as e:
        logger.error(f"[DEBUG] 獲取公司名稱失敗: {e}")
        return ticker


def create_market_analyst_react(llm, toolkit):
    """使用 ReAct Agent 模式的市場分析師"""
    @log_analyst_module("market_react")
    def market_analyst_react_node(state):
        logger.debug(f"[DEBUG] ===== ReAct市場分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        logger.debug(f"[DEBUG] 輸入參數: ticker={ticker}, date={current_date}")

        if toolkit.config["online_tools"]:
            # 在線模式，使用 ReAct Agent
            logger.info(f"[市場分析師] 使用 ReAct Agent 分析美股")

            # 建立美股數據工具
            from langchain_core.tools import BaseTool

            class USStockDataTool(BaseTool):
                name: str = "get_us_stock_data"
                description: str = f"獲取美股{ticker}的市場數據和技術指標。直接調用，無需參數。"

                def _run(self, query: str = "") -> str:
                    try:
                        logger.debug(f"[DEBUG] USStockDataTool 調用，股票代碼: {ticker}")
                        from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
                        return get_us_stock_data_cached(
                            symbol=ticker,
                            start_date='2025-05-28',
                            end_date=current_date,
                            force_refresh=False
                        )
                    except Exception as e:
                        logger.error(f"優化美股數據獲取失敗: {e}")
                        try:
                            return toolkit.get_YFin_data_online.invoke({
                                'symbol': ticker,
                                'start_date': '2025-05-28',
                                'end_date': current_date
                            })
                        except Exception as e2:
                            return f"獲取股票數據失敗: {str(e2)}"

            class FinnhubNewsTool(BaseTool):
                name: str = "get_finnhub_news"
                description: str = f"獲取美股{ticker}的最新新聞和市場情緒（透過 FINNHUB API）。直接調用，無需參數。"

                def _run(self, query: str = "") -> str:
                    try:
                        logger.debug(f"[DEBUG] FinnhubNewsTool 調用，股票代碼: {ticker}")
                        return toolkit.get_finnhub_news.invoke({
                            'ticker': ticker,
                            'start_date': '2025-05-28',
                            'end_date': current_date
                        })
                    except Exception as e:
                        return f"獲取新聞數據失敗: {str(e)}"

            tools = [USStockDataTool(), FinnhubNewsTool()]
            query = f"""請對美股{ticker}進行詳細的技術分析。

執行步驟：
1. 使用get_us_stock_data工具獲取股票市場數據和技術指標（通過FINNHUB API）
2. 使用get_finnhub_news工具獲取最新新聞和市場情緒
3. 基於獲取的真實數據進行深入的技術指標分析
4. 直接輸出完整的技術分析報告內容

重要要求：
- 必須輸出完整的技術分析報告內容，不要只是描述報告已完成
- 報告必須基於工具獲取的真實數據進行分析
- 報告長度不少於800字
- 包含具體的數據、指標數值和專業分析
- 結合新聞信息分析市場情緒

報告格式應包含：
## 股票基本信息
## 技術指標分析
## 價格趨勢分析
## 成交量分析
## 新聞和市場情緒分析
## 投資建議"""

            try:
                prompt = hub.pull("hwchase17/react")
                agent = create_react_agent(llm, tools, prompt)
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=10,
                    max_execution_time=180
                )

                logger.debug(f"[DEBUG] 執行 ReAct Agent 查詢...")
                result = agent_executor.invoke({'input': query})

                report = result['output']
                logger.info(f"[市場分析師] ReAct Agent 完成，報告長度: {len(report)}")

            except Exception as e:
                logger.error(f"[DEBUG] ReAct Agent 失敗: {str(e)}")
                report = f"ReAct Agent 市場分析失敗: {str(e)}"
        else:
            # 離線模式，使用原有邏輯
            report = "離線模式，暫不支援"

        logger.debug(f"[DEBUG] ===== ReAct市場分析師節點結束 =====")

        return {
            "messages": [("assistant", report)],
            "market_report": report,
        }

    return market_analyst_react_node


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        logger.debug(f"[DEBUG] ===== 市場分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        logger.debug(f"[DEBUG] 輸入參數: ticker={ticker}, date={current_date}")
        logger.debug(f"[DEBUG] 當前狀態中的訊息數量: {len(state.get('messages', []))}")
        logger.debug(f"[DEBUG] 現有市場報告: {state.get('market_report', 'None')}")

        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info

        market_info = get_stock_market_info(ticker)

        logger.debug(f"[DEBUG] 股票類型檢查: {ticker} -> {market_info['market_name']} ({market_info['currency_name']})")

        # 獲取公司名稱
        company_name = _get_company_name(ticker, market_info)
        logger.debug(f"[DEBUG] 公司名稱: {ticker} -> {company_name}")

        if toolkit.config["online_tools"]:
            # 使用統一的市場數據工具，工具內部會自動識別股票類型
            logger.info(f"[市場分析師] 使用統一市場數據工具，自動識別股票類型")
            tools = [toolkit.get_stock_market_data_unified]
            # 安全地獲取工具名稱用於調試
            tool_names_debug = []
            for tool in tools:
                if hasattr(tool, 'name'):
                    tool_names_debug.append(tool.name)
                elif hasattr(tool, '__name__'):
                    tool_names_debug.append(tool.__name__)
                else:
                    tool_names_debug.append(str(tool))
            logger.debug(f"[DEBUG] 選擇的工具: {tool_names_debug}")
            logger.debug(f"[DEBUG] 統一工具將自動處理: {market_info['market_name']}")
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        # 統一的系統提示，適用於所有股票類型
        system_message = (
            f"""你是一位專業的股票技術分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

你必須對{company_name}（股票代碼：{ticker}）進行詳細的技術分析。

**股票信息：**
- 公司名稱：{company_name}
- 股票代碼：{ticker}
- 所屬市場：{market_info['market_name']}
- 計價貨幣：{market_info['currency_name']}（{market_info['currency_symbol']}）

**工具調用指令：**
你有一個工具叫做get_stock_market_data_unified，你必須立即調用這個工具來獲取{company_name}（{ticker}）的市場數據。
不要說你將要調用工具，直接調用工具。

**分析要求：**
1. 調用工具後，基於獲取的真實數據進行技術分析
2. 分析移動平均線、MACD、RSI、布林帶等技術指標
3. 考慮{market_info['market_name']}市場特點進行分析
4. 提供具體的數值和專業分析
5. 給出明確的投資建議
6. 所有價格數據使用{market_info['currency_name']}（{market_info['currency_symbol']}）表示

**輸出格式：**
## 股票基本信息
- 公司名稱：{company_name}
- 股票代碼：{ticker}
- 所屬市場：{market_info['market_name']}

## 技術指標分析
## 價格趨勢分析
## 投資建議

請使用中文，基於真實數據進行分析。確保在分析中正確使用公司名稱"{company_name}"和股票代碼"{ticker}"。"""
        )


        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一位專業的股票技術分析師，與其他分析師協作。"
                    "使用提供的工具來獲取和分析股票數據。"
                    "如果你無法完全回答，沒關係；其他分析師會從不同角度繼續分析。"
                    "執行你能做的技術分析工作來取得進展。"
                    "如果你有明確的技術面投資建議：**買入/持有/賣出**，"
                    "請在你的回覆中明確標註，但不要使用'最終交易建議'前綴，因為最終決策需要綜合所有分析師的意見。"
                    "你可以使用以下工具：{tool_names}。\n{system_message}"
                    "供你參考，當前日期是{current_date}。"
                    "我們要分析的是{company_name}（股票代碼：{ticker}）。"
                    "請確保所有分析都使用中文，並在分析中正確區分公司名稱和股票代碼。",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

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

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        # 使用統一的Google工具調用處理器
        if GoogleToolCallHandler.is_google_model(llm):
            logger.info(f"[市場分析師] 檢測到Google模型，使用統一工具調用處理器")
            
            # 創建分析提示詞
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="市場分析",
                specific_requirements="重點關注市場數據、價格走勢、交易量變化等市場指標。"
            )
            
            # 處理Google模型工具調用
            report, messages = GoogleToolCallHandler.handle_google_tool_calls(
                result=result,
                llm=llm,
                tools=tools,
                state=state,
                analysis_prompt_template=analysis_prompt_template,
                analyst_name="市場分析師"
            )
            
            return {
                "messages": [result],
                "market_report": report,
            }
        else:
            # 非Google模型的處理邏輯
            logger.debug(f"[DEBUG] 非Google模型 ({llm.__class__.__name__})，使用標準處理邏輯")
            
            # 處理市場分析報告
            if len(result.tool_calls) == 0:
                # 沒有工具調用，直接使用LLM的回覆
                report = result.content
                logger.info(f"[市場分析師] 直接回覆，長度: {len(report)}")
            else:
                # 有工具調用，執行工具並生成完整分析報告
                logger.info(f"[市場分析師] 工具調用: {[call.get('name', 'unknown') for call in result.tool_calls]}")

                try:
                    # 執行工具調用
                    from langchain_core.messages import ToolMessage, HumanMessage

                    tool_messages = []
                    for tool_call in result.tool_calls:
                        tool_name = tool_call.get('name')
                        tool_args = tool_call.get('args', {})
                        tool_id = tool_call.get('id')

                        logger.debug(f"[DEBUG] 執行工具: {tool_name}, 參數: {tool_args}")

                        # 找到對應的工具並執行
                        tool_result = None
                        for tool in tools:
                            # 安全地獲取工具名稱進行比較
                            current_tool_name = None
                            if hasattr(tool, 'name'):
                                current_tool_name = tool.name
                            elif hasattr(tool, '__name__'):
                                current_tool_name = tool.__name__

                            if current_tool_name == tool_name:
                                try:
                                    tool_result = tool.invoke(tool_args)
                                    logger.debug(f"[DEBUG] 工具執行成功，結果長度: {len(str(tool_result))}")
                                    break
                                except Exception as tool_error:
                                    logger.error(f"[DEBUG] 工具執行失敗: {tool_error}")
                                    tool_result = f"工具執行失敗: {str(tool_error)}"

                        if tool_result is None:
                            tool_result = f"未找到工具: {tool_name}"

                        # 創建工具訊息
                        tool_message = ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_id
                        )
                        tool_messages.append(tool_message)

                    # 基於工具結果生成完整分析報告
                    analysis_prompt = f"""現在請基於上述工具獲取的數據，生成詳細的技術分析報告。

要求：
1. 報告必須基於工具返回的真實數據進行分析
2. 包含具體的技術指標數值和專業分析
3. 提供明確的投資建議和風險提示
4. 報告長度不少於800字
5. 使用中文撰寫

請分析股票{ticker}的技術面情況，包括：
- 價格趨勢分析
- 技術指標解讀
- 支撐阻力位分析
- 成交量分析
- 投資建議"""

                    # 構建完整的訊息序列
                    messages = state["messages"] + [result] + tool_messages + [HumanMessage(content=analysis_prompt)]

                    # 生成最終分析報告
                    final_result = llm.invoke(messages)
                    report = final_result.content

                    logger.info(f"[市場分析師] 生成完整分析報告，長度: {len(report)}")

                    # 返回包含工具調用和最終分析的完整訊息序列
                    return {
                        "messages": [result] + tool_messages + [final_result],
                        "market_report": report,
                    }

                except Exception as e:
                    logger.error(f"[市場分析師] 工具執行或分析生成失敗: {e}")
                    traceback.print_exc()

                    # 降級處理：返回工具調用信息
                    report = f"市場分析師調用了工具但分析生成失敗: {[call.get('name', 'unknown') for call in result.tool_calls]}"

                    return {
                        "messages": [result],
                        "market_report": report,
                    }

            return {
                "messages": [result],
                "market_report": report,
            }

    return market_analyst_node
