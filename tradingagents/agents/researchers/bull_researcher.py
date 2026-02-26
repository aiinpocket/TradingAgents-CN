
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
        logger.debug(f"- 基本面報告前200字元: {fundamentals_report[:200]}...")
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

        prompt = f"""你是看漲分析師，為股票 {company_name} 建立投資論證。請用繁體中文回答，不可使用簡體字。貨幣單位：{currency}（{currency_symbol}）。

以對話風格直接回應看跌論點並有效辯論，重點關注：
- 增長潛力：市場機會、收入預測、可擴展性
- 競爭優勢：獨特產品、品牌優勢、市場地位
- 積極指標：財務健康、行業趨勢、正面訊息
- 反駁看跌觀點：用具體資料和推理解決擔憂

可用資源：
市場研究：{market_research_report}
情緒報告：{sentiment_report}
新聞：{news_report}
基本面：{fundamentals_report}
辯論歷史：{history}
看跌論點：{current_response}
過去經驗教訓：{past_memory_str}
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
