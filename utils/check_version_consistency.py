#!/usr/bin/env python3
"""
版本號一致性檢查工具
確保項目中所有版本號引用都是一致的
"""

import os
import re
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')


def get_target_version():
    """從VERSION文件獲取目標版本號"""
    version_file = Path("VERSION")
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def check_file_versions(file_path: Path, target_version: str):
    """檢查文件中的版本號"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 版本號模式
        version_patterns = [
            r'v?\d+\.\d+\.\d+(?:-\w+)?',  # 基本版本號
            r'Version-v\d+\.\d+\.\d+',    # Badge版本號
            r'版本.*?v?\d+\.\d+\.\d+',     # 中文版本描述
        ]
        
        issues = []
        
        for pattern in version_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                found_version = match.group()
                
                # 跳過一些特殊情况
                if any(skip in found_version.lower() for skip in [
                    'python-3.', 'mongodb', 'redis', 'streamlit', 
                    'langchain', 'pandas', 'numpy'
                ]):
                    continue
                
                # 標準化版本號進行比較
                normalized_found = found_version.lower().replace('version-', '').replace('版本', '').strip()
                normalized_target = target_version.lower()
                
                if normalized_found != normalized_target and not normalized_found.startswith('0.1.'):
                    # 如果不是歷史版本號，則報告不一致
                    if not any(hist in normalized_found for hist in ['0.1.1', '0.1.2', '0.1.3', '0.1.4', '0.1.5']):
                        issues.append({
                            'line': content[:match.start()].count('\n') + 1,
                            'found': found_version,
                            'expected': target_version,
                            'context': content[max(0, match.start()-20):match.end()+20]
                        })
        
        return issues
        
    except Exception as e:
        return [{'error': str(e)}]

def main():
    """主檢查函數"""
    logger.debug(f"🔍 版本號一致性檢查")
    logger.info(f"=")
    
    # 獲取目標版本號
    target_version = get_target_version()
    if not target_version:
        logger.error(f"❌ 無法讀取VERSION文件")
        return
    
    logger.info(f"🎯 目標版本: {target_version}")
    
    # 需要檢查的文件
    files_to_check = [
        "README.md",
        "docs/PROJECT_INFO.md",
        "docs/releases/CHANGELOG.md",
        "docs/overview/quick-start.md",
        "docs/configuration/dashscope-config.md",
        "docs/data/data-sources.md",
    ]
    
    total_issues = 0
    
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"⚠️ 文件不存在: {file_path}")
            continue
        
        logger.info(f"\n📄 檢查文件: {file_path}")
        issues = check_file_versions(path, target_version)
        
        if not issues:
            logger.info(f"   ✅ 版本號一致")
        else:
            for issue in issues:
                if 'error' in issue:
                    logger.error(f"   ❌ 檢查錯誤: {issue['error']}")
                else:
                    logger.error(f"   ❌ 第{issue['line']}行: 發現 '{issue['found']}', 期望 '{issue['expected']}'")
                    logger.info(f"      上下文: ...{issue['context']}...")
                total_issues += len(issues)
    
    # 总結
    logger.info(f"\n📊 檢查总結")
    logger.info(f"=")
    
    if total_issues == 0:
        logger.info(f"🎉 所有版本號都是一致的！")
        logger.info(f"✅ 當前版本: {target_version}")
    else:
        logger.warning(f"⚠️ 發現 {total_issues} 個版本號不一致問題")
        logger.info(f"請手動修複上述問題")
    
    # 版本號規範提醒
    logger.info(f"\n💡 版本號規範:")
    logger.info(f"   - 主版本文件: VERSION")
    logger.info(f"   - 當前版本: {target_version}")
    logger.info(f"   - 格式要求: v0.1.x")
    logger.info(f"   - 歷史版本: 可以保留在CHANGELOG中")

if __name__ == "__main__":
    main()
