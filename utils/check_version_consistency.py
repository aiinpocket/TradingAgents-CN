#!/usr/bin/env python3
"""


"""

import os
import re
from pathlib import Path

# 
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')


def get_target_version():
    """VERSION"""
    version_file = Path("VERSION")
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def check_file_versions(file_path: Path, target_version: str):
    """"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 
        version_patterns = [
            r'v?\d+\.\d+\.\d+(?:-\w+)?',  # 
            r'Version-v\d+\.\d+\.\d+',    # Badge
            r'.*?v?\d+\.\d+\.\d+',     # 
        ]
        
        issues = []
        
        for pattern in version_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                found_version = match.group()
                
                # 
                if any(skip in found_version.lower() for skip in [
                    'python-3.', 'mongodb', 'redis', 'streamlit', 
                    'langchain', 'pandas', 'numpy'
                ]):
                    continue
                
                # 
                normalized_found = found_version.lower().replace('version-', '').replace('', '').strip()
                normalized_target = target_version.lower()
                
                if normalized_found != normalized_target and not normalized_found.startswith('0.1.'):
                    # 
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
    """"""
    logger.debug(f" ")
    logger.info(f"=")
    
    # 
    target_version = get_target_version()
    if not target_version:
        logger.error(f" VERSION")
        return
    
    logger.info(f" : {target_version}")
    
    # 
    files_to_check = [
        "README.md",
        "docs/PROJECT_INFO.md",
        "docs/releases/CHANGELOG.md",
        "docs/overview/quick-start.md",
        "docs/configuration/llm-config.md",
        "docs/data/data-sources.md",
    ]
    
    total_issues = 0
    
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f" : {file_path}")
            continue
        
        logger.info(f"\n : {file_path}")
        issues = check_file_versions(path, target_version)
        
        if not issues:
            logger.info(f"    ")
        else:
            for issue in issues:
                if 'error' in issue:
                    logger.error(f"    : {issue['error']}")
                else:
                    logger.error(f"    {issue['line']}:  '{issue['found']}',  '{issue['expected']}'")
                    logger.info(f"      : ...{issue['context']}...")
                total_issues += len(issues)
    
    # 
    logger.info(f"\n ")
    logger.info(f"=")
    
    if total_issues == 0:
        logger.info(f" ")
        logger.info(f" : {target_version}")
    else:
        logger.warning(f"  {total_issues} ")
        logger.info(f"")
    
    # 
    logger.info(f"\n :")
    logger.info(f"   - : VERSION")
    logger.info(f"   - : {target_version}")
    logger.info(f"   - : v0.1.x")
    logger.info(f"   - : CHANGELOG")

if __name__ == "__main__":
    main()
