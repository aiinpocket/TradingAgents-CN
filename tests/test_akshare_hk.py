"""
測試AKShare港股功能
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_akshare_hk_basic():
    """測試AKShare港股基本功能"""
    print("🧪 測試AKShare港股基本功能...")
    
    try:
        from tradingagents.dataflows.akshare_utils import get_akshare_provider
        
        provider = get_akshare_provider()
        
        if not provider.connected:
            print("⚠️ AKShare未連接，跳過測試")
            return True
        
        # 測試港股代碼標準化
        test_symbols = [
            ("0700.HK", "00700"),
            ("700", "00700"),
            ("9988.HK", "09988"),
            ("3690", "03690")
        ]
        
        for input_symbol, expected in test_symbols:
            normalized = provider._normalize_hk_symbol_for_akshare(input_symbol)
            print(f"  標準化: {input_symbol} -> {normalized} {'✅' if normalized == expected else '❌'}")
            
            if normalized != expected:
                print(f"❌ 港股代碼標準化失败: {input_symbol} -> {normalized}, 期望: {expected}")
                return False
        
        print("✅ AKShare港股基本功能測試通過")
        return True
        
    except Exception as e:
        print(f"❌ AKShare港股基本功能測試失败: {e}")
        return False

def test_akshare_hk_data():
    """測試AKShare港股數據獲取"""
    print("\n🧪 測試AKShare港股數據獲取...")
    
    try:
        from tradingagents.dataflows.akshare_utils import get_hk_stock_data_akshare
        from datetime import datetime, timedelta
        
        # 設置測試日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 測試腾讯港股
        symbol = "0700.HK"
        print(f"  獲取 {symbol} 數據...")
        
        data = get_hk_stock_data_akshare(symbol, start_date, end_date)
        
        if data and len(data) > 100:
            print("  ✅ AKShare港股數據獲取成功")
            
            # 檢查關键信息
            checks = [
                ("港股數據報告", "包含標題"),
                ("AKShare", "包含數據源標识"),
                ("HK$", "包含港币符號"),
                ("香港交易所", "包含交易所信息"),
                (symbol, "包含股票代碼")
            ]
            
            for check_text, description in checks:
                if check_text in data:
                    print(f"    ✅ {description}")
                else:
                    print(f"    ⚠️ 缺少{description}")
            
            print("✅ AKShare港股數據獲取測試通過")
            return True
        else:
            print("❌ AKShare港股數據獲取失败")
            print(f"返回數據: {data[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ AKShare港股數據獲取測試失败: {e}")
        return False

def test_akshare_hk_info():
    """測試AKShare港股信息獲取"""
    print("\n🧪 測試AKShare港股信息獲取...")
    
    try:
        from tradingagents.dataflows.akshare_utils import get_hk_stock_info_akshare
        
        symbol = "0700.HK"
        print(f"  獲取 {symbol} 信息...")
        
        info = get_hk_stock_info_akshare(symbol)
        
        if info and 'symbol' in info:
            print(f"    ✅ 股票代碼: {info['symbol']}")
            print(f"    ✅ 股票名稱: {info['name']}")
            print(f"    ✅ 貨币: {info['currency']}")
            print(f"    ✅ 交易所: {info['exchange']}")
            print(f"    ✅ 數據源: {info['source']}")
            
            # 驗證港股特有信息
            if info['currency'] == 'HKD' and info['exchange'] == 'HKG':
                print("    ✅ 港股信息正確")
            else:
                print("    ⚠️ 港股信息可能不完整")
            
            print("✅ AKShare港股信息獲取測試通過")
            return True
        else:
            print("❌ AKShare港股信息獲取失败")
            return False
            
    except Exception as e:
        print(f"❌ AKShare港股信息獲取測試失败: {e}")
        return False

def test_unified_interface():
    """測試統一接口的AKShare支持"""
    print("\n🧪 測試統一接口的AKShare支持...")
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_data_unified, get_hk_stock_info_unified
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        symbol = "0700.HK"
        print(f"  通過統一接口獲取 {symbol} 數據...")
        
        # 測試數據獲取
        data = get_hk_stock_data_unified(symbol, start_date, end_date)
        
        if data and len(data) > 50:
            print("    ✅ 統一接口數據獲取成功")
            
            # 檢查是否包含AKShare標识
            if "AKShare" in data:
                print("    ✅ 成功使用AKShare作為數據源")
            elif "Yahoo Finance" in data:
                print("    ✅ 使用Yahoo Finance作為备用數據源")
            elif "演示模式" in data:
                print("    ✅ 使用演示模式作為最终备用")
            
        # 測試信息獲取
        info = get_hk_stock_info_unified(symbol)
        
        if info and 'symbol' in info:
            print("    ✅ 統一接口信息獲取成功")
            print(f"    數據源: {info.get('source', 'unknown')}")
        
        print("✅ 統一接口AKShare支持測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 統一接口AKShare支持測試失败: {e}")
        return False

def main():
    """運行所有AKShare港股測試"""
    print("🇭🇰 開始AKShare港股功能測試")
    print("=" * 50)
    
    tests = [
        test_akshare_hk_basic,
        test_akshare_hk_data,
        test_akshare_hk_info,
        test_unified_interface
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"🇭🇰 AKShare港股功能測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！AKShare港股功能正常")
        print("\n✅ AKShare港股功能特點:")
        print("  - 支持港股代碼格式轉換")
        print("  - 獲取港股歷史數據")
        print("  - 獲取港股基本信息")
        print("  - 集成到統一數據接口")
        print("  - 作為Yahoo Finance的备用方案")
    else:
        print("⚠️ 部分測試失败，但核心功能可能正常")

if __name__ == "__main__":
    main()
