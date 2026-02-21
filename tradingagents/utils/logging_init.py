#!/usr/bin/env python3
"""
日誌系統初始化模塊
在應用啟動時初始化統一日誌系統
"""

import os
import sys
from pathlib import Path
from typing import Optional

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.logging_manager import setup_logging, get_logger


def init_logging(config_override: Optional[dict] = None) -> None:
    """
    初始化項目日誌系統
    
    Args:
        config_override: 可選的配置覆蓋
    """
    # 設置日誌系統
    logger_manager = setup_logging(config_override)
    
    # 獲取初始化日誌器
    logger = get_logger('tradingagents.init')
    
    # 記錄初始化信息
    logger.info("TradingAgents-CN 日誌系統初始化完成")
    logger.info(f"日誌目錄: {logger_manager.config.get('handlers', {}).get('file', {}).get('directory', 'N/A')}")
    logger.info(f"日誌級別: {logger_manager.config.get('level', 'INFO')}")
    
    # Docker環境特殊處理
    if logger_manager.config.get('docker', {}).get('enabled', False):
        logger.info("Docker環境檢測到，使用容器優化配置")
    
    # 記錄環境信息
    logger.debug(f"Python版本: {sys.version}")
    logger.debug(f"工作目錄: {os.getcwd()}")
    logger.debug(f"環境變量: DOCKER_CONTAINER={os.getenv('DOCKER_CONTAINER', 'false')}")


def get_session_logger(session_id: str, module_name: str = 'session') -> 'logging.Logger':
    """
    獲取會話專用日誌器
    
    Args:
        session_id: 會話ID
        module_name: 模塊名稱
        
    Returns:
        配置好的日誌器
    """
    logger_name = f"{module_name}.{session_id[:8]}"  # 使用前8位會話ID
    
    # 添加會話ID到所有日誌記錄
    class SessionAdapter:
        def __init__(self, logger, session_id):
            self.logger = logger
            self.session_id = session_id
        
        def debug(self, msg, *args, **kwargs):
            kwargs.setdefault('extra', {})['session_id'] = self.session_id
            return self.logger.debug(msg, *args, **kwargs)
        
        def info(self, msg, *args, **kwargs):
            kwargs.setdefault('extra', {})['session_id'] = self.session_id
            return self.logger.info(msg, *args, **kwargs)
        
        def warning(self, msg, *args, **kwargs):
            kwargs.setdefault('extra', {})['session_id'] = self.session_id
            return self.logger.warning(msg, *args, **kwargs)
        
        def error(self, msg, *args, **kwargs):
            kwargs.setdefault('extra', {})['session_id'] = self.session_id
            return self.logger.error(msg, *args, **kwargs)
        
        def critical(self, msg, *args, **kwargs):
            kwargs.setdefault('extra', {})['session_id'] = self.session_id
            return self.logger.critical(msg, *args, **kwargs)
    
    return SessionAdapter(logger, session_id)


def log_startup_info():
    """記錄應用啟動信息"""
    logger = get_logger('tradingagents.startup')
    
    logger.info("=" * 60)
    logger.info("TradingAgents-CN 啟動")
    logger.info("=" * 60)
    
    # 系統信息
    import platform
    logger.info(f"系統: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    
    # 環境信息
    env_info = {
        'DOCKER_CONTAINER': os.getenv('DOCKER_CONTAINER', 'false'),
        'TRADINGAGENTS_LOG_LEVEL': os.getenv('TRADINGAGENTS_LOG_LEVEL', 'INFO'),
        'TRADINGAGENTS_LOG_DIR': os.getenv('TRADINGAGENTS_LOG_DIR', './logs'),
    }
    
    for key, value in env_info.items():
        logger.info(f"{key}: {value}")
    
    logger.info("=" * 60)


def log_shutdown_info():
    """記錄應用關閉信息"""
    logger = get_logger('tradingagents.shutdown')
    
    logger.info("=" * 60)
    logger.info("TradingAgents-CN 關閉")
    logger.info("=" * 60)


# 便捷函數
def setup_web_logging():
    """設置Web應用專用日誌"""
    init_logging()
    log_startup_info()
    return get_logger('web')


def setup_analysis_logging(session_id: str):
    """設置分析專用日誌"""
    return get_session_logger(session_id, 'analysis')


def setup_dataflow_logging():
    """設置數據流專用日誌"""
    return get_logger('dataflows')


def setup_llm_logging():
    """設置LLM相關模組專用日誌"""
    return get_logger('llm')


if __name__ == "__main__":
    # 測試日誌系統
    init_logging()
    log_startup_info()
    
    # 測試不同模塊的日誌
    web_logger = setup_web_logging()
    web_logger.info("Web模塊日誌測試")
    
    analysis_logger = setup_analysis_logging("test-session-123")
    analysis_logger.info("分析模塊日誌測試")
    
    dataflow_logger = setup_dataflow_logging()
    dataflow_logger.info("數據流模塊日誌測試")
    
    llm_logger = setup_llm_logging()
    llm_logger.info("LLM適配器模塊日誌測試")
    
    log_shutdown_info()
