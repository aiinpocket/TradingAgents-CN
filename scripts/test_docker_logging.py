#!/usr/bin/env python3
"""
測試Docker環境下的日誌功能
"""

import os
import sys
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_logging():
    """測試日誌功能"""
    print("🧪 測試Docker環境日誌功能")
    print("=" * 50)
    
    try:
        # 設置Docker環境變量
        os.environ['DOCKER_CONTAINER'] = 'true'
        os.environ['TRADINGAGENTS_LOG_DIR'] = '/app/logs'
        
        # 導入日誌模塊
        from tradingagents.utils.logging_init import init_logging, get_logger
        
        # 初始化日誌
        print("📋 初始化日誌系統...")
        init_logging()
        
        # 獲取日誌器
        logger = get_logger('test')
        
        # 測試各種級別的日誌
        print("📝 寫入測試日誌...")
        logger.debug("🔍 這是DEBUG級別日誌")
        logger.info("ℹ️ 這是INFO級別日誌")
        logger.warning("⚠️ 這是WARNING級別日誌")
        logger.error("❌ 這是ERROR級別日誌")
        
        # 檢查日誌文件
        log_dir = Path("/app/logs")
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log*"))
            print(f"📄 找到日誌文件: {len(log_files)} 個")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"   📄 {log_file.name}: {size} 字節")
        else:
            print("❌ 日誌目錄不存在")
        
        print("✅ 日誌測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 日誌測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_logging()
    sys.exit(0 if success else 1)
