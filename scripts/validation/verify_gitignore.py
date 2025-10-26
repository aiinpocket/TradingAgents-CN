#!/usr/bin/env python3
"""
驗證docs/contribution目錄的Git忽略配置
"""

import os
import subprocess
import sys
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


def run_git_command(cmd, cwd=None):
    """運行Git命令"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def main():
    """主函數"""
    logger.info(f"🔧 驗證docs/contribution目錄的Git配置")
    logger.info(f"=")
    
    # 設置項目路徑
    project_path = Path("C:/code/TradingAgentsCN")
    contribution_path = project_path / "docs" / "contribution"
    gitignore_path = project_path / ".gitignore"
    
    # 檢查目錄是否存在
    logger.info(f"📁 檢查目錄狀態...")
    if contribution_path.exists():
        file_count = len(list(contribution_path.rglob("*")))
        logger.info(f"✅ docs/contribution 目錄存在，包含 {file_count} 個項目")
    else:
        logger.error(f"❌ docs/contribution 目錄不存在")
        return False
    
    # 檢查.gitignore配置
    logger.info(f"\n📝 檢查.gitignore配置...")
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        if "docs/contribution/" in gitignore_content:
            logger.info(f"✅ .gitignore 已包含 docs/contribution/")
        else:
            logger.error(f"❌ .gitignore 未包含 docs/contribution/")
            return False
    else:
        logger.error(f"❌ .gitignore 文件不存在")
        return False
    
    # 檢查Git跟蹤狀態
    logger.debug(f"\n🔍 檢查Git跟蹤狀態...")
    
    # 檢查是否有contribution文件被跟蹤
    success, output, error = run_git_command(
        "git ls-files docs/contribution/", 
        cwd=str(project_path)
    )
    
    if success:
        if output:
            tracked_files = output.split('\n')
            logger.warning(f"⚠️ 仍有 {len(tracked_files)} 個文件被Git跟蹤:")
            for file in tracked_files[:5]:  # 只顯示前5個
                logger.info(f"  - {file}")
            if len(tracked_files) > 5:
                logger.info(f"  ... 还有 {len(tracked_files) - 5} 個文件")
            
            logger.info(f"\n🔧 需要從Git跟蹤中移除這些文件:")
            logger.info(f"git rm -r --cached docs/contribution/")
            return False
        else:
            logger.info(f"✅ 没有contribution文件被Git跟蹤")
    else:
        logger.warning(f"⚠️ 無法檢查Git跟蹤狀態: {error}")
    
    # 測試.gitignore是否生效
    logger.info(f"\n🧪 測試.gitignore是否生效...")
    
    test_file = contribution_path / "test_ignore.txt"
    try:
        # 創建測試文件
        with open(test_file, 'w') as f:
            f.write("測試文件")
        
        # 檢查Git是否忽略了這個文件
        success, output, error = run_git_command(
            f"git check-ignore {test_file.relative_to(project_path)}", 
            cwd=str(project_path)
        )
        
        if success:
            logger.info(f"✅ .gitignore 正常工作，測試文件被忽略")
        else:
            logger.error(f"❌ .gitignore 可能未生效")
            return False
        
        # 刪除測試文件
        test_file.unlink()
        
    except Exception as e:
        logger.error(f"⚠️ 測試失败: {e}")
    
    # 檢查當前Git狀態
    logger.info(f"\n📊 檢查當前Git狀態...")
    
    success, output, error = run_git_command(
        "git status --porcelain", 
        cwd=str(project_path)
    )
    
    if success:
        if output:
            # 檢查是否有contribution相關的更改
            contribution_changes = [
                line for line in output.split('\n') 
                if 'contribution' in line
            ]
            
            if contribution_changes:
                logger.warning(f"⚠️ 發現contribution相關的更改:")
                for change in contribution_changes:
                    logger.info(f"  {change}")
                logger.info(f"\n建议操作:")
                logger.info(f"1. git add .gitignore")
                logger.info(f"2. git commit -m 'chore: exclude docs/contribution from version control'")
            else:
                logger.info(f"✅ 没有contribution相關的未提交更改")
        else:
            logger.info(f"✅ 工作目錄干净")
    else:
        logger.warning(f"⚠️ 無法檢查Git狀態: {error}")
    
    logger.info(f"\n🎯 总結:")
    logger.info(f"✅ docs/contribution 目錄已成功配置為不被Git管理")
    logger.info(f"📁 本地文件保留，但不會被版本控制")
    logger.info(f"🔒 新增的contribution文件将自動被忽略")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info(f"\n🎉 配置驗證成功！")
    else:
        logger.error(f"\n❌ 配置需要調整")
    
    sys.exit(0 if success else 1)
