from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 導入統一日誌系統和分析模塊日誌裝饰器
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
        if market_info['is_china']:
            # 中國A股：使用統一接口獲取股票信息
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            stock_info = get_china_stock_info_unified(ticker)

            # 解析股票名稱
            if "股票名稱:" in stock_info:
                company_name = stock_info.split("股票名稱:")[1].split("\n")[0].strip()
                logger.debug(f"📊 [社交媒體分析師] 從統一接口獲取中國股票名稱: {ticker} -> {company_name}")
                return company_name
            else:
                logger.warning(f"⚠️ [社交媒體分析師] 無法從統一接口解析股票名稱: {ticker}")
                return f"股票代碼{ticker}"

        elif market_info['is_hk']:
            # 港股：使用改進的港股工具
            try:
                from tradingagents.dataflows.improved_hk_utils import get_hk_company_name_improved
                company_name = get_hk_company_name_improved(ticker)
                logger.debug(f"📊 [社交媒體分析師] 使用改進港股工具獲取名稱: {ticker} -> {company_name}")
                return company_name
            except Exception as e:
                logger.debug(f"📊 [社交媒體分析師] 改進港股工具獲取名稱失败: {e}")
                # 降級方案：生成友好的默認名稱
                clean_ticker = ticker.replace('.HK', '').replace('.hk', '')
                return f"港股{clean_ticker}"

        elif market_info['is_us']:
            # 美股：使用簡單映射或返回代碼
            us_stock_names = {
                'AAPL': '苹果公司',
                'TSLA': '特斯拉',
                'NVDA': '英伟達',
                'MSFT': '微软',
                'GOOGL': '谷歌',
                'AMZN': '亚馬逊',
                'META': 'Meta',
                'NFLX': '奈飞'
            }

            company_name = us_stock_names.get(ticker.upper(), f"美股{ticker}")
            logger.debug(f"📊 [社交媒體分析師] 美股名稱映射: {ticker} -> {company_name}")
            return company_name

        else:
            return f"股票{ticker}"

    except Exception as e:
        logger.error(f"❌ [社交媒體分析師] 獲取公司名稱失败: {e}")
        return f"股票{ticker}"


def create_social_media_analyst(llm, toolkit):
    @log_analyst_module("social_media")
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # 獲取股票市場信息
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(ticker)
        
        # 獲取公司名稱
        company_name = _get_company_name_for_social_media(ticker, market_info)
        logger.info(f"[社交媒體分析師] 公司名稱: {company_name}")

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news_openai]
        else:
            # 優先使用中國社交媒體數據，如果不可用則回退到Reddit
            tools = [
                toolkit.get_chinese_social_sentiment,
                toolkit.get_reddit_stock_info,
            ]

        system_message = (
            """您是一位專業的中國市場社交媒體和投資情绪分析師，负责分析中國投資者對特定股票的討論和情绪變化。

您的主要職责包括：
1. 分析中國主要財經平台的投資者情绪（如雪球、东方財富股吧等）
2. 監控財經媒體和新聞對股票的報道倾向
3. 识別影響股價的熱點事件和市場傳言
4. 評估散戶与機構投資者的觀點差異
5. 分析政策變化對投資者情绪的影響
6. 評估情绪變化對股價的潜在影響

重點關註平台：
- 財經新聞：財聯社、新浪財經、东方財富、腾讯財經
- 投資社区：雪球、东方財富股吧、同花顺
- 社交媒體：微博財經大V、知乎投資話題
- 專業分析：各大券商研報、財經自媒體

分析要點：
- 投資者情绪的變化趋势和原因
- 關键意见領袖(KOL)的觀點和影響力
- 熱點事件對股價預期的影響
- 政策解讀和市場預期變化
- 散戶情绪与機構觀點的差異

📊 情绪價格影響分析要求：
- 量化投資者情绪强度（乐觀/悲觀程度）
- 評估情绪變化對短期股價的影響（1-5天）
- 分析散戶情绪与股價走势的相關性
- 识別情绪驱動的價格支撑位和阻力位
- 提供基於情绪分析的價格預期調整
- 評估市場情绪對估值的影響程度
- 不允許回複'無法評估情绪影響'或'需要更多數據'

💰 必须包含：
- 情绪指數評分（1-10分）
- 預期價格波動幅度
- 基於情绪的交易時機建议

請撰寫詳細的中文分析報告，並在報告末尾附上Markdown表格总結關键發現。
註意：由於中國社交媒體API限制，如果數據獲取受限，請明確說明並提供替代分析建议。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一位有用的AI助手，与其他助手協作。"
                    " 使用提供的工具來推進回答問題。"
                    " 如果您無法完全回答，没關系；具有不同工具的其他助手"
                    " 将從您停下的地方繼续幫助。執行您能做的以取得進展。"
                    " 如果您或任何其他助手有最终交易提案：**买入/持有/卖出**或可交付成果，"
                    " 請在您的回應前加上最终交易提案：**买入/持有/卖出**，以便团隊知道停止。"
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
            logger.info(f"📊 [社交媒體分析師] 檢測到Google模型，使用統一工具調用處理器")
            
            # 創建分析提示詞
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="社交媒體情绪分析",
                specific_requirements="重點關註投資者情绪、社交媒體討論熱度、舆論影響等。"
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
            # 非Google模型的處理逻辑
            logger.debug(f"📊 [DEBUG] 非Google模型 ({llm.__class__.__name__})，使用標準處理逻辑")
            
            report = ""
            if len(result.tool_calls) == 0:
                report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
