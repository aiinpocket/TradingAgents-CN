from langchain_core.messages import HumanMessage
from typing import Annotated
from langchain_core.tools import tool
from datetime import datetime
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import tradingagents.dataflows.interface as interface
from tradingagents.dataflows.finnhub_extra import (
    get_finnhub_sentiment_report,
    get_finnhub_analyst_report,
    get_finnhub_technical_report,
)
from tradingagents.default_config import DEFAULT_CONFIG

# 匯入工具日誌裝飾器
from tradingagents.utils.tool_logging import log_tool_call

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

# 全域工具執行緒池（共享給所有分析師的工具呼叫，避免每次建立新池的開銷）
# CPU 核心數 * 2 上限為 12，因為工具呼叫主要是 I/O 密集（API / DB）
_TOOL_EXECUTOR_WORKERS = max(4, min(12, (os.cpu_count() or 4) * 2))
_GLOBAL_TOOL_EXECUTOR = ThreadPoolExecutor(
    max_workers=_TOOL_EXECUTOR_WORKERS,
    thread_name_prefix="tool",
)

# 分析層級工具結果快取（跨分析師共享，每次分析重置）
# 當多個分析師並行呼叫相同工具+參數時（如 get_finnhub_sentiment_data），
# 第二個呼叫直接返回快取結果，避免重複 API 呼叫
_tool_result_cache: dict[str, str] = {}
_tool_cache_lock = threading.Lock()
_tool_cache_hits = 0
_tool_cache_misses = 0


# 分析層級記憶嵌入快取（避免多節點重複呼叫嵌入 API）
# 同一次分析中 5 個節點使用相同的 current_situation，只需計算一次嵌入
_embedding_cache: dict[int, list[float]] = {}
_embedding_cache_lock = threading.Lock()


def truncate_report(text: str, max_chars: int = 800) -> str:
    """截斷報告文字，用於下游節點的參考上下文。

    風險辯論者等節點不需要完整的分析報告，只需關鍵結論。
    截斷可大幅減少 LLM 輸入 token，加速推理。

    Args:
        text: 原始報告文字
        max_chars: 保留的最大字元數

    Returns:
        str: 截斷後的文字（超過上限時加 '...(略)' 後綴）
    """
    if not text or len(text) <= max_chars:
        return text or ""
    return text[:max_chars] + "...(略)"


def calc_start_date(trade_date: str, days_back: int = 90) -> str:
    """根據交易日期動態計算資料起始日期（共用函式，供所有分析師和 prefetch 使用）"""
    from datetime import timedelta
    try:
        dt = datetime.strptime(trade_date, "%Y-%m-%d")
        return (dt - timedelta(days=days_back)).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")


def get_situation_for_memory(state: dict, max_chars: int = 1500) -> str:
    """產生標準化的 current_situation 字串供記憶嵌入使用。

    所有節點使用相同格式和截斷長度，確保嵌入快取最大命中率。
    第一個節點計算嵌入後，後續節點全部命中快取，
    將 3-4 次嵌入 API 呼叫減少為 1 次。

    Args:
        state: LangGraph 狀態字典
        max_chars: 每份報告保留的最大字元數

    Returns:
        str: 標準化的情境描述文字
    """
    return (
        truncate_report(state.get("market_report", ""), max_chars)
        + "\n\n"
        + truncate_report(state.get("sentiment_report", ""), max_chars)
        + "\n\n"
        + truncate_report(state.get("news_report", ""), max_chars)
        + "\n\n"
        + truncate_report(state.get("fundamentals_report", ""), max_chars)
    )


def get_cached_embedding(situation_text: str, memory_instance) -> list[float]:
    """取得 current_situation 的嵌入向量（快取避免重複 API 呼叫）"""
    cache_key = hash(situation_text)
    with _embedding_cache_lock:
        cached = _embedding_cache.get(cache_key)
        if cached is not None:
            logger.debug("記憶嵌入快取命中，跳過 API 呼叫")
            return cached

    # 快取未命中，計算嵌入
    embedding = memory_instance.get_embedding(situation_text)
    with _embedding_cache_lock:
        _embedding_cache[cache_key] = embedding
    logger.info("記憶嵌入已計算並快取")
    return embedding


