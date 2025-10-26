#!/usr/bin/env python3
"""
将項目中的print語句轉換為日誌輸出
排除tests和env目錄
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple


class PrintToLogConverter:
    """Print語句到日誌轉換器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.converted_files = []
        self.errors = []
        
        # 需要排除的目錄
        self.exclude_dirs = {'tests', 'env', '.env', '__pycache__', '.git', '.github'}
        
        # 需要排除的文件模式
        self.exclude_patterns = {
            'test_*.py',
            '*_test.py', 
            'conftest.py',
            'setup.py',
            'convert_prints_to_logs.py'  # 排除自己
        }
    
    def should_skip_file(self, file_path: Path) -> bool:
        """判斷是否應该跳過文件"""
        # 檢查是否在排除目錄中
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return True
        
        # 檢查文件名模式
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return True
        
        return False
    
    def get_log_level_from_message(self, message: str) -> str:
        """根據消息內容確定日誌級別"""
        message_lower = message.lower()
        
        # 錯誤級別
        if any(indicator in message for indicator in ['❌', '錯誤', 'ERROR', 'Error', '失败', 'Failed', 'Exception']):
            return 'error'
        
        # 警告級別
        elif any(indicator in message for indicator in ['⚠️', '警告', 'WARNING', 'Warning', '註意']):
            return 'warning'
        
        # 調試級別
        elif any(indicator in message for indicator in ['🔍', 'DEBUG', 'Debug', '[DEBUG]']):
            return 'debug'
        
        # 成功/完成信息
        elif any(indicator in message for indicator in ['✅', '成功', '完成', 'Success', 'Complete']):
            return 'info'
        
        # 默認信息級別
        else:
            return 'info'
    
    def add_logging_import(self, content: str, file_path: Path) -> str:
        """添加日誌導入"""
        # 檢查是否已經有日誌導入
        if 'from tradingagents.utils.logging_manager import get_logger' in content:
            return content
        
        lines = content.split('\n')
        insert_pos = 0
        in_docstring = False
        docstring_char = None
        
        # 找到所有import語句的結束位置
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 處理文档字符串
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    docstring_char = stripped[:3]
                    if not stripped.endswith(docstring_char) or len(stripped) == 3:
                        in_docstring = True
                    continue
            else:
                if stripped.endswith(docstring_char):
                    in_docstring = False
                continue
            
            # 跳過空行和註釋
            if not stripped or stripped.startswith('#'):
                continue
            
            # 如果是import語句，更新插入位置
            if stripped.startswith(('import ', 'from ')) and 'logging_manager' not in line:
                insert_pos = i + 1
            # 如果遇到非import語句，停止搜索
            elif insert_pos > 0:
                break
        
        # 確定日誌器名稱
        relative_path = file_path.relative_to(self.project_root)
        if 'web' in str(relative_path):
            logger_name = 'web'
        elif 'tradingagents' in str(relative_path):
            if 'agents' in str(relative_path):
                logger_name = 'agents'
            elif 'dataflows' in str(relative_path):
                logger_name = 'dataflows'
            elif 'llm_adapters' in str(relative_path):
                logger_name = 'llm_adapters'
            elif 'utils' in str(relative_path):
                logger_name = 'utils'
            else:
                logger_name = 'tradingagents'
        elif 'cli' in str(relative_path):
            logger_name = 'cli'
        elif 'scripts' in str(relative_path):
            logger_name = 'scripts'
        else:
            logger_name = 'default'
        
        # 插入日誌導入
        lines.insert(insert_pos, "")
        lines.insert(insert_pos + 1, "# 導入日誌模塊")
        lines.insert(insert_pos + 2, "from tradingagents.utils.logging_manager import get_logger")
        lines.insert(insert_pos + 3, f"logger = get_logger('{logger_name}')")
        
        return '\n'.join(lines)
    
    def convert_print_statements(self, content: str) -> str:
        """轉換print語句為日誌調用"""
        lines = content.split('\n')
        modified_lines = []
        
        for line in lines:
            # 跳過註釋行
            if line.strip().startswith('#'):
                modified_lines.append(line)
                continue
            
            # 查找print語句
            # 匹配各種print格式：print("..."), print(f"..."), print('...'), print(f'...')
            print_patterns = [
                r'print\s*\(\s*f?"([^"]*?)"([^)]*)\)',  # print("...")
                r"print\s*\(\s*f?'([^']*?)'([^)]*)\)",   # print('...')
                r'print\s*\(\s*f?"""([^"]*?)"""([^)]*)\)',  # print("""...""")
                r"print\s*\(\s*f?'''([^']*?)'''([^)]*)\)",   # print('''...''')
            ]
            
            line_modified = False
            for pattern in print_patterns:
                match = re.search(pattern, line, re.DOTALL)
                if match:
                    message = match.group(1)
                    rest = match.group(2).strip()
                    
                    # 確定日誌級別
                    log_level = self.get_log_level_from_message(message)
                    
                    # 獲取縮進
                    indent = len(line) - len(line.lstrip())
                    
                    # 構建新的日誌語句
                    if rest and rest.startswith(','):
                        # 有額外參數
                        new_line = f"{' ' * indent}logger.{log_level}(f\"{message}\"{rest})"
                    else:
                        # 没有額外參數
                        new_line = f"{' ' * indent}logger.{log_level}(f\"{message}\")"
                    
                    line = new_line
                    line_modified = True
                    break
            
            modified_lines.append(line)
        
        return '\n'.join(modified_lines)
    
    def convert_file(self, file_path: Path) -> bool:
        """轉換單個文件"""
        try:
            print(f"🔄 轉換文件: {file_path}")
            
            # 讀取文件內容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否包含print語句
            if 'print(' not in content:
                print(f"⏭️ 跳過文件（無print語句）: {file_path}")
                return False
            
            original_content = content
            
            # 添加日誌導入
            content = self.add_logging_import(content, file_path)
            
            # 轉換print語句
            content = self.convert_print_statements(content)
            
            # 如果內容有變化，寫回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.converted_files.append(str(file_path))
                print(f"✅ 轉換完成: {file_path}")
                return True
            else:
                print(f"⏭️ 無需修改: {file_path}")
                return False
                
        except Exception as e:
            error_msg = f"❌ 轉換失败 {file_path}: {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
    
    def convert_project(self) -> Dict[str, int]:
        """轉換整個項目"""
        stats = {'converted': 0, 'skipped': 0, 'errors': 0}
        
        # 查找所有Python文件
        for py_file in self.project_root.rglob('*.py'):
            if self.should_skip_file(py_file):
                continue
            
            if self.convert_file(py_file):
                stats['converted'] += 1
            else:
                if str(py_file) in [error.split(':')[0] for error in self.errors]:
                    stats['errors'] += 1
                else:
                    stats['skipped'] += 1
        
        return stats
    
    def generate_report(self) -> str:
        """生成轉換報告"""
        report = f"""
# Print語句轉換報告

## 轉換統計
- 成功轉換文件: {len(self.converted_files)}
- 錯誤數量: {len(self.errors)}

## 轉換的文件
"""
        for file_path in self.converted_files:
            report += f"- {file_path}\n"
        
        if self.errors:
            report += "\n## 錯誤列表\n"
            for error in self.errors:
                report += f"- {error}\n"
        
        return report


def main():
    """主函數"""
    print("🚀 開始将print語句轉換為日誌輸出")
    print("=" * 50)
    
    # 確定項目根目錄
    project_root = Path(__file__).parent
    
    # 創建轉換器
    converter = PrintToLogConverter(project_root)
    
    # 執行轉換
    stats = converter.convert_project()
    
    # 顯示結果
    print("\n" + "=" * 50)
    print("📊 轉換結果汇总:")
    print(f"   轉換文件: {stats['converted']}")
    print(f"   跳過文件: {stats['skipped']}")
    print(f"   錯誤文件: {stats['errors']}")
    
    if stats['converted'] > 0:
        print(f"\n🎉 成功轉換 {stats['converted']} 個文件的print語句為日誌輸出！")
    
    if converter.errors:
        print(f"\n⚠️ 有 {len(converter.errors)} 個文件轉換失败")
        for error in converter.errors:
            print(f"   {error}")
    
    # 生成報告
    report = converter.generate_report()
    report_file = project_root / 'print_to_log_conversion_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 詳細報告已保存到: {report_file}")


if __name__ == '__main__':
    main()