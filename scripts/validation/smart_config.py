#!/usr/bin/env python3
"""
智能配置系統 - 自動檢測和配置數據庫依賴
確保系統在有或沒有MongoDB/Redis的情況下都能正常運行
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

class SmartConfigManager:
    """智能配置管理器 - 自動檢測可用服務並配置系統"""
    
    def __init__(self):
        self.config = {}
        self.mongodb_available = False
        self.redis_available = False
        self.detection_results = {}
        
        # 設置日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 執行檢測
        self._detect_services()
        self._generate_config()
    
    def _detect_mongodb(self) -> Tuple[bool, str]:
        """檢測MongoDB是否可用"""
        try:
            import pymongo
            from pymongo import MongoClient
            
            # 嘗試連接MongoDB
            client = MongoClient(
                'localhost', 
                27017, 
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000
            )
            client.server_info()  # 觸發連接測試
            client.close()
            
            return True, "MongoDB服務正在運行"
            
        except ImportError:
            return False, "pymongo未安裝"
        except Exception as e:
            return False, f"MongoDB連接失敗: {str(e)}"
    
    def _detect_redis(self) -> Tuple[bool, str]:
        """檢測Redis是否可用"""
        try:
            import redis

            
            # 嘗試連接Redis
            r = redis.Redis(
                host='localhost', 
                port=6379, 
                socket_timeout=2,
                socket_connect_timeout=2
            )
            r.ping()
            
            return True, "Redis服務正在運行"
            
        except ImportError:
            return False, "redis未安裝"
        except Exception as e:
            return False, f"Redis連接失敗: {str(e)}"
    
    def _detect_services(self):
        """檢測所有服務"""
        logger.debug(f"🔍 檢測系統服務...")
        
        # 檢測MongoDB
        self.mongodb_available, mongodb_msg = self._detect_mongodb()
        self.detection_results['mongodb'] = {
            'available': self.mongodb_available,
            'message': mongodb_msg
        }
        
        if self.mongodb_available:
            logger.info(f"✅ MongoDB: {mongodb_msg}")
        else:
            logger.error(f"❌ MongoDB: {mongodb_msg}")
        
        # 檢測Redis
        self.redis_available, redis_msg = self._detect_redis()
        self.detection_results['redis'] = {
            'available': self.redis_available,
            'message': redis_msg
        }
        
        if self.redis_available:
            logger.info(f"✅ Redis: {redis_msg}")
        else:
            logger.error(f"❌ Redis: {redis_msg}")
    
    def _generate_config(self):
        """根據檢測結果生成配置"""
        logger.info(f"\n⚙️ 生成智能配置...")
        
        # 基礎配置
        self.config = {
            "cache": {
                "enabled": True,
                "primary_backend": "file",  # 默認使用文件緩存
                "fallback_enabled": True,
                "ttl_settings": {
                    "us_stock_data": 7200,      # 2小時
                    "china_stock_data": 3600,   # 1小時
                    "us_news": 21600,           # 6小時
                    "china_news": 14400,        # 4小時
                    "us_fundamentals": 86400,   # 24小時
                    "china_fundamentals": 43200, # 12小時
                }
            },
            "database": {
                "mongodb": {
                    "enabled": self.mongodb_available,
                    "host": "localhost",
                    "port": 27017,
                    "database": "tradingagents",
                    "timeout": 2000
                },
                "redis": {
                    "enabled": self.redis_available,
                    "host": "localhost",
                    "port": 6379,
                    "timeout": 2
                }
            },
            "detection_results": self.detection_results
        }
        
        # 根據可用服務調整緩存策略
        if self.redis_available and self.mongodb_available:
            self.config["cache"]["primary_backend"] = "redis"
            self.config["cache"]["secondary_backend"] = "mongodb"
            self.config["cache"]["tertiary_backend"] = "file"
            logger.info(f"🚀 配置模式: Redis + MongoDB + 文件緩存")
            
        elif self.redis_available:
            self.config["cache"]["primary_backend"] = "redis"
            self.config["cache"]["secondary_backend"] = "file"
            logger.info(f"⚡ 配置模式: Redis + 文件緩存")
            
        elif self.mongodb_available:
            self.config["cache"]["primary_backend"] = "mongodb"
            self.config["cache"]["secondary_backend"] = "file"
            logger.info(f"💾 配置模式: MongoDB + 文件緩存")
            
        else:
            self.config["cache"]["primary_backend"] = "file"
            logger.info(f"📁 配置模式: 純文件緩存")
    
    def get_config(self) -> Dict[str, Any]:
        """獲取配置"""
        return self.config.copy()
    
    def save_config(self, config_path: str = "smart_config.json"):
        """保存配置到文件"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ 配置已保存到: {config_path}")
        except Exception as e:
            logger.error(f"❌ 配置保存失敗: {e}")
    
    def load_config(self, config_path: str = "smart_config.json") -> bool:
        """從文件加載配置"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"✅ 配置已從文件加載: {config_path}")
                return True
        except Exception as e:
            logger.error(f"❌ 配置加載失敗: {e}")
        return False
    
    def get_cache_backend_info(self) -> Dict[str, Any]:
        """獲取緩存後端信息"""
        return {
            "primary_backend": self.config["cache"]["primary_backend"],
            "mongodb_available": self.mongodb_available,
            "redis_available": self.redis_available,
            "fallback_enabled": self.config["cache"]["fallback_enabled"]
        }
    
    def print_status(self):
        """打印系統狀態"""
        logger.info(f"\n📊 系統狀態報告:")
        logger.info(f"=")
        
        # 服務狀態
        logger.info(f"🔧 服務狀態:")
        for service, info in self.detection_results.items():
            status = "✅ 可用" if info['available'] else "❌ 不可用"
            logger.info(f"  {service.upper()}: {status} - {info['message']}")
        
        # 緩存配置
        cache_info = self.get_cache_backend_info()
        logger.info(f"\n💾 緩存配置:")
        logger.info(f"  主要後端: {cache_info['primary_backend']}")
        logger.info(f"  降級支持: {'啟用' if cache_info['fallback_enabled'] else '禁用'}")
        
        # 運行模式
        if self.mongodb_available and self.redis_available:
            mode = "🚀 高性能模式 (Redis + MongoDB + 文件)"
        elif self.redis_available:
            mode = "⚡ 快速模式 (Redis + 文件)"
        elif self.mongodb_available:
            mode = "💾 持久化模式 (MongoDB + 文件)"
        else:
            mode = "📁 基礎模式 (純文件緩存)"
        
        logger.info(f"  運行模式: {mode}")
        
        # 性能預期
        logger.info(f"\n📈 性能預期:")
        if self.redis_available:
            logger.info(f"  緩存性能: 極快 (<0.001秒)")
        else:
            logger.info(f"  緩存性能: 很快 (<0.01秒)")
        logger.info(f"  相比API調用: 99%+ 性能提升")


# 全局配置管理器實例
_config_manager = None

def get_smart_config() -> SmartConfigManager:
    """獲取全局智能配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SmartConfigManager()
    return _config_manager

