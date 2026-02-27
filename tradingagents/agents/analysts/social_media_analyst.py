# 匯入統一日誌系統和分析模組日誌裝飾器
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_analyst_module
from tradingagents.utils.stock_utils import get_company_name as _get_company_name
logger = get_logger("analysts.social_media")


def create_social_media_analyst(llm, toolkit):
    @log_analyst_module("social_media")
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info
        market_info = get_stock_market_info(ticker)
        
        # 取得公司名稱
        company_name = _get_company_name(ticker)
        logger.info(f"[社交媒體分析師] 公司名稱: {company_name}")

        # 直接呼叫工具取得資料（跳過 LLM 工具決策步驟，節省一次 LLM 呼叫）
        logger.info("[社交媒體分析師] 直接呼叫工具取得社群情緒資料")

        from tradingagents.agents.utils.agent_utils import invoke_tools_direct

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news_openai, toolkit.get_finnhub_sentiment_data]
            tool_args = [
                {"ticker": ticker, "curr_date": current_date},
                {"ticker": ticker, "curr_date": current_date},
            ]
        else:
            tools = [toolkit.get_stock_sentiment_unified, toolkit.get_finnhub_sentiment_data]
            tool_args = [
                {"ticker": ticker, "curr_date": current_date},
                {"ticker": ticker, "curr_date": current_date},
            ]

        tool_results = invoke_tools_direct(tools, tool_args, logger)
        social_data = tool_results[0]
        sentiment_data = tool_results[1]

        # 單次 LLM 呼叫：基於已取得的資料生成情緒分析報告
        from langchain_core.messages import HumanMessage

        analysis_prompt = f"""你是一位專業的社交媒體和投資情緒分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。**

請基於以下真實資料，對{company_name}（{ticker}）進行詳細的社群情緒分析。
當前日期：{current_date}

=== 社群與新聞資料 ===
{social_data}

=== FinnHub 情緒量化 ===
{sentiment_data}

**分析要求：**
1. 基於上述真實資料進行分析，不要編造
2. 使用 FinnHub 情緒量化指標（bullish/bearish 比例、行業比較）
3. 分析投資者情緒的變化趨勢和原因
4. 量化投資者情緒強度，給出情緒指數評分（1-10分）
5. 評估情緒變化對短期股價的影響（1-5天）
6. 提供基於情緒的交易時機建議
7. 報告末尾附上 Markdown 表格總結關鍵發現

**輸出格式：**
## 社群情緒概覽
## FinnHub 情緒量化分析
## 投資者情緒趨勢
## 價格影響評估
## 交易建議"""

        try:
            result = llm.invoke([HumanMessage(content=analysis_prompt)])
            report = result.content
            logger.info(f"[社交媒體分析師] 直接模式完成，報告長度: {len(report)}")
        except Exception as e:
            logger.error(f"[社交媒體分析師] LLM 分析失敗: {e}", exc_info=True)
            report = f"社群情緒分析失敗: {str(e)}"

        return {
            "messages": [("assistant", report)],
            "sentiment_report": report,
        }

    return social_media_analyst_node
