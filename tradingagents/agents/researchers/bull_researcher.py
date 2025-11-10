from langchain_core.messages import AIMessage
import time
import json

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        logger.debug(f"🐂 [DEBUG] ===== 看涨研究員節點開始 =====")

        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 使用統一的股票類型檢測
        company_name = state.get('company_of_interest', 'Unknown')
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(company_name)
        is_china = market_info['is_china']
        is_hk = market_info['is_hk']
        is_us = market_info['is_us']

        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']

        logger.debug(f"🐂 [DEBUG] 接收到的報告:")
        logger.debug(f"🐂 [DEBUG] - 市場報告長度: {len(market_research_report)}")
        logger.debug(f"🐂 [DEBUG] - 情绪報告長度: {len(sentiment_report)}")
        logger.debug(f"🐂 [DEBUG] - 新聞報告長度: {len(news_report)}")
        logger.debug(f"🐂 [DEBUG] - 基本面報告長度: {len(fundamentals_report)}")
        logger.debug(f"🐂 [DEBUG] - 基本面報告前200字符: {fundamentals_report[:200]}...")
        logger.debug(f"🐂 [DEBUG] - 股票代碼: {company_name}, 類型: {market_info['market_name']}, 貨币: {currency}")
        logger.debug(f"🐂 [DEBUG] - 市場詳情: 中國A股={is_china}, 港股={is_hk}, 美股={is_us}")

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

        prompt = f"""你是一位看涨分析師，負責為股票 {company_name} 的投資建立强有力的論證。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

⚠️ 重要提醒：當前分析的是 {'中國A股' if is_china else '海外股票'}，所有價格和估值請使用 {currency}（{currency_symbol}）作為單位。

你的任務是構建基於證據的强有力案例，强調增長潜力、競爭優势和積極的市場指標。利用提供的研究和數據來解決擔忧並有效反驳看跌論點。

請用中文回答，重點關註以下几個方面：
- 增長潜力：突出公司的市場機會、收入預測和可擴展性
- 競爭優势：强調獨特產品、强势品牌或主導市場地位等因素
- 積極指標：使用財務健康狀况、行業趋势和最新積極消息作為證據
- 反驳看跌觀點：用具體數據和合理推理批判性分析看跌論點，全面解決擔忧並說明為什么看涨觀點更有說服力
- 參与討論：以對話風格呈現你的論點，直接回應看跌分析師的觀點並進行有效辩論，而不仅仅是列举數據

可用資源：
市場研究報告：{market_research_report}
社交媒體情绪報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辩論對話歷史：{history}
最後的看跌論點：{current_response}
類似情況的反思和經驗教訓：{past_memory_str}

請使用這些信息提供令人信服的看涨論點，反驳看跌擔忧，並參与動態辩論，展示看涨立場的優势。你还必须處理反思並從過去的經驗教訓和錯誤中學习。

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
