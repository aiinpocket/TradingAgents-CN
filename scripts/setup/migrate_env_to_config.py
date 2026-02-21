#!/usr/bin/env python3
"""
將 .env 檔案中的配置遷移到新的JSON配置系統
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.config.config_manager import config_manager, ModelConfig

def load_env_config():
    """載入 .env 檔案配置"""
    env_file = project_root / ".env"
    if not env_file.exists():
        logger.error(f" .env 檔案不存在")
        return None
    
    load_dotenv(env_file)
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', ''),
        'finnhub_api_key': os.getenv('FINNHUB_API_KEY', ''),
        'results_dir': os.getenv('TRADINGAGENTS_RESULTS_DIR', './results'),
        'log_level': os.getenv('TRADINGAGENTS_LOG_LEVEL', 'INFO'),
    }

def migrate_model_configs(env_config):
    """遷移模型配置"""
    logger.info(f" 遷移模型配置...")
    
    # 載入現有配置
    models = config_manager.load_models()
    
    # 更新API密鑰
    updated = False
    for model in models:
        if model.provider == "openai" and env_config['openai_api_key']:
            if model.api_key != env_config['openai_api_key']:
                model.api_key = env_config['openai_api_key']
                model.enabled = True
                updated = True
                logger.info(f" 更新 {model.provider} - {model.model_name} API密鑰")
        
        elif model.provider == "anthropic" and env_config['anthropic_api_key']:
            if model.api_key != env_config['anthropic_api_key']:
                model.api_key = env_config['anthropic_api_key']
                model.enabled = True
                updated = True
                logger.info(f" 更新 {model.provider} - {model.model_name} API密鑰")
    
    if updated:
        config_manager.save_models(models)
        logger.info(f" 模型配置已保存")
    else:
        logger.info(f"[INFO]模型配置無需更新")

def migrate_system_settings(env_config):
    """遷移系統設定"""
    logger.info(f"\n 遷移系統設定...")
    
    settings = config_manager.load_settings()
    
    # 更新設定
    updated = False
    if env_config['results_dir'] and settings.get('results_dir') != env_config['results_dir']:
        settings['results_dir'] = env_config['results_dir']
        updated = True
        logger.info(f" 更新結果目錄: {env_config['results_dir']}")
    
    if env_config['log_level'] and settings.get('log_level') != env_config['log_level']:
        settings['log_level'] = env_config['log_level']
        updated = True
        logger.info(f" 更新日誌級別: {env_config['log_level']}")
    
    # 添加其他配置
    if env_config['finnhub_api_key']:
        settings['finnhub_api_key'] = env_config['finnhub_api_key']
        updated = True
        logger.info(f" 添加 FinnHub API密鑰")
    
    if updated:
        config_manager.save_settings(settings)
        logger.info(f" 系統設定已保存")
    else:
        logger.info(f"[INFO]系統設定無需更新")

def main():
    """主函式"""
    logger.info(f" .env 配置遷移工具")
    logger.info(f"=")
    
    # 載入 .env 配置
    env_config = load_env_config()
    if not env_config:
        return False
    
    logger.info(f" 檢測到的 .env 配置:")
    for key, value in env_config.items():
        if 'api_key' in key or 'secret' in key:
            # 隱藏敏感資訊
            display_value = f"***{value[-4:]}" if value else "未設定"
        else:
            display_value = value if value else "未設定"
        logger.info(f"  {key}: {display_value}")
    
    logger.info(f"\n 開始遷移配置...")
    
    try:
        # 遷移模型配置
        migrate_model_configs(env_config)
        
        # 遷移系統設定
        migrate_system_settings(env_config)
        
        logger.info(f"\n 配置遷移完成！")
        logger.info(f"\n 下一步:")
        logger.info(f"1. 啟動Web介面: python -m streamlit run web/app.py")
        logger.info(f"2. 訪問 ' 配置管理' 頁面查看遷移結果")
        logger.info(f"3. 根據需要調整模型參數和定價配置")
        logger.info(f"4. 可以繼續使用 .env 檔案，也可以完全使用Web配置")
        
        return True
        
    except Exception as e:
        logger.error(f" 遷移失敗: {e}")
        import traceback

        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
