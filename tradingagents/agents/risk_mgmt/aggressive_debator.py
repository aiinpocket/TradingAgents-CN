
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
from tradingagents.agents.utils.agent_utils import truncate_report
logger = get_logger("agents.risk_mgmt.aggressive")


def create_risky_debator(llm):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 截斷報告上下文：風險辯論者只需關鍵結論，不需完整分析資料
        market_research_report = truncate_report(state["market_report"])
        sentiment_report = truncate_report(state["sentiment_report"])
        news_report = truncate_report(state["news_report"])
        fundamentals_report = truncate_report(state["fundamentals_report"])

        trader_decision = state["trader_investment_plan"]

        # 激進風險分析師 prompt：強調高回報策略與競爭優勢
        prompt = f"""你是激進風險分析師，積極倡導高回報策略，強調增長潛力與競爭優勢。請用繁體中文回答，不可使用簡體字。

交易員決策：
{trader_decision}

參考資料：
- 市場研究：{market_research_report}
- 情緒分析：{sentiment_report}
- 新聞事件：{news_report}
- 基本面：{fundamentals_report}

辯論歷史：{history}
保守分析師觀點：{current_safe_response}
中性分析師觀點：{current_neutral_response}

任務：直接回應保守和中性分析師的每個論點，用資料驅動的反駁指出他們過於謹慎而錯失的機會。強調為什麼高回報策略是最優選擇。若對方尚未回應，直接提出你的觀點即可。以對話方式輸出，不使用任何特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
