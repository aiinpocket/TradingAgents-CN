#!/usr/bin/env python3
"""
修複Docker環境下的日誌文件生成問題
"""

import os
import shutil
from pathlib import Path

def fix_docker_logging_config():
    """修複Docker日誌配置"""
    print("🔧 修複Docker環境日誌配置...")
    
    # 1. 修改 logging_docker.toml
    docker_config_file = Path("config/logging_docker.toml")
    if docker_config_file.exists():
        print(f"📝 修改 {docker_config_file}")
        
        # 讀取現有配置
        with open(docker_config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改配置：啟用文件日誌
        new_content = content.replace(
            '[logging.handlers.file]\nenabled = false',
            '[logging.handlers.file]\nenabled = true\nlevel = "DEBUG"\nmax_size = "100MB"\nbackup_count = 5\ndirectory = "/app/logs"'
        )
        
        new_content = new_content.replace(
            'disable_file_logging = true',
            'disable_file_logging = false'
        )
        
        new_content = new_content.replace(
            'stdout_only = true',
            'stdout_only = false'
        )
        
        # 寫回文件
        with open(docker_config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Docker日誌配置已修複")
    else:
        print("⚠️ Docker日誌配置文件不存在，創建新的...")
        create_docker_logging_config()

def create_docker_logging_config():
    """創建新的Docker日誌配置"""
    docker_config_content = '''# Docker環境專用日誌配置 - 修複版
# 同時支持控制台輸出和文件日誌

[logging]
level = "INFO"

[logging.format]
console = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
file = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
structured = "json"

[logging.handlers]

# 控制台輸出
[logging.handlers.console]
enabled = true
colored = false
level = "INFO"

# 文件輸出 - 啟用！
[logging.handlers.file]
enabled = true
level = "DEBUG"
max_size = "100MB"
backup_count = 5
directory = "/app/logs"

# 結構化日誌
[logging.handlers.structured]
enabled = true
level = "INFO"
directory = "/app/logs"

[logging.loggers]
[logging.loggers.tradingagents]
level = "INFO"

[logging.loggers.web]
level = "INFO"

[logging.loggers.streamlit]
level = "WARNING"

[logging.loggers.urllib3]
level = "WARNING"

[logging.loggers.requests]
level = "WARNING"

# Docker配置 - 修複版
[logging.docker]
enabled = true
stdout_only = false  # 不只輸出到stdout
disable_file_logging = false  # 不禁用文件日誌

[logging.performance]
enabled = true
log_slow_operations = true
slow_threshold_seconds = 10.0

[logging.security]
enabled = true
log_api_calls = true
log_token_usage = true
mask_sensitive_data = true

[logging.business]
enabled = true
log_analysis_events = true
log_user_actions = true
log_export_events = true
'''
    
    # 確保config目錄存在
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # 寫入配置文件
    docker_config_file = config_dir / "logging_docker.toml"
    with open(docker_config_file, 'w', encoding='utf-8') as f:
        f.write(docker_config_content)
    
    print(f"✅ 創建新的Docker日誌配置: {docker_config_file}")

def update_docker_compose():
    """更新docker-compose.yml環境變量"""
    print("\n🐳 檢查docker-compose.yml配置...")
    
    compose_file = Path("docker-compose.yml")
    if not compose_file.exists():
        print("❌ docker-compose.yml文件不存在")
        return
    
    with open(compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否已有正確的環境變量
    required_vars = [
        'TRADINGAGENTS_LOG_DIR: "/app/logs"',
        'TRADINGAGENTS_LOG_FILE: "/app/logs/tradingagents.log"'
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ 缺少環境變量: {missing_vars}")
        print("💡 請確保docker-compose.yml包含以下環境變量:")
        for var in required_vars:
            print(f"   {var}")
    else:
        print("✅ docker-compose.yml環境變量配置正確")

def create_test_script():
    """創建測試腳本"""
    print("\n📝 創建日誌測試腳本...")
    
    test_script_content = '''#!/usr/bin/env python3
"""
測試Docker環境下的日誌功能
"""

import os
import sys
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_logging():
    """測試日誌功能"""
    print("🧪 測試Docker環境日誌功能")
    print("=" * 50)
    
    try:
        # 設置Docker環境變量
        os.environ['DOCKER_CONTAINER'] = 'true'
        os.environ['TRADINGAGENTS_LOG_DIR'] = '/app/logs'
        
        # 導入日誌模塊
        from tradingagents.utils.logging_init import init_logging, get_logger
        
        # 初始化日誌
        print("📋 初始化日誌系統...")
        init_logging()
        
        # 獲取日誌器
        logger = get_logger('test')
        
        # 測試各種級別的日誌
        print("📝 寫入測試日誌...")
        logger.debug("🔍 這是DEBUG級別日誌")
        logger.info("ℹ️ 這是INFO級別日誌")
        logger.warning("⚠️ 這是WARNING級別日誌")
        logger.error("❌ 這是ERROR級別日誌")
        
        # 檢查日誌文件
        log_dir = Path("/app/logs")
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log*"))
            print(f"📄 找到日誌文件: {len(log_files)} 個")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"   📄 {log_file.name}: {size} 字節")
        else:
            print("❌ 日誌目錄不存在")
        
        print("✅ 日誌測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 日誌測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_logging()
    sys.exit(0 if success else 1)
'''
    
    test_file = Path("test_docker_logging.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script_content)
    
    print(f"✅ 創建測試腳本: {test_file}")

def main():
    """主函數"""
    print("🚀 TradingAgents Docker日誌修複工具")
    print("=" * 60)
    
    # 1. 修複Docker日誌配置
    fix_docker_logging_config()
    
    # 2. 檢查docker-compose配置
    update_docker_compose()
    
    # 3. 創建測試腳本
    create_test_script()
    
    print("\n" + "=" * 60)
    print("🎉 Docker日誌修複完成！")
    print("\n💡 接下來的步骤:")
    print("1. 重新構建Docker鏡像: docker-compose build")
    print("2. 重啟容器: docker-compose down && docker-compose up -d")
    print("3. 測試日誌: docker exec TradingAgents-web python test_docker_logging.py")
    print("4. 檢查日誌文件: ls -la logs/")
    print("5. 實時查看: tail -f logs/tradingagents.log")
    
    print("\n🔧 如果仍然没有日誌文件，請檢查:")
    print("- 容器是否正常啟動: docker-compose ps")
    print("- 應用是否正常運行: docker-compose logs web")
    print("- 日誌目錄權限: ls -la logs/")

if __name__ == "__main__":
    main()
