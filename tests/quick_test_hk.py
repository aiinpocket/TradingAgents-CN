"""
快速測試港股功能
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_stock_recognition():
    """測試股票识別"""
    print("🧪 測試股票识別...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        test_cases = [
            "0700.HK",  # 腾讯港股
            "000001",   # 平安銀行A股
            "AAPL"      # 苹果美股
        ]
        
        for ticker in test_cases:
            info = StockUtils.get_market_info(ticker)
            print(f"  {ticker}: {info['market_name']} ({info['currency_symbol']})")
        
        print("✅ 股票识別測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 股票识別測試失败: {e}")
        return False

def test_akshare_basic():
    """測試AKShare基本功能"""
    print("\n🧪 測試AKShare基本功能...")
    
    try:
        from tradingagents.dataflows.akshare_utils import get_akshare_provider
        
        provider = get_akshare_provider()
        
        if provider.connected:
            print("  ✅ AKShare連接成功")
            
            # 測試港股代碼標準化
            test_symbol = "0700.HK"
            normalized = provider._normalize_hk_symbol_for_akshare(test_symbol)
            print(f"  港股代碼標準化: {test_symbol} -> {normalized}")
            
            return True
        else:
            print("  ⚠️ AKShare未連接")
            return False
        
    except Exception as e:
        print(f"❌ AKShare基本功能測試失败: {e}")
        return False

def test_unified_interface():
    """測試統一接口"""
    print("\n🧪 測試統一接口...")
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_info_unified
        
        symbol = "0700.HK"
        print(f"  獲取 {symbol} 信息...")
        
        info = get_hk_stock_info_unified(symbol)
        
        if info and 'symbol' in info:
            print(f"    代碼: {info['symbol']}")
            print(f"    名稱: {info['name']}")
            print(f"    貨币: {info['currency']}")
            print(f"    數據源: {info['source']}")
            print("  ✅ 統一接口測試成功")
            return True
        else:
            print("  ❌ 統一接口測試失败")
            return False
        
    except Exception as e:
        print(f"❌ 統一接口測試失败: {e}")
        return False

def main():
    """運行快速測試"""
    print("🇭🇰 港股功能快速測試")
    print("=" * 30)
    
    tests = [
        test_stock_recognition,
        test_akshare_basic,
        test_unified_interface
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 測試異常: {e}")
    
    print("\n" + "=" * 30)
    print(f"🇭🇰 測試完成: {passed}/{total} 通過")
    
    if passed >= 2:
        print("🎉 港股功能基本正常！")
    else:
        print("⚠️ 港股功能可能有問題")

if __name__ == "__main__":
    main()
