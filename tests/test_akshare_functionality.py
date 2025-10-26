#!/usr/bin/env python3
"""
AKShare功能檢查測試
檢查當前分支中AKShare的可用性和功能完整性
"""

import sys
import os
import traceback
from typing import Dict, Any, List

def test_akshare_import():
    """測試AKShare庫導入"""
    print("🔍 測試AKShare庫導入...")
    try:
        import akshare as ak
        print(f"✅ AKShare導入成功，版本: {ak.__version__}")
        return True, ak
    except ImportError as e:
        print(f"❌ AKShare導入失败: {e}")
        return False, None

def test_data_source_manager():
    """測試數據源管理器中的AKShare支持"""
    print("\n🔍 測試數據源管理器...")
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        # 檢查AKShare是否在枚举中
        akshare_enum = ChinaDataSource.AKSHARE
        print(f"✅ AKShare枚举存在: {akshare_enum.value}")
        
        # 初始化數據源管理器
        manager = DataSourceManager()
        
        # 檢查AKShare是否在可用數據源中
        available_sources = [s.value for s in manager.available_sources]
        if 'akshare' in available_sources:
            print("✅ AKShare在可用數據源列表中")
        else:
            print("⚠️ AKShare不在可用數據源列表中")
        
        return True, manager
    except Exception as e:
        print(f"❌ 數據源管理器測試失败: {e}")
        traceback.print_exc()
        return False, None

def test_akshare_adapter():
    """測試AKShare適配器"""
    print("\n🔍 測試AKShare適配器...")
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        
        manager = DataSourceManager()
        
        # 嘗試獲取AKShare適配器
        akshare_adapter = manager._get_akshare_adapter()
        
        if akshare_adapter is not None:
            print("✅ AKShare適配器獲取成功")
            return True, akshare_adapter
        else:
            print("❌ AKShare適配器獲取失败")
            return False, None
            
    except Exception as e:
        print(f"❌ AKShare適配器測試失败: {e}")
        traceback.print_exc()
        return False, None

def test_akshare_utils_file():
    """檢查akshare_utils.py文件是否存在"""
    print("\n🔍 檢查akshare_utils.py文件...")
    
    akshare_utils_path = "tradingagents/dataflows/akshare_utils.py"
    
    if os.path.exists(akshare_utils_path):
        print(f"✅ 找到AKShare工具文件: {akshare_utils_path}")
        
        try:
            from tradingagents.dataflows.akshare_utils import get_akshare_provider
            print("✅ get_akshare_provider函數導入成功")
            return True
        except ImportError as e:
            print(f"❌ 導入get_akshare_provider失败: {e}")
            return False
    else:
        print(f"❌ AKShare工具文件不存在: {akshare_utils_path}")
        return False

def test_akshare_basic_functionality():
    """測試AKShare基本功能"""
    print("\n🔍 測試AKShare基本功能...")
    
    success, ak = test_akshare_import()
    if not success:
        return False
    
    try:
        # 測試獲取股票列表
        print("📊 測試獲取A股股票列表...")
        stock_list = ak.stock_info_a_code_name()
        if stock_list is not None and not stock_list.empty:
            print(f"✅ 獲取股票列表成功，共{len(stock_list)}只股票")
            print(f"   示例: {stock_list.head(3).to_dict('records')}")
        else:
            print("❌ 獲取股票列表失败")
            return False
        
        # 測試獲取股票歷史數據
        print("\n📈 測試獲取股票歷史數據...")
        stock_data = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20241201", end_date="20241210", adjust="")
        if stock_data is not None and not stock_data.empty:
            print(f"✅ 獲取股票數據成功，共{len(stock_data)}條記錄")
            print(f"   最新數據: {stock_data.tail(1).to_dict('records')}")
        else:
            print("❌ 獲取股票數據失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AKShare基本功能測試失败: {e}")
        traceback.print_exc()
        return False

def test_data_source_switching():
    """測試數據源切換功能"""
    print("\n🔍 測試數據源切換功能...")
    
    try:
        from tradingagents.dataflows.interface import switch_china_data_source
        
        # 嘗試切換到AKShare
        result = switch_china_data_source("akshare")
        print(f"切換結果: {result}")
        
        if "成功" in result or "✅" in result:
            print("✅ 數據源切換到AKShare成功")
            return True
        else:
            print("❌ 數據源切換到AKShare失败")
            return False
            
    except Exception as e:
        print(f"❌ 數據源切換測試失败: {e}")
        traceback.print_exc()
        return False

