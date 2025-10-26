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
            logger.warning(f"⚠️ [DEBUG] memory為None，跳過歷史記忆檢索")
            past_memories = []

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""作為投資組合經理和辩論主持人，您的職责是批判性地評估這轮辩論並做出明確決策：支持看跌分析師、看涨分析師，或者仅在基於所提出論點有强有力理由時選擇持有。

簡潔地总結雙方的關键觀點，重點關註最有說服力的證據或推理。您的建议——买入、卖出或持有——必须明確且可操作。避免仅仅因為雙方都有有效觀點就默認選擇持有；要基於辩論中最强有力的論點做出承诺。

此外，為交易員制定詳細的投資計劃。這應该包括：

您的建议：基於最有說服力論點的明確立場。
理由：解釋為什么這些論點導致您的結論。
战略行動：實施建议的具體步骤。
📊 目標價格分析：基於所有可用報告（基本面、新聞、情绪），提供全面的目標價格区間和具體價格目標。考慮：
- 基本面報告中的基本估值
- 新聞對價格預期的影響
- 情绪驱動的價格調整
- 技術支撑/阻力位
- 風險調整價格情景（保守、基準、乐觀）
- 價格目標的時間範围（1個月、3個月、6個月）
💰 您必须提供具體的目標價格 - 不要回複"無法確定"或"需要更多信息"。

考慮您在類似情况下的過去錯誤。利用這些见解來完善您的決策制定，確保您在學习和改進。以對話方式呈現您的分析，就像自然說話一樣，不使用特殊格式。

以下是您對錯誤的過去反思：
\"{past_memory_str}\"

以下是综合分析報告：
市場研究：{market_research_report}

情绪分析：{sentiment_report}

新聞分析：{news_report}

基本面分析：{fundamentals_report}

以下是辩論：
辩論歷史：
{history}

請用中文撰寫所有分析內容和建议。"""
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
