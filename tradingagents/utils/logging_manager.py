#!/usr/bin/env python3
"""
統一日誌管理器
提供專案層級的日誌配置和管理功能
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json
import toml

# 註意：這裡不能匯入自己，會造成循環匯入
# 在日誌系統初始化前，使用標準庫自舉日誌器，避免未定義引用
_bootstrap_logger = logging.getLogger("tradingagents.logging_manager")


class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器"""
    
    # ANSI顏色碼
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 綠色
        'WARNING': '\033[33m',  # 黃色
        'ERROR': '\033[31m',    # 紅色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加顏色
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """結構化日誌格式化器（JSON格式）"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加額外字段
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'analysis_type'):
            log_entry['analysis_type'] = record.analysis_type
        if hasattr(record, 'stock_symbol'):
            log_entry['stock_symbol'] = record.stock_symbol
        if hasattr(record, 'cost'):
            log_entry['cost'] = record.cost
        if hasattr(record, 'tokens'):
            log_entry['tokens'] = record.tokens
            
        return json.dumps(log_entry, ensure_ascii=False)


class TradingAgentsLogger:
    """TradingAgents統一日誌管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """載入預設日誌配置"""
        # 嘗試從配置檔載入
        config = self._load_config_file()
        if config:
            return config

        # 從環境變數取得配置
        log_level = os.getenv('TRADINGAGENTS_LOG_LEVEL', 'INFO').upper()
        log_dir = os.getenv('TRADINGAGENTS_LOG_DIR', './logs')

        return {
            'level': log_level,
            'format': {
                'console': '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
                'file': '%(asctime)s | %(name)-20s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
                'structured': 'json'
            },
            'handlers': {
                'console': {
                    'enabled': True,
                    'colored': True,
                    'level': log_level
                },
                'file': {
                    'enabled': True,
                    'level': 'DEBUG',
                    'max_size': '10MB',
                    'backup_count': 5,
                    'directory': log_dir
                },
                'structured': {
                    'enabled': False,  # 預設關閉，可通過環境變數啟用
                    'level': 'INFO',
                    'directory': log_dir
                }
            },
            'loggers': {
                'tradingagents': {'level': log_level},
                'web': {'level': log_level},
                'streamlit': {'level': 'WARNING'},  # Streamlit日誌較多，設為WARNING
                'urllib3': {'level': 'WARNING'},    # HTTP請求日誌較多
                'requests': {'level': 'WARNING'},
                'matplotlib': {'level': 'WARNING'}
            },
            'docker': {
                'enabled': os.getenv('DOCKER_CONTAINER', 'false').lower() == 'true',
                'stdout_only': True  # Docker環境只輸出到stdout
            }
        }

    def _load_config_file(self) -> Optional[Dict[str, Any]]:
        """從配置檔載入日誌配置"""
        # 確定配置檔案路徑
        config_paths = [
            'config/logging_docker.toml' if os.getenv('DOCKER_CONTAINER') == 'true' else None,
            'config/logging.toml',
            './logging.toml'
        ]

        for config_path in config_paths:
            if config_path and Path(config_path).exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = toml.load(f)

                    # 轉換配置格式
                    return self._convert_toml_config(config_data)
                except Exception as e:
                    _bootstrap_logger.warning(f"警告: 無法載入配置檔 {config_path}: {e}")
                    continue

        return None

    def _convert_toml_config(self, toml_config: Dict[str, Any]) -> Dict[str, Any]:
        """將TOML配置轉換為內部配置格式"""
        logging_config = toml_config.get('logging', {})

        # 檢查Docker環境
        is_docker = (
            os.getenv('DOCKER_CONTAINER') == 'true' or
            logging_config.get('docker', {}).get('enabled', False)
        )

        return {
            'level': logging_config.get('level', 'INFO'),
            'format': logging_config.get('format', {}),
            'handlers': logging_config.get('handlers', {}),
            'loggers': logging_config.get('loggers', {}),
            'docker': {
                'enabled': is_docker,
                'stdout_only': logging_config.get('docker', {}).get('stdout_only', True)
            },
            'performance': logging_config.get('performance', {}),
            'security': logging_config.get('security', {}),
            'business': logging_config.get('business', {})
        }
    
    def _setup_logging(self):
        """設定日誌系統"""
        # 建立日誌目錄
        if self.config['handlers']['file']['enabled']:
            log_dir = Path(self.config['handlers']['file']['directory'])
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                # 如果無法建立日誌目錄（例如只讀檔案系統），禁用檔案日誌
                import warnings
                warnings.warn(f"無法建立日誌目錄 {log_dir}: {e}，禁用檔案日誌")
                self.config['handlers']['file']['enabled'] = False
        
        # 設定根日誌等級
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config['level']))
        
        # 清除現有處理器
        root_logger.handlers.clear()
        
        # 添加處理器
        self._add_console_handler(root_logger)
        
        if not self.config['docker']['enabled'] or not self.config['docker']['stdout_only']:
            self._add_file_handler(root_logger)
            if self.config['handlers']['structured']['enabled']:
                self._add_structured_handler(root_logger)
        
        # 配置特定日誌器
        self._configure_specific_loggers()
    
    def _add_console_handler(self, logger: logging.Logger):
        """添加主控台處理器"""
        if not self.config['handlers']['console']['enabled']:
            return
            
        console_handler = logging.StreamHandler(sys.stdout)
        console_level = getattr(logging, self.config['handlers']['console']['level'])
        console_handler.setLevel(console_level)
        
        # 選擇格式化器
        if self.config['handlers']['console']['colored'] and sys.stdout.isatty():
            formatter = ColoredFormatter(self.config['format']['console'])
        else:
            formatter = logging.Formatter(self.config['format']['console'])
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    def _add_file_handler(self, logger: logging.Logger):
        """添加檔案處理器"""
        if not self.config['handlers']['file']['enabled']:
            return
            
        log_dir = Path(self.config['handlers']['file']['directory'])
        log_file = log_dir / 'tradingagents.log'
        
        # 使用RotatingFileHandler進行日誌輪轉
        max_size = self._parse_size(self.config['handlers']['file']['max_size'])
        backup_count = self.config['handlers']['file']['backup_count']
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        file_level = getattr(logging, self.config['handlers']['file']['level'])
        file_handler.setLevel(file_level)
        
        formatter = logging.Formatter(self.config['format']['file'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    def _add_structured_handler(self, logger: logging.Logger):
        """添加結構化日誌處理器"""
        try:
            log_dir = Path(self.config['handlers']['structured']['directory'])
            log_file = log_dir / 'tradingagents_structured.log'

            structured_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self._parse_size('10MB'),
                backupCount=3,
                encoding='utf-8'
            )

            structured_level = getattr(logging, self.config['handlers']['structured']['level'])
            structured_handler.setLevel(structured_level)

            formatter = StructuredFormatter()
            structured_handler.setFormatter(formatter)
            logger.addHandler(structured_handler)
        except (OSError, PermissionError, FileNotFoundError) as e:
            # 如果無法建立structured日誌，只輸出警告但不中斷
            import warnings
            warnings.warn(f"無法建立結構化日誌檔案: {e}，跳過structured handler")
    
    def _configure_specific_loggers(self):
        """配置特定的日誌器"""
        for logger_name, logger_config in self.config['loggers'].items():
            logger = logging.getLogger(logger_name)
            level = getattr(logging, logger_config['level'])
            logger.setLevel(level)
    
    def _parse_size(self, size_str: str) -> int:
        """解析大小字串（如'10MB'）為位元組數"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def get_logger(self, name: str) -> logging.Logger:
        """取得指定名稱的日誌器"""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]
    
    def log_analysis_start(self, logger: logging.Logger, stock_symbol: str, analysis_type: str, session_id: str):
        """記錄分析開始"""
        logger.info(
            f"開始分析 - 股票: {stock_symbol}, 類型: {analysis_type}",
            extra={
                'stock_symbol': stock_symbol,
                'analysis_type': analysis_type,
                'session_id': session_id,
                'event_type': 'analysis_start',
                'timestamp': datetime.now().isoformat()
            }
        )

    def log_analysis_complete(self, logger: logging.Logger, stock_symbol: str, analysis_type: str,
                            session_id: str, duration: float, cost: float = 0):
        """記錄分析完成"""
        logger.info(
            f"分析完成 - 股票: {stock_symbol}, 耗時: {duration:.2f}s, 成本: ¥{cost:.4f}",
            extra={
                'stock_symbol': stock_symbol,
                'analysis_type': analysis_type,
                'session_id': session_id,
                'duration': duration,
                'cost': cost,
                'event_type': 'analysis_complete',
                'timestamp': datetime.now().isoformat()
            }
        )

    def log_module_start(self, logger: logging.Logger, module_name: str, stock_symbol: str,
                        session_id: str, **extra_data):
        """記錄模組開始分析"""
        logger.info(
            f"[模組開始] {module_name} - 股票: {stock_symbol}",
            extra={
                'module_name': module_name,
                'stock_symbol': stock_symbol,
                'session_id': session_id,
                'event_type': 'module_start',
                'timestamp': datetime.now().isoformat(),
                **extra_data
            }
        )

    def log_module_complete(self, logger: logging.Logger, module_name: str, stock_symbol: str,
                           session_id: str, duration: float, success: bool = True,
                           result_length: int = 0, **extra_data):
        """記錄模組完成分析"""
        status = "成功" if success else "失敗"
        logger.info(
            f"[模組完成] {module_name} - {status} - 股票: {stock_symbol}, 耗時: {duration:.2f}s",
            extra={
                'module_name': module_name,
                'stock_symbol': stock_symbol,
                'session_id': session_id,
                'duration': duration,
                'success': success,
                'result_length': result_length,
                'event_type': 'module_complete',
                'timestamp': datetime.now().isoformat(),
                **extra_data
            }
        )

    def log_module_error(self, logger: logging.Logger, module_name: str, stock_symbol: str,
                        session_id: str, duration: float, error: str, **extra_data):
        """記錄模組分析錯誤"""
        logger.error(
            f"[模組錯誤] {module_name} - 股票: {stock_symbol}, 耗時: {duration:.2f}s, 錯誤: {error}",
            extra={
                'module_name': module_name,
                'stock_symbol': stock_symbol,
                'session_id': session_id,
                'duration': duration,
                'error': error,
                'event_type': 'module_error',
                'timestamp': datetime.now().isoformat(),
                **extra_data
            },
            exc_info=True
        )
    
    def log_token_usage(self, logger: logging.Logger, provider: str, model: str, 
                       input_tokens: int, output_tokens: int, cost: float, session_id: str):
        """記錄Token使用"""
        logger.info(
            f"Token使用 - {provider}/{model}: 輸入={input_tokens}, 輸出={output_tokens}, 成本=¥{cost:.6f}",
            extra={
                'provider': provider,
                'model': model,
                'tokens': {'input': input_tokens, 'output': output_tokens},
                'cost': cost,
                'session_id': session_id,
                'event_type': 'token_usage'
            }
        )


# 全局日誌管理器實例
_logger_manager: Optional[TradingAgentsLogger] = None


def get_logger_manager() -> TradingAgentsLogger:
    """取得全局日誌管理器實例"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = TradingAgentsLogger()
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """取得指定名稱的日誌器（便捷函式）"""
    return get_logger_manager().get_logger(name)


def setup_logging(config: Optional[Dict[str, Any]] = None):
    """設定項目日誌系統（便捷函式）"""
    global _logger_manager
    _logger_manager = TradingAgentsLogger(config)
    return _logger_manager
