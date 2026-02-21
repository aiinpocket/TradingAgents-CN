#!/usr/bin/env python3
"""
系統狀態檢查腳本
檢查數據庫配置和緩存系統狀態
"""

import sys
import os
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_system_status():
    """檢查系統狀態"""
    logger.debug(f"🔍 TradingAgents 系統狀態檢查")
    logger.info(f"=")
    
    # 檢查環境配置文件
    logger.info(f"\n📁 檢查環境配置...")
    env_file = project_root / ".env"
    env_example_file = project_root / ".env.example"

    if env_file.exists():
        logger.info(f"✅ 環境配置文件存在: {env_file}")

        try:
            import os
            from dotenv import load_dotenv

            # 加載環境變量
            load_dotenv(env_file)

            logger.info(f"📊 數據庫配置狀態:")
            mongodb_enabled = os.getenv('MONGODB_ENABLED', 'false').lower() == 'true'
            redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
            mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
            mongodb_port = os.getenv('MONGODB_PORT', '27017')
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = os.getenv('REDIS_PORT', '6379')

            logger.error(f"  MongoDB啟用: {'✅ 是' if mongodb_enabled else '❌ 否'}")
            logger.info(f"  MongoDB地址: {mongodb_host}:{mongodb_port}")
            logger.error(f"  Redis啟用: {'✅ 是' if redis_enabled else '❌ 否'}")
            logger.info(f"  Redis地址: {redis_host}:{redis_port}")

            logger.info(f"\n📊 API密鑰配置狀態:")
            api_keys = {
                'FINNHUB_API_KEY': 'FinnHub',
                'OPENAI_API_KEY': 'OpenAI',
                'GOOGLE_API_KEY': 'Google AI',
                'ANTHROPIC_API_KEY': 'Anthropic',
                'OPENROUTER_API_KEY': 'OpenRouter'
            }

            for key, name in api_keys.items():
                value = os.getenv(key, '')
                if value and value != f'your_{key.lower()}_here':
                    logger.info(f"  {name}: ✅ 已配置")
                else:
                    logger.error(f"  {name}: ❌ 未配置")

        except ImportError:
            logger.warning(f"⚠️ python-dotenv未安裝，無法解析.env文件")
        except Exception as e:
            logger.error(f"❌ 環境配置解析失敗: {e}")
    else:
        logger.error(f"❌ 環境配置文件不存在: {env_file}")
        if env_example_file.exists():
            logger.info(f"💡 請複制 {env_example_file} 為 {env_file} 並配置API密鑰")
    
    # 檢查數據庫管理器
    logger.info(f"\n🔧 檢查數據庫管理器...")
    try:
        from tradingagents.config.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        status = db_manager.get_status_report()
        
        logger.info(f"📊 數據庫狀態:")
        logger.error(f"  數據庫可用: {'✅ 是' if status['database_available'] else '❌ 否'}")
        logger.error(f"  MongoDB: {'✅ 可用' if status['mongodb']['available'] else '❌ 不可用'}")
        logger.error(f"  Redis: {'✅ 可用' if status['redis']['available'] else '❌ 不可用'}")
        logger.info(f"  緩存後端: {status['cache_backend']}")
        logger.error(f"  降級支持: {'✅ 啟用' if status['fallback_enabled'] else '❌ 禁用'}")
        
    except Exception as e:
        logger.error(f"❌ 數據庫管理器檢查失敗: {e}")
        import traceback
        traceback.print_exc()
    
    # 檢查緩存系統
    logger.info(f"\n💾 檢查緩存系統...")
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        backend_info = cache.get_cache_backend_info()
        
        logger.info(f"📊 緩存系統狀態:")
        logger.info(f"  緩存系統: {backend_info['system']}")
        logger.info(f"  主要後端: {backend_info['primary_backend']}")
        logger.error(f"  降級支持: {'✅ 啟用' if backend_info['fallback_enabled'] else '❌ 禁用'}")
        logger.info(f"  性能模式: {cache.get_performance_mode()}")
        
        # 獲取詳細統計
        stats = cache.get_cache_stats()
        if 'adaptive_cache' in stats:
            adaptive_stats = stats['adaptive_cache']
            logger.info(f"  文件緩存數量: {adaptive_stats.get('file_cache_count', 0)}")
            if 'redis_keys' in adaptive_stats:
                logger.info(f"  Redis鍵數量: {adaptive_stats['redis_keys']}")
            if 'mongodb_cache_count' in adaptive_stats:
                logger.info(f"  MongoDB緩存數量: {adaptive_stats['mongodb_cache_count']}")
        
    except Exception as e:
        logger.error(f"❌ 緩存系統檢查失敗: {e}")
        import traceback
        traceback.print_exc()
    
    # 測試緩存功能
    logger.info(f"\n🧪 測試緩存功能...")
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        from datetime import datetime
        
        cache = get_cache()
        
        # 測試數據保存
        test_data = f"測試數據 - {datetime.now()}"
        cache_key = cache.save_stock_data(
            symbol="TEST",
            data=test_data,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="system_test"
        )
        logger.info(f"✅ 數據保存成功: {cache_key}")
        
        # 測試數據加載
        loaded_data = cache.load_stock_data(cache_key)
        if loaded_data == test_data:
            logger.info(f"✅ 數據加載成功，內容匹配")
        else:
            logger.error(f"❌ 數據加載失敗或內容不匹配")
        
        # 測試數據查找
        found_key = cache.find_cached_stock_data(
            symbol="TEST",
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="system_test"
        )
        
        if found_key:
            logger.info(f"✅ 緩存查找成功: {found_key}")
        else:
            logger.error(f"❌ 緩存查找失敗")
        
    except Exception as e:
        logger.error(f"❌ 緩存功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
    
    # 性能測試
    logger.info(f"\n⚡ 簡單性能測試...")
    try:
        import time
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        
        # 保存性能測試
        start_time = time.time()
        cache_key = cache.save_stock_data(
            symbol="PERF",
            data="性能測試數據",
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_source="perf_test"
        )
        save_time = time.time() - start_time
        
        # 加載性能測試
        start_time = time.time()
        data = cache.load_stock_data(cache_key)
        load_time = time.time() - start_time
        
        logger.info(f"📊 性能測試結果:")
        logger.info(f"  保存時間: {save_time:.4f}秒")
        logger.info(f"  加載時間: {load_time:.4f}秒")
        
        if load_time < 0.1:
            logger.info(f"✅ 緩存性能良好 (<0.1秒)")
        else:
            logger.warning(f"⚠️ 緩存性能需要優化")
        
        # 計算性能改進
        api_simulation_time = 2.0  # 假設API調用需要2秒
        if load_time < api_simulation_time:
            improvement = ((api_simulation_time - load_time) / api_simulation_time) * 100
            logger.info(f"🚀 相比API調用性能提升: {improvement:.1f}%")
        
    except Exception as e:
        logger.error(f"❌ 性能測試失敗: {e}")
    
    # 系統建議
    logger.info(f"\n💡 系統建議:")
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        
        if cache.is_database_available():
            logger.info(f"✅ 數據庫可用，系統運行在最佳性能模式")
        else:
            logger.info(f"ℹ️ 數據庫不可用，系統使用文件緩存模式")
            logger.info(f"💡 提升性能建議:")
            logger.info(f"  1. 配置環境變量啟用數據庫:")
            logger.info(f"     MONGODB_ENABLED=true")
            logger.info(f"     REDIS_ENABLED=true")
            logger.info(f"  2. 啟動數據庫服務:")
            logger.info(f"     docker-compose up -d  # 推薦方式")
            logger.info(f"     或手動啟動:")
            logger.info(f"     - MongoDB: docker run -d -p 27017:27017 mongo:4.4")
            logger.info(f"     - Redis: docker run -d -p 6379:6379 redis:alpine")
        
        performance_mode = cache.get_performance_mode()
        logger.info(f"🎯 當前性能模式: {performance_mode}")
        
    except Exception as e:
        logger.warning(f"⚠️ 無法生成系統建議: {e}")
    
    logger.info(f"\n")
    logger.info(f"🎉 系統狀態檢查完成!")

def main():
    """主函數"""
    try:
        check_system_status()
        return True
    except Exception as e:
        logger.error(f"❌ 系統檢查失敗: {e}")
        import traceback

        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
