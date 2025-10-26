#!/usr/bin/env python3
"""
集成緩存管理器
結合原有緩存系統和新的自適應數據庫支持
提供向後兼容的接口
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd

# 導入統一日誌系統
from tradingagents.utils.logging_init import setup_dataflow_logging

# 導入原有緩存系統
from .cache_manager import StockDataCache

# 導入自適應緩存系統
try:
    from .adaptive_cache import get_cache_system
    from ..config.database_manager import get_database_manager
    ADAPTIVE_CACHE_AVAILABLE = True
except ImportError:
    ADAPTIVE_CACHE_AVAILABLE = False

class IntegratedCacheManager:
    """集成緩存管理器 - 智能選擇緩存策略"""
    
    def __init__(self, cache_dir: str = None):
        self.logger = setup_dataflow_logging()
        
        # 初始化原有緩存系統（作為备用）
        self.legacy_cache = StockDataCache(cache_dir)
        
        # 嘗試初始化自適應緩存系統
        self.adaptive_cache = None
        self.use_adaptive = False
        
        if ADAPTIVE_CACHE_AVAILABLE:
            try:
                self.adaptive_cache = get_cache_system()
                self.db_manager = get_database_manager()
                self.use_adaptive = True
                self.logger.info("✅ 自適應緩存系統已啟用")
            except Exception as e:
                self.logger.warning(f"自適應緩存系統初始化失败，使用傳統緩存: {e}")
                self.use_adaptive = False
        else:
            self.logger.info("自適應緩存系統不可用，使用傳統文件緩存")
        
        # 顯示當前配置
        self._log_cache_status()
    
    def _log_cache_status(self):
        """記錄緩存狀態"""
        if self.use_adaptive:
            backend = self.adaptive_cache.primary_backend
            mongodb_available = self.db_manager.is_mongodb_available()
            redis_available = self.db_manager.is_redis_available()
            
            self.logger.info(f"📊 緩存配置:")
            self.logger.info(f"  主要後端: {backend}")
            self.logger.info(f"  MongoDB: {'✅ 可用' if mongodb_available else '❌ 不可用'}")
            self.logger.info(f"  Redis: {'✅ 可用' if redis_available else '❌ 不可用'}")
            self.logger.info(f"  降級支持: {'✅ 啟用' if self.adaptive_cache.fallback_enabled else '❌ 禁用'}")
        else:
            self.logger.info("📁 使用傳統文件緩存系統")
    
    def save_stock_data(self, symbol: str, data: Any, start_date: str = None, 
                       end_date: str = None, data_source: str = "default") -> str:
        """
        保存股票數據到緩存
        
        Args:
            symbol: 股票代碼
            data: 股票數據
            start_date: 開始日期
            end_date: 結束日期
            data_source: 數據源
            
        Returns:
            緩存键
        """
        if self.use_adaptive:
            # 使用自適應緩存系統
            return self.adaptive_cache.save_data(
                symbol=symbol,
                data=data,
                start_date=start_date or "",
                end_date=end_date or "",
                data_source=data_source,
                data_type="stock_data"
            )
        else:
            # 使用傳統緩存系統
            return self.legacy_cache.save_stock_data(
                symbol=symbol,
                data=data,
                start_date=start_date,
                end_date=end_date,
                data_source=data_source
            )
    
    def load_stock_data(self, cache_key: str) -> Optional[Any]:
        """
        從緩存加載股票數據
        
        Args:
            cache_key: 緩存键
            
        Returns:
            股票數據或None
        """
        if self.use_adaptive:
            # 使用自適應緩存系統
            return self.adaptive_cache.load_data(cache_key)
        else:
            # 使用傳統緩存系統
            return self.legacy_cache.load_stock_data(cache_key)
    
    def find_cached_stock_data(self, symbol: str, start_date: str = None, 
                              end_date: str = None, data_source: str = "default") -> Optional[str]:
        """
        查找緩存的股票數據
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            data_source: 數據源
            
        Returns:
            緩存键或None
        """
        if self.use_adaptive:
            # 使用自適應緩存系統
            return self.adaptive_cache.find_cached_data(
                symbol=symbol,
                start_date=start_date or "",
                end_date=end_date or "",
                data_source=data_source,
                data_type="stock_data"
            )
        else:
            # 使用傳統緩存系統
            return self.legacy_cache.find_cached_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data_source=data_source
            )
    
    def save_news_data(self, symbol: str, data: Any, data_source: str = "default") -> str:
        """保存新聞數據"""
        if self.use_adaptive:
            return self.adaptive_cache.save_data(
                symbol=symbol,
                data=data,
                data_source=data_source,
                data_type="news_data"
            )
        else:
            return self.legacy_cache.save_news_data(symbol, data, data_source)
    
    def load_news_data(self, cache_key: str) -> Optional[Any]:
        """加載新聞數據"""
        if self.use_adaptive:
            return self.adaptive_cache.load_data(cache_key)
        else:
            return self.legacy_cache.load_news_data(cache_key)
    
    def save_fundamentals_data(self, symbol: str, data: Any, data_source: str = "default") -> str:
        """保存基本面數據"""
        if self.use_adaptive:
            return self.adaptive_cache.save_data(
                symbol=symbol,
                data=data,
                data_source=data_source,
                data_type="fundamentals_data"
            )
        else:
            return self.legacy_cache.save_fundamentals_data(symbol, data, data_source)
    
    def load_fundamentals_data(self, cache_key: str) -> Optional[Any]:
        """加載基本面數據"""
        if self.use_adaptive:
            return self.adaptive_cache.load_data(cache_key)
        else:
            return self.legacy_cache.load_fundamentals_data(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取緩存統計信息"""
        if self.use_adaptive:
            # 獲取自適應緩存統計
            adaptive_stats = self.adaptive_cache.get_cache_stats()
            
            # 添加傳統緩存統計
            legacy_stats = self.legacy_cache.get_cache_stats()
            
            return {
                "cache_system": "adaptive",
                "adaptive_cache": adaptive_stats,
                "legacy_cache": legacy_stats,
                "database_available": self.db_manager.is_database_available(),
                "mongodb_available": self.db_manager.is_mongodb_available(),
                "redis_available": self.db_manager.is_redis_available()
            }
        else:
            # 只返回傳統緩存統計
            legacy_stats = self.legacy_cache.get_cache_stats()
            return {
                "cache_system": "legacy",
                "legacy_cache": legacy_stats,
                "database_available": False,
                "mongodb_available": False,
                "redis_available": False
            }
    
    def clear_expired_cache(self):
        """清理過期緩存"""
        if self.use_adaptive:
            self.adaptive_cache.clear_expired_cache()
        
        # 总是清理傳統緩存
        self.legacy_cache.clear_expired_cache()
    
    def get_cache_backend_info(self) -> Dict[str, Any]:
        """獲取緩存後端信息"""
        if self.use_adaptive:
            return {
                "system": "adaptive",
                "primary_backend": self.adaptive_cache.primary_backend,
                "fallback_enabled": self.adaptive_cache.fallback_enabled,
                "mongodb_available": self.db_manager.is_mongodb_available(),
                "redis_available": self.db_manager.is_redis_available()
            }
        else:
            return {
                "system": "legacy",
                "primary_backend": "file",
                "fallback_enabled": False,
                "mongodb_available": False,
                "redis_available": False
            }
    
    def is_database_available(self) -> bool:
        """檢查數據庫是否可用"""
        if self.use_adaptive:
            return self.db_manager.is_database_available()
        return False
    
    def get_performance_mode(self) -> str:
        """獲取性能模式"""
        if not self.use_adaptive:
            return "基础模式 (文件緩存)"
        
        mongodb_available = self.db_manager.is_mongodb_available()
        redis_available = self.db_manager.is_redis_available()
        
        if redis_available and mongodb_available:
            return "高性能模式 (Redis + MongoDB + 文件)"
        elif redis_available:
            return "快速模式 (Redis + 文件)"
        elif mongodb_available:
            return "持久化模式 (MongoDB + 文件)"
        else:
            return "標準模式 (智能文件緩存)"


# 全局集成緩存管理器實例
_integrated_cache = None

def get_cache() -> IntegratedCacheManager:
    """獲取全局集成緩存管理器實例"""
    global _integrated_cache
    if _integrated_cache is None:
        _integrated_cache = IntegratedCacheManager()
    return _integrated_cache

# 向後兼容的函數
def get_stock_cache():
    """向後兼容：獲取股票緩存"""
    return get_cache()

def create_cache_manager(cache_dir: str = None):
    """向後兼容：創建緩存管理器"""
    return IntegratedCacheManager(cache_dir)
