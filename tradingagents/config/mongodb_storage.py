#!/usr/bin/env python3
"""
MongoDB儲存適配器
用於將token使用記錄儲存到MongoDB資料庫
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from .config_manager import UsageRecord

# 匯入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoClient = None


class MongoDBStorage:
    """MongoDB儲存適配器"""
    
    def __init__(self, connection_string: str = None, database_name: str = "tradingagents"):
        if not MONGODB_AVAILABLE:
            raise ImportError("pymongo is not installed. Please install it with: pip install pymongo")
        
        # 修複硬編碼問題 - 如果沒有提供連接字串且環境變量也未設定，則拋出錯誤
        self.connection_string = connection_string or os.getenv("MONGODB_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError(
                "MongoDB連接字串未配置。請通過以下方式之一進行配置：\n"
                "1. 設定環境變量 MONGODB_CONNECTION_STRING\n"
                "2. 在初始化時傳入 connection_string 參數\n"
                "例如: MONGODB_CONNECTION_STRING=mongodb://localhost:27017/"
            )
        
        self.database_name = database_name
        self.collection_name = "token_usage"
        
        self.client = None
        self.db = None
        self.collection = None
        self._connected = False
        
        # 嘗試連接
        self._connect()
    
    def _connect(self):
        """連接到MongoDB"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000  # 5秒超時
            )
            # 測試連接
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # 創建索引以提高查詢性能
            self._create_indexes()
            
            self._connected = True
            logger.info(f"MongoDB連接成功: {self.database_name}.{self.collection_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB連接失敗: {e}")
            logger.info("將使用本地JSON 檔案儲存")
            self._connected = False
        except Exception as e:
            logger.error(f"MongoDB初始化失敗: {e}")
            self._connected = False
    
    def _create_indexes(self):
        """創建資料庫索引"""
        try:
            # 創建複合索引
            self.collection.create_index([
                ("timestamp", -1),  # 按時間倒序
                ("provider", 1),
                ("model_name", 1)
            ])
            
            # 創建會話ID索引
            self.collection.create_index("session_id")
            
            # 創建分析類型索引
            self.collection.create_index("analysis_type")
            
        except Exception as e:
            logger.error(f"創建MongoDB索引失敗: {e}")
    
    def is_connected(self) -> bool:
        """檢查是否連接到MongoDB"""
        return self._connected
    
    def save_usage_record(self, record: UsageRecord) -> bool:
        """保存單個使用記錄到MongoDB"""
        if not self._connected:
            return False
        
        try:
            # 轉換為字典格式
            record_dict = asdict(record)
            
            # 添加MongoDB特有的字段
            record_dict['_created_at'] = datetime.now()
            
            # 插入記錄
            result = self.collection.insert_one(record_dict)
            
            if result.inserted_id:
                return True
            else:
                logger.error("MongoDB插入失敗：未返回插入ID")
                return False
                
        except Exception as e:
            logger.error(f"保存記錄到MongoDB失敗: {e}")
            return False
    
    def load_usage_records(self, limit: int = 10000, days: int = None) -> List[UsageRecord]:
        """從MongoDB載入使用記錄"""
        if not self._connected:
            return []
        
        try:
            # 構建查詢條件
            query = {}
            if days:
                from datetime import timedelta
                cutoff_date = datetime.now() - timedelta(days=days)
                query['timestamp'] = {'$gte': cutoff_date.isoformat()}
            
            # 查詢記錄，按時間倒序
            cursor = self.collection.find(query).sort('timestamp', -1).limit(limit)
            
            records = []
            for doc in cursor:
                # 移除MongoDB特有的字段
                doc.pop('_id', None)
                doc.pop('_created_at', None)
                
                # 轉換為UsageRecord對象
                try:
                    record = UsageRecord(**doc)
                    records.append(record)
                except Exception as e:
                    logger.error(f"解析記錄失敗: {e}, 記錄: {doc}")
                    continue
            
            return records
            
        except Exception as e:
            logger.error(f"從MongoDB載入記錄失敗: {e}")
            return []
    
    def get_usage_statistics(self, days: int = 30) -> Dict[str, Any]:
        """從MongoDB獲取使用統計"""
        if not self._connected:
            return {}
        
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 聚合查詢
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': cutoff_date.isoformat()}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_cost': {'$sum': '$cost'},
                        'total_input_tokens': {'$sum': '$input_tokens'},
                        'total_output_tokens': {'$sum': '$output_tokens'},
                        'total_requests': {'$sum': 1}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                return {
                    'period_days': days,
                    'total_cost': round(stats.get('total_cost', 0), 4),
                    'total_input_tokens': stats.get('total_input_tokens', 0),
                    'total_output_tokens': stats.get('total_output_tokens', 0),
                    'total_requests': stats.get('total_requests', 0)
                }
            else:
                return {
                    'period_days': days,
                    'total_cost': 0,
                    'total_input_tokens': 0,
                    'total_output_tokens': 0,
                    'total_requests': 0
                }
                
        except Exception as e:
            logger.error(f"獲取MongoDB統計失敗: {e}")
            return {}
    
    def get_provider_statistics(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """按供應商獲取統計資訊"""
        if not self._connected:
            return {}
        
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 按供應商聚合
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': cutoff_date.isoformat()}
                    }
                },
                {
                    '$group': {
                        '_id': '$provider',
                        'cost': {'$sum': '$cost'},
                        'input_tokens': {'$sum': '$input_tokens'},
                        'output_tokens': {'$sum': '$output_tokens'},
                        'requests': {'$sum': 1}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            provider_stats = {}
            for result in results:
                provider = result['_id']
                provider_stats[provider] = {
                    'cost': round(result.get('cost', 0), 4),
                    'input_tokens': result.get('input_tokens', 0),
                    'output_tokens': result.get('output_tokens', 0),
                    'requests': result.get('requests', 0)
                }
            
            return provider_stats
            
        except Exception as e:
            logger.error(f"獲取供應商統計失敗: {e}")
            return {}
    
    def cleanup_old_records(self, days: int = 90) -> int:
        """清理舊記錄"""
        if not self._connected:
            return 0
        
        try:
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=days)
            
            result = self.collection.delete_many({
                'timestamp': {'$lt': cutoff_date.isoformat()}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 條超過 {days} 天的記錄")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理舊記錄失敗: {e}")
            return 0
    
    def close(self):
        """關閉MongoDB連接"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("MongoDB連接已關閉")