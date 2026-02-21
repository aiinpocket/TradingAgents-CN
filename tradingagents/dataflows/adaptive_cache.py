#!/usr/bin/env python3
"""
自適應緩存系統
根據數據庫可用性自動選擇最佳緩存策略
"""

import os
import json
import pickle
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd

from ..config.database_manager import get_database_manager

class AdaptiveCacheSystem:
    """自適應緩存系統"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.logger = logging.getLogger(__name__)
        
        # 獲取數據庫管理器
        self.db_manager = get_database_manager()
        
        # 設置緩存目錄
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 獲取配置
        self.config = self.db_manager.get_config()
        self.cache_config = self.config["cache"]
        
        # 初始化緩存後端
        self.primary_backend = self.cache_config["primary_backend"]
        self.fallback_enabled = self.cache_config["fallback_enabled"]
        
        self.logger.info(f"自適應緩存系統初始化 - 主要後端: {self.primary_backend}")
    
    def _get_cache_key(self, symbol: str, start_date: str = "", end_date: str = "", 
                      data_source: str = "default", data_type: str = "stock_data") -> str:
        """生成緩存鍵"""
        key_data = f"{symbol}_{start_date}_{end_date}_{data_source}_{data_type}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_ttl_seconds(self, symbol: str, data_type: str = "stock_data") -> int:
        """獲取TTL秒數"""
        # 判斷市場類型
        if len(symbol) == 6 and symbol.isdigit():
            market = "china"
        else:
            market = "us"
        
        # 獲取TTL配置
        ttl_key = f"{market}_{data_type}"
        ttl_seconds = self.cache_config["ttl_settings"].get(ttl_key, 7200)
        return ttl_seconds
    
    def _is_cache_valid(self, cache_time: datetime, ttl_seconds: int) -> bool:
        """檢查緩存是否有效"""
        if cache_time is None:
            return False
        
        expiry_time = cache_time + timedelta(seconds=ttl_seconds)
        return datetime.now() < expiry_time
    
    def _save_to_file(self, cache_key: str, data: Any, metadata: Dict) -> bool:
        """保存到文件緩存"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            cache_data = {
                'data': data,
                'metadata': metadata,
                'timestamp': datetime.now(),
                'backend': 'file'
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.logger.debug(f"文件緩存保存成功: {cache_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"文件緩存保存失敗: {e}")
            return False
    
    def _load_from_file(self, cache_key: str) -> Optional[Dict]:
        """從文件緩存加載"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.logger.debug(f"文件緩存加載成功: {cache_key}")
            return cache_data
            
        except Exception as e:
            self.logger.error(f"文件緩存加載失敗: {e}")
            return None
    
    def _save_to_redis(self, cache_key: str, data: Any, metadata: Dict, ttl_seconds: int) -> bool:
        """保存到Redis緩存"""
        redis_client = self.db_manager.get_redis_client()
        if not redis_client:
            return False
        
        try:
            cache_data = {
                'data': data,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat(),
                'backend': 'redis'
            }
            
            serialized_data = pickle.dumps(cache_data)
            redis_client.setex(cache_key, ttl_seconds, serialized_data)
            
            self.logger.debug(f"Redis緩存保存成功: {cache_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Redis緩存保存失敗: {e}")
            return False
    
    def _load_from_redis(self, cache_key: str) -> Optional[Dict]:
        """從Redis緩存加載"""
        redis_client = self.db_manager.get_redis_client()
        if not redis_client:
            return None
        
        try:
            serialized_data = redis_client.get(cache_key)
            if not serialized_data:
                return None
            
            cache_data = pickle.loads(serialized_data)
            
            # 轉換時間戳
            if isinstance(cache_data['timestamp'], str):
                cache_data['timestamp'] = datetime.fromisoformat(cache_data['timestamp'])
            
            self.logger.debug(f"Redis緩存加載成功: {cache_key}")
            return cache_data
            
        except Exception as e:
            self.logger.error(f"Redis緩存加載失敗: {e}")
            return None
    
    def _save_to_mongodb(self, cache_key: str, data: Any, metadata: Dict, ttl_seconds: int) -> bool:
        """保存到MongoDB緩存"""
        mongodb_client = self.db_manager.get_mongodb_client()
        if not mongodb_client:
            return False
        
        try:
            db = mongodb_client.tradingagents
            collection = db.cache
            
            # 序列化數據
            if isinstance(data, pd.DataFrame):
                serialized_data = data.to_json()
                data_type = 'dataframe'
            else:
                serialized_data = pickle.dumps(data).hex()
                data_type = 'pickle'
            
            cache_doc = {
                '_id': cache_key,
                'data': serialized_data,
                'data_type': data_type,
                'metadata': metadata,
                'timestamp': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds),
                'backend': 'mongodb'
            }
            
            collection.replace_one({'_id': cache_key}, cache_doc, upsert=True)
            
            self.logger.debug(f"MongoDB緩存保存成功: {cache_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"MongoDB緩存保存失敗: {e}")
            return False
    
    def _load_from_mongodb(self, cache_key: str) -> Optional[Dict]:
        """從MongoDB緩存加載"""
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
            
            # 反序列化數據
            if doc['data_type'] == 'dataframe':
                data = pd.read_json(doc['data'])
            else:
                data = pickle.loads(bytes.fromhex(doc['data']))
            
            cache_data = {
                'data': data,
                'metadata': doc['metadata'],
                'timestamp': doc['timestamp'],
                'backend': 'mongodb'
            }
            
            self.logger.debug(f"MongoDB緩存加載成功: {cache_key}")
            return cache_data
            
        except Exception as e:
            self.logger.error(f"MongoDB緩存加載失敗: {e}")
            return None
    
    def save_data(self, symbol: str, data: Any, start_date: str = "", end_date: str = "", 
                  data_source: str = "default", data_type: str = "stock_data") -> str:
        """保存數據到緩存"""
        # 生成緩存鍵
        cache_key = self._get_cache_key(symbol, start_date, end_date, data_source, data_type)
        
        # 準備元數據
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
            self.logger.warning(f"主要後端({self.primary_backend})保存失敗，使用文件緩存降級")
            success = self._save_to_file(cache_key, data, metadata)
        
        if success:
            self.logger.info(f"數據緩存成功: {symbol} -> {cache_key} (後端: {self.primary_backend})")
        else:
            self.logger.error(f"數據緩存失敗: {symbol}")
        
        return cache_key
    
    def load_data(self, cache_key: str) -> Optional[Any]:
        """從緩存加載數據"""
        cache_data = None
        
        # 根據主要後端加載
        if self.primary_backend == "redis":
            cache_data = self._load_from_redis(cache_key)
        elif self.primary_backend == "mongodb":
            cache_data = self._load_from_mongodb(cache_key)
        elif self.primary_backend == "file":
            cache_data = self._load_from_file(cache_key)
        
        # 如果主要後端失敗，嘗試降級
        if not cache_data and self.fallback_enabled:
            self.logger.debug(f"主要後端({self.primary_backend})加載失敗，嘗試文件緩存")
            cache_data = self._load_from_file(cache_key)
        
        if not cache_data:
            return None
        
        # 檢查緩存是否有效（僅對文件緩存，數據庫緩存有自己的TTL機制）
        if cache_data.get('backend') == 'file':
            symbol = cache_data['metadata'].get('symbol', '')
            data_type = cache_data['metadata'].get('data_type', 'stock_data')
            ttl_seconds = self._get_ttl_seconds(symbol, data_type)
            
            if not self._is_cache_valid(cache_data['timestamp'], ttl_seconds):
                self.logger.debug(f"文件緩存已過期: {cache_key}")
                return None
        
        return cache_data['data']
    
    def find_cached_data(self, symbol: str, start_date: str = "", end_date: str = "", 
                        data_source: str = "default", data_type: str = "stock_data") -> Optional[str]:
        """查找緩存的數據"""
        cache_key = self._get_cache_key(symbol, start_date, end_date, data_source, data_type)
        
        # 檢查緩存是否存在且有效
        if self.load_data(cache_key) is not None:
            return cache_key
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取緩存統計信息"""
        stats = {
            'primary_backend': self.primary_backend,
            'fallback_enabled': self.fallback_enabled,
            'database_available': self.db_manager.is_database_available(),
            'mongodb_available': self.db_manager.is_mongodb_available(),
            'redis_available': self.db_manager.is_redis_available(),
            'file_cache_directory': str(self.cache_dir),
            'file_cache_count': len(list(self.cache_dir.glob("*.pkl"))),
        }
        
        # Redis統計
        redis_client = self.db_manager.get_redis_client()
        if redis_client:
            try:
                redis_info = redis_client.info()
                stats['redis_memory_used'] = redis_info.get('used_memory_human', 'N/A')
                stats['redis_keys'] = redis_client.dbsize()
            except:
                stats['redis_status'] = 'Error'
        
        # MongoDB統計
        mongodb_client = self.db_manager.get_mongodb_client()
        if mongodb_client:
            try:
                db = mongodb_client.tradingagents
                stats['mongodb_cache_count'] = db.cache.count_documents({})
            except:
                stats['mongodb_status'] = 'Error'
        
        return stats
    
    def clear_expired_cache(self):
        """清理過期緩存"""
        self.logger.info("開始清理過期緩存...")
        
        # 清理文件緩存
        cleared_files = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                symbol = cache_data['metadata'].get('symbol', '')
                data_type = cache_data['metadata'].get('data_type', 'stock_data')
                ttl_seconds = self._get_ttl_seconds(symbol, data_type)
                
                if not self._is_cache_valid(cache_data['timestamp'], ttl_seconds):
                    cache_file.unlink()
                    cleared_files += 1
                    
            except Exception as e:
                self.logger.error(f"清理緩存文件失敗 {cache_file}: {e}")
        
        self.logger.info(f"文件緩存清理完成，刪除 {cleared_files} 個過期文件")
        
        # MongoDB會自動清理過期文檔（通過expires_at字段）
        # Redis會自動清理過期鍵


# 全局緩存系統實例
_cache_system = None

def get_cache_system() -> AdaptiveCacheSystem:
    """獲取全局自適應緩存系統實例"""
    global _cache_system
    if _cache_system is None:
        _cache_system = AdaptiveCacheSystem()
    return _cache_system
