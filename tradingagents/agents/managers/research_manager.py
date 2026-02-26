
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"

        # 安全檢查：確保memory不為None
        if memory is not None:
            past_memories = memory.get_memories(curr_situation, n_matches=2)
        else:
            logger.warning("memory為None，跳過歷史記憶檢索")
            past_memories = []

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是投資組合經理兼辯論主持人。請用繁體中文回答，不可使用簡體字。以自然對話方式呈現分析，不使用特殊格式。

職責：批判性評估多空辯論，做出明確決策（看多/看空/持有）。避免因雙方皆有理就預設持有，須基於最強論點做出承諾。

請提供以下內容：
1. 雙方關鍵觀點摘要（聚焦最有說服力的證據）
2. 明確建議（買入/賣出/持有）及理由
3. 戰略行動：實施建議的具體步驟
4. 目標價格分析：綜合基本面估值、新聞影響、情緒調整、技術支撐阻力位，提供三種情景（保守/基準/樂觀）的具體目標價和時間範圍（1/3/6個月）。必須給出具體價格。

參考過去反思以完善決策：
\"{past_memory_str}\"

綜合分析報告：
市場研究：{market_research_report}
情緒分析：{sentiment_report}
新聞分析：{news_report}
基本面分析：{fundamentals_report}

辯論歷史：
{history}"""
        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
