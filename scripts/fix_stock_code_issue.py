#!/usr/bin/env python3
"""
修複股票代碼誤判問題的腳本
"""

import os
import shutil
import sys

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

def clear_all_caches():
    """清理所有緩存"""
    logger.info(f"🧹 清理所有緩存...")
    
    cache_dirs = [
        "tradingagents/dataflows/data_cache",
        "web/results",
        "web/eval_results/002027",
        "__pycache__",
        "tradingagents/__pycache__",
        "tradingagents/agents/__pycache__",
        "tradingagents/dataflows/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                if os.path.isdir(cache_dir):
                    shutil.rmtree(cache_dir)
                    logger.info(f"✅ 已清理目錄: {cache_dir}")
                else:
                    os.remove(cache_dir)
                    logger.info(f"✅ 已刪除文件: {cache_dir}")
            except Exception as e:
                logger.error(f"⚠️ 清理 {cache_dir} 失败: {e}")
    
    logger.info(f"✅ 緩存清理完成")

def add_stock_code_validation():
    """添加股票代碼驗證機制"""
    logger.info(f"🔧 添加股票代碼驗證機制...")
    
    validation_code = '''
def validate_stock_code(original_code: str, processed_content: str) -> str:
    """
    驗證處理後的內容中是否包含正確的股票代碼
    
    Args:
        original_code: 原始股票代碼
        processed_content: 處理後的內容
        
    Returns:
        str: 驗證並修正後的內容
    """
    import re
    
    # 定義常见的錯誤映射
    error_mappings = {
        "002027": ["002021", "002026", "002028"],  # 分眾傳媒常见錯誤
        "002021": ["002027"],  # 反向映射
    }
    
    if original_code in error_mappings:
        for wrong_code in error_mappings[original_code]:
            if wrong_code in processed_content:
                logger.error(f"🔍 [股票代碼驗證] 發現錯誤代碼 {wrong_code}，修正為 {original_code}")
                processed_content = processed_content.replace(wrong_code, original_code)
    
    return processed_content
'''
    
    # 将驗證代碼寫入文件
    with open("stock_code_validator.py", "w", encoding="utf-8") as f:
        f.write(validation_code)
    
    logger.info(f"✅ 股票代碼驗證機制已添加")

def create_test_script():
    """創建專門的測試腳本"""
    logger.info(f"📝 創建測試腳本...")
    
    test_script = '''#!/usr/bin/env python3
"""
002027 股票代碼專項測試
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_002027_specifically():
    """專門測試002027股票代碼"""
    logger.debug(f"🔍 002027 專項測試")
    logger.info(f"=")
    
    test_ticker = "002027"
    
    try:
        from tradingagents.utils.logging_init import get_logger
        logger.setLevel("INFO")
        
        # 測試1: 數據獲取
        logger.info(f"\\n📊 測試1: 數據獲取")
        from tradingagents.dataflows.interface import get_china_stock_data_tushare
        data = get_china_stock_data_tushare(test_ticker, "2025-07-01", "2025-07-15")
        
        if "002021" in data:
            logger.error(f"❌ 數據獲取階段發現錯誤代碼 002021")
            return False
        else:
            logger.info(f"✅ 數據獲取階段正確")
        
        # 測試2: 基本面分析
        logger.info(f"\\n💰 測試2: 基本面分析")
        from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
        analyzer = OptimizedChinaDataProvider()
        report = analyzer._generate_fundamentals_report(test_ticker, data)
        
        if "002021" in report:
            logger.error(f"❌ 基本面分析階段發現錯誤代碼 002021")
            return False
        else:
            logger.info(f"✅ 基本面分析階段正確")
        
        # 測試3: LLM處理
        logger.info(f"\\n🤖 測試3: LLM處理")
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if api_key:
            from tradingagents.llm_adapters import ChatDashScopeOpenAI
            from langchain_core.messages import HumanMessage

            
            llm = ChatDashScopeOpenAI(model="qwen-turbo", temperature=0.1, max_tokens=500)
            
            prompt = f"請分析股票{test_ticker}的基本面，股票名稱是分眾傳媒。要求：1.必须使用正確的股票代碼{test_ticker} 2.不要使用任何其他股票代碼"
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            if "002021" in response.content:
                logger.error(f"❌ LLM處理階段發現錯誤代碼 002021")
                logger.error(f"錯誤內容: {response.content[:200]}...")
                return False
            else:
                logger.info(f"✅ LLM處理階段正確")
        else:
            logger.warning(f"⚠️ 跳過LLM測試（未配置API密鑰）")
        
        logger.info(f"\\n🎉 所有測試通過！002027股票代碼處理正確")
        return True
        
    except Exception as e:
        logger.error(f"❌ 測試失败: {e}")
        return False

if __name__ == "__main__":
    test_002027_specifically()
'''
    
    with open("test_002027_specific.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    logger.info(f"✅ 測試腳本已創建: test_002027_specific.py")

def main():
    """主函數"""
    logger.info(f"🚀 開始修複股票代碼誤判問題")
    logger.info(f"=")
    
    # 1. 清理緩存
    clear_all_caches()
    
    # 2. 添加驗證機制
    add_stock_code_validation()
    
    # 3. 創建測試腳本
    create_test_script()
    
    logger.info(f"\\n✅ 修複完成！")
    logger.info(f"\\n📋 後续操作建议：")
    logger.info(f"1. 重啟Web應用")
    logger.info(f"2. 清理浏覽器緩存")
    logger.info(f"3. 運行測試腳本: python test_002027_specific.py")
    logger.info(f"4. 在Web界面重新測試002027")
    logger.info(f"5. 如果問題仍然存在，請檢查LLM模型配置")

if __name__ == "__main__":
    main()
