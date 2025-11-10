from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
import time
import json
import traceback

# 導入分析模塊日誌裝饰器
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
        if market_info['is_china']:
            # 中國A股：使用統一接口獲取股票信息
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            stock_info = get_china_stock_info_unified(ticker)

            # 解析股票名稱
            if "股票名稱:" in stock_info:
                company_name = stock_info.split("股票名稱:")[1].split("\n")[0].strip()
                logger.debug(f"📊 [DEBUG] 從統一接口獲取中國股票名稱: {ticker} -> {company_name}")
                return company_name
            else:
                logger.warning(f"⚠️ [DEBUG] 無法從統一接口解析股票名稱: {ticker}")
                return f"股票代碼{ticker}"

        elif market_info['is_hk']:
            # 港股：使用改進的港股工具
            try:
                from tradingagents.dataflows.improved_hk_utils import get_hk_company_name_improved
                company_name = get_hk_company_name_improved(ticker)
                logger.debug(f"📊 [DEBUG] 使用改進港股工具獲取名稱: {ticker} -> {company_name}")
                return company_name
            except Exception as e:
                logger.debug(f"📊 [DEBUG] 改進港股工具獲取名稱失败: {e}")
                # 降級方案：生成友好的默認名稱
                clean_ticker = ticker.replace('.HK', '').replace('.hk', '')
                return f"港股{clean_ticker}"

        elif market_info['is_us']:
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

            company_name = us_stock_names.get(ticker.upper(), f"美股{ticker}")
            logger.debug(f"📊 [DEBUG] 美股名稱映射: {ticker} -> {company_name}")
            return company_name

        else:
            return f"股票{ticker}"

    except Exception as e:
        logger.error(f"❌ [DEBUG] 獲取公司名稱失败: {e}")
        return f"股票{ticker}"


