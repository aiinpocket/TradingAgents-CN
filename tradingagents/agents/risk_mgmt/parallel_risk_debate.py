# 並行風險分析辯論包裝器
# 當風險辯論僅需一輪時，同時執行三位風險分析師（激進、保守、中立）以加速分析

from concurrent.futures import ThreadPoolExecutor, as_completed

from tradingagents.utils.logging_init import get_logger
logger = get_logger("agents.risk_mgmt.parallel")


def create_parallel_risk_debate(risky_fn, safe_fn, neutral_fn):
    """建立並行風險辯論節點，同時執行三位風險分析師。

    適用於 max_risk_discuss_rounds == 1 的情境：
    第一輪中三位分析師尚未看到彼此的回應，因此可安全並行執行。
    串行執行約需 6 秒（每位分析師 ~2 秒），並行後約 2 秒完成。
    """

    def parallel_risk_debate_node(state) -> dict:
        logger.info("[Parallel Risk Debate] 啟動三位風險分析師並行執行")

        results = {}
        errors = {}

        # 使用執行緒池同時呼叫三位分析師的 LLM
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix="risk_analyst") as executor:
            futures = {
                executor.submit(risky_fn, state): "risky",
                executor.submit(safe_fn, state): "safe",
                executor.submit(neutral_fn, state): "neutral",
            }

            for future in as_completed(futures):
                analyst_name = futures[future]
                try:
                    results[analyst_name] = future.result()
                    logger.info(f"[Parallel Risk Debate] {analyst_name} 分析師完成")
                except Exception as e:
                    logger.error(f"[Parallel Risk Debate] {analyst_name} 分析師發生錯誤: {e}")
                    errors[analyst_name] = str(e)

        if errors:
            logger.warning(f"[Parallel Risk Debate] 部分分析師失敗: {list(errors.keys())}")

        # 合併三位分析師的結果
        risk_debate_state = state["risk_debate_state"]
        base_history = risk_debate_state.get("history", "")
        base_count = risk_debate_state.get("count", 0)

        # 從各分析師結果中提取回應
        risky_state = results.get("risky", {}).get("risk_debate_state", {})
        safe_state = results.get("safe", {}).get("risk_debate_state", {})
        neutral_state = results.get("neutral", {}).get("risk_debate_state", {})

        risky_response = risky_state.get("current_risky_response", "")
        safe_response = safe_state.get("current_safe_response", "")
        neutral_response = neutral_state.get("current_neutral_response", "")

        # 合併對話歷史：將三位分析師的回應按序加入
        combined_history = base_history
        if risky_response:
            combined_history += "\n" + risky_response
        if safe_response:
            combined_history += "\n" + safe_response
        if neutral_response:
            combined_history += "\n" + neutral_response

        merged_state = {
            "history": combined_history,
            "risky_history": risky_state.get(
                "risky_history", risk_debate_state.get("risky_history", "")
            ),
            "safe_history": safe_state.get(
                "safe_history", risk_debate_state.get("safe_history", "")
            ),
            "neutral_history": neutral_state.get(
                "neutral_history", risk_debate_state.get("neutral_history", "")
            ),
            "latest_speaker": "Neutral",
            "current_risky_response": risky_response,
            "current_safe_response": safe_response,
            "current_neutral_response": neutral_response,
            "count": base_count + len(results),
            "judge_decision": "",
        }

        logger.info(
            f"[Parallel Risk Debate] 合併完成，{len(results)} 位分析師結果已整合"
        )
        return {"risk_debate_state": merged_state}

    return parallel_risk_debate_node
