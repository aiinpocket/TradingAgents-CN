#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
語法檢查腳本 - 檢查除env目錄外的所有Python文件
Syntax Check Script - Check all Python files except env directory
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple

def find_python_files(root_dir: str, exclude_dirs: List[str] = None) -> List[str]:
    """
    查找所有Python文件，排除指定目錄
    Find all Python files, excluding specified directories
    """
    if exclude_dirs is None:
        exclude_dirs = ['env', '.env', 'venv', '.venv', '__pycache__', '.git', 'node_modules']
    
    python_files = []
    root_path = Path(root_dir)
    
    for file_path in root_path.rglob('*.py'):
        # 檢查是否在排除目錄中
        should_exclude = False
        for exclude_dir in exclude_dirs:
            if exclude_dir in file_path.parts:
                should_exclude = True
                break
        
        if not should_exclude:
            python_files.append(str(file_path))
    
    return sorted(python_files)

def check_syntax(file_path: str) -> Tuple[bool, str]:
    """
    檢查單個Python文件的語法
    Check syntax of a single Python file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 嘗試解析AST
        ast.parse(content, filename=file_path)
        return True, "OK"
    
    except SyntaxError as e:
        error_msg = f"語法錯誤 | Syntax Error: Line {e.lineno}, Column {e.offset}: {e.msg}"
        return False, error_msg
    
    except UnicodeDecodeError as e:
        error_msg = f"編碼錯誤 | Encoding Error: {e}"
        return False, error_msg
    
    except Exception as e:
        error_msg = f"其他錯誤 | Other Error: {e}"
        return False, error_msg

def main():
    """
    主函數
    Main function
    """
    print("\n🔍 開始語法檢查 | Starting syntax check...")
    
    # 獲取當前目錄
    current_dir = os.getcwd()
    print(f"📁 檢查目錄 | Checking directory: {current_dir}")
    
    # 查找所有Python文件
    python_files = find_python_files(current_dir)
    print(f"📄 找到 {len(python_files)} 個Python文件 | Found {len(python_files)} Python files")
    
    # 檢查語法
    success_count = 0
    error_count = 0
    error_files = []
    
    for file_path in python_files:
        relative_path = os.path.relpath(file_path, current_dir)
        is_valid, message = check_syntax(file_path)
        
        if is_valid:
            success_count += 1
            print(f"✅ {relative_path}: {message}")
        else:
            error_count += 1
            error_files.append((relative_path, message))
            print(f"❌ {relative_path}: {message}")
    
    # 輸出总結
    print(f"\n📊 檢查完成 | Check completed:")
    print(f"✅ 成功文件 | Successful files: {success_count}")
    print(f"❌ 錯誤文件 | Error files: {error_count}")
    
    if error_files:
        print(f"\n🚨 錯誤詳情 | Error details:")
        for file_path, error_msg in error_files:
            print(f"  {file_path}: {error_msg}")
        
        # 返回錯誤代碼
        sys.exit(1)
    else:
        print(f"\n🎉 所有文件語法檢查通過！| All files passed syntax check!")
        sys.exit(0)

if __name__ == "__main__":
    main()