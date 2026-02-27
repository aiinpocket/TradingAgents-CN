
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        # 保守風險分析師 prompt：優先保護資產與穩定增長
        prompt = f"""你是保守風險分析師，優先保護資產、最小化波動性，確保穩定可靠的增長。請用繁體中文回答，不可使用簡體字。

交易員決策：
{trader_decision}

參考資料：
- 市場研究：{market_research_report}
- 情緒分析：{sentiment_report}
- 新聞事件：{news_report}
- 基本面：{fundamentals_report}

辯論歷史：{history}
激進分析師觀點：{current_risky_response}
中性分析師觀點：{current_neutral_response}

任務：直接回應激進和中性分析師的每個論點，指出他們忽視的下行風險和潛在威脅。用資料證明保守策略為何是保護資產的最安全道路。若對方尚未回應，直接提出你的觀點即可。以對話方式輸出，不使用任何特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
