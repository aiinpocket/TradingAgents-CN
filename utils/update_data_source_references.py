#!/usr/bin/env python3
"""
批量更新數據源引用
将所有"通達信"引用更新為"Tushare"或通用描述
"""

import os
import re
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')


def update_file_content(file_path: Path, replacements: list):
    """更新文件內容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_text, new_text in replacements:
            content = content.replace(old_text, new_text)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ 更新: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"❌ 更新失败 {file_path}: {e}")
        return False

def main():
    """主函數"""
    logger.info(f"🔧 批量更新數據源引用")
    logger.info(f"=")
    
    # 項目根目錄
    project_root = Path(__file__).parent.parent
    
    # 需要更新的文件模式
    file_patterns = [
        "**/*.py",
        "**/*.md",
        "**/*.txt"
    ]
    
    # 排除的目錄
    exclude_dirs = {
        ".git", "__pycache__", "env", "venv", ".vscode", 
        "node_modules", ".pytest_cache", "dist", "build"
    }
    
    # 替換規則
    replacements = [
        # 數據來源標识
        ("數據來源: Tushare數據接口", "數據來源: Tushare數據接口"),
        ("數據來源: Tushare數據接口 (實時數據)", "數據來源: Tushare數據接口"),
        ("數據來源: Tushare數據接口\n", "數據來源: Tushare數據接口\n"),
        
        # 用戶界面提示
        ("使用中國股票數據源進行基本面分析", "使用中國股票數據源進行基本面分析"),
        ("使用中國股票數據源", "使用中國股票數據源"),
        ("Tushare數據接口 + 基本面分析模型", "Tushare數據接口 + 基本面分析模型"),
        
        # 錯誤提示
        ("由於數據接口限制", "由於數據接口限制"),
        ("數據接口需要網絡連接", "數據接口需要網絡連接"),
        ("數據服務器", "數據服務器"),
        
        # 技術文档
        ("Tushare + FinnHub API", "Tushare + FinnHub API"),
        ("Tushare數據接口", "Tushare數據接口"),
        
        # CLI提示
        ("将使用中國股票數據源", "将使用中國股票數據源"),
        ("china_stock", "china_stock"),
        
        # 註釋和說明
        ("# 中國股票數據", "# 中國股票數據"),
        ("數據源搜索功能", "數據源搜索功能"),
        
        # 變量名和標识符 (保持代碼功能，只更新顯示文本)
        ("'china_stock'", "'china_stock'"),
        ('"china_stock"', '"china_stock"'),
    ]
    
    # 收集所有需要更新的文件
    files_to_update = []
    
    for pattern in file_patterns:
        for file_path in project_root.glob(pattern):
            # 檢查是否在排除目錄中
            if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                continue
            
            # 跳過二進制文件和特殊文件
            if file_path.suffix in {'.pyc', '.pyo', '.so', '.dll', '.exe'}:
                continue
                
            files_to_update.append(file_path)
    
    logger.info(f"📁 找到 {len(files_to_update)} 個文件需要檢查")
    
    # 更新文件
    updated_count = 0
    
    for file_path in files_to_update:
        if update_file_content(file_path, replacements):
            updated_count += 1
    
    logger.info(f"\n📊 更新完成:")
    logger.info(f"   檢查文件: {len(files_to_update)}")
    logger.info(f"   更新文件: {updated_count}")
    
    if updated_count > 0:
        logger.info(f"\n🎉 成功更新 {updated_count} 個文件的數據源引用！")
        logger.info(f"\n📋 主要更新內容:")
        logger.info(f"   ✅ 'Tushare數據接口' → 'Tushare數據接口'")
        logger.info(f"   ✅ '通達信數據源' → '中國股票數據源'")
        logger.error(f"   ✅ 錯誤提示和用戶界面文本")
        logger.info(f"   ✅ 技術文档和註釋")
    else:
        logger.info(f"\n✅ 所有文件的數據源引用都是最新的")

if __name__ == "__main__":
    main()
