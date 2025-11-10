#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票數據API接口
提供簡單易用的股票數據獲取接口，內置完整的降級機制
"""

from typing import Dict, List, Optional, Any
from .stock_data_service import get_stock_data_service

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

def get_stock_info(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    獲取單個股票的基础信息
    
    Args:
        stock_code: 股票代碼（如 '000001'）
    
    Returns:
        Dict: 股票信息，包含code, name, market, category等字段
              如果獲取失败，返回包含error字段的字典
    
    Example:
        >>> info = get_stock_info('000001')
        >>> print(info['name'])  # 輸出: 平安銀行
    """
    service = get_stock_data_service()
    return service.get_stock_basic_info(stock_code)

def get_all_stocks() -> List[Dict[str, Any]]:
    """
    獲取所有股票列表
    
    Returns:
        List[Dict]: 股票列表，每個元素包含股票基础信息
                   如果獲取失败，返回包含error字段的字典
    
    Example:
        >>> stocks = get_all_stocks()
        logger.info(f"共有{len(stocks)}只股票")
    """
    service = get_stock_data_service()
    result = service.get_stock_basic_info()
    
    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and 'error' in result:
        return [result]  # 返回錯誤信息
    else:
        return []

def get_stock_data(stock_code: str, start_date: str, end_date: str) -> str:
    """
    獲取股票歷史數據（帶降級機制）
    
    Args:
        stock_code: 股票代碼
        start_date: 開始日期 'YYYY-MM-DD'
        end_date: 結束日期 'YYYY-MM-DD'
    
    Returns:
        str: 格式化的股票數據報告
    
    Example:
        >>> data = get_stock_data('000001', '2024-01-01', '2024-01-31')
        >>> print(data)
    """
    service = get_stock_data_service()
    return service.get_stock_data_with_fallback(stock_code, start_date, end_date)

def search_stocks_by_name(name: str) -> List[Dict[str, Any]]:
    """
    根據股票名稱搜索股票（需要MongoDB支持）
    
    Args:
        name: 股票名稱關键詞
    
    Returns:
        List[Dict]: 匹配的股票列表
    
    Example:
        >>> results = search_stocks_by_name('銀行')
        >>> for stock in results:
        logger.info(f"{stock['code']}: {stock['name']}")
    """
    # 這個功能需要MongoDB支持，暂時通過原有方式實現
    try:
        from ..examples.stock_query_examples import EnhancedStockQueryService

        service = EnhancedStockQueryService()
        return service.query_stocks_by_name(name)
    except Exception as e:
        return [{'error': f'名稱搜索功能不可用: {str(e)}'}]

def check_data_sources() -> Dict[str, Any]:
    """
    檢查數據源狀態
    
    Returns:
        Dict: 各數據源的可用狀態
    
    Example:
        >>> status = check_data_sources()
        logger.info(f"MongoDB可用: {status['mongodb_available']}")
        logger.info(f"統一數據接口可用: {status['unified_api_available']}")
    """
    service = get_stock_data_service()
    
    return {
        'mongodb_available': service.db_manager is not None and service.db_manager.mongodb_db is not None,
        'unified_api_available': True,  # 統一接口总是可用
        'enhanced_fetcher_available': True,  # 這個通常都可用
        'fallback_mode': service.db_manager is None or service.db_manager.mongodb_db is None,
        'recommendation': (
            "所有數據源正常" if service.db_manager and service.db_manager.mongodb_db 
            else "建議配置MongoDB以獲得最佳性能，當前使用統一數據接口降級模式"
        )
    }