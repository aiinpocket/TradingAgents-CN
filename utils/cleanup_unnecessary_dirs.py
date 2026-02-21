#!/usr/bin/env python3
"""
清理不必要的目錄和文件
移除自動生成的文件和臨時輸出
"""

import os
import shutil
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')


def cleanup_directories():
    """清理不必要的目錄"""
    logger.info(f"🧹 清理不必要的目錄和文件")
    logger.info(f"=")
    
    # 項目根目錄
    project_root = Path(".")
    
    # 需要清理的目錄
    cleanup_dirs = [
        "tradingagents.egg-info",
        "enhanced_analysis_reports",
        "__pycache__",
        ".pytest_cache",
    ]
    
    # 需要清理的文件模式
    cleanup_patterns = [
        "*.pyc",
        "*.pyo", 
        "*.pyd",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    cleaned_count = 0
    
    # 清理目錄
    for dir_name in cleanup_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                logger.info(f"✅ 刪除目錄: {dir_name}")
                cleaned_count += 1
            except Exception as e:
                logger.error(f"❌ 刪除失敗 {dir_name}: {e}")
    
    # 遞歸清理文件
    for pattern in cleanup_patterns:
        for file_path in project_root.rglob(pattern):
            try:
                file_path.unlink()
                logger.info(f"✅ 刪除文件: {file_path}")
                cleaned_count += 1
            except Exception as e:
                logger.error(f"❌ 刪除失敗 {file_path}: {e}")
    
    return cleaned_count

def update_gitignore():
    """更新.gitignore文件"""
    logger.info(f"\n📝 更新.gitignore文件")
    logger.info(f"=")
    
    gitignore_path = Path(".gitignore")
    
    # 需要添加的忽略規則
    ignore_rules = [
        "# Python包元數據",
        "*.egg-info/",
        "tradingagents.egg-info/",
        "",
        "# 臨時輸出文件", 
        "enhanced_analysis_reports/",
        "analysis_reports/",
        "",
        "# Python緩存",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        ".pytest_cache/",
        "",
        "# 系統文件",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# IDE文件",
        ".vscode/settings.json",
        ".idea/",
        "",
        "# 日誌文件",
        "*.log",
        "logs/",
    ]
    
    try:
        # 讀取現有內容
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 檢查哪些規則需要添加
        new_rules = []
        for rule in ignore_rules:
            if rule.strip() and rule not in existing_content:
                new_rules.append(rule)
        
        if new_rules:
            # 添加新規則
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write("\n# 自動清理腳本添加的規則\n")
                for rule in new_rules:
                    f.write(f"{rule}\n")
            
            logger.info(f"✅ 添加了 {len(new_rules)} 條新的忽略規則")
        else:
            logger.info(f"✅ .gitignore已經是最新的")
            
    except Exception as e:
        logger.error(f"❌ 更新.gitignore失敗: {e}")

def analyze_upstream_contribution():
    """分析upstream_contribution目錄"""
    logger.debug(f"\n🔍 分析upstream_contribution目錄")
    logger.info(f"=")
    
    upstream_dir = Path("upstream_contribution")
    
    if not upstream_dir.exists():
        logger.info(f"✅ upstream_contribution目錄不存在")
        return
    
    # 統計內容
    batch_dirs = list(upstream_dir.glob("batch*"))
    json_files = list(upstream_dir.glob("*.json"))
    
    logger.info(f"📊 發現內容:")
    logger.info(f"   - Batch目錄: {len(batch_dirs)}個")
    logger.info(f"   - JSON文件: {len(json_files)}個")
    
    for batch_dir in batch_dirs:
        logger.info(f"   - {batch_dir.name}: {len(list(batch_dir.rglob('*')))}個文件")
    
    # 詢問是否刪除
    logger.info(f"\n💡 upstream_contribution目錄用途:")
    logger.info(f"   - 準備向上游項目(TauricResearch/TradingAgents)貢獻代碼")
    logger.info(f"   - 包含移除中文內容的版本")
    logger.info(f"   - 如果不計劃向上游貢獻，可以刪除")
    
    return len(batch_dirs) + len(json_files)

def main():
    """主函數"""
    logger.info(f"🧹 TradingAgents 目錄清理工具")
    logger.info(f"=")
    logger.info(f"💡 目標: 清理自動生成的文件和不必要的目錄")
    logger.info(f"=")
    
    # 清理目錄和文件
    cleaned_count = cleanup_directories()
    
    # 更新gitignore
    update_gitignore()
    
    # 分析upstream_contribution
    upstream_count = analyze_upstream_contribution()
    
    # 總結
    logger.info(f"\n📊 清理總結")
    logger.info(f"=")
    logger.info(f"✅ 清理了 {cleaned_count} 個文件/目錄")
    logger.info(f"📝 更新了 .gitignore 文件")
    
    if upstream_count > 0:
        logger.warning(f"⚠️ upstream_contribution目錄包含 {upstream_count} 個項目")
        logger.info(f"   如果不需要向上游貢獻，可以手動刪除:")
        logger.info(f"   rm -rf upstream_contribution/")
    
    logger.info(f"\n🎉 清理完成！項目目錄更加整潔")
    logger.info(f"\n💡 建議:")
    logger.info(f"   1. 檢查git狀態: git status")
    logger.info(f"   2. 提交清理更改: git add . && git commit -m '清理不必要的目錄和文件'")
    logger.info(f"   3. 如果不需要upstream_contribution，可以手動刪除")

if __name__ == "__main__":
    main()
