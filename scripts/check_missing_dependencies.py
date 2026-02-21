"""
檢查 pyproject.toml 中缺失的依賴包

掃描代碼中實際使用的第三方包，與 pyproject.toml 中聲明的依賴進行對比
"""

import os
import re
import sys
from pathlib import Path
from typing import Set

# 項目根目錄
project_root = Path(__file__).parent.parent

# 標準庫模塊（Python 3.10）
STDLIB_MODULES = {
    'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
    'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins',
    'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
    'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
    'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv',
    'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
    'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
    'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions', 'ftplib',
    'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp',
    'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp',
    'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword',
    'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap',
    'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib', 'msvcrt',
    'multiprocessing', 'netrc', 'nis', 'nntplib', 'numbers', 'operator', 'optparse',
    'os', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes',
    'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint',
    'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue',
    'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter',
    'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil',
    'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd',
    'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct',
    'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog',
    'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap',
    'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace', 'traceback',
    'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'typing_extensions',
    'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave',
    'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml',
    'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', '__future__', '__main__',
}

# 項目內部模塊（包括子模塊和組件）
INTERNAL_MODULES = {
    'tradingagents', 'web', 'cli', 'app', 'tests', 'scripts', 'examples',
    'auth_manager', 'components', 'modules', 'utils',  # web/ 下的內部模塊
    'stock_data_service',  # 內部服務模組
}

# 已知的包名映射（import 名稱 -> PyPI 包名）
PACKAGE_NAME_MAPPING = {
    'bs4': 'beautifulsoup4',
    'cv2': 'opencv-python',
    'PIL': 'Pillow',
    'sklearn': 'scikit-learn',
    'yaml': 'pyyaml',
    'dotenv': 'python-dotenv',
    'langchain_openai': 'langchain-openai',
    'langchain_anthropic': 'langchain-anthropic',
    'langchain_google_genai': 'langchain-google-genai',
    'langchain_experimental': 'langchain-experimental',
    'google': 'google-generativeai',  # 可能是多個包
    'dateutil': 'python-dateutil',
    'finnhub': 'finnhub-python',
}


def extract_imports_from_file(file_path: Path) -> Set[str]:
    """從 Python 文件中提取導入的包名"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # 匹配 import xxx
        for match in re.finditer(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE):
            imports.add(match.group(1))
        
        # 匹配 from xxx import
        for match in re.finditer(r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE):
            imports.add(match.group(1))
            
    except Exception as e:
        print(f"⚠️  讀取文件失敗 {file_path}: {e}")
    
    return imports


def scan_directory(directory: Path) -> Set[str]:
    """掃描目錄中所有 Python 文件的導入"""
    all_imports = set()
    
    for py_file in directory.rglob('*.py'):
        # 跳過一些目錄
        if any(part in py_file.parts for part in ['.venv', 'env', '__pycache__', '.git', 'node_modules']):
            continue
        
        imports = extract_imports_from_file(py_file)
        all_imports.update(imports)
    
    return all_imports


def get_declared_dependencies() -> Set[str]:
    """從 pyproject.toml 中獲取已聲明的依賴"""
    pyproject_file = project_root / 'pyproject.toml'
    dependencies = set()
    
    try:
        with open(pyproject_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 dependencies 列表中的包名
        in_dependencies = False
        for line in content.split('\n'):
            if 'dependencies = [' in line:
                in_dependencies = True
                continue
            if in_dependencies:
                if ']' in line:
                    break
                # 提取包名（去除版本號）
                match = re.search(r'"([a-zA-Z0-9_-]+)', line)
                if match:
                    dependencies.add(match.group(1).lower())
    
    except Exception as e:
        print(f"❌ 讀取 pyproject.toml 失敗: {e}")
    
    return dependencies


def normalize_package_name(import_name: str) -> str:
    """標準化包名"""
    # 使用映射表
    if import_name in PACKAGE_NAME_MAPPING:
        return PACKAGE_NAME_MAPPING[import_name]
    
    # 默認轉小寫並替換下劃線為連字符
    return import_name.lower().replace('_', '-')


def main():
    """主函數"""
    print("=" * 80)
    print("🔍 檢查 pyproject.toml 中缺失的依賴包")
    print("=" * 80)
    
    # 掃描代碼中的導入
    print("\n📂 掃描代碼目錄...")
    directories_to_scan = [
        project_root / 'tradingagents',
        project_root / 'web',
        project_root / 'cli',
    ]
    
    all_imports = set()
    for directory in directories_to_scan:
        if directory.exists():
            print(f"   掃描: {directory.relative_to(project_root)}")
            imports = scan_directory(directory)
            all_imports.update(imports)
    
    # 過濾掉標準庫和內部模塊
    third_party_imports = {
        imp for imp in all_imports
        if imp not in STDLIB_MODULES and imp not in INTERNAL_MODULES
    }
    
    print(f"\n✅ 發現 {len(third_party_imports)} 個第三方包導入")
    
    # 獲取已聲明的依賴
    print("\n📋 讀取 pyproject.toml 中的依賴...")
    declared_deps = get_declared_dependencies()
    print(f"✅ pyproject.toml 中聲明了 {len(declared_deps)} 個依賴")
    
    # 查找缺失的依賴
    print("\n🔎 檢查缺失的依賴...")
    missing_deps = set()
    
    for import_name in sorted(third_party_imports):
        package_name = normalize_package_name(import_name)
        
        # 檢查是否在已聲明的依賴中
        if package_name not in declared_deps:
            # 也檢查原始名稱
            if import_name.lower() not in declared_deps:
                missing_deps.add((import_name, package_name))
    
    # 輸出結果
    if missing_deps:
        print(f"\n❌ 發現 {len(missing_deps)} 個可能缺失的依賴:")
        print("-" * 80)
        for import_name, package_name in sorted(missing_deps):
            print(f"  • {import_name:25s} → 建議添加: {package_name}")
        
        print("\n💡 建議在 pyproject.toml 的 dependencies 中添加:")
        print("-" * 80)
        for import_name, package_name in sorted(missing_deps):
            print(f'    "{package_name}",')
    else:
        print("\n✅ 所有第三方包都已在 pyproject.toml 中聲明！")
    
    # 顯示所有發現的第三方導入
    print("\n📦 所有第三方包導入列表:")
    print("-" * 80)
    for imp in sorted(third_party_imports):
        status = "✅" if normalize_package_name(imp) in declared_deps or imp.lower() in declared_deps else "❌"
        print(f"  {status} {imp}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