def reset_tool_result_cache():
    """重置工具結果快取，在每次新分析開始前呼叫"""
    global _tool_result_cache, _tool_cache_hits, _tool_cache_misses
    with _tool_cache_lock:
        if _tool_result_cache:
            logger.info(
                f"工具結果快取重置: {len(_tool_result_cache)} 筆, "
                f"命中 {_tool_cache_hits} 次, 未命中 {_tool_cache_misses} 次"
            )
        _tool_result_cache = {}
        _tool_cache_hits = 0
        _tool_cache_misses = 0
    # 同時重置嵌入快取
    with _embedding_cache_lock:
        if _embedding_cache:
            logger.info(f"記憶嵌入快取重置: {len(_embedding_cache)} 筆")
        _embedding_cache.clear()


def _make_cache_key(tool_name: str, args: dict) -> str:
    """產生工具結果快取鍵（工具名稱 + 參數雜湊）"""
    try:
        args_str = json.dumps(args, sort_keys=True, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        args_str = str(args)
    return f"{tool_name}::{args_str}"


def invoke_tools_direct(tools, tool_args_list, logger_instance=None):
    """跳過 LLM 工具決策，直接以程式碼並行呼叫所有指定工具。

    內建分析層級快取：同一次分析中，相同工具+參數的呼叫只執行一次，
    後續呼叫直接返回快取結果（例如多個分析師都呼叫 get_finnhub_sentiment_data）。

    Args:
        tools: 要呼叫的工具物件列表
        tool_args_list: 每個工具對應的參數字典列表（與 tools 同序）
        logger_instance: 日誌實例（可選）

    Returns:
        list[str]: 每個工具的回傳結果（字串列表，與 tools 同序）
    """
    global _tool_cache_hits, _tool_cache_misses
    _log = logger_instance or logger

    def _invoke_one(tool, args):
        """執行單一工具呼叫，帶分析層級快取。
        支援 LangChain 工具（有 .invoke 方法）和普通可呼叫物件（如函式）。
        """
        name = getattr(tool, 'name', getattr(tool, '__name__', str(tool)))
        cache_key = _make_cache_key(name, args)

        # 檢查快取（讀取不需要鎖，dict 讀取是原子操作）
        cached = _tool_result_cache.get(cache_key)
        if cached is not None:
            with _tool_cache_lock:
                _tool_cache_hits += 1
            _log.info(f"工具快取命中: {name} (結果長度: {len(cached)})")
            return cached

        try:
            # 支援 LangChain 工具和普通可呼叫物件
            if hasattr(tool, 'invoke'):
                result = tool.invoke(args)
            elif callable(tool):
                result = tool(**args)
            else:
                raise TypeError(f"工具 {name} 既無 invoke 方法也不可呼叫")
            result_str = str(result)
            _log.debug(f"直接工具呼叫 {name} 成功，結果長度: {len(result_str)}")

            # 寫入快取（加鎖保護）
            with _tool_cache_lock:
                _tool_result_cache[cache_key] = result_str
                _tool_cache_misses += 1

            return result_str
        except Exception as e:
            _log.error(f"直接工具呼叫 {name} 失敗: {e}")
            return f"工具 {name} 執行失敗: {str(e)}"

    if len(tools) <= 1:
        return [_invoke_one(t, a) for t, a in zip(tools, tool_args_list)]

    _log.info(f"直接並行呼叫 {len(tools)} 個工具（全域池 {_TOOL_EXECUTOR_WORKERS} workers）")
    results = [None] * len(tools)
    # 使用全域共享執行緒池，避免每次呼叫建立/銷毀池的開銷
    future_to_idx = {
        _GLOBAL_TOOL_EXECUTOR.submit(_invoke_one, t, a): i
        for i, (t, a) in enumerate(zip(tools, tool_args_list))
    }
    # 30 秒超時保護：避免單一工具卡住阻塞整個流程
    try:
        for future in as_completed(future_to_idx, timeout=30):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result(timeout=5)
            except Exception as e:
                name = getattr(tools[idx], 'name', '?')
                _log.error(f"工具 {name} 執行失敗: {e}")
                results[idx] = f"工具 {name} 執行失敗: {str(e)}"
    except TimeoutError:
        _log.warning("部分工具呼叫超過 30 秒超時，跳過未完成的工具")

    # 快取命中率摘要（幫助監控 prefetch 效能）
    with _tool_cache_lock:
        total = _tool_cache_hits + _tool_cache_misses
        if total > 0:
            hit_rate = _tool_cache_hits / total * 100
            _log.info(
                f"工具快取統計: 命中 {_tool_cache_hits}/{total} "
                f"({hit_rate:.0f}%), 快取條目 {len(_tool_result_cache)}"
            )

    return results


def prefetch_analyst_data(toolkit, ticker: str, trade_date: str):
    """在圖執行前預載入所有分析師需要的資料到快取中。

    將 7 個獨立 API 呼叫合併為一批並行請求，
    避免 4 個分析師各自建立執行緒池競爭資源。
    分析師開始時所有資料已在快取中，零等待直接進入 LLM 推理。

    Args:
        toolkit: Toolkit 實例，包含所有工具
        ticker: 股票代碼（如 AAPL）
        trade_date: 分析日期（YYYY-MM-DD）
    """
    start_date = calc_start_date(trade_date)

    # 建立統一新聞工具（與新聞分析師使用相同的工具和參數）
    from tradingagents.tools.unified_news_tool import create_unified_news_tool
    unified_news_tool = create_unified_news_tool(toolkit)
    unified_news_tool.name = "get_stock_news_unified"

    # 收集 4 個分析師需要的所有 7 個不重複工具呼叫
    # 全部使用純 API 呼叫（無 OpenAI web_search LLM），大幅縮短預載入時間
    tools = [
        # 市場分析師需要的 2 個工具
        toolkit.get_stock_market_data_unified,
        toolkit.get_finnhub_technical_signals,
        # 社交媒體分析師需要的 2 個工具（Google News + Finnhub 情緒）
        toolkit.get_google_news,
        toolkit.get_finnhub_sentiment_data,  # 新聞分析師也需要，會快取命中
        # 新聞分析師的統一新聞工具
        unified_news_tool,
        # 基本面分析師需要的 2 個工具
        toolkit.get_stock_fundamentals_unified,
        toolkit.get_finnhub_analyst_consensus,
    ]

    tool_args = [
        {"ticker": ticker, "start_date": start_date, "end_date": trade_date},
        {"ticker": ticker},
        {"query": f"{ticker} stock social media sentiment", "curr_date": trade_date},
        {"ticker": ticker, "curr_date": trade_date},
        {"stock_code": ticker, "max_news": 10, "model_info": ""},
        {"ticker": ticker, "start_date": start_date, "end_date": trade_date, "curr_date": trade_date},
        {"ticker": ticker, "curr_date": trade_date},
    ]

    logger.info(f"[資料預載入] 開始並行載入 {len(tools)} 個工具結果到快取")
    import time
    t0 = time.time()

    results = invoke_tools_direct(tools, tool_args, logger)

    # 檢查哪些工具失敗了，嘗試重試一次（指數退避 1 秒）
    failed_indices = [
        i for i, r in enumerate(results)
        if not r or "失敗" in str(r) or "執行失敗" in str(r)
    ]
    if failed_indices:
        failed_names = [getattr(tools[i], 'name', '?') for i in failed_indices]
        logger.warning(f"[資料預載入] {len(failed_indices)} 個工具失敗，1 秒後重試: {failed_names}")
        time.sleep(1)
        retry_tools = [tools[i] for i in failed_indices]
        retry_args = [tool_args[i] for i in failed_indices]
        retry_results = invoke_tools_direct(retry_tools, retry_args, logger)
        for idx, retry_result in zip(failed_indices, retry_results):
            if retry_result and "失敗" not in str(retry_result) and "執行失敗" not in str(retry_result):
                results[idx] = retry_result

    elapsed = time.time() - t0
    ok_count = sum(1 for r in results if r and "失敗" not in str(r) and "執行失敗" not in str(r))
    logger.info(f"[資料預載入] 完成，{ok_count}/{len(results)} 個成功，耗時: {elapsed:.1f}秒")


def create_msg_delete():
    """建立訊息清理節點，用於分析師完成後標記分支結束。

    不刪除任何訊息，僅回傳佔位訊息讓 LangGraph fan-in 能正常合併。
    下游節點（Bull/Bear Researcher、Research Manager、Trader、Risk 節點）
    都使用專用狀態欄位（market_report、sentiment_report 等），
    不依賴 state["messages"]，因此不需要清理對話歷史。
    使用 RemoveMessage 會在並行分支 fan-in 合併時產生 ID 不存在的衝突。
    """
    def delete_messages(state):
        """回傳佔位訊息，不執行任何刪除操作"""
        return {"messages": [HumanMessage(content="Continue")]}

    return delete_messages


class Toolkit:
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """Update the class-level configuration."""
        cls._config.update(config)

    @property
    def config(self):
        """Access the configuration."""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    def get_finnhub_news(
        ticker: Annotated[
            str,
            "Search query of a company, e.g. 'AAPL, TSM, etc.",
        ],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock from Finnhub within a date range
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing news about the company within the date range from start_date to end_date
        """

        end_date_str = end_date

        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        look_back_days = (end_date - start_date).days

        finnhub_news_result = interface.get_finnhub_news(
            ticker, end_date_str, look_back_days
        )

        return finnhub_news_result

    @staticmethod
    @tool
    def get_YFin_data(
        symbol: Annotated[str, "ticker symbol of the company"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve the stock price data for a given ticker symbol from Yahoo Finance.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
        """

        result_data = interface.get_YFin_data(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_YFin_data_online(
        symbol: Annotated[str, "ticker symbol of the company"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve the stock price data for a given ticker symbol from Yahoo Finance.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
        """

        result_data = interface.get_YFin_data_online(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_stockstats_indicators_report(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted dataframe containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, False
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted dataframe containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, True
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "ticker symbol for the company"],
        curr_date: Annotated[
            str,
            "current date of you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider sentiment information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the sentiment in the past 30 days starting at curr_date
        """

        data_sentiment = interface.get_finnhub_company_insider_sentiment(
            ticker, curr_date, 30
        )

        return data_sentiment

    @staticmethod
    @tool
    def get_finnhub_company_insider_transactions(
        ticker: Annotated[str, "ticker symbol"],
        curr_date: Annotated[
            str,
            "current date you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider transaction information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the company's insider transactions/trading information in the past 30 days
        """

        data_trans = interface.get_finnhub_company_insider_transactions(
            ticker, curr_date, 30
        )

        return data_trans

    @staticmethod
    @tool
    def get_simfin_balance_sheet(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent balance sheet of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the company's most recent balance sheet
        """

        data_balance_sheet = interface.get_simfin_balance_sheet(ticker, freq, curr_date)

        return data_balance_sheet

    @staticmethod
    @tool
    def get_simfin_cashflow(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent cash flow statement of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
                str: a report of the company's most recent cash flow statement
        """

        data_cashflow = interface.get_simfin_cashflow(ticker, freq, curr_date)

        return data_cashflow

    @staticmethod
    @tool
    def get_simfin_income_stmt(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent income statement of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
                str: a report of the company's most recent income statement
        """

        data_income_stmt = interface.get_simfin_income_statements(
            ticker, freq, curr_date
        )

        return data_income_stmt

    @staticmethod
    @tool
    def get_google_news(
        query: Annotated[str, "Query to search with"],
        curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news from Google News based on a query and date range.
        Args:
            query (str): Query to search with
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): How many days to look back
        Returns:
            str: A formatted string containing the latest news from Google News based on the query and date range.
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results

    @staticmethod
    @tool
    def get_realtime_stock_news(
        ticker: Annotated[str, "Ticker of a company. e.g. AAPL, TSM"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        """
        取得股票的實時新聞分析，解決傳統新聞源的滯後性問題。
        整合多個專業財經API，提供15-30分鐘內的最新新聞。
        支援多種新聞源輪詢機制，優先使用實時新聞聚合器，失敗時自動嘗試備用新聞源。
        支援美股新聞的英文和中文雙語搜索。
        
        Args:
            ticker (str): 股票代碼，如 AAPL, TSM, MSFT
            curr_date (str): 當前日期，格式為 yyyy-mm-dd
        Returns:
            str: 包含實時新聞分析、緊急程度評估、時效性說明的格式化報告
        """
        from tradingagents.dataflows.realtime_news_utils import get_realtime_stock_news
        return get_realtime_stock_news(ticker, curr_date, hours_back=6)

    @staticmethod
    @tool
    def get_stock_news_openai(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest news about the company on the given date.
        """

        openai_news_results = interface.get_stock_news_openai(ticker, curr_date)

        return openai_news_results

    @staticmethod
    @tool
    def get_global_news_openai(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest macroeconomics news on a given date using OpenAI's macroeconomics news API.
        Args:
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest macroeconomic news on the given date.
        """

        openai_news_results = interface.get_global_news_openai(curr_date)

        return openai_news_results

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_fundamentals_unified", log_args=True)
    def get_stock_fundamentals_unified(
        ticker: Annotated[str, "股票代碼（美股）"],
        start_date: Annotated[str, "開始日期，格式：YYYY-MM-DD"] = None,
        end_date: Annotated[str, "結束日期，格式：YYYY-MM-DD"] = None,
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"] = None
    ) -> str:
        """
        統一的股票基本面分析工具，使用 Finnhub API 資料來源

        Args:
            ticker: 股票代碼（如：AAPL、TSLA）
            start_date: 開始日期（可選，格式：YYYY-MM-DD）
            end_date: 結束日期（可選，格式：YYYY-MM-DD）
            curr_date: 當前日期（可選，格式：YYYY-MM-DD）

        Returns:
            str: 基本面分析資料和報告
        """
        logger.info(f"[統一基本面工具] 分析股票: {ticker}")

        try:
            from datetime import datetime, timedelta

            # 設定預設日期
            if not curr_date:
                curr_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = curr_date

            result_data = []

            # 直接使用 Finnhub API 取得基本面資料（無 LLM 呼叫，速度快 5-10 倍）
            logger.info(f"[統一基本面工具] 處理美股資料: {ticker}")

            try:
                from tradingagents.dataflows.interface import get_fundamentals_finnhub
                us_data = get_fundamentals_finnhub(ticker, curr_date)
                result_data.append(f"## 基本面資料\n{us_data}")
            except Exception as e:
                result_data.append(f"## 基本面資料\n取得失敗: {e}")

            # 組合所有資料
            combined_result = f"""# {ticker} 基本面分析資料

**分析日期**: {curr_date}

{chr(10).join(result_data)}

---
*資料來源: Finnhub API*
"""

            logger.info(f"[統一基本面工具] 資料取得完成，總長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一基本面分析工具執行失敗: {str(e)}"
            logger.error(f"[統一基本面工具] {error_msg}")
            return error_msg

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_market_data_unified", log_args=True)
    def get_stock_market_data_unified(
        ticker: Annotated[str, "股票代碼（美股）"],
        start_date: Annotated[str, "開始日期，格式：YYYY-MM-DD"],
        end_date: Annotated[str, "結束日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        統一的股票市場資料工具，取得價格和技術指標資料

        Args:
            ticker: 股票代碼（如：AAPL、TSLA）
            start_date: 開始日期（格式：YYYY-MM-DD）
            end_date: 結束日期（格式：YYYY-MM-DD）

        Returns:
            str: 市場資料和技術分析報告
        """
        logger.info(f"[統一市場工具] 分析股票: {ticker}")

        try:
            result_data = []

            # 使用優化的美股資料取得工具
            logger.info(f"[統一市場工具] 處理美股市場資料: {ticker}")

            try:
                from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
                us_data = get_us_stock_data_cached(ticker, start_date, end_date)
                result_data.append(f"## 市場資料\n{us_data}")
            except Exception as e:
                result_data.append(f"## 市場資料\n取得失敗: {e}")

            # 組合資料
            combined_result = f"""# {ticker} 市場資料分析

**分析期間**: {start_date} 至 {end_date}

{chr(10).join(result_data)}

---
*資料來源: Yahoo Finance / Finnhub API*
"""

            logger.info(f"[統一市場工具] 資料取得完成，總長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一市場資料工具執行失敗: {str(e)}"
            logger.error(f"[統一市場工具] {error_msg}")
            return error_msg

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_news_unified", log_args=True)
    def get_stock_news_unified(
        ticker: Annotated[str, "股票代碼（美股）"],
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        統一的股票新聞工具，使用 Finnhub 新聞資料來源

        Args:
            ticker: 股票代碼（如：AAPL、TSLA）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 新聞分析報告
        """
        logger.info(f"[統一新聞工具] 分析股票: {ticker}")

        try:
            from datetime import datetime, timedelta

            # 計算新聞查詢的日期範圍
            end_date = datetime.strptime(curr_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=7)
            start_date_str = start_date.strftime('%Y-%m-%d')

            result_data = []

            # 使用 Finnhub 新聞
            logger.info(f"[統一新聞工具] 處理美股新聞: {ticker}")

            try:
                from tradingagents.dataflows.interface import get_finnhub_news
                news_data = get_finnhub_news(ticker, start_date_str, curr_date)
                result_data.append(f"## 新聞資料\n{news_data}")
            except Exception as e:
                result_data.append(f"## 新聞資料\n取得失敗: {e}")

            # 組合所有資料
            combined_result = f"""# {ticker} 新聞分析

**分析日期**: {curr_date}
**新聞時間範圍**: {start_date_str} 至 {curr_date}

{chr(10).join(result_data)}

---
*資料來源: Finnhub API*
"""

            logger.info(f"[統一新聞工具] 資料取得完成，總長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一新聞工具執行失敗: {str(e)}"
            logger.error(f"[統一新聞工具] {error_msg}")
            return error_msg

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_sentiment_unified", log_args=True)
    def get_stock_sentiment_unified(
        ticker: Annotated[str, "股票代碼（美股）"],
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        統一的股票情緒分析工具，使用 FinnHub 社交媒體情緒資料

        Args:
            ticker: 股票代碼（如：AAPL、TSLA）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 情緒分析報告
        """
        logger.info(f"[統一情緒工具] 分析股票: {ticker}")

        try:
            # 使用 FinnHub 情緒資料
            logger.info(f"[統一情緒工具] 透過 FinnHub 取得情緒資料: {ticker}")

            try:
                from tradingagents.dataflows.finnhub_extra import get_finnhub_sentiment_report
                sentiment_data = get_finnhub_sentiment_report(ticker, curr_date)
            except Exception as e:
                sentiment_data = f"FinnHub 情緒資料取得失敗: {e}"

            combined_result = f"""# {ticker} 情緒分析

**分析日期**: {curr_date}

{sentiment_data}

---
*資料來源: FinnHub*
"""

            logger.info(f"[統一情緒工具] 資料取得完成，總長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一情緒分析工具執行失敗: {str(e)}"
            logger.error(f"[統一情緒工具] {error_msg}")
            return error_msg

    @staticmethod
    @tool
    def get_finnhub_sentiment_data(
        ticker: Annotated[str, "股票代碼（美股），如 AAPL、TSLA"],
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        取得 FinnHub 情緒量化資料，包含新聞情緒評分和社交媒體情緒分析。
        整合 News Sentiment（看多/看空比例、行業比較）和
        Social Sentiment（社交媒體提及次數、正負面比例）。

        Args:
            ticker: 股票代碼（如 AAPL、TSLA）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 情緒量化資料報告
        """
        logger.info(f"[FinnHub情緒工具] 取得 {ticker} 的情緒資料")
        return get_finnhub_sentiment_report(ticker, curr_date)

    @staticmethod
    @tool
    def get_finnhub_analyst_consensus(
        ticker: Annotated[str, "股票代碼（美股），如 AAPL、TSLA"],
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        取得華爾街分析師共識資料，包含評級分布、目標價、評級變動、
        盈利預測（EPS/營收）、下次財報日期和同業公司列表。

        Args:
            ticker: 股票代碼（如 AAPL、TSLA）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 分析師共識資料報告
        """
        logger.info(f"[FinnHub分析師工具] 取得 {ticker} 的分析師共識資料")
        return get_finnhub_analyst_report(ticker, curr_date)

    @staticmethod
    @tool
    def get_finnhub_technical_signals(
        ticker: Annotated[str, "股票代碼（美股），如 AAPL、TSLA"],
    ) -> str:
        """
        取得 FinnHub 技術分析綜合訊號，包含買入/賣出/中性訊號統計、
        ADX 趨勢強度和支撐壓力位。

        Args:
            ticker: 股票代碼（如 AAPL、TSLA）

        Returns:
            str: 技術訊號分析報告
        """
        logger.info(f"[FinnHub技術工具] 取得 {ticker} 的技術訊號")
        return get_finnhub_technical_report(ticker)
