from langchain_core.messages import HumanMessage, RemoveMessage
from typing import Annotated
from langchain_core.tools import tool
from datetime import datetime
import tradingagents.dataflows.interface as interface
from tradingagents.dataflows.finnhub_extra import (
    get_finnhub_sentiment_report,
    get_finnhub_analyst_report,
    get_finnhub_technical_report,
)
from tradingagents.default_config import DEFAULT_CONFIG

# 導入工具日誌裝飾器
from tradingagents.utils.tool_logging import log_tool_call

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        
        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")
        
        return {"messages": removal_operations + [placeholder]}
    
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
        獲取股票的實時新聞分析，解決傳統新聞源的滯後性問題。
        整合多個專業財經API，提供15-30分鐘內的最新新聞。
        支持多種新聞源輪詢機制，優先使用實時新聞聚合器，失敗時自動嘗試備用新聞源。
        支持美股新聞的英文和中文雙語搜索。
        
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
        統一的股票基本面分析工具，使用 OpenAI/Finnhub 數據源

        Args:
            ticker: 股票代碼（如：AAPL、TSLA）
            start_date: 開始日期（可選，格式：YYYY-MM-DD）
            end_date: 結束日期（可選，格式：YYYY-MM-DD）
            curr_date: 當前日期（可選，格式：YYYY-MM-DD）

        Returns:
            str: 基本面分析數據和報告
        """
        logger.info(f"[統一基本面工具] 分析股票: {ticker}")

        try:
            from datetime import datetime, timedelta

            # 設置預設日期
            if not curr_date:
                curr_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = curr_date

            result_data = []

            # 使用 OpenAI/Finnhub 數據源獲取基本面資料
            logger.info(f"[統一基本面工具] 處理美股數據: {ticker}")

            try:
                from tradingagents.dataflows.interface import get_fundamentals_openai
                us_data = get_fundamentals_openai(ticker, curr_date)
                result_data.append(f"## 基本面數據\n{us_data}")
            except Exception as e:
                result_data.append(f"## 基本面數據\n獲取失敗: {e}")

            # 組合所有資料
            combined_result = f"""# {ticker} 基本面分析數據

**分析日期**: {curr_date}

{chr(10).join(result_data)}

---
*數據來源: OpenAI / Finnhub API*
"""

            logger.info(f"[統一基本面工具] 數據獲取完成，總長度: {len(combined_result)}")
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
        統一的股票市場數據工具，獲取價格和技術指標數據

        Args:
            ticker: 股票代碼（如：AAPL、TSLA）
            start_date: 開始日期（格式：YYYY-MM-DD）
            end_date: 結束日期（格式：YYYY-MM-DD）

        Returns:
            str: 市場數據和技術分析報告
        """
        logger.info(f"[統一市場工具] 分析股票: {ticker}")

        try:
            result_data = []

            # 使用優化的美股數據獲取工具
            logger.info(f"[統一市場工具] 處理美股市場數據: {ticker}")

            try:
                from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
                us_data = get_us_stock_data_cached(ticker, start_date, end_date)
                result_data.append(f"## 市場數據\n{us_data}")
            except Exception as e:
                result_data.append(f"## 市場數據\n獲取失敗: {e}")

            # 組合資料
            combined_result = f"""# {ticker} 市場數據分析

**分析期間**: {start_date} 至 {end_date}

{chr(10).join(result_data)}

---
*數據來源: Yahoo Finance / Finnhub API*
"""

            logger.info(f"[統一市場工具] 數據獲取完成，總長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一市場數據工具執行失敗: {str(e)}"
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
        統一的股票新聞工具，使用 Finnhub 新聞數據源

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
                result_data.append(f"## 新聞資料\n獲取失敗: {e}")

            # 組合所有資料
            combined_result = f"""# {ticker} 新聞分析

**分析日期**: {curr_date}
**新聞時間範圍**: {start_date_str} 至 {curr_date}

{chr(10).join(result_data)}

---
*數據來源: Finnhub API*
"""

            logger.info(f"[統一新聞工具] 數據獲取完成，總長度: {len(combined_result)}")
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
        統一的股票情緒分析工具，使用 FinnHub 社交媒體情緒數據

        Args:
            ticker: 股票代碼（如：AAPL、TSLA）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 情緒分析報告
        """
        logger.info(f"[統一情緒工具] 分析股票: {ticker}")

        try:
            # 使用 FinnHub 情緒數據
            logger.info(f"[統一情緒工具] 透過 FinnHub 獲取情緒數據: {ticker}")

            try:
                from tradingagents.dataflows.finnhub_extra import get_finnhub_sentiment_report
                sentiment_data = get_finnhub_sentiment_report(ticker, curr_date)
            except Exception as e:
                sentiment_data = f"FinnHub 情緒數據獲取失敗: {e}"

            combined_result = f"""# {ticker} 情緒分析

**分析日期**: {curr_date}

{sentiment_data}

---
*數據來源: FinnHub*
"""

            logger.info(f"[統一情緒工具] 數據獲取完成，總長度: {len(combined_result)}")
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
        取得 FinnHub 情緒量化數據，包含新聞情緒評分和社交媒體情緒分析。
        整合 News Sentiment（看多/看空比例、行業比較）和
        Social Sentiment（社交媒體提及次數、正負面比例）。

        Args:
            ticker: 股票代碼（如 AAPL、TSLA）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 情緒量化數據報告
        """
        logger.info(f"[FinnHub情緒工具] 取得 {ticker} 的情緒數據")
        return get_finnhub_sentiment_report(ticker, curr_date)

    @staticmethod
    @tool
    def get_finnhub_analyst_consensus(
        ticker: Annotated[str, "股票代碼（美股），如 AAPL、TSLA"],
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        取得華爾街分析師共識數據，包含評級分布、目標價、評級變動、
        盈利預測（EPS/營收）、下次財報日期和同業公司列表。

        Args:
            ticker: 股票代碼（如 AAPL、TSLA）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 分析師共識數據報告
        """
        logger.info(f"[FinnHub分析師工具] 取得 {ticker} 的分析師共識數據")
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
