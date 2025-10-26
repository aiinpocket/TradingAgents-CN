#!/usr/bin/env python3
"""
簡單的AKShare測試
驗證修複後的導入是否正常
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_basic_imports():
    """測試基本導入"""
    print("🔍 測試基本導入")
    print("=" * 40)
    
    try:
        # 測試AKShare直接導入
        import akshare as ak
        print(f"✅ AKShare導入成功: {ak.__version__}")
    except Exception as e:
        print(f"❌ AKShare導入失败: {e}")
        return False
    
    try:
        # 測試dataflows模塊導入
        from tradingagents.dataflows import akshare_utils
        print("✅ akshare_utils模塊導入成功")
    except Exception as e:
        print(f"❌ akshare_utils模塊導入失败: {e}")
        return False
    
    try:
        # 測試數據源管理器導入
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        print("✅ DataSourceManager導入成功")
    except Exception as e:
        print(f"❌ DataSourceManager導入失败: {e}")
        return False
    
    return True

def test_akshare_provider():
    """測試AKShare提供器"""
    print("\n🔍 測試AKShare提供器")
    print("=" * 40)
    
    try:
        from tradingagents.dataflows.akshare_utils import get_akshare_provider
        provider = get_akshare_provider()
        print(f"✅ AKShare提供器創建成功，連接狀態: {provider.connected}")
        
        if provider.connected:
            # 測試獲取股票數據
            data = provider.get_stock_data("000001", "2024-12-01", "2024-12-10")
            if data is not None and not data.empty:
                print(f"✅ 獲取股票數據成功: {len(data)}條記錄")
            else:
                print("❌ 獲取股票數據失败")
                return False
        
        return True
    except Exception as e:
        print(f"❌ AKShare提供器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_source_manager():
    """測試數據源管理器"""
    print("\n🔍 測試數據源管理器")
    print("=" * 40)
    
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        # 檢查AKShare枚举
        akshare_enum = ChinaDataSource.AKSHARE
        print(f"✅ AKShare枚举: {akshare_enum.value}")
        
        # 創建管理器
        manager = DataSourceManager()
        print("✅ 數據源管理器創建成功")
        
        # 檢查可用數據源
        available = [s.value for s in manager.available_sources]
        print(f"✅ 可用數據源: {available}")
        
        if 'akshare' in available:
            print("✅ AKShare在可用數據源中")
        else:
            print("⚠️ AKShare不在可用數據源中")
        
        return True
    except Exception as e:
        print(f"❌ 數據源管理器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🔍 簡單AKShare功能測試")
    print("=" * 60)
    
    results = []
    
    # 1. 基本導入測試
    results.append(test_basic_imports())
    
    # 2. AKShare提供器測試
    results.append(test_akshare_provider())
    
    # 3. 數據源管理器測試
    results.append(test_data_source_manager())
    
    # 总結
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 測試結果: {passed}/{total} 項通過")
    
    if passed == total:
        print("🎉 AKShare功能完全正常！")
        print("✅ 可以安全刪除重複的AKShare分支")
        return True
    elif passed >= 2:
        print("⚠️ AKShare基本功能正常，部分高級功能可能有問題")
        print("✅ 可以考慮刪除重複的AKShare分支")
        return True
    else:
        print("❌ AKShare功能存在問題")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎯 分支管理建议:")
        print("✅ AKShare功能基本正常")
        print("✅ 可以刪除以下重複分支:")
        print("   - feature/akshare-integration")
        print("   - feature/akshare-integration-clean")
        print("✅ 保留 feature/tushare-integration（包含完整功能）")
    else:
        print(f"\n⚠️ 建议:")
        print("1. 先修複AKShare集成問題")
        print("2. 再考慮分支清理")
