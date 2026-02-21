#!/usr/bin/env python3
"""
數據庫環境設置腳本
自動安裝和配置MongoDB + Redis
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def run_command(command, description=""):
    """運行命令並處理錯誤"""
    logger.info(f"🔄 {description}")
    logger.info(f"   執行: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        logger.info(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} 失敗")
        logger.error(f"   錯誤: {e.stderr}")
        return False

def install_python_packages():
    """安裝Python依賴包"""
    logger.info(f"\n📦 安裝Python數據庫依賴包...")
    
    packages = [
        "pymongo>=4.6.0",
        "redis>=5.0.0", 
        "hiredis>=2.2.0"
    ]
    
    for package in packages:
        success = run_command(
            f"pip install {package}",
            f"安裝 {package}"
        )
        if not success:
            logger.error(f"⚠️ {package} 安裝失敗，請手動安裝")

def setup_mongodb_windows():
    """Windows環境MongoDB設置"""
    logger.info(f"\n🍃 Windows MongoDB 設置指南:")
    print("""
    請按以下步驟手動安裝MongoDB:
    
    1. 下載MongoDB Community Server:
       https://www.mongodb.com/try/download/community
    
    2. 安裝MongoDB:
       - 選擇 "Complete" 安裝
       - 勾選 "Install MongoDB as a Service"
       - 勾選 "Install MongoDB Compass" (可選的圖形界面)
    
    3. 啟動MongoDB服務:
       - 打開服務管理器 (services.msc)
       - 找到 "MongoDB" 服務並啟動
       
    4. 驗證安裝:
       - 打開命令行，運行: mongosh
       - 如果連接成功，說明安裝正確
    
    默認連接地址: mongodb://localhost:27017
    """)

def setup_redis_windows():
    """Windows環境Redis設置"""
    logger.info(f"\n🔴 Windows Redis 設置指南:")
    print("""
    請按以下步驟手動安裝Redis:
    
    1. 下載Redis for Windows:
       https://github.com/microsoftarchive/redis/releases
       
    2. 解壓到目錄 (如 C:\\Redis)
    
    3. 啟動Redis服務器:
       - 打開命令行，進入Redis目錄
       - 運行: redis-server.exe
       
    4. 測試Redis連接:
       - 新開命令行窗口
       - 運行: redis-cli.exe
       - 輸入: ping
       - 應該返回: PONG
    
    或者使用Docker:
    docker run -d -p 6379:6379 --name redis redis:latest
    
    默認連接地址: redis://localhost:6379
    """)

def setup_mongodb_linux():
    """Linux環境MongoDB設置"""
    logger.info(f"\n🍃 Linux MongoDB 設置...")
    
    # 檢測Linux發行版
    if os.path.exists("/etc/ubuntu-release") or os.path.exists("/etc/debian_version"):
        # Ubuntu/Debian
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y mongodb",
            "sudo systemctl start mongodb",
            "sudo systemctl enable mongodb"
        ]
    elif os.path.exists("/etc/redhat-release") or os.path.exists("/etc/centos-release"):
        # CentOS/RHEL
        commands = [
            "sudo yum install -y mongodb-server",
            "sudo systemctl start mongod",
            "sudo systemctl enable mongod"
        ]
    else:
        logger.warning(f"⚠️ 未識別的Linux發行版，請手動安裝MongoDB")
        return
    
    for cmd in commands:
        run_command(cmd, f"執行: {cmd}")

def setup_redis_linux():
    """Linux環境Redis設置"""
    logger.info(f"\n🔴 Linux Redis 設置...")
    
    # 檢測Linux發行版
    if os.path.exists("/etc/ubuntu-release") or os.path.exists("/etc/debian_version"):
        # Ubuntu/Debian
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y redis-server",
            "sudo systemctl start redis-server",
            "sudo systemctl enable redis-server"
        ]
    elif os.path.exists("/etc/redhat-release") or os.path.exists("/etc/centos-release"):
        # CentOS/RHEL
        commands = [
            "sudo yum install -y redis",
            "sudo systemctl start redis",
            "sudo systemctl enable redis"
        ]
    else:
        logger.warning(f"⚠️ 未識別的Linux發行版，請手動安裝Redis")
        return
    
    for cmd in commands:
        run_command(cmd, f"執行: {cmd}")

def setup_docker_option():
    """Docker方式設置"""
    logger.info(f"\n🐳 Docker 方式設置 (推薦):")
    print("""
    如果您已安裝Docker，可以使用以下命令快速啟動:
    
    # 啟動MongoDB
    docker run -d \\
      --name mongodb \\
      -p 27017:27017 \\
      -v mongodb_data:/data/db \\
      mongo:latest
    
    # 啟動Redis
    docker run -d \\
      --name redis \\
      -p 6379:6379 \\
      -v redis_data:/data \\
      redis:latest
    
    # 查看運行狀態
    docker ps
    
    # 停止服務
    docker stop mongodb redis
    
    # 重新啟動
    docker start mongodb redis
    """)

def create_env_template():
    """創建環境變量模板"""
    logger.info(f"📄 數據庫配置已整合到主要的 .env 文件中")
    logger.info(f"請參考 .env.example 文件進行配置")

def test_connections():
    """測試數據庫連接"""
    logger.debug(f"\n🔍 測試數據庫連接...")
    
    try:
        from tradingagents.config.database_manager import get_database_manager


        db_manager = get_database_manager()
        
        # 測試基本功能
        if db_manager.is_mongodb_available() and db_manager.is_redis_available():
            logger.info(f"🎉 MongoDB + Redis 連接成功！")

            # 獲取統計信息
            stats = db_manager.get_cache_stats()
            logger.info(f"📊 緩存統計: {stats}")

        elif db_manager.is_mongodb_available():
            logger.info(f"✅ MongoDB 連接成功，Redis 未連接")
        elif db_manager.is_redis_available():
            logger.info(f"✅ Redis 連接成功，MongoDB 未連接")
        else:
            logger.error(f"❌ 數據庫連接失敗")
            
        db_manager.close()
        
    except ImportError as e:
        logger.error(f"❌ 導入失敗: {e}")
        logger.info(f"請先安裝依賴包: pip install -r requirements_db.txt")
    except Exception as e:
        logger.error(f"❌ 連接測試失敗: {e}")

def main():
    """主函數"""
    logger.info(f"🚀 TradingAgents 數據庫環境設置")
    logger.info(f"=")
    
    # 檢測操作系統
    system = platform.system().lower()
    logger.info(f"🖥️ 檢測到操作系統: {system}")
    
    # 安裝Python依賴
    install_python_packages()
    
    # 根據操作系統提供設置指南
    if system == "windows":
        setup_mongodb_windows()
        setup_redis_windows()
    elif system == "linux":
        setup_mongodb_linux()
        setup_redis_linux()
    else:
        logger.warning(f"⚠️ 不支持的操作系統: {system}")
    
    # Docker選項
    setup_docker_option()
    
    # 創建配置文件
    create_env_template()
    
    logger.info(f"\n")
    logger.info(f"📋 設置完成後，請運行以下命令測試連接:")
    logger.info(f"python scripts/setup_databases.py --test")
    
    # 如果指定了測試參數
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_connections()

if __name__ == "__main__":
    main()
