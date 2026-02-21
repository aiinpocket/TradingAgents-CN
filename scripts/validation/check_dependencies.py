#!/usr/bin/env python3
"""
檢查和配置MongoDB等依賴項
確保系統可以在有或沒有MongoDB的情況下正常運行
"""

import sys
import os
import traceback
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def check_mongodb_availability():
    """檢查MongoDB是否可用"""
    logger.debug(f"🔍 檢查MongoDB依賴...")
    
    # 檢查pymongo是否安裝
    try:
        import pymongo
        logger.info(f"✅ pymongo 已安裝")
        pymongo_available = True
    except ImportError:
        logger.error(f"❌ pymongo 未安裝")
        pymongo_available = False
    
    # 檢查MongoDB服務是否運行
    mongodb_running = False
    if pymongo_available:
        try:
            from pymongo import MongoClient
            client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
            client.server_info()  # 觸發連接
            logger.info(f"✅ MongoDB 服務正在運行")
            mongodb_running = True
            client.close()
        except Exception as e:
            logger.error(f"❌ MongoDB 服務未運行: {e}")
            mongodb_running = False
    
    return pymongo_available, mongodb_running

def check_redis_availability():
    """檢查Redis是否可用"""
    logger.debug(f"\n🔍 檢查Redis依賴...")
    
    # 檢查redis是否安裝
    try:
        import redis
        logger.info(f"✅ redis 已安裝")
        redis_available = True
    except ImportError:
        logger.error(f"❌ redis 未安裝")
        redis_available = False
    
    # 檢查Redis服務是否運行
    redis_running = False
    if redis_available:
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
            r.ping()
            logger.info(f"✅ Redis 服務正在運行")
            redis_running = True
        except Exception as e:
            logger.error(f"❌ Redis 服務未運行: {e}")
            redis_running = False
    
    return redis_available, redis_running

def check_basic_dependencies():
    """檢查基本依賴"""
    logger.debug(f"\n🔍 檢查基本依賴...")
    
    required_packages = [
        'pandas',
        'yfinance', 
        'requests',
        'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} 已安裝")
        except ImportError:
            logger.error(f"❌ {package} 未安裝")
            missing_packages.append(package)
    
    return missing_packages

def create_fallback_config():
    """創建無數據庫的備用配置"""
    logger.info(f"\n⚙️ 創建備用配置...")
    
    fallback_config = {
        "cache": {
            "enabled": True,
            "backend": "file",  # 使用文件緩存而不是數據庫
            "file_cache_dir": "./tradingagents/dataflows/data_cache",
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
            "enabled": False,  # 禁用數據庫
            "mongodb": {
                "enabled": False
            },
            "redis": {
                "enabled": False
            }
        }
    }
    
    return fallback_config

def test_cache_without_database():
    """測試不使用數據庫的緩存功能"""
    logger.info(f"\n💾 測試文件緩存功能...")
    
    try:
        # 導入緩存管理器
        from tradingagents.dataflows.cache_manager import get_cache

        
        # 創建緩存實例
        cache = get_cache()
        logger.info(f"✅ 緩存實例創建成功: {type(cache).__name__}")
        
        # 測試基本功能
        test_data = "測試數據 - 無數據庫模式"
        cache_key = cache.save_stock_data(
            symbol="TEST",
            data=test_data,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="no_db_test"
        )
        logger.info(f"✅ 數據保存成功: {cache_key}")
        
        # 加載數據
        loaded_data = cache.load_stock_data(cache_key)
        if loaded_data == test_data:
            logger.info(f"✅ 數據加載成功，文件緩存工作正常")
            return True
        else:
            logger.error(f"❌ 數據加載失敗")
            return False
            
    except Exception as e:
        logger.error(f"❌ 緩存測試失敗: {e}")
        traceback.print_exc()
        return False

def generate_installation_guide():
    """生成安裝指南"""
    guide = """
# 依賴安裝指南

## 基本運行（無數據庫）
系統可以在沒有MongoDB和Redis的情況下正常運行，使用文件緩存。

### 必需依賴
```bash
pip install pandas yfinance requests
```

## 完整功能（包含數據庫）
如果需要企業級緩存和數據持久化功能：

### 1. 安裝Python包
```bash
pip install pymongo redis
```

### 2. 安裝MongoDB（可選）
#### Windows:
1. 下載MongoDB Community Server
2. 安裝並啟動服務
3. 默認端口：27017

#### 使用Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:4.4
```

### 3. 安裝Redis（可選）
#### Windows:
1. 下載Redis for Windows
2. 啟動redis-server
3. 默認端口：6379

#### 使用Docker:
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

## 配置說明

### 文件緩存模式（默認）
- 緩存存儲在本地文件系統
- 性能良好，適合單機使用
- 無需額外服務

### 數據庫模式（可選）
- MongoDB：數據持久化
- Redis：高性能緩存
- 適合生產環境和多實例部署

## 運行模式檢測
系統會自動檢測可用的服務：
1. 如果MongoDB/Redis可用，自動使用數據庫緩存
2. 如果不可用，自動降級到文件緩存
3. 功能完全兼容，性能略有差異
"""
    
    return guide

def main():
    """主函數"""
    logger.info(f"🔧 TradingAgents 依賴檢查和配置")
    logger.info(f"=")
    
    # 檢查基本依賴
    missing_packages = check_basic_dependencies()
    
    # 檢查數據庫依賴
    pymongo_available, mongodb_running = check_mongodb_availability()
    redis_available, redis_running = check_redis_availability()
    
    # 生成配置建議
    logger.info(f"\n📋 配置建議:")
    
    if missing_packages:
        logger.error(f"❌ 缺少必需依賴: {', '.join(missing_packages)}")
        logger.info(f"請運行: pip install ")
        return False
    
    if not pymongo_available and not redis_available:
        logger.info(f"ℹ️ 數據庫依賴未安裝，將使用文件緩存模式")
        logger.info(f"✅ 系統可以正常運行，性能良好")
        
    elif not mongodb_running and not redis_running:
        logger.info(f"ℹ️ 數據庫服務未運行，將使用文件緩存模式")
        logger.info(f"✅ 系統可以正常運行")
        
    else:
        logger.info(f"🚀 數據庫服務可用，將使用高性能緩存模式")
        if mongodb_running:
            logger.info(f"  ✅ MongoDB: 數據持久化")
        if redis_running:
            logger.info(f"  ✅ Redis: 高性能緩存")
    
    # 測試緩存功能
    cache_works = test_cache_without_database()
    
    # 生成安裝指南
    guide = generate_installation_guide()
    with open("DEPENDENCY_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide)
    logger.info(f"\n📝 已生成依賴安裝指南: DEPENDENCY_GUIDE.md")
    
    # 總結
    logger.info(f"\n")
    logger.info(f"📊 檢查結果總結:")
    logger.error(f"  基本依賴: {'✅ 完整' if not missing_packages else '❌ 缺失'}")
    logger.error(f"  MongoDB: {'✅ 可用' if mongodb_running else '❌ 不可用'}")
    logger.error(f"  Redis: {'✅ 可用' if redis_running else '❌ 不可用'}")
    logger.error(f"  緩存功能: {'✅ 正常' if cache_works else '❌ 異常'}")
    
    if not missing_packages and cache_works:
        logger.info(f"\n🎉 系統可以正常運行！")
        if not mongodb_running and not redis_running:
            logger.info(f"💡 提示: 安裝MongoDB和Redis可以獲得更好的性能")
        return True
    else:
        logger.warning(f"\n⚠️ 需要解決依賴問題才能正常運行")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
