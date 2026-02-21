from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 導入統一日誌系統和分析模塊日誌裝飾器
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_analyst_module
logger = get_logger("analysts.social_media")

# 導入Google工具調用處理器
from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler


def _get_company_name_for_social_media(ticker: str, market_info: dict) -> str:
    """
    為社交媒體分析師獲取公司名稱

    Args:
        ticker: 股票代碼
        market_info: 市場信息字典

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
        logger.error(f"[社交媒體分析師] 獲取公司名稱失敗: {e}")
        return ticker


def create_social_media_analyst(llm, toolkit):
    @log_analyst_module("social_media")
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info
        market_info = get_stock_market_info(ticker)
        
        # 獲取公司名稱
        company_name = _get_company_name_for_social_media(ticker, market_info)
        logger.info(f"[社交媒體分析師] 公司名稱: {company_name}")

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news_openai]
        else:
            # 使用 Reddit 和統一情緒分析工具
            tools = [
                toolkit.get_stock_sentiment_unified,
                toolkit.get_reddit_stock_info,
            ]

        system_message = (
            """您是一位專業的社交媒體和投資情緒分析師，負責分析投資者對特定美股的討論和情緒變化。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**


您的主要職責包括：
1. 分析主要投資社群平台的投資者情緒（如 Reddit、StockTwits 等）
2. 監控財經媒體和新聞對股票的報導傾向
3. 識別影響股價的熱點事件和市場傳言
4. 評估散戶與機構投資者的觀點差異
5. 分析政策變化對投資者情緒的影響
6. 評估情緒變化對股價的潛在影響

重點關注平台：
- 投資社群：Reddit (r/wallstreetbets, r/stocks)、StockTwits
- 財經新聞：Bloomberg、CNBC、Reuters、Yahoo Finance
- 社交媒體：Twitter/X 財經大V
- 專業分析：各大券商研報、Seeking Alpha

分析要點：
- 投資者情緒的變化趨勢和原因
- 關鍵意見領袖(KOL)的觀點和影響力
- 熱點事件對股價預期的影響
- 政策解讀和市場預期變化
- 散戶情緒與機構觀點的差異

情緒價格影響分析要求：
- 量化投資者情緒強度（樂觀/悲觀程度）
- 評估情緒變化對短期股價的影響（1-5天）
- 分析散戶情緒與股價走勢的相關性
- 識別情緒驅動的價格支撐位和阻力位
- 提供基於情緒分析的價格預期調整
- 評估市場情緒對估值的影響程度
- 不允許回覆'無法評估情緒影響'或'需要更多數據'

必須包含：
- 情緒指數評分（1-10分）
- 預期價格波動幅度
- 基於情緒的交易時機建議

請撰寫詳細的中文分析報告，並在報告末尾附上Markdown表格總結關鍵發現。
注意：如果特定平台的數據獲取受限，請明確說明並提供替代分析建議。"""
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
        # 安全地獲取工具名稱，處理函數和工具對象
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

        # 使用統一的Google工具調用處理器
        if GoogleToolCallHandler.is_google_model(llm):
            logger.info(f"[社交媒體分析師] 檢測到Google模型，使用統一工具調用處理器")
            
            # 創建分析提示詞
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="社交媒體情緒分析",
                specific_requirements="重點關注投資者情緒、社交媒體討論熱度、輿論影響等。"
            )
            
            # 處理Google模型工具調用
            report, messages = GoogleToolCallHandler.handle_google_tool_calls(
                result=result,
                llm=llm,
                tools=tools,
                state=state,
                analysis_prompt_template=analysis_prompt_template,
                analyst_name="社交媒體分析師"
            )
        else:
            # 非Google模型的處理邏輯
            logger.debug(f"[DEBUG] 非Google模型 ({llm.__class__.__name__})，使用標準處理邏輯")
            
            report = ""
            if len(result.tool_calls) == 0:
                report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
