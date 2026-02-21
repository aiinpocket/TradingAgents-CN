#!/usr/bin/env python3
"""
系統初始化指令碼
初始化資料庫配置，確保系統可以在有或沒有資料庫的情況下執行
"""

import sys
import os
import json
from pathlib import Path

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def initialize_system():
    """初始化系統"""
    logger.info(f" TradingAgents 系統初始化")
    logger.info(f"=")
    
    # 1. 建立配置目錄
    logger.info(f"\n 建立配置目錄...")
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)
    logger.info(f" 配置目錄: {config_dir}")
    
    # 2. 建立資料快取目錄
    logger.info(f"\n 建立快取目錄...")
    cache_dir = project_root / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f" 快取目錄: {cache_dir}")
    
    # 3. 檢查並建立資料庫配置檔
    logger.info(f"\n 配置資料庫設定...")
    config_file = config_dir / "database_config.json"
    
    if config_file.exists():
        logger.info(f"[INFO]配置檔已存在: {config_file}")
        
        # 讀取現有配置
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            logger.info(f" 現有配置載入成功")
        except Exception as e:
            logger.error(f" 現有配置讀取失敗: {e}")
            existing_config = None
    else:
        existing_config = None
    
    # 4. 檢測資料庫可用性
    logger.debug(f"\n 檢測資料庫可用性...")
    
    # 檢測MongoDB
    mongodb_available = False
    try:
        import pymongo
        from pymongo import MongoClient
        
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
        client.server_info()
        client.close()
        mongodb_available = True
        logger.info(f" MongoDB: 可用")
    except ImportError:
        logger.error(f" MongoDB: pymongo未安裝")
    except Exception as e:
        logger.error(f" MongoDB: 連接失敗 - {e}")
    
    # 檢測Redis
    redis_available = False
    try:
        import redis
        
        r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
        r.ping()
        redis_available = True
        logger.info(f" Redis: 可用")
    except ImportError:
        logger.error(f" Redis: redis未安裝")
    except Exception as e:
        logger.error(f" Redis: 連接失敗 - {e}")
    
    # 5. 生成配置
    logger.info(f"\n 生成系統配置...")
    
    # 確定主要快取後端
    if redis_available:
        primary_backend = "redis"
        logger.info(f" 選擇Redis作為主要快取後端")
    elif mongodb_available:
        primary_backend = "mongodb"
        logger.info(f" 選擇MongoDB作為主要快取後端")
    else:
        primary_backend = "file"
        logger.info(f" 選擇檔案作為主要快取後端")
    
    # 建立配置
    config = {
        "database": {
            "enabled": mongodb_available or redis_available,
            "auto_detect": True,
            "fallback_to_file": True,
            "mongodb": {
                "enabled": mongodb_available,
                "host": "localhost",
                "port": 27017,
                "database": "tradingagents",
                "timeout": 2000,
                "auto_detect": True
            },
            "redis": {
                "enabled": redis_available,
                "host": "localhost",
                "port": 6379,
                "timeout": 2,
                "auto_detect": True
            }
        },
        "cache": {
            "enabled": True,
            "primary_backend": primary_backend,
            "fallback_enabled": True,
            "file_cache": {
                "enabled": True,
                "directory": "data/cache",
                "max_size_mb": 1000,
                "cleanup_interval_hours": 24
            },
            "ttl_settings": {
                "us_stock_data": 7200,      # 2小時
                "us_news": 21600,           # 6小時
                "us_fundamentals": 86400    # 24小時
            }
        },
        "performance": {
            "enable_compression": True,
            "enable_async_cache": False,
            "max_concurrent_requests": 10
        },
        "logging": {
            "level": "INFO",
            "log_database_operations": True,
            "log_cache_operations": False
        }
    }
    
    # 6. 保存配置
    logger.info(f"\n 保存配置檔...")
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f" 配置已保存: {config_file}")
    except Exception as e:
        logger.error(f" 配置保存失敗: {e}")
        return False
    
    # 7. 測試系統
    logger.info(f"\n 測試系統初始化...")
    try:
        # 測試資料庫管理器
        from tradingagents.config.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        status = db_manager.get_status_report()
        
        logger.info(f" 系統狀態:")
        logger.error(f"  資料庫可用: {' 是' if status['database_available'] else ' 否'}")
        logger.error(f"  MongoDB: {' 可用' if status['mongodb']['available'] else ' 不可用'}")
        logger.error(f"  Redis: {' 可用' if status['redis']['available'] else ' 不可用'}")
        logger.info(f"  快取後端: {status['cache_backend']}")
        
        # 測試快取系統
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        performance_mode = cache.get_performance_mode()
        logger.info(f"  性能模式: {performance_mode}")
        
        # 簡單功能測試
        test_key = cache.save_stock_data("INIT_TEST", "初始化測試資料", data_source="init")
        test_data = cache.load_stock_data(test_key)
        
        if test_data == "初始化測試資料":
            logger.info(f" 快取功能測試通過")
        else:
            logger.error(f" 快取功能測試失敗")
            return False
        
    except Exception as e:
        logger.error(f" 系統測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 8. 生成使用指南
    logger.info(f"\n 生成使用指南...")
    
    usage_guide = f"""# TradingAgents 系統配置

## 當前配置

- **資料庫可用**: {'是' if mongodb_available or redis_available else '否'}
- **MongoDB**: {' 可用' if mongodb_available else ' 不可用'}
- **Redis**: {' 可用' if redis_available else ' 不可用'}
- **主要快取後端**: {primary_backend}
- **性能模式**: {cache.get_performance_mode() if 'cache' in locals() else '未知'}

## 系統特性

### 自動降級支援
- 系統會自動檢測可用的資料庫服務
- 如果資料庫不可用，自動使用檔案快取
- 保證系統在任何環境下都能正常執行

### 性能優化
- 智能快取策略，減少API呼叫
- 支援多種資料類型的TTL管理
- 自動清理過期快取

## 使用方法

### 基本使用
```python
from tradingagents.dataflows.integrated_cache import get_cache

# 取得快取實例
cache = get_cache()

# 保存資料
cache_key = cache.save_stock_data("AAPL", stock_data)

# 載入資料
data = cache.load_stock_data(cache_key)
```

### 檢查系統狀態
```bash
python scripts/validation/check_system_status.py
```

## 性能提升建議

"""

    if not mongodb_available and not redis_available:
        usage_guide += """
### 安裝資料庫以獲得更好性能

1. **安裝Python依賴**:
   ```bash
   pip install pymongo redis
   ```

2. **啟動MongoDB** (可選):
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:4.4
   ```

3. **啟動Redis** (可選):
   ```bash
   docker run -d -p 6379:6379 --name redis redis:alpine
   ```

4. **重新初始化系統**:
   ```bash
   python scripts/setup/initialize_system.py
   ```
"""
    else:
        usage_guide += """
### 系統已優化
 資料庫服務可用，系統執行在最佳性能模式
"""
    
    usage_file = project_root / "SYSTEM_SETUP_GUIDE.md"
    try:
        with open(usage_file, 'w', encoding='utf-8') as f:
            f.write(usage_guide)
        logger.info(f" 使用指南已生成: {usage_file}")
    except Exception as e:
        logger.error(f" 使用指南生成失敗: {e}")
    
    # 9. 總結
    logger.info(f"\n")
    logger.info(f" 系統初始化完成!")
    logger.info(f"\n 初始化結果:")
    logger.info(f"  配置檔:  已建立")
    logger.info(f"  快取目錄:  已建立")
    logger.info(f"  資料庫檢測:  已完成")
    logger.info(f"  系統測試:  已通過")
    logger.info(f"  使用指南:  已生成")
    
    if mongodb_available or redis_available:
        logger.info(f"\n 系統執行在高性能模式!")
    else:
        logger.info(f"\n 系統執行在檔案快取模式")
        logger.info(f" 安裝MongoDB/Redis可獲得更好性能")
    
    logger.info(f"\n 下一步:")
    logger.info(f"1. 執行系統狀態檢查: python scripts/validation/check_system_status.py")
    logger.info(f"2. 查看使用指南: {usage_file}")
    logger.info(f"3. 開始使用TradingAgents!")
    
    return True

def main():
    """主函數"""
    try:
        success = initialize_system()
        return success
    except Exception as e:
        logger.error(f" 系統初始化失敗: {e}")
        import traceback

        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
