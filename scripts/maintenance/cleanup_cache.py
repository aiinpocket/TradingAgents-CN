#!/usr/bin/env python3
"""
快取清理工具
清理過期的快取檔案和資料庫記錄
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 新增專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def cleanup_file_cache(max_age_days: int = 7):
    """清理檔案快取"""
    logger.info(f" 清理 {max_age_days} 天前的檔案快取...")
    
    cache_dirs = [
        project_root / "cache",
        project_root / "data" / "cache", 
        project_root / "tradingagents" / "dataflows" / "data_cache"
    ]
    
    total_cleaned = 0
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    
    for cache_dir in cache_dirs:
        if not cache_dir.exists():
            continue
            
        logger.info(f" 檢查快取目錄: {cache_dir}")
        
        for cache_file in cache_dir.rglob("*"):
            if cache_file.is_file():
                try:
                    file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        cache_file.unlink()
                        total_cleaned += 1
                        logger.info(f"   刪除: {cache_file.name}")
                except Exception as e:
                    logger.error(f"   刪除失敗: {cache_file.name} - {e}")
    
    logger.info(f" 檔案快取清理完成，刪除了 {total_cleaned} 個檔案")
    return total_cleaned

def cleanup_database_cache(max_age_days: int = 7):
    """清理資料庫快取"""
    logger.info(f" 清理 {max_age_days} 天前的資料庫快取...")
    
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        
        if hasattr(cache, 'clear_old_cache'):
            cleared_count = cache.clear_old_cache(max_age_days)
            logger.info(f" 資料庫快取清理完成，刪除了 {cleared_count} 條記錄")
            return cleared_count
        else:
            logger.info("[INFO]當前快取系統不支援自動清理")
            return 0
            
    except Exception as e:
        logger.error(f" 資料庫快取清理失敗: {e}")
        return 0

def cleanup_python_cache():
    """清理Python快取檔案"""
    logger.info(f" 清理Python快取檔案...")
    
    cache_patterns = ["__pycache__", "*.pyc", "*.pyo"]
    total_cleaned = 0
    
    for pattern in cache_patterns:
        if pattern == "__pycache__":
            cache_dirs = list(project_root.rglob(pattern))
            for cache_dir in cache_dirs:
                try:
                    import shutil
                    shutil.rmtree(cache_dir)
                    total_cleaned += 1
                    logger.info(f"   刪除目錄: {cache_dir.relative_to(project_root)}")
                except Exception as e:
                    logger.error(f"   刪除失敗: {cache_dir.relative_to(project_root)} - {e}")
        else:
            cache_files = list(project_root.rglob(pattern))
            for cache_file in cache_files:
                try:
                    cache_file.unlink()
                    total_cleaned += 1
                    logger.info(f"   刪除檔案: {cache_file.relative_to(project_root)}")
                except Exception as e:
                    logger.error(f"   刪除失敗: {cache_file.relative_to(project_root)} - {e}")
    
    logger.info(f" Python快取清理完成，刪除了 {total_cleaned} 個項目")
    return total_cleaned

def get_cache_statistics():
    """取得快取統計資訊"""
    logger.info(f" 取得快取統計資訊...")
    
    try:
        from tradingagents.dataflows.integrated_cache import get_cache
        
        cache = get_cache()
        
        logger.info(f" 快取模式: {cache.get_performance_mode()}")
        logger.info(f" 資料庫可用: {'是' if cache.is_database_available() else '否'}")
        
        # 統計檔案快取
        cache_dirs = [
            project_root / "cache",
            project_root / "data" / "cache",
            project_root / "tradingagents" / "dataflows" / "data_cache"
        ]
        
        total_files = 0
        total_size = 0
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                for cache_file in cache_dir.rglob("*"):
                    if cache_file.is_file():
                        total_files += 1
                        total_size += cache_file.stat().st_size
        
        logger.info(f" 檔案快取: {total_files} 個檔案，{total_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        logger.error(f" 取得快取統計失敗: {e}")

def main():
    """主函式"""
    logger.info(f" TradingAgents 快取清理工具")
    logger.info(f"=")
    
    import argparse

    parser = argparse.ArgumentParser(description="清理TradingAgents快取")
    parser.add_argument("--days", type=int, default=7, help="清理多少天前的快取 (預設: 7)")
    parser.add_argument("--type", choices=["all", "file", "database", "python"], 
                       default="all", help="清理類型 (預設: all)")
    parser.add_argument("--stats", action="store_true", help="只顯示統計資訊，不清理")
    
    args = parser.parse_args()
    
    if args.stats:
        get_cache_statistics()
        return
    
    total_cleaned = 0
    
    if args.type in ["all", "file"]:
        total_cleaned += cleanup_file_cache(args.days)
    
    if args.type in ["all", "database"]:
        total_cleaned += cleanup_database_cache(args.days)
    
    if args.type in ["all", "python"]:
        total_cleaned += cleanup_python_cache()
    
    logger.info(f"\n")
    logger.info(f" 快取清理完成！總共清理了 {total_cleaned} 個項目")
    logger.info(f"\n 使用提示:")
    logger.info(f"  --stats     查看快取統計")
    logger.info(f"  --days 3    清理3天前的快取")
    logger.info(f"  --type file 只清理檔案快取")

if __name__ == "__main__":
    main()
