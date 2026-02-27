import functools

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
from tradingagents.agents.utils.agent_utils import get_situation_for_memory
logger = get_logger("default")


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]

        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info
        market_info = get_stock_market_info(company_name)

        # 確定貨幣單位
        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']

        logger.debug("===== 交易員節點開始 =====")
        logger.debug(f"交易員檢測股票類型: {company_name} -> {market_info['market_name']}, 貨幣: {currency}")
        logger.debug(f"貨幣符號: {currency_symbol}")

        # 使用標準化情境描述（與其他節點共用格式，嵌入快取命中率 100%）
        curr_situation = get_situation_for_memory(state)

        # 檢查memory是否可用
        if memory is not None:
            logger.debug("memory可用，取得歷史記憶")
            from tradingagents.agents.utils.agent_utils import get_cached_embedding
            cached_emb = get_cached_embedding(curr_situation, memory)
            past_memories = memory.get_memories(curr_situation, n_matches=2, cached_embedding=cached_emb)
            past_memory_str = ""
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            logger.warning("memory為None，跳過歷史記憶檢索")
            past_memories = []
            past_memory_str = "暫無歷史記憶資料可參考。"

        # 交易員接收 Research Manager 的投資計劃，作為交易決策的基礎
        context = {
            "role": "user",
            "content": f"以下是分析團隊針對 {company_name} 的綜合投資計劃，整合了技術面趨勢、宏觀經濟指標及社群情緒分析。請以此為基礎做出交易決策。\n\n投資計劃：{investment_plan}",
        }

        messages = [
            {
                "role": "system",
                "content": f"""你是專業交易員。請用繁體中文回答，不可使用簡體字。

當前股票：{company_name}，貨幣單位：{currency}（{currency_symbol}）

嚴格要求：
- 公司名稱必須依照基本面報告中的真實資料，禁止混淆或編造
- 所有分析必須基於提供的真實資料
- 必須提供具體目標價位（不允許 null 或「無法確定」）

分析內容須包含：
1. 投資建議：明確的買入/持有/賣出決策
2. 目標價位（{currency_symbol}）：基於估值（P/E、P/B、DCF）、技術支撐阻力位、行業估值水平及市場情緒綜合判斷
   - 買入：目標價 + 預期漲幅
   - 持有：合理價格區間
   - 賣出：止損價 + 目標賣出價
3. 置信度（0-1）
4. 風險評分（0-1，0=低風險）
5. 詳細推理

過去交易反思（避免重蹈覆轍）：{past_memory_str}

以「最終交易建議: **買入/持有/賣出**」結束回應。""",
            },
            context,
        ]

        logger.debug(f"準備呼叫LLM，系統提示包含貨幣: {currency}")
        logger.debug(f"系統提示中的關鍵部分: 目標價格({currency})")

        result = llm.invoke(messages)

        logger.debug("LLM呼叫完成")
        logger.debug(f"交易員回覆長度: {len(result.content)}")
        logger.debug(f"交易員回覆前500字元: {result.content[:500]}...")
        logger.debug("===== 交易員節點結束 =====")

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
