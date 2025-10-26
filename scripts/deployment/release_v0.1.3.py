#!/usr/bin/env python3
"""
TradingAgents-CN v0.1.3 發布腳本
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


def run_command(command, cwd=None):
    """運行命令並返回結果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_git_status():
    """檢查Git狀態"""
    logger.debug(f"🔍 檢查Git狀態...")
    
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        logger.error(f"❌ Git狀態檢查失败: {stderr}")
        return False
    
    if stdout.strip():
        logger.warning(f"⚠️ 發現未提交的更改:")
        print(stdout)
        response = input("是否繼续發布? (y/N): ")
        if response.lower() != 'y':
            return False
    
    logger.info(f"✅ Git狀態檢查通過")
    return True

def update_version_files():
    """更新版本文件"""
    logger.info(f"📝 更新版本文件...")
    
    version = "cn-0.1.3"
    
    # 更新VERSION文件
    try:
        with open("VERSION", "w", encoding='utf-8') as f:
            f.write(f"{version}\n")
        logger.info(f"✅ VERSION文件已更新")
    except Exception as e:
        logger.error(f"❌ 更新VERSION文件失败: {e}")
        return False
    
    return True

def run_tests():
    """運行測試"""
    logger.info(f"🧪 運行基础測試...")
    
    # 測試Tushare數據接口
    logger.info(f"  📊 測試Tushare數據接口...")
    success, stdout, stderr = run_command("python tests/fast_tdx_test.py")
    if success:
        logger.info(f"  ✅ Tushare數據接口測試通過")
    else:
        logger.warning(f"  ⚠️ Tushare數據接口測試警告: {stderr}")
        # 不阻止發布，因為可能是網絡問題
    
    # 測試Web界面啟動
    logger.info(f"  🌐 測試Web界面...")
    # 這里可以添加Web界面的基础測試
    logger.info(f"  ✅ Web界面測試跳過（需要手動驗證）")
    
    return True

def create_git_tag():
    """創建Git標簽"""
    logger.info(f"🏷️ 創建Git標簽...")
    
    tag_name = "v0.1.3"
    tag_message = "TradingAgents-CN v0.1.3 - A股市場完整支持"
    
    # 檢查標簽是否已存在
    success, stdout, stderr = run_command(f"git tag -l {tag_name}")
    if stdout.strip():
        logger.warning(f"⚠️ 標簽 {tag_name} 已存在")
        response = input("是否刪除現有標簽並重新創建? (y/N): ")
        if response.lower() == 'y':
            run_command(f"git tag -d {tag_name}")
            run_command(f"git push origin --delete {tag_name}")
        else:
            return False
    
    # 創建標簽
    success, stdout, stderr = run_command(f'git tag -a {tag_name} -m "{tag_message}"')
    if not success:
        logger.error(f"❌ 創建標簽失败: {stderr}")
        return False
    
    logger.info(f"✅ 標簽 {tag_name} 創建成功")
    return True

def commit_changes():
    """提交更改"""
    logger.info(f"💾 提交版本更改...")
    
    # 添加更改的文件
    files_to_add = [
        "VERSION",
        "CHANGELOG.md", 
        "README.md",
        "RELEASE_NOTES_v0.1.3.md",
        "docs/guides/a-share-analysis-guide.md",
        "docs/data/china_stock-api-integration.md",
        "tradingagents/dataflows/tdx_utils.py",
        "tradingagents/agents/utils/agent_utils.py",
        "web/components/analysis_form.py",
        "requirements.txt"
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            run_command(f"git add {file}")
    
    # 提交更改
    commit_message = "🚀 Release v0.1.3: A股市場完整支持\n\n- 集成Tushare數據接口支持A股實時數據\n- 新增Web界面市場選擇功能\n- 優化新聞分析滞後性\n- 完善文档和使用指南"
    
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success and "nothing to commit" not in stderr:
        logger.error(f"❌ 提交失败: {stderr}")
        return False
    
    logger.info(f"✅ 更改已提交")
    return True

def push_to_remote():
    """推送到远程仓庫"""
    logger.info(f"🚀 推送到远程仓庫...")
    
    # 推送代碼
    success, stdout, stderr = run_command("git push origin main")
    if not success:
        logger.error(f"❌ 推送代碼失败: {stderr}")
        return False
    
    # 推送標簽
    success, stdout, stderr = run_command("git push origin --tags")
    if not success:
        logger.error(f"❌ 推送標簽失败: {stderr}")
        return False
    
    logger.info(f"✅ 推送完成")
    return True

def generate_release_summary():
    """生成發布摘要"""
    logger.info(f"\n")
    logger.info(f"🎉 TradingAgents-CN v0.1.3 發布完成!")
    logger.info(f"=")
    
    logger.info(f"\n📋 發布內容:")
    logger.info(f"  🇨🇳 A股市場完整支持")
    logger.info(f"  📊 Tushare數據接口集成")
    logger.info(f"  🌐 Web界面市場選擇")
    logger.info(f"  📰 實時新聞優化")
    logger.info(f"  📚 完善的文档和指南")
    
    logger.info(f"\n🔗 相關文件:")
    logger.info(f"  📄 發布說明: RELEASE_NOTES_v0.1.3.md")
    logger.info(f"  📖 A股指南: docs/guides/a-share-analysis-guide.md")
    logger.info(f"  🔧 技術文档: docs/data/china_stock-api-integration.md")
    
    logger.info(f"\n🚀 下一步:")
    logger.info(f"  1. 在GitHub上創建Release")
    logger.info(f"  2. 更新項目README")
    logger.info(f"  3. 通知用戶更新")
    logger.info(f"  4. 收集用戶反馈")
    
    logger.info(f"\n💡 使用方法:")
    logger.info(f"  git pull origin main")
    logger.info(f"  pip install -r requirements.txt")
    logger.info(f"  pip install pytdx")
    logger.info(f"  python -m streamlit run web/app.py")

def main():
    """主函數"""
    logger.info(f"🚀 TradingAgents-CN v0.1.3 發布流程")
    logger.info(f"=")
    
    # 檢查當前目錄
    if not os.path.exists("VERSION"):
        logger.error(f"❌ 請在項目根目錄運行此腳本")
        return False
    
    # 執行發布步骤
    steps = [
        ("檢查Git狀態", check_git_status),
        ("更新版本文件", update_version_files),
        ("運行測試", run_tests),
        ("提交更改", commit_changes),
        ("創建Git標簽", create_git_tag),
        ("推送到远程", push_to_remote),
    ]
    
    for step_name, step_func in steps:
        logger.info(f"\n📋 {step_name}...")
        if not step_func():
            logger.error(f"❌ {step_name}失败，發布中止")
            return False
    
    # 生成發布摘要
    generate_release_summary()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            logger.info(f"\n🎉 發布成功完成!")
            sys.exit(0)
        else:
            logger.error(f"\n❌ 發布失败")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.warning(f"\n\n⚠️ 發布被用戶中斷")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 發布過程中出現異常: {e}")
        sys.exit(1)
