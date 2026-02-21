#!/usr/bin/env python3
"""
TradingAgents-CN 安裝驗證腳本
用於驗證系統安裝是否正確
"""

import sys
import os
import importlib
from pathlib import Path
from typing import Dict, List, Tuple

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class InstallationTester:
    """安裝驗證測試器"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        
    def test_python_version(self) -> bool:
        """測試Python版本"""
        print("🐍 檢查Python版本...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 10:
            self.results.append(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.errors.append(f"❌ Python版本過低: {version.major}.{version.minor}.{version.micro} (需要3.10+)")
            return False
    
    def test_virtual_environment(self) -> bool:
        """測試虛擬環境"""
        print("🔧 檢查虛擬環境...")
        
        in_venv = (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if in_venv:
            self.results.append("✅ 虛擬環境: 已激活")
            return True
        else:
            self.errors.append("⚠️ 虛擬環境: 未激活 (建議使用虛擬環境)")
            return False
    
    def test_core_modules(self) -> bool:
        """測試核心模塊導入"""
        print("📦 檢查核心模塊...")
        
        core_modules = [
            'tradingagents',
            'tradingagents.config',
            'tradingagents.llm_adapters',
            'tradingagents.agents',
            'tradingagents.dataflows'
        ]
        
        success = True
        for module in core_modules:
            try:
                importlib.import_module(module)
                self.results.append(f"✅ 核心模塊: {module}")
            except ImportError as e:
                self.errors.append(f"❌ 核心模塊導入失敗: {module} - {e}")
                success = False
        
        return success
    
    def test_dependencies(self) -> bool:
        """測試依賴包"""
        print("📚 檢查依賴包...")
        
        dependencies = [
            ('streamlit', 'Web框架'),
            ('pandas', '數據處理'),
            ('numpy', '數值計算'),
            ('requests', 'HTTP請求'),
            ('yfinance', '股票數據'),
            ('openai', 'OpenAI客戶端'),
            ('langchain', 'LangChain框架'),
            ('plotly', '圖表繪製'),
            ('redis', 'Redis客戶端'),
            ('pymongo', 'MongoDB客戶端')
        ]
        
        success = True
        for package, description in dependencies:
            try:
                importlib.import_module(package)
                self.results.append(f"✅ 依賴包: {package} ({description})")
            except ImportError:
                self.errors.append(f"❌ 依賴包缺失: {package} ({description})")
                success = False
        
        return success
    
    def test_config_files(self) -> bool:
        """測試配置文件"""
        print("⚙️ 檢查配置文件...")
        
        config_files = [
            ('VERSION', '版本文件'),
            ('.env.example', '環境變量模板'),
            ('config/settings.json', '設置配置'),
            ('config/models.json', '模型配置'),
            ('config/pricing.json', '價格配置'),
            ('config/logging.toml', '日誌配置')
        ]
        
        success = True
        for file_path, description in config_files:
            full_path = project_root / file_path
            if full_path.exists():
                self.results.append(f"✅ 配置文件: {file_path} ({description})")
            else:
                self.errors.append(f"❌ 配置文件缺失: {file_path} ({description})")
                success = False
        
        return success
    
    def test_environment_variables(self) -> bool:
        """測試環境變量"""
        print("🔑 檢查環境變量...")
        
        # 檢查.env文件
        env_file = project_root / '.env'
        if env_file.exists():
            self.results.append("✅ 環境變量文件: .env 存在")
            
            # 讀取並檢查關鍵配置
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 檢查是否有API密鑰配置
                api_keys = [
                    'OPENAI_API_KEY',
                    'GOOGLE_API_KEY'
                ]
                
                configured_apis = []
                for key in api_keys:
                    if key in content and not content.count(f'{key}=your_') > 0:
                        configured_apis.append(key)
                
                if configured_apis:
                    self.results.append(f"✅ 已配置API: {', '.join(configured_apis)}")
                else:
                    self.errors.append("⚠️ 未發現已配置的API密鑰")
                
            except Exception as e:
                self.errors.append(f"❌ 讀取.env文件失敗: {e}")
                return False
        else:
            self.errors.append("⚠️ 環境變量文件: .env 不存在 (請複制.env.example)")
            return False
        
        return True
    
    def test_web_application(self) -> bool:
        """測試Web應用"""
        print("🌐 檢查Web應用...")
        
        web_files = [
            ('web/app.py', 'Streamlit主應用'),
            ('web/components/sidebar.py', '側邊欄組件'),
            ('start_web.py', '啟動腳本')
        ]
        
        success = True
        for file_path, description in web_files:
            full_path = project_root / file_path
            if full_path.exists():
                self.results.append(f"✅ Web文件: {file_path} ({description})")
            else:
                self.errors.append(f"❌ Web文件缺失: {file_path} ({description})")
                success = False
        
        return success
    
    def test_data_directories(self) -> bool:
        """測試數據目錄"""
        print("📁 檢查數據目錄...")
        
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
                    self.results.append(f"✅ 數據目錄: {dir_path} (已創建)")
                except Exception as e:
                    self.errors.append(f"❌ 創建目錄失敗: {dir_path} - {e}")
                    return False
            else:
                self.results.append(f"✅ 數據目錄: {dir_path} (已存在)")
        
        return True
    
    def run_all_tests(self) -> Dict[str, bool]:
        """運行所有測試"""
        print("🚀 開始安裝驗證測試...")
        print("=" * 60)
        
        tests = [
            ('Python版本', self.test_python_version),
            ('虛擬環境', self.test_virtual_environment),
            ('核心模塊', self.test_core_modules),
            ('依賴包', self.test_dependencies),
            ('配置文件', self.test_config_files),
            ('環境變量', self.test_environment_variables),
            ('Web應用', self.test_web_application),
            ('數據目錄', self.test_data_directories)
        ]
        
        test_results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                test_results[test_name] = result
                print()
            except Exception as e:
                self.errors.append(f"❌ 測試異常: {test_name} - {e}")
                test_results[test_name] = False
                print()
        
        return test_results
    
    def print_summary(self, test_results: Dict[str, bool]):
        """打印測試總結"""
        print("=" * 60)
        print("📊 測試總結")
        print("=" * 60)
        
        # 成功的測試
        if self.results:
            print("\n✅ 成功項目:")
            for result in self.results:
                print(f"  {result}")
        
        # 失敗的測試
        if self.errors:
            print("\n❌ 問題項目:")
            for error in self.errors:
                print(f"  {error}")
        
        # 總體狀態
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())

        print(f"\n📈 測試統計:")
        print(f"  總測試數: {total_tests}")
        print(f"  通過測試: {passed_tests}")
        print(f"  失敗測試: {total_tests - passed_tests}")
        print(f"  成功率: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 恭喜！安裝驗證全部通過！")
            print("   你可以開始使用TradingAgents-CN了！")
            print("   運行: python start_web.py")
        else:
            print("\n⚠️ 安裝驗證發現問題，請根據上述錯誤資訊進行修復。")
            print("   參考文件: docs/guides/installation-guide.md")

def main():
    """主函數"""
    tester = InstallationTester()
    test_results = tester.run_all_tests()
    tester.print_summary(test_results)
    
    # 返回退出碼
    if all(test_results.values()):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
