from datetime import datetime, timedelta

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic import hub

# 匯入分析模組日誌裝飾器
from tradingagents.utils.tool_logging import log_analyst_module

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


from tradingagents.agents.utils.agent_utils import calc_start_date as _calc_start_date


def _get_company_name(ticker: str, market_info: dict) -> str:
    """
    根據股票代碼取得公司名稱

    Args:
        ticker: 股票代碼
        market_info: 市場資訊字典

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
        logger.debug(f"美股名稱映射: {ticker} -> {company_name}")
        return company_name

    except Exception as e:
        logger.error(f"取得公司名稱失敗: {e}")
        return ticker


def create_market_analyst_react(llm, toolkit):
    """使用 ReAct Agent 模式的市場分析師"""
    @log_analyst_module("market_react")
    def market_analyst_react_node(state):
        logger.debug("===== ReAct市場分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        logger.debug(f"輸入參數: ticker={ticker}, date={current_date}")

        if toolkit.config["online_tools"]:
            # 在線模式，使用 ReAct Agent
            logger.info("[市場分析師] 使用 ReAct Agent 分析美股")

            # 建立美股資料工具
            from langchain_core.tools import BaseTool

            class USStockDataTool(BaseTool):
                name: str = "get_us_stock_data"
                description: str = f"取得美股{ticker}的市場資料和技術指標。直接呼叫，無需參數。"

                def _run(self, query: str = "") -> str:
                    try:
                        logger.debug(f"USStockDataTool 呼叫，股票代碼: {ticker}")
                        from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
                        return get_us_stock_data_cached(
                            symbol=ticker,
                            start_date=_calc_start_date(current_date),
                            end_date=current_date,
                            force_refresh=False
                        )
                    except Exception as e:
                        logger.error(f"優化美股資料取得失敗: {e}")
                        try:
                            return toolkit.get_YFin_data_online.invoke({
                                'symbol': ticker,
                                'start_date': _calc_start_date(current_date),
                                'end_date': current_date
                            })
                        except Exception as e2:
                            return f"取得股票資料失敗: {str(e2)}"

            class FinnhubNewsTool(BaseTool):
                name: str = "get_finnhub_news"
                description: str = f"取得美股{ticker}的最新新聞和市場情緒（透過 FINNHUB API）。直接呼叫，無需參數。"

                def _run(self, query: str = "") -> str:
                    try:
                        logger.debug(f"FinnhubNewsTool 呼叫，股票代碼: {ticker}")
                        return toolkit.get_finnhub_news.invoke({
                            'ticker': ticker,
                            'start_date': _calc_start_date(current_date),
                            'end_date': current_date
                        })
                    except Exception as e:
                        return f"取得新聞資料失敗: {str(e)}"

            tools = [USStockDataTool(), FinnhubNewsTool()]
            query = f"""請對美股{ticker}進行詳細的技術分析。

執行步驟：
1. 使用get_us_stock_data工具取得股票市場資料和技術指標（通過FINNHUB API）
2. 使用get_finnhub_news工具取得最新新聞和市場情緒
3. 基於取得的真實資料進行深入的技術指標分析
4. 直接輸出完整的技術分析報告內容

重要要求：
- 必須輸出完整的技術分析報告內容，不要只是描述報告已完成
- 報告必須基於工具取得的真實資料進行分析
- 報告長度不少於800字
- 包含具體的資料、指標數值和專業分析
- 結合新聞資訊分析市場情緒

