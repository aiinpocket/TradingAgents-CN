#!/usr/bin/env python3
"""
環境變數解析工具
提供相容Python 3.13+的強健環境變數解析功能
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def parse_bool_env(env_var: str, default: bool = False) -> bool:
    """
    解析布爾類型環境變數，相容多種格式
    
    支持的格式：
    - true/True/TRUE
    - false/False/FALSE  
    - 1/0
    - yes/Yes/YES
    - no/No/NO
    - on/On/ON
    - off/Off/OFF
    
    Args:
        env_var: 環境變數名
        default: 預設值
        
    Returns:
        bool: 解析後的布爾值
    """
    value = os.getenv(env_var)
    
    if value is None:
        return default
    
    # 轉換為字串並去除空白
    value_str = str(value).strip()
    
    if not value_str:
        return default
    
    # 轉換為小寫進行比較
    value_lower = value_str.lower()
    
    # 真值列表
    true_values = {
        'true', '1', 'yes', 'on', 'enable', 'enabled', 
        't', 'y', 'ok', 'okay'
    }
    
    # 假值列表
    false_values = {
        'false', '0', 'no', 'off', 'disable', 'disabled',
        'f', 'n', 'none', 'null', 'nil'
    }
    
    if value_lower in true_values:
        return True
    elif value_lower in false_values:
        return False
    else:
        # 如果無法識別，記錄警告並返回預設值
        logger.warning(f"無法解析環境變數 {env_var}='{value}'，使用預設值 {default}")
        return default


def parse_int_env(env_var: str, default: int = 0) -> int:
    """
    解析整數類型環境變數
    
    Args:
        env_var: 環境變數名
        default: 預設值
        
    Returns:
        int: 解析後的整數值
    """
    value = os.getenv(env_var)
    
    if value is None:
        return default
    
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        logger.warning(f"無法解析環境變數 {env_var}='{value}' 為整數，使用預設值 {default}")
        return default


def parse_float_env(env_var: str, default: float = 0.0) -> float:
    """
    解析浮點數類型環境變數
    
    Args:
        env_var: 環境變數名
        default: 預設值
        
    Returns:
        float: 解析後的浮點數值
    """
    value = os.getenv(env_var)
    
    if value is None:
        return default
    
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        logger.warning(f"無法解析環境變數 {env_var}='{value}' 為浮點數，使用預設值 {default}")
        return default


def parse_str_env(env_var: str, default: str = "") -> str:
    """
    解析字串類型環境變數
    
    Args:
        env_var: 環境變數名
        default: 預設值
        
    Returns:
        str: 解析後的字串值
    """
    value = os.getenv(env_var)
    
    if value is None:
        return default
    
    return str(value).strip()


def parse_list_env(env_var: str, separator: str = ",", default: Optional[list] = None) -> list:
    """
    解析列表類型環境變數
    
    Args:
        env_var: 環境變數名
        separator: 分隔符
        default: 預設值
        
    Returns:
        list: 解析後的列表
    """
    if default is None:
        default = []
    
    value = os.getenv(env_var)
    
    if value is None:
        return default
    
    try:
        # 分割並去除空白
        items = [item.strip() for item in value.split(separator)]
        # 過濾空字串
        return [item for item in items if item]
    except AttributeError:
        logger.warning(f"無法解析環境變數 {env_var}='{value}' 為列表，使用預設值 {default}")
        return default


def get_env_info(env_var: str) -> dict:
    """
    取得環境變數的詳細資訊
    
    Args:
        env_var: 環境變數名
        
    Returns:
        dict: 環境變數資訊
    """
    value = os.getenv(env_var)
    
    return {
        'name': env_var,
        'value': value,
        'exists': value is not None,
        'empty': value is None or str(value).strip() == '',
        'type': type(value).__name__ if value is not None else 'None',
        'length': len(str(value)) if value is not None else 0
    }


def validate_required_env_vars(required_vars: list) -> dict:
    """
    驗證必需的環境變數是否已設定
    
    Args:
        required_vars: 必需的環境變數列表
        
    Returns:
        dict: 驗證結果
    """
    results = {
        'all_set': True,
        'missing': [],
        'empty': [],
        'valid': []
    }
    
    for var in required_vars:
        info = get_env_info(var)
        
        if not info['exists']:
            results['missing'].append(var)
            results['all_set'] = False
        elif info['empty']:
            results['empty'].append(var)
            results['all_set'] = False
        else:
            results['valid'].append(var)
    
    return results


# 相容性函數：保持向後相容
def get_bool_env(env_var: str, default: bool = False) -> bool:
    """向後相容的布爾值解析函數"""
    return parse_bool_env(env_var, default)


def get_int_env(env_var: str, default: int = 0) -> int:
    """向後相容的整數解析函數"""
    return parse_int_env(env_var, default)


def get_str_env(env_var: str, default: str = "") -> str:
    """向後相容的字串解析函數"""
    return parse_str_env(env_var, default)


# 匯出主要函數
__all__ = [
    'parse_bool_env',
    'parse_int_env', 
    'parse_float_env',
    'parse_str_env',
    'parse_list_env',
    'get_env_info',
    'validate_required_env_vars',
    'get_bool_env',  # 向後相容
    'get_int_env',   # 向後相容
    'get_str_env'    # 向後相容
]
