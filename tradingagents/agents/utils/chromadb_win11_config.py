# Windows 11 ChromaDB 優化配置
import os
import platform
import chromadb
from chromadb.config import Settings

def is_windows_11():
    '''檢測是否為Windows 11'''
    if platform.system() != "Windows":
        return False
    
    # Windows 11的版本號通常是10.0.22000或更高
    version = platform.version()
    try:
        # 提取版本號，格式通常是 "10.0.26100"
        version_parts = version.split('.')
        if len(version_parts) >= 3:
            build_number = int(version_parts[2])
            # Windows 11的構建號從22000開始
            return build_number >= 22000
    except (ValueError, IndexError):
        pass
    
    return False

def get_win11_chromadb_client():
    '''獲取Windows 11優化的ChromaDB客戶端'''
    # Windows 11 對 ChromaDB 支持更好，可以使用更現代的配置
    settings = Settings(
        allow_reset=True,
        anonymized_telemetry=False,  # 禁用遙測避免posthog錯誤
        is_persistent=False,
        # Windows 11 可以使用預設實現，性能更好
        chroma_db_impl="duckdb+parquet",
        chroma_api_impl="chromadb.api.segment.SegmentAPI"
        # 移除persist_directory=None，讓它使用預設值
    )
    
    try:
        client = chromadb.Client(settings)
        return client
    except Exception as e:
        # 如果還有問題，使用最簡配置
        minimal_settings = Settings(
            allow_reset=True,
            anonymized_telemetry=False,  # 關鍵：禁用遙測
            is_persistent=False
        )
        return chromadb.Client(minimal_settings)

def get_optimal_chromadb_client():
    '''根據Windows版本自動選擇最優ChromaDB配置'''
    system = platform.system()
    
    if system == "Windows":
        # 使用更準確的Windows 11檢測
        if is_windows_11():
            # Windows 11 或更新版本
            return get_win11_chromadb_client()
        else:
            # Windows 10 或更老版本，使用兼容配置
            from .chromadb_win10_config import get_win10_chromadb_client
            return get_win10_chromadb_client()
    else:
        # 非Windows系統，使用標準配置
        settings = Settings(
            allow_reset=True,
            anonymized_telemetry=False,
            is_persistent=False
        )
        return chromadb.Client(settings)

# 導出配置
__all__ = ['get_win11_chromadb_client', 'get_optimal_chromadb_client', 'is_windows_11']