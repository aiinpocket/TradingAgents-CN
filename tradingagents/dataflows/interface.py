from typing import Annotated
import os
from .googlenews_utils import getNewsData
from .finnhub_utils import get_data_in_range

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('dataflows')

# 嘗試匯入 yfinance 相關模組，如果失敗則跳過
try:
    from .yfin_utils import YFinanceUtils
except ImportError as e:
    logger.warning(f"yfinance工具不可用: {e}")
    YFinanceUtils = None

try:
    from .stockstats_utils import StockstatsUtils
except ImportError as e:
    logger.warning(f"stockstats工具不可用: {e}")
    StockstatsUtils = None
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pandas as pd
from openai import OpenAI

# 嘗試匯入yfinance，如果失敗則設定為None
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError as e:
    logger.warning(f"yfinance庫不可用: {e}")
    yf = None
    YF_AVAILABLE = False
from .config import get_config, DATA_DIR


def get_finnhub_news(
    ticker: Annotated[
        str,
        "Search query of a company's, e.g. 'AAPL, TSM, etc.",
    ],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve news about a company within a time frame

    Args
        ticker (str): ticker for the company you are interested in
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns
        str: dataframe containing the news of the company in the time frame

    """

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    result = get_data_in_range(ticker, before, curr_date, "news_data", DATA_DIR)

    if len(result) == 0:
        error_msg = f"無法獲取{ticker}的新聞資料 ({before} 到 {curr_date})\n"
        error_msg += f"可能的原因：\n"
        error_msg += f"1. 資料檔案不存在或路徑配置錯誤\n"
        error_msg += f"2. 指定日期範圍內沒有新聞資料\n"
        error_msg += f"3. 需要先下載或更新Finnhub新聞資料\n"
        error_msg += f"建議：檢查資料目錄配置或重新獲取新聞資料"
        logger.debug(f"{error_msg}")
        return error_msg

    combined_result = ""
    for day, data in result.items():
        if len(data) == 0:
            continue
        for entry in data:
            current_news = (
                "### " + entry["headline"] + f" ({day})" + "\n" + entry["summary"]
            )
            combined_result += current_news + "\n\n"

    return f"## {ticker} News, from {before} to {curr_date}:\n" + str(combined_result)


def get_finnhub_company_insider_sentiment(
    ticker: Annotated[str, "ticker symbol for the company"],
    curr_date: Annotated[
        str,
        "current date of you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "number of days to look back"],
):
    """
    Retrieve insider sentiment about a company (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading on, yyyy-mm-dd
    Returns:
        str: a report of the sentiment in the past 15 days starting at curr_date
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if len(data) == 0:
        return f"[{ticker}] 在指定期間內無內部人情緒資料。"

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### {entry['year']}-{entry['month']}:\nChange: {entry['change']}\nMonthly Share Purchase Ratio: {entry['mspr']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} Insider Sentiment Data for {before} to {curr_date}:\n"
        + result_str
        + "The change field refers to the net buying/selling from all insiders' transactions. The mspr field refers to monthly share purchase ratio."
    )


def get_finnhub_company_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[
        str,
        "current date you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve insider transcaction information about a company (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading at, yyyy-mm-dd
    Returns:
        str: a report of the company's insider transaction/trading informtaion in the past 15 days
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if len(data) == 0:
        return f"[{ticker}] 在指定期間內無內部人交易資料。"

    result_str = ""

    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### Filing Date: {entry['filingDate']}, {entry['name']}:\nChange:{entry['change']}\nShares: {entry['share']}\nTransaction Price: {entry['transactionPrice']}\nTransaction Code: {entry['transactionCode']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} insider transactions from {before} to {curr_date}:\n"
        + result_str
        + "The change field reflects the variation in share count—here a negative number indicates a reduction in holdings—while share specifies the total number of shares involved. The transactionPrice denotes the per-share price at which the trade was executed, and transactionDate marks when the transaction occurred. The name field identifies the insider making the trade, and transactionCode (e.g., S for sale) clarifies the nature of the transaction. FilingDate records when the transaction was officially reported, and the unique id links to the specific SEC filing, as indicated by the source. Additionally, the symbol ties the transaction to a particular company, isDerivative flags whether the trade involves derivative securities, and currency notes the currency context of the transaction."
    )


def get_simfin_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "balance_sheet",
        "companies",
        "us",
        f"us-balance-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        logger.info("No balance sheet available before the given current date.")
        return f"[{ticker}] 在指定日期前無可用的資產負債表資料。"

    # Get the most recent balance sheet by selecting the row with the latest Publish Date
    latest_balance_sheet = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_balance_sheet = latest_balance_sheet.drop("SimFinId")

    return (
        f"## {freq} balance sheet for {ticker} released on {str(latest_balance_sheet['Publish Date'])[0:10]}: \n"
        + str(latest_balance_sheet)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of assets, liabilities, and equity. Assets are grouped as current (liquid items like cash and receivables) and noncurrent (long-term investments and property). Liabilities are split between short-term obligations and long-term debts, while equity reflects shareholder funds such as paid-in capital and retained earnings. Together, these components ensure that total assets equal the sum of liabilities and equity."
    )


def get_simfin_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "cash_flow",
        "companies",
        "us",
        f"us-cashflow-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        logger.info("No cash flow statement available before the given current date.")
        return f"[{ticker}] 在指定日期前無可用的現金流量表資料。"

    # Get the most recent cash flow statement by selecting the row with the latest Publish Date
    latest_cash_flow = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_cash_flow = latest_cash_flow.drop("SimFinId")

    return (
        f"## {freq} cash flow statement for {ticker} released on {str(latest_cash_flow['Publish Date'])[0:10]}: \n"
        + str(latest_cash_flow)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of cash movements. Operating activities show cash generated from core business operations, including net income adjustments for non-cash items and working capital changes. Investing activities cover asset acquisitions/disposals and investments. Financing activities include debt transactions, equity issuances/repurchases, and dividend payments. The net change in cash represents the overall increase or decrease in the company's cash position during the reporting period."
    )


def get_simfin_income_statements(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "income_statements",
        "companies",
        "us",
        f"us-income-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        logger.info("No income statement available before the given current date.")
        return f"[{ticker}] 在指定日期前無可用的損益表資料。"

    # Get the most recent income statement by selecting the row with the latest Publish Date
    latest_income = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_income = latest_income.drop("SimFinId")

    return (
        f"## {freq} income statement for {ticker} released on {str(latest_income['Publish Date'])[0:10]}: \n"
        + str(latest_income)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a comprehensive breakdown of the company's financial performance. Starting with Revenue, it shows Cost of Revenue and resulting Gross Profit. Operating Expenses are detailed, including SG&A, R&D, and Depreciation. The statement then shows Operating Income, followed by non-operating items and Interest Expense, leading to Pretax Income. After accounting for Income Tax and any Extraordinary items, it concludes with Net Income, representing the company's bottom-line profit or loss for the period."
    )


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"] = 7,
) -> str:
    """透過 Google News 搜尋指定查詢的新聞資料"""
    query = query.replace(" ", "+")

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    logger.info(f"[Google新聞] 開始獲取新聞，查詢: {query}, 時間範圍: {before} 至 {curr_date}")
    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        logger.warning(f"[Google新聞] 未找到相關新聞，查詢: {query}")
        return f"在指定期間內未找到 {query.replace('+', ' ')} 的相關 Google 新聞。"

    logger.info(f"[Google新聞] 成功獲取 {len(news_results)} 條新聞，查詢: {query}")
    return f"## {query.replace('+', ' ')} Google News, from {before} to {curr_date}:\n\n{news_str}"


def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date - relativedelta(days=look_back_days)

    if not online:
        # read from YFin data
        data = pd.read_csv(
            os.path.join(
                DATA_DIR,
                f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
            )
        )
        data["Date"] = pd.to_datetime(data["Date"], utc=True)
        dates_in_df = data["Date"].astype(str).str[:10]

        ind_string = ""
        while curr_date >= before:
            # only do the trading dates
            if curr_date.strftime("%Y-%m-%d") in dates_in_df.values:
                indicator_value = get_stockstats_indicator(
                    symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
                )

                ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)
    else:
        # online gathering
        ind_string = ""
        while curr_date >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
            )

            ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str


