"""

Data Directory Configuration Utilities


"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

#  Python 
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.unified_data_manager import get_data_manager, get_data_path
except ImportError:
    # 
    def get_data_path(key: str, create: bool = True) -> Path:
        """"""
        project_root = Path(__file__).parent.parent
        
        # 
        path_mapping = {
            'data_root': 'data',
            'cache': 'data/cache',
            'analysis_results': 'data/analysis_results',
            'sessions': 'data/sessions',
            'logs': 'data/logs',
            'config': 'data/config',
            'temp': 'data/temp',
        }
        
        path_str = path_mapping.get(key, f'data/{key}')
        path = project_root / path_str
        
        if create:
            path.mkdir(parents=True, exist_ok=True)
        
        return path


# 
def get_cache_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    
    
    Args:
        subdir: 
        create: 
        
    Returns:
        Path: 
    """
    if subdir:
        cache_path = get_data_path('cache', create=create) / subdir
        if create:
            cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    return get_data_path('cache', create=create)


def get_results_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    
    
    Args:
        subdir: 
        create: 
        
    Returns:
        Path: 
    """
    if subdir:
        results_path = get_data_path('analysis_results', create=create) / subdir
        if create:
            results_path.mkdir(parents=True, exist_ok=True)
        return results_path
    return get_data_path('analysis_results', create=create)


def get_sessions_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    
    
    Args:
        subdir: 
        create: 
        
    Returns:
        Path: 
    """
    if subdir:
        sessions_path = get_data_path('sessions', create=create) / subdir
        if create:
            sessions_path.mkdir(parents=True, exist_ok=True)
        return sessions_path
    return get_data_path('sessions', create=create)


def get_logs_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    
    
    Args:
        subdir: 
        create: 
        
    Returns:
        Path: 
    """
    if subdir:
        logs_path = get_data_path('logs', create=create) / subdir
        if create:
            logs_path.mkdir(parents=True, exist_ok=True)
        return logs_path
    return get_data_path('logs', create=create)


def get_config_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    
    
    Args:
        subdir: 
        create: 
        
    Returns:
        Path: 
    """
    if subdir:
        config_path = get_data_path('config', create=create) / subdir
        if create:
            config_path.mkdir(parents=True, exist_ok=True)
        return config_path
    return get_data_path('config', create=create)


def get_temp_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    
    
    Args:
        subdir: 
        create: 
        
    Returns:
        Path: 
    """
    if subdir:
        temp_path = get_data_path('temp', create=create) / subdir
        if create:
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path
    return get_data_path('temp', create=create)


#  - 
def get_analysis_results_dir() -> Path:
    """ ()"""
    return get_results_dir()


def get_stock_data_cache_dir() -> Path:
    """"""
    return get_cache_dir('stock_data')


def get_news_data_cache_dir() -> Path:
    """"""
    return get_cache_dir('news_data')


def get_fundamentals_cache_dir() -> Path:
    """"""
    return get_cache_dir('fundamentals')


def get_metadata_cache_dir() -> Path:
    """"""
    return get_cache_dir('metadata')


def get_web_sessions_dir() -> Path:
    """Web"""
    return get_sessions_dir('web_sessions')


def get_cli_sessions_dir() -> Path:
    """CLI"""
    return get_sessions_dir('cli_sessions')


def get_application_logs_dir() -> Path:
    """"""
    return get_logs_dir('application')


def get_operations_logs_dir() -> Path:
    """"""
    return get_logs_dir('operations')


def get_user_activities_logs_dir() -> Path:
    """"""
    return get_logs_dir('user_activities')


# 
def check_data_directory_config() -> dict:
    """
    
    
    Returns:
        dict: 
    """
    env_vars = [
        'TRADINGAGENTS_DATA_DIR',
        'TRADINGAGENTS_CACHE_DIR',
        'TRADINGAGENTS_RESULTS_DIR',
        'TRADINGAGENTS_SESSIONS_DIR',
        'TRADINGAGENTS_LOGS_DIR',
        'TRADINGAGENTS_CONFIG_DIR',
        'TRADINGAGENTS_TEMP_DIR',
    ]
    
    config_status = {}
    for var in env_vars:
        value = os.getenv(var)
        config_status[var] = {
            'set': value is not None,
            'value': value,
            'exists': Path(value).exists() if value else False
        }
    
    return config_status


def print_data_directory_status():
    """"""
    print(" :")
    print("=" * 50)
    
    status = check_data_directory_config()
    
    for var, info in status.items():
        status_icon = "" if info['set'] else ""
        exists_icon = "" if info['exists'] else ""
        
        print(f"{status_icon} {var}")
        if info['set']:
            print(f"   : {info['value']}")
            print(f"   {exists_icon} : {'' if info['exists'] else ''}")
        else:
            print("   ")
        print()


if __name__ == '__main__':
    print_data_directory_status()