#!/usr/bin/env python3
"""
批量更新檔案腳本
為所有核心檔案添加版本資訊頭部，修復常見問題
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DocumentationUpdater:
    """檔案批量更新器"""
    
    def __init__(self):
        self.project_root = project_root
        self.docs_dir = self.project_root / "docs"
        
        # 讀取當前版本
        version_file = self.project_root / "VERSION"
        if version_file.exists():
            self.current_version = version_file.read_text().strip()
        else:
            self.current_version = "cn-0.1.13-preview"
        
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 需要添加版本頭部的核心檔案
        self.core_docs = [
            "agents/managers.md",
            "agents/researchers.md", 
            "agents/risk-management.md",
            "agents/trader.md",
            "architecture/agent-architecture.md",
            "architecture/data-flow-architecture.md",
            "architecture/system-architecture.md",
            "development/CONTRIBUTING.md",
            "development/development-workflow.md"
        ]
    
    def create_version_header(self, status: str = "待更新") -> str:
        """創建版本資訊頭部"""
        return f"""---
version: {self.current_version}
last_updated: {self.current_date}
code_compatibility: {self.current_version}
status: {status}
---

"""
    
    def add_version_headers(self) -> List[str]:
        """為核心檔案添加版本頭部"""
        print(" 為核心檔案添加版本頭部...")
        updated_files = []
        
        for doc_path in self.core_docs:
            full_path = self.docs_dir / doc_path
            if not full_path.exists():
                print(f"    檔案不存在: {doc_path}")
                continue
            
            try:
                content = full_path.read_text(encoding='utf-8')
                
                # 檢查是否已有版本頭部
                if content.startswith("---"):
                    print(f"    已有版本頭部: {doc_path}")
                    continue
                
                # 添加版本頭部
                new_content = self.create_version_header() + content
                full_path.write_text(new_content, encoding='utf-8')
                updated_files.append(doc_path)
                print(f"    已更新: {doc_path}")
                
            except Exception as e:
                print(f"    更新失敗 {doc_path}: {e}")
        
        return updated_files
    
    def fix_code_blocks(self) -> List[str]:
        """修復檔案中的代碼塊問題"""
        print(" 修復代碼塊問題...")
        fixed_files = []
        
        # 查找所有markdown檔案
        md_files = list(self.docs_dir.rglob("*.md"))
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                original_content = content
                
                # 修復常見的代碼塊問題
                
                # 1. 修復中文冒號
                content = re.sub(r'：', ':', content)
                
                # 2. 修復箭頭符號（在代碼塊中）
                content = re.sub(r'→', '->', content)
                
                # 3. 修復BaseAnalyst引用（在代碼塊外的說明中）
                if "BaseAnalyst" in content and "已廢棄" not in content:
                    # 在提到BaseAnalyst的地方添加廢棄說明
                    content = re.sub(
                        r'BaseAnalyst',
                        'BaseAnalyst (已廢棄，現使用函數式架構)',
                        content
                    )
                
                # 4. 修復不完整的代碼塊
                # 查找以```python開始但沒有正確結束的代碼塊
                python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
                for block in python_blocks:
                    if block.strip().endswith(':') and not block.strip().endswith('"""'):
                        # 不完整的函數定義，添加pass
                        fixed_block = block + '\n    pass'
                        content = content.replace(f'```python\n{block}\n```', f'```python\n{fixed_block}\n```')
                
                # 如果內容有變化，保存檔案
                if content != original_content:
                    md_file.write_text(content, encoding='utf-8')
                    fixed_files.append(str(md_file.relative_to(self.project_root)))
                    print(f"    已修復: {md_file.relative_to(self.project_root)}")
                
            except Exception as e:
                print(f"    修復失敗 {md_file}: {e}")
        
        return fixed_files
    
    def update_status_tracking(self, updated_files: List[str], fixed_files: List[str]):
        """更新檔案狀態追蹤"""
        print(" 更新檔案狀態追蹤...")
        
        status_file = self.docs_dir / "DOCUMENTATION_STATUS.md"
        if not status_file.exists():
            print("    狀態追蹤檔案不存在")
            return
        
        try:
            content = status_file.read_text(encoding='utf-8')
            
            # 更新最後更新時間
            content = re.sub(
                r'> \*\*最後更新\*\*: \d{4}-\d{2}-\d{2}',
                f'> **最後更新**: {self.current_date}',
                content
            )
            
            # 在檔案末尾添加更新記錄
            update_record = f"""
## 最新更新記錄

### {self.current_date} 批量更新
-  為 {len(updated_files)} 個核心檔案添加了版本頭部
-  修復了 {len(fixed_files)} 個檔案的代碼塊問題
-  更新了檔案狀態追蹤

**更新的檔案:**
{chr(10).join(f'- {file}' for file in updated_files)}

**修復的檔案:**
{chr(10).join(f'- {file}' for file in fixed_files)}
"""
            
            content += update_record
            status_file.write_text(content, encoding='utf-8')
            print("    狀態追蹤已更新")
            
        except Exception as e:
            print(f"    更新狀態追蹤失敗: {e}")
    
    def generate_summary_report(self, updated_files: List[str], fixed_files: List[str]) -> str:
        """生成更新摘要報告"""
        report = f"""# 檔案批量更新報告

**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**項目版本**: {self.current_version}

## 更新摘要

-  添加版本頭部: {len(updated_files)} 個檔案
-  修復代碼塊問題: {len(fixed_files)} 個檔案
-  更新狀態追蹤: 1 個檔案

## 詳細更新列表

### 添加版本頭部的檔案
{chr(10).join(f'-  {file}' for file in updated_files) if updated_files else '- 無'}

### 修復代碼塊的檔案  
{chr(10).join(f'-  {file}' for file in fixed_files) if fixed_files else '- 無'}

## 下一步建議

1. **繼續更新其他檔案**: 還有更多檔案需要添加版本頭部
2. **驗證代碼示例**: 檢查修復後的代碼塊是否正確
3. **更新API參考**: 創建或更新API參考檔案
4. **建立定期檢查**: 設定定期的檔案一致性檢查

## 質量檢查

建議執行以下命令驗證更新效果：
```bash
python scripts/check_doc_consistency.py
```

---
*此報告由批量更新腳本自動生成*
"""
        return report

def main():
    """主函數"""
    print(" 開始批量更新檔案...")
    
    updater = DocumentationUpdater()
    
    # 1. 添加版本頭部
    updated_files = updater.add_version_headers()
    
    # 2. 修復代碼塊問題
    fixed_files = updater.fix_code_blocks()
    
    # 3. 更新狀態追蹤
    updater.update_status_tracking(updated_files, fixed_files)
    
    # 4. 生成摘要報告
    report = updater.generate_summary_report(updated_files, fixed_files)
    report_file = updater.project_root / "docs" / "BATCH_UPDATE_REPORT.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"\n 批量更新完成！")
    print(f"    添加版本頭部: {len(updated_files)} 個檔案")
    print(f"    修復代碼塊: {len(fixed_files)} 個檔案")
    print(f"    報告已保存到: {report_file}")
    
    print(f"\n 建議執行以下命令驗證更新效果:")
    print(f"   python scripts/check_doc_consistency.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
