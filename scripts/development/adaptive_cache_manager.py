#!/usr/bin/env python3
"""
自適應緩存管理器 - 根據可用服務自動選擇最佳緩存策略
支持文件緩存、Redis緩存、MongoDB緩存的智能切換
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

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 導入智能配置
try:
    from smart_config import get_smart_config, get_config
    SMART_CONFIG_AVAILABLE = True
except ImportError:
    SMART_CONFIG_AVAILABLE = False

class AdaptiveCacheManager:
    """自適應緩存管理器 - 智能選擇緩存後端"""
    
    def __init__(self, cache_dir: str = "data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 設置日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 獲取智能配置
        self._load_smart_config()
        
        # 初始化緩存後端
        self._init_backends()
        
        self.logger.info(f"緩存管理器初始化完成，主要後端: {self.primary_backend}")
    
    def _load_smart_config(self):
        """加載智能配置"""
        if SMART_CONFIG_AVAILABLE:
            try:
                config_manager = get_smart_config()
                self.config = config_manager.get_config()
                self.primary_backend = self.config["cache"]["primary_backend"]
                self.mongodb_enabled = self.config["database"]["mongodb"]["enabled"]
                self.redis_enabled = self.config["database"]["redis"]["enabled"]
                self.fallback_enabled = self.config["cache"]["fallback_enabled"]
                self.ttl_settings = self.config["cache"]["ttl_settings"]
                
                self.logger.info("✅ 智能配置加載成功")
                return
            except Exception as e:
                self.logger.warning(f"智能配置加載失敗: {e}")
        
        # 默認配置（純文件緩存）
        self.config = {
            "cache": {
                "primary_backend": "file",
                "fallback_enabled": True,
                "ttl_settings": {
                    "us_stock_data": 7200,
                    "china_stock_data": 3600,
                    "us_news": 21600,
                    "china_news": 14400,
                    "us_fundamentals": 86400,
                    "china_fundamentals": 43200,
                }
            }
        }
        self.primary_backend = "file"
        self.mongodb_enabled = False
        self.redis_enabled = False
        self.fallback_enabled = True
        self.ttl_settings = self.config["cache"]["ttl_settings"]
        
        self.logger.info("使用默認配置（純文件緩存）")
    
    def _init_backends(self):
        """初始化緩存後端"""
        self.mongodb_client = None
        self.redis_client = None
        
        # 初始化MongoDB
        if self.mongodb_enabled:
            try:
                import pymongo
                self.mongodb_client = pymongo.MongoClient(
                    'localhost', 27017, 
                    serverSelectionTimeoutMS=2000
                )
                # 測試連接
                self.mongodb_client.server_info()
                self.mongodb_db = self.mongodb_client.tradingagents
                self.logger.info("✅ MongoDB後端初始化成功")
            except Exception as e:
                self.logger.warning(f"MongoDB初始化失敗: {e}")
                self.mongodb_enabled = False
                self.mongodb_client = None
        
        # 初始化Redis
        if self.redis_enabled:
            try:
                import redis

                self.redis_client = redis.Redis(
                    host='localhost', port=6379, 
                    socket_timeout=2
                )
                # 測試連接
                self.redis_client.ping()
                self.logger.info("✅ Redis後端初始化成功")
            except Exception as e:
                self.logger.warning(f"Redis初始化失敗: {e}")
                self.redis_enabled = False
                self.redis_client = None
        
        # 如果主要後端不可用，自動降級
        if self.primary_backend == "redis" and not self.redis_enabled:
            if self.mongodb_enabled:
                self.primary_backend = "mongodb"
                self.logger.info("Redis不可用，降級到MongoDB")
            else:
                self.primary_backend = "file"
                self.logger.info("Redis不可用，降級到文件緩存")
        
        elif self.primary_backend == "mongodb" and not self.mongodb_enabled:
            if self.redis_enabled:
                self.primary_backend = "redis"
                self.logger.info("MongoDB不可用，降級到Redis")
            else:
                self.primary_backend = "file"
                self.logger.info("MongoDB不可用，降級到文件緩存")
    
    def _get_cache_key(self, symbol: str, start_date: str, end_date: str, 
                      data_source: str = "default") -> str:
        """生成緩存鍵"""
        key_data = f"{symbol}_{start_date}_{end_date}_{data_source}"
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
        ttl_hours = self.ttl_settings.get(ttl_key, 7200)  # 默認2小時
        return ttl_hours
    
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
                'timestamp': datetime.now()
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
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
            
            return cache_data
        except Exception as e:
            self.logger.error(f"文件緩存加載失敗: {e}")
            return None
    
    def _save_to_redis(self, cache_key: str, data: Any, metadata: Dict, ttl_seconds: int) -> bool:
        """保存到Redis緩存"""
        if not self.redis_client:
            return False
        
        try:
            cache_data = {
                'data': data,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            serialized_data = pickle.dumps(cache_data)
            self.redis_client.setex(cache_key, ttl_seconds, serialized_data)
            return True
        except Exception as e:
            self.logger.error(f"Redis緩存保存失敗: {e}")
            return False
    
    def _load_from_redis(self, cache_key: str) -> Optional[Dict]:
        """從Redis緩存加載"""
        if not self.redis_client:
            return None
        
        try:
            serialized_data = self.redis_client.get(cache_key)
            if not serialized_data:
                return None
            
            cache_data = pickle.loads(serialized_data)
            # 轉換時間戳
            if isinstance(cache_data['timestamp'], str):
                cache_data['timestamp'] = datetime.fromisoformat(cache_data['timestamp'])
            
            return cache_data
        except Exception as e:
            self.logger.error(f"Redis緩存加載失敗: {e}")
            return None
    
    def save_stock_data(self, symbol: str, data: Any, start_date: str = None, 
                       end_date: str = None, data_source: str = "default") -> str:
        """保存股票數據到緩存"""
        # 生成緩存鍵
        cache_key = self._get_cache_key(symbol, start_date or "", end_date or "", data_source)
        
        # 準備元數據
        metadata = {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'data_source': data_source,
            'data_type': 'stock_data'
        }
        
        # 獲取TTL
        ttl_seconds = self._get_ttl_seconds(symbol, 'stock_data')
        
        # 根據主要後端保存
        success = False
        
        if self.primary_backend == "redis":
            success = self._save_to_redis(cache_key, data, metadata, ttl_seconds)
        elif self.primary_backend == "mongodb":
            # MongoDB保存邏輯（簡化版）
            success = self._save_to_file(cache_key, data, metadata)
        
        # 如果主要後端失敗，使用文件緩存作為備用
        if not success and self.fallback_enabled:
            success = self._save_to_file(cache_key, data, metadata)
            if success:
                self.logger.info(f"使用文件緩存備用保存: {cache_key}")
        
        if success:
            self.logger.info(f"數據保存成功: {symbol} -> {cache_key}")
        else:
            self.logger.error(f"數據保存失敗: {symbol}")
        
        return cache_key
    
    def load_stock_data(self, cache_key: str) -> Optional[Any]:
        """從緩存加載股票數據"""
        cache_data = None
        
        # 根據主要後端加載
        if self.primary_backend == "redis":
            cache_data = self._load_from_redis(cache_key)
        elif self.primary_backend == "mongodb":
            # MongoDB加載邏輯（簡化版）
            cache_data = self._load_from_file(cache_key)
        
        # 如果主要後端失敗，嘗試文件緩存
        if not cache_data and self.fallback_enabled:
            cache_data = self._load_from_file(cache_key)
            if cache_data:
                self.logger.info(f"使用文件緩存備用加載: {cache_key}")
        
        if not cache_data:
            return None
        
        # 檢查緩存是否有效
        symbol = cache_data['metadata'].get('symbol', '')
        data_type = cache_data['metadata'].get('data_type', 'stock_data')
        ttl_seconds = self._get_ttl_seconds(symbol, data_type)
        
        if not self._is_cache_valid(cache_data['timestamp'], ttl_seconds):
            self.logger.info(f"緩存已過期: {cache_key}")
            return None
        
        return cache_data['data']
    
    def find_cached_stock_data(self, symbol: str, start_date: str = None, 
                              end_date: str = None, data_source: str = "default") -> Optional[str]:
        """查找緩存的股票數據"""
        cache_key = self._get_cache_key(symbol, start_date or "", end_date or "", data_source)
        
        # 檢查緩存是否存在且有效
        if self.load_stock_data(cache_key) is not None:
            return cache_key
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取緩存統計信息"""
        stats = {
            'primary_backend': self.primary_backend,
            'mongodb_enabled': self.mongodb_enabled,
            'redis_enabled': self.redis_enabled,
            'fallback_enabled': self.fallback_enabled,
            'cache_directory': str(self.cache_dir),
            'file_cache_count': len(list(self.cache_dir.glob("*.pkl"))),
        }
        
        # Redis統計
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats['redis_memory_used'] = redis_info.get('used_memory_human', 'N/A')
                stats['redis_keys'] = self.redis_client.dbsize()
            except:
                stats['redis_status'] = 'Error'
        
        return stats


