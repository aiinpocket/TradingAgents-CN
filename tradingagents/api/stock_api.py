#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票資料 API 介面
提供便捷的美股資料取得介面，支援完整的降級機制
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# 將 dataflows 目錄加入路徑
dataflows_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataflows')
if dataflows_path not in sys.path:
    sys.path.append(dataflows_path)

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger('agents')

try:
    from stock_data_service import get_stock_data_service

    SERVICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"股票資料服務不可用: {e}")
    SERVICE_AVAILABLE = False


def get_stock_info(stock_code: str) -> Dict[str, Any]:
    """
    取得單檔股票的基礎資訊

    Args:
        stock_code: 股票代碼（如 'AAPL'、'MSFT'）

    Returns:
        Dict: 股票基礎資訊

    Example:
        >>> info = get_stock_info('AAPL')
        >>> print(info['name'])  # Apple Inc.
    """
    if not SERVICE_AVAILABLE:
        return {
            'error': '股票資料服務不可用',
            'code': stock_code,
            'suggestion': '請檢查服務配置'
        }

    service = get_stock_data_service()
    result = service.get_stock_basic_info(stock_code)

    if result is None:
        return {
            'error': f'未找到股票 {stock_code} 的資訊',
            'code': stock_code,
            'suggestion': '請檢查股票代碼是否正確'
        }

    return result


def get_all_stocks() -> List[Dict[str, Any]]:
    """
    取得所有股票的基礎資訊

    Returns:
        List[Dict]: 所有股票的基礎資訊列表

    Example:
        >>> stocks = get_all_stocks()
        >>> logger.info(f"共有 {len(stocks)} 檔股票")
    """
    if not SERVICE_AVAILABLE:
        return [{
            'error': '股票資料服務不可用',
            'suggestion': '請檢查服務配置'
        }]

    service = get_stock_data_service()
    result = service.get_stock_basic_info()

    if result is None or (isinstance(result, dict) and 'error' in result):
        return [{
            'error': '無法取得股票列表',
            'suggestion': '請檢查網路連線和資料庫配置'
        }]

    return result if isinstance(result, list) else [result]


def get_stock_data(stock_code: str, start_date: str = None, end_date: str = None) -> str:
    """
    取得股票歷史資料（帶降級機制）

    Args:
        stock_code: 股票代碼（如 'AAPL'、'TSLA'）
        start_date: 開始日期（格式：YYYY-MM-DD），預設為 30 天前
        end_date: 結束日期（格式：YYYY-MM-DD），預設為今天

    Returns:
        str: 股票資料的字串表示或錯誤訊息

    Example:
        >>> data = get_stock_data('AAPL', '2024-01-01', '2024-01-31')
        >>> print(data)
    """
    if not SERVICE_AVAILABLE:
        return "股票資料服務不可用，請檢查服務配置"

    # 設定預設日期
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    service = get_stock_data_service()
    return service.get_stock_data_with_fallback(stock_code, start_date, end_date)


