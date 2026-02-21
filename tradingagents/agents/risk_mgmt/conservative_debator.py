
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

        prompt = f"""作為安全/保守風險分析師，您的主要目標是保護資產、最小化波動性，並確保穩定、可靠的增長。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**
您優先考慮穩定性、安全性和風險緩解，仔細評估潛在損失、經濟衰退和市場波動。在評估交易員的決策或計劃時，請批判性地審查高風險要素，指出決策可能使公司面臨不當風險的地方，以及更謹慎的替代方案如何能夠確保長期收益。以下是交易員的決策：

{trader_decision}

您的任務是積極反駁激進和中性分析師的論點，突出他們的觀點可能忽視的潛在威脅或未能優先考慮可持續性的地方。直接回應他們的觀點，利用以下數據來源為交易員決策的低風險方法調整建立令人信服的案例：

市場研究報告：{market_research_report}
社交媒體情緒報告：{sentiment_report}
最新世界事務報告：{news_report}
公司基本面報告：{fundamentals_report}
以下是當前對話歷史：{history} 以下是激進分析師的最後回應：{current_risky_response} 以下是中性分析師的最後回應：{current_neutral_response}。如果其他觀點沒有回應，請不要虛構，只需提出您的觀點。

通過質疑他們的樂觀態度並強調他們可能忽視的潛在下行風險來參與討論。解決他們的每個反駁點，展示為什麼保守立場最終是公司資產最安全的道路。專注於辯論和批評他們的論點，證明低風險策略相對於他們方法的優勢。請用中文以對話方式輸出，就像您在說話一樣，不使用任何特殊格式。"""

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
