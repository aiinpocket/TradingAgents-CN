from datetime import datetime

# 匯入統一日誌系統和分析模組日誌裝飾器
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_analyst_module
# 匯入統一新聞工具
from tradingagents.tools.unified_news_tool import create_unified_news_tool
# 匯入股票市場資訊工具和公司名稱查詢
from tradingagents.utils.stock_utils import get_stock_market_info, get_company_name as _get_company_name
logger = get_logger("analysts.news")


def create_news_analyst(llm, toolkit):
    @log_analyst_module("news")
    def news_analyst_node(state):
        start_time = datetime.now()
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        logger.info(f"[新聞分析師] 開始分析 {ticker} 的新聞，交易日期: {current_date}")
        session_id = state.get("session_id", "未知會話")
        logger.info(f"[新聞分析師] 會話ID: {session_id}，開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 取得市場資訊（僅支援美股）
        market_info = get_stock_market_info(ticker)
        logger.info(f"[新聞分析師] 股票類型: {market_info['market_name']}")
        
        # 取得公司名稱
        company_name = _get_company_name(ticker)
        logger.info(f"[新聞分析師] 公司名稱: {company_name}")
        
        # 直接呼叫工具取得資料（跳過 LLM 工具決策步驟，節省一次 LLM 呼叫）
        logger.info("[新聞分析師] 直接呼叫統一新聞工具和 FinnHub 情緒工具")

        unified_news_tool = create_unified_news_tool(toolkit)
        unified_news_tool.name = "get_stock_news_unified"

        from tradingagents.agents.utils.agent_utils import invoke_tools_direct
        tools = [unified_news_tool, toolkit.get_finnhub_sentiment_data]
        tool_args = [
            {"stock_code": ticker, "max_news": 10, "model_info": ""},
            {"ticker": ticker, "curr_date": current_date},
        ]
        tool_results = invoke_tools_direct(tools, tool_args, logger)

        news_data = tool_results[0]
        sentiment_data = tool_results[1]

        tool_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[新聞分析師] 工具呼叫完成，耗時: {tool_time:.2f}秒")

        # 單次 LLM 呼叫：基於已取得的資料生成新聞分析報告
        from langchain_core.messages import HumanMessage

        analysis_prompt = f"""你是一位專業的財經新聞分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。**

請基於以下真實資料，對{company_name}（{ticker}）進行詳細的新聞與輿情分析。
當前日期：{current_date}

=== 最新新聞資料 ===
{news_data}

=== FinnHub 新聞情緒量化 ===
{sentiment_data}

**分析要求：**
1. 基於上述真實新聞資料進行分析，不要編造
2. 評估新聞事件的緊急程度和市場影響
3. 使用 FinnHub 情緒量化評分佐證分析判斷
4. 評估新聞對股價的短期影響（1-3天）和價格波動幅度
5. 識別關鍵價格支撐位和阻力位
6. 報告末尾附上 Markdown 表格總結關鍵發現

**輸出格式：**
## 重要新聞摘要
## 市場情緒分析
## 價格影響評估
## 投資建議"""

        try:
            llm_start_time = datetime.now()
            result = llm.invoke([HumanMessage(content=analysis_prompt)])
            report = result.content
            llm_time = (datetime.now() - llm_start_time).total_seconds()
            logger.info(f"[新聞分析師] 直接模式完成，報告長度: {len(report)}，LLM耗時: {llm_time:.2f}秒")
        except Exception as e:
            logger.error(f"[新聞分析師] LLM 分析失敗: {e}", exc_info=True)
            report = f"新聞分析失敗: {str(e)}"

        total_time_taken = (datetime.now() - start_time).total_seconds()
        logger.info(f"[新聞分析師] 新聞分析完成，總耗時: {total_time_taken:.2f}秒")

        return {
            "messages": [("assistant", report)],
            "news_report": report,
        }

    return news_analyst_node