def search_stocks(keyword: str) -> List[Dict[str, Any]]:
    """
    根據關鍵詞搜尋股票

    Args:
        keyword: 搜尋關鍵詞（股票代碼或名稱的一部分）

    Returns:
        List[Dict]: 符合條件的股票資訊列表

    Example:
        >>> results = search_stocks('AAPL')
        >>> for stock in results:
        ...     logger.info(f"{stock['code']}: {stock['name']}")
    """
    all_stocks = get_all_stocks()

    if not all_stocks or (len(all_stocks) == 1 and 'error' in all_stocks[0]):
        return all_stocks

    # 搜尋符合條件的股票
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
    取得美股市場概覽資訊

    Returns:
        Dict: 市場統計資訊

    Example:
        >>> summary = get_market_summary()
        >>> logger.info(f"股票總數: {summary['total_count']}")
    """
    all_stocks = get_all_stocks()

    if not all_stocks or (len(all_stocks) == 1 and 'error' in all_stocks[0]):
        return {
            'error': '無法取得市場資料',
            'suggestion': '請檢查網路連線和資料庫配置'
        }

    # 統計市場資訊（依交易所分類）
    exchange_stats = {}
    category_stats = {}

    for stock in all_stocks:
        if 'error' in stock:
            continue

        exchange = stock.get('exchange', stock.get('market', 'unknown'))
        category = stock.get('category', 'unknown')

        exchange_stats[exchange] = exchange_stats.get(exchange, 0) + 1
        category_stats[category] = category_stats.get(category, 0) + 1

    return {
        'total_count': len([s for s in all_stocks if 'error' not in s]),
        'exchange_stats': exchange_stats,
        'category_stats': category_stats,
        'data_source': all_stocks[0].get('source', 'unknown') if all_stocks else 'unknown',
        'updated_at': datetime.now().isoformat()
    }


def check_service_status() -> Dict[str, Any]:
    """
    檢查服務狀態

    Returns:
        Dict: 服務狀態資訊

    Example:
        >>> status = check_service_status()
        >>> logger.info(f"MongoDB 狀態: {status['mongodb_status']}")
    """
    if not SERVICE_AVAILABLE:
        return {
            'service_available': False,
            'error': '股票資料服務不可用',
            'suggestion': '請檢查服務配置和依賴'
        }

    service = get_stock_data_service()

    # 檢查 MongoDB 狀態
    mongodb_status = 'disconnected'
    if service.db_manager:
        try:
            # 嘗試檢查資料庫管理器的連線狀態
            if hasattr(service.db_manager, 'is_mongodb_available') and service.db_manager.is_mongodb_available():
                mongodb_status = 'connected'
            elif hasattr(service.db_manager, 'mongodb_client') and service.db_manager.mongodb_client:
                # 嘗試執行一個簡單的查詢來測試連線
                service.db_manager.mongodb_client.admin.command('ping')
                mongodb_status = 'connected'
            else:
                mongodb_status = 'unavailable'
        except Exception:
            mongodb_status = 'error'

    # 檢查統一資料介面狀態
    unified_api_status = 'unavailable'
    try:
        # 嘗試取得一檔股票資訊來測試統一介面
        test_result = service.get_stock_basic_info('AAPL')
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
        'data_sources_available': ['yfinance', 'finnhub'],
        'fallback_available': True,
        'checked_at': datetime.now().isoformat()
    }


# 便捷的別名函式
get_stock = get_stock_info
get_stocks = get_all_stocks
search = search_stocks
status = check_service_status

if __name__ == '__main__':
    # 簡易命令列測試
    logger.debug("股票資料 API 測試")
    logger.info("=" * 50)

    # 檢查服務狀態
    logger.info("\n服務狀態檢查:")
    status_info = check_service_status()
    for key, value in status_info.items():
        logger.info(f"  {key}: {value}")

    # 測試取得單檔股票資訊
    logger.info("\n取得 AAPL 股票資訊:")
    stock_info = get_stock_info('AAPL')
    if 'error' not in stock_info:
        logger.info(f"  代碼: {stock_info.get('code')}")
        logger.info(f"  名稱: {stock_info.get('name')}")
        logger.info(f"  交易所: {stock_info.get('exchange')}")
        logger.info(f"  類別: {stock_info.get('category')}")
        logger.info(f"  資料來源: {stock_info.get('source')}")
    else:
        logger.error(f"  錯誤: {stock_info.get('error')}")

    # 測試搜尋功能
    logger.debug("\n搜尋 'AAPL' 相關股票:")
    search_results = search_stocks('AAPL')
    for i, stock in enumerate(search_results[:3]):
        if 'error' not in stock:
            logger.info(f"  {i+1}. {stock.get('code')}")

    # 測試市場概覽
    logger.info("\n市場概覽:")
    summary = get_market_summary()
    if 'error' not in summary:
        logger.info(f"  股票總數: {summary.get('total_count')}")
        logger.info(f"  交易所分布: {summary.get('exchange_stats')}")
        logger.info(f"  資料來源: {summary.get('data_source')}")
    else:
        logger.error(f"  錯誤: {summary.get('error')}")
