#!/usr/bin/env python3
"""
MongoDB + Redis 資料庫快取管理器
提供高性能的股票資料快取和持久化儲存
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import pandas as pd

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

# MongoDB
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logger.warning("pymongo 未安裝，MongoDB功能不可用")

# Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis 未安裝，Redis功能不可用")


class DatabaseCacheManager:
    """MongoDB + Redis 資料庫快取管理器"""
    
    def __init__(self,
                 mongodb_url: Optional[str] = None,
                 redis_url: Optional[str] = None,
                 mongodb_db: str = "tradingagents",
                 redis_db: int = 0):
        """
        初始化資料庫快取管理器

        Args:
            mongodb_url: MongoDB連接URL，預設使用配置檔端口
            redis_url: Redis連接URL，預設使用配置檔端口
            mongodb_db: MongoDB資料庫名
            redis_db: Redis資料庫編號
        """
        # 從配置檔取得正確的端口
        mongodb_port = os.getenv("MONGODB_PORT", "27018")
        redis_port = os.getenv("REDIS_PORT", "6380")
        mongodb_password = os.getenv("MONGODB_PASSWORD", "")
        redis_password = os.getenv("REDIS_PASSWORD", "")

        # 優先使用完整 URL，其次組合環境變數（不在程式碼中嵌入預設密碼）
        # 使用關鍵字參數避免密碼出現在 URL 字串中
        self.mongodb_url = mongodb_url or os.getenv("MONGODB_URL")
        self.mongodb_host = "localhost"
        self.mongodb_port_num = int(mongodb_port)
        self.mongodb_username = os.getenv("MONGODB_USERNAME", "admin") if mongodb_password else None
        self.mongodb_password = mongodb_password or None

        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.redis_host = "localhost"
        self.redis_port_num = int(redis_port)
        self.redis_password = redis_password or None
        self.mongodb_db_name = mongodb_db
        self.redis_db = redis_db
        
        # 初始化連接
        self.mongodb_client = None
        self.mongodb_db = None
        self.redis_client = None
        
        self._init_mongodb()
        self._init_redis()
        
        logger.info("資料庫快取管理器初始化完成")
        logger.debug(f"   MongoDB: {'已連接' if self.mongodb_client else '未連接'}")
        logger.debug(f"   Redis: {'已連接' if self.redis_client else '未連接'}")
    
    def _init_mongodb(self):
        """初始化MongoDB連接"""
        if not MONGODB_AVAILABLE:
            return
        
        try:
            # 使用關鍵字參數連接，避免密碼出現在 URL 字串中
            if self.mongodb_url:
                self.mongodb_client = MongoClient(
                    self.mongodb_url,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
            else:
                kwargs = {
                    "host": self.mongodb_host,
                    "port": self.mongodb_port_num,
                    "serverSelectionTimeoutMS": 5000,
                    "connectTimeoutMS": 5000,
                }
                if self.mongodb_username:
                    kwargs["username"] = self.mongodb_username
                    kwargs["password"] = self.mongodb_password
                self.mongodb_client = MongoClient(**kwargs)

            # 測試連接
            self.mongodb_client.admin.command('ping')
            self.mongodb_db = self.mongodb_client[self.mongodb_db_name]

            # 建立索引
            self._create_mongodb_indexes()

            logger.info("MongoDB連接成功")
            
        except Exception as e:
            logger.error(f"MongoDB連接失敗: {e}")
            self.mongodb_client = None
            self.mongodb_db = None
    
    def _init_redis(self):
        """初始化Redis連接"""
        if not REDIS_AVAILABLE:
            return
        
        try:
            # 使用關鍵字參數連接，避免密碼出現在 URL 字串中
            if self.redis_url:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    db=self.redis_db,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    decode_responses=True
                )
            else:
                self.redis_client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port_num,
                    db=self.redis_db,
                    password=self.redis_password,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    decode_responses=True
                )
            # 測試連接
            self.redis_client.ping()
            
            # 不記錄完整 URL 以避免洩露密碼
            logger.info("Redis連接成功")
            
        except Exception as e:
            logger.error(f"Redis連接失敗: {e}")
            self.redis_client = None
    
    def _create_mongodb_indexes(self):
        """建立MongoDB索引"""
        if self.mongodb_db is None:
            return
        
        try:
            # 股票資料集合索引
            stock_collection = self.mongodb_db.stock_data
            stock_collection.create_index([
                ("symbol", 1),
                ("data_source", 1),
                ("start_date", 1),
                ("end_date", 1)
            ])
            stock_collection.create_index([("created_at", 1)])
            
            # 新聞資料集合索引
            news_collection = self.mongodb_db.news_data
            news_collection.create_index([
                ("symbol", 1),
                ("data_source", 1),
                ("date_range", 1)
            ])
            news_collection.create_index([("created_at", 1)])
            
            # 基本面資料集合索引
            fundamentals_collection = self.mongodb_db.fundamentals_data
            fundamentals_collection.create_index([
                ("symbol", 1),
                ("data_source", 1),
                ("analysis_date", 1)
            ])
            fundamentals_collection.create_index([("created_at", 1)])
            
            logger.info("MongoDB索引建立完成")
            
        except Exception as e:
            logger.error(f"MongoDB索引建立失敗: {e}")
    
    def _generate_cache_key(self, data_type: str, symbol: str, **kwargs) -> str:
        """生成快取鍵"""
        params_str = f"{data_type}_{symbol}"
        for key, value in sorted(kwargs.items()):
            params_str += f"_{key}_{value}"
        
        cache_key = hashlib.md5(params_str.encode()).hexdigest()[:16]
        return f"{data_type}:{symbol}:{cache_key}"
    
    def save_stock_data(self, symbol: str, data: Union[pd.DataFrame, str],
                       start_date: str = None, end_date: str = None,
                       data_source: str = "unknown", market_type: str = None) -> str:
        """
        保存股票資料到MongoDB和Redis
        
        Args:
            symbol: 股票代碼
            data: 股票資料
            start_date: 開始日期
            end_date: 結束日期
            data_source: 資料來源
            market_type: 市場類型 (僅支援 us)
        
        Returns:
            cache_key: 快取鍵
        """
        cache_key = self._generate_cache_key("stock", symbol,
                                           start_date=start_date,
                                           end_date=end_date,
                                           source=data_source)
        
        # 自動推斷市場類型
        if market_type is None:
            # 根據股票代碼格式推斷市場類型
            pass

            # 統一視為美股
            market_type = "us"
        
        # 準備文件資料
        doc = {
            "_id": cache_key,
            "symbol": symbol,
            "market_type": market_type,
            "data_type": "stock_data",
            "start_date": start_date,
            "end_date": end_date,
            "data_source": data_source,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # 處理資料格式
        if isinstance(data, pd.DataFrame):
            doc["data"] = data.to_json(orient='records', date_format='iso')
            doc["data_format"] = "dataframe_json"
        else:
            doc["data"] = str(data)
            doc["data_format"] = "text"
        
        # 保存到MongoDB（持久化）
        if self.mongodb_db is not None:
            try:
                collection = self.mongodb_db.stock_data
                collection.replace_one({"_id": cache_key}, doc, upsert=True)
                logger.info(f"股票資料已保存到MongoDB: {symbol} -> {cache_key}")
            except Exception as e:
                logger.error(f"MongoDB保存失敗: {e}")
        
        # 保存到Redis（快速快取，6小時過期）
        if self.redis_client:
            try:
                redis_data = {
                    "data": doc["data"],
                    "data_format": doc["data_format"],
                    "symbol": symbol,
                    "data_source": data_source,
                    "created_at": doc["created_at"].isoformat()
                }
                self.redis_client.setex(
                    cache_key,
                    6 * 3600,  # 6小時過期
                    json.dumps(redis_data, ensure_ascii=False)
                )
                logger.info(f"股票資料已快取到Redis: {symbol} -> {cache_key}")
            except Exception as e:
                logger.error(f"Redis快取失敗: {e}")
        
        return cache_key
    
    def load_stock_data(self, cache_key: str) -> Optional[Union[pd.DataFrame, str]]:
        """從Redis或MongoDB載入股票資料"""
        
        # 首先嘗試從Redis載入（更快）
        if self.redis_client:
            try:
                redis_data = self.redis_client.get(cache_key)
                if redis_data:
                    data_dict = json.loads(redis_data)
                    logger.info(f"從Redis載入資料: {cache_key}")
                    
                    if data_dict["data_format"] == "dataframe_json":
                        return pd.read_json(data_dict["data"], orient='records')
                    else:
                        return data_dict["data"]
            except Exception as e:
                logger.error(f"Redis載入失敗: {e}")
        
        # 如果Redis沒有，從MongoDB載入
        if self.mongodb_db is not None:
            try:
                collection = self.mongodb_db.stock_data
                doc = collection.find_one({"_id": cache_key})
                
                if doc:
                    logger.info(f"從MongoDB載入資料: {cache_key}")
                    
                    # 同時更新到Redis快取
                    if self.redis_client:
                        try:
                            redis_data = {
                                "data": doc["data"],
                                "data_format": doc["data_format"],
                                "symbol": doc["symbol"],
                                "data_source": doc["data_source"],
                                "created_at": doc["created_at"].isoformat()
                            }
                            self.redis_client.setex(
                                cache_key,
                                6 * 3600,
                                json.dumps(redis_data, ensure_ascii=False)
                            )
                            logger.info("資料已同步到Redis快取")
                        except Exception as e:
                            logger.error(f"Redis同步失敗: {e}")
                    
                    if doc["data_format"] == "dataframe_json":
                        return pd.read_json(doc["data"], orient='records')
                    else:
                        return doc["data"]
                        
            except Exception as e:
                logger.error(f"MongoDB載入失敗: {e}")
        
        return None
    
    def find_cached_stock_data(self, symbol: str, start_date: str = None,
                              end_date: str = None, data_source: str = None,
                              max_age_hours: int = 6) -> Optional[str]:
        """查找匹配的快取資料"""
        
        # 生成精確匹配的快取鍵
        exact_key = self._generate_cache_key("stock", symbol,
                                           start_date=start_date,
                                           end_date=end_date,
                                           source=data_source)
        
        # 檢查Redis中是否有精確匹配
        if self.redis_client and self.redis_client.exists(exact_key):
            logger.info(f"Redis中找到精確匹配: {symbol} -> {exact_key}")
            return exact_key
        
        # 檢查MongoDB中的匹配項
        if self.mongodb_db is not None:
            try:
                collection = self.mongodb_db.stock_data
                cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
                
                query = {
                    "symbol": symbol,
                    "created_at": {"$gte": cutoff_time}
                }
                
                if data_source:
                    query["data_source"] = data_source
                if start_date:
                    query["start_date"] = start_date
                if end_date:
                    query["end_date"] = end_date
                
                doc = collection.find_one(query, sort=[("created_at", -1)])
                
                if doc:
                    cache_key = doc["_id"]
                    logger.info(f"MongoDB中找到匹配: {symbol} -> {cache_key}")
                    return cache_key
                    
            except Exception as e:
                logger.error(f"MongoDB查詢失敗: {e}")
        
        logger.error(f"未找到有效快取: {symbol}")
        return None

    def save_news_data(self, symbol: str, news_data: str,
                      start_date: str = None, end_date: str = None,
                      data_source: str = "unknown") -> str:
        """保存新聞資料到MongoDB和Redis"""
        cache_key = self._generate_cache_key("news", symbol,
                                           start_date=start_date,
                                           end_date=end_date,
                                           source=data_source)

        doc = {
            "_id": cache_key,
            "symbol": symbol,
            "data_type": "news_data",
            "date_range": f"{start_date}_{end_date}",
            "start_date": start_date,
            "end_date": end_date,
            "data_source": data_source,
            "data": news_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # 保存到MongoDB
        if self.mongodb_db is not None:
            try:
                collection = self.mongodb_db.news_data
                collection.replace_one({"_id": cache_key}, doc, upsert=True)
                logger.info(f"新聞資料已保存到MongoDB: {symbol} -> {cache_key}")
            except Exception as e:
                logger.error(f"MongoDB保存失敗: {e}")

        # 保存到Redis（24小時過期）
        if self.redis_client:
            try:
                redis_data = {
                    "data": news_data,
                    "symbol": symbol,
                    "data_source": data_source,
                    "created_at": doc["created_at"].isoformat()
                }
                self.redis_client.setex(
                    cache_key,
                    24 * 3600,  # 24小時過期
                    json.dumps(redis_data, ensure_ascii=False)
                )
                logger.info(f"新聞資料已快取到Redis: {symbol} -> {cache_key}")
            except Exception as e:
                logger.error(f"Redis快取失敗: {e}")

        return cache_key

    def save_fundamentals_data(self, symbol: str, fundamentals_data: str,
                              analysis_date: str = None,
                              data_source: str = "unknown") -> str:
        """保存基本面資料到MongoDB和Redis"""
        if not analysis_date:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        cache_key = self._generate_cache_key("fundamentals", symbol,
                                           date=analysis_date,
                                           source=data_source)

        doc = {
            "_id": cache_key,
            "symbol": symbol,
            "data_type": "fundamentals_data",
            "analysis_date": analysis_date,
            "data_source": data_source,
            "data": fundamentals_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # 保存到MongoDB
        if self.mongodb_db is not None:
            try:
                collection = self.mongodb_db.fundamentals_data
                collection.replace_one({"_id": cache_key}, doc, upsert=True)
                logger.info(f"基本面資料已保存到MongoDB: {symbol} -> {cache_key}")
            except Exception as e:
                logger.error(f"MongoDB保存失敗: {e}")

        # 保存到Redis（24小時過期）
        if self.redis_client:
            try:
                redis_data = {
                    "data": fundamentals_data,
                    "symbol": symbol,
                    "data_source": data_source,
                    "analysis_date": analysis_date,
                    "created_at": doc["created_at"].isoformat()
                }
                self.redis_client.setex(
                    cache_key,
                    24 * 3600,  # 24小時過期
                    json.dumps(redis_data, ensure_ascii=False)
                )
                logger.info(f"基本面資料已快取到Redis: {symbol} -> {cache_key}")
            except Exception as e:
                logger.error(f"Redis快取失敗: {e}")

        return cache_key

    def get_cache_stats(self) -> Dict[str, Any]:
        """取得快取統計資訊"""
        stats = {
            "mongodb": {"available": self.mongodb_db is not None, "collections": {}},
            "redis": {"available": self.redis_client is not None, "keys": 0, "memory_usage": "N/A"}
        }

        # MongoDB統計
        if self.mongodb_db is not None:
            try:
                for collection_name in ["stock_data", "news_data", "fundamentals_data"]:
                    collection = self.mongodb_db[collection_name]
                    count = collection.count_documents({})
                    size = self.mongodb_db.command("collStats", collection_name).get("size", 0)
                    stats["mongodb"]["collections"][collection_name] = {
                        "count": count,
                        "size_mb": round(size / (1024 * 1024), 2)
                    }
            except Exception as e:
                logger.error(f"MongoDB統計取得失敗: {e}")

        # Redis統計
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats["redis"]["keys"] = info.get("db0", {}).get("keys", 0)
                stats["redis"]["memory_usage"] = f"{info.get('used_memory_human', 'N/A')}"
            except Exception as e:
                logger.error(f"Redis統計取得失敗: {e}")

        return stats

    def clear_old_cache(self, max_age_days: int = 7):
        """清理過期快取"""
        cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)
        cleared_count = 0

        # 清理MongoDB
        if self.mongodb_db is not None:
            try:
                for collection_name in ["stock_data", "news_data", "fundamentals_data"]:
                    collection = self.mongodb_db[collection_name]
                    result = collection.delete_many({"created_at": {"$lt": cutoff_time}})
                    cleared_count += result.deleted_count
                    logger.info(f"MongoDB {collection_name} 清理了 {result.deleted_count} 條記錄")
            except Exception as e:
                logger.error(f"MongoDB清理失敗: {e}")

        # Redis會自動過期，不需要手動清理
        logger.info(f"總共清理了 {cleared_count} 條過期記錄")
        return cleared_count

    def close(self):
        """關閉資料庫連接"""
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("MongoDB連接已關閉")

        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis連接已關閉")


# 全局資料庫快取實例
_db_cache_instance = None

def get_db_cache() -> DatabaseCacheManager:
    """取得全局資料庫快取實例"""
    global _db_cache_instance
    if _db_cache_instance is None:
        _db_cache_instance = DatabaseCacheManager()
    return _db_cache_instance
