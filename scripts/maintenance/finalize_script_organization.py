#!/usr/bin/env python3
"""
完成腳本文件的最终整理
将剩余的腳本文件移動到合適的分類目錄
"""

import os
import shutil
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def finalize_script_organization():
    """完成腳本文件的最终整理"""
    
    # 項目根目錄
    project_root = Path(__file__).parent.parent.parent
    scripts_dir = project_root / "scripts"
    
    logger.info(f"📁 完成TradingAgentsCN腳本文件的最终整理")
    logger.info(f"=")
    logger.info(f"📍 項目根目錄: {project_root}")
    
    # 定義剩余文件的移動規則
    remaining_moves = {
        # 設置和數據庫腳本 -> scripts/setup/
        "setup_databases.py": "setup/setup_databases.py",
        "init_database.py": "setup/init_database.py",
        "migrate_env_to_config.py": "setup/migrate_env_to_config.py",
        
        # 開發和贡献腳本 -> scripts/development/
        "prepare_upstream_contribution.py": "development/prepare_upstream_contribution.py",
        "download_finnhub_sample_data.py": "development/download_finnhub_sample_data.py",
        "fix_streamlit_watcher.py": "development/fix_streamlit_watcher.py",
        
        # 發布和版本管理 -> scripts/deployment/
        "create_github_release.py": "deployment/create_github_release.py",
        "release_v0.1.2.py": "deployment/release_v0.1.2.py",
        "release_v0.1.3.py": "deployment/release_v0.1.3.py",
        
        # 維護和管理腳本 -> scripts/maintenance/
        "branch_manager.py": "maintenance/branch_manager.py",
        "sync_upstream.py": "maintenance/sync_upstream.py",
        "version_manager.py": "maintenance/version_manager.py",
        
        # Docker腳本 -> scripts/docker/
        "docker-compose-start.bat": "docker/docker-compose-start.bat",
        "start_docker_services.bat": "docker/start_docker_services.bat",
        "start_docker_services.sh": "docker/start_docker_services.sh",
        "stop_docker_services.bat": "docker/stop_docker_services.bat",
        "stop_docker_services.sh": "docker/stop_docker_services.sh",
        "start_services_alt_ports.bat": "docker/start_services_alt_ports.bat",
        "start_services_simple.bat": "docker/start_services_simple.bat",
        "mongo-init.js": "docker/mongo-init.js",
        
        # Git工具 -> scripts/git/
        "upstream_git_workflow.sh": "git/upstream_git_workflow.sh",
        "setup_fork_environment.sh": "git/setup_fork_environment.sh",
    }
    
    # 創建必要的目錄
    directories_to_create = [
        "deployment",
        "docker", 
        "git"
    ]
    
    logger.info(f"\n📁 創建必要的目錄...")
    for dir_name in directories_to_create:
        dir_path = scripts_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ 確保目錄存在: scripts/{dir_name}")
    
    # 移動文件
    logger.info(f"\n📦 移動剩余腳本文件...")
    moved_count = 0
    
    for source_file, target_path in remaining_moves.items():
        source_path = scripts_dir / source_file
        target_full_path = scripts_dir / target_path
        
        if source_path.exists():
            try:
                # 確保目標目錄存在
                target_full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 移動文件
                shutil.move(str(source_path), str(target_full_path))
                logger.info(f"✅ 移動: {source_file} -> scripts/{target_path}")
                moved_count += 1
                
            except Exception as e:
                logger.error(f"❌ 移動失败 {source_file}: {e}")
        else:
            logger.info(f"ℹ️ 文件不存在: {source_file}")
    
    # 創建各目錄的README文件
    logger.info(f"\n📝 創建README文件...")
    
    readme_contents = {
        "deployment": {
            "title": "Deployment Scripts",
            "description": "部署和發布相關腳本",
            "scripts": [
                "create_github_release.py - 創建GitHub發布",
                "release_v0.1.2.py - 發布v0.1.2版本",
                "release_v0.1.3.py - 發布v0.1.3版本"
            ]
        },
        "docker": {
            "title": "Docker Scripts", 
            "description": "Docker容器管理腳本",
            "scripts": [
                "docker-compose-start.bat - 啟動Docker Compose",
                "start_docker_services.* - 啟動Docker服務",
                "stop_docker_services.* - 停止Docker服務",
                "mongo-init.js - MongoDB初始化腳本"
            ]
        },
        "git": {
            "title": "Git Tools",
            "description": "Git工具和工作流腳本", 
            "scripts": [
                "upstream_git_workflow.sh - 上游Git工作流",
                "setup_fork_environment.sh - 設置Fork環境"
            ]
        }
    }
    
    for dir_name, info in readme_contents.items():
        readme_path = scripts_dir / dir_name / "README.md"
        
        content = f"""# {info['title']}

## 目錄說明

{info['description']}

## 腳本列表

"""
        for script in info['scripts']:
            content += f"- `{script}`\n"
        
        content += f"""
## 使用方法

```bash
# 進入項目根目錄
cd C:\\code\\TradingAgentsCN

# 運行腳本
python scripts/{dir_name}/script_name.py
```

## 註意事項

- 確保在項目根目錄下運行腳本
- 檢查腳本的依賴要求
- 某些腳本可能需要特殊權限
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"✅ 創建README: scripts/{dir_name}/README.md")
    
    # 更新主README
    logger.info(f"\n📝 更新主README...")
    main_readme_path = scripts_dir / "README.md"
    
    main_content = """# Scripts Directory

