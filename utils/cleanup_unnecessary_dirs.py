#!/usr/bin/env python3
"""


"""

import os
import shutil
from pathlib import Path

# 
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')


def cleanup_directories():
    """"""
    logger.info(f" ")
    logger.info(f"=")
    
    # 
    project_root = Path(".")
    
    # 
    cleanup_dirs = [
        "tradingagents.egg-info",
        "enhanced_analysis_reports",
        "__pycache__",
        ".pytest_cache",
    ]
    
    # 
    cleanup_patterns = [
        "*.pyc",
        "*.pyo", 
        "*.pyd",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    cleaned_count = 0
    
    # 
    for dir_name in cleanup_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                logger.info(f" : {dir_name}")
                cleaned_count += 1
            except Exception as e:
                logger.error(f"  {dir_name}: {e}")
    
    # 
    for pattern in cleanup_patterns:
        for file_path in project_root.rglob(pattern):
            try:
                file_path.unlink()
                logger.info(f" : {file_path}")
                cleaned_count += 1
            except Exception as e:
                logger.error(f"  {file_path}: {e}")
    
    return cleaned_count

def update_gitignore():
    """.gitignore"""
    logger.info(f"\n .gitignore")
    logger.info(f"=")
    
    gitignore_path = Path(".gitignore")
    
    # 
    ignore_rules = [
        "# Python",
        "*.egg-info/",
        "tradingagents.egg-info/",
        "",
        "# ", 
        "enhanced_analysis_reports/",
        "analysis_reports/",
        "",
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        ".pytest_cache/",
        "",
        "# ",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# IDE",
        ".vscode/settings.json",
        ".idea/",
        "",
        "# ",
        "*.log",
        "logs/",
    ]
    
    try:
        # 
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 
        new_rules = []
        for rule in ignore_rules:
            if rule.strip() and rule not in existing_content:
                new_rules.append(rule)
        
        if new_rules:
            # 
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write("\n# \n")
                for rule in new_rules:
                    f.write(f"{rule}\n")
            
            logger.info(f"  {len(new_rules)} ")
        else:
            logger.info(f" .gitignore")
            
    except Exception as e:
        logger.error(f" .gitignore: {e}")

def analyze_upstream_contribution():
    """upstream_contribution"""
    logger.debug(f"\n upstream_contribution")
    logger.info(f"=")
    
    upstream_dir = Path("upstream_contribution")
    
    if not upstream_dir.exists():
        logger.info(f" upstream_contribution")
        return
    
    # 
    batch_dirs = list(upstream_dir.glob("batch*"))
    json_files = list(upstream_dir.glob("*.json"))
    
    logger.info(f" :")
    logger.info(f"   - Batch: {len(batch_dirs)}")
    logger.info(f"   - JSON: {len(json_files)}")
    
    for batch_dir in batch_dirs:
        logger.info(f"   - {batch_dir.name}: {len(list(batch_dir.rglob('*')))}")
    
    # 
    logger.info(f"\n upstream_contribution:")
    logger.info(f"   - (TauricResearch/TradingAgents)")
    logger.info(f"   - ")
    logger.info(f"   - ")
    
    return len(batch_dirs) + len(json_files)

def main():
    """"""
    logger.info(f" TradingAgents ")
    logger.info(f"=")
    logger.info(f" : ")
    logger.info(f"=")
    
    # 
    cleaned_count = cleanup_directories()
    
    # gitignore
    update_gitignore()
    
    # upstream_contribution
    upstream_count = analyze_upstream_contribution()
    
    # 
    logger.info(f"\n ")
    logger.info(f"=")
    logger.info(f"  {cleaned_count} /")
    logger.info(f"  .gitignore ")
    
    if upstream_count > 0:
        logger.warning(f" upstream_contribution {upstream_count} ")
        logger.info(f"   :")
        logger.info(f"   rm -rf upstream_contribution/")
    
    logger.info(f"\n ")
    logger.info(f"\n :")
    logger.info(f"   1. git: git status")
    logger.info(f"   2. : git add . && git commit -m ''")
    logger.info(f"   3. upstream_contribution")

if __name__ == "__main__":
    main()
