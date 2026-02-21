#!/usr/bin/env python3
"""
資料庫初始化指令碼
建立MongoDB集合和索引，初始化Redis快取結構
"""

import os
import sys
from datetime import datetime

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 新增項目根目錄到路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def init_mongodb():
    """初始化MongoDB資料庫"""
    logger.info(f" 初始化MongoDB資料庫...")
    
    try:
        from tradingagents.config.database_manager import get_database_manager

        db_manager = get_database_manager()

        if not db_manager.is_mongodb_available():
            logger.error(f" MongoDB未連接，請先啟動MongoDB服務")
            return False

        mongodb_client = db_manager.get_mongodb_client()
        db = mongodb_client[db_manager.mongodb_config["database"]]
        
        # 建立股票資料集合和索引
        logger.info(f" 建立股票資料集合...")
        stock_data_collection = db.stock_data
        
        # 建立索引
        stock_data_collection.create_index([("symbol", 1), ("market_type", 1)], unique=True)
        stock_data_collection.create_index([("created_at", -1)])
        stock_data_collection.create_index([("updated_at", -1)])
        
        logger.info(f" 股票資料集合建立完成")
        
        # 建立分析結果集合和索引
        logger.info(f" 建立分析結果集合...")
        analysis_collection = db.analysis_results
        
        # 建立索引
        analysis_collection.create_index([("symbol", 1), ("analysis_type", 1)])
        analysis_collection.create_index([("created_at", -1)])
        analysis_collection.create_index([("symbol", 1), ("created_at", -1)])
        
        logger.info(f" 分析結果集合建立完成")
        
        # 建立使用者會話集合和索引
        logger.info(f" 建立使用者會話集合...")
        sessions_collection = db.user_sessions
        
        # 建立索引
        sessions_collection.create_index([("session_id", 1)], unique=True)
        sessions_collection.create_index([("created_at", -1)])
        sessions_collection.create_index([("last_activity", -1)])
        
        logger.info(f" 使用者會話集合建立完成")
        
        # 建立配置集合
        logger.info(f" 建立配置集合...")
        config_collection = db.configurations
        
        # 建立索引
        config_collection.create_index([("config_type", 1), ("config_name", 1)], unique=True)
        config_collection.create_index([("updated_at", -1)])
        
        logger.info(f" 配置集合建立完成")
        
        # 插入初始配置資料
        logger.info(f" 插入初始配置資料...")
        initial_configs = [
            {
                "config_type": "cache",
                "config_name": "ttl_settings",
                "config_value": {
                    "us_stock_data": 7200,
                    "us_news": 21600,
                    "us_fundamentals": 86400
                },
                "description": "快取TTL配置",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "config_type": "llm",
                "config_name": "default_models",
                "config_value": {
                    "default_provider": "openai",
                    "models": {
                        "openai": "gpt-4o-mini",
                        "anthropic": "claude-sonnet-4"
                    }
                },
                "description": "預設LLM模型配置",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        for config in initial_configs:
            config_collection.replace_one(
                {"config_type": config["config_type"], "config_name": config["config_name"]},
                config,
                upsert=True
            )
        
        logger.info(f" 初始配置資料插入完成")
        
        # 顯示資料庫統計
        logger.info(f"\n 資料庫統計:")
        logger.info(f"  - 股票資料: {stock_data_collection.count_documents({})} 條記錄")
        logger.info(f"  - 分析結果: {analysis_collection.count_documents({})} 條記錄")
        logger.info(f"  - 使用者會話: {sessions_collection.count_documents({})} 條記錄")
        logger.info(f"  - 配置項: {config_collection.count_documents({})} 條記錄")
        
        return True
        
    except Exception as e:
        logger.error(f" MongoDB初始化失敗: {e}")
        return False


def init_redis():
    """初始化Redis快取"""
    logger.info(f"\n 初始化Redis快取...")
    
    try:
        from tradingagents.config.database_manager import get_database_manager

        db_manager = get_database_manager()

        if not db_manager.is_redis_available():
            logger.error(f" Redis未連接，請先啟動Redis服務")
            return False
        
        redis_client = db_manager.get_redis_client()
        
        # 清理現有快取（可選）
        logger.info(f" 清理現有快取...")
        redis_client.flushdb()
        
        # 設定初始快取配置
        logger.info(f" 設定快取配置...")
        cache_config = {
            "version": "1.0",
            "initialized_at": datetime.utcnow().isoformat(),
            "ttl_settings": {
                "us_stock_data": 7200,
                "us_news": 21600,
                "us_fundamentals": 86400
            }
        }
        
        db_manager.cache_set("system:cache_config", cache_config, ttl=86400*30)  # 30天
        
        # 設定快取統計初始值
        logger.info(f" 初始化快取統計...")
        stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "last_reset": datetime.utcnow().isoformat()
        }
        
        db_manager.cache_set("system:cache_stats", stats, ttl=86400*7)  # 7天
        
        # 測試快取功能
        logger.info(f" 測試快取功能...")
        test_key = "test:init"
        test_value = {"message": "Redis初始化成功", "timestamp": datetime.utcnow().isoformat()}
        
        if db_manager.cache_set(test_key, test_value, ttl=60):
            retrieved_value = db_manager.cache_get(test_key)
            if retrieved_value and retrieved_value["message"] == test_value["message"]:
                logger.info(f" 快取讀寫測試通過")
                db_manager.cache_delete(test_key)  # 清理測試資料
            else:
                logger.error(f" 快取讀取測試失敗")
                return False
        else:
            logger.error(f" 快取寫入測試失敗")
            return False
        
        # 顯示Redis統計
        info = redis_client.info()
        logger.info(f"\n Redis統計:")
        logger.info(f"  - 已用記憶體: {info.get('used_memory_human', 'N/A')}")
        logger.info(f"  - 連接客戶端: {info.get('connected_clients', 0)}")
        logger.info(f"  - 總命令數: {info.get('total_commands_processed', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f" Redis初始化失敗: {e}")
        return False


def test_database_connection():
    """測試資料庫連接"""
    logger.info(f"\n 測試資料庫連接...")
    
    try:
        from tradingagents.config.database_manager import get_database_manager

        
        db_manager = get_database_manager()
        
        # 測試MongoDB連接
        mongodb_ok = False
        if db_manager.mongodb_client:
            try:
                db_manager.mongodb_client.admin.command('ping')
                logger.info(f" MongoDB連接正常")
                mongodb_ok = True
            except Exception as e:
                logger.error(f" MongoDB連接失敗: {e}")
        else:
            logger.error(f" MongoDB未連接")
        
        # 測試Redis連接
        redis_ok = False
        if db_manager.redis_client:
            try:
                db_manager.redis_client.ping()
                logger.info(f" Redis連接正常")
                redis_ok = True
            except Exception as e:
                logger.error(f" Redis連接失敗: {e}")
        else:
            logger.error(f" Redis未連接")
        
        return mongodb_ok and redis_ok
        
    except Exception as e:
        logger.error(f" 資料庫連接測試失敗: {e}")
        return False


def main():
    """主函式"""
    logger.info(f" TradingAgents 資料庫初始化")
    logger.info(f"=")
    
    # 測試連接
    if not test_database_connection():
        logger.error(f"\n 資料庫連接失敗，請檢查:")
        logger.info(f"1. Docker服務是否啟動: docker ps")
        logger.info(f"2. 執行啟動指令碼: scripts/start_docker_services.bat")
        logger.info(f"3. 檢查環境變數配置: .env 檔案")
        return False
    
    # 初始化MongoDB
    mongodb_success = init_mongodb()
    
    # 初始化Redis
    redis_success = init_redis()
    
    # 輸出結果
    logger.info(f"\n")
    logger.info(f" 初始化結果:")
    logger.error(f"  MongoDB: {' 成功' if mongodb_success else ' 失敗'}")
    logger.error(f"  Redis: {' 成功' if redis_success else ' 失敗'}")
    
    if mongodb_success and redis_success:
        logger.info(f"\n 資料庫初始化完成！")
        logger.info(f"\n 下一步:")
        logger.info(f"1. 啟動Web應用: python start_web.py")
        logger.info(f"2. 存取快取管理: http://localhost:8501 -> 快取管理")
        logger.info(f"3. 存取Redis管理介面: http://localhost:8081")
        return True
    else:
        logger.error(f"\n 部分初始化失敗，請檢查錯誤訊息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