這個目錄包含TradingAgentsCN項目的各種腳本工具，按功能分類組織。

## 目錄結構

### 📦 setup/ - 安裝和配置腳本
- 環境設置
- 依賴安裝  
- API配置
- 數據庫設置

### 🔍 validation/ - 驗證腳本
- Git配置驗證
- 依賴檢查
- 配置驗證
- API連接測試

### 🔧 maintenance/ - 維護腳本
- 緩存清理
- 數據备份
- 依賴更新
- 上游同步
- 分支管理

### 🛠️ development/ - 開發辅助腳本
- 代碼分析
- 性能基準測試
- 文档生成
- 贡献準备
- 數據下載

### 🚀 deployment/ - 部署腳本
- GitHub發布
- 版本發布
- 打包部署

### 🐳 docker/ - Docker腳本
- Docker服務管理
- 容器啟動停止
- 數據庫初始化

### 📋 git/ - Git工具腳本
- 上游同步
- Fork環境設置
- 贡献工作流

## 使用原則

### 腳本分類
- **tests/** - 單元測試和集成測試（pytest運行）
- **scripts/** - 工具腳本和驗證腳本（獨立運行）
- **utils/** - 實用工具腳本

### 運行方式
```bash
# 從項目根目錄運行
cd C:\\code\\TradingAgentsCN

# Python腳本
python scripts/validation/verify_gitignore.py

# PowerShell腳本  
powershell -ExecutionPolicy Bypass -File scripts/maintenance/cleanup.ps1

# Bash腳本
bash scripts/git/upstream_git_workflow.sh
```

## 目錄說明

| 目錄 | 用途 | 示例腳本 |
|------|------|----------|
| `setup/` | 環境配置和初始化 | setup_databases.py |
| `validation/` | 驗證和檢查 | verify_gitignore.py |
| `maintenance/` | 維護和管理 | sync_upstream.py |
| `development/` | 開發辅助 | prepare_upstream_contribution.py |
| `deployment/` | 部署發布 | create_github_release.py |
| `docker/` | 容器管理 | start_docker_services.bat |
| `git/` | Git工具 | upstream_git_workflow.sh |

## 註意事項

- 所有腳本應该從項目根目錄運行
- 檢查腳本的依賴要求
- 某些腳本可能需要特殊權限
- 保持腳本的獨立性和可重用性

## 開發指南

### 添加新腳本
1. 確定腳本類型和目標目錄
2. 創建腳本文件
3. 添加適當的文档註釋
4. 更新相應目錄的README
5. 測試腳本功能

### 腳本模板
每個腳本應包含：
- 文件头註釋說明用途
- 使用方法說明
- 依賴要求
- 錯誤處理
- 日誌輸出
"""
    
    with open(main_readme_path, 'w', encoding='utf-8') as f:
        f.write(main_content)
    logger.info(f"✅ 更新主README: scripts/README.md")
    
    # 檢查最终狀態
    logger.info(f"\n📊 檢查最终狀態...")
    
    # 統計各目錄的腳本數量
    subdirs = ["setup", "validation", "maintenance", "development", "deployment", "docker", "git"]
    total_scripts = 0
    
    for subdir in subdirs:
        subdir_path = scripts_dir / subdir
        if subdir_path.exists():
            script_files = [f for f in subdir_path.iterdir() 
                          if f.is_file() and f.suffix in ['.py', '.ps1', '.sh', '.bat', '.js']]
            script_count = len(script_files)
            total_scripts += script_count
            logger.info(f"📁 scripts/{subdir}: {script_count} 個腳本")
    
    # 檢查根級別剩余腳本
    root_scripts = [f for f in scripts_dir.iterdir() 
                   if f.is_file() and f.suffix in ['.py', '.ps1', '.sh', '.bat', '.js']]
    
    if root_scripts:
        logger.warning(f"\n⚠️ scripts根目錄仍有 {len(root_scripts)} 個腳本:")
        for script in root_scripts:
            logger.info(f"  - {script.name}")
    else:
        logger.info(f"\n✅ scripts根目錄已清理完成")
    
    logger.info(f"\n📊 整理結果:")
    logger.info(f"✅ 总共整理: {total_scripts} 個腳本")
    logger.info(f"✅ 分類目錄: {len(subdirs)} 個")
    logger.info(f"✅ 本次移動: {moved_count} 個文件")
    
    return moved_count > 0

def main():
    """主函數"""
    try:
        success = finalize_script_organization()
        
        if success:
            logger.info(f"\n🎉 腳本整理完成!")
            logger.info(f"\n💡 建议:")
            logger.info(f"1. 檢查移動後的腳本是否正常工作")
            logger.info(f"2. 更新相關文档中的路徑引用")
            logger.info(f"3. 提交這些目錄結構變更")
            logger.info(f"4. 驗證各分類目錄的腳本功能")
        else:
            logger.info(f"\n✅ 腳本已經整理完成，無需移動")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 整理失败: {e}")
        import traceback

        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
