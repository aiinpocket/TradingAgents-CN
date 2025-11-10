import time
import json

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

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

        prompt = f"""作為風險管理委員會主席和辩論主持人，您的目標是評估三位風險分析師——激進、中性和安全/保守——之間的辩論，並確定交易員的最佳行動方案。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**
您的決策必须產生明確的建議：买入、卖出或持有。只有在有具體論據强烈支持時才選擇持有，而不是在所有方面都似乎有效時作為後备選擇。力求清晰和果斷。

決策指導原則：
1. **总結關键論點**：提取每位分析師的最强觀點，重點關註与背景的相關性。
2. **提供理由**：用辩論中的直接引用和反驳論點支持您的建議。
3. **完善交易員計劃**：從交易員的原始計劃**{trader_plan}**開始，根據分析師的見解進行調整。
4. **從過去的錯誤中學习**：使用**{past_memory_str}**中的經驗教訓來解決先前的誤判，改進您現在做出的決策，確保您不會做出錯誤的买入/卖出/持有決定而亏損。

交付成果：
- 明確且可操作的建議：买入、卖出或持有。
- 基於辩論和過去反思的詳細推理。

---

**分析師辩論歷史：**
{history}

---

專註於可操作的見解和持续改進。建立在過去經驗教訓的基础上，批判性地評估所有觀點，確保每個決策都能帶來更好的結果。請用中文撰寫所有分析內容和建議。"""

        # 增强的LLM調用，包含錯誤處理和重試機制
        max_retries = 3
        retry_count = 0
        response_content = ""
        
        while retry_count < max_retries:
            try:
                logger.info(f"🔄 [Risk Manager] 調用LLM生成交易決策 (嘗試 {retry_count + 1}/{max_retries})")
                response = llm.invoke(prompt)
                
                if response and hasattr(response, 'content') and response.content:
                    response_content = response.content.strip()
                    if len(response_content) > 10:  # 確保響應有實质內容
                        logger.info(f"✅ [Risk Manager] LLM調用成功，生成決策長度: {len(response_content)} 字符")
                        break
                    else:
                        logger.warning(f"⚠️ [Risk Manager] LLM響應內容過短: {len(response_content)} 字符")
                        response_content = ""
                else:
                    logger.warning(f"⚠️ [Risk Manager] LLM響應為空或無效")
                    response_content = ""
                    
            except Exception as e:
                logger.error(f"❌ [Risk Manager] LLM調用失败 (嘗試 {retry_count + 1}): {str(e)}")
                response_content = ""
            
            retry_count += 1
            if retry_count < max_retries and not response_content:
                logger.info(f"🔄 [Risk Manager] 等待2秒後重試...")
                time.sleep(2)
        
        # 如果所有重試都失败，生成默認決策
        if not response_content:
            logger.error(f"❌ [Risk Manager] 所有LLM調用嘗試失败，使用默認決策")
            response_content = f"""**默認建議：持有**

由於技術原因無法生成詳細分析，基於當前市場狀况和風險控制原則，建議對{company_name}採取持有策略。

**理由：**
1. 市場信息不足，避免盲目操作
2. 保持現有仓位，等待更明確的市場信號
3. 控制風險，避免在不確定性高的情況下做出激進決策

**建議：**
- 密切關註市場動態和公司基本面變化
- 設置合理的止損和止盈位
- 等待更好的入場或出場時機

註意：此為系統默認建議，建議結合人工分析做出最終決策。"""

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

        logger.info(f"📋 [Risk Manager] 最終決策生成完成，內容長度: {len(response_content)} 字符")
        
        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response_content,
        }

    return risk_manager_node
