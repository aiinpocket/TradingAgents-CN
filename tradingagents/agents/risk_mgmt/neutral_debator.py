import time
import json

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""作為中性風險分析師，您的角色是提供平衡的視角，權衡交易員決策或計劃的潛在收益和風險。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**
您優先考慮全面的方法，評估上行和下行風險，同時考慮更廣泛的市場趋势、潛在的經濟變化和多元化策略。以下是交易員的決策：

{trader_decision}

您的任務是挑戰激進和安全分析師，指出每種觀點可能過於乐觀或過於謹慎的地方。使用以下數據來源的見解來支持調整交易員決策的溫和、可持續策略：

市場研究報告：{market_research_report}
社交媒體情绪報告：{sentiment_report}
最新世界事務報告：{news_report}
公司基本面報告：{fundamentals_report}
以下是當前對話歷史：{history} 以下是激進分析師的最後回應：{current_risky_response} 以下是安全分析師的最後回應：{current_safe_response}。如果其他觀點没有回應，請不要虛構，只需提出您的觀點。

通過批判性地分析雙方來積極參与，解決激進和保守論點中的弱點，倡導更平衡的方法。挑戰他們的每個觀點，說明為什么適度風險策略可能提供两全其美的效果，既提供增長潜力又防範極端波動。專註於辩論而不是簡單地呈現數據，旨在表明平衡的觀點可以帶來最可靠的結果。請用中文以對話方式輸出，就像您在說話一樣，不使用任何特殊格式。"""

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
