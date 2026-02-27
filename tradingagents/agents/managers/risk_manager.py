import time

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        risk_debate_state = state["risk_debate_state"]
        # 截斷辯論歷史以降低 deep_think 輸入 token（超過 4000 字元時截斷）
        from tradingagents.agents.utils.agent_utils import truncate_report
        history = truncate_report(risk_debate_state.get("history", ""), max_chars=4000)
        trader_plan = truncate_report(state.get("investment_plan", ""), max_chars=3000)

        # 使用標準化情境描述（與其他節點共用格式，嵌入快取命中率 100%）
        from tradingagents.agents.utils.agent_utils import get_situation_for_memory, get_cached_embedding
        curr_situation = get_situation_for_memory(state)

        # 安全檢查：確保memory不為None
        if memory is not None:
            cached_emb = get_cached_embedding(curr_situation, memory)
            past_memories = memory.get_memories(curr_situation, n_matches=2, cached_embedding=cached_emb)
        else:
            logger.warning("memory為None，跳過歷史記憶檢索")
            past_memories = []

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是風險管理委員會主席。請用繁體中文回答，不可使用簡體字。以自然對話方式呈現分析。

職責：評估激進、中性、保守三位風險分析師的辯論，為交易員確定最佳行動方案。決策必須明確（買入/賣出/持有），避免因各方皆有理就預設持有。

請提供：
1. 各分析師關鍵論點摘要
2. 明確建議及推理依據（引用辯論中的具體論點）
3. 完善交易員計劃：基於原始計劃調整風險控制措施

交易員原始計劃：{trader_plan}

過去經驗教訓（避免重蹈覆轍）：
\"{past_memory_str}\"

分析師辯論歷史：
{history}"""

        # 增強的LLM呼叫，包含錯誤處理和重試機制
        max_retries = 3
        retry_count = 0
        response_content = ""
        
        while retry_count < max_retries:
            try:
                logger.info(f"[Risk Manager] 呼叫LLM生成交易決策 (嘗試 {retry_count + 1}/{max_retries})")
                response = llm.invoke(prompt)
                
                if response and hasattr(response, 'content') and response.content:
                    response_content = response.content.strip()
                    if len(response_content) > 10:  # 確保回應有實質內容
                        logger.info(f"[Risk Manager] LLM呼叫成功，生成決策長度: {len(response_content)} 字元")
                        break
                    else:
                        logger.warning(f"[Risk Manager] LLM回應內容過短: {len(response_content)} 字元")
                        response_content = ""
                else:
                    logger.warning("[Risk Manager] LLM回應為空或無效")
                    response_content = ""
                    
            except Exception as e:
                logger.error(f"[Risk Manager] LLM呼叫失敗 (嘗試 {retry_count + 1}): {str(e)}")
                response_content = ""
            
            retry_count += 1
            if retry_count < max_retries and not response_content:
                # 指數退避：0.5s, 1s, 2s...
                backoff = 0.5 * (2 ** (retry_count - 1))
                logger.info(f"[Risk Manager] 等待 {backoff}s 後重試...")
                time.sleep(backoff)
        
        # 如果所有重試都失敗，生成預設決策
        if not response_content:
            logger.error("[Risk Manager] 所有LLM呼叫嘗試失敗，使用預設決策")
            response_content = f"""**預設建議：持有**

由於技術原因無法生成詳細分析，基於當前市場狀況和風險控制原則，建議對{company_name}採取持有策略。

**理由：**
1. 市場資訊不足，避免盲目操作
2. 保持現有倉位，等待更明確的市場訊號
3. 控制風險，避免在不確定性高的情況下做出激進決策

**建議：**
- 密切關注市場動態和公司基本面變化
- 設定合理的止損和止盈位
- 等待更好的入場或出場時機

注意：此為系統預設建議，建議結合人工分析做出最終決策。"""

        new_risk_debate_state = {
            "judge_decision": response_content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        logger.info(f"[Risk Manager] 最終決策生成完成，內容長度: {len(response_content)} 字元")
        
        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response_content,
        }

    return risk_manager_node
