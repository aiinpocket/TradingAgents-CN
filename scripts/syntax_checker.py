#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
語法檢查器 - 檢查項目中所有Python檔案的語法錯誤
Syntax Checker - Check syntax errors in all Python files in the project
"""

import os
import py_compile
import sys
from pathlib import Path
from typing import List, Tuple

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')



def find_python_files(root_dir: str, exclude_dirs: List[str] = None) -> List[str]:
    """
    查找項目中所有Python檔案，排除指定目錄
    Find all Python files in the project, excluding specified directories
    """
    if exclude_dirs is None:
        exclude_dirs = ['env', 'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache']
    
    python_files = []
    root_path = Path(root_dir)
    
    for file_path in root_path.rglob('*.py'):
        # 檢查是否在排除目錄中
        if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
            continue
        python_files.append(str(file_path))
    
    return sorted(python_files)


def check_syntax(file_path: str) -> Tuple[bool, str]:
    """
    檢查單個Python檔案的語法
    Check syntax of a single Python file
    
    Returns:
        Tuple[bool, str]: (是否有語法錯誤, 錯誤訊息)
    """
    try:
        py_compile.compile(file_path, doraise=True)
        return False, ""
    except py_compile.PyCompileError as e:
        return True, str(e)
    except Exception as e:
        return True, f"Unexpected error: {str(e)}"


def main():
    """
    主函數 - 執行語法檢查
    Main function - Execute syntax checking
    """
    logger.error(f" 開始檢查項目中的Python檔案語法錯誤...")
    logger.debug(f" Starting syntax check for Python files in the project...\n")
    
    # 取得當前目錄
    current_dir = os.getcwd()
    logger.info(f" 檢查目錄: {current_dir}")
    logger.info(f" Checking directory: {current_dir}\n")
    
    # 查找所有Python檔案
    python_files = find_python_files(current_dir)
    logger.info(f" 找到 {len(python_files)} 個Python檔案")
    logger.info(f" Found {len(python_files)} Python files\n")
    
    # 檢查語法錯誤
    error_files = []
    success_count = 0
    
    for i, file_path in enumerate(python_files, 1):
        relative_path = os.path.relpath(file_path, current_dir)
        logger.info(f"[{i:3d}/{len(python_files)}] 檢查: {relative_path}", end=" ")
        
        has_error, error_msg = check_syntax(file_path)
        
        if has_error:
            logger.error(f" 語法錯誤")
            error_files.append((relative_path, error_msg))
        else:
            logger.info(f" 語法正確")
            success_count += 1
    
    # 輸出結果摘要
    logger.info(f"\n")
    logger.info(f" 檢查結果摘要 | Check Results Summary")
    logger.info(f"=")
    logger.info(f" 語法正確的檔案: {success_count}")
    logger.info(f" Files with correct syntax: {success_count}")
    logger.error(f" 有語法錯誤的檔案: {len(error_files)}")
    logger.error(f" Files with syntax errors: {len(error_files)}")
    
    if error_files:
        logger.error(f"\n 語法錯誤詳情 | Syntax Error Details:")
        logger.info(f"-")
        for file_path, error_msg in error_files:
            logger.info(f"\n 檔案: {file_path}")
            logger.info(f" File: {file_path}")
            logger.error(f" 錯誤: {error_msg}")
            logger.error(f" Error: {error_msg}")
        
        logger.error(f"\n 建議: 請修復上述語法錯誤後重新執行檢查")
        logger.info(f" Suggestion: Please fix the above syntax errors and run the check again")
        sys.exit(1)
    else:
        logger.info(f"\n 恭喜！所有Python檔案語法檢查通過！")
        logger.info(f" Congratulations! All Python files passed syntax check!")
        sys.exit(0)


if __name__ == "__main__":
    main()