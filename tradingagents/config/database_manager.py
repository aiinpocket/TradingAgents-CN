#!/usr/bin/env python3
"""
智慧資料庫管理器
自動檢測MongoDB和Redis可用性，提供降級方案
使用專案現有的.env配置
"""

import logging
import os
from typing import Dict, Any, Tuple

class DatabaseManager:
    """智慧資料庫管理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 載入.env配置
        self._load_env_config()

        # 資料庫連接狀態
        self.mongodb_available = False
        self.redis_available = False
        self.mongodb_client = None
        self.redis_client = None

        # 檢測資料庫可用性
        self._detect_databases()

        # 初始化連接
        self._initialize_connections()

        self.logger.info(f"資料庫管理器初始化完成 - MongoDB: {self.mongodb_available}, Redis: {self.redis_available}")
    
    def _load_env_config(self):
        """從.env 檔案載入配置"""
        # 嘗試載入python-dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            self.logger.info("python-dotenv未安裝，直接讀取環境變數")

        # 使用強健的布爾值解析（相容Python 3.13+）
        from .env_utils import parse_bool_env
        self.mongodb_enabled = parse_bool_env("MONGODB_ENABLED", False)
        self.redis_enabled = parse_bool_env("REDIS_ENABLED", False)

        # 從環境變數讀取MongoDB配置
        self.mongodb_config = {
            "enabled": self.mongodb_enabled,
            "host": os.getenv("MONGODB_HOST", "localhost"),
            "port": int(os.getenv("MONGODB_PORT", "27017")),
            "username": os.getenv("MONGODB_USERNAME"),
            "password": os.getenv("MONGODB_PASSWORD"),
            "database": os.getenv("MONGODB_DATABASE", "tradingagents"),
            "auth_source": os.getenv("MONGODB_AUTH_SOURCE", "admin"),
            "timeout": 2000
        }

        # 從環境變數讀取Redis配置
        self.redis_config = {
            "enabled": self.redis_enabled,
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "password": os.getenv("REDIS_PASSWORD"),
            "db": int(os.getenv("REDIS_DB", "0")),
            "timeout": 2
        }

        self.logger.info(f"MongoDB啟用: {self.mongodb_enabled}")
        self.logger.info(f"Redis啟用: {self.redis_enabled}")
        if self.mongodb_enabled:
            self.logger.info(f"MongoDB配置: {self.mongodb_config['host']}:{self.mongodb_config['port']}")
        if self.redis_enabled:
            self.logger.info(f"Redis配置: {self.redis_config['host']}:{self.redis_config['port']}")
    

    
    def _detect_mongodb(self) -> Tuple[bool, str]:
        """檢測MongoDB是否可用"""
        # 首先檢查是否啟用
        if not self.mongodb_enabled:
            return False, "MongoDB未啟用 (MONGODB_ENABLED=false)"

        try:
            from pymongo import MongoClient

            # 構建連接參數
            connect_kwargs = {
                "host": self.mongodb_config["host"],
                "port": self.mongodb_config["port"],
                "serverSelectionTimeoutMS": self.mongodb_config["timeout"],
                "connectTimeoutMS": self.mongodb_config["timeout"]
            }

            # 如果有使用者名和密碼，新增認證
            if self.mongodb_config["username"] and self.mongodb_config["password"]:
                connect_kwargs.update({
                    "username": self.mongodb_config["username"],
                    "password": self.mongodb_config["password"],
                    "authSource": self.mongodb_config["auth_source"]
                })

            client = MongoClient(**connect_kwargs)

            # 測試連接
            client.server_info()
            client.close()

            return True, "MongoDB連接成功"

        except ImportError:
            return False, "pymongo未安裝"
        except Exception as e:
            return False, f"MongoDB連接失敗: {str(e)}"
    
    def _detect_redis(self) -> Tuple[bool, str]:
        """檢測Redis是否可用"""
        # 首先檢查是否啟用
        if not self.redis_enabled:
            return False, "Redis未啟用 (REDIS_ENABLED=false)"

        try:
            import redis

            # 構建連接參數
            connect_kwargs = {
                "host": self.redis_config["host"],
                "port": self.redis_config["port"],
                "db": self.redis_config["db"],
                "socket_timeout": self.redis_config["timeout"],
                "socket_connect_timeout": self.redis_config["timeout"]
            }

            # 如果有密碼，新增密碼
            if self.redis_config["password"]:
                connect_kwargs["password"] = self.redis_config["password"]

            client = redis.Redis(**connect_kwargs)

            # 測試連接
            client.ping()

            return True, "Redis連接成功"

        except ImportError:
            return False, "redis未安裝"
        except Exception as e:
            return False, f"Redis連接失敗: {str(e)}"
    
    def _detect_databases(self):
        """檢測所有資料庫"""
        self.logger.info("開始檢測資料庫可用性...")
        
        # 檢測MongoDB
        mongodb_available, mongodb_msg = self._detect_mongodb()
        self.mongodb_available = mongodb_available
        
        if mongodb_available:
            self.logger.info(f"MongoDB: {mongodb_msg}")
        else:
            self.logger.info(f"MongoDB: {mongodb_msg}")
        
        # 檢測Redis
        redis_available, redis_msg = self._detect_redis()
        self.redis_available = redis_available
        
        if redis_available:
            self.logger.info(f"Redis: {redis_msg}")
        else:
            self.logger.info(f"Redis: {redis_msg}")
        
        # 更新配置
        self._update_config_based_on_detection()
    
    def _update_config_based_on_detection(self):
        """根據檢測結果更新配置"""
        # 確定快取後端
        if self.redis_available:
            self.primary_backend = "redis"
        elif self.mongodb_available:
            self.primary_backend = "mongodb"
        else:
            self.primary_backend = "file"

        self.logger.info(f"主要快取後端: {self.primary_backend}")
    
    def _initialize_connections(self):
        """初始化資料庫連接"""
        # 初始化MongoDB連接
        if self.mongodb_available:
            try:
                import pymongo

                # 構建連接參數
                connect_kwargs = {
                    "host": self.mongodb_config["host"],
                    "port": self.mongodb_config["port"],
                    "serverSelectionTimeoutMS": self.mongodb_config["timeout"]
                }

                # 如果有使用者名和密碼，新增認證
                if self.mongodb_config["username"] and self.mongodb_config["password"]:
                    connect_kwargs.update({
                        "username": self.mongodb_config["username"],
                        "password": self.mongodb_config["password"],
                        "authSource": self.mongodb_config["auth_source"]
                    })

                self.mongodb_client = pymongo.MongoClient(**connect_kwargs)
                self.logger.info("MongoDB客戶端初始化成功")
            except Exception as e:
                self.logger.error(f"MongoDB客戶端初始化失敗: {e}")
                self.mongodb_available = False

        # 初始化Redis連接
        if self.redis_available:
            try:
                import redis

                # 構建連接參數
                connect_kwargs = {
                    "host": self.redis_config["host"],
                    "port": self.redis_config["port"],
                    "db": self.redis_config["db"],
                    "socket_timeout": self.redis_config["timeout"]
                }

                # 如果有密碼，新增密碼
                if self.redis_config["password"]:
                    connect_kwargs["password"] = self.redis_config["password"]

                self.redis_client = redis.Redis(**connect_kwargs)
                self.logger.info("Redis客戶端初始化成功")
            except Exception as e:
                self.logger.error(f"Redis客戶端初始化失敗: {e}")
                self.redis_available = False
    
    def get_mongodb_client(self):
        """取得MongoDB客戶端"""
        if self.mongodb_available and self.mongodb_client:
            return self.mongodb_client
        return None
    
    def get_redis_client(self):
        """取得Redis客戶端"""
        if self.redis_available and self.redis_client:
            return self.redis_client
        return None
    
    def is_mongodb_available(self) -> bool:
        """檢查MongoDB是否可用"""
        return self.mongodb_available
    
    def is_redis_available(self) -> bool:
        """檢查Redis是否可用"""
        return self.redis_available
    
    def is_database_available(self) -> bool:
        """檢查是否有任何資料庫可用"""
        return self.mongodb_available or self.redis_available
    
    def get_cache_backend(self) -> str:
        """取得當前快取後端"""
        return self.primary_backend

    def get_config(self) -> Dict[str, Any]:
        """取得配置資訊"""
        return {
            "mongodb": self.mongodb_config,
            "redis": self.redis_config,
            "primary_backend": self.primary_backend,
            "mongodb_available": self.mongodb_available,
            "redis_available": self.redis_available
        }

    def get_status_report(self) -> Dict[str, Any]:
        """取得狀態報告"""
        return {
            "database_available": self.is_database_available(),
            "mongodb": {
                "available": self.mongodb_available,
                "host": self.mongodb_config["host"],
                "port": self.mongodb_config["port"]
            },
            "redis": {
                "available": self.redis_available,
                "host": self.redis_config["host"],
                "port": self.redis_config["port"]
            },
            "cache_backend": self.get_cache_backend(),
            "fallback_enabled": True  # 總是啟用降級
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """取得快取統計資訊"""
        stats = {
            "mongodb_available": self.mongodb_available,
            "redis_available": self.redis_available,
            "redis_keys": 0,
            "redis_memory": "N/A"
        }

        # Redis統計
        if self.redis_available and self.redis_client:
            try:
                info = self.redis_client.info()
                stats["redis_keys"] = self.redis_client.dbsize()
                stats["redis_memory"] = info.get("used_memory_human", "N/A")
            except Exception as e:
                self.logger.error(f"取得Redis統計失敗: {e}")

        return stats

    def cache_clear_pattern(self, pattern: str) -> int:
        """清理匹配模式的快取"""
        cleared_count = 0

        if self.redis_available and self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    cleared_count += self.redis_client.delete(*keys)
            except Exception as e:
                self.logger.error(f"Redis快取清理失敗: {e}")

        return cleared_count


# 全局資料庫管理器實例
_database_manager = None

def get_database_manager() -> DatabaseManager:
    """取得全局資料庫管理器實例"""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager

def is_mongodb_available() -> bool:
    """檢查MongoDB是否可用"""
    return get_database_manager().is_mongodb_available()

def is_redis_available() -> bool:
    """檢查Redis是否可用"""
    return get_database_manager().is_redis_available()

def get_cache_backend() -> str:
    """取得當前快取後端"""
    return get_database_manager().get_cache_backend()

def get_mongodb_client():
    """取得MongoDB客戶端"""
    return get_database_manager().get_mongodb_client()

def get_redis_client():
    """取得Redis客戶端"""
    return get_database_manager().get_redis_client()
