"""
數據目錄配置工具
Data Directory Configuration Utilities

為項目中的其他模塊提供統一的數據目錄訪問接口
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.unified_data_manager import get_data_manager, get_data_path
except ImportError:
    # 如果無法導入，提供基本的實現
    def get_data_path(key: str, create: bool = True) -> Path:
        """基本的數據路徑獲取函數"""
        project_root = Path(__file__).parent.parent
        
        # 基本路徑映射
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


# 便捷函數
def get_cache_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    獲取緩存目錄
    
    Args:
        subdir: 子目錄名稱
        create: 是否自動創建目錄
        
    Returns:
        Path: 緩存目錄路徑
    """
    if subdir:
        cache_path = get_data_path('cache', create=create) / subdir
        if create:
            cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    return get_data_path('cache', create=create)


def get_results_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    獲取分析結果目錄
    
    Args:
        subdir: 子目錄名稱
        create: 是否自動創建目錄
        
    Returns:
        Path: 結果目錄路徑
    """
    if subdir:
        results_path = get_data_path('analysis_results', create=create) / subdir
        if create:
            results_path.mkdir(parents=True, exist_ok=True)
        return results_path
    return get_data_path('analysis_results', create=create)


def get_sessions_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    獲取會話數據目錄
    
    Args:
        subdir: 子目錄名稱
        create: 是否自動創建目錄
        
    Returns:
        Path: 會話目錄路徑
    """
    if subdir:
        sessions_path = get_data_path('sessions', create=create) / subdir
        if create:
            sessions_path.mkdir(parents=True, exist_ok=True)
        return sessions_path
    return get_data_path('sessions', create=create)


def get_logs_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    獲取日誌目錄
    
    Args:
        subdir: 子目錄名稱
        create: 是否自動創建目錄
        
    Returns:
        Path: 日誌目錄路徑
    """
    if subdir:
        logs_path = get_data_path('logs', create=create) / subdir
        if create:
            logs_path.mkdir(parents=True, exist_ok=True)
        return logs_path
    return get_data_path('logs', create=create)


def get_config_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    獲取配置目錄
    
    Args:
        subdir: 子目錄名稱
        create: 是否自動創建目錄
        
    Returns:
        Path: 配置目錄路徑
    """
    if subdir:
        config_path = get_data_path('config', create=create) / subdir
        if create:
            config_path.mkdir(parents=True, exist_ok=True)
        return config_path
    return get_data_path('config', create=create)


def get_temp_dir(subdir: Optional[str] = None, create: bool = True) -> Path:
    """
    獲取臨時文件目錄
    
    Args:
        subdir: 子目錄名稱
        create: 是否自動創建目錄
        
    Returns:
        Path: 臨時目錄路徑
    """
    if subdir:
        temp_path = get_data_path('temp', create=create) / subdir
        if create:
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path
    return get_data_path('temp', create=create)


# 兼容性函數 - 為現有代碼提供向後兼容
def get_analysis_results_dir() -> Path:
    """獲取分析結果目錄 (兼容性函數)"""
    return get_results_dir()


def get_stock_data_cache_dir() -> Path:
    """獲取股票數據緩存目錄"""
    return get_cache_dir('stock_data')


def get_news_data_cache_dir() -> Path:
    """獲取新聞數據緩存目錄"""
    return get_cache_dir('news_data')


def get_fundamentals_cache_dir() -> Path:
    """獲取基本面數據緩存目錄"""
    return get_cache_dir('fundamentals')


def get_metadata_cache_dir() -> Path:
    """獲取元數據緩存目錄"""
    return get_cache_dir('metadata')


def get_web_sessions_dir() -> Path:
    """獲取Web會話目錄"""
    return get_sessions_dir('web_sessions')


def get_cli_sessions_dir() -> Path:
    """獲取CLI會話目錄"""
    return get_sessions_dir('cli_sessions')


def get_application_logs_dir() -> Path:
    """獲取應用程序日誌目錄"""
    return get_logs_dir('application')


def get_operations_logs_dir() -> Path:
    """獲取操作日誌目錄"""
    return get_logs_dir('operations')


def get_user_activities_logs_dir() -> Path:
    """獲取用戶活動日誌目錄"""
    return get_logs_dir('user_activities')


# 環境變量檢查函數
def check_data_directory_config() -> dict:
    """
    檢查數據目錄配置狀態
    
    Returns:
        dict: 配置狀態信息
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
    """打印數據目錄配置狀態"""
    print("📁 數據目錄配置狀態:")
    print("=" * 50)
    
    status = check_data_directory_config()
    
    for var, info in status.items():
        status_icon = "✅" if info['set'] else "❌"
        exists_icon = "📁" if info['exists'] else "❓"
        
        print(f"{status_icon} {var}")
        if info['set']:
            print(f"   值: {info['value']}")
            print(f"   {exists_icon} 目錄存在: {'是' if info['exists'] else '否'}")
        else:
            print("   未設置")
        print()


if __name__ == '__main__':
    print_data_directory_status()