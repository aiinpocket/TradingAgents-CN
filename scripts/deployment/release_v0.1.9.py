#!/usr/bin/env python3
"""
TradingAgents-CN v0.1.9 版本發布腳本
CLI用戶體驗重大優化与統一日誌管理版本
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def run_command(command, cwd=None):
    """執行命令並返回結果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd or project_root,
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_version_consistency():
    """檢查版本號一致性"""
    print("🔍 檢查版本號一致性...")
    
    # 檢查VERSION文件
    version_file = os.path.join(project_root, "VERSION")
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            version_content = f.read().strip()
        print(f"   VERSION文件: {version_content}")
    else:
        print("   ❌ VERSION文件不存在")
        return False
    
    # 檢查pyproject.toml
    pyproject_file = os.path.join(project_root, "pyproject.toml")
    if os.path.exists(pyproject_file):
        with open(pyproject_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('version ='):
                    pyproject_version = line.split('=')[1].strip().strip('"')
                    print(f"   pyproject.toml: {pyproject_version}")
                    break
    
    # 檢查README.md
    readme_file = os.path.join(project_root, "README.md")
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "cn--0.1.9" in content:
                print("   README.md: cn-0.1.9 ✅")
            else:
                print("   README.md: 版本號未更新 ❌")
                return False
    
    return True

def create_git_tag():
    """創建Git標簽"""
    print("🏷️ 創建Git標簽...")
    
    tag_name = "v0.1.9"
    tag_message = "TradingAgents-CN v0.1.9: CLI用戶體驗重大優化与統一日誌管理"
    
    # 檢查標簽是否已存在
    success, stdout, stderr = run_command(f"git tag -l {tag_name}")
    if tag_name in stdout:
        print(f"   標簽 {tag_name} 已存在")
        return True
    
    # 創建標簽
    success, stdout, stderr = run_command(f'git tag -a {tag_name} -m "{tag_message}"')
    if success:
        print(f"   ✅ 標簽 {tag_name} 創建成功")
        return True
    else:
        print(f"   ❌ 標簽創建失败: {stderr}")
        return False

def generate_release_summary():
    """生成發布摘要"""
    print("📋 生成發布摘要...")
    
    summary = {
        "version": "cn-0.1.9",
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "title": "CLI用戶體驗重大優化与統一日誌管理",
        "highlights": [
            "🎨 CLI界面重構 - 界面与日誌分離，提供清爽用戶體驗",
            "🔄 進度顯示優化 - 解決重複提示，添加多階段進度跟蹤", 
            "⏱️ 時間預估功能 - 智能分析階段添加10分鐘時間預估",
            "📝 統一日誌管理 - 配置化日誌系統，支持多環境",
            "🇭🇰 港股數據優化 - 改進數據獲取穩定性和容錯機制",
            "🔑 OpenAI配置修複 - 解決配置混乱和錯誤處理問題"
        ],
        "key_features": {
            "cli_optimization": {
                "interface_separation": "用戶界面与系統日誌完全分離",
                "progress_display": "智能進度顯示，防止重複提示",
                "time_estimation": "分析階段時間預估，管理用戶期望",
                "visual_enhancement": "Rich彩色輸出，專業視觉效果"
            },
            "logging_system": {
                "unified_management": "LoggingManager統一日誌管理",
                "configurable": "TOML配置文件，灵活控制日誌級別",
                "tool_logging": "詳細記錄工具調用過程和結果",
                "multi_environment": "本地和Docker環境差異化配置"
            },
            "data_source_improvements": {
                "hk_stocks": "港股數據獲取優化和容錯機制",
                "openai_config": "OpenAI配置統一和錯誤處理",
                "caching_strategy": "智能緩存和多級fallback"
            }
        },
        "user_experience": {
            "before": "技術日誌干扰、重複提示、等待焦慮",
            "after": "清爽界面、智能進度、時間預估、專業體驗"
        },
        "technical_improvements": [
            "代碼质量提升 - 統一導入方式，增强錯誤處理",
            "測試覆蓋增加 - CLI和日誌系統測試套件",
            "文档完善 - 設計文档和配置管理指南",
            "架構優化 - 模塊化設計，提升可維護性"
        ],
        "files_changed": {
            "core_files": [
                "cli/main.py - CLI界面重構和進度顯示優化",
                "tradingagents/utils/logging_manager.py - 統一日誌管理器",
                "tradingagents/utils/tool_logging.py - 工具調用日誌記錄",
                "config/logging.toml - 日誌配置文件"
            ],
            "documentation": [
                "docs/releases/v0.1.9.md - 詳細發布說明",
                "docs/releases/CHANGELOG.md - 更新日誌",
                "README.md - 版本信息更新"
            ],
            "tests": [
                "test_cli_logging_fix.py - CLI日誌修複測試",
                "test_cli_progress_display.py - 進度顯示測試",
                "test_duplicate_progress_fix.py - 重複提示修複測試",
                "test_detailed_progress_display.py - 詳細進度顯示測試"
            ]
        }
    }
    
    # 保存發布摘要
    summary_file = os.path.join(project_root, "docs", "releases", "v0.1.9_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 發布摘要已保存到: {summary_file}")
    return True

def validate_release():
    """驗證發布準备"""
    print("✅ 驗證發布準备...")
    
    checks = []
    
    # 檢查關键文件是否存在
    key_files = [
        "VERSION",
        "README.md", 
        "docs/releases/v0.1.9.md",
        "docs/releases/CHANGELOG.md",
        "cli/main.py",
        "tradingagents/utils/logging_manager.py"
    ]
    
    for file_path in key_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            checks.append(f"   ✅ {file_path}")
        else:
            checks.append(f"   ❌ {file_path} 缺失")
    
    # 檢查Git狀態
    success, stdout, stderr = run_command("git status --porcelain")
    if success:
        if stdout.strip():
            checks.append("   ⚠️ 有未提交的更改")
        else:
            checks.append("   ✅ Git工作区干净")
    
    for check in checks:
        print(check)
    
    return all("✅" in check for check in checks)

def main():
    """主函數"""
    print("🚀 TradingAgents-CN v0.1.9 版本發布")
    print("=" * 60)
    print("📋 版本主題: CLI用戶體驗重大優化与統一日誌管理")
    print("📅 發布日期:", datetime.now().strftime("%Y年%m月%d日"))
    print("=" * 60)
    
    steps = [
        ("檢查版本號一致性", check_version_consistency),
        ("驗證發布準备", validate_release),
        ("生成發布摘要", generate_release_summary),
        ("創建Git標簽", create_git_tag)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if not step_func():
            print(f"❌ {step_name}失败，發布中止")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 v0.1.9 版本發布準备完成！")
    print("=" * 60)
    
    print("\n📋 發布亮點:")
    highlights = [
        "🎨 CLI界面重構 - 專業、清爽、用戶友好",
        "🔄 進度顯示優化 - 智能跟蹤，消除重複",
        "⏱️ 時間預估功能 - 管理期望，减少焦慮",
        "📝 統一日誌管理 - 配置化，多環境支持",
        "🇭🇰 港股數據優化 - 穩定性和容錯性提升",
        "🔑 配置問題修複 - OpenAI配置統一管理"
    ]
    
    for highlight in highlights:
        print(f"   {highlight}")
    
    print("\n🎯 用戶體驗提升:")
    print("   - 界面清爽美觀，没有技術信息干扰")
    print("   - 實時進度反馈，消除等待焦慮") 
    print("   - 專業分析流程展示，增强系統信任")
    print("   - 時間預估管理，提升等待體驗")
    
    print("\n📚 相關文档:")
    print("   - 詳細發布說明: docs/releases/v0.1.9.md")
    print("   - 完整更新日誌: docs/releases/CHANGELOG.md")
    print("   - 發布摘要: docs/releases/v0.1.9_summary.json")
    
    print("\n🔄 下一步操作:")
    print("   1. git push origin main")
    print("   2. git push origin v0.1.9")
    print("   3. 在GitHub創建Release")
    print("   4. 更新Docker鏡像")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