# 全局緩存管理器實例
_cache_manager = None

def get_cache() -> AdaptiveCacheManager:
    """獲取全局自適應緩存管理器"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = AdaptiveCacheManager()
    return _cache_manager


def main():
    """測試自適應緩存管理器"""
    logger.info(f"🔧 測試自適應緩存管理器")
    logger.info(f"=")
    
    # 創建緩存管理器
    cache = get_cache()
    
    # 顯示狀態
    stats = cache.get_cache_stats()
    logger.info(f"\n📊 緩存狀態:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    # 測試緩存功能
    logger.info(f"\n💾 測試緩存功能...")
    
    test_data = "測試股票數據 - AAPL"
    cache_key = cache.save_stock_data(
        symbol="AAPL",
        data=test_data,
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="test"
    )
    logger.info(f"✅ 數據保存: {cache_key}")
    
    # 加載數據
    loaded_data = cache.load_stock_data(cache_key)
    if loaded_data == test_data:
        logger.info(f"✅ 數據加載成功")
    else:
        logger.error(f"❌ 數據加載失敗")
    
    # 查找緩存
    found_key = cache.find_cached_stock_data(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="test"
    )
    
    if found_key:
        logger.info(f"✅ 緩存查找成功: {found_key}")
    else:
        logger.error(f"❌ 緩存查找失敗")
    
    logger.info(f"\n🎉 自適應緩存管理器測試完成!")


if __name__ == "__main__":
    main()
