
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 取得股票市場資訊（僅支援美股）
        company_name = state.get('company_of_interest', 'Unknown')
        from tradingagents.utils.stock_utils import get_stock_market_info
        market_info = get_stock_market_info(company_name)

        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']

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

        prompt = f"""你是看跌分析師，論證不投資股票 {company_name} 的理由。請用繁體中文回答，不可使用簡體字。貨幣單位：{currency}（{currency_symbol}）。

以對話風格直接回應看漲論點並有效辯論，重點關注：
- 風險與挑戰：市場飽和、財務不穩定、宏觀經濟威脅
- 競爭劣勢：市場地位弱化、創新下降、競爭對手威脅
- 負面指標：不利的財務資料、市場趨勢、負面訊息
- 反駁看漲觀點：用具體資料揭露弱點或過度樂觀假設

可用資源：
市場研究：{market_research_report}
情緒報告：{sentiment_report}
新聞：{news_report}
基本面：{fundamentals_report}
辯論歷史：{history}
看漲論點：{current_response}
過去經驗教訓：{past_memory_str}
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
