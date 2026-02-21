"""
比較 requirements.txt 和 pyproject.toml 中的依賴是否一致

確保兩個檔案中聲明的依賴套件保持同步
"""

import re
from pathlib import Path
from typing import Set, Dict

project_root = Path(__file__).parent.parent


def parse_requirements_txt() -> Dict[str, str]:
    """解析 requirements.txt 檔案"""
    requirements_file = project_root / 'requirements.txt'
    packages = {}
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳過註釋和空行
            if not line or line.startswith('#'):
                continue
            
            # 提取包名和版本
            match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', line)
            if match:
                package_name = match.group(1).lower()
                version_spec = match.group(2).strip()
                packages[package_name] = version_spec
    
    return packages


def parse_pyproject_toml() -> Dict[str, str]:
    """解析 pyproject.toml 檔案"""
    pyproject_file = project_root / 'pyproject.toml'
    packages = {}
    
    with open(pyproject_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 dependencies 列表
    in_dependencies = False
    for line in content.split('\n'):
        if 'dependencies = [' in line:
            in_dependencies = True
            continue
        if in_dependencies:
            if ']' in line:
                break
            # 提取包名和版本
            match = re.search(r'"([a-zA-Z0-9_-]+)([^"]*)"', line)
            if match:
                package_name = match.group(1).lower()
                version_spec = match.group(2).strip()
                packages[package_name] = version_spec
    
    return packages


def main():
    """主函數"""
    print("=" * 80)
    print(" 比較 requirements.txt 和 pyproject.toml")
    print("=" * 80)
    
    # 解析兩個檔案
    print("\n 解析 requirements.txt...")
    req_packages = parse_requirements_txt()
    print(f" 發現 {len(req_packages)} 個包")
    
    print("\n 解析 pyproject.toml...")
    pyproject_packages = parse_pyproject_toml()
    print(f" 發現 {len(pyproject_packages)} 個包")
    
    # 比較差異
    print("\n 檢查差異...")
    
    # 在 pyproject.toml 中但不在 requirements.txt 中
    missing_in_req = set(pyproject_packages.keys()) - set(req_packages.keys())
    
    # 在 requirements.txt 中但不在 pyproject.toml 中
    missing_in_pyproject = set(req_packages.keys()) - set(pyproject_packages.keys())
    
    # 版本不一致
    version_mismatch = []
    for package in set(req_packages.keys()) & set(pyproject_packages.keys()):
        if req_packages[package] != pyproject_packages[package]:
            version_mismatch.append((
                package,
                req_packages[package],
                pyproject_packages[package]
            ))
    
    # 輸出結果
    if not missing_in_req and not missing_in_pyproject and not version_mismatch:
        print("\n 兩個檔案完全一致！")
    else:
        if missing_in_req:
            print(f"\n 在 pyproject.toml 中但不在 requirements.txt 中 ({len(missing_in_req)} 個):")
            print("-" * 80)
            for package in sorted(missing_in_req):
                version = pyproject_packages[package]
                print(f"  • {package}{version}")
            print("\n 建議在 requirements.txt 中添加這些包")
        
        if missing_in_pyproject:
            print(f"\n 在 requirements.txt 中但不在 pyproject.toml 中 ({len(missing_in_pyproject)} 個):")
            print("-" * 80)
            for package in sorted(missing_in_pyproject):
                version = req_packages[package]
                print(f"  • {package}{version}")
            print("\n 建議在 pyproject.toml 中添加這些包")
        
        if version_mismatch:
            print(f"\n  版本不一致 ({len(version_mismatch)} 個):")
            print("-" * 80)
            for package, req_ver, pyproject_ver in sorted(version_mismatch):
                print(f"  • {package}")
                print(f"    requirements.txt: {req_ver or '(無版本限制)'}")
                print(f"    pyproject.toml:   {pyproject_ver or '(無版本限制)'}")
    
    # 顯示統計
    print("\n 統計資訊:")
    print("-" * 80)
    print(f"  requirements.txt:  {len(req_packages)} 個包")
    print(f"  pyproject.toml:    {len(pyproject_packages)} 個包")
    print(f"  共同包:            {len(set(req_packages.keys()) & set(pyproject_packages.keys()))} 個")
    print(f"  僅在 req:          {len(missing_in_pyproject)} 個")
    print(f"  僅在 pyproject:    {len(missing_in_req)} 個")
    print(f"  版本不一致:        {len(version_mismatch)} 個")
    
    print("\n" + "=" * 80)
    
    # 返回狀態碼
    if missing_in_req or missing_in_pyproject or version_mismatch:
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

