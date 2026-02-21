#!/usr/bin/env python3
"""
集成快取管理器
結合原有快取系統和新的自適應資料庫支持
提供向後兼容的介面
"""

from typing import Any, Dict, Optional

# 匯入統一日誌系統
from tradingagents.utils.logging_init import setup_dataflow_logging

# 匯入原有快取系統
from .cache_manager import StockDataCache

# 匯入自適應快取系統
try:
    from .adaptive_cache import get_cache_system
    from ..config.database_manager import get_database_manager
    ADAPTIVE_CACHE_AVAILABLE = True
except ImportError:
    ADAPTIVE_CACHE_AVAILABLE = False

class IntegratedCacheManager:
    """集成快取管理器 - 智能選擇快取策略"""
    
    def __init__(self, cache_dir: str = None):
        self.logger = setup_dataflow_logging()
        
        # 初始化原有快取系統（作為備用）
        self.legacy_cache = StockDataCache(cache_dir)
        
        # 嘗試初始化自適應快取系統
        self.adaptive_cache = None
        self.use_adaptive = False
        
        if ADAPTIVE_CACHE_AVAILABLE:
            try:
                self.adaptive_cache = get_cache_system()
                self.db_manager = get_database_manager()
                self.use_adaptive = True
                self.logger.info("自適應快取系統已啟用")
            except Exception as e:
                self.logger.warning(f"自適應快取系統初始化失敗，使用傳統快取: {e}")
                self.use_adaptive = False
        else:
            self.logger.info("自適應快取系統不可用，使用傳統檔案快取")
        
        # 顯示當前配置
        self._log_cache_status()
    
    def _log_cache_status(self):
        """記錄快取狀態"""
        if self.use_adaptive:
            backend = self.adaptive_cache.primary_backend
            mongodb_available = self.db_manager.is_mongodb_available()
            redis_available = self.db_manager.is_redis_available()
            
            self.logger.info("快取配置:")
            self.logger.info(f"  主要後端: {backend}")
            self.logger.info(f"  MongoDB: {'可用' if mongodb_available else '不可用'}")
            self.logger.info(f"  Redis: {'可用' if redis_available else '不可用'}")
            self.logger.info(f"  降級支持: {'啟用' if self.adaptive_cache.fallback_enabled else '禁用'}")
        else:
            self.logger.info("使用傳統檔案快取系統")
    
    def save_stock_data(self, symbol: str, data: Any, start_date: str = None, 
                       end_date: str = None, data_source: str = "default") -> str:
        """
        保存股票資料到快取
        
        Args:
            symbol: 股票代碼
            data: 股票資料
            start_date: 開始日期
            end_date: 結束日期
            data_source: 資料來源
            
        Returns:
            快取鍵
        """
        if self.use_adaptive:
            # 使用自適應快取系統
            return self.adaptive_cache.save_data(
                symbol=symbol,
                data=data,
                start_date=start_date or "",
                end_date=end_date or "",
                data_source=data_source,
                data_type="stock_data"
            )
        else:
            # 使用傳統快取系統
            return self.legacy_cache.save_stock_data(
                symbol=symbol,
                data=data,
                start_date=start_date,
                end_date=end_date,
                data_source=data_source
            )
    
    def load_stock_data(self, cache_key: str) -> Optional[Any]:
        """
        從快取載入股票資料
        
        Args:
            cache_key: 快取鍵
            
        Returns:
            股票資料或None
        """
        if self.use_adaptive:
            # 使用自適應快取系統
            return self.adaptive_cache.load_data(cache_key)
        else:
            # 使用傳統快取系統
            return self.legacy_cache.load_stock_data(cache_key)
    
    def find_cached_stock_data(self, symbol: str, start_date: str = None, 
                              end_date: str = None, data_source: str = "default") -> Optional[str]:
        """
        查找快取的股票資料
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            data_source: 資料來源
            
        Returns:
            快取鍵或None
        """
        if self.use_adaptive:
            # 使用自適應快取系統
            return self.adaptive_cache.find_cached_data(
                symbol=symbol,
                start_date=start_date or "",
                end_date=end_date or "",
                data_source=data_source,
                data_type="stock_data"
            )
        else:
            # 使用傳統快取系統
            return self.legacy_cache.find_cached_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data_source=data_source
            )
    
    def save_news_data(self, symbol: str, data: Any, data_source: str = "default") -> str:
        """保存新聞資料"""
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
        """載入新聞資料"""
        if self.use_adaptive:
            return self.adaptive_cache.load_data(cache_key)
        else:
            return self.legacy_cache.load_news_data(cache_key)
    
    def save_fundamentals_data(self, symbol: str, data: Any, data_source: str = "default") -> str:
        """保存基本面資料"""
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
        """載入基本面資料"""
        if self.use_adaptive:
            return self.adaptive_cache.load_data(cache_key)
        else:
            return self.legacy_cache.load_fundamentals_data(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """取得快取統計資訊"""
        if self.use_adaptive:
            # 取得自適應快取統計
            adaptive_stats = self.adaptive_cache.get_cache_stats()
            
            # 添加傳統快取統計
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
            # 只返回傳統快取統計
            legacy_stats = self.legacy_cache.get_cache_stats()
            return {
                "cache_system": "legacy",
                "legacy_cache": legacy_stats,
                "database_available": False,
                "mongodb_available": False,
                "redis_available": False
            }
    
    def clear_expired_cache(self):
        """清理過期快取"""
        if self.use_adaptive:
            self.adaptive_cache.clear_expired_cache()
        
        # 總是清理傳統快取
        self.legacy_cache.clear_expired_cache()
    
    def get_cache_backend_info(self) -> Dict[str, Any]:
        """取得快取後端資訊"""
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
        """檢查資料庫是否可用"""
        if self.use_adaptive:
            return self.db_manager.is_database_available()
        return False
    
    def get_performance_mode(self) -> str:
        """取得性能模式"""
        if not self.use_adaptive:
            return "基礎模式 (檔案快取)"
        
        mongodb_available = self.db_manager.is_mongodb_available()
        redis_available = self.db_manager.is_redis_available()
        
        if redis_available and mongodb_available:
            return "高性能模式 (Redis + MongoDB + 檔案)"
        elif redis_available:
            return "快速模式 (Redis + 檔案)"
        elif mongodb_available:
            return "持久化模式 (MongoDB + 檔案)"
        else:
            return "標準模式 (智能檔案快取)"


# 全局集成快取管理器實例
_integrated_cache = None

def get_cache() -> IntegratedCacheManager:
    """取得全局集成快取管理器實例"""
    global _integrated_cache
    if _integrated_cache is None:
        _integrated_cache = IntegratedCacheManager()
    return _integrated_cache

# 向後兼容的函數
def get_stock_cache():
    """向後兼容：取得股票快取"""
    return get_cache()

def create_cache_manager(cache_dir: str = None):
    """向後兼容：創建快取管理器"""
    return IntegratedCacheManager(cache_dir)
