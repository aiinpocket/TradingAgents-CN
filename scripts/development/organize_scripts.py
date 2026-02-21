#!/usr/bin/env python3
"""
整理TradingAgentsCN項目的scripts目錄結構
將現有指令碼按功能分類到子目錄中
"""

import os
import shutil
from pathlib import Path

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


def create_scripts_structure():
    """建立scripts子目錄結構"""
    
    project_path = Path("C:/code/TradingAgentsCN")
    scripts_path = project_path / "scripts"
    
    logger.info(f" 整理TradingAgentsCN項目的scripts目錄")
    logger.info(f"=")
    
    # 定義目錄結構和指令碼分類
    script_categories = {
        "setup": {
            "description": "安裝和配置指令碼",
            "scripts": [
                "setup_databases.py",
                "init_database.py", 
                "setup_fork_environment.sh",
                "migrate_env_to_config.py"
            ]
        },
        "validation": {
            "description": "驗證和檢查指令碼", 
            "scripts": [
                # 這裡會放置驗證指令碼
            ]
        },
        "maintenance": {
            "description": "維護和管理指令碼",
            "scripts": [
                "sync_upstream.py",
                "branch_manager.py",
                "version_manager.py"
            ]
        },
        "development": {
            "description": "開發輔助指令碼",
            "scripts": [
                "prepare_upstream_contribution.py",
                "download_finnhub_sample_data.py",
                "fix_streamlit_watcher.py"
            ]
        },
        "deployment": {
            "description": "部署和發布指令碼",
            "scripts": [
                "create_github_release.py",
                "release_v0.1.2.py", 
                "release_v0.1.3.py"
            ]
        },
        "docker": {
            "description": "Docker相關指令碼",
            "scripts": [
                "docker-compose-start.bat",
                "start_docker_services.bat",
                "start_docker_services.sh", 
                "stop_docker_services.bat",
                "stop_docker_services.sh",
                "start_services_alt_ports.bat",
                "start_services_simple.bat",
                "mongo-init.js"
            ]
        },
        "git": {
            "description": "Git相關指令碼",
            "scripts": [
                "upstream_git_workflow.sh"
            ]
        }
    }
    
    # 建立子目錄
    logger.info(f" 建立子目錄...")
    for category, info in script_categories.items():
        category_path = scripts_path / category
        category_path.mkdir(exist_ok=True)
        logger.info(f" 建立目錄: scripts/{category} - {info['description']}")
        
        # 建立README檔案
        readme_path = category_path / "README.md"
        readme_content = f"""# {category.title()} Scripts

## 目錄說明

{info['description']}

## 指令碼列表

"""
        for script in info['scripts']:
            readme_content += f"- `{script}` - 指令碼功能說明\n"
        
        readme_content += f"""
## 使用方法

```bash
# 進入項目根目錄
cd C:\\code\\TradingAgentsCN

# 執行指令碼
python scripts/{category}/script_name.py
```

## 註意事項

- 確保在項目根目錄下執行指令碼
- 檢查指令碼的依賴要求
- 某些指令碼可能需要管理員權限
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        logger.info(f" 建立README: scripts/{category}/README.md")
    
    # 移動現有指令碼到對應目錄
    logger.info(f"\n 移動現有指令碼...")
    
    for category, info in script_categories.items():
        category_path = scripts_path / category
        
        for script_name in info['scripts']:
            source_path = scripts_path / script_name
            target_path = category_path / script_name
            
            if source_path.exists():
                try:
                    shutil.move(str(source_path), str(target_path))
                    logger.info(f" 移動: {script_name} -> scripts/{category}/")
                except Exception as e:
                    logger.error(f" 移動失敗 {script_name}: {e}")
            else:
                logger.info(f"[INFO]指令碼不存在: {script_name}")
    
    # 建立主README
    logger.info(f"\n 建立主README...")
    main_readme_path = scripts_path / "README.md"
    main_readme_content = """# Scripts Directory

這個目錄包含TradingAgentsCN項目的各種指令碼工具。

## 目錄結構

###  setup/ - 安裝和配置指令碼
- 環境設定
- 依賴安裝  
- API配置
- 資料庫設定

###  validation/ - 驗證指令碼
- Git配置驗證
- 依賴檢查
- 配置驗證
- API連接測試

###  maintenance/ - 維護指令碼
- 快取清理
- 資料備份
- 依賴更新
- 上游同步

###  development/ - 開發輔助指令碼
- 代碼分析
- 性能基準測試
- 檔案生成
- 貢獻準備

###  deployment/ - 部署指令碼
- Web應用部署
- 發布打包
- GitHub發布

###  docker/ - Docker指令碼
- Docker服務管理
- 容器啟動停止
- 資料庫初始化

###  git/ - Git工具指令碼
- 上游同步
- 分支管理
- 貢獻工作流

## 使用原則

### 指令碼分類
- **tests/** - 單元測試和集成測試（pytest執行）
- **scripts/** - 工具指令碼和驗證指令碼（獨立執行）
- **tools/** - 複雜的獨立工具程式

### 執行方式
```bash
# 從項目根目錄執行
cd C:\\code\\TradingAgentsCN

# Python指令碼
python scripts/validation/verify_gitignore.py

# PowerShell指令碼  
powershell -ExecutionPolicy Bypass -File scripts/maintenance/cleanup.ps1
```

## 註意事項

- 所有指令碼應該從項目根目錄執行
- 檢查指令碼的依賴要求
- 某些指令碼可能需要特殊權限
- 保持指令碼的獨立性和可重用性
"""
    
    with open(main_readme_path, 'w', encoding='utf-8') as f:
        f.write(main_readme_content)
    logger.info(f" 建立主README: scripts/README.md")
    
    # 顯示剩餘的未分類指令碼
    logger.info(f"\n 檢查未分類的指令碼...")
    remaining_scripts = []
    for item in scripts_path.iterdir():
        if item.is_file() and item.suffix in ['.py', '.sh', '.bat', '.js']:
            if item.name not in ['README.md']:
                remaining_scripts.append(item.name)
    
    if remaining_scripts:
        logger.warning(f" 未分類的指令碼:")
        for script in remaining_scripts:
            logger.info(f"  - {script}")
        logger.info(f"建議手動將這些指令碼移動到合適的分類目錄中")
    else:
        logger.info(f" 所有指令碼都已分類")
    
    logger.info(f"\n Scripts目錄整理完成！")
    
    return True

def main():
    """主函數"""
    try:
        success = create_scripts_structure()
        
        if success:
            logger.info(f"\n 整理結果:")
            logger.info(f" 建立了分類子目錄")
            logger.info(f" 移動了現有指令碼")
            logger.info(f" 生成了README檔案")
            logger.info(f"\n 建議:")
            logger.info(f"1. 驗證指令碼放在 scripts/validation/")
            logger.info(f"2. 測試代碼放在 tests/")
            logger.info(f"3. 新指令碼按功能放在對應分類目錄")
        
        return success
        
    except Exception as e:
        logger.error(f" 整理失敗: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
