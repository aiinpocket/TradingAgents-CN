#!/usr/bin/env python3
"""
修複重複logger定義問題的腳本

這個腳本會:
1. 扫描所有Python文件
2. 檢測重複的logger = get_logger()定義
3. 移除重複定義，只保留文件头部的第一個定義
4. 生成詳細的修複報告
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def find_python_files(root_dir: str, exclude_dirs: List[str] = None) -> List[str]:
    """查找所有Python文件"""
    if exclude_dirs is None:
        exclude_dirs = ['env', '.env', '__pycache__', '.git', 'node_modules', '.venv']
    
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # 排除指定目錄
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def analyze_logger_definitions(file_path: str) -> Dict:
    """分析文件中的logger定義"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {'error': str(e), 'logger_lines': []}
    
    logger_lines = []
    logger_pattern = re.compile(r'^\s*logger\s*=\s*get_logger\s*\(')
    
    for i, line in enumerate(lines, 1):
        if logger_pattern.match(line):
            logger_lines.append({
                'line_number': i,
                'content': line.strip(),
                'indentation': len(line) - len(line.lstrip())
            })
    
    return {
        'total_lines': len(lines),
        'logger_lines': logger_lines,
        'has_duplicates': len(logger_lines) > 1
    }

def find_import_section_end(lines: List[str]) -> int:
    """找到import語句結束的位置"""
    import_end = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 處理文档字符串
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) == 1:  # 開始文档字符串
                    in_docstring = True
                # 如果同一行包含開始和結束，則不進入文档字符串狀態
        else:
            if docstring_char in stripped:
                in_docstring = False
                continue
        
        if in_docstring:
            continue
            
        # 跳過註釋和空行
        if not stripped or stripped.startswith('#'):
            continue
            
        # 檢查是否是import語句
        if (stripped.startswith('import ') or 
            stripped.startswith('from ') or
            stripped.startswith('sys.path.') or
            stripped.startswith('load_dotenv(')):
            import_end = i + 1
        elif stripped and not stripped.startswith('#'):
            # 遇到非import語句，停止
            break
    
    return import_end

def fix_duplicate_loggers(file_path: str) -> Dict:
    """修複文件中的重複logger定義"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {'success': False, 'error': f'讀取文件失败: {str(e)}'}
    
    analysis = analyze_logger_definitions(file_path)
    
    if not analysis['has_duplicates']:
        return {'success': True, 'message': '無需修複', 'changes': 0}
    
    logger_lines = analysis['logger_lines']
    if len(logger_lines) <= 1:
        return {'success': True, 'message': '無需修複', 'changes': 0}
    
    # 找到import語句結束位置
    import_end = find_import_section_end(lines)
    
    # 確定要保留的logger定義
    keep_logger = None
    remove_lines = []
    
    # 優先保留在import区域附近的logger定義
    for logger_info in logger_lines:
        line_num = logger_info['line_number'] - 1  # 轉換為0索引
        if line_num <= import_end + 5:  # 在import区域附近
            if keep_logger is None:
                keep_logger = logger_info
            else:
                remove_lines.append(line_num)
        else:
            remove_lines.append(line_num)
    
    # 如果没有在import区域找到，保留第一個
    if keep_logger is None:
        keep_logger = logger_lines[0]
        remove_lines = [info['line_number'] - 1 for info in logger_lines[1:]]
    
    # 移除重複的logger定義（從後往前刪除以保持行號正確）
    remove_lines.sort(reverse=True)
    changes_made = 0
    
    for line_num in remove_lines:
        if 0 <= line_num < len(lines):
            # 檢查是否確實是logger定義
            if 'logger = get_logger(' in lines[line_num]:
                lines.pop(line_num)
                changes_made += 1
    
    if changes_made > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return {
                'success': True, 
                'message': f'移除了{changes_made}個重複的logger定義',
                'changes': changes_made,
                'kept_logger': keep_logger['content'],
                'removed_count': changes_made
            }
        except Exception as e:
            return {'success': False, 'error': f'寫入文件失败: {str(e)}'}
    
    return {'success': True, 'message': '無需修複', 'changes': 0}

def main():
    """主函數"""
    root_dir = "c:\\code\\TradingAgentsCN"
    
    print("🔍 開始扫描Python文件...")
    python_files = find_python_files(root_dir)
    print(f"📁 找到 {len(python_files)} 個Python文件")
    
    # 分析所有文件
    print("\n📊 分析logger定義...")
    files_with_duplicates = []
    total_duplicates = 0
    
    for file_path in python_files:
        analysis = analyze_logger_definitions(file_path)
        if analysis.get('has_duplicates', False):
            files_with_duplicates.append((file_path, analysis))
            total_duplicates += len(analysis['logger_lines']) - 1
    
    print(f"⚠️  發現 {len(files_with_duplicates)} 個文件有重複logger定義")
    print(f"📈 总共有 {total_duplicates} 個重複定義需要修複")
    
    if not files_with_duplicates:
        print("✅ 没有發現重複的logger定義！")
        return
    
    # 修複重複定義
    print("\n🔧 開始修複重複logger定義...")
    fixed_files = 0
    total_changes = 0
    errors = []
    
    for file_path, analysis in files_with_duplicates:
        rel_path = os.path.relpath(file_path, root_dir)
        print(f"\n📝 處理: {rel_path}")
        print(f"   發現 {len(analysis['logger_lines'])} 個logger定義")
        
        result = fix_duplicate_loggers(file_path)
        
        if result['success']:
            if result['changes'] > 0:
                fixed_files += 1
                total_changes += result['changes']
                print(f"   ✅ {result['message']}")
                if 'kept_logger' in result:
                    print(f"   📌 保留: {result['kept_logger']}")
            else:
                print(f"   ℹ️  {result['message']}")
        else:
            errors.append((rel_path, result['error']))
            print(f"   ❌ {result['error']}")
    
    # 生成報告
    print("\n" + "="*60)
    print("📋 修複報告")
    print("="*60)
    print(f"✅ 成功修複文件數: {fixed_files}")
    print(f"🔧 总共移除重複定義: {total_changes}")
    print(f"❌ 修複失败文件數: {len(errors)}")
    
    if errors:
        print("\n❌ 修複失败的文件:")
        for file_path, error in errors:
            print(f"   - {file_path}: {error}")
    
    # 保存詳細報告
    report_file = "duplicate_logger_fix_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 重複Logger定義修複報告\n\n")
        f.write(f"## 概要\n\n")
        f.write(f"- 扫描文件总數: {len(python_files)}\n")
        f.write(f"- 發現重複定義文件數: {len(files_with_duplicates)}\n")
        f.write(f"- 成功修複文件數: {fixed_files}\n")
        f.write(f"- 总共移除重複定義: {total_changes}\n")
        f.write(f"- 修複失败文件數: {len(errors)}\n\n")
        
        if errors:
            f.write("## 修複失败的文件\n\n")
            for file_path, error in errors:
                f.write(f"- `{file_path}`: {error}\n")
            f.write("\n")
        
        f.write("## 修複詳情\n\n")
        for file_path, analysis in files_with_duplicates:
            rel_path = os.path.relpath(file_path, root_dir)
            f.write(f"### {rel_path}\n\n")
            f.write(f"- 原有logger定義數: {len(analysis['logger_lines'])}\n")
            for i, logger_info in enumerate(analysis['logger_lines']):
                f.write(f"  - 第{logger_info['line_number']}行: `{logger_info['content']}`\n")
            f.write("\n")
    
    print(f"\n📄 詳細報告已保存到: {report_file}")
    print("\n🎉 修複完成！")

if __name__ == "__main__":
    main()