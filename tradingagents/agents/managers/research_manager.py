import time
import json

# 導入統一日誌系統
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
            logger.warning(f"[DEBUG] memory為None，跳過歷史記憶檢索")
            past_memories = []

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""作為投資組合經理和辯論主持人，您的職責是批判性地評估這輪辯論並做出明確決策：支持看跌分析師、看漲分析師，或者僅在基於所提出論點有強有力理由時選擇持有。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**


簡潔地總結雙方的關鍵觀點，重點關注最有說服力的證據或推理。您的建議——買入、賣出或持有——必須明確且可操作。避免僅僅因為雙方都有有效觀點就默認選擇持有；要基於辯論中最強有力的論點做出承諾。

此外，為交易員制定詳細的投資計劃。這應該包括：

您的建議：基於最有說服力論點的明確立場。
理由：解釋為什麼這些論點導致您的結論。
戰略行動：實施建議的具體步驟。
目標價格分析：基於所有可用報告（基本面、新聞、情緒），提供全面的目標價格區間和具體價格目標。考慮：
- 基本面報告中的基本估值
- 新聞對價格預期的影響
- 情緒驅動的價格調整
- 技術支撐/阻力位
- 風險調整價格情景（保守、基準、樂觀）
- 價格目標的時間範圍（1個月、3個月、6個月）
您必須提供具體的目標價格 - 不要回覆「無法確定」或「需要更多信息」。

考慮您在類似情況下的過去錯誤。利用這些見解來完善您的決策制定，確保您在學習和改進。以對話方式呈現您的分析，就像自然說話一樣，不使用特殊格式。

以下是您對錯誤的過去反思：
\"{past_memory_str}\"

以下是綜合分析報告：
市場研究：{market_research_report}

情緒分析：{sentiment_report}

新聞分析：{news_report}

基本面分析：{fundamentals_report}

以下是辯論：
辯論歷史：
{history}

請用中文撰寫所有分析內容和建議。"""
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
