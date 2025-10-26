#!/usr/bin/env python3
"""
簡單的.env配置測試
"""

import os

def test_env_reading():
    """測試.env文件讀取"""
    print("🔧 測試.env配置讀取")
    print("=" * 30)
    
    # 檢查.env文件
    if os.path.exists('.env'):
        print("✅ .env文件存在")
    else:
        print("❌ .env文件不存在")
        return False
    
    # 讀取環境變量
    print("\n📊 數據庫配置:")
    
    # MongoDB配置
    mongodb_host = os.getenv("MONGODB_HOST", "localhost")
    mongodb_port = os.getenv("MONGODB_PORT", "27017")
    mongodb_username = os.getenv("MONGODB_USERNAME")
    mongodb_password = os.getenv("MONGODB_PASSWORD")
    mongodb_database = os.getenv("MONGODB_DATABASE", "tradingagents")
    
    print(f"MongoDB:")
    print(f"  Host: {mongodb_host}")
    print(f"  Port: {mongodb_port}")
    print(f"  Username: {mongodb_username or '未設置'}")
    print(f"  Password: {'***' if mongodb_password else '未設置'}")
    print(f"  Database: {mongodb_database}")
    
    # Redis配置
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_db = os.getenv("REDIS_DB", "0")
    
    print(f"\nRedis:")
    print(f"  Host: {redis_host}")
    print(f"  Port: {redis_port}")
    print(f"  Password: {'***' if redis_password else '未設置'}")
    print(f"  DB: {redis_db}")
    
    # 測試數據庫連接
    print("\n🧪 測試數據庫連接...")
    
    # 測試MongoDB
    mongodb_available = False
    try:
        import pymongo
        client = pymongo.MongoClient(
            host=mongodb_host,
            port=int(mongodb_port),
            username=mongodb_username,
            password=mongodb_password,
            authSource="admin",
            serverSelectionTimeoutMS=2000
        )
        client.server_info()
        client.close()
        mongodb_available = True
        print("✅ MongoDB 連接成功")
    except ImportError:
        print("❌ pymongo 未安裝")
    except Exception as e:
        print(f"❌ MongoDB 連接失败: {e}")
    
    # 測試Redis
    redis_available = False
    try:
        import redis
        r = redis.Redis(
            host=redis_host,
            port=int(redis_port),
            password=redis_password,
            db=int(redis_db),
            socket_timeout=2
        )
        r.ping()
        redis_available = True
        print("✅ Redis 連接成功")
    except ImportError:
        print("❌ redis 未安裝")
    except Exception as e:
        print(f"❌ Redis 連接失败: {e}")
    
    # 总結
    print(f"\n📊 总結:")
    print(f"MongoDB: {'✅ 可用' if mongodb_available else '❌ 不可用'}")
    print(f"Redis: {'✅ 可用' if redis_available else '❌ 不可用'}")
    
    if mongodb_available or redis_available:
        print("🚀 數據庫可用，系統将使用高性能模式")
    else:
        print("📁 數據庫不可用，系統将使用文件緩存模式")
        print("💡 這是正常的，系統可以正常工作")
    
    return True

if __name__ == "__main__":
    test_env_reading()
