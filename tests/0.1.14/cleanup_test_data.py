#!/usr/bin/env python3
"""
清理測試數據
"""

import sys
import os
from pathlib import Path

# 添加項目路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

def cleanup_test_files():
    """清理測試文件"""
    print("🧹 清理測試文件...")
    
    # 清理詳細報告目錄
    project_root = Path(__file__).parent
    test_dir = project_root / "data" / "analysis_results" / "TEST123"
    
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print(f"✅ 已刪除測試目錄: {test_dir}")
    else:
        print(f"⚠️ 測試目錄不存在: {test_dir}")

def cleanup_mongodb_test_data():
    """清理MongoDB測試數據"""
    print("🗄️ 清理MongoDB測試數據...")
    
    try:
        from web.utils.mongodb_report_manager import mongodb_report_manager
        
        if not mongodb_report_manager.connected:
            print("❌ MongoDB未連接")
            return
        
        # 刪除測試數據
        collection = mongodb_report_manager.collection
        result = collection.delete_many({"stock_symbol": "TEST123"})
        
        print(f"✅ 已刪除 {result.deleted_count} 條TEST123相關記錄")
        
        # 刪除其他測試數據
        result2 = collection.delete_many({"stock_symbol": "TEST001"})
        print(f"✅ 已刪除 {result2.deleted_count} 條TEST001相關記錄")
        
    except Exception as e:
        print(f"❌ MongoDB清理失败: {e}")

def main():
    """主函數"""
    print("🧹 清理測試數據")
    print("=" * 30)
    
    cleanup_test_files()
    cleanup_mongodb_test_data()
    
    print("\n🎉 清理完成")

if __name__ == "__main__":
    main()
