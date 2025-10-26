#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票數據API接口
提供便捷的股票數據獲取接口，支持完整的降級機制
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

# 添加dataflows目錄到路徑
dataflows_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataflows')
if dataflows_path not in sys.path:
    sys.path.append(dataflows_path)

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger

try:
    from stock_data_service import get_stock_data_service

    SERVICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ 股票數據服務不可用: {e}")
    SERVICE_AVAILABLE = False

def get_stock_info(stock_code: str) -> Dict[str, Any]:
    """
    獲取單個股票的基础信息
    
    Args:
        stock_code: 股票代碼（如 '000001'）
    
    Returns:
        Dict: 股票基础信息
    
    Example:
        >>> info = get_stock_info('000001')
        >>> print(info['name'])  # 平安銀行
    """
    if not SERVICE_AVAILABLE:
        return {
            'error': '股票數據服務不可用',
            'code': stock_code,
            'suggestion': '請檢查服務配置'
        }
    
    service = get_stock_data_service()
    result = service.get_stock_basic_info(stock_code)
    
    if result is None:
        return {
            'error': f'未找到股票{stock_code}的信息',
            'code': stock_code,
            'suggestion': '請檢查股票代碼是否正確'
        }
    
    return result

def get_all_stocks() -> List[Dict[str, Any]]:
    """
    獲取所有股票的基础信息
    
    Returns:
        List[Dict]: 所有股票的基础信息列表
    
    Example:
        >>> stocks = get_all_stocks()
        logger.info(f"共有{len(stocks)}只股票")
    """
    if not SERVICE_AVAILABLE:
        return [{
            'error': '股票數據服務不可用',
            'suggestion': '請檢查服務配置'
        }]
    
    service = get_stock_data_service()
    result = service.get_stock_basic_info()
    
    if result is None or (isinstance(result, dict) and 'error' in result):
        return [{
            'error': '無法獲取股票列表',
            'suggestion': '請檢查網絡連接和數據庫配置'
        }]
    
    return result if isinstance(result, list) else [result]

def get_stock_data(stock_code: str, start_date: str = None, end_date: str = None) -> str:
    """
    獲取股票歷史數據（帶降級機制）
    
    Args:
        stock_code: 股票代碼
        start_date: 開始日期（格式：YYYY-MM-DD），默認為30天前
        end_date: 結束日期（格式：YYYY-MM-DD），默認為今天
    
    Returns:
        str: 股票數據的字符串表示或錯誤信息
    
    Example:
        >>> data = get_stock_data('000001', '2024-01-01', '2024-01-31')
        >>> print(data)
    """
    if not SERVICE_AVAILABLE:
        return "❌ 股票數據服務不可用，請檢查服務配置"
    
    # 設置默認日期
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    service = get_stock_data_service()
    return service.get_stock_data_with_fallback(stock_code, start_date, end_date)

def search_stocks(keyword: str) -> List[Dict[str, Any]]:
    """
    根據關键詞搜索股票
    
    Args:
        keyword: 搜索關键詞（股票代碼或名稱的一部分）
    
    Returns:
        List[Dict]: 匹配的股票信息列表
    
    Example:
        >>> results = search_stocks('平安')
        >>> for stock in results:
        logger.info(f"{stock["code']}: {stock['name']}")
    """
    all_stocks = get_all_stocks()
    
    if not all_stocks or (len(all_stocks) == 1 and 'error' in all_stocks[0]):
        return all_stocks
    
    # 搜索匹配的股票
    matches = []
    keyword_lower = keyword.lower()
    
    for stock in all_stocks:
        if 'error' in stock:
            continue
            
        code = stock.get('code', '').lower()
        name = stock.get('name', '').lower()
        
        if keyword_lower in code or keyword_lower in name:
            matches.append(stock)
    
    return matches

