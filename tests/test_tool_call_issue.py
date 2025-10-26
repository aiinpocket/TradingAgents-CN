#!/usr/bin/env python3
"""
測試LLM工具調用問題的詳細腳本
專門分析為什么LLM聲稱調用了工具但實际没有執行
"""

import os
import sys
import logging
from datetime import datetime

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('test_tool_call_issue.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_tool_call_mechanism():
    """測試工具調用機制"""
    logger.info("=" * 60)
    logger.info("開始測試LLM工具調用機制問題")
    logger.info("=" * 60)
    
    try:
        # 1. 導入必要模塊
        logger.info("1. 導入模塊...")
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.utils.realtime_news_utils import get_realtime_stock_news
        from langchain_core.messages import HumanMessage
        from langchain_core.tools import tool
        
        # 2. 創建LLM實例
        logger.info("2. 創建LLM實例...")
        llm = ChatDashScopeOpenAI(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=1000
        )
        logger.info(f"   LLM類型: {llm.__class__.__name__}")
        
        # 3. 創建Toolkit
        logger.info("3. 創建Toolkit...")
        toolkit = Toolkit()
        logger.info(f"   Toolkit創建成功")
        
        # 4. 獲取工具
        logger.info("4. 獲取工具...")
        realtime_news_tool = toolkit.get_realtime_stock_news
        logger.info(f"   工具名稱: {realtime_news_tool.name}")
        logger.info(f"   工具描述: {realtime_news_tool.description}")
        
        # 5. 绑定工具到LLM
        logger.info("5. 绑定工具到LLM...")
        llm_with_tools = llm.bind_tools([realtime_news_tool])
        logger.info(f"   工具绑定完成")
        
        # 6. 測試工具調用
        logger.info("6. 測試工具調用...")
        test_message = HumanMessage(
            content="請調用get_realtime_stock_news工具獲取000001.SZ的最新新聞"
        )
        
        logger.info("   開始LLM調用...")
        result = llm_with_tools.invoke([test_message])
        logger.info("   LLM調用完成")
        
        # 7. 分析結果
        logger.info("7. 分析結果...")
        logger.info(f"   結果類型: {type(result)}")
        logger.info(f"   是否有tool_calls屬性: {hasattr(result, 'tool_calls')}")
        
        if hasattr(result, 'tool_calls'):
            tool_calls = result.tool_calls
            logger.info(f"   工具調用數量: {len(tool_calls)}")
            
            if len(tool_calls) > 0:
                logger.info("   工具調用詳情:")
                for i, call in enumerate(tool_calls):
                    logger.info(f"     調用 {i+1}:")
                    logger.info(f"       類型: {type(call)}")
                    if hasattr(call, 'name'):
                        logger.info(f"       名稱: {call.name}")
                    if hasattr(call, 'args'):
                        logger.info(f"       參數: {call.args}")
                    if isinstance(call, dict):
                        logger.info(f"       字典內容: {call}")
                        
                # 8. 嘗試手動執行工具調用
                logger.info("8. 嘗試手動執行工具調用...")
                for i, call in enumerate(tool_calls):
                    try:
                        logger.info(f"   執行工具調用 {i+1}...")
                        
                        # 獲取參數
                        if hasattr(call, 'args'):
                            args = call.args
                        elif isinstance(call, dict) and 'args' in call:
                            args = call['args']
                        else:
                            logger.error(f"     無法獲取參數: {call}")
                            continue
                            
                        logger.info(f"     參數: {args}")
                        
                        # 執行工具
                        if 'ticker' in args:
                            ticker = args['ticker']
                            logger.info(f"     調用 get_realtime_stock_news(ticker='{ticker}')")
                            
                            # 直接調用函數
                            news_result = get_realtime_stock_news(ticker)
                            logger.info(f"     函數調用成功，結果長度: {len(news_result)} 字符")
                            logger.info(f"     結果前100字符: {news_result[:100]}...")
                            
                        else:
                            logger.error(f"     參數中缺少ticker: {args}")
                            
                    except Exception as e:
                        logger.error(f"     工具執行失败: {e}")
                        import traceback
                        logger.error(f"     錯誤詳情: {traceback.format_exc()}")
            else:
                logger.warning("   LLM没有調用任何工具")
        else:
            logger.warning("   結果没有tool_calls屬性")
            
        # 9. 檢查響應內容
        logger.info("9. 檢查響應內容...")
        if hasattr(result, 'content'):
            content = result.content
            logger.info(f"   響應內容長度: {len(content)} 字符")
            logger.info(f"   響應內容前200字符: {content[:200]}...")
        else:
            logger.warning("   結果没有content屬性")
            
        logger.info("=" * 60)
        logger.info("測試完成")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"測試失败: {e}")
        import traceback
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_tool_call_mechanism()