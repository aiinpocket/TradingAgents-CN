#!/usr/bin/env python3
"""
簡單的日誌測試 - 避免複雜導入
"""

import os
import logging
import logging.handlers
from pathlib import Path

def simple_log_test():
    """簡單的日誌測試"""
    print("🧪 簡單日誌測試")
    
    # 創建日誌目錄
    log_dir = Path("/app/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 創建簡單的日誌配置
    logger = logging.getLogger("simple_test")
    logger.setLevel(logging.DEBUG)
    
    # 清除現有處理器
    logger.handlers.clear()
    
    # 添加控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 添加文件處理器
    try:
        log_file = log_dir / "simple_test.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s | %(name)-20s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        print(f"✅ 文件處理器創建成功: {log_file}")
    except Exception as e:
        print(f"❌ 文件處理器創建失败: {e}")
        return False
    
    # 測試日誌寫入
    try:
        logger.debug("🔍 DEBUG級別測試日誌")
        logger.info("ℹ️ INFO級別測試日誌")
        logger.warning("⚠️ WARNING級別測試日誌")
        logger.error("❌ ERROR級別測試日誌")
        
        print("✅ 日誌寫入測試完成")
        
        # 檢查文件是否生成
        if log_file.exists():
            size = log_file.stat().st_size
            print(f"📄 日誌文件大小: {size} 字節")
            
            if size > 0:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"📄 日誌文件行數: {len(lines)}")
                    if lines:
                        print("📄 最後一行:")
                        print(f"   {lines[-1].strip()}")
                return True
            else:
                print("⚠️ 日誌文件為空")
                return False
        else:
            print("❌ 日誌文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 日誌寫入失败: {e}")
        return False

if __name__ == "__main__":
    success = simple_log_test()
    exit(0 if success else 1)
