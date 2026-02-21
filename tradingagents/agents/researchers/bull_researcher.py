
# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        logger.debug("===== 看漲研究員節點開始 =====")

        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

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

        logger.debug("接收到的報告:")
        logger.debug(f"- 市場報告長度: {len(market_research_report)}")
        logger.debug(f"- 情緒報告長度: {len(sentiment_report)}")
        logger.debug(f"- 新聞報告長度: {len(news_report)}")
        logger.debug(f"- 基本面報告長度: {len(fundamentals_report)}")
        logger.debug(f"- 基本面報告前200字符: {fundamentals_report[:200]}...")
        logger.debug(f"- 股票代碼: {company_name}, 類型: {market_info['market_name']}, 貨幣: {currency}")

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

        prompt = f"""你是一位看漲分析師，負責為股票 {company_name} 的投資建立強有力的論證。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

重要提醒：當前分析的是{market_info['market_name']}，所有價格和估值請使用 {currency}（{currency_symbol}）作為單位。

你的任務是構建基於證據的強有力案例，強調增長潛力、競爭優勢和積極的市場指標。利用提供的研究和數據來解決擔憂並有效反駁看跌論點。

請用中文回答，重點關注以下幾個方面：
- 增長潛力：突出公司的市場機會、收入預測和可擴展性
- 競爭優勢：強調獨特產品、強勢品牌或主導市場地位等因素
- 積極指標：使用財務健康狀況、行業趨勢和最新積極訊息作為證據
- 反駁看跌觀點：用具體數據和合理推理批判性分析看跌論點，全面解決擔憂並說明為什麼看漲觀點更有說服力
- 參與討論：以對話風格呈現你的論點，直接回應看跌分析師的觀點並進行有效辯論，而不僅僅是列舉數據

可用資源：
市場研究報告：{market_research_report}
社交媒體情緒報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辯論對話歷史：{history}
最後的看跌論點：{current_response}
類似情況的反思和經驗教訓：{past_memory_str}

請使用這些資訊提供令人信服的看漲論點，反駁看跌擔憂，並參與動態辯論，展示看漲立場的優勢。你還必須處理反思並從過去的經驗教訓和錯誤中學習。

請確保所有回答都使用中文。
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
