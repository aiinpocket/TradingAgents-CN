#!/usr/bin/env python3
"""
TradingAgents-CN 

"""

import sys
import os
import importlib
from pathlib import Path
from typing import Dict, List, Tuple

# 
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class InstallationTester:
    """"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        
    def test_python_version(self) -> bool:
        """Python"""
        print(" Python...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 10:
            self.results.append(f" Python: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.errors.append(f" Python: {version.major}.{version.minor}.{version.micro} (3.10+)")
            return False
    
    def test_virtual_environment(self) -> bool:
        """"""
        print(" ...")
        
        in_venv = (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if in_venv:
            self.results.append(" : ")
            return True
        else:
            self.errors.append(" :  ()")
            return False
    
    def test_core_modules(self) -> bool:
        """"""
        print(" ...")
        
        core_modules = [
            'tradingagents',
            'tradingagents.config',
            'tradingagents.agents',
            'tradingagents.dataflows'
        ]
        
        success = True
        for module in core_modules:
            try:
                importlib.import_module(module)
                self.results.append(f" : {module}")
            except ImportError as e:
                self.errors.append(f" : {module} - {e}")
                success = False
        
        return success
    
    def test_dependencies(self) -> bool:
        """"""
        print(" ...")
        
        dependencies = [
            ('streamlit', 'Web'),
            ('pandas', ''),
            ('numpy', ''),
            ('requests', 'HTTP'),
            ('yfinance', ''),
            ('openai', 'OpenAI'),
            ('langchain', 'LangChain'),
            ('plotly', ''),
            ('redis', 'Redis'),
            ('pymongo', 'MongoDB')
        ]
        
        success = True
        for package, description in dependencies:
            try:
                importlib.import_module(package)
                self.results.append(f" : {package} ({description})")
            except ImportError:
                self.errors.append(f" : {package} ({description})")
                success = False
        
        return success
    
    def test_config_files(self) -> bool:
        """"""
        print(" ...")
        
        config_files = [
            ('VERSION', ''),
            ('.env.example', ''),
            ('config/settings.json', ''),
            ('config/models.json', ''),
            ('config/pricing.json', ''),
            ('config/logging.toml', '')
        ]
        
        success = True
        for file_path, description in config_files:
            full_path = project_root / file_path
            if full_path.exists():
                self.results.append(f" : {file_path} ({description})")
            else:
                self.errors.append(f" : {file_path} ({description})")
                success = False
        
        return success
    
    def test_environment_variables(self) -> bool:
        """"""
        print(" ...")
        
        # .env
        env_file = project_root / '.env'
        if env_file.exists():
            self.results.append(" : .env ")
            
            # 
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # API
                api_keys = [
                    'OPENAI_API_KEY',
                    'ANTHROPIC_API_KEY'
                ]
                
                configured_apis = []
                for key in api_keys:
                    if key in content and not content.count(f'{key}=your_') > 0:
                        configured_apis.append(key)
                
                if configured_apis:
                    self.results.append(f" API: {', '.join(configured_apis)}")
                else:
                    self.errors.append(" API")
                
            except Exception as e:
                self.errors.append(f" .env: {e}")
                return False
        else:
            self.errors.append(" : .env  (.env.example)")
            return False
        
        return True
    
    def test_web_application(self) -> bool:
        """Web"""
        print(" Web...")
        
        web_files = [
            ('web/app.py', 'Streamlit'),
            ('web/components/sidebar.py', ''),
            ('start_web.py', '')
        ]
        
        success = True
        for file_path, description in web_files:
            full_path = project_root / file_path
            if full_path.exists():
                self.results.append(f" Web: {file_path} ({description})")
            else:
                self.errors.append(f" Web: {file_path} ({description})")
                success = False
        
        return success
    
    def test_data_directories(self) -> bool:
        """"""
        print(" ...")
        
        data_dirs = [
            'data',
            'data/cache',
            'logs'
        ]
        
        for dir_path in data_dirs:
            full_path = project_root / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.results.append(f" : {dir_path} ()")
                except Exception as e:
                    self.errors.append(f" : {dir_path} - {e}")
                    return False
            else:
                self.results.append(f" : {dir_path} ()")
        
        return True
    
    def run_all_tests(self) -> Dict[str, bool]:
        """"""
        print(" ...")
        print("=" * 60)
        
        tests = [
            ('Python', self.test_python_version),
            ('', self.test_virtual_environment),
            ('', self.test_core_modules),
            ('', self.test_dependencies),
            ('', self.test_config_files),
            ('', self.test_environment_variables),
            ('Web', self.test_web_application),
            ('', self.test_data_directories)
        ]
        
        test_results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                test_results[test_name] = result
                print()
            except Exception as e:
                self.errors.append(f" : {test_name} - {e}")
                test_results[test_name] = False
                print()
        
        return test_results
    
    def print_summary(self, test_results: Dict[str, bool]):
        """"""
        print("=" * 60)
        print(" ")
        print("=" * 60)
        
        # 
        if self.results:
            print("\n :")
            for result in self.results:
                print(f"  {result}")
        
        # 
        if self.errors:
            print("\n :")
            for error in self.errors:
                print(f"  {error}")
        
        # 
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())

        print(f"\n :")
        print(f"  : {total_tests}")
        print(f"  : {passed_tests}")
        print(f"  : {total_tests - passed_tests}")
        print(f"  : {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n ")
            print("   TradingAgents-CN")
            print("   : python start_web.py")
        else:
            print("\n ")
            print("   : docs/guides/installation-guide.md")

def main():
    """"""
    tester = InstallationTester()
    test_results = tester.run_all_tests()
    tester.print_summary(test_results)
    
    # 
    if all(test_results.values()):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
