#!/usr/bin/env python3
"""

"""

import re
from pathlib import Path
from collections import defaultdict

def has_simplified_chinese(text):
    """
    
    
    """
    # 
    simplified_chars = {
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '', '': '',
        '': '', '': '', '': '', '': '',
    }

    found = []
    for char, traditional in simplified_chars.items():
        if char in text:
            found.append((char, traditional))

    return found

def scan_file(file_path):
    """"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        simplified_found = has_simplified_chinese(content)
        return simplified_found

    except Exception as e:
        return None

def main():
    project_root = Path(__file__).parent.parent
    print(f" : {project_root}\n")
    print(" ...\n")

    # 
    extensions = {'.py', '.md', '.yaml', '.yml', '.json', '.txt', '.sh', '.rst'}

    # 
    exclude_dirs = {
        '.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
        'node_modules', '.idea', '.vscode', 'dist', 'build',
        'data_backup_', 'data_cache', 'results', 'logs', 'env'
    }

    # 
    total_files = 0
    files_with_simplified = 0
    simplified_chars_count = defaultdict(int)

    # 
    for root, dirs, files in os.walk(project_root):
        # 
        dirs[:] = [d for d in dirs if not any(exc in d for exc in exclude_dirs)]

        for file in files:
            file_path = Path(root) / file

            if file_path.suffix not in extensions:
                continue

            total_files += 1
            result = scan_file(file_path)

            if result:
                files_with_simplified += 1
                rel_path = file_path.relative_to(project_root)
                print(f"  {rel_path}")
                for simp, trad in result[:5]:  # 5
                    print(f"    '{simp}' → '{trad}'")
                    simplified_chars_count[simp] += 1
                if len(result) > 5:
                    print(f"    ... {len(result) - 5} ")
                print()

    # 
    print(f"\n{'='*60}")
    print(f" ")
    print(f"{'='*60}")
    print(f"   : {total_files}")
    print(f"   : {files_with_simplified}")

    if simplified_chars_count:
        print(f"\n   :")
        sorted_chars = sorted(simplified_chars_count.items(), key=lambda x: x[1], reverse=True)
        for char, count in sorted_chars[:20]:
            print(f"      '{char}': {count} ")

    if files_with_simplified == 0:
        print(f"\n    ")
    else:
        print(f"\n     ")

    print(f"{'='*60}")

import os
if __name__ == "__main__":
    main()
