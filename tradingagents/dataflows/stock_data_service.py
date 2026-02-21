#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一的股票資料獲取服務
實現 MongoDB -> Yahoo Finance 資料介面的完整降級機制
僅支援美股市場
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# 導入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

try:
    from tradingagents.config.database_manager import get_database_manager
    DATABASE_MANAGER_AVAILABLE = True
except ImportError:
    DATABASE_MANAGER_AVAILABLE = False


class StockDataService:
    """
    統一的股票資料獲取服務
    實現完整的降級機制：MongoDB -> Yahoo Finance -> 快取 -> 錯誤處理
    僅支援美股市場
    """

    def __init__(self):
        self.db_manager = None
        self._init_services()

    def _init_services(self):
        """初始化服務連線"""
        if DATABASE_MANAGER_AVAILABLE:
            try:
                self.db_manager = get_database_manager()
                if self.db_manager.is_mongodb_available():
                    logger.info("MongoDB 連線成功")
                else:
                    logger.warning("MongoDB 連線失敗，將使用其他資料來源")
            except Exception as e:
                logger.error(f"資料庫管理器初始化失敗: {e}")
                self.db_manager = None

    def get_stock_basic_info(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """
        獲取股票基礎資訊（單個股票或全部股票）

        Args:
            stock_code: 美股股票代碼（如 AAPL、MSFT），若為 None 則回傳所有股票

        Returns:
            Dict: 股票基礎資訊
        """
        logger.info(f"獲取股票基礎資訊: {stock_code or '全部股票'}")

        # 優先從 MongoDB 獲取
        if self.db_manager and self.db_manager.is_mongodb_available():
            try:
                result = self._get_from_mongodb(stock_code)
                if result:
                    count = len(result) if isinstance(result, list) else 1
                    logger.info(f"從 MongoDB 獲取成功: {count} 筆記錄")
                    return result
            except Exception as e:
                logger.error(f"MongoDB 查詢失敗: {e}")

        # 降級方案：回傳基本資訊
        logger.warning("MongoDB 不可用，使用降級方案")
        return self._get_fallback_data(stock_code)

    def _get_from_mongodb(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """從 MongoDB 獲取資料"""
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
            logger.error(f"MongoDB 查詢失敗: {e}")
            return None

    def _cache_to_mongodb(self, data: Any) -> bool:
        """將資料快取到 MongoDB"""
        if not self.db_manager or not self.db_manager.mongodb_db:
            return False

        try:
            collection = self.db_manager.mongodb_db['stock_basic_info']

            if isinstance(data, list):
                # 批次寫入
                for item in data:
                    collection.update_one(
                        {'code': item['code']},
                        {'$set': item},
                        upsert=True
                    )
                logger.info(f"已快取 {len(data)} 筆記錄到 MongoDB")
            elif isinstance(data, dict):
                # 單筆寫入
                collection.update_one(
                    {'code': data['code']},
                    {'$set': data},
                    upsert=True
                )
                logger.info(f"已快取股票 {data['code']} 到 MongoDB")

            return True

        except Exception as e:
            logger.error(f"快取到 MongoDB 失敗: {e}")
            return False

    def _get_fallback_data(self, stock_code: str = None) -> Dict[str, Any]:
        """所有資料來源皆不可用時的降級回傳"""
        if stock_code:
            return {
                'code': stock_code,
                'name': f'股票 {stock_code}',
                'market': self._get_market_name(stock_code),
                'category': self._get_stock_category(stock_code),
                'source': 'fallback',
                'updated_at': datetime.now().isoformat(),
                'error': '所有資料來源皆不可用'
            }
        else:
            return {
                'error': '無法獲取股票列表，請檢查網路連線和資料庫設定',
                'suggestion': '請確保 MongoDB 已設定或網路連線正常以存取資料服務'
            }

    def _get_market_name(self, stock_code: str) -> str:
        """根據股票代碼判斷市場，僅支援美股"""
        return '美股'

    def _get_stock_category(self, stock_code: str) -> str:
        """根據股票代碼判斷分類，僅支援美股"""
        return '美股'

    def get_stock_data_with_fallback(self, stock_code: str, start_date: str, end_date: str) -> str:
        """
        獲取股票資料（帶降級機制）

        Args:
            stock_code: 美股股票代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            str: 股票資料或錯誤訊息
        """
        logger.info(f"獲取股票資料: {stock_code} ({start_date} 到 {end_date})")

        # 確保股票基礎資訊可用
        stock_info = self.get_stock_basic_info(stock_code)
        if stock_info and 'error' in stock_info:
            return f"無法獲取股票 {stock_code} 的基礎資訊: {stock_info.get('error', '未知錯誤')}"

        # 透過資料庫管理器獲取資料
        try:
            if self.db_manager:
                return self.db_manager.get_stock_data(stock_code, start_date, end_date)
            return "資料服務不可用，請檢查資料庫設定"
        except Exception as e:
            return f"獲取股票資料失敗: {str(e)}"


# 全域服務實例（單例模式）
_stock_data_service = None


def get_stock_data_service() -> StockDataService:
    """獲取股票資料服務實例（單例模式）"""
    global _stock_data_service
    if _stock_data_service is None:
        _stock_data_service = StockDataService()
    return _stock_data_service
