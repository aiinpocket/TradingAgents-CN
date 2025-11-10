from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI
import tradingagents.dataflows.interface as interface
from tradingagents.default_config import DEFAULT_CONFIG
from langchain_core.messages import HumanMessage

# 導入統一日誌系統和工具日誌裝饰器
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_tool_call, log_analysis_step

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
    def get_reddit_news(
        curr_date: Annotated[str, "Date you want to get news for in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve global news from Reddit within a specified time frame.
        Args:
            curr_date (str): Date you want to get news for in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the latest global news from Reddit in the specified time frame.
        """
        
        global_news_result = interface.get_reddit_global_news(curr_date, 7, 5)

        return global_news_result

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
    def get_reddit_stock_info(
        ticker: Annotated[
            str,
            "Ticker of a company. e.g. AAPL, TSM",
        ],
        curr_date: Annotated[str, "Current date you want to get news for"],
    ) -> str:
        """
        Retrieve the latest news about a given stock from Reddit, given the current date.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): current date in yyyy-mm-dd format to get news for
        Returns:
            str: A formatted dataframe containing the latest news about the company on the given date
        """

        stock_news_results = interface.get_reddit_company_news(ticker, curr_date, 7, 5)

        return stock_news_results

    @staticmethod
    @tool
    def get_chinese_social_sentiment(
        ticker: Annotated[str, "Ticker of a company. e.g. AAPL, TSM"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        """
        獲取中國社交媒體和財經平台上關於特定股票的情绪分析和討論熱度。
        整合雪球、东方財富股吧、新浪財經等中國本土平台的數據。
        Args:
            ticker (str): 股票代碼，如 AAPL, TSM
            curr_date (str): 當前日期，格式為 yyyy-mm-dd
        Returns:
            str: 包含中國投資者情绪分析、討論熱度、關键觀點的格式化報告
        """
        try:
            # 這里可以集成多個中國平台的數據
            chinese_sentiment_results = interface.get_chinese_social_sentiment(ticker, curr_date)
            return chinese_sentiment_results
        except Exception as e:
            # 如果中國平台數據獲取失败，回退到原有的Reddit數據
            return interface.get_reddit_company_news(ticker, curr_date, 7, 5)

    @staticmethod
    # @tool  # 已移除：請使用 get_stock_fundamentals_unified 或 get_stock_market_data_unified
    def get_china_stock_data(
        stock_code: Annotated[str, "中國股票代碼，如 000001(平安銀行), 600519(贵州茅台)"],
        start_date: Annotated[str, "開始日期，格式 yyyy-mm-dd"],
        end_date: Annotated[str, "結束日期，格式 yyyy-mm-dd"],
    ) -> str:
        """
        獲取中國A股實時和歷史數據，通過Tushare等高質量數據源提供專業的股票數據。
        支持實時行情、歷史K線、技術指標等全面數據，自動使用最佳數據源。
        Args:
            stock_code (str): 中國股票代碼，如 000001(平安銀行), 600519(贵州茅台)
            start_date (str): 開始日期，格式 yyyy-mm-dd
            end_date (str): 結束日期，格式 yyyy-mm-dd
        Returns:
            str: 包含實時行情、歷史數據、技術指標的完整股票分析報告
        """
        try:
            logger.debug(f"📊 [DEBUG] ===== agent_utils.get_china_stock_data 開始調用 =====")
            logger.debug(f"📊 [DEBUG] 參數: stock_code={stock_code}, start_date={start_date}, end_date={end_date}")

            from tradingagents.dataflows.interface import get_china_stock_data_unified
            logger.debug(f"📊 [DEBUG] 成功導入統一數據源接口")

            logger.debug(f"📊 [DEBUG] 正在調用統一數據源接口...")
            result = get_china_stock_data_unified(stock_code, start_date, end_date)

            logger.debug(f"📊 [DEBUG] 統一數據源接口調用完成")
            logger.debug(f"📊 [DEBUG] 返回結果類型: {type(result)}")
            logger.debug(f"📊 [DEBUG] 返回結果長度: {len(result) if result else 0}")
            logger.debug(f"📊 [DEBUG] 返回結果前200字符: {str(result)[:200]}...")
            logger.debug(f"📊 [DEBUG] ===== agent_utils.get_china_stock_data 調用結束 =====")

            return result
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"❌ [DEBUG] ===== agent_utils.get_china_stock_data 異常 =====")
            logger.error(f"❌ [DEBUG] 錯誤類型: {type(e).__name__}")
            logger.error(f"❌ [DEBUG] 錯誤信息: {str(e)}")
            logger.error(f"❌ [DEBUG] 詳細堆棧:")
            print(error_details)
            logger.error(f"❌ [DEBUG] ===== 異常處理結束 =====")
            return f"中國股票數據獲取失败: {str(e)}。請檢查數據源配置和網絡連接。"

    @staticmethod
    @tool
    def get_china_market_overview(
        curr_date: Annotated[str, "當前日期，格式 yyyy-mm-dd"],
    ) -> str:
        """
        獲取中國股市整體概覽，包括主要指數的實時行情。
        涵蓋上證指數、深證成指、創業板指、科創50等主要指數。
        Args:
            curr_date (str): 當前日期，格式 yyyy-mm-dd
        Returns:
            str: 包含主要指數實時行情的市場概覽報告
        """
        try:
            # 使用Tushare獲取主要指數數據
            from tradingagents.dataflows.tushare_adapter import get_tushare_adapter

            adapter = get_tushare_adapter()
            if not adapter.provider or not adapter.provider.connected:
                # 如果Tushare不可用，返回基础信息
                logger.warning(f"⚠️ Tushare不可用，返回基础市場概覽")
                return f"""# 中國股市概覽 - {curr_date}

## 📊 主要指數
- 上證指數: 數據獲取中...
- 深證成指: 數據獲取中...
- 創業板指: 數據獲取中...
- 科創50: 數據獲取中...

## 💡 說明
市場概覽功能需要配置Tushare數據源，完整功能即将推出。
當前可以使用股票數據獲取功能分析個股。

數據來源: 統一數據接口
更新時間: {curr_date}
"""

            # 使用Tushare獲取主要指數信息
            # 這里可以擴展為獲取具體的指數數據
            return f"""# 中國股市概覽 - {curr_date}

## 📊 主要指數
- 上證指數: 數據獲取中...
- 深證成指: 數據獲取中...
- 創業板指: 數據獲取中...
- 科創50: 數據獲取中...

## 💡 說明
市場概覽功能正在完善中，完整功能即将推出。
當前可以使用股票數據獲取功能分析個股。

數據來源: Tushare專業數據源
更新時間: {curr_date}
"""

        except Exception as e:
            return f"中國市場概覽獲取失败: {str(e)}。請檢查數據源配置。"

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
        獲取股票的實時新聞分析，解決傳統新聞源的滞後性問題。
        整合多個專業財經API，提供15-30分鐘內的最新新聞。
        支持多種新聞源轮詢機制，優先使用實時新聞聚合器，失败時自動嘗試備用新聞源。
        對於A股和港股，會優先使用中文財經新聞源（如东方財富）。
        
        Args:
            ticker (str): 股票代碼，如 AAPL, TSM, 600036.SH
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
    # @tool  # 已移除：請使用 get_stock_fundamentals_unified
    def get_fundamentals_openai(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest fundamental information about a given stock on a given date by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest fundamental information about the company on the given date.
        """
        logger.debug(f"📊 [DEBUG] get_fundamentals_openai 被調用: ticker={ticker}, date={curr_date}")

        # 檢查是否為中國股票
        import re
        if re.match(r'^\d{6}$', str(ticker)):
            logger.debug(f"📊 [DEBUG] 檢測到中國A股代碼: {ticker}")
            # 使用統一接口獲取中國股票名稱
            try:
                from tradingagents.dataflows.interface import get_china_stock_info_unified
                stock_info = get_china_stock_info_unified(ticker)

                # 解析股票名稱
                if "股票名稱:" in stock_info:
                    company_name = stock_info.split("股票名稱:")[1].split("\n")[0].strip()
                else:
                    company_name = f"股票代碼{ticker}"

                logger.debug(f"📊 [DEBUG] 中國股票名稱映射: {ticker} -> {company_name}")
            except Exception as e:
                logger.error(f"⚠️ [DEBUG] 從統一接口獲取股票名稱失败: {e}")
                company_name = f"股票代碼{ticker}"

            # 修改查詢以包含正確的公司名稱
            modified_query = f"{company_name}({ticker})"
            logger.debug(f"📊 [DEBUG] 修改後的查詢: {modified_query}")
        else:
            logger.debug(f"📊 [DEBUG] 檢測到非中國股票: {ticker}")
            modified_query = ticker

        try:
            openai_fundamentals_results = interface.get_fundamentals_openai(
                modified_query, curr_date
            )
            logger.debug(f"📊 [DEBUG] OpenAI基本面分析結果長度: {len(openai_fundamentals_results) if openai_fundamentals_results else 0}")
            return openai_fundamentals_results
        except Exception as e:
            logger.error(f"❌ [DEBUG] OpenAI基本面分析失败: {str(e)}")
            return f"基本面分析失败: {str(e)}"

    @staticmethod
    # @tool  # 已移除：請使用 get_stock_fundamentals_unified
    def get_china_fundamentals(
        ticker: Annotated[str, "中國A股股票代碼，如600036"],
        curr_date: Annotated[str, "當前日期，格式為yyyy-mm-dd"],
    ):
        """
        獲取中國A股股票的基本面信息，使用中國股票數據源。
        Args:
            ticker (str): 中國A股股票代碼，如600036, 000001
            curr_date (str): 當前日期，格式為yyyy-mm-dd
        Returns:
            str: 包含股票基本面信息的格式化字符串
        """
        logger.debug(f"📊 [DEBUG] get_china_fundamentals 被調用: ticker={ticker}, date={curr_date}")

        # 檢查是否為中國股票
        import re
        if not re.match(r'^\d{6}$', str(ticker)):
            return f"錯誤：{ticker} 不是有效的中國A股代碼格式"

        try:
            # 使用統一數據源接口獲取股票數據（默認Tushare，支持備用數據源）
            from tradingagents.dataflows.interface import get_china_stock_data_unified
            logger.debug(f"📊 [DEBUG] 正在獲取 {ticker} 的股票數據...")

            # 獲取最近30天的數據用於基本面分析
            from datetime import datetime, timedelta
            end_date = datetime.strptime(curr_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=30)

            stock_data = get_china_stock_data_unified(
                ticker,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            logger.debug(f"📊 [DEBUG] 股票數據獲取完成，長度: {len(stock_data) if stock_data else 0}")

            if not stock_data or "獲取失败" in stock_data or "❌" in stock_data:
                return f"無法獲取股票 {ticker} 的基本面數據：{stock_data}"

            # 調用真正的基本面分析
            from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider

            # 創建分析器實例
            analyzer = OptimizedChinaDataProvider()

            # 生成真正的基本面分析報告
            fundamentals_report = analyzer._generate_fundamentals_report(ticker, stock_data)

            logger.debug(f"📊 [DEBUG] 中國基本面分析報告生成完成")
            logger.debug(f"📊 [DEBUG] get_china_fundamentals 結果長度: {len(fundamentals_report)}")

            return fundamentals_report

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"❌ [DEBUG] get_china_fundamentals 失败:")
            logger.error(f"❌ [DEBUG] 錯誤: {str(e)}")
            logger.error(f"❌ [DEBUG] 堆棧: {error_details}")
            return f"中國股票基本面分析失败: {str(e)}"

    @staticmethod
    # @tool  # 已移除：請使用 get_stock_fundamentals_unified 或 get_stock_market_data_unified
    def get_hk_stock_data_unified(
        symbol: Annotated[str, "港股代碼，如：0700.HK、9988.HK等"],
        start_date: Annotated[str, "開始日期，格式：YYYY-MM-DD"],
        end_date: Annotated[str, "結束日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        獲取港股數據的統一接口，優先使用AKShare數據源，備用Yahoo Finance

        Args:
            symbol: 港股代碼 (如: 0700.HK)
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)

        Returns:
            str: 格式化的港股數據
        """
        logger.debug(f"🇭🇰 [DEBUG] get_hk_stock_data_unified 被調用: symbol={symbol}, start_date={start_date}, end_date={end_date}")

        try:
            from tradingagents.dataflows.interface import get_hk_stock_data_unified

            result = get_hk_stock_data_unified(symbol, start_date, end_date)

            logger.debug(f"🇭🇰 [DEBUG] 港股數據獲取完成，長度: {len(result) if result else 0}")

            return result

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"❌ [DEBUG] get_hk_stock_data_unified 失败:")
            logger.error(f"❌ [DEBUG] 錯誤: {str(e)}")
            logger.error(f"❌ [DEBUG] 堆棧: {error_details}")
            return f"港股數據獲取失败: {str(e)}"

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_fundamentals_unified", log_args=True)
    def get_stock_fundamentals_unified(
        ticker: Annotated[str, "股票代碼（支持A股、港股、美股）"],
        start_date: Annotated[str, "開始日期，格式：YYYY-MM-DD"] = None,
        end_date: Annotated[str, "結束日期，格式：YYYY-MM-DD"] = None,
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"] = None
    ) -> str:
        """
        統一的股票基本面分析工具
        自動识別股票類型（A股、港股、美股）並調用相應的數據源

        Args:
            ticker: 股票代碼（如：000001、0700.HK、AAPL）
            start_date: 開始日期（可選，格式：YYYY-MM-DD）
            end_date: 結束日期（可選，格式：YYYY-MM-DD）
            curr_date: 當前日期（可選，格式：YYYY-MM-DD）

        Returns:
            str: 基本面分析數據和報告
        """
        logger.info(f"📊 [統一基本面工具] 分析股票: {ticker}")

        # 添加詳細的股票代碼追蹤日誌
        logger.info(f"🔍 [股票代碼追蹤] 統一基本面工具接收到的原始股票代碼: '{ticker}' (類型: {type(ticker)})")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(ticker))}")
        logger.info(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(ticker))}")

        # 保存原始ticker用於對比
        original_ticker = ticker

        try:
            from tradingagents.utils.stock_utils import StockUtils
            from datetime import datetime, timedelta

            # 自動识別股票類型
            market_info = StockUtils.get_market_info(ticker)
            is_china = market_info['is_china']
            is_hk = market_info['is_hk']
            is_us = market_info['is_us']

            logger.info(f"🔍 [股票代碼追蹤] StockUtils.get_market_info 返回的市場信息: {market_info}")
            logger.info(f"📊 [統一基本面工具] 股票類型: {market_info['market_name']}")
            logger.info(f"📊 [統一基本面工具] 貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")

            # 檢查ticker是否在處理過程中發生了變化
            if str(ticker) != str(original_ticker):
                logger.warning(f"🔍 [股票代碼追蹤] 警告：股票代碼發生了變化！原始: '{original_ticker}' -> 當前: '{ticker}'")

            # 設置默認日期
            if not curr_date:
                curr_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = curr_date

            result_data = []

            if is_china:
                # 中國A股：獲取股票數據 + 基本面數據
                logger.info(f"🇨🇳 [統一基本面工具] 處理A股數據...")
                logger.info(f"🔍 [股票代碼追蹤] 進入A股處理分支，ticker: '{ticker}'")

                try:
                    # 獲取股票價格數據
                    from tradingagents.dataflows.interface import get_china_stock_data_unified
                    logger.info(f"🔍 [股票代碼追蹤] 調用 get_china_stock_data_unified，傳入參數: ticker='{ticker}', start_date='{start_date}', end_date='{end_date}'")
                    stock_data = get_china_stock_data_unified(ticker, start_date, end_date)
                    logger.info(f"🔍 [股票代碼追蹤] get_china_stock_data_unified 返回結果前200字符: {stock_data[:200] if stock_data else 'None'}")
                    result_data.append(f"## A股價格數據\n{stock_data}")
                except Exception as e:
                    logger.error(f"🔍 [股票代碼追蹤] get_china_stock_data_unified 調用失败: {e}")
                    result_data.append(f"## A股價格數據\n獲取失败: {e}")

                try:
                    # 獲取基本面數據
                    from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
                    analyzer = OptimizedChinaDataProvider()
                    logger.info(f"🔍 [股票代碼追蹤] 調用 OptimizedChinaDataProvider._generate_fundamentals_report，傳入參數: ticker='{ticker}'")
                    fundamentals_data = analyzer._generate_fundamentals_report(ticker, stock_data if 'stock_data' in locals() else "")
                    logger.info(f"🔍 [股票代碼追蹤] _generate_fundamentals_report 返回結果前200字符: {fundamentals_data[:200] if fundamentals_data else 'None'}")
                    result_data.append(f"## A股基本面數據\n{fundamentals_data}")
                except Exception as e:
                    logger.error(f"🔍 [股票代碼追蹤] _generate_fundamentals_report 調用失败: {e}")
                    result_data.append(f"## A股基本面數據\n獲取失败: {e}")

            elif is_hk:
                # 港股：使用AKShare數據源，支持多重備用方案
                logger.info(f"🇭🇰 [統一基本面工具] 處理港股數據...")

                hk_data_success = False

                # 主要數據源：AKShare
                try:
                    from tradingagents.dataflows.interface import get_hk_stock_data_unified
                    hk_data = get_hk_stock_data_unified(ticker, start_date, end_date)

                    # 檢查數據質量
                    if hk_data and len(hk_data) > 100 and "❌" not in hk_data:
                        result_data.append(f"## 港股數據\n{hk_data}")
                        hk_data_success = True
                        logger.info(f"✅ [統一基本面工具] 港股主要數據源成功")
                    else:
                        logger.warning(f"⚠️ [統一基本面工具] 港股主要數據源質量不佳")

                except Exception as e:
                    logger.error(f"⚠️ [統一基本面工具] 港股主要數據源失败: {e}")

                # 備用方案：基础港股信息
                if not hk_data_success:
                    try:
                        from tradingagents.dataflows.interface import get_hk_stock_info_unified
                        hk_info = get_hk_stock_info_unified(ticker)

                        basic_info = f"""## 港股基础信息

**股票代碼**: {ticker}
**股票名稱**: {hk_info.get('name', f'港股{ticker}')}
**交易貨币**: 港币 (HK$)
**交易所**: 香港交易所 (HKG)
**數據源**: {hk_info.get('source', '基础信息')}

⚠️ 註意：詳細的價格和財務數據暂時無法獲取，建議稍後重試或使用其他數據源。

**基本面分析建議**：
- 建議查看公司最新財報
- 關註港股市場整體走势
- 考慮汇率因素對投資的影響
"""
                        result_data.append(basic_info)
                        logger.info(f"✅ [統一基本面工具] 港股備用信息成功")

                    except Exception as e2:
                        # 最終備用方案
                        fallback_info = f"""## 港股信息（備用）

**股票代碼**: {ticker}
**股票類型**: 港股
**交易貨币**: 港币 (HK$)
**交易所**: 香港交易所 (HKG)

❌ 數據獲取遇到問題: {str(e2)}

**建議**：
1. 檢查網絡連接
2. 稍後重試分析
3. 使用其他港股數據源
4. 查看公司官方財報
"""
                        result_data.append(fallback_info)
                        logger.warning(f"⚠️ [統一基本面工具] 港股使用最終備用方案")

            else:
                # 美股：使用OpenAI/Finnhub數據源
                logger.info(f"🇺🇸 [統一基本面工具] 處理美股數據...")

                try:
                    from tradingagents.dataflows.interface import get_fundamentals_openai
                    us_data = get_fundamentals_openai(ticker, curr_date)
                    result_data.append(f"## 美股基本面數據\n{us_data}")
                except Exception as e:
                    result_data.append(f"## 美股基本面數據\n獲取失败: {e}")

            # 組合所有數據
            combined_result = f"""# {ticker} 基本面分析數據

**股票類型**: {market_info['market_name']}
**貨币**: {market_info['currency_name']} ({market_info['currency_symbol']})
**分析日期**: {curr_date}

{chr(10).join(result_data)}

---
*數據來源: 根據股票類型自動選擇最適合的數據源*
"""

            logger.info(f"📊 [統一基本面工具] 數據獲取完成，总長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一基本面分析工具執行失败: {str(e)}"
            logger.error(f"❌ [統一基本面工具] {error_msg}")
            return error_msg

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_market_data_unified", log_args=True)
    def get_stock_market_data_unified(
        ticker: Annotated[str, "股票代碼（支持A股、港股、美股）"],
        start_date: Annotated[str, "開始日期，格式：YYYY-MM-DD"],
        end_date: Annotated[str, "結束日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        統一的股票市場數據工具
        自動识別股票類型（A股、港股、美股）並調用相應的數據源獲取價格和技術指標數據

        Args:
            ticker: 股票代碼（如：000001、0700.HK、AAPL）
            start_date: 開始日期（格式：YYYY-MM-DD）
            end_date: 結束日期（格式：YYYY-MM-DD）

        Returns:
            str: 市場數據和技術分析報告
        """
        logger.info(f"📈 [統一市場工具] 分析股票: {ticker}")

        try:
            from tradingagents.utils.stock_utils import StockUtils

            # 自動识別股票類型
            market_info = StockUtils.get_market_info(ticker)
            is_china = market_info['is_china']
            is_hk = market_info['is_hk']
            is_us = market_info['is_us']

            logger.info(f"📈 [統一市場工具] 股票類型: {market_info['market_name']}")
            logger.info(f"📈 [統一市場工具] 貨币: {market_info['currency_name']} ({market_info['currency_symbol']}")

            result_data = []

            if is_china:
                # 中國A股：使用中國股票數據源
                logger.info(f"🇨🇳 [統一市場工具] 處理A股市場數據...")

                try:
                    from tradingagents.dataflows.interface import get_china_stock_data_unified
                    stock_data = get_china_stock_data_unified(ticker, start_date, end_date)
                    result_data.append(f"## A股市場數據\n{stock_data}")
                except Exception as e:
                    result_data.append(f"## A股市場數據\n獲取失败: {e}")

            elif is_hk:
                # 港股：使用AKShare數據源
                logger.info(f"🇭🇰 [統一市場工具] 處理港股市場數據...")

                try:
                    from tradingagents.dataflows.interface import get_hk_stock_data_unified
                    hk_data = get_hk_stock_data_unified(ticker, start_date, end_date)
                    result_data.append(f"## 港股市場數據\n{hk_data}")
                except Exception as e:
                    result_data.append(f"## 港股市場數據\n獲取失败: {e}")

            else:
                # 美股：優先使用FINNHUB API數據源
                logger.info(f"🇺🇸 [統一市場工具] 處理美股市場數據...")

                try:
                    from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
                    us_data = get_us_stock_data_cached(ticker, start_date, end_date)
                    result_data.append(f"## 美股市場數據\n{us_data}")
                except Exception as e:
                    result_data.append(f"## 美股市場數據\n獲取失败: {e}")

            # 組合所有數據
            combined_result = f"""# {ticker} 市場數據分析

**股票類型**: {market_info['market_name']}
**貨币**: {market_info['currency_name']} ({market_info['currency_symbol']})
**分析期間**: {start_date} 至 {end_date}

{chr(10).join(result_data)}

---
*數據來源: 根據股票類型自動選擇最適合的數據源*
"""

            logger.info(f"📈 [統一市場工具] 數據獲取完成，总長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一市場數據工具執行失败: {str(e)}"
            logger.error(f"❌ [統一市場工具] {error_msg}")
            return error_msg

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_news_unified", log_args=True)
    def get_stock_news_unified(
        ticker: Annotated[str, "股票代碼（支持A股、港股、美股）"],
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        統一的股票新聞工具
        自動识別股票類型（A股、港股、美股）並調用相應的新聞數據源

        Args:
            ticker: 股票代碼（如：000001、0700.HK、AAPL）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 新聞分析報告
        """
        logger.info(f"📰 [統一新聞工具] 分析股票: {ticker}")

        try:
            from tradingagents.utils.stock_utils import StockUtils
            from datetime import datetime, timedelta

            # 自動识別股票類型
            market_info = StockUtils.get_market_info(ticker)
            is_china = market_info['is_china']
            is_hk = market_info['is_hk']
            is_us = market_info['is_us']

            logger.info(f"📰 [統一新聞工具] 股票類型: {market_info['market_name']}")

            # 計算新聞查詢的日期範围
            end_date = datetime.strptime(curr_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=7)
            start_date_str = start_date.strftime('%Y-%m-%d')

            result_data = []

            if is_china or is_hk:
                # 中國A股和港股：使用AKShare东方財富新聞和Google新聞（中文搜索）
                logger.info(f"🇨🇳🇭🇰 [統一新聞工具] 處理中文新聞...")

                # 1. 嘗試獲取AKShare东方財富新聞
                try:
                    # 處理股票代碼
                    clean_ticker = ticker.replace('.SH', '').replace('.SZ', '').replace('.SS', '')\
                                   .replace('.HK', '').replace('.XSHE', '').replace('.XSHG', '')
                    
                    logger.info(f"🇨🇳🇭🇰 [統一新聞工具] 嘗試獲取东方財富新聞: {clean_ticker}")
                    
                    # 導入AKShare新聞獲取函數
                    from tradingagents.dataflows.akshare_utils import get_stock_news_em
                    
                    # 獲取东方財富新聞
                    news_df = get_stock_news_em(clean_ticker)
                    
                    if not news_df.empty:
                        # 格式化东方財富新聞
                        em_news_items = []
                        for _, row in news_df.iterrows():
                            news_title = row.get('標題', '')
                            news_time = row.get('時間', '')
                            news_url = row.get('鏈接', '')
                            
                            news_item = f"- **{news_title}** [{news_time}]({news_url})"
                            em_news_items.append(news_item)
                        
                        # 添加到結果中
                        if em_news_items:
                            em_news_text = "\n".join(em_news_items)
                            result_data.append(f"## 东方財富新聞\n{em_news_text}")
                            logger.info(f"🇨🇳🇭🇰 [統一新聞工具] 成功獲取{len(em_news_items)}條东方財富新聞")
                except Exception as em_e:
                    logger.error(f"❌ [統一新聞工具] 东方財富新聞獲取失败: {em_e}")
                    result_data.append(f"## 东方財富新聞\n獲取失败: {em_e}")

                # 2. 獲取Google新聞作為補充
                try:
                    # 獲取公司中文名稱用於搜索
                    if is_china:
                        # A股使用股票代碼搜索，添加更多中文關键詞
                        clean_ticker = ticker.replace('.SH', '').replace('.SZ', '').replace('.SS', '')\
                                       .replace('.XSHE', '').replace('.XSHG', '')
                        search_query = f"{clean_ticker} 股票 公司 財報 新聞"
                        logger.info(f"🇨🇳 [統一新聞工具] A股Google新聞搜索關键詞: {search_query}")
                    else:
                        # 港股使用代碼搜索
                        search_query = f"{ticker} 港股"
                        logger.info(f"🇭🇰 [統一新聞工具] 港股Google新聞搜索關键詞: {search_query}")

                    from tradingagents.dataflows.interface import get_google_news
                    news_data = get_google_news(search_query, curr_date)
                    result_data.append(f"## Google新聞\n{news_data}")
                    logger.info(f"🇨🇳🇭🇰 [統一新聞工具] 成功獲取Google新聞")
                except Exception as google_e:
                    logger.error(f"❌ [統一新聞工具] Google新聞獲取失败: {google_e}")
                    result_data.append(f"## Google新聞\n獲取失败: {google_e}")

            else:
                # 美股：使用Finnhub新聞
                logger.info(f"🇺🇸 [統一新聞工具] 處理美股新聞...")

                try:
                    from tradingagents.dataflows.interface import get_finnhub_news
                    news_data = get_finnhub_news(ticker, start_date_str, curr_date)
                    result_data.append(f"## 美股新聞\n{news_data}")
                except Exception as e:
                    result_data.append(f"## 美股新聞\n獲取失败: {e}")

            # 組合所有數據
            combined_result = f"""# {ticker} 新聞分析

**股票類型**: {market_info['market_name']}
**分析日期**: {curr_date}
**新聞時間範围**: {start_date_str} 至 {curr_date}

{chr(10).join(result_data)}

---
*數據來源: 根據股票類型自動選擇最適合的新聞源*
"""

            logger.info(f"📰 [統一新聞工具] 數據獲取完成，总長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一新聞工具執行失败: {str(e)}"
            logger.error(f"❌ [統一新聞工具] {error_msg}")
            return error_msg

    @staticmethod
    @tool
    @log_tool_call(tool_name="get_stock_sentiment_unified", log_args=True)
    def get_stock_sentiment_unified(
        ticker: Annotated[str, "股票代碼（支持A股、港股、美股）"],
        curr_date: Annotated[str, "當前日期，格式：YYYY-MM-DD"]
    ) -> str:
        """
        統一的股票情绪分析工具
        自動识別股票類型（A股、港股、美股）並調用相應的情绪數據源

        Args:
            ticker: 股票代碼（如：000001、0700.HK、AAPL）
            curr_date: 當前日期（格式：YYYY-MM-DD）

        Returns:
            str: 情绪分析報告
        """
        logger.info(f"😊 [統一情绪工具] 分析股票: {ticker}")

        try:
            from tradingagents.utils.stock_utils import StockUtils

            # 自動识別股票類型
            market_info = StockUtils.get_market_info(ticker)
            is_china = market_info['is_china']
            is_hk = market_info['is_hk']
            is_us = market_info['is_us']

            logger.info(f"😊 [統一情绪工具] 股票類型: {market_info['market_name']}")

            result_data = []

            if is_china or is_hk:
                # 中國A股和港股：使用社交媒體情绪分析
                logger.info(f"🇨🇳🇭🇰 [統一情绪工具] 處理中文市場情绪...")

                try:
                    # 可以集成微博、雪球、东方財富等中文社交媒體情绪
                    # 目前使用基础的情绪分析
                    sentiment_summary = f"""
## 中文市場情绪分析

**股票**: {ticker} ({market_info['market_name']})
**分析日期**: {curr_date}

### 市場情绪概况
- 由於中文社交媒體情绪數據源暂未完全集成，當前提供基础分析
- 建議關註雪球、东方財富、同花顺等平台的討論熱度
- 港股市場还需關註香港本地財經媒體情绪

### 情绪指標
- 整體情绪: 中性
- 討論熱度: 待分析
- 投資者信心: 待評估

*註：完整的中文社交媒體情绪分析功能正在開發中*
"""
                    result_data.append(sentiment_summary)
                except Exception as e:
                    result_data.append(f"## 中文市場情绪\n獲取失败: {e}")

            else:
                # 美股：使用Reddit情绪分析
                logger.info(f"🇺🇸 [統一情绪工具] 處理美股情绪...")

                try:
                    from tradingagents.dataflows.interface import get_reddit_sentiment

                    sentiment_data = get_reddit_sentiment(ticker, curr_date)
                    result_data.append(f"## 美股Reddit情绪\n{sentiment_data}")
                except Exception as e:
                    result_data.append(f"## 美股Reddit情绪\n獲取失败: {e}")

            # 組合所有數據
            combined_result = f"""# {ticker} 情绪分析

**股票類型**: {market_info['market_name']}
**分析日期**: {curr_date}

{chr(10).join(result_data)}

---
*數據來源: 根據股票類型自動選擇最適合的情绪數據源*
"""

            logger.info(f"😊 [統一情绪工具] 數據獲取完成，总長度: {len(combined_result)}")
            return combined_result

        except Exception as e:
            error_msg = f"統一情绪分析工具執行失败: {str(e)}"
            logger.error(f"❌ [統一情绪工具] {error_msg}")
            return error_msg
