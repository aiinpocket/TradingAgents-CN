#!/usr/bin/env python3
"""
Docker環境快速配置腳本
幫助用戶快速配置Docker部署環境
"""

import os
import shutil
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def setup_docker_env():
    """配置Docker環境"""
    project_root = Path(__file__).parent.parent
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    
    logger.info(f"🐳 TradingAgents-CN Docker環境配置向導")
    logger.info(f"=")
    
    # 檢查.env文件
    if env_file.exists():
        logger.info(f"📁 發現現有的.env文件")
        choice = input("是否要備份現有配置並重新配置？(y/N): ").lower()
        if choice == 'y':
            backup_file = project_root / f".env.backup.{int(time.time())}"
            shutil.copy(env_file, backup_file)
            logger.info(f"✅ 已備份到: {backup_file}")
        else:
            logger.error(f"❌ 取消配置")
            return False
    
    # 複制模板文件
    if not env_example.exists():
        logger.error(f"❌ 找不到.env.example文件")
        return False
    
    shutil.copy(env_example, env_file)
    logger.info(f"✅ 已複制配置模板")
    
    # 讀取配置文件
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Docker環境配置
    docker_configs = {
        'MONGODB_ENABLED': 'true',
        'REDIS_ENABLED': 'true',
        'MONGODB_HOST': 'mongodb',
        'REDIS_HOST': 'redis',
        'MONGODB_PORT': '27017',
        'REDIS_PORT': '6379'
    }
    
    logger.info(f"\n🔧 配置Docker環境變量...")
    for key, value in docker_configs.items():
        # 替換配置值
        import re
        pattern = f'^{key}=.*$'
        replacement = f'{key}={value}'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 寫回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"✅ Docker環境配置完成")
    
    # API密鑰配置提醒
    logger.info(f"\n🔑 API密鑰配置")
    logger.info(f"Please configure the following API keys in .env (at least one LLM key):")
    logger.info(f"- OPENAI_API_KEY or GOOGLE_API_KEY (LLM provider)")
    logger.info(f"- FINNHUB_API_KEY (financial data)")
    
    # 顯示下一步操作
    logger.info(f"\n🚀 下一步操作：")
    logger.info(f"1. 編輯.env文件，填入您的API密鑰")
    logger.info(f"2. 運行: docker-compose up -d")
    logger.info(f"3. 訪問: http://localhost:8501")
    
    return True

def check_docker():
    """檢查Docker環境"""
    logger.debug(f"🔍 檢查Docker環境...")
    
    # 檢查Docker
    if shutil.which('docker') is None:
        logger.error(f"❌ 未找到Docker，請先安裝Docker Desktop")
        return False
    
    # 檢查docker-compose
    if shutil.which('docker-compose') is None:
        logger.error(f"❌ 未找到docker-compose，請確保Docker Desktop已正確安裝")
        return False
    
    # 檢查Docker是否運行
    try:
        import subprocess
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.error(f"❌ Docker未運行，請啟動Docker Desktop")
            return False
    except Exception as e:
        logger.error(f"❌ Docker檢查失敗: {e}")
        return False
    
    logger.info(f"✅ Docker環境檢查通過")
    return True

def main():
    """主函數"""
    import time

    
    if not check_docker():
        logger.info(f"\n💡 請先安裝並啟動Docker Desktop:")
        logger.info(f"- Windows/macOS: https://www.docker.com/products/docker-desktop")
        logger.info(f"- Linux: https://docs.docker.com/engine/install/")
        return
    
    if setup_docker_env():
        logger.info(f"\n🎉 Docker環境配置完成！")
        logger.info(f"\n📚 更多信息請參考:")
        logger.info(f"- Docker部署指南: docs/DOCKER_GUIDE.md")
        logger.info(f"- 項目文件: README.md")
    else:
        logger.error(f"\n❌ 配置失敗")

if __name__ == "__main__":
    main()
