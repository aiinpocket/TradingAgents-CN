# 並行多空辯論包裝器
# 當投資辯論僅需一輪時，同時執行看漲和看跌研究員以加速分析

from concurrent.futures import ThreadPoolExecutor, as_completed

from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def create_parallel_invest_debate(bull_fn, bear_fn):
    """建立並行多空辯論節點，同時執行看漲和看跌研究員。

    適用於 max_debate_rounds == 1 的情境：
    第一輪中兩位研究員尚未看到彼此的回應，因此可安全並行執行。
    串行執行約需 4-10 秒（每位研究員 ~2-5 秒），並行後僅需一次 LLM 延遲。
    """

    def parallel_invest_debate_node(state) -> dict:
        logger.info("[Parallel Invest Debate] 啟動看漲/看跌研究員並行執行")

        results = {}
        errors = {}

        # 使用執行緒池同時呼叫兩位研究員的 LLM
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="invest_debate") as executor:
            futures = {
                executor.submit(bull_fn, state): "bull",
                executor.submit(bear_fn, state): "bear",
            }

            for future in as_completed(futures):
                researcher_name = futures[future]
                try:
                    results[researcher_name] = future.result()
                    logger.info(f"[Parallel Invest Debate] {researcher_name} 研究員完成")
                except Exception as e:
                    logger.error(f"[Parallel Invest Debate] {researcher_name} 研究員發生錯誤: {e}")
                    errors[researcher_name] = str(e)

        if errors:
            logger.warning(f"[Parallel Invest Debate] 部分研究員失敗: {list(errors.keys())}")

        # 合併兩位研究員的結果
        debate_state = state["investment_debate_state"]
        base_history = debate_state.get("history", "")
        base_count = debate_state.get("count", 0)

        # 從各研究員結果中提取回應
        bull_state = results.get("bull", {}).get("investment_debate_state", {})
        bear_state = results.get("bear", {}).get("investment_debate_state", {})

        bull_response = bull_state.get("current_response", "")
        bear_response = bear_state.get("current_response", "")

        # 合併對話歷史：將兩位研究員的回應按序加入
        combined_history = base_history
        if bull_response:
            combined_history += "\n" + bull_response
        if bear_response:
            combined_history += "\n" + bear_response

        merged_state = {
            "history": combined_history,
            "bull_history": bull_state.get(
                "bull_history", debate_state.get("bull_history", "")
            ),
            "bear_history": bear_state.get(
                "bear_history", debate_state.get("bear_history", "")
            ),
            "current_response": bear_response or bull_response,
            "count": base_count + len(results),
            "judge_decision": "",
        }

        logger.info(
            f"[Parallel Invest Debate] 合併完成，{len(results)} 位研究員結果已整合"
        )
        return {"investment_debate_state": merged_state}

    return parallel_invest_debate_node
