#!/usr/bin/env python3
"""
修複版AKShare功能檢查
添加路徑設置以解決模塊導入問題
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_akshare_import():
    """檢查AKShare導入"""
    try:
        import akshare as ak
        print(f"✅ AKShare導入成功，版本: {ak.__version__}")
        return True
    except ImportError as e:
        print(f"❌ AKShare導入失败: {e}")
        return False

def check_akshare_utils():
    """檢查akshare_utils.py"""
    try:
        from tradingagents.dataflows.akshare_utils import get_akshare_provider
        provider = get_akshare_provider()
        print(f"✅ AKShare工具模塊正常，連接狀態: {provider.connected}")
        return True, provider
    except Exception as e:
        print(f"❌ AKShare工具模塊異常: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def check_data_source_manager():
    """檢查數據源管理器"""
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        # 檢查AKShare枚举
        akshare_enum = ChinaDataSource.AKSHARE
        print(f"✅ AKShare枚举: {akshare_enum.value}")
        
        # 初始化管理器
        manager = DataSourceManager()
        
        # 檢查可用數據源
        available = [s.value for s in manager.available_sources]
        if 'akshare' in available:
            print("✅ AKShare在可用數據源中")
        else:
            print("⚠️ AKShare不在可用數據源中")
        
        return True, manager
    except Exception as e:
        print(f"❌ 數據源管理器檢查失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_akshare_adapter():
    """測試AKShare適配器"""
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        
        manager = DataSourceManager()
        
        # 獲取AKShare適配器
        akshare_adapter = manager._get_akshare_adapter()
        
        if akshare_adapter is not None:
            print("✅ AKShare適配器獲取成功")
            
            # 測試獲取股票數據
            test_data = akshare_adapter.get_stock_data("000001", "2024-12-01", "2024-12-10")
            if test_data is not None and not test_data.empty:
                print(f"✅ AKShare適配器數據獲取成功，{len(test_data)}條記錄")
                return True
            else:
                print("❌ AKShare適配器數據獲取失败")
                return False
        else:
            print("❌ AKShare適配器獲取失败")
            return False
            
    except Exception as e:
        print(f"❌ AKShare適配器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_source_switching():
    """測試數據源切換"""
    try:
        from tradingagents.dataflows.interface import switch_china_data_source
        
        # 切換到AKShare
        result = switch_china_data_source("akshare")
        print(f"數據源切換結果: {result}")
        
        if "成功" in result or "✅" in result or "akshare" in result.lower():
            print("✅ 數據源切換到AKShare成功")
            return True
        else:
            print("❌ 數據源切換到AKShare失败")
            return False
            
    except Exception as e:
        print(f"❌ 數據源切換測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_interface():
    """測試統一數據接口"""
    try:
        from tradingagents.dataflows.interface import get_china_stock_data_unified, switch_china_data_source
        
        # 先切換到AKShare
        switch_china_data_source("akshare")
        
        # 測試獲取數據
        data = get_china_stock_data_unified("000001", "2024-12-01", "2024-12-10")
        
        if data and len(data) > 100:  # 假設返回的是字符串格式的數據
            print("✅ 統一數據接口測試成功")
            print(f"   數據長度: {len(data)} 字符")
            return True
        else:
            print("❌ 統一數據接口測試失败")
            print(f"   返回數據: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 統一數據接口測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_akshare():
    """測試基本AKShare功能"""
    try:
        import akshare as ak
        
        # 測試獲取股票列表
        print("📊 測試獲取股票列表...")
        stock_list = ak.stock_info_a_code_name()
        print(f"✅ 獲取到{len(stock_list)}只股票")
        
        # 測試獲取股票數據
        print("📈 測試獲取股票數據...")
        data = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20241201", end_date="20241210", adjust="")
        print(f"✅ 獲取到{len(data)}條數據")
        
        return True
    except Exception as e:
        print(f"❌ AKShare基本功能測試失败: {e}")
        return False

def main():
    """主檢查函數"""
    print("🔍 AKShare功能完整檢查（修複版）")
    print("=" * 50)
    print(f"項目根目錄: {project_root}")
    print(f"Python路徑: {sys.path[0]}")
    print("=" * 50)
    
    test_results = {}
    
    # 1. 基本AKShare功能
    print("\n1️⃣ 基本AKShare功能測試")
    test_results['basic_akshare'] = test_basic_akshare()
    
    # 2. AKShare工具模塊
    print("\n2️⃣ AKShare工具模塊測試")
    success, provider = check_akshare_utils()
    test_results['akshare_utils'] = success
    
    # 3. 數據源管理器
    print("\n3️⃣ 數據源管理器測試")
    success, manager = check_data_source_manager()
    test_results['data_source_manager'] = success
    
    # 4. AKShare適配器
    print("\n4️⃣ AKShare適配器測試")
    test_results['akshare_adapter'] = test_akshare_adapter()
    
    # 5. 數據源切換
    print("\n5️⃣ 數據源切換測試")
    test_results['data_source_switching'] = test_data_source_switching()
    
    # 6. 統一數據接口
    print("\n6️⃣ 統一數據接口測試")
    test_results['unified_interface'] = test_unified_interface()
    
    # 总結結果
    print(f"\n📊 AKShare功能檢查总結")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name:25} {status}")
    
    print(f"\n🎯 总體結果: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 AKShare功能完全可用！")
        print("💡 可以安全刪除重複的AKShare分支")
    elif passed >= total * 0.7:
        print("⚠️ AKShare功能基本可用，但有部分問題")
        print("💡 建议修複問題後再刪除重複分支")
    else:
        print("❌ AKShare功能存在嚴重問題")
        print("💡 不建议刪除AKShare分支，需要先修複問題")
    
    return passed >= total * 0.7

if __name__ == "__main__":
    success = main()
    
    print(f"\n🎯 分支管理建议:")
    if success:
        print("✅ AKShare功能基本正常，可以考慮刪除重複分支")
        print("   - feature/akshare-integration")
        print("   - feature/akshare-integration-clean")
        print("   - 保留 feature/tushare-integration（包含完整功能）")
    else:
        print("⚠️ 建议先修複AKShare功能問題，再考慮分支清理")
