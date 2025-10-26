#!/usr/bin/env python3
"""
整理根目錄下的腳本文件
将測試和驗證腳本移動到對應的目錄中
"""

import os
import shutil
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def organize_root_scripts():
    """整理根目錄下的腳本文件"""
    
    # 項目根目錄
    project_root = Path(__file__).parent.parent.parent
    
    logger.info(f"📁 整理TradingAgentsCN根目錄下的腳本文件")
    logger.info(f"=")
    logger.info(f"📍 項目根目錄: {project_root}")
    
    # 定義文件移動規則
    file_moves = {
        # 驗證腳本 -> scripts/validation/
        "check_dependencies.py": "scripts/validation/check_dependencies.py",
        "verify_gitignore.py": "scripts/validation/verify_gitignore.py",
        "smart_config.py": "scripts/validation/smart_config.py",
        
        # 測試腳本 -> tests/
        "quick_test.py": "tests/quick_test.py",
        "test_smart_system.py": "tests/test_smart_system.py",
        "demo_fallback_system.py": "tests/demo_fallback_system.py",
        
        # 開發腳本 -> scripts/development/
        "adaptive_cache_manager.py": "scripts/development/adaptive_cache_manager.py",
        "organize_scripts.py": "scripts/development/organize_scripts.py",
        
        # 設置腳本 -> scripts/setup/
        "setup_fork_environment.ps1": "scripts/setup/setup_fork_environment.ps1",
        
        # 維護腳本 -> scripts/maintenance/
        "remove_contribution_from_git.ps1": "scripts/maintenance/remove_contribution_from_git.ps1",
        "analyze_differences.ps1": "scripts/maintenance/analyze_differences.ps1",
        "debug_integration.ps1": "scripts/maintenance/debug_integration.ps1",
        "integrate_cache_improvements.ps1": "scripts/maintenance/integrate_cache_improvements.ps1",
        "migrate_first_contribution.ps1": "scripts/maintenance/migrate_first_contribution.ps1",
        "create_scripts_structure.ps1": "scripts/maintenance/create_scripts_structure.ps1",
    }
    
    # 創建必要的目錄
    directories_to_create = [
        "scripts/validation",
        "scripts/setup", 
        "scripts/maintenance",
        "scripts/development",
        "tests/integration",
        "tests/validation"
    ]
    
    logger.info(f"\n📁 創建必要的目錄...")
    for dir_path in directories_to_create:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ 確保目錄存在: {dir_path}")
    
    # 移動文件
    logger.info(f"\n📦 移動腳本文件...")
    moved_count = 0
    skipped_count = 0
    
    for source_file, target_path in file_moves.items():
        source_path = project_root / source_file
        target_full_path = project_root / target_path
        
        if source_path.exists():
            try:
                # 確保目標目錄存在
                target_full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 移動文件
                shutil.move(str(source_path), str(target_full_path))
                logger.info(f"✅ 移動: {source_file} -> {target_path}")
                moved_count += 1
                
            except Exception as e:
                logger.error(f"❌ 移動失败 {source_file}: {e}")
        else:
            logger.info(f"ℹ️ 文件不存在: {source_file}")
            skipped_count += 1
    
    # 檢查剩余的腳本文件
    logger.debug(f"\n🔍 檢查剩余的腳本文件...")
    remaining_scripts = []
    
    script_extensions = ['.py', '.ps1', '.sh', '.bat']
    for item in project_root.iterdir():
        if item.is_file() and item.suffix in script_extensions:
            # 排除主要的項目文件
            if item.name not in ['main.py', 'setup.py', 'start_web.bat', 'start_web.ps1']:
                remaining_scripts.append(item.name)
    
    if remaining_scripts:
        logger.warning(f"⚠️ 根目錄下仍有腳本文件:")
        for script in remaining_scripts:
            logger.info(f"  - {script}")
        logger.info(f"\n💡 建议手動檢查這些文件是否需要移動")
    else:
        logger.info(f"✅ 根目錄下没有剩余的腳本文件")
    
    # 創建README文件
    logger.info(f"\n📝 更新README文件...")
    
    # 更新scripts/validation/README.md
    validation_readme = project_root / "scripts/validation/README.md"
    validation_content = """# Validation Scripts

## 目錄說明

這個目錄包含各種驗證腳本，用於檢查項目配置、依賴、Git設置等。

## 腳本列表

- `verify_gitignore.py` - 驗證Git忽略配置，確保docs/contribution目錄不被版本控制
- `check_dependencies.py` - 檢查項目依賴是否正確安裝
- `smart_config.py` - 智能配置檢測和管理

## 使用方法

```bash
# 進入項目根目錄
cd C:\\code\\TradingAgentsCN

# 運行驗證腳本
python scripts/validation/verify_gitignore.py
python scripts/validation/check_dependencies.py
python scripts/validation/smart_config.py
```

## 驗證腳本 vs 測試腳本的区別

### 驗證腳本 (scripts/validation/)
- **目的**: 檢查項目配置、環境設置、依賴狀態
- **運行時機**: 開發環境設置、部署前檢查、問題排查
- **特點**: 獨立運行，提供詳細的檢查報告和修複建议

### 測試腳本 (tests/)
- **目的**: 驗證代碼功能正確性
- **運行時機**: 開發過程中、CI/CD流程
- **特點**: 使用pytest框架，專註於代碼逻辑測試

## 註意事項

- 確保在項目根目錄下運行腳本
- 驗證腳本會檢查系統狀態並提供修複建议
- 某些驗證可能需要網絡連接或特定權限
- 驗證失败時會提供詳細的錯誤信息和解決方案
"""
    
    with open(validation_readme, 'w', encoding='utf-8') as f:
        f.write(validation_content)
    logger.info(f"✅ 更新: scripts/validation/README.md")
    
    # 更新tests/README.md
    tests_readme = project_root / "tests/README.md"
    if tests_readme.exists():
        with open(tests_readme, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # 添加新移動的測試文件說明
        additional_content = """

## 新增的測試文件

### 集成測試
- `quick_test.py` - 快速集成測試，驗證基本功能
- `test_smart_system.py` - 智能系統完整測試
- `demo_fallback_system.py` - 降級系統演示和測試

### 運行方法
```bash
# 快速測試
python tests/quick_test.py

# 智能系統測試
python tests/test_smart_system.py

# 降級系統演示
python tests/demo_fallback_system.py
```
"""
        
        if "新增的測試文件" not in existing_content:
            with open(tests_readme, 'a', encoding='utf-8') as f:
                f.write(additional_content)
            logger.info(f"✅ 更新: tests/README.md")
    
    # 統計結果
    logger.info(f"\n📊 整理結果統計:")
    logger.info(f"✅ 成功移動: {moved_count} 個文件")
    logger.info(f"ℹ️ 跳過文件: {skipped_count} 個文件")
    logger.warning(f"⚠️ 剩余腳本: {len(remaining_scripts)} 個文件")
    
    logger.info(f"\n🎯 目錄結構優化完成!")
    logger.info(f"📁 驗證腳本: scripts/validation/")
    logger.info(f"🧪 測試腳本: tests/")
    logger.info(f"🔧 工具腳本: scripts/對應分類/")
    
    return moved_count > 0

def main():
    """主函數"""
    try:
        success = organize_root_scripts()
        
        if success:
            logger.info(f"\n🎉 腳本整理完成!")
            logger.info(f"\n💡 建议:")
            logger.info(f"1. 檢查移動後的腳本是否正常工作")
            logger.info(f"2. 更新相關文档中的路徑引用")
            logger.info(f"3. 提交這些目錄結構變更")
        else:
            logger.warning(f"\n⚠️ 没有文件被移動")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 整理失败: {e}")
        import traceback

        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
