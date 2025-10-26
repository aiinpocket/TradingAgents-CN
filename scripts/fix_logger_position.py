#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修複logger變量位置腳本 (改進版)
Fix logger variable position script (improved version)

将錯誤位置的logger初始化移動到文件头部import語句下面
Move misplaced logger initialization to the correct position after import statements
"""

import os
import re
import sys
from typing import List, Tuple, Optional
from collections import defaultdict

class LoggerPositionFixer:
    """
    Logger位置修複器
    Logger position fixer
    """
    
    def __init__(self):
        self.fixed_files = []
        self.skipped_files = []
        self.error_files = []
        
    def find_python_files(self, directory: str) -> List[str]:
        """
        查找所有Python文件
        Find all Python files
        """
        python_files = []
        
        for root, dirs, files in os.walk(directory):
            # 跳過虛擬環境目錄
            if 'env' in dirs:
                dirs.remove('env')
            if 'venv' in dirs:
                dirs.remove('venv')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
                    
        return python_files
    
    def analyze_file_structure(self, content: str) -> dict:
        """
        分析文件結構
        Analyze file structure
        """
        lines = content.split('\n')
        structure = {
            'docstring_end': 0,
            'last_import': 0,
            'logger_positions': [],
            'has_logging_import': False,
            'logging_import_line': -1,
            'proper_logger_exists': False
        }
        
        in_docstring = False
        docstring_quotes = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 檢查文档字符串
            if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                docstring_quotes = stripped[:3]
                in_docstring = True
                if stripped.count(docstring_quotes) >= 2:  # 單行文档字符串
                    in_docstring = False
                    structure['docstring_end'] = i + 1
                continue
            elif in_docstring and docstring_quotes in stripped:
                in_docstring = False
                structure['docstring_end'] = i + 1
                continue
            elif in_docstring:
                continue
                
            # 跳過註釋和空行
            if not stripped or stripped.startswith('#'):
                continue
                
            # 檢查import語句
            if (stripped.startswith('import ') or 
                stripped.startswith('from ') or
                ('import ' in stripped and not stripped.startswith('logger'))):
                structure['last_import'] = i + 1
                
                # 檢查是否有日誌相關的import
                if ('logging_manager' in stripped or 
                    'get_logger' in stripped):
                    structure['has_logging_import'] = True
                    structure['logging_import_line'] = i
                continue
                
            # 檢查logger初始化
            if re.match(r'^\s*logger\s*=\s*get_logger\s*\(', stripped):
                structure['logger_positions'].append(i)
                
                # 檢查是否在合適位置（import後不久）
                if i <= structure['last_import'] + 10:  # 允許在import後10行內
                    structure['proper_logger_exists'] = True
                
        return structure
    
    def fix_logger_position(self, file_path: str) -> bool:
        """
        修複單個文件的logger位置
        Fix logger position in a single file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            structure = self.analyze_file_structure(content)
            
            # 如果没有logger初始化或没有日誌import，跳過
            if not structure['logger_positions'] or not structure['has_logging_import']:
                return False
                
            # 如果只有一個logger且在正確位置，跳過
            if (len(structure['logger_positions']) == 1 and 
                structure['proper_logger_exists']):
                return False
                
            # 檢查是否需要修複
            needs_fix = False
            correct_position = max(structure['docstring_end'], structure['last_import'])
            
            # 查找錯誤位置的logger（在函數內部或文件末尾）
            misplaced_loggers = []
            for pos in structure['logger_positions']:
                # 如果logger在import後很远的位置，認為是錯誤位置
                if pos > correct_position + 20:
                    misplaced_loggers.append(pos)
                    needs_fix = True
                    
            if not needs_fix:
                return False
                
            # 提取logger初始化語句
            logger_statements = []
            lines_to_remove = []
            
            for pos in misplaced_loggers:
                logger_line = lines[pos].strip()
                if logger_line:
                    logger_statements.append(logger_line)
                    lines_to_remove.append(pos)
                    
            # 移除原位置的logger語句
            for pos in sorted(lines_to_remove, reverse=True):
                lines.pop(pos)
                
            # 如果已經有正確位置的logger，不重複添加
            if not structure['proper_logger_exists'] and logger_statements:
                # 找到插入位置
                insert_position = correct_position
                
                # 確保插入位置後有空行
                while (insert_position < len(lines) and 
                       lines[insert_position].strip() == ''):
                    insert_position += 1
                    
                # 插入第一個logger語句（通常只需要一個）
                lines.insert(insert_position, logger_statements[0])
                
                # 確保logger語句後有空行
                if (insert_position + 1 < len(lines) and
                    lines[insert_position + 1].strip() != ''):
                    lines.insert(insert_position + 1, '')
                
            # 寫回文件
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return True
            
        except Exception as e:
            print(f"修複文件 {file_path} 時出錯: {e}")
            return False
    
    def fix_all_files(self, directory: str) -> dict:
        """
        修複所有文件的logger位置
        Fix logger position in all files
        """
        python_files = self.find_python_files(directory)
        
        print(f"找到 {len(python_files)} 個Python文件")
        
        for file_path in python_files:
            relative_path = os.path.relpath(file_path, directory)
            
            try:
                if self.fix_logger_position(file_path):
                    self.fixed_files.append(relative_path)
                    print(f"✅ 修複: {relative_path}")
                else:
                    self.skipped_files.append(relative_path)
                    
            except Exception as e:
                self.error_files.append((relative_path, str(e)))
                print(f"❌ 錯誤: {relative_path} - {e}")
                
        return {
            'fixed': len(self.fixed_files),
            'skipped': len(self.skipped_files),
            'errors': len(self.error_files)
        }
    
    def generate_report(self, output_file: str = 'logger_position_fix_report.md'):
        """
        生成修複報告
        Generate fix report
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Logger位置修複報告\n")
            f.write("# Logger Position Fix Report\n\n")
            f.write(f"生成時間: {__import__('datetime').datetime.now()}\n\n")
            
            f.write("## 修複統計 | Fix Statistics\n\n")
            f.write(f"- 修複文件數: {len(self.fixed_files)}\n")
            f.write(f"- 跳過文件數: {len(self.skipped_files)}\n")
            f.write(f"- 錯誤文件數: {len(self.error_files)}\n\n")
            
            if self.fixed_files:
                f.write("## 修複的文件 | Fixed Files\n\n")
                for file_path in sorted(self.fixed_files):
                    f.write(f"- {file_path}\n")
                f.write("\n")
                
            if self.error_files:
                f.write("## 錯誤文件 | Error Files\n\n")
                for file_path, error in self.error_files:
                    f.write(f"- {file_path}: {error}\n")
                f.write("\n")

def main():
    """
    主函數
    Main function
    """
    print("🔧 開始修複logger位置問題...")
    
    current_dir = os.getcwd()
    fixer = LoggerPositionFixer()
    
    # 修複所有文件
    results = fixer.fix_all_files(current_dir)
    
    # 生成報告
    fixer.generate_report()
    
    print(f"\n📊 修複完成:")
    print(f"✅ 修複文件: {results['fixed']}")
    print(f"⏭️  跳過文件: {results['skipped']}")
    print(f"❌ 錯誤文件: {results['errors']}")
    print(f"\n📄 詳細報告: logger_position_fix_report.md")
    
    return results['errors']

if __name__ == "__main__":
    error_count = main()
    sys.exit(0 if error_count == 0 else 1)