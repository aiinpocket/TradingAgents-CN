
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        # 截斷辯論歷史以降低 deep_think 輸入 token
        from tradingagents.agents.utils.agent_utils import truncate_report as _trunc
        history = _trunc(state["investment_debate_state"].get("history", ""), max_chars=4000)
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        # 使用標準化情境描述（與其他節點共用格式，嵌入快取命中率 100%）
        from tradingagents.agents.utils.agent_utils import truncate_report, get_situation_for_memory
        curr_situation = get_situation_for_memory(state)

        # 截斷報告以減少 deep_think 模型輸入 token（加速 20-30%）
        # 辯論歷史已包含研究員引用的關鍵資訊，LLM prompt 不需完整報告
        market_summary = truncate_report(market_research_report, max_chars=1500)
        sentiment_summary = truncate_report(sentiment_report, max_chars=1200)
        news_summary = truncate_report(news_report, max_chars=1200)
        fundamentals_summary = truncate_report(fundamentals_report, max_chars=1500)

        # 安全檢查：確保memory不為None
        if memory is not None:
            from tradingagents.agents.utils.agent_utils import get_cached_embedding
            cached_emb = get_cached_embedding(curr_situation, memory)
            past_memories = memory.get_memories(curr_situation, n_matches=2, cached_embedding=cached_emb)
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

綜合分析報告（摘要）：
市場研究：{market_summary}
情緒分析：{sentiment_summary}
新聞分析：{news_summary}
基本面分析：{fundamentals_summary}

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
