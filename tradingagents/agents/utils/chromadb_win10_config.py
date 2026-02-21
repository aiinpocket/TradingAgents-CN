# Windows 10 ChromaDB 兼容性配置
import os
import tempfile
import chromadb
from chromadb.config import Settings

# Windows 10 專用配置
def get_win10_chromadb_client():
    '''獲取Windows 10兼容的ChromaDB客戶端'''
    settings = Settings(
        allow_reset=True,
        anonymized_telemetry=False,
        is_persistent=False,
        # Windows 10 特定配置
        chroma_db_impl="duckdb+parquet",
        chroma_api_impl="chromadb.api.segment.SegmentAPI",
        # 使用臨時目錄避免權限問題
        persist_directory=None
    )
    
    try:
        client = chromadb.Client(settings)
        return client
    except Exception as e:
        # 降級到最基本配置
        basic_settings = Settings(
            allow_reset=True,
            is_persistent=False
        )
        return chromadb.Client(basic_settings)

# 導出配置
__all__ = ['get_win10_chromadb_client']
