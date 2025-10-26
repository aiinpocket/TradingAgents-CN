#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票查詢示例（增强版）
演示如何使用新的股票數據服務，支持完整的降級機制
"""

import sys
import os

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from tradingagents.api.stock_api import (
        get_stock_info, get_all_stocks, get_stock_data,
        search_stocks, get_market_summary, check_service_status
    )
    API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ 新API不可用，使用傳統方式: {e}")
    API_AVAILABLE = False
    # 回退到傳統方式
    from tradingagents.dataflows.database_manager import get_database_manager

from datetime import datetime, timedelta
import pandas as pd

def demo_service_status():
    """
    演示服務狀態檢查
    """
    logger.info(f"\n=== 服務狀態檢查 ===")
    
    if not API_AVAILABLE:
        logger.error(f"❌ 新API不可用，跳過狀態檢查")
        return
    
    status = check_service_status()
    logger.info(f"📊 當前服務狀態:")
    
    for key, value in status.items():
        if key == 'service_available':
            icon = "✅" if value else "❌"
            logger.info(f"  {icon} 服務可用性: {value}")
        elif key == 'mongodb_status':
            icon = "✅" if value == 'connected' else "⚠️" if value == 'disconnected' else "❌"
            logger.info(f"  {icon} MongoDB狀態: {value}")
        elif key == 'unified_api_status':
            icon = "✅" if value == 'available' else "⚠️" if value == 'limited' else "❌"
            logger.info(f"  {icon} 統一數據接口狀態: {value}")
        else:
            logger.info(f"  📋 {key}: {value}")

def demo_single_stock_query():
    """
    演示單個股票查詢（帶降級機制）
    """
    logger.info(f"\n=== 單個股票查詢示例 ===")
    
    stock_codes = ['000001', '000002', '600000', '300001']
    
    for stock_code in stock_codes:
        logger.debug(f"\n🔍 查詢股票 {stock_code}:")
        
        if API_AVAILABLE:
            # 使用新API
            stock_info = get_stock_info(stock_code)
            
            if 'error' in stock_info:
                logger.error(f"  ❌ {stock_info['error']}")
                if 'suggestion' in stock_info:
                    logger.info(f"  💡 {stock_info['suggestion']}")
            else:
                logger.info(f"  ✅ 代碼: {stock_info.get('code')}")
                logger.info(f"  📝 名稱: {stock_info.get('name')}")
                logger.info(f"  🏢 市場: {stock_info.get('market')}")
                logger.info(f"  📊 類別: {stock_info.get('category')}")
                logger.info(f"  🔗 數據源: {stock_info.get('source')}")
                logger.info(f"  🕒 更新時間: {stock_info.get('updated_at', 'N/A')[:19]}")
        else:
            # 使用傳統方式
            logger.warning(f"  ⚠️ 使用傳統查詢方式")
            db_manager = get_database_manager()
            if db_manager.is_mongodb_available():
                try:
                    collection = db_manager.mongodb_db['stock_basic_info']
                    stock = collection.find_one({"code": stock_code})
                    if stock:
                        logger.info(f"  ✅ 找到: {stock.get('name')}")
                    else:
                        logger.error(f"  ❌ 未找到股票信息")
                except Exception as e:
                    logger.error(f"  ❌ 查詢失败: {e}")
            else:
                logger.error(f"  ❌ 數據庫連接失败")

def demo_stock_search():
    """
    演示股票搜索功能
    """
    logger.info(f"\n=== 股票搜索示例 ===")
    
    if not API_AVAILABLE:
        logger.error(f"❌ 新API不可用，跳過搜索演示")
        return
    
    keywords = ['平安', '銀行', '科技', '000001']
    
    for keyword in keywords:
        logger.debug(f"\n🔍 搜索關键詞: '{keyword}'")
        
        results = search_stocks(keyword)
        
        if not results or (len(results) == 1 and 'error' in results[0]):
            logger.error(f"  ❌ 未找到匹配的股票")
            if results and 'error' in results[0]:
                logger.info(f"  💡 {results[0].get('suggestion', '')}")
        else:
            logger.info(f"  ✅ 找到 {len(results)} 只匹配的股票:")
            for i, stock in enumerate(results[:5], 1):  # 只顯示前5個
                if 'error' not in stock:
                    logger.info(f"    {i}. {stock.get('code'):6s} - {stock.get('name'):15s} [{stock.get('market')}]")

def demo_market_overview():
    """
    演示市場概覽功能
    """
    logger.info(f"\n=== 市場概覽示例 ===")
    
    if not API_AVAILABLE:
        logger.error(f"❌ 新API不可用，跳過市場概覽")
        return
    
    summary = get_market_summary()
    
    if 'error' in summary:
        logger.error(f"❌ {summary['error']}")
        if 'suggestion' in summary:
            logger.info(f"💡 {summary['suggestion']}")
    else:
        logger.info(f"📊 市場統計信息:")
        logger.info(f"  📈 总股票數: {summary.get('total_count', 0):,}")
        logger.info(f"  🏢 沪市股票: {summary.get('shanghai_count', 0):,}")
        logger.info(f"  🏢 深市股票: {summary.get('shenzhen_count', 0):,}")
        logger.info(f"  🔗 數據源: {summary.get('data_source', 'unknown')}")
        
        # 顯示類別統計
        category_stats = summary.get('category_stats', {})
        if category_stats:
            logger.info(f"\n📋 按類別統計:")
            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {category}: {count:,} 只")

def demo_stock_data_query():
    """
    演示股票歷史數據查詢（帶降級機制）
    """
    logger.info(f"\n=== 股票歷史數據查詢示例 ===")
    
    if not API_AVAILABLE:
        logger.error(f"❌ 新API不可用，跳過歷史數據查詢")
        return
    
    stock_code = '000001'
    logger.info(f"📊 獲取股票 {stock_code} 的歷史數據...")
    
    # 獲取最近30天的數據
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    result = get_stock_data(stock_code, start_date, end_date)
    
    # 顯示結果（截取前500個字符以避免輸出過長）
    if len(result) > 500:
        logger.info(f"📋 數據獲取結果（前500字符）:")
        print(result[:500] + "...")
    else:
        logger.info(f"📋 數據獲取結果:")
        print(result)

def demo_fallback_mechanism():
    """
    演示降級機制
    """
    logger.info(f"\n=== 降級機制演示 ===")
    
    if not API_AVAILABLE:
        logger.error(f"❌ 新API不可用，無法演示降級機制")
        return
    
    logger.info(f"🔄 降級機制說明:")
    logger.info(f"  1. 優先從MongoDB獲取數據")
    logger.info(f"  2. MongoDB不可用時，降級到Tushare數據接口")
    logger.info(f"  3. Tushare數據接口不可用時，提供基础的降級數據")
    logger.info(f"  4. 獲取到的數據會自動緩存到MongoDB（如果可用）")
    
    # 測試一個可能不存在的股票代碼
    test_code = '999999'
    logger.info(f"\n🧪 測試不存在的股票代碼 {test_code}:")
    
    result = get_stock_info(test_code)
    if 'error' in result:
        logger.error(f"  ❌ 預期的錯誤: {result['error']}")
    else:
        logger.info(f"  ✅ 意外獲得數據: {result.get('name')}")



def main():
    """
    主函數
    """
    logger.info(f"🚀 股票查詢示例程序（增强版）")
    logger.info(f"=")
    
    if API_AVAILABLE:
        logger.info(f"✅ 使用新的股票數據API（支持降級機制）")
    else:
        logger.warning(f"⚠️ 新API不可用，使用傳統查詢方式")
    
    try:
        # 執行各種查詢示例
        demo_service_status()
        demo_single_stock_query()
        demo_stock_search()
        demo_market_overview()
        demo_stock_data_query()
        demo_fallback_mechanism()
        
        logger.info(f"\n")
        logger.info(f"✅ 所有查詢示例執行完成")
        logger.info(f"\n💡 使用建议:")
        logger.info(f"  1. 確保MongoDB已正確配置以獲得最佳性能")
        logger.info(f"  2. 網絡連接正常時可以使用Tushare數據接口作為备選")
        logger.info(f"  3. 定期運行數據同步腳本更新股票信息")
        
    except KeyboardInterrupt:
        logger.warning(f"\n⚠️ 用戶中斷程序")
    except Exception as e:
        logger.error(f"\n❌ 程序執行出錯: {e}")
        import traceback

        traceback.print_exc()

if __name__ == "__main__":
    main()