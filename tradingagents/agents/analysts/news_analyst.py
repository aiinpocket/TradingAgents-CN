from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from datetime import datetime

# 導入統一日誌系統和分析模塊日誌裝飾器
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_analyst_module
# 導入統一新聞工具
from tradingagents.tools.unified_news_tool import create_unified_news_tool
# 導入股票工具類
from tradingagents.utils.stock_utils import StockUtils
# 導入Google工具調用處理器
from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler

logger = get_logger("analysts.news")


def create_news_analyst(llm, toolkit):
    @log_analyst_module("news")
    def news_analyst_node(state):
        start_time = datetime.now()
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        logger.info(f"[新聞分析師] 開始分析 {ticker} 的新聞，交易日期: {current_date}")
        session_id = state.get("session_id", "未知會話")
        logger.info(f"[新聞分析師] 會話ID: {session_id}，開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 獲取市場信息
        market_info = StockUtils.get_market_info(ticker)
        logger.info(f"[新聞分析師] 股票類型: {market_info['market_name']}")
        
        # 獲取公司名稱
        def _get_company_name(ticker: str, market_info: dict) -> str:
            """根據股票代碼獲取公司名稱"""
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
                logger.debug(f"[DEBUG] 美股名稱映射: {ticker} -> {company_name}")
                return company_name

            except Exception as e:
                logger.error(f"[DEBUG] 獲取公司名稱失敗: {e}")
                return ticker
        
        company_name = _get_company_name(ticker, market_info)
        logger.info(f"[新聞分析師] 公司名稱: {company_name}")
        
        # 🔧 使用統一新聞工具，簡化工具調用
        logger.info(f"[新聞分析師] 使用統一新聞工具，自動識別股票類型並獲取相應新聞")
   # 創建統一新聞工具
        unified_news_tool = create_unified_news_tool(toolkit)
        unified_news_tool.name = "get_stock_news_unified"
        
        tools = [unified_news_tool]
        logger.info(f"[新聞分析師] 已加載統一新聞工具: get_stock_news_unified")

        system_message = (
            """您是一位專業的財經新聞分析師，負責分析最新的市場新聞和事件對股票價格的潛在影響。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**


您的主要職责包括：
1. 獲取和分析最新的實時新聞（優先15-30分鐘內的新聞）
2. 評估新聞事件的緊急程度和市場影響
3. 識別可能影響股價的關鍵信息
4. 分析新聞的時效性和可靠性
5. 提供基於新聞的交易建議和價格影響評估

重點關注的新聞類型：
- 財報發布和業績指導
- 重大合作和並購訊息
- 政策變化和監管動態
- 突發事件和危機管理
- 行業趨勢和技術突破
- 管理層變動和戰略調整

分析要點：
- 新聞的時效性（發布時間距離現在多久）
- 新聞的可信度（來源權威性）
- 市場影響程度（對股價的潛在影響）
- 投資者情緒變化（正面/負面/中性）
- 與歷史類似事件的對比

📊 價格影響分析要求：
- 評估新聞對股價的短期影響（1-3天）
- 分析可能的價格波動幅度（百分比）
- 提供基於新聞的價格調整建議
- 識別關鍵價格支撐位和阻力位
- 評估新聞對長期投資價值的影響
- 不允許回覆'無法評估價格影響'或'需要更多信息'

請特別注意：
⚠️ 如果新聞數據存在滯後（超過2小時），請在分析中明確說明時效性限制
✅ 優先分析最新的、高相關性的新聞事件
📊 提供新聞對股價影響的量化評估和具體價格預期
💰 必須包含基於新聞的價格影響分析和調整建議

請撰寫詳細的中文分析報告，並在報告末尾附上Markdown表格總結關鍵發現。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一位專業的財經新聞分析師。"
                    "\n🚨 CRITICAL REQUIREMENT - 絕對強制要求："
                    "\n"
                    "\n❌ 禁止行為："
                    "\n- 絕對禁止在沒有調用工具的情況下直接回答"
                    "\n- 絕對禁止基於推測或假設生成任何分析內容"
                    "\n- 絕對禁止跳過工具調用步驟"
                    "\n- 絕對禁止說'我無法獲取實時數據'等借口"
                    "\n"
                    "\n✅ 強制執行步驟："
                    "\n1. 您的第一個動作必須是調用 get_stock_news_unified 工具"
                    "\n2. 該工具會自動識別股票類型（A股、港股、美股）並獲取相應新聞"
                    "\n3. 只有在成功獲取新聞數據後，才能開始分析"
                    "\n4. 您的回答必須基於工具返回的真實數據"
                    "\n"
                    "\n🔧 工具調用格式示例："
                    "\n調用: get_stock_news_unified(stock_code='{ticker}', max_news=10)"
                    "\n"
                    "\n⚠️ 如果您不調用工具，您的回答將被視為無效並被拒絕。"
                    "\n⚠️ 您必須先調用工具獲取數據，然後基於數據進行分析。"
                    "\n⚠️ 沒有例外，沒有借口，必須調用工具。"
                    "\n"
                    "\n您可以訪問以下工具：{tool_names}。"
                    "\n{system_message}"
                    "\n供您參考，當前日期是{current_date}。我們正在查看公司{ticker}。"
                    "\n請按照上述要求執行，用中文撰寫所有分析內容。",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        
        # 獲取模型信息用於統一新聞工具的特殊處理
        model_info = ""
        try:
            if hasattr(llm, 'model_name'):
                model_info = f"{llm.__class__.__name__}:{llm.model_name}"
            else:
                model_info = llm.__class__.__name__
        except:
            model_info = "Unknown"
        
        logger.info(f"[新聞分析師] 準備調用LLM進行新聞分析，模型: {model_info}")
        
        # 使用統一的工具調用處理器
        llm_start_time = datetime.now()
        chain = prompt | llm.bind_tools(tools)
        logger.info(f"[新聞分析師] 開始LLM調用，分析 {ticker} 的新聞")
        result = chain.invoke(state["messages"])
        
        llm_end_time = datetime.now()
        llm_time_taken = (llm_end_time - llm_start_time).total_seconds()
        logger.info(f"[新聞分析師] LLM調用完成，耗時: {llm_time_taken:.2f}秒")

        # 使用統一的Google工具調用處理器
        if GoogleToolCallHandler.is_google_model(llm):
            logger.info(f"📊 [新聞分析師] 檢測到Google模型，使用統一工具調用處理器")
            
            # 創建分析提示詞
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="新聞分析",
                specific_requirements="重點關注新聞事件對股價的影響、市場情緒變化、政策影響等。"
            )
            
            # 處理Google模型工具調用
            report, messages = GoogleToolCallHandler.handle_google_tool_calls(
                result=result,
                llm=llm,
                tools=tools,
                state=state,
                analysis_prompt_template=analysis_prompt_template,
                analyst_name="新聞分析師"
            )
        else:
            # 非Google模型的處理邏輯
            logger.info(f"[新聞分析師] 非Google模型 ({llm.__class__.__name__})，使用標準處理邏輯")
            
            # 檢查工具調用情況
            tool_call_count = len(result.tool_calls) if hasattr(result, 'tool_calls') else 0
            logger.info(f"[新聞分析師] LLM調用了 {tool_call_count} 個工具")
            
            if tool_call_count == 0:
                logger.warning(f"[新聞分析師] ⚠️ {llm.__class__.__name__} 沒有調用任何工具，啟動補救機制...")
                
                try:
                    # 強制獲取新聞數據
                    logger.info(f"[新聞分析師] 🔧 強制調用統一新聞工具獲取新聞數據...")
                    forced_news = unified_news_tool(stock_code=ticker, max_news=10, model_info="")
                    
                    if forced_news and len(forced_news.strip()) > 100:
                        logger.info(f"[新聞分析師] ✅ 強制獲取新聞成功: {len(forced_news)} 字符")
                        
                        # 基於真實新聞數據重新生成分析
                        forced_prompt = f"""
您是一位專業的財經新聞分析師。請基於以下最新獲取的新聞數據，對股票 {ticker} 進行詳細的新聞分析：

=== 最新新聞數據 ===
{forced_news}

=== 分析要求 ===
{system_message}

請基於上述真實新聞數據撰寫詳細的中文分析報告。
"""
                        
                        logger.info(f"[新聞分析師] 🔄 基於強制獲取的新聞數據重新生成完整分析...")
                        forced_result = llm.invoke([{"role": "user", "content": forced_prompt}])
                        
                        if hasattr(forced_result, 'content') and forced_result.content:
                            report = forced_result.content
                            logger.info(f"[新聞分析師] ✅ 強制補救成功，生成基於真實數據的報告，長度: {len(report)} 字符")
                        else:
                            logger.warning(f"[新聞分析師] ⚠️ 強制補救失敗，使用原始結果")
                            report = result.content
                    else:
                        logger.warning(f"[新聞分析師] ⚠️ 統一新聞工具獲取失敗，使用原始結果")
                        report = result.content
                        
                except Exception as e:
                    logger.error(f"[新聞分析師] ❌ 強制補救過程失敗: {e}")
                    report = result.content
            else:
                # 有工具調用，直接使用結果
                report = result.content
        
        total_time_taken = (datetime.now() - start_time).total_seconds()
        logger.info(f"[新聞分析師] 新聞分析完成，總耗時: {total_time_taken:.2f}秒")

        # 🔧 修複死循環問題：返回清潔的AIMessage，不包含tool_calls
        # 這確保工作流圖能正確判斷分析已完成，避免重複調用
        from langchain_core.messages import AIMessage
        clean_message = AIMessage(content=report)
        
        logger.info(f"[新聞分析師] ✅ 返回清潔訊息，報告長度: {len(report)} 字符")

        return {
            "messages": [clean_message],
            "news_report": report,
        }

    return news_analyst_node