def get_market_summary() -> Dict[str, Any]:
    """
    獲取市場概覽信息
    
    Returns:
        Dict: 市場統計信息
    
    Example:
        >>> summary = get_market_summary()
        logger.info(f"沪市股票數量: {summary["shanghai_count']}")
    """
    all_stocks = get_all_stocks()
    
    if not all_stocks or (len(all_stocks) == 1 and 'error' in all_stocks[0]):
        return {
            'error': '無法獲取市場數據',
            'suggestion': '請檢查網絡連接和數據庫配置'
        }
    
    # 統計市場信息
    shanghai_count = 0
    shenzhen_count = 0
    category_stats = {}
    
    for stock in all_stocks:
        if 'error' in stock:
            continue
            
        market = stock.get('market', '')
        category = stock.get('category', '未知')
        
        if market == '上海':
            shanghai_count += 1
        elif market == '深圳':
            shenzhen_count += 1
        
        category_stats[category] = category_stats.get(category, 0) + 1
    
    return {
        'total_count': len([s for s in all_stocks if 'error' not in s]),
        'shanghai_count': shanghai_count,
        'shenzhen_count': shenzhen_count,
        'category_stats': category_stats,
        'data_source': all_stocks[0].get('source', 'unknown') if all_stocks else 'unknown',
        'updated_at': datetime.now().isoformat()
    }

def check_service_status() -> Dict[str, Any]:
    """
    檢查服務狀態
    
    Returns:
        Dict: 服務狀態信息
    
    Example:
        >>> status = check_service_status()
        logger.info(f"MongoDB狀態: {status["mongodb_status']}")
    """
    if not SERVICE_AVAILABLE:
        return {
            'service_available': False,
            'error': '股票數據服務不可用',
            'suggestion': '請檢查服務配置和依賴'
        }
    
    service = get_stock_data_service()
    
    # 檢查MongoDB狀態
    mongodb_status = 'disconnected'
    if service.db_manager:
        try:
            # 嘗試檢查數據庫管理器的連接狀態
            if hasattr(service.db_manager, 'is_mongodb_available') and service.db_manager.is_mongodb_available():
                mongodb_status = 'connected'
            elif hasattr(service.db_manager, 'mongodb_client') and service.db_manager.mongodb_client:
                # 嘗試執行一個簡單的查詢來測試連接
                service.db_manager.mongodb_client.admin.command('ping')
                mongodb_status = 'connected'
            else:
                mongodb_status = 'unavailable'
        except Exception:
            mongodb_status = 'error'
    
    # 檢查統一數據接口狀態
    unified_api_status = 'unavailable'
    try:
        # 嘗試獲取一個股票信息來測試統一接口
        test_result = service.get_stock_basic_info('000001')
        if test_result and 'error' not in test_result:
            unified_api_status = 'available'
        else:
            unified_api_status = 'limited'
    except Exception:
        unified_api_status = 'error'
    
    return {
        'service_available': True,
        'mongodb_status': mongodb_status,
        'unified_api_status': unified_api_status,
        'data_sources_available': ['tushare', 'akshare', 'baostock'],
        'fallback_available': True,
        'checked_at': datetime.now().isoformat()
    }

# 便捷的別名函數
get_stock = get_stock_info  # 別名
get_stocks = get_all_stocks  # 別名
search = search_stocks  # 別名
status = check_service_status  # 別名

if __name__ == '__main__':
    # 簡單的命令行測試
    logger.debug(f"🔍 股票數據API測試")
    logger.info(f"=" * 50)
    
    # 檢查服務狀態
    logger.info(f"\n📊 服務狀態檢查:")
    status_info = check_service_status()
    for key, value in status_info.items():
        logger.info(f"  {key}: {value}")
    
    # 測試獲取單個股票信息
    logger.info(f"\n🏢 獲取平安銀行信息:")
    stock_info = get_stock_info('000001')
    if 'error' not in stock_info:
        logger.info(f"  代碼: {stock_info.get('code')}")
        logger.info(f"  名稱: {stock_info.get('name')}")
        logger.info(f"  市場: {stock_info.get('market')}")
        logger.info(f"  類別: {stock_info.get('category')}")
        logger.info(f"  數據源: {stock_info.get('source')}")
    else:
        logger.error(f"  錯誤: {stock_info.get('error')}")
    
    # 測試搜索功能
    logger.debug(f"\n🔍 搜索'平安'相關股票:")
    search_results = search_stocks('平安')
    for i, stock in enumerate(search_results[:3]):  # 只顯示前3個結果
        if 'error' not in stock:
            logger.info(f"  {i+1}. {stock.get('code')}")

    # 測試市場概覽
    logger.info(f"\n📈 市場概覽:")
    summary = get_market_summary()
    if 'error' not in summary:
        logger.info(f"  总股票數: {summary.get('total_count')}")
        logger.info(f"  沪市股票: {summary.get('shanghai_count')}")
        logger.info(f"  深市股票: {summary.get('shenzhen_count')}")
        logger.info(f"  數據源: {summary.get('data_source')}")
    else:
        logger.error(f"  錯誤: {summary.get('error')}")