"""
測試Google工具處理器的改進
"""
import sys
import os
import logging
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler
from tradingagents.agents.utils.agent_utils import Toolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"google_tool_handler_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("test_google_tool_handler")

def test_google_tool_handler_improvements():
    """測試Google工具處理器的改進"""
    logger.info("開始測試Google工具處理器的改進...")
    
    # 創建Google模型
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.1)
    
    # 創建工具集
    tools = [Toolkit.get_stock_market_data_unified]
    
    # 測試場景1: 檢查是否為Google模型
    logger.info("測試場景1: 檢查是否為Google模型")
    try:
        is_google = GoogleToolCallHandler.is_google_model(llm)
        logger.info(f"場景1結果: 是否為Google模型: {is_google}")
    except Exception as e:
        logger.error(f"場景1異常: {e}")
    
    # 測試場景2: 模擬空工具調用的AIMessage
    logger.info("測試場景2: 模擬空工具調用的AIMessage")
    try:
        # 創建一個没有工具調用的AIMessage
        ai_message = AIMessage(content="我需要獲取股票數據來進行分析")
        
        state = {
            "messages": [HumanMessage(content="請分析贵州茅台(600519)的市場情况")],
            "trade_date": "2023-12-31",
            "company_of_interest": "贵州茅台",
            "ticker": "600519"
        }
        
        result, messages = GoogleToolCallHandler.handle_google_tool_calls(
            result=ai_message,
            llm=llm,
            tools=tools,
            state=state,
            analysis_prompt_template="請基於以上數據生成詳細的市場分析報告",
            analyst_name="市場分析師"
        )
        logger.info(f"場景2結果: {result[:100]}...")
    except Exception as e:
        logger.error(f"場景2異常: {e}")
    
    # 測試場景3: 模擬有工具調用的AIMessage
    logger.info("測試場景3: 模擬有工具調用的AIMessage")
    try:
        # 創建一個有工具調用的AIMessage
        ai_message = AIMessage(
            content="我需要獲取股票數據",
            tool_calls=[{
                'id': 'test_tool_call_1',
                'name': 'get_stock_market_data_unified',
                'args': {
                    'ticker': '600519',
                    'start_date': '2023-01-01',
                    'end_date': '2023-12-31'
                }
            }]
        )
        
        state = {
            "messages": [HumanMessage(content="請分析贵州茅台(600519)的市場情况")],
            "trade_date": "2023-12-31",
            "company_of_interest": "贵州茅台",
            "ticker": "600519"
        }
        
        result, messages = GoogleToolCallHandler.handle_google_tool_calls(
            result=ai_message,
            llm=llm,
            tools=tools,
            state=state,
            analysis_prompt_template="請基於以上數據生成詳細的市場分析報告",
            analyst_name="市場分析師"
        )
        logger.info(f"場景3結果: {result[:100]}...")
    except Exception as e:
        logger.error(f"場景3異常: {e}")
    
    logger.info("Google工具處理器改進測試完成")

if __name__ == "__main__":
    test_google_tool_handler_improvements()