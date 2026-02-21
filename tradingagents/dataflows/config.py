import tradingagents.default_config as default_config
from typing import Dict, Optional
from tradingagents.config.config_manager import config_manager

# Use default config but allow it to be overridden
_config: Optional[Dict] = None
DATA_DIR: Optional[str] = None


def initialize_config():
    """Initialize the configuration with default values."""
    global _config, DATA_DIR
    if _config is None:
        # 優先使用配置管理器的設定
        settings = config_manager.load_settings()
        _config = default_config.DEFAULT_CONFIG.copy()
        
        # 如果配置管理器中有資料目錄設定，使用它
        if settings.get("data_dir"):
            _config["data_dir"] = settings["data_dir"]
        
        DATA_DIR = _config["data_dir"]
        
        # 確保目錄存在
        config_manager.ensure_directories_exist()


def set_config(config: Dict):
    """Update the configuration with custom values."""
    global _config, DATA_DIR
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    
    _config.update(config)
    DATA_DIR = _config["data_dir"]
    
    # 如果設定了資料目錄，同時更新配置管理器
    if "data_dir" in config:
        config_manager.set_data_dir(config["data_dir"])


def get_config() -> Dict:
    """Get the current configuration."""
    if _config is None:
        initialize_config()

    # 動態取得最新的資料目錄配置
    current_data_dir = config_manager.get_data_dir()
    if _config["data_dir"] != current_data_dir:
        _config["data_dir"] = current_data_dir
        global DATA_DIR
        DATA_DIR = current_data_dir

    # 註意：資料庫配置現在由 tradingagents.config.database_manager 管理
    # 這裡不再包含資料庫配置，避免配置衝突
    config_copy = _config.copy()

    return config_copy


def get_data_dir() -> str:
    """取得資料目錄路徑"""
    return config_manager.get_data_dir()


def set_data_dir(data_dir: str):
    """設定資料目錄路徑"""
    config_manager.set_data_dir(data_dir)
    # 更新全局變量
    global _config, DATA_DIR
    if _config is None:
        initialize_config()
    _config["data_dir"] = data_dir
    DATA_DIR = data_dir


# Initialize with default config
initialize_config()
