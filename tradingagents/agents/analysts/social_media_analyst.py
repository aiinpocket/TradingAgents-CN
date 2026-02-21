from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 匯入統一日誌系統和分析模組日誌裝飾器
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_analyst_module
logger = get_logger("analysts.social_media")



def _get_company_name_for_social_media(ticker: str, market_info: dict) -> str:
    """
    為社交媒體分析師取得公司名稱

    Args:
        ticker: 股票代碼
        market_info: 市場資訊字典

    Returns:
        str: 公司名稱
    """
    try:
        us_stock_names = {
            'AAPL': '蘋果公司',
            'TSLA': '特斯拉',
            'NVDA': '輝達',
            'MSFT': '微軟',
            'GOOGL': '谷歌',
            'AMZN': '亞馬遜',
            'META': 'Meta',
            'NFLX': 'Netflix'
        }

        company_name = us_stock_names.get(ticker.upper(), ticker)
        logger.debug(f"[社交媒體分析師] 美股名稱映射: {ticker} -> {company_name}")
        return company_name

    except Exception as e:
        logger.error(f"[社交媒體分析師] 取得公司名稱失敗: {e}")
        return ticker


def create_social_media_analyst(llm, toolkit):
    @log_analyst_module("social_media")
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info
        market_info = get_stock_market_info(ticker)
        
        # 取得公司名稱
        company_name = _get_company_name_for_social_media(ticker, market_info)
        logger.info(f"[社交媒體分析師] 公司名稱: {company_name}")

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news_openai, toolkit.get_finnhub_sentiment_data]
        else:
            # 使用 FinnHub 情緒量化資料和統一情緒分析工具
            tools = [
                toolkit.get_stock_sentiment_unified,
                toolkit.get_finnhub_sentiment_data,
            ]

        system_message = (
            """您是一位專業的社交媒體和投資情緒分析師，負責分析投資者對特定美股的討論和情緒變化。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

**使用 FinnHub 情緒量化資料**（新聞看多/看空比例、分析師共識評分），這些資料提供客觀的量化指標。
搭配新聞分析來理解市場情緒的具體內容和變化趨勢。

您的主要職責包括：
1. 使用 FinnHub 情緒量化資料取得客觀的看多/看空比例和行業比較
2. 監控財經媒體和新聞對股票的報導傾向
3. 識別影響股價的熱點事件和市場傳言
4. 評估散戶與機構投資者的觀點差異
5. 分析政策變化對投資者情緒的影響
6. 評估情緒變化對股價的潛在影響

重點關注來源：
- 財經新聞：Bloomberg、CNBC、Reuters、Yahoo Finance
- 專業分析：各大券商研報、Seeking Alpha
- FinnHub 情緒量化資料：新聞情緒評分、分析師共識

分析要點：
- FinnHub 新聞情緒量化指標（bullish/bearish 比例、與行業平均的比較）
- 投資者情緒的變化趨勢和原因
- 熱點事件對股價預期的影響
- 散戶情緒與機構觀點的差異

情緒價格影響分析要求：
- 量化投資者情緒強度（樂觀/悲觀程度）
- 評估情緒變化對短期股價的影響（1-5天）
- 分析散戶情緒與股價走勢的相關性
- 識別情緒驅動的價格支撐位和阻力位
- 提供基於情緒分析的價格預期調整
- 評估市場情緒對估值的影響程度
- 不允許回覆'無法評估情緒影響'或'需要更多資料'

必須包含：
- 情緒指數評分（1-10分）
- 預期價格波動幅度
- 基於情緒的交易時機建議

請撰寫詳細的中文分析報告，並在報告末尾附上Markdown表格總結關鍵發現。
注意：如果特定平台的資料取得受限，請明確說明並提供替代分析建議。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一位有用的AI助手，與其他助手協作。"
                    " 使用提供的工具來推進回答問題。"
                    " 如果您無法完全回答，沒關係；具有不同工具的其他助手"
                    " 將從您停下的地方繼續幫助。執行您能做的以取得進展。"
                    " 如果您或任何其他助手有最終交易提案：**買入/持有/賣出**或可交付成果，"
                    " 請在您的回應前加上最終交易提案：**買入/持有/賣出**，以便團隊知道停止。"
                    " 您可以訪問以下工具：{tool_names}。\n{system_message}"
                    "供您參考，當前日期是{current_date}。我們要分析的當前公司是{ticker}。請用中文撰寫所有分析內容。",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        # 安全地取得工具名稱，處理函數和工具對象
        tool_names = []
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                tool_names.append(tool.__name__)
            else:
                tool_names.append(str(tool))

        prompt = prompt.partial(tool_names=", ".join(tool_names))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