報告格式應包含：
## 股票基本資訊
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

                logger.debug("執行 ReAct Agent 查詢...")
                result = agent_executor.invoke({'input': query})

                report = result['output']
                logger.info(f"[市場分析師] ReAct Agent 完成，報告長度: {len(report)}")

            except Exception as e:
                logger.error(f"ReAct Agent 失敗: {str(e)}")
                report = f"ReAct Agent 市場分析失敗: {str(e)}"
        else:
            # 離線模式，使用原有邏輯
            report = "離線模式，暫不支援"

        logger.debug("===== ReAct市場分析師節點結束 =====")

        return {
            "messages": [("assistant", report)],
            "market_report": report,
        }

    return market_analyst_react_node


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        logger.debug("===== 市場分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        logger.debug(f"輸入參數: ticker={ticker}, date={current_date}")
        logger.debug(f"當前狀態中的訊息數量: {len(state.get('messages', []))}")
        logger.debug(f"現有市場報告: {state.get('market_report', 'None')}")

        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info

        market_info = get_stock_market_info(ticker)

        logger.debug(f"股票類型檢查: {ticker} -> {market_info['market_name']} ({market_info['currency_name']})")

        # 取得公司名稱
        company_name = _get_company_name(ticker, market_info)
        logger.debug(f"公司名稱: {ticker} -> {company_name}")

        if toolkit.config["online_tools"]:
            # 直接呼叫工具取得資料（跳過 LLM 工具決策，節省一次 LLM 呼叫）
            logger.info("[市場分析師] 直接呼叫工具取得市場資料和技術訊號")
            start_date = _calc_start_date(current_date)

            from tradingagents.agents.utils.agent_utils import invoke_tools_direct
            tools = [toolkit.get_stock_market_data_unified, toolkit.get_finnhub_technical_signals]
            tool_args = [
                {"ticker": ticker, "start_date": start_date, "end_date": current_date},
                {"ticker": ticker},
            ]
            tool_results = invoke_tools_direct(tools, tool_args, logger)

            market_data = tool_results[0]
            technical_signals = tool_results[1]

            # 單次 LLM 呼叫：基於已取得的工具資料生成分析報告
            from langchain_core.messages import HumanMessage

            analysis_prompt = f"""你是一位專業的股票技術分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。**

請基於以下真實資料，對{company_name}（{ticker}）進行詳細的技術分析。
當前日期：{current_date}
所屬市場：{market_info['market_name']}
計價貨幣：{market_info['currency_name']}（{market_info['currency_symbol']}）

=== 市場資料 ===
{market_data}

=== FinnHub 技術訊號 ===
{technical_signals}

**分析要求：**
1. 基於上述真實資料進行分析，不要編造數據
2. 分析移動平均線、MACD、RSI、布林帶等技術指標
3. 參考 FinnHub 技術分析綜合訊號和支撐壓力位
4. 提供具體的數值和專業分析
5. 給出明確的投資建議
6. 所有價格使用{market_info['currency_name']}表示

**輸出格式：**
## 股票基本資訊
## 技術指標分析
## 價格趨勢分析
## 投資建議"""

            try:
                result = llm.invoke([HumanMessage(content=analysis_prompt)])
                report = result.content
                logger.info(f"[市場分析師] 直接模式完成，報告長度: {len(report)}")
            except Exception as e:
                logger.error(f"[市場分析師] LLM 分析失敗: {e}", exc_info=True)
                report = f"市場分析失敗: {str(e)}"
        else:
            # 離線模式保留原有工具呼叫流程
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
                toolkit.get_finnhub_technical_signals,
            ]
            from langchain_core.messages import HumanMessage
            from tradingagents.agents.utils.agent_utils import invoke_tools_direct

            tool_args = [
                {"symbol": ticker, "start_date": _calc_start_date(current_date), "end_date": current_date},
                {"symbol": ticker, "indicator": "rsi_14", "curr_date": current_date},
                {"ticker": ticker},
            ]
            tool_results = invoke_tools_direct(tools, tool_args, logger)

            result = llm.invoke([HumanMessage(content=(
                f"你是一位專業的股票技術分析師。請用繁體中文分析{ticker}。\n\n"
                + "\n\n".join(f"工具結果 {i+1}:\n{r}" for i, r in enumerate(tool_results))
                + "\n\n請生成完整的技術分析報告。"
            ))])
            report = result.content

        return {
            "messages": [("assistant", report)],
            "market_report": report,
        }

    return market_analyst_node
