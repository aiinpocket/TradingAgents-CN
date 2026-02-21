#!/usr/bin/env python3
"""
測試LLM工具調用機制的詳細調試腳本
模擬實際的LLM工具調用過程
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 添加項目根目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.realtime_news_utils import get_realtime_stock_news
from tradingagents.agents.utils.agent_utils import Toolkit

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def test_function_exists():
    """測試函數是否存在"""
    logger.info("========== 測試1: 函數存在性檢查 ==========")
    
    # 檢查直接導入的函數
    logger.info(f"get_realtime_stock_news 函數: {get_realtime_stock_news}")
    logger.info(f"函數類型: {type(get_realtime_stock_news)}")
    
    # 檢查Toolkit中的函數
    try:
        toolkit_func = getattr(Toolkit, 'get_realtime_stock_news', None)
        logger.info(f"Toolkit.get_realtime_stock_news: {toolkit_func}")
        logger.info(f"Toolkit函數類型: {type(toolkit_func)}")
    except Exception as e:
        logger.error(f"獲取Toolkit函數失敗: {e}")

def test_direct_call():
    """測試直接函數調用"""
    logger.info("========== 測試2: 直接函數調用 ==========")
    try:
        curr_date = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"調用參數: ticker='AAPL', date='{curr_date}'")
        
        start_time = datetime.now()
        result = get_realtime_stock_news('AAPL', curr_date)
        end_time = datetime.now()
        
        logger.info(f"調用成功，耗時: {(end_time - start_time).total_seconds():.2f}秒")
        logger.info(f"返回結果類型: {type(result)}")
        logger.info(f"返回結果長度: {len(result)} 字符")
        logger.info(f"結果前100字符: {result[:100]}...")
        return True, result
    except Exception as e:
        logger.error(f"直接調用失敗: {e}")
        import traceback
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return False, None

def test_toolkit_call():
    """測試Toolkit調用"""
    logger.info("========== 測試3: Toolkit調用 ==========")
    try:
        curr_date = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"調用參數: ticker='AAPL', date='{curr_date}'")
        
        start_time = datetime.now()
        result = Toolkit.get_realtime_stock_news('AAPL', curr_date)
        end_time = datetime.now()
        
        logger.info(f"Toolkit調用成功，耗時: {(end_time - start_time).total_seconds():.2f}秒")
        logger.info(f"返回結果類型: {type(result)}")
        logger.info(f"返回結果長度: {len(result)} 字符")
        logger.info(f"結果前100字符: {result[:100]}...")
        return True, result
    except Exception as e:
        logger.error(f"Toolkit調用失敗: {e}")
        import traceback
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return False, None

def test_toolkit_attributes():
    """測試Toolkit的屬性和方法"""
    logger.info("========== 測試4: Toolkit屬性檢查 ==========")
    
    # 列出Toolkit的所有屬性
    toolkit_attrs = [attr for attr in dir(Toolkit) if not attr.startswith('_')]
    logger.info(f"Toolkit可用屬性: {toolkit_attrs}")
    
    # 檢查是否有get_realtime_stock_news
    if 'get_realtime_stock_news' in toolkit_attrs:
        logger.info(" get_realtime_stock_news 在Toolkit中存在")
    else:
        logger.warning(" get_realtime_stock_news 不在Toolkit中")
    
    # 檢查Toolkit類型
    logger.info(f"Toolkit類型: {type(Toolkit)}")
    logger.info(f"Toolkit模塊: {Toolkit.__module__ if hasattr(Toolkit, '__module__') else 'N/A'}")

def simulate_llm_tool_call():
    """模擬LLM工具調用過程"""
    logger.info("========== 測試5: 模擬LLM工具調用 ==========")
    
    # 模擬LLM工具調用的參數格式
    tool_call_params = {
        "name": "get_realtime_stock_news",
        "arguments": {
            "ticker": "AAPL",
            "date": datetime.now().strftime('%Y-%m-%d')
        }
    }
    
    logger.info(f"模擬工具調用參數: {tool_call_params}")
    
    try:
        # 嘗試通過反射調用
        func_name = tool_call_params["name"]
        args = tool_call_params["arguments"]
        
        if hasattr(Toolkit, func_name):
            func = getattr(Toolkit, func_name)
            logger.info(f"找到函數: {func}")
            
            start_time = datetime.now()
            result = func(**args)
            end_time = datetime.now()
            
            logger.info(f"模擬LLM調用成功，耗時: {(end_time - start_time).total_seconds():.2f}秒")
            logger.info(f"返回結果長度: {len(result)} 字符")
            return True, result
        else:
            logger.error(f"函數 {func_name} 不存在於Toolkit中")
            return False, None
            
    except Exception as e:
        logger.error(f"模擬LLM調用失敗: {e}")
        import traceback
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return False, None

def main():
    """主測試函數"""
    logger.info("開始LLM工具調用機制詳細測試")
    logger.info("=" * 60)
    
    # 測試1: 函數存在性
    test_function_exists()
    
    # 測試2: 直接調用
    direct_success, direct_result = test_direct_call()
    
    # 測試3: Toolkit調用
    toolkit_success, toolkit_result = test_toolkit_call()
    
    # 測試4: Toolkit屬性檢查
    test_toolkit_attributes()
    
    # 測試5: 模擬LLM調用
    llm_success, llm_result = simulate_llm_tool_call()
    
    # 結果匯總
    logger.info("=" * 60)
    logger.info("========== 測試結果匯總 ==========")
    logger.info(f"直接函數調用: {' 成功' if direct_success else ' 失敗'}")
    logger.info(f"Toolkit調用: {' 成功' if toolkit_success else ' 失敗'}")
    logger.info(f"模擬LLM調用: {' 成功' if llm_success else ' 失敗'}")
    
    # 分析問題
    if direct_success and not toolkit_success:
        logger.warning(" 問題分析: Toolkit工具綁定存在問題")
    elif direct_success and not llm_success:
        logger.warning(" 問題分析: LLM工具調用機制存在問題")
    elif not direct_success:
        logger.warning(" 問題分析: 函數本身存在問題")
    else:
        logger.info(" 問題分析: 所有調用方式都成功")
    
    # 比較結果
    if direct_success and toolkit_success:
        if direct_result == toolkit_result:
            logger.info(" 直接調用和Toolkit調用結果一致")
        else:
            logger.warning(" 直接調用和Toolkit調用結果不一致")
            logger.info(f"直接調用結果長度: {len(direct_result)}")
            logger.info(f"Toolkit調用結果長度: {len(toolkit_result)}")

if __name__ == "__main__":
    main()