
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
from tradingagents.agents.utils.agent_utils import truncate_report, get_situation_for_memory
logger = get_logger("agents.researchers.bull")


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        logger.debug("===== 看漲研究員節點開始 =====")

        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        # 截斷分析報告以降低 token 消耗（辯論用 2000 字元足以涵蓋關鍵論點）
        market_research_report = truncate_report(state["market_report"], max_chars=2000)
        sentiment_report = truncate_report(state["sentiment_report"], max_chars=1500)
        news_report = truncate_report(state["news_report"], max_chars=1500)
        fundamentals_report = truncate_report(state["fundamentals_report"], max_chars=2000)

        # 取得股票市場資訊（僅支援美股）
        company_name = state.get('company_of_interest', 'Unknown')
        from tradingagents.utils.stock_utils import get_stock_market_info
        market_info = get_stock_market_info(company_name)

        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']

        logger.debug(f"[看漲研究員] {company_name} 報告長度: 市場={len(market_research_report)} 情緒={len(sentiment_report)} 新聞={len(news_report)} 基本面={len(fundamentals_report)}")

        # 使用標準化情境描述（所有節點共用相同格式，確保嵌入快取 100% 命中）
        curr_situation = get_situation_for_memory(state)

        # 安全檢查：確保memory不為None
        if memory is not None:
            # 使用快取嵌入（避免多節點重複呼叫嵌入 API）
            from tradingagents.agents.utils.agent_utils import get_cached_embedding
            cached_emb = get_cached_embedding(curr_situation, memory)
            past_memories = memory.get_memories(curr_situation, n_matches=2, cached_embedding=cached_emb)
        else:
            logger.warning("memory為None，跳過歷史記憶檢索")
            past_memories = []

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是看漲分析師，為股票 {company_name} 建立投資論證。請用繁體中文回答，不可使用簡體字。貨幣單位：{currency}（{currency_symbol}）。

以對話風格直接回應看跌論點並有效辯論，重點關注：
- 增長潛力：市場機會、收入預測、可擴展性
- 競爭優勢：獨特產品、品牌優勢、市場地位
- 積極指標：財務健康、行業趨勢、正面訊息
- 反駁看跌觀點：用具體資料和推理解決擔憂

可用資源：
市場研究：{market_research_report}
情緒報告：{sentiment_report}
新聞：{news_report}
基本面：{fundamentals_report}
辯論歷史：{history}
看跌論點：{current_response}
過去經驗教訓：{past_memory_str}
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
