#!/usr/bin/env python3
"""
将 .env 文件中的配置迁移到新的JSON配置系統
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.config.config_manager import config_manager, ModelConfig

def load_env_config():
    """加載 .env 文件配置"""
    env_file = project_root / ".env"
    if not env_file.exists():
        logger.error(f"❌ .env 文件不存在")
        return None
    
    load_dotenv(env_file)
    return {
        'dashscope_api_key': os.getenv('DASHSCOPE_API_KEY', ''),
        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
        'google_api_key': os.getenv('GOOGLE_API_KEY', ''),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', ''),
        'finnhub_api_key': os.getenv('FINNHUB_API_KEY', ''),
        'reddit_client_id': os.getenv('REDDIT_CLIENT_ID', ''),
        'reddit_client_secret': os.getenv('REDDIT_CLIENT_SECRET', ''),
        'reddit_user_agent': os.getenv('REDDIT_USER_AGENT', ''),
        'results_dir': os.getenv('TRADINGAGENTS_RESULTS_DIR', './results'),
        'log_level': os.getenv('TRADINGAGENTS_LOG_LEVEL', 'INFO'),
    }

def migrate_model_configs(env_config):
    """迁移模型配置"""
    logger.info(f"🔄 迁移模型配置...")
    
    # 加載現有配置
    models = config_manager.load_models()
    
    # 更新API密鑰
    updated = False
    for model in models:
        if model.provider == "dashscope" and env_config['dashscope_api_key']:
            if model.api_key != env_config['dashscope_api_key']:
                model.api_key = env_config['dashscope_api_key']
                model.enabled = True  # 有API密鑰的模型自動啟用
                updated = True
                logger.info(f"✅ 更新 {model.provider} - {model.model_name} API密鑰")
        
        elif model.provider == "openai" and env_config['openai_api_key']:
            if model.api_key != env_config['openai_api_key']:
                model.api_key = env_config['openai_api_key']
                model.enabled = True
                updated = True
                logger.info(f"✅ 更新 {model.provider} - {model.model_name} API密鑰")
        
        elif model.provider == "google" and env_config['google_api_key']:
            if model.api_key != env_config['google_api_key']:
                model.api_key = env_config['google_api_key']
                model.enabled = True
                updated = True
                logger.info(f"✅ 更新 {model.provider} - {model.model_name} API密鑰")
        
        elif model.provider == "anthropic" and env_config['anthropic_api_key']:
            if model.api_key != env_config['anthropic_api_key']:
                model.api_key = env_config['anthropic_api_key']
                model.enabled = True
                updated = True
                logger.info(f"✅ 更新 {model.provider} - {model.model_name} API密鑰")
    
    if updated:
        config_manager.save_models(models)
        logger.info(f"💾 模型配置已保存")
    else:
        logger.info(f"ℹ️ 模型配置無需更新")

def migrate_system_settings(env_config):
    """迁移系統設置"""
    logger.info(f"\n🔄 迁移系統設置...")
    
    settings = config_manager.load_settings()
    
    # 更新設置
    updated = False
    if env_config['results_dir'] and settings.get('results_dir') != env_config['results_dir']:
        settings['results_dir'] = env_config['results_dir']
        updated = True
        logger.info(f"✅ 更新結果目錄: {env_config['results_dir']}")
    
    if env_config['log_level'] and settings.get('log_level') != env_config['log_level']:
        settings['log_level'] = env_config['log_level']
        updated = True
        logger.info(f"✅ 更新日誌級別: {env_config['log_level']}")
    
    # 添加其他配置
    if env_config['finnhub_api_key']:
        settings['finnhub_api_key'] = env_config['finnhub_api_key']
        updated = True
        logger.info(f"✅ 添加 FinnHub API密鑰")
    
    if env_config['reddit_client_id']:
        settings['reddit_client_id'] = env_config['reddit_client_id']
        updated = True
        logger.info(f"✅ 添加 Reddit 客戶端ID")
    
    if env_config['reddit_client_secret']:
        settings['reddit_client_secret'] = env_config['reddit_client_secret']
        updated = True
        logger.info(f"✅ 添加 Reddit 客戶端密鑰")
    
    if env_config['reddit_user_agent']:
        settings['reddit_user_agent'] = env_config['reddit_user_agent']
        updated = True
        logger.info(f"✅ 添加 Reddit 用戶代理")
    
    if updated:
        config_manager.save_settings(settings)
        logger.info(f"💾 系統設置已保存")
    else:
        logger.info(f"ℹ️ 系統設置無需更新")

def main():
    """主函數"""
    logger.info(f"🔄 .env 配置迁移工具")
    logger.info(f"=")
    
    # 加載 .env 配置
    env_config = load_env_config()
    if not env_config:
        return False
    
    logger.info(f"📋 檢測到的 .env 配置:")
    for key, value in env_config.items():
        if 'api_key' in key or 'secret' in key:
            # 隐藏敏感信息
            display_value = f"***{value[-4:]}" if value else "未設置"
        else:
            display_value = value if value else "未設置"
        logger.info(f"  {key}: {display_value}")
    
    logger.info(f"\n🎯 開始迁移配置...")
    
    try:
        # 迁移模型配置
        migrate_model_configs(env_config)
        
        # 迁移系統設置
        migrate_system_settings(env_config)
        
        logger.info(f"\n🎉 配置迁移完成！")
        logger.info(f"\n💡 下一步:")
        logger.info(f"1. 啟動Web界面: python -m streamlit run web/app.py")
        logger.info(f"2. 訪問 '⚙️ 配置管理' 页面查看迁移結果")
        logger.info(f"3. 根據需要調整模型參數和定價配置")
        logger.info(f"4. 可以繼续使用 .env 文件，也可以完全使用Web配置")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        import traceback

        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
