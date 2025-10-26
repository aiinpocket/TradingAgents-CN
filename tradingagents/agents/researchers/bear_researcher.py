from langchain_core.messages import AIMessage
import time
import json

# 導入統一日誌系統
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

        # 使用統一的股票類型檢測
        company_name = state.get('company_of_interest', 'Unknown')
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(company_name)
        is_china = market_info['is_china']
        is_hk = market_info['is_hk']
        is_us = market_info['is_us']

        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"

        # 安全檢查：確保memory不為None
        if memory is not None:
            past_memories = memory.get_memories(curr_situation, n_matches=2)
        else:
            logger.warning(f"⚠️ [DEBUG] memory為None，跳過歷史記忆檢索")
            past_memories = []

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是一位看跌分析師，负责論證不投資股票 {company_name} 的理由。

⚠️ 重要提醒：當前分析的是 {market_info['market_name']}，所有價格和估值請使用 {currency}（{currency_symbol}）作為單位。

你的目標是提出合理的論證，强調風險、挑战和负面指標。利用提供的研究和數據來突出潜在的不利因素並有效反驳看涨論點。

請用中文回答，重點關註以下几個方面：

- 風險和挑战：突出市場饱和、財務不穩定或宏觀經濟威胁等可能阻碍股票表現的因素
- 競爭劣势：强調市場地位較弱、創新下降或來自競爭對手威胁等脆弱性
- 负面指標：使用財務數據、市場趋势或最近不利消息的證據來支持你的立場
- 反驳看涨觀點：用具體數據和合理推理批判性分析看涨論點，揭露弱點或過度乐觀的假設
- 參与討論：以對話風格呈現你的論點，直接回應看涨分析師的觀點並進行有效辩論，而不仅仅是列举事實

可用資源：

市場研究報告：{market_research_report}
社交媒體情绪報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辩論對話歷史：{history}
最後的看涨論點：{current_response}
類似情况的反思和經驗教训：{past_memory_str}

請使用這些信息提供令人信服的看跌論點，反驳看涨聲明，並參与動態辩論，展示投資该股票的風險和弱點。你还必须處理反思並從過去的經驗教训和錯誤中學习。

請確保所有回答都使用中文。
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
