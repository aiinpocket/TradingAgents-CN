#!/usr/bin/env python3
"""
自適應快取系統
根據資料庫可用性自動選擇最佳快取策略
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd

from ..config.database_manager import get_database_manager

class AdaptiveCacheSystem:
    """自適應快取系統"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.logger = logging.getLogger(__name__)
        
        # 獲取資料庫管理器
        self.db_manager = get_database_manager()
        
        # 設置快取目錄
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 獲取配置
        self.config = self.db_manager.get_config()
        self.cache_config = self.config["cache"]
        
        # 初始化快取後端
        self.primary_backend = self.cache_config["primary_backend"]
        self.fallback_enabled = self.cache_config["fallback_enabled"]
        
        self.logger.info(f"自適應快取系統初始化 - 主要後端: {self.primary_backend}")
    
    def _get_cache_key(self, symbol: str, start_date: str = "", end_date: str = "", 
                      data_source: str = "default", data_type: str = "stock_data") -> str:
        """生成快取鍵"""
        key_data = f"{symbol}_{start_date}_{end_date}_{data_source}_{data_type}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_ttl_seconds(self, symbol: str, data_type: str = "stock_data") -> int:
        """獲取TTL秒數（僅支援美股）"""
        market = "us"

        # 獲取TTL配置
        ttl_key = f"{market}_{data_type}"
        ttl_seconds = self.cache_config["ttl_settings"].get(ttl_key, 7200)
        return ttl_seconds
    
    def _is_cache_valid(self, cache_time: datetime, ttl_seconds: int) -> bool:
        """檢查快取是否有效"""
        if cache_time is None:
            return False
        
        expiry_time = cache_time + timedelta(seconds=ttl_seconds)
        return datetime.now() < expiry_time
    
    def _serialize_data(self, data: Any) -> dict:
        """將資料序列化為 JSON 安全格式，避免使用 pickle"""
        if isinstance(data, pd.DataFrame):
            return {'_type': 'dataframe', '_value': data.to_json()}
        elif isinstance(data, pd.Series):
            return {'_type': 'series', '_value': data.to_json()}
        elif isinstance(data, datetime):
            return {'_type': 'datetime', '_value': data.isoformat()}
        else:
            return {'_type': 'raw', '_value': data}

    def _deserialize_data(self, serialized: dict) -> Any:
        """從 JSON 安全格式還原資料"""
        data_type = serialized.get('_type', 'raw')
        value = serialized.get('_value')
        if data_type == 'dataframe':
            return pd.read_json(value)
        elif data_type == 'series':
            return pd.read_json(value, typ='series')
        elif data_type == 'datetime':
            return datetime.fromisoformat(value)
        else:
            return value

    def _save_to_file(self, cache_key: str, data: Any, metadata: Dict) -> bool:
        """保存到檔案快取（使用 JSON 格式取代 pickle）"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            cache_data = {
                'data': self._serialize_data(data),
                'metadata': metadata,
                'timestamp': datetime.now().isoformat(),
                'backend': 'file'
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, default=str)

            self.logger.debug(f"檔案快取保存成功: {cache_key}")
            return True

        except Exception as e:
            self.logger.error(f"檔案快取保存失敗: {e}")
            return False
    
    def _load_from_file(self, cache_key: str) -> Optional[Dict]:
        """從檔案快取載入（支援 JSON 格式，兼容舊 .pkl 檔案）"""
        try:
            # 優先使用 JSON 格式
            json_file = self.cache_dir / f"{cache_key}.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                # 還原序列化的資料
                cache_data['data'] = self._deserialize_data(cache_data['data'])
                # 還原時間戳
                if isinstance(cache_data['timestamp'], str):
                    cache_data['timestamp'] = datetime.fromisoformat(cache_data['timestamp'])
                self.logger.debug(f"檔案快取載入成功 (JSON): {cache_key}")
                return cache_data

            # 舊格式 .pkl 檔案不再支援載入（安全考量）
            pkl_file = self.cache_dir / f"{cache_key}.pkl"
            if pkl_file.exists():
                self.logger.warning(f"發現舊格式 .pkl 快取檔案，已跳過（安全考量）: {cache_key}")
                return None

            return None

        except Exception as e:
            self.logger.error(f"檔案快取載入失敗: {e}")
            return None
    
    def _save_to_redis(self, cache_key: str, data: Any, metadata: Dict, ttl_seconds: int) -> bool:
        """保存到 Redis 快取（使用 JSON 序列化）"""
        redis_client = self.db_manager.get_redis_client()
        if not redis_client:
            return False

        try:
            cache_data = {
                'data': self._serialize_data(data),
                'metadata': metadata,
                'timestamp': datetime.now().isoformat(),
                'backend': 'redis'
            }

            serialized_data = json.dumps(cache_data, ensure_ascii=False, default=str)
            redis_client.setex(cache_key, ttl_seconds, serialized_data)

            self.logger.debug(f"Redis快取保存成功: {cache_key}")
            return True

        except Exception as e:
            self.logger.error(f"Redis快取保存失敗: {e}")
            return False
    
    def _load_from_redis(self, cache_key: str) -> Optional[Dict]:
        """從 Redis 快取載入（使用 JSON 反序列化）"""
        redis_client = self.db_manager.get_redis_client()
        if not redis_client:
            return None

        try:
            serialized_data = redis_client.get(cache_key)
            if not serialized_data:
                return None

            # 解碼 bytes
            if isinstance(serialized_data, bytes):
                serialized_data = serialized_data.decode('utf-8')

            cache_data = json.loads(serialized_data)
            # 還原序列化的資料
            cache_data['data'] = self._deserialize_data(cache_data['data'])
            # 轉換時間戳
            if isinstance(cache_data['timestamp'], str):
                cache_data['timestamp'] = datetime.fromisoformat(cache_data['timestamp'])

            self.logger.debug(f"Redis快取載入成功: {cache_key}")
            return cache_data

        except Exception as e:
            self.logger.error(f"Redis快取載入失敗: {e}")
            return None
    
    def _save_to_mongodb(self, cache_key: str, data: Any, metadata: Dict, ttl_seconds: int) -> bool:
        """保存到 MongoDB 快取（使用 JSON 序列化）"""
        mongodb_client = self.db_manager.get_mongodb_client()
        if not mongodb_client:
            return False

        try:
            db = mongodb_client.tradingagents
            collection = db.cache

            # 統一使用 JSON 安全序列化
            serialized = self._serialize_data(data)

            cache_doc = {
                '_id': cache_key,
                'data': json.dumps(serialized, ensure_ascii=False, default=str),
                'data_type': 'json',
                'metadata': metadata,
                'timestamp': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds),
                'backend': 'mongodb'
            }

            collection.replace_one({'_id': cache_key}, cache_doc, upsert=True)

            self.logger.debug(f"MongoDB快取保存成功: {cache_key}")
            return True

        except Exception as e:
            self.logger.error(f"MongoDB快取保存失敗: {e}")
            return False
    
    def _load_from_mongodb(self, cache_key: str) -> Optional[Dict]:
        """從 MongoDB 快取載入（使用 JSON 反序列化）"""
        mongodb_client = self.db_manager.get_mongodb_client()
        if not mongodb_client:
            return None

        try:
            db = mongodb_client.tradingagents
            collection = db.cache

            doc = collection.find_one({'_id': cache_key})
            if not doc:
                return None

            # 檢查是否過期
            if doc.get('expires_at') and doc['expires_at'] < datetime.now():
                collection.delete_one({'_id': cache_key})
                return None

            # 反序列化資料
            if doc['data_type'] == 'json':
                serialized = json.loads(doc['data'])
                data = self._deserialize_data(serialized)
            elif doc['data_type'] == 'dataframe':
                # 兼容舊格式
                data = pd.read_json(doc['data'])
            else:
                # 舊 pickle 格式不再支援（安全考量）
                self.logger.warning(f"MongoDB 快取包含不安全的 pickle 格式，已跳過: {cache_key}")
                return None

            cache_data = {
                'data': data,
                'metadata': doc['metadata'],
                'timestamp': doc['timestamp'],
                'backend': 'mongodb'
            }

            self.logger.debug(f"MongoDB快取載入成功: {cache_key}")
            return cache_data

        except Exception as e:
            self.logger.error(f"MongoDB快取載入失敗: {e}")
            return None
    
    def save_data(self, symbol: str, data: Any, start_date: str = "", end_date: str = "", 
                  data_source: str = "default", data_type: str = "stock_data") -> str:
        """保存資料到快取"""
        # 生成快取鍵
        cache_key = self._get_cache_key(symbol, start_date, end_date, data_source, data_type)
        
        # 準備中繼資料
        metadata = {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'data_source': data_source,
            'data_type': data_type
        }
        
        # 獲取TTL
        ttl_seconds = self._get_ttl_seconds(symbol, data_type)
        
        # 根據主要後端保存
        success = False
        
        if self.primary_backend == "redis":
            success = self._save_to_redis(cache_key, data, metadata, ttl_seconds)
        elif self.primary_backend == "mongodb":
            success = self._save_to_mongodb(cache_key, data, metadata, ttl_seconds)
        elif self.primary_backend == "file":
            success = self._save_to_file(cache_key, data, metadata)
        
        # 如果主要後端失敗，使用降級策略
        if not success and self.fallback_enabled:
            self.logger.warning(f"主要後端({self.primary_backend})保存失敗，使用檔案快取降級")
            success = self._save_to_file(cache_key, data, metadata)
        
        if success:
            self.logger.info(f"資料快取成功: {symbol} -> {cache_key} (後端: {self.primary_backend})")
        else:
            self.logger.error(f"資料快取失敗: {symbol}")
        
        return cache_key
    
    def load_data(self, cache_key: str) -> Optional[Any]:
        """從快取載入資料"""
        cache_data = None
        
        # 根據主要後端載入
        if self.primary_backend == "redis":
            cache_data = self._load_from_redis(cache_key)
        elif self.primary_backend == "mongodb":
            cache_data = self._load_from_mongodb(cache_key)
        elif self.primary_backend == "file":
            cache_data = self._load_from_file(cache_key)
        
        # 如果主要後端失敗，嘗試降級
        if not cache_data and self.fallback_enabled:
            self.logger.debug(f"主要後端({self.primary_backend})載入失敗，嘗試檔案快取")
            cache_data = self._load_from_file(cache_key)
        
        if not cache_data:
            return None
        
        # 檢查快取是否有效（僅對檔案快取，資料庫快取有自己的TTL機制）
        if cache_data.get('backend') == 'file':
            symbol = cache_data['metadata'].get('symbol', '')
            data_type = cache_data['metadata'].get('data_type', 'stock_data')
            ttl_seconds = self._get_ttl_seconds(symbol, data_type)
            
            if not self._is_cache_valid(cache_data['timestamp'], ttl_seconds):
                self.logger.debug(f"檔案快取已過期: {cache_key}")
                return None
        
        return cache_data['data']
    
    def find_cached_data(self, symbol: str, start_date: str = "", end_date: str = "", 
                        data_source: str = "default", data_type: str = "stock_data") -> Optional[str]:
        """查找快取的資料"""
        cache_key = self._get_cache_key(symbol, start_date, end_date, data_source, data_type)
        
        # 檢查快取是否存在且有效
        if self.load_data(cache_key) is not None:
            return cache_key
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取快取統計資訊"""
        stats = {
            'primary_backend': self.primary_backend,
            'fallback_enabled': self.fallback_enabled,
            'database_available': self.db_manager.is_database_available(),
            'mongodb_available': self.db_manager.is_mongodb_available(),
            'redis_available': self.db_manager.is_redis_available(),
            'file_cache_directory': str(self.cache_dir),
            'file_cache_count': len(list(self.cache_dir.glob("*.json"))),
        }
        
        # Redis統計
        redis_client = self.db_manager.get_redis_client()
        if redis_client:
            try:
                redis_info = redis_client.info()
                stats['redis_memory_used'] = redis_info.get('used_memory_human', 'N/A')
                stats['redis_keys'] = redis_client.dbsize()
            except Exception as e:
                stats['redis_status'] = 'Error'
        
        # MongoDB統計
        mongodb_client = self.db_manager.get_mongodb_client()
        if mongodb_client:
            try:
                db = mongodb_client.tradingagents
                stats['mongodb_cache_count'] = db.cache.count_documents({})
            except Exception as e:
                stats['mongodb_status'] = 'Error'
        
        return stats
    
    def clear_expired_cache(self):
        """清理過期快取"""
        self.logger.info("開始清理過期快取...")

        cleared_files = 0
        # 清理 JSON 格式快取
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                symbol = cache_data['metadata'].get('symbol', '')
                data_type = cache_data['metadata'].get('data_type', 'stock_data')
                ttl_seconds = self._get_ttl_seconds(symbol, data_type)

                timestamp = cache_data.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)

                if not self._is_cache_valid(timestamp, ttl_seconds):
                    cache_file.unlink()
                    cleared_files += 1

            except Exception as e:
                self.logger.error(f"清理快取檔案失敗 {cache_file}: {e}")

        # 同時清理舊的 .pkl 檔案（不安全格式，直接刪除）
        for pkl_file in self.cache_dir.glob("*.pkl"):
            try:
                pkl_file.unlink()
                cleared_files += 1
                self.logger.info(f"已刪除不安全的舊格式快取: {pkl_file.name}")
            except Exception as e:
                self.logger.error(f"刪除舊快取檔案失敗 {pkl_file}: {e}")

        self.logger.info(f"檔案快取清理完成，刪除 {cleared_files} 個過期/不安全檔案")

        # MongoDB 會自動清理過期文檔（透過 expires_at 字段）
        # Redis 會自動清理過期鍵


# 全局快取系統實例
_cache_system = None

def get_cache_system() -> AdaptiveCacheSystem:
    """獲取全局自適應快取系統實例"""
    global _cache_system
    if _cache_system is None:
        _cache_system = AdaptiveCacheSystem()
    return _cache_system
