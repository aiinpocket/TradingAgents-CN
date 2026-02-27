
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
from tradingagents.agents.utils.agent_utils import truncate_report
logger = get_logger("agents.risk_mgmt.neutral")


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        # 截斷報告上下文：風險辯論者只需關鍵結論，不需完整分析資料
        market_research_report = truncate_report(state["market_report"])
        sentiment_report = truncate_report(state["sentiment_report"])
        news_report = truncate_report(state["news_report"])
        fundamentals_report = truncate_report(state["fundamentals_report"])

        trader_decision = state["trader_investment_plan"]

        # 中性風險分析師 prompt：平衡視角，權衡收益與風險
        prompt = f"""你是中性風險分析師，提供平衡視角，同時權衡收益潛力與下行風險。請用繁體中文回答，不可使用簡體字。

交易員決策：
{trader_decision}

參考資料：
- 市場研究：{market_research_report}
- 情緒分析：{sentiment_report}
- 新聞事件：{news_report}
- 基本面：{fundamentals_report}

辯論歷史：{history}
激進分析師觀點：{current_risky_response}
保守分析師觀點：{current_safe_response}

任務：批判性分析激進和保守雙方論點中的弱點，指出各自過於樂觀或過於謹慎之處。倡導適度風險策略，說明平衡方法如何兼顧增長潛力與風險防範。若對方尚未回應，直接提出你的觀點即可。以對話方式輸出，不使用任何特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
