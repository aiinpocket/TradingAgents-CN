#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一的股票數據獲取服務
實現 MongoDB -> Yahoo Finance 數據接口的完整降級機制
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

try:
    from tradingagents.config.database_manager import get_database_manager
    DATABASE_MANAGER_AVAILABLE = True
except ImportError:
    DATABASE_MANAGER_AVAILABLE = False

try:
    import sys
    import os
    # 添加utils目錄到路徑
    utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'utils')
    if utils_path not in sys.path:
        sys.path.append(utils_path)
    from enhanced_stock_list_fetcher import enhanced_fetch_stock_list
    ENHANCED_FETCHER_AVAILABLE = True
except ImportError:
    ENHANCED_FETCHER_AVAILABLE = False

logger = logging.getLogger(__name__)

class StockDataService:
    """
    統一的股票數據獲取服務
    實現完整的降級機制：MongoDB -> Yahoo Finance -> 緩存 -> 錯誤處理
    """
    
    def __init__(self):
        self.db_manager = None
        self._init_services()
    
    def _init_services(self):
        """初始化服務"""
        # 嘗試初始化數據庫管理器
        if DATABASE_MANAGER_AVAILABLE:
            try:
                self.db_manager = get_database_manager()
                if self.db_manager.is_mongodb_available():
                    logger.info(f"✅ MongoDB連接成功")
                else:
                    logger.error(f"⚠️ MongoDB連接失敗，將使用其他數據源")
            except Exception as e:
                logger.error(f"⚠️ 數據庫管理器初始化失敗: {e}")
                self.db_manager = None
    
    def get_stock_basic_info(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """
        獲取股票基礎信息（單個股票或全部股票）
        
        Args:
            stock_code: 股票代碼，如果為None則返回所有股票
        
        Returns:
            Dict: 股票基礎信息
        """
        logger.info(f"📊 獲取股票基礎信息: {stock_code or '全部股票'}")
        
        # 1. 優先從MongoDB獲取
        if self.db_manager and self.db_manager.is_mongodb_available():
            try:
                result = self._get_from_mongodb(stock_code)
                if result:
                    logger.info(f"✅ 從MongoDB獲取成功: {len(result) if isinstance(result, list) else 1}條記錄")
                    return result
            except Exception as e:
                logger.error(f"⚠️ MongoDB查詢失敗: {e}")
        
        # 2. 降級到增強獲取器
        logger.info(f"🔄 MongoDB不可用，降級到增強獲取器")
        if ENHANCED_FETCHER_AVAILABLE:
            try:
                result = self._get_from_enhanced_fetcher(stock_code)
                if result:
                    logger.info(f"✅ 從增強獲取器獲取成功: {len(result) if isinstance(result, list) else 1}條記錄")
                    # 嘗試緩存到MongoDB（如果可用）
                    self._cache_to_mongodb(result)
                    return result
            except Exception as e:
                logger.error(f"⚠️ 增強獲取器查詢失敗: {e}")
        
        # 3. 最後的降級方案
        logger.error(f"❌ 所有數據源都不可用")
        return self._get_fallback_data(stock_code)
    
    def _get_from_mongodb(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """從MongoDB獲取數據"""
        try:
            mongodb_client = self.db_manager.get_mongodb_client()
            if not mongodb_client:
                return None

            db = mongodb_client[self.db_manager.mongodb_config["database"]]
            collection = db['stock_basic_info']

            if stock_code:
                # 獲取單個股票
                result = collection.find_one({'code': stock_code})
                return result if result else None
            else:
                # 獲取所有股票
                cursor = collection.find({})
                results = list(cursor)
                return results if results else None

        except Exception as e:
            logger.error(f"MongoDB查詢失敗: {e}")
            return None
    
    def _get_from_enhanced_fetcher(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """從增強獲取器獲取數據"""
        try:
            if stock_code:
                # 獲取單個股票信息 - 使用增強獲取器獲取所有股票然後篩選
                stock_df = enhanced_fetch_stock_list(
                    type_='stock',
                    enable_server_failover=True,
                    max_retries=3
                )
                
                if stock_df is not None and not stock_df.empty:
                    # 查找指定股票代碼
                    stock_row = stock_df[stock_df['code'] == stock_code]
                    if not stock_row.empty:
                        row = stock_row.iloc[0]
                        return {
                            'code': row.get('code', stock_code),
                            'name': row.get('name', ''),
                            'market': row.get('market', self._get_market_name(stock_code)),
                            'category': row.get('category', self._get_stock_category(stock_code)),
                            'source': 'enhanced_fetcher',
                            'updated_at': datetime.now().isoformat()
                        }
                    else:
                        # 如果沒找到，返回基本信息
                        return {
                            'code': stock_code,
                            'name': '',
                            'market': self._get_market_name(stock_code),
                            'category': self._get_stock_category(stock_code),
                            'source': 'enhanced_fetcher',
                            'updated_at': datetime.now().isoformat()
                        }
            else:
                # 獲取所有股票列表
                stock_df = enhanced_fetch_stock_list(
                    type_='stock',
                    enable_server_failover=True,
                    max_retries=3
                )
                
                if stock_df is not None and not stock_df.empty:
                    # 轉換為字典列表
                    results = []
                    for _, row in stock_df.iterrows():
                        results.append({
                            'code': row.get('code', ''),
                            'name': row.get('name', ''),
                            'market': row.get('market', ''),
                            'category': row.get('category', ''),
                            'source': 'enhanced_fetcher',
                            'updated_at': datetime.now().isoformat()
                        })
                    return results
                    
        except Exception as e:
            logger.error(f"增強獲取器查詢失敗: {e}")
            return None
    
    def _cache_to_mongodb(self, data: Any) -> bool:
        """將數據緩存到MongoDB"""
        if not self.db_manager or not self.db_manager.mongodb_db:
            return False
        
        try:
            collection = self.db_manager.mongodb_db['stock_basic_info']
            
            if isinstance(data, list):
                # 批量插入
                for item in data:
                    collection.update_one(
                        {'code': item['code']},
                        {'$set': item},
                        upsert=True
                    )
                logger.info(f"💾 已緩存{len(data)}條記錄到MongoDB")
            elif isinstance(data, dict):
                # 單條插入
                collection.update_one(
                    {'code': data['code']},
                    {'$set': data},
                    upsert=True
                )
                logger.info(f"💾 已緩存股票{data['code']}到MongoDB")
            
            return True
            
        except Exception as e:
            logger.error(f"緩存到MongoDB失敗: {e}")
            return False
    
    def _get_fallback_data(self, stock_code: str = None) -> Dict[str, Any]:
        """最後的降級數據"""
        if stock_code:
            return {
                'code': stock_code,
                'name': f'股票{stock_code}',
                'market': self._get_market_name(stock_code),
                'category': '未知',
                'source': 'fallback',
                'updated_at': datetime.now().isoformat(),
                'error': '所有數據源都不可用'
            }
        else:
            return {
                'error': '無法獲取股票列表，請檢查網絡連接和數據庫配置',
                'suggestion': '請確保MongoDB已配置或網絡連接正常以存取數據服務'
            }
    
    def _get_market_name(self, stock_code: str) -> str:
        """根據股票代碼判斷市場"""
        if stock_code.startswith(('60', '68', '90')):
            return '上海'
        elif stock_code.startswith(('00', '30', '20')):
            return '深圳'
        else:
            return '未知'
    
    def _get_stock_category(self, stock_code: str) -> str:
        """根據股票代碼判斷類別"""
        if stock_code.startswith('60'):
            return '滬市主板'
        elif stock_code.startswith('68'):
            return '科創板'
        elif stock_code.startswith('00'):
            return '深市主板'
        elif stock_code.startswith('30'):
            return '創業板'
        elif stock_code.startswith('20'):
            return '深市B股'
        else:
            return '其他'
    
    def get_stock_data_with_fallback(self, stock_code: str, start_date: str, end_date: str) -> str:
        """
        獲取股票數據（帶降級機制）
        """
        logger.info(f"獲取股票數據: {stock_code} ({start_date} 到 {end_date})")

        # 確保股票基礎資訊可用
        stock_info = self.get_stock_basic_info(stock_code)
        if stock_info and 'error' in stock_info:
            return f"無法獲取股票 {stock_code} 的基礎資訊: {stock_info.get('error', '未知錯誤')}"

        # 透過資料庫管理器獲取數據
        try:
            if self.db_manager:
                return self.db_manager.get_stock_data(stock_code, start_date, end_date)
            return f"數據服務不可用，請檢查資料庫配置"
        except Exception as e:
            return f"獲取股票數據失敗: {str(e)}"

# 全局服務實例
_stock_data_service = None

def get_stock_data_service() -> StockDataService:
    """獲取股票數據服務實例（單例模式）"""
    global _stock_data_service
    if _stock_data_service is None:
        _stock_data_service = StockDataService()
    return _stock_data_service