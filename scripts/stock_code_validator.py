

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

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


    
    # 定義常見的錯誤映射
    error_mappings = {
        "002027": ["002021", "002026", "002028"],  # 分眾傳媒常見錯誤
        "002021": ["002027"],  # 反向映射
    }
    
    if original_code in error_mappings:
        for wrong_code in error_mappings[original_code]:
            if wrong_code in processed_content:
                logger.error(f"🔍 [股票代碼驗證] 發現錯誤代碼 {wrong_code}，修正為 {original_code}")
                processed_content = processed_content.replace(wrong_code, original_code)
    
    return processed_content
