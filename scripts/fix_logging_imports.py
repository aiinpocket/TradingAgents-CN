#!/usr/bin/env python3
"""
修複日誌導入位置腳本
将錯誤位置的日誌導入移動到文件顶部的正確位置
"""

import re
from pathlib import Path
from typing import List, Dict

class LoggingImportFixer:
    """日誌導入位置修複器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.fixed_files = []
        self.errors = []
    
    def should_skip_file(self, file_path: Path) -> bool:
        """判斷是否應该跳過文件"""
        # 跳過tests和env目錄
        path_parts = file_path.parts
        if 'tests' in path_parts or 'env' in path_parts:
            return True
        
        # 跳過__pycache__目錄
        if '__pycache__' in str(file_path):
            return True
        
        # 跳過這個腳本本身
        if file_path.name in ['fix_logging_imports.py', 'convert_prints_to_logs.py']:
            return True
        
        return False
    
    def fix_logging_import_position(self, content: str, file_path: Path) -> str:
        """修複日誌導入位置"""
        lines = content.split('\n')
        
        # 查找錯誤位置的日誌導入
        logging_import_lines = []
        logging_import_indices = []
        
        for i, line in enumerate(lines):
            if ('# 導入日誌模塊' in line or 
                'from tradingagents.utils.logging_manager import get_logger' in line or 
                (line.strip().startswith('logger = get_logger(') and 'logging_manager' in lines[max(0, i-2):i+1])):
                logging_import_lines.append(line)
                logging_import_indices.append(i)
        
        # 如果没有找到日誌導入，跳過
        if not logging_import_lines:
            return content
        
        # 移除原有的日誌導入
        for index in reversed(logging_import_indices):
            lines.pop(index)
        
        # 找到正確的插入位置（所有import語句之後）
        insert_pos = 0
        in_docstring = False
        docstring_char = None
        
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
        
        # 在正確位置插入日誌導入
        lines.insert(insert_pos, "")
        lines.insert(insert_pos + 1, "# 導入日誌模塊")
        lines.insert(insert_pos + 2, "from tradingagents.utils.logging_manager import get_logger")
        lines.insert(insert_pos + 3, f"logger = get_logger('{logger_name}')")
        
        return '\n'.join(lines)
    
    def fix_file(self, file_path: Path) -> bool:
        """修複單個文件"""
        try:
            print(f"🔧 檢查文件: {file_path}")
            
            # 讀取文件內容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否包含日誌導入
            if 'from tradingagents.utils.logging_manager import get_logger' not in content:
                return False
            
            original_content = content
            
            # 修複日誌導入位置
            content = self.fix_logging_import_position(content, file_path)
            
            # 如果內容有變化，寫回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixed_files.append(str(file_path))
                print(f"✅ 修複完成: {file_path}")
                return True
            else:
                print(f"⏭️ 無需修複: {file_path}")
                return False
                
        except Exception as e:
            error_msg = f"❌ 修複失败 {file_path}: {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
    
    def fix_project(self) -> Dict[str, int]:
        """修複整個項目"""
        stats = {'fixed': 0, 'skipped': 0, 'errors': 0}
        
        # 查找所有Python文件
        for py_file in self.project_root.rglob('*.py'):
            if self.should_skip_file(py_file):
                continue
            
            if self.fix_file(py_file):
                stats['fixed'] += 1
            else:
                if str(py_file) in [error.split(':')[0] for error in self.errors]:
                    stats['errors'] += 1
                else:
                    stats['skipped'] += 1
        
        return stats
    
    def generate_report(self) -> str:
        """生成修複報告"""
        report = f"""
# 日誌導入位置修複報告

## 修複統計
- 成功修複文件: {len(self.fixed_files)}
- 錯誤數量: {len(self.errors)}

## 修複的文件
"""
        for file_path in self.fixed_files:
            report += f"- {file_path}\n"
        
        if self.errors:
            report += "\n## 錯誤列表\n"
            for error in self.errors:
                report += f"- {error}\n"
        
        return report


def main():
    """主函數"""
    print("🔧 開始修複日誌導入位置")
    print("=" * 50)
    
    # 確定項目根目錄
    project_root = Path(__file__).parent
    
    # 創建修複器
    fixer = LoggingImportFixer(project_root)
    
    # 執行修複
    stats = fixer.fix_project()
    
    # 顯示結果
    print("\n" + "=" * 50)
    print("📊 修複結果汇总:")
    print(f"   修複文件: {stats['fixed']}")
    print(f"   跳過文件: {stats['skipped']}")
    print(f"   錯誤文件: {stats['errors']}")
    
    if stats['fixed'] > 0:
        print(f"\n🎉 成功修複 {stats['fixed']} 個文件的日誌導入位置！")
    
    if fixer.errors:
        print(f"\n⚠️ 有 {len(fixer.errors)} 個文件修複失败")
        for error in fixer.errors:
            print(f"   {error}")
    
    # 生成報告
    report = fixer.generate_report()
    report_file = project_root / 'logging_import_fix_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 詳細報告已保存到: {report_file}")


if __name__ == '__main__':
    main()