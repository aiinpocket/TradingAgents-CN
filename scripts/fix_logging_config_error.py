#!/usr/bin/env python3
"""
修複日誌配置KeyError錯誤
"""

import os
from pathlib import Path

def fix_logging_docker_config():
    """修複Docker日誌配置文件"""
    print("🔧 修複Docker日誌配置文件...")
    
    docker_config_content = '''# Docker環境專用日誌配置 - 完整修複版
# 解決KeyError: 'file'錯誤

[logging]
level = "INFO"

[logging.format]
# 必须包含所有格式配置
console = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
file = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
structured = "json"

[logging.handlers]

# 控制台輸出
[logging.handlers.console]
enabled = true
colored = false
level = "INFO"

# 文件輸出 - 完整配置
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

[logging.loggers.dataflows]
level = "INFO"

[logging.loggers.llm_adapters]
level = "INFO"

[logging.loggers.streamlit]
level = "WARNING"

[logging.loggers.urllib3]
level = "WARNING"

[logging.loggers.requests]
level = "WARNING"

[logging.loggers.matplotlib]
level = "WARNING"

[logging.loggers.pandas]
level = "WARNING"

# Docker配置 - 修複版
[logging.docker]
enabled = true
stdout_only = false  # 同時輸出到文件和stdout
disable_file_logging = false  # 啟用文件日誌

[logging.development]
enabled = false
debug_modules = ["tradingagents.graph", "tradingagents.llm_adapters"]
save_debug_files = true

[logging.production]
enabled = false
structured_only = false
error_notification = true
max_log_size = "100MB"

[logging.performance]
enabled = true
log_slow_operations = true
slow_threshold_seconds = 10.0
log_memory_usage = false

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
    
    # 寫入修複後的配置文件
    docker_config_file = config_dir / "logging_docker.toml"
    with open(docker_config_file, 'w', encoding='utf-8') as f:
        f.write(docker_config_content)
    
    print(f"✅ 修複Docker日誌配置: {docker_config_file}")

def fix_main_logging_config():
    """修複主日誌配置文件"""
    print("🔧 檢查主日誌配置文件...")
    
    main_config_file = Path("config/logging.toml")
    if main_config_file.exists():
        with open(main_config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否包含file格式配置
        if 'file = "' not in content:
            print("⚠️ 主配置文件缺少file格式配置，正在修複...")
            
            # 在format部分添加file配置
            if '[logging.format]' in content:
                content = content.replace(
                    'console = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"',
                    'console = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"\nfile = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"'
                )
                
                with open(main_config_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ 主配置文件已修複")
            else:
                print("❌ 主配置文件格式異常")
        else:
            print("✅ 主配置文件正常")
    else:
        print("⚠️ 主配置文件不存在")

def create_simple_test():
    """創建簡單的日誌測試"""
    print("📝 創建簡單日誌測試...")
    
    test_content = '''#!/usr/bin/env python3
"""
簡單的日誌測試 - 避免複雜導入
"""

import os
import logging
import logging.handlers
from pathlib import Path

def simple_log_test():
    """簡單的日誌測試"""
    print("🧪 簡單日誌測試")
    
    # 創建日誌目錄
    log_dir = Path("/app/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 創建簡單的日誌配置
    logger = logging.getLogger("simple_test")
    logger.setLevel(logging.DEBUG)
    
    # 清除現有處理器
    logger.handlers.clear()
    
    # 添加控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 添加文件處理器
    try:
        log_file = log_dir / "simple_test.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s | %(name)-20s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        print(f"✅ 文件處理器創建成功: {log_file}")
    except Exception as e:
        print(f"❌ 文件處理器創建失败: {e}")
        return False
    
    # 測試日誌寫入
    try:
        logger.debug("🔍 DEBUG級別測試日誌")
        logger.info("ℹ️ INFO級別測試日誌")
        logger.warning("⚠️ WARNING級別測試日誌")
        logger.error("❌ ERROR級別測試日誌")
        
        print("✅ 日誌寫入測試完成")
        
        # 檢查文件是否生成
        if log_file.exists():
            size = log_file.stat().st_size
            print(f"📄 日誌文件大小: {size} 字節")
            
            if size > 0:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"📄 日誌文件行數: {len(lines)}")
                    if lines:
                        print("📄 最後一行:")
                        print(f"   {lines[-1].strip()}")
                return True
            else:
                print("⚠️ 日誌文件為空")
                return False
        else:
            print("❌ 日誌文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 日誌寫入失败: {e}")
        return False

if __name__ == "__main__":
    success = simple_log_test()
    exit(0 if success else 1)
'''
    
    test_file = Path("simple_log_test.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ 創建簡單測試: {test_file}")

def main():
    """主函數"""
    print("🚀 修複日誌配置KeyError錯誤")
    print("=" * 60)
    
    # 1. 修複Docker配置
    fix_logging_docker_config()
    
    # 2. 修複主配置
    fix_main_logging_config()
    
    # 3. 創建簡單測試
    create_simple_test()
    
    print("\n" + "=" * 60)
    print("🎉 日誌配置修複完成！")
    print("\n💡 接下來的步骤:")
    print("1. 重新構建Docker鏡像: docker-compose build")
    print("2. 重啟容器: docker-compose down && docker-compose up -d")
    print("3. 簡單測試: docker exec TradingAgents-web python simple_log_test.py")
    print("4. 檢查日誌: ls -la logs/")
    print("5. 查看容器日誌: docker-compose logs web")
    
    print("\n🔧 如果还有問題:")
    print("- 檢查容器啟動日誌: docker-compose logs web")
    print("- 進入容器調試: docker exec -it TradingAgents-web bash")
    print("- 檢查配置文件: docker exec TradingAgents-web cat /app/config/logging_docker.toml")

if __name__ == "__main__":
    main()
