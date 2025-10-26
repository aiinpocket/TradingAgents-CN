from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

# 導入Google工具調用處理器
from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler


def _get_company_name_for_china_market(ticker: str, market_info: dict) -> str:
    """
    為中國市場分析師獲取公司名稱

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
                logger.debug(f"📊 [中國市場分析師] 從統一接口獲取中國股票名稱: {ticker} -> {company_name}")
                return company_name
            else:
                logger.warning(f"⚠️ [中國市場分析師] 無法從統一接口解析股票名稱: {ticker}")
                return f"股票代碼{ticker}"

        elif market_info['is_hk']:
            # 港股：使用改進的港股工具
            try:
                from tradingagents.dataflows.improved_hk_utils import get_hk_company_name_improved
                company_name = get_hk_company_name_improved(ticker)
                logger.debug(f"📊 [中國市場分析師] 使用改進港股工具獲取名稱: {ticker} -> {company_name}")
                return company_name
            except Exception as e:
                logger.debug(f"📊 [中國市場分析師] 改進港股工具獲取名稱失敗: {e}")
                # 降級方案：生成友好的默認名稱
                clean_ticker = ticker.replace('.HK', '').replace('.hk', '')
                return f"港股{clean_ticker}"

        elif market_info['is_us']:
            # 美股：使用簡單映射或返回代碼
            us_stock_names = {
                'AAPL': '蘋果公司',
                'TSLA': '特斯拉',
                'NVDA': '英偉達',
                'MSFT': '微軟',
                'GOOGL': '谷歌',
                'AMZN': '亞馬遜',
                'META': 'Meta',
                'NFLX': '奈飛'
            }

            company_name = us_stock_names.get(ticker.upper(), f"美股{ticker}")
            logger.debug(f"📊 [中國市場分析師] 美股名稱映射: {ticker} -> {company_name}")
            return company_name

        else:
            return f"股票{ticker}"

    except Exception as e:
        logger.error(f"❌ [中國市場分析師] 獲取公司名稱失敗: {e}")
        return f"股票{ticker}"


def create_china_market_analyst(llm, toolkit):
    """創建中國市場分析師"""
    
    def china_market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # 獲取股票市場信息
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(ticker)
        
        # 獲取公司名稱
        company_name = _get_company_name_for_china_market(ticker, market_info)
        logger.info(f"[中國市場分析師] 公司名稱: {company_name}")
        
        # 中國股票分析工具
        tools = [
            toolkit.get_china_stock_data,
            toolkit.get_china_market_overview,
            toolkit.get_YFin_data,  # 备用數據源
        ]
        
        system_message = (
            """您是一位專業的中國股市分析師，專門分析A股、港股等中國資本市場。您具備深厚的中國股市知識和豐富的本土投資經驗。

您的專業領域包括：
1. **A股市場分析**: 深度理解A股的獨特性，包括漲跌停制度、T+1交易、融資融券等
2. **中國經濟政策**: 熟悉貨幣政策、財政政策對股市的影響機制
3. **行業板塊輪動**: 掌握中國特色的板塊輪動規律和熱點切換
4. **監管環境**: 了解證監會政策、退市制度、註冊制等監管變化
5. **市場情緒**: 理解中國投資者的行為特徵和情緒波動

分析重點：
- **技術面分析**: 使用通達信數據進行精確的技術指標分析
- **基本面分析**: 結合中國會計準則和財報特點進行分析
- **政策面分析**: 評估政策變化對個股和板塊的影響
- **資金面分析**: 分析北向資金、融資融券、大宗交易等資金流向
- **市場風格**: 判斷當前是成長風格還是價值風格占優

中國股市特色考慮：
- 漲跌停板限制對交易策略的影響
- ST股票的特殊風險和機會
- 科創板、創業板的差異化分析
- 國企改革、混改等主題投資機會
- 中美關系、地緣政治對中概股的影響

請基於Tushare數據接口提供的實時數據和技術指標，結合中國股市的特殊性，撰寫專業的中文分析報告。
確保在報告末尾附上Markdown表格總結關鍵發現和投資建議。"""
        )
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一位專業的AI助手，與其他分析師協作進行股票分析。"
                    " 使用提供的工具獲取和分析數據。"
                    " 如果您無法完全回答，沒關係；其他分析師會補充您的分析。"
                    " 專註於您的專業領域，提供高質量的分析見解。"
                    " 您可以訪問以下工具：{tool_names}。\n{system_message}"
                    "當前分析日期：{current_date}，分析標的：{ticker}。請用中文撰寫所有分析內容。",
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
            logger.info(f"📊 [中國市場分析師] 檢測到Google模型，使用統一工具調用處理器")
            
            # 創建分析提示詞
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="中國市場分析",
                specific_requirements="重點關註中國A股市場特點、政策影響、行業發展趨勢等。"
            )
            
            # 處理Google模型工具調用
            report, messages = GoogleToolCallHandler.handle_google_tool_calls(
                result=result,
                llm=llm,
                tools=tools,
                state=state,
                analysis_prompt_template=analysis_prompt_template,
                analyst_name="中國市場分析師"
            )
        else:
            # 非Google模型的處理邏輯
            logger.debug(f"📊 [DEBUG] 非Google模型 ({llm.__class__.__name__})，使用標準處理邏輯")
            
            report = ""
            if len(result.tool_calls) == 0:
                report = result.content
        
        return {
            "messages": [result],
            "china_market_report": report,
            "sender": "ChinaMarketAnalyst",
        }
    
    return china_market_analyst_node


def create_china_stock_screener(llm, toolkit):
    """創建中國股票篩選器"""
    
    def china_stock_screener_node(state):
        current_date = state["trade_date"]
        
        tools = [
            toolkit.get_china_market_overview,
        ]
        
        system_message = (
            """您是一位專業的中國股票篩選專家，負責從A股市場中篩選出具有投資價值的股票。

篩選維度包括：
1. **基本面篩選**:
   - 財務指標：ROE、ROA、淨利潤增長率、營收增長率
   - 估值指標：PE、PB、PEG、PS比率
   - 財務健康：資產負債率、流動比率、速動比率

2. **技術面篩選**:
   - 趨勢指標：均線系統、MACD、KDJ
   - 動量指標：RSI、威廉指標、CCI
   - 成交量指標：量價關系、換手率

3. **市場面篩選**:
   - 資金流向：主力資金淨流入、北向資金偏好
   - 機構持倉：基金重倉、社保持倉、QFII持倉
   - 市場熱度：概念板塊活躍度、題材炒作程度

4. **政策面篩選**:
   - 政策受益：國家政策扶持行業
   - 改革紅利：國企改革、混改標的
   - 監管影響：監管政策變化的影響

篩選策略：
- **價值投資**: 低估值、高分紅、穩定增長
- **成長投資**: 高增長、新興行業、技術創新
- **主題投資**: 政策驅動、事件催化、概念炒作
- **周期投資**: 經濟周期、行業周期、季節性

請基於當前市場環境和政策背景，提供專業的股票篩選建議。"""
        )
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", 
                    "您是一位專業的股票篩選專家。"
                    " 使用提供的工具分析市場概況。"
                    " 您可以訪問以下工具：{tool_names}。\n{system_message}"
                    "當前日期：{current_date}。請用中文撰寫分析內容。",
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
        
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])
        
        return {
            "messages": [result],
            "stock_screening_report": result.content,
            "sender": "ChinaStockScreener",
        }
    
    return china_stock_screener_node