def create_market_analyst_react(llm, toolkit):
    """使用ReAct Agent模式的市場分析師（適用於通義千問）"""
    @log_analyst_module("market_react")
    def market_analyst_react_node(state):
        logger.debug(f"📈 [DEBUG] ===== ReAct市場分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        logger.debug(f"📈 [DEBUG] 輸入參數: ticker={ticker}, date={current_date}")

        # 檢查是否為中國股票
        def is_china_stock(ticker_code):
            import re
            return re.match(r'^\d{6}$', str(ticker_code))

        is_china = is_china_stock(ticker)
        logger.debug(f"📈 [DEBUG] 股票類型檢查: {ticker} -> 中國A股: {is_china}")

        if toolkit.config["online_tools"]:
            # 在線模式，使用ReAct Agent
            if is_china:
                logger.info(f"📈 [市場分析師] 使用ReAct Agent分析中國股票")

                # 創建中國股票數據工具
                from langchain_core.tools import BaseTool

                class ChinaStockDataTool(BaseTool):
                    name: str = "get_china_stock_data"
                    description: str = f"獲取中國A股股票{ticker}的市場數據和技術指標（優化緩存版本）。直接調用，無需參數。"

                    def _run(self, query: str = "") -> str:
                        try:
                            logger.debug(f"📈 [DEBUG] ChinaStockDataTool調用，股票代碼: {ticker}")
                            # 使用優化的緩存數據獲取
                            from tradingagents.dataflows.optimized_china_data import get_china_stock_data_cached
                            return get_china_stock_data_cached(
                                symbol=ticker,
                                start_date='2025-05-28',
                                end_date=current_date,
                                force_refresh=False
                            )
                        except Exception as e:
                            logger.error(f"❌ 優化A股數據獲取失败: {e}")
                            # 备用方案：使用原始API
                            try:
                                return toolkit.get_china_stock_data.invoke({
                                    'stock_code': ticker,
                                    'start_date': '2025-05-28',
                                    'end_date': current_date
                                })
                            except Exception as e2:
                                return f"獲取股票數據失败: {str(e2)}"

                tools = [ChinaStockDataTool()]
                query = f"""請對中國A股股票{ticker}進行詳細的技術分析。

執行步骤：
1. 使用get_china_stock_data工具獲取股票市場數據
2. 基於獲取的真實數據進行深入的技術指標分析
3. 直接輸出完整的技術分析報告內容

重要要求：
- 必须輸出完整的技術分析報告內容，不要只是描述報告已完成
- 報告必须基於工具獲取的真實數據進行分析
- 報告長度不少於800字
- 包含具體的數據、指標數值和專業分析

報告格式應包含：
## 股票基本信息
## 技術指標分析
## 價格趋势分析
## 成交量分析
## 市場情绪分析
## 投資建议"""
            else:
                logger.info(f"📈 [市場分析師] 使用ReAct Agent分析美股/港股")

                # 創建美股數據工具
                from langchain_core.tools import BaseTool

                class USStockDataTool(BaseTool):
                    name: str = "get_us_stock_data"
                    description: str = f"獲取美股/港股{ticker}的市場數據和技術指標（優化緩存版本）。直接調用，無需參數。"

                    def _run(self, query: str = "") -> str:
                        try:
                            logger.debug(f"📈 [DEBUG] USStockDataTool調用，股票代碼: {ticker}")
                            # 使用優化的緩存數據獲取
                            from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
                            return get_us_stock_data_cached(
                                symbol=ticker,
                                start_date='2025-05-28',
                                end_date=current_date,
                                force_refresh=False
                            )
                        except Exception as e:
                            logger.error(f"❌ 優化美股數據獲取失败: {e}")
                            # 备用方案：使用原始API
                            try:
                                return toolkit.get_YFin_data_online.invoke({
                                    'symbol': ticker,
                                    'start_date': '2025-05-28',
                                    'end_date': current_date
                                })
                            except Exception as e2:
                                return f"獲取股票數據失败: {str(e2)}"

                class FinnhubNewsTool(BaseTool):
                    name: str = "get_finnhub_news"
                    description: str = f"獲取美股{ticker}的最新新聞和市場情绪（通過FINNHUB API）。直接調用，無需參數。"

                    def _run(self, query: str = "") -> str:
                        try:
                            logger.debug(f"📈 [DEBUG] FinnhubNewsTool調用，股票代碼: {ticker}")
                            return toolkit.get_finnhub_news.invoke({
                                'ticker': ticker,
                                'start_date': '2025-05-28',
                                'end_date': current_date
                            })
                        except Exception as e:
                            return f"獲取新聞數據失败: {str(e)}"

                tools = [USStockDataTool(), FinnhubNewsTool()]
                query = f"""請對美股{ticker}進行詳細的技術分析。

執行步骤：
1. 使用get_us_stock_data工具獲取股票市場數據和技術指標（通過FINNHUB API）
2. 使用get_finnhub_news工具獲取最新新聞和市場情绪
3. 基於獲取的真實數據進行深入的技術指標分析
4. 直接輸出完整的技術分析報告內容

重要要求：
- 必须輸出完整的技術分析報告內容，不要只是描述報告已完成
- 報告必须基於工具獲取的真實數據進行分析
- 報告長度不少於800字
- 包含具體的數據、指標數值和專業分析
- 結合新聞信息分析市場情绪

報告格式應包含：
## 股票基本信息
## 技術指標分析
## 價格趋势分析
## 成交量分析
## 新聞和市場情绪分析
## 投資建议"""

            try:
                # 創建ReAct Agent
                prompt = hub.pull("hwchase17/react")
                agent = create_react_agent(llm, tools, prompt)
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=10,  # 增加到10次迭代，確保有足夠時間完成分析
                    max_execution_time=180  # 增加到3分鐘，給更多時間生成詳細報告
                )

                logger.debug(f"📈 [DEBUG] 執行ReAct Agent查詢...")
                result = agent_executor.invoke({'input': query})

                report = result['output']
                logger.info(f"📈 [市場分析師] ReAct Agent完成，報告長度: {len(report)}")

            except Exception as e:
                logger.error(f"❌ [DEBUG] ReAct Agent失败: {str(e)}")
                report = f"ReAct Agent市場分析失败: {str(e)}"
        else:
            # 離線模式，使用原有逻辑
            report = "離線模式，暂不支持"

        logger.debug(f"📈 [DEBUG] ===== ReAct市場分析師節點結束 =====")

        return {
            "messages": [("assistant", report)],
            "market_report": report,
        }

    return market_analyst_react_node


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        logger.debug(f"📈 [DEBUG] ===== 市場分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        logger.debug(f"📈 [DEBUG] 輸入參數: ticker={ticker}, date={current_date}")
        logger.debug(f"📈 [DEBUG] 當前狀態中的消息數量: {len(state.get('messages', []))}")
        logger.debug(f"📈 [DEBUG] 現有市場報告: {state.get('market_report', 'None')}")

        # 根據股票代碼格式選擇數據源
        from tradingagents.utils.stock_utils import StockUtils

        market_info = StockUtils.get_market_info(ticker)

        logger.debug(f"📈 [DEBUG] 股票類型檢查: {ticker} -> {market_info['market_name']} ({market_info['currency_name']})")

        # 獲取公司名稱
        company_name = _get_company_name(ticker, market_info)
        logger.debug(f"📈 [DEBUG] 公司名稱: {ticker} -> {company_name}")

        if toolkit.config["online_tools"]:
            # 使用統一的市場數據工具，工具內部會自動识別股票類型
            logger.info(f"📊 [市場分析師] 使用統一市場數據工具，自動识別股票類型")
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
            logger.debug(f"📊 [DEBUG] 選擇的工具: {tool_names_debug}")
            logger.debug(f"📊 [DEBUG] 🔧 統一工具将自動處理: {market_info['market_name']}")
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        # 統一的系統提示，適用於所有股票類型
        system_message = (
            f"""你是一位專業的股票技術分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

你必须對{company_name}（股票代碼：{ticker}）進行詳細的技術分析。

**股票信息：**
- 公司名稱：{company_name}
- 股票代碼：{ticker}
- 所屬市場：{market_info['market_name']}
- 計價貨币：{market_info['currency_name']}（{market_info['currency_symbol']}）

**工具調用指令：**
你有一個工具叫做get_stock_market_data_unified，你必须立即調用這個工具來獲取{company_name}（{ticker}）的市場數據。
不要說你将要調用工具，直接調用工具。

**分析要求：**
1. 調用工具後，基於獲取的真實數據進行技術分析
2. 分析移動平均線、MACD、RSI、布林帶等技術指標
3. 考慮{market_info['market_name']}市場特點進行分析
4. 提供具體的數值和專業分析
5. 給出明確的投資建议
6. 所有價格數據使用{market_info['currency_name']}（{market_info['currency_symbol']}）表示

**輸出格式：**
## 📊 股票基本信息
- 公司名稱：{company_name}
- 股票代碼：{ticker}
- 所屬市場：{market_info['market_name']}

## 📈 技術指標分析
## 📉 價格趋势分析
## 💭 投資建议

請使用中文，基於真實數據進行分析。確保在分析中正確使用公司名稱"{company_name}"和股票代碼"{ticker}"。"""
        )


        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一位專業的股票技術分析師，与其他分析師協作。"
                    "使用提供的工具來獲取和分析股票數據。"
                    "如果你無法完全回答，没關系；其他分析師會從不同角度繼续分析。"
                    "執行你能做的技術分析工作來取得進展。"
                    "如果你有明確的技術面投資建议：**买入/持有/卖出**，"
                    "請在你的回複中明確標註，但不要使用'最终交易建议'前缀，因為最终決策需要综合所有分析師的意见。"
                    "你可以使用以下工具：{tool_names}。\n{system_message}"
                    "供你參考，當前日期是{current_date}。"
                    "我們要分析的是{company_name}（股票代碼：{ticker}）。"
                    "請確保所有分析都使用中文，並在分析中正確区分公司名稱和股票代碼。",
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
            logger.info(f"📊 [市場分析師] 檢測到Google模型，使用統一工具調用處理器")
            
            # 創建分析提示詞
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="市場分析",
                specific_requirements="重點關註市場數據、價格走势、交易量變化等市場指標。"
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
            # 非Google模型的處理逻辑
            logger.debug(f"📊 [DEBUG] 非Google模型 ({llm.__class__.__name__})，使用標準處理逻辑")
            
            # 處理市場分析報告
            if len(result.tool_calls) == 0:
                # 没有工具調用，直接使用LLM的回複
                report = result.content
                logger.info(f"📊 [市場分析師] 直接回複，長度: {len(report)}")
            else:
                # 有工具調用，執行工具並生成完整分析報告
                logger.info(f"📊 [市場分析師] 工具調用: {[call.get('name', 'unknown') for call in result.tool_calls]}")

                try:
                    # 執行工具調用
                    from langchain_core.messages import ToolMessage, HumanMessage

                    tool_messages = []
                    for tool_call in result.tool_calls:
                        tool_name = tool_call.get('name')
                        tool_args = tool_call.get('args', {})
                        tool_id = tool_call.get('id')

                        logger.debug(f"📊 [DEBUG] 執行工具: {tool_name}, 參數: {tool_args}")

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
                                    if tool_name == "get_china_stock_data":
                                        # 中國股票數據工具
                                        tool_result = tool.invoke(tool_args)
                                    else:
                                        # 其他工具
                                        tool_result = tool.invoke(tool_args)
                                    logger.debug(f"📊 [DEBUG] 工具執行成功，結果長度: {len(str(tool_result))}")
                                    break
                                except Exception as tool_error:
                                    logger.error(f"❌ [DEBUG] 工具執行失败: {tool_error}")
                                    tool_result = f"工具執行失败: {str(tool_error)}"

                        if tool_result is None:
                            tool_result = f"未找到工具: {tool_name}"

                        # 創建工具消息
                        tool_message = ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_id
                        )
                        tool_messages.append(tool_message)

                    # 基於工具結果生成完整分析報告
                    analysis_prompt = f"""現在請基於上述工具獲取的數據，生成詳細的技術分析報告。

要求：
1. 報告必须基於工具返回的真實數據進行分析
2. 包含具體的技術指標數值和專業分析
3. 提供明確的投資建议和風險提示
4. 報告長度不少於800字
5. 使用中文撰寫

請分析股票{ticker}的技術面情况，包括：
- 價格趋势分析
- 技術指標解讀
- 支撑阻力位分析
- 成交量分析
- 投資建议"""

                    # 構建完整的消息序列
                    messages = state["messages"] + [result] + tool_messages + [HumanMessage(content=analysis_prompt)]

                    # 生成最终分析報告
                    final_result = llm.invoke(messages)
                    report = final_result.content

                    logger.info(f"📊 [市場分析師] 生成完整分析報告，長度: {len(report)}")

                    # 返回包含工具調用和最终分析的完整消息序列
                    return {
                        "messages": [result] + tool_messages + [final_result],
                        "market_report": report,
                    }

                except Exception as e:
                    logger.error(f"❌ [市場分析師] 工具執行或分析生成失败: {e}")
                    traceback.print_exc()

                    # 降級處理：返回工具調用信息
                    report = f"市場分析師調用了工具但分析生成失败: {[call.get('name', 'unknown') for call in result.tool_calls]}"

                    return {
                        "messages": [result],
                        "market_report": report,
                    }

            return {
                "messages": [result],
                "market_report": report,
            }

    return market_analyst_node
