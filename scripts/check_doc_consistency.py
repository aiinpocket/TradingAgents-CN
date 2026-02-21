#!/usr/bin/env python3
"""
檔案一致性檢查指令碼
檢查檔案與代碼的一致性，確保檔案內容準確反映實際實現
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import ast
import importlib.util

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DocumentationChecker:
    """檔案一致性檢查器"""
    
    def __init__(self):
        self.project_root = project_root
        self.docs_dir = self.project_root / "docs"
        self.code_dir = self.project_root / "tradingagents"
        self.issues = []
        
    def check_all(self) -> Dict[str, List[str]]:
        """執行所有檢查"""
        print(" 開始檔案一致性檢查...")
        
        results = {
            "version_consistency": self.check_version_consistency(),
            "agent_architecture": self.check_agent_architecture(),
            "code_examples": self.check_code_examples(),
            "api_references": self.check_api_references(),
            "file_existence": self.check_file_existence()
        }
        
        return results
    
    def check_version_consistency(self) -> List[str]:
        """檢查版本一致性"""
        print(" 檢查版本一致性...")
        issues = []
        
        # 讀取項目版本
        version_file = self.project_root / "VERSION"
        if not version_file.exists():
            issues.append(" VERSION 檔案不存在")
            return issues
            
        project_version = version_file.read_text().strip()
        print(f"   項目版本: {project_version}")
        
        # 檢查檔案中的版本資訊
        doc_files = list(self.docs_dir.rglob("*.md"))
        for doc_file in doc_files:
            try:
                content = doc_file.read_text(encoding='utf-8')
                
                # 檢查是否有版本頭部
                if content.startswith("---"):
                    # 解析YAML頭部
                    yaml_end = content.find("---", 3)
                    if yaml_end > 0:
                        yaml_content = content[3:yaml_end]
                        
                        # 檢查版本字段
                        version_match = re.search(r'version:\s*(.+)', yaml_content)
                        if version_match:
                            doc_version = version_match.group(1).strip()
                            if doc_version != project_version:
                                issues.append(f" {doc_file.relative_to(self.project_root)}: 版本不一致 (檔案: {doc_version}, 項目: {project_version})")
                        else:
                            issues.append(f" {doc_file.relative_to(self.project_root)}: 缺少版本資訊")
                else:
                    # 核心檔案應該有版本頭部
                    if any(keyword in str(doc_file) for keyword in ["agents", "architecture", "development"]):
                        issues.append(f" {doc_file.relative_to(self.project_root)}: 缺少版本頭部")
                        
            except Exception as e:
                issues.append(f" 讀取檔案失敗 {doc_file}: {e}")
        
        return issues
    
    def check_agent_architecture(self) -> List[str]:
        """檢查智慧體架構描述的一致性"""
        print(" 檢查智慧體架構一致性...")
        issues = []
        
        # 檢查實際的智慧體實現
        agents_code_dir = self.code_dir / "agents"
        if not agents_code_dir.exists():
            issues.append(" 智慧體程式碼目錄不存在")
            return issues
        
        # 取得實際的智慧體列表
        actual_agents = {}
        for category in ["analysts", "researchers", "managers", "trader", "risk_mgmt"]:
            category_dir = agents_code_dir / category
            if category_dir.exists():
                actual_agents[category] = []
                for py_file in category_dir.glob("*.py"):
                    if py_file.name != "__init__.py":
                        actual_agents[category].append(py_file.stem)
        
        print(f"   發現的智慧體: {actual_agents}")
        
        # 檢查檔案中的智慧體描述
        agents_doc_dir = self.docs_dir / "agents"
        if agents_doc_dir.exists():
            for doc_file in agents_doc_dir.glob("*.md"):
                try:
                    content = doc_file.read_text(encoding='utf-8')
                    
                    # 檢查是否提到了BaseAnalyst類（應該已經移除）
                    if "class BaseAnalyst" in content:
                        issues.append(f" {doc_file.name}: 仍然提到BaseAnalyst類，應該更新為函式式架構")
                    
                    # 檢查是否提到了create_*_analyst函式
                    if "create_" in content and "analyst" in content:
                        if "def create_" not in content:
                            issues.append(f" {doc_file.name}: 提到create函式但沒有正確的函式簽名")
                    
                except Exception as e:
                    issues.append(f" 讀取智慧體檔案失敗 {doc_file}: {e}")
        
        return issues
    
    def check_code_examples(self) -> List[str]:
        """檢查檔案中的代碼示例"""
        print(" 檢查代碼示例...")
        issues = []
        
        doc_files = list(self.docs_dir.rglob("*.md"))
        for doc_file in doc_files:
            try:
                content = doc_file.read_text(encoding='utf-8')
                
                # 提取Python代碼塊
                python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
                
                for i, code_block in enumerate(python_blocks):
                    # 基本語法檢查
                    try:
                        # 簡單的語法檢查
                        ast.parse(code_block)
                    except SyntaxError as e:
                        issues.append(f" {doc_file.relative_to(self.project_root)} 代碼塊 {i+1}: 語法錯誤 - {e}")
                    
                    # 檢查是否使用了已廢棄的類
                    if "BaseAnalyst" in code_block:
                        issues.append(f" {doc_file.relative_to(self.project_root)} 代碼塊 {i+1}: 使用了已廢棄的BaseAnalyst類")
                    
                    # 檢查匯入語句的正確性
                    import_lines = [line.strip() for line in code_block.split('\n') if line.strip().startswith('from tradingagents')]
                    for import_line in import_lines:
                        # 簡單檢查模組路徑是否存在
                        if 'from tradingagents.agents.analysts.base_analyst' in import_line:
                            issues.append(f" {doc_file.relative_to(self.project_root)} 代碼塊 {i+1}: 匯入不存在的base_analyst模組")
                
            except Exception as e:
                issues.append(f" 檢查代碼示例失敗 {doc_file}: {e}")
        
        return issues
    
    def check_api_references(self) -> List[str]:
        """檢查API參考檔案"""
        print(" 檢查API參考...")
        issues = []
        
        # 檢查是否有API參考檔案
        api_ref_dir = self.docs_dir / "reference"
        if not api_ref_dir.exists():
            issues.append(" 缺少API參考檔案目錄")
            return issues
        
        # 檢查智慧體API檔案
        agents_ref = api_ref_dir / "agents"
        if not agents_ref.exists():
            issues.append(" 缺少智慧體API參考檔案")
        
        return issues
    
    def check_file_existence(self) -> List[str]:
        """檢查檔案中引用的檔案是否存在"""
        print(" 檢查檔案引用...")
        issues = []
        
        doc_files = list(self.docs_dir.rglob("*.md"))
        for doc_file in doc_files:
            try:
                content = doc_file.read_text(encoding='utf-8')
                
                # 檢查相對路徑引用
                relative_refs = re.findall(r'\[.*?\]\(([^)]+)\)', content)
                for ref in relative_refs:
                    if ref.startswith(('http', 'https', 'mailto')):
                        continue
                    
                    # 解析相對路徑
                    ref_path = doc_file.parent / ref
                    if not ref_path.exists():
                        issues.append(f" {doc_file.relative_to(self.project_root)}: 引用的檔案不存在 - {ref}")
                
            except Exception as e:
                issues.append(f" 檢查檔案引用失敗 {doc_file}: {e}")
        
        return issues
    
    def generate_report(self, results: Dict[str, List[str]]) -> str:
        """生成檢查報告"""
        report = ["# 檔案一致性檢查報告\n"]
        report.append(f"**檢查時間**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        total_issues = sum(len(issues) for issues in results.values())
        report.append(f"**總問題數**: {total_issues}\n")
        
        for category, issues in results.items():
            report.append(f"## {category.replace('_', ' ').title()}\n")
            
            if not issues:
                report.append(" 無問題發現\n")
            else:
                for issue in issues:
                    report.append(f"- {issue}")
                report.append("")
        
        return "\n".join(report)

def main():
    """主函式"""
    checker = DocumentationChecker()
    results = checker.check_all()
    
    # 生成報告
    report = checker.generate_report(results)
    
    # 保存報告
    report_file = checker.project_root / "docs" / "CONSISTENCY_CHECK_REPORT.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"\n 檢查完成！報告已保存到: {report_file}")
    print(f"總問題數: {sum(len(issues) for issues in results.values())}")
    
    # 如果有嚴重問題，返回非零退出碼
    critical_issues = sum(1 for issues in results.values() for issue in issues if issue.startswith(""))
    if critical_issues > 0:
        print(f" 發現 {critical_issues} 個嚴重問題，建議立即修復")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