def get_config() -> Dict[str, Any]:
    """獲取系統配置"""
    return get_smart_config().get_config()

def is_mongodb_available() -> bool:
    """檢查MongoDB是否可用"""
    return get_smart_config().mongodb_available

def is_redis_available() -> bool:
    """檢查Redis是否可用"""
    return get_smart_config().redis_available

def get_cache_backend() -> str:
    """獲取當前緩存後端"""
    config = get_config()
    return config["cache"]["primary_backend"]


def main():
    """主函數 - 演示智能配置系統"""
    logger.info(f"🔧 TradingAgents 智能配置系統")
    logger.info(f"=")
    
    # 創建配置管理器
    config_manager = get_smart_config()
    
    # 顯示狀態
    config_manager.print_status()
    
    # 保存配置
    config_manager.save_config()
    
    # 生成環境變量設置腳本
    config = config_manager.get_config()
    
    env_script = f"""# 環境變量配置腳本
# 根據檢測結果自動生成

# 緩存配置
export CACHE_BACKEND="{config['cache']['primary_backend']}"
export CACHE_ENABLED="true"
export FALLBACK_ENABLED="{str(config['cache']['fallback_enabled']).lower()}"

# 數據庫配置
export MONGODB_ENABLED="{str(config['database']['mongodb']['enabled']).lower()}"
export REDIS_ENABLED="{str(config['database']['redis']['enabled']).lower()}"

# TTL設置
export US_STOCK_TTL="{config['cache']['ttl_settings']['us_stock_data']}"
export CHINA_STOCK_TTL="{config['cache']['ttl_settings']['china_stock_data']}"

echo "✅ 環境變量已設置"
echo "緩存後端: $CACHE_BACKEND"
echo "MongoDB: $MONGODB_ENABLED"
echo "Redis: $REDIS_ENABLED"
"""
    
    with open("set_env.sh", "w", encoding="utf-8") as f:
        f.write(env_script)
    
    logger.info(f"\n✅ 環境配置腳本已生成: set_env.sh")
    
    # 生成PowerShell版本
    ps_script = f"""# PowerShell環境變量配置腳本
# 根據檢測結果自動生成

# 緩存配置
$env:CACHE_BACKEND = "{config['cache']['primary_backend']}"
$env:CACHE_ENABLED = "true"
$env:FALLBACK_ENABLED = "{str(config['cache']['fallback_enabled']).lower()}"

# 數據庫配置
$env:MONGODB_ENABLED = "{str(config['database']['mongodb']['enabled']).lower()}"
$env:REDIS_ENABLED = "{str(config['database']['redis']['enabled']).lower()}"

# TTL設置
$env:US_STOCK_TTL = "{config['cache']['ttl_settings']['us_stock_data']}"
$env:CHINA_STOCK_TTL = "{config['cache']['ttl_settings']['china_stock_data']}"

Write-Host "✅ 環境變量已設置" -ForegroundColor Green
Write-Host "緩存後端: $env:CACHE_BACKEND" -ForegroundColor Cyan
Write-Host "MongoDB: $env:MONGODB_ENABLED" -ForegroundColor Cyan
Write-Host "Redis: $env:REDIS_ENABLED" -ForegroundColor Cyan
"""
    
    with open("set_env.ps1", "w", encoding="utf-8") as f:
        f.write(ps_script)
    
    logger.info(f"✅ PowerShell配置腳本已生成: set_env.ps1")
    
    logger.info(f"\n🎯 下一步:")
    logger.info(f"1. 運行: python test_with_smart_config.py")
    logger.info(f"2. 或者: .\set_env.ps1 (設置環境變量)")
    logger.info(f"3. 然後: python quick_test.py")


if __name__ == "__main__":
    main()
