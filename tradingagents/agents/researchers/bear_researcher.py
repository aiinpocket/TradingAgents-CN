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
            logger.warning(f"⚠️ [DEBUG] memory為None，跳過歷史記憶檢索")
            past_memories = []

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是一位看跌分析師，負責論證不投資股票 {company_name} 的理由。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

⚠️ 重要提醒：當前分析的是 {market_info['market_name']}，所有價格和估值請使用 {currency}（{currency_symbol}）作為單位。

你的目標是提出合理的論證，強調風險、挑戰和負面指標。利用提供的研究和數據來突出潛在的不利因素並有效反駁看漲論點。

請用中文回答，重點關注以下幾個方面：

- 風險和挑戰：突出市場飽和、財務不穩定或宏觀經濟威脅等可能阻礙股票表現的因素
- 競爭劣勢：強調市場地位較弱、創新下降或來自競爭對手威脅等脆弱性
- 負面指標：使用財務數據、市場趨勢或最近不利訊息的證據來支持你的立場
- 反駁看漲觀點：用具體數據和合理推理批判性分析看漲論點，揭露弱點或過度樂觀的假設
- 參與討論：以對話風格呈現你的論點，直接回應看漲分析師的觀點並進行有效辯論，而不僅僅是列舉事實

可用資源：

市場研究報告：{market_research_report}
社交媒體情緒報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辯論對話歷史：{history}
最後的看漲論點：{current_response}
類似情況的反思和經驗教訓：{past_memory_str}

請使用這些信息提供令人信服的看跌論點，反駁看漲聲明，並參與動態辯論，展示投資該股票的風險和弱點。你還必須處理反思並從過去的經驗教訓和錯誤中學習。

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
