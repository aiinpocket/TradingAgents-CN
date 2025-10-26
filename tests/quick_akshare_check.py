#!/usr/bin/env python3
"""
快速AKShare功能檢查
"""

def check_akshare_import():
    """檢查AKShare導入"""
    try:
        import akshare as ak
        print(f"✅ AKShare導入成功，版本: {ak.__version__}")
        return True
    except ImportError as e:
        print(f"❌ AKShare導入失败: {e}")
        print("💡 請安裝AKShare: pip install akshare")
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
        return False, None

def check_data_source_manager():
    """檢查數據源管理器"""
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        manager = DataSourceManager()
        
        available = [s.value for s in manager.available_sources]
        if 'akshare' in available:
            print("✅ AKShare在可用數據源中")
        else:
            print("⚠️ AKShare不在可用數據源中")
        
        return True
    except Exception as e:
        print(f"❌ 數據源管理器檢查失败: {e}")
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
    print("🔍 AKShare功能快速檢查")
    print("=" * 40)
    
    results = []
    
    # 1. 檢查導入
    results.append(check_akshare_import())
    
    # 2. 檢查工具模塊
    success, provider = check_akshare_utils()
    results.append(success)
    
    # 3. 檢查數據源管理器
    results.append(check_data_source_manager())
    
    # 4. 測試基本功能
    if results[0]:  # 如果導入成功
        results.append(test_basic_akshare())
    
    # 总結
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 檢查結果: {passed}/{total} 項通過")
    
    if passed == total:
        print("🎉 AKShare功能完全可用！")
    else:
        print("⚠️ AKShare功能存在問題")
    
    return passed == total

if __name__ == "__main__":
    main()