def test_unified_data_interface():
    """測試統一數據接口"""
    print("\n🔍 測試統一數據接口...")
    
    try:
        from tradingagents.dataflows.interface import get_china_stock_data_unified
        
        # 設置使用AKShare數據源
        from tradingagents.dataflows.interface import switch_china_data_source
        switch_china_data_source("akshare")
        
        # 測試獲取股票數據
        data = get_china_stock_data_unified("000001", "2024-12-01", "2024-12-10")
        
        if data and "股票代碼" in data:
            print("✅ 統一數據接口測試成功")
            print(f"   數據預覽: {data[:200]}...")
            return True
        else:
            print("❌ 統一數據接口測試失败")
            return False
            
    except Exception as e:
        print(f"❌ 統一數據接口測試失败: {e}")
        traceback.print_exc()
        return False

def create_missing_akshare_utils():
    """如果缺失，創建基本的akshare_utils.py文件"""
    print("\n🔧 檢查是否需要創建akshare_utils.py...")
    
    akshare_utils_path = "tradingagents/dataflows/akshare_utils.py"
    
    if not os.path.exists(akshare_utils_path):
        print("📝 創建基本的akshare_utils.py文件...")
        
        akshare_utils_content = '''#!/usr/bin/env python3
"""
AKShare數據源工具
提供AKShare數據獲取的統一接口
"""

import pandas as pd
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class AKShareProvider:
    """AKShare數據提供器"""
    
    def __init__(self):
        """初始化AKShare提供器"""
        try:
            import akshare as ak
            self.ak = ak
            self.connected = True
            print("✅ AKShare初始化成功")
        except ImportError:
            self.ak = None
            self.connected = False
            print("❌ AKShare未安裝")
    
    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """獲取股票歷史數據"""
        if not self.connected:
            return None
        
        try:
            # 轉換股票代碼格式
            if len(symbol) == 6:
                symbol = symbol
            else:
                symbol = symbol.replace('.SZ', '').replace('.SS', '')
            
            # 獲取數據
            data = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace('-', '') if start_date else "20240101",
                end_date=end_date.replace('-', '') if end_date else "20241231",
                adjust=""
            )
            
            return data
            
        except Exception as e:
            print(f"❌ AKShare獲取股票數據失败: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """獲取股票基本信息"""
        if not self.connected:
            return {}
        
        try:
            # 獲取股票基本信息
            stock_list = self.ak.stock_info_a_code_name()
            stock_info = stock_list[stock_list['code'] == symbol]
            
            if not stock_info.empty:
                return {
                    'symbol': symbol,
                    'name': stock_info.iloc[0]['name'],
                    'source': 'akshare'
                }
            else:
                return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'akshare'}
                
        except Exception as e:
            print(f"❌ AKShare獲取股票信息失败: {e}")
            return {'symbol': symbol, 'name': f'股票{symbol}', 'source': 'akshare'}

def get_akshare_provider() -> AKShareProvider:
    """獲取AKShare提供器實例"""
    return AKShareProvider()
'''
        
        try:
            with open(akshare_utils_path, 'w', encoding='utf-8') as f:
                f.write(akshare_utils_content)
            print(f"✅ 創建akshare_utils.py成功: {akshare_utils_path}")
            return True
        except Exception as e:
            print(f"❌ 創建akshare_utils.py失败: {e}")
            return False
    else:
        print("✅ akshare_utils.py文件已存在")
        return True

def main():
    """主測試函數"""
    print("🔍 AKShare功能完整性檢查")
    print("=" * 60)
    
    test_results = {}
    
    # 1. 測試AKShare庫導入
    test_results['akshare_import'] = test_akshare_import()[0]
    
    # 2. 檢查akshare_utils.py文件
    test_results['akshare_utils_file'] = test_akshare_utils_file()
    
    # 3. 如果文件不存在，嘗試創建
    if not test_results['akshare_utils_file']:
        test_results['create_akshare_utils'] = create_missing_akshare_utils()
    
    # 4. 測試數據源管理器
    test_results['data_source_manager'] = test_data_source_manager()[0]
    
    # 5. 測試AKShare適配器
    test_results['akshare_adapter'] = test_akshare_adapter()[0]
    
    # 6. 測試AKShare基本功能
    test_results['akshare_basic'] = test_akshare_basic_functionality()
    
    # 7. 測試數據源切換
    test_results['data_source_switching'] = test_data_source_switching()
    
    # 8. 測試統一數據接口
    test_results['unified_interface'] = test_unified_data_interface()
    
    # 总結結果
    print(f"\n📊 AKShare功能檢查总結")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name:25} {status}")
    
    print(f"\n🎯 总體結果: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 AKShare功能完全可用！")
    elif passed >= total * 0.7:
        print("⚠️ AKShare功能基本可用，但有部分問題需要修複")
    else:
        print("❌ AKShare功能存在嚴重問題，需要修複")
    
    return passed == total

if __name__ == "__main__":
    main()
