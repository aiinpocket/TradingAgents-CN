import functools
import time
import json

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 使用統一的股票類型檢測
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(company_name)
        is_china = market_info['is_china']
        is_hk = market_info['is_hk']
        is_us = market_info['is_us']

        # 根據股票類型確定貨币單位
        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']

        logger.debug(f"💰 [DEBUG] ===== 交易員節點開始 =====")
        logger.debug(f"💰 [DEBUG] 交易員檢測股票類型: {company_name} -> {market_info['market_name']}, 貨币: {currency}")
        logger.debug(f"💰 [DEBUG] 貨币符號: {currency_symbol}")
        logger.debug(f"💰 [DEBUG] 市場詳情: 中國A股={is_china}, 港股={is_hk}, 美股={is_us}")
        logger.debug(f"💰 [DEBUG] 基本面報告長度: {len(fundamentals_report)}")
        logger.debug(f"💰 [DEBUG] 基本面報告前200字符: {fundamentals_report[:200]}...")

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"

        # 檢查memory是否可用
        if memory is not None:
            logger.warning(f"⚠️ [DEBUG] memory可用，獲取歷史記忆")
            past_memories = memory.get_memories(curr_situation, n_matches=2)
            past_memory_str = ""
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            logger.warning(f"⚠️ [DEBUG] memory為None，跳過歷史記忆檢索")
            past_memories = []
            past_memory_str = "暂無歷史記忆數據可參考。"

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        messages = [
            {
                "role": "system",
                "content": f"""您是一位專業的交易員，负责分析市場數據並做出投資決策。基於您的分析，請提供具體的买入、卖出或持有建议。

⚠️ 重要提醒：當前分析的股票代碼是 {company_name}，請使用正確的貨币單位：{currency}（{currency_symbol}）

🔴 嚴格要求：
- 股票代碼 {company_name} 的公司名稱必须嚴格按照基本面報告中的真實數據
- 絕對禁止使用錯誤的公司名稱或混淆不同的股票
- 所有分析必须基於提供的真實數據，不允許假設或編造
- **必须提供具體的目標價位，不允許設置為null或空值**

請在您的分析中包含以下關键信息：
1. **投資建议**: 明確的买入/持有/卖出決策
2. **目標價位**: 基於分析的合理目標價格({currency}) - 🚨 强制要求提供具體數值
   - 买入建议：提供目標價位和預期涨幅
   - 持有建议：提供合理價格区間（如：{currency_symbol}XX-XX）
   - 卖出建议：提供止損價位和目標卖出價
3. **置信度**: 對決策的信心程度(0-1之間)
4. **風險評分**: 投資風險等級(0-1之間，0為低風險，1為高風險)
5. **詳細推理**: 支持決策的具體理由

🎯 目標價位計算指導：
- 基於基本面分析中的估值數據（P/E、P/B、DCF等）
- 參考技術分析的支撑位和阻力位
- 考慮行業平均估值水平
- 結合市場情绪和新聞影響
- 即使市場情绪過熱，也要基於合理估值給出目標價

特別註意：
- 如果是中國A股（6位數字代碼），請使用人民币（¥）作為價格單位
- 如果是美股或港股，請使用美元（$）作為價格單位
- 目標價位必须与當前股價的貨币單位保持一致
- 必须使用基本面報告中提供的正確公司名稱
- **絕對不允許說"無法確定目標價"或"需要更多信息"**

請用中文撰寫分析內容，並始终以'最终交易建议: **买入/持有/卖出**'結束您的回應以確認您的建议。

請不要忘記利用過去決策的經驗教训來避免重複錯誤。以下是類似情况下的交易反思和經驗教训: {past_memory_str}""",
            },
            context,
        ]

        logger.debug(f"💰 [DEBUG] 準备調用LLM，系統提示包含貨币: {currency}")
        logger.debug(f"💰 [DEBUG] 系統提示中的關键部分: 目標價格({currency})")

        result = llm.invoke(messages)

        logger.debug(f"💰 [DEBUG] LLM調用完成")
        logger.debug(f"💰 [DEBUG] 交易員回複長度: {len(result.content)}")
        logger.debug(f"💰 [DEBUG] 交易員回複前500字符: {result.content[:500]}...")
        logger.debug(f"💰 [DEBUG] ===== 交易員節點結束 =====")

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