def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
            os.path.join(DATA_DIR, "market_data", "price_data"),
            online=online,
        )
    except Exception as e:
        logger.error(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return f"[{symbol}] 無法獲取 {indicator} 技術指標資料: {e}"

    return str(indicator_value)


def get_YFin_data_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    # calculate past days
    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    start_date = before.strftime("%Y-%m-%d")

    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= curr_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # Set pandas display options to show the full DataFrame
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        df_string = filtered_data.to_string()

    return (
        f"## Raw Market Data for {symbol} from {start_date} to {curr_date}:\n\n"
        + df_string
    )


def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):
    # 檢查yfinance是否可用
    if not YF_AVAILABLE or yf is None:
        return "yfinance庫不可用，無法獲取美股資料"

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string


def get_YFin_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    if end_date > "2025-03-25":
        raise Exception(
            f"Get_YFin_Data: {end_date} is outside of the data range of 2015-01-01 to 2025-03-25"
        )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= end_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # remove the index from the dataframe
    filtered_data = filtered_data.reset_index(drop=True)

    return filtered_data


def get_stock_news_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Social Media for {ticker} from 7 days before {curr_date} to {curr_date}? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text


def get_global_news_openai(curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search global or macroeconomics news from 7 days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text


def get_fundamentals_finnhub(ticker, curr_date):
    """
    使用Finnhub API獲取股票基本面資料作為OpenAI的備選方案
    Args:
        ticker (str): 股票代碼
        curr_date (str): 當前日期，格式為yyyy-mm-dd
    Returns:
        str: 格式化的基本面資料報告
    """
    try:
        import finnhub
        import os
        from .cache_manager import get_cache
        
        # 檢查快取
        cache = get_cache()
        cached_key = cache.find_cached_fundamentals_data(ticker, data_source="finnhub")
        if cached_key:
            cached_data = cache.load_fundamentals_data(cached_key)
            if cached_data:
                logger.debug(f"從快取載入Finnhub基本面資料: {ticker}")
                return cached_data
        
        # 獲取Finnhub API密鑰
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            return "錯誤：未配置FINNHUB_API_KEY環境變數"
        
        # 初始化Finnhub客戶端
        finnhub_client = finnhub.Client(api_key=api_key)
        
        logger.debug(f"使用Finnhub API獲取 {ticker} 的基本面資料...")
        
        # 獲取基本財務資料
        try:
            basic_financials = finnhub_client.company_basic_financials(ticker, 'all')
        except Exception as e:
            logger.error(f"Finnhub基本財務資料取得失敗: {str(e)}")
            basic_financials = None
        
        # 獲取公司概況
        try:
            company_profile = finnhub_client.company_profile2(symbol=ticker)
        except Exception as e:
            logger.error(f"Finnhub公司概況獲取失敗: {str(e)}")
            company_profile = None
        
        # 獲取收益資料
        try:
            earnings = finnhub_client.company_earnings(ticker, limit=4)
        except Exception as e:
            logger.error(f"Finnhub收益資料取得失敗: {str(e)}")
            earnings = None
        
        # 格式化報告
        report = f"# {ticker} 基本面分析報告（Finnhub資料來源）\n\n"
        report += f"**資料取得時間**: {curr_date}\n"
        report += f"**資料來源**: Finnhub API\n\n"
        
        # 公司概況部分
        if company_profile:
            report += "## 公司概況\n"
            report += f"- **公司名稱**: {company_profile.get('name', 'N/A')}\n"
            report += f"- **行業**: {company_profile.get('finnhubIndustry', 'N/A')}\n"
            report += f"- **國家**: {company_profile.get('country', 'N/A')}\n"
            report += f"- **貨幣**: {company_profile.get('currency', 'N/A')}\n"
            report += f"- **市值**: {company_profile.get('marketCapitalization', 'N/A')} 百萬美元\n"
            report += f"- **流通股數**: {company_profile.get('shareOutstanding', 'N/A')} 百萬股\n\n"
        
        # 基本財務指標
        if basic_financials and 'metric' in basic_financials:
            metrics = basic_financials['metric']
            report += "## 關鍵財務指標\n"
            report += "| 指標 | 數值 |\n"
            report += "|------|------|\n"
            
            # 估值指標
            if 'peBasicExclExtraTTM' in metrics:
                report += f"| 市盈率 (PE) | {metrics['peBasicExclExtraTTM']:.2f} |\n"
            if 'psAnnual' in metrics:
                report += f"| 市銷率 (PS) | {metrics['psAnnual']:.2f} |\n"
            if 'pbAnnual' in metrics:
                report += f"| 市淨率 (PB) | {metrics['pbAnnual']:.2f} |\n"
            
            # 盈利能力指標
            if 'roeTTM' in metrics:
                report += f"| 淨資產收益率 (ROE) | {metrics['roeTTM']:.2f}% |\n"
            if 'roaTTM' in metrics:
                report += f"| 總資產收益率 (ROA) | {metrics['roaTTM']:.2f}% |\n"
            if 'netProfitMarginTTM' in metrics:
                report += f"| 淨利潤率 | {metrics['netProfitMarginTTM']:.2f}% |\n"
            
            # 財務健康指標
            if 'currentRatioAnnual' in metrics:
                report += f"| 流動比率 | {metrics['currentRatioAnnual']:.2f} |\n"
            if 'totalDebt/totalEquityAnnual' in metrics:
                report += f"| 負債權益比 | {metrics['totalDebt/totalEquityAnnual']:.2f} |\n"
            
            report += "\n"
        
        # 收益歷史
        if earnings:
            report += "## 收益歷史\n"
            report += "| 季度 | 實際EPS | 預期EPS | 差異 |\n"
            report += "|------|---------|---------|------|\n"
            for earning in earnings[:4]:  # 顯示最近4個季度
                actual = earning.get('actual', 'N/A')
                estimate = earning.get('estimate', 'N/A')
                period = earning.get('period', 'N/A')
                surprise = earning.get('surprise', 'N/A')
                report += f"| {period} | {actual} | {estimate} | {surprise} |\n"
            report += "\n"
        
        # 資料可用性說明
        report += "## 資料說明\n"
        report += "- 本報告使用Finnhub API提供的官方財務資料\n"
        report += "- 資料來源於公司財報和SEC檔案\n"
        report += "- TTM表示過去12個月資料\n"
        report += "- Annual表示年度資料\n\n"
        
        if not basic_financials and not company_profile and not earnings:
            report += "**警告**: 無法獲取該股票的基本面資料，可能原因：\n"
            report += "- 股票代碼不正確\n"
            report += "- Finnhub API限制\n"
            report += "- 該股票暫無基本面資料\n"
        
        # 儲存到快取
        if report and len(report) > 100:  # 只有當報告有實際內容時才快取
            cache.save_fundamentals_data(ticker, report, data_source="finnhub")
        
        logger.debug(f"Finnhub基本面資料取得完成，報告長度: {len(report)}")
        return report
        
    except ImportError:
        return "錯誤：未安裝finnhub-python庫，請運行: pip install finnhub-python"
    except Exception as e:
        logger.error(f"Finnhub基本面資料取得失敗: {str(e)}")
        return f"Finnhub基本面資料取得失敗: {str(e)}"


def get_fundamentals_openai(ticker, curr_date):
    """
    獲取股票基本面資料，優先使用OpenAI，失敗時回退到Finnhub API
    支援快取機制以提高效能
    Args:
        ticker (str): 股票代碼
        curr_date (str): 當前日期，格式為yyyy-mm-dd
    Returns:
        str: 基本面資料報告
    """
    try:
        from .cache_manager import get_cache
        
        # 檢查快取 - 優先檢查OpenAI快取
        cache = get_cache()
        cached_key = cache.find_cached_fundamentals_data(ticker, data_source="openai")
        if cached_key:
            cached_data = cache.load_fundamentals_data(cached_key)
            if cached_data:
                logger.debug(f"從快取載入OpenAI基本面資料: {ticker}")
                return cached_data
        
        config = get_config()

        # 檢查是否配置了OpenAI API Key（這是最關鍵的檢查）
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.debug("未配置OPENAI_API_KEY，跳過OpenAI API，直接使用Finnhub")
            return get_fundamentals_finnhub(ticker, curr_date)

        # 檢查是否配置了OpenAI相關設定
        if not config.get("backend_url") or not config.get("quick_think_llm"):
            logger.debug("OpenAI配置不完整，直接使用Finnhub API")
            return get_fundamentals_finnhub(ticker, curr_date)

        # 檢查backend_url是否是OpenAI的URL
        backend_url = config.get("backend_url", "")
        if "openai.com" not in backend_url:
            logger.debug(f"backend_url不是OpenAI API ({backend_url})，跳過OpenAI，使用Finnhub")
            return get_fundamentals_finnhub(ticker, curr_date)
        
        logger.debug(f"嘗試使用OpenAI獲取 {ticker} 的基本面資料...")
        
        client = OpenAI(base_url=config["backend_url"])

        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to the month of {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc",
                        }
                    ],
                }
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[
                {
                    "type": "web_search_preview",
                    "user_location": {"type": "approximate"},
                    "search_context_size": "low",
                }
            ],
            temperature=1,
            max_output_tokens=4096,
            top_p=1,
            store=True,
        )

        result = response.output[1].content[0].text
        
        # 儲存到快取
        if result and len(result) > 100:  # 只有當結果有實際內容時才快取
            cache.save_fundamentals_data(ticker, result, data_source="openai")
        
        logger.debug(f"OpenAI基本面資料取得成功，長度: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"OpenAI基本面資料取得失敗: {str(e)}")
        logger.debug("回退到Finnhub API...")
        return get_fundamentals_finnhub(ticker, curr_date)


def get_stock_data_by_market(symbol: str, start_date: str = None, end_date: str = None) -> str:
    """
    取得美股股票資料，透過快取機制獲取資料

    Args:
        symbol: 股票代碼（美股）
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        str: 格式化的股票資料
    """
    try:
        from .optimized_us_data import get_us_stock_data_cached

        return get_us_stock_data_cached(symbol, start_date, end_date)

    except Exception as e:
        logger.error(f"[get_stock_data_by_market] 取得股票資料失敗: {e}")
        return f"取得股票 {symbol} 資料失敗: {e}"
