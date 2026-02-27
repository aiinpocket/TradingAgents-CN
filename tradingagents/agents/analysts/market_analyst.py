# 匯入分析模組日誌裝飾器
from tradingagents.utils.tool_logging import log_analyst_module

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("agents.analysts.market")


from tradingagents.agents.utils.agent_utils import calc_start_date as _calc_start_date
from tradingagents.utils.stock_utils import get_company_name as _get_company_name


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
        company_name = _get_company_name(ticker)
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
