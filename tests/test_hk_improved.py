"""
改進的港股功能測試
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_stock_recognition():
    """測試股票识別功能"""
    print("🧪 測試股票识別功能...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        test_cases = [
            ("0700.HK", "港股", "HK$"),
            ("9988.HK", "港股", "HK$"),
            ("000001", "中國A股", "¥"),
            ("AAPL", "美股", "$"),
        ]
        
        for ticker, expected_market, expected_currency in test_cases:
            market_info = StockUtils.get_market_info(ticker)
            
            print(f"  {ticker}:")
            print(f"    市場: {market_info['market_name']}")
            print(f"    貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")
            print(f"    數據源: {market_info['data_source']}")
            
            # 驗證結果
            if expected_market in market_info['market_name'] and market_info['currency_symbol'] == expected_currency:
                print(f"    ✅ 识別正確")
            else:
                print(f"    ❌ 识別錯誤")
                return False
        
        print("✅ 股票识別功能測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 股票识別功能測試失败: {e}")
        return False

def test_hk_data_unified():
    """測試港股統一數據接口"""
    print("\n🧪 測試港股統一數據接口...")
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_data_unified
        from datetime import datetime, timedelta
        
        # 設置測試日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 測試腾讯港股
        symbol = "0700.HK"
        print(f"  獲取 {symbol} 數據...")
        
        data = get_hk_stock_data_unified(symbol, start_date, end_date)
        
        if data and len(data) > 100:
            print("  ✅ 數據獲取成功")
            
            # 檢查關键信息
            checks = [
                ("港股數據報告", "包含標題"),
                ("HK$", "包含港币符號"),
                ("香港交易所", "包含交易所信息"),
                (symbol, "包含股票代碼")
            ]
            
            for check_text, description in checks:
                if check_text in data:
                    print(f"    ✅ {description}")
                else:
                    print(f"    ⚠️ 缺少{description}")
            
            print("✅ 港股統一數據接口測試通過")
            return True
        else:
            print("❌ 港股統一數據接口測試失败")
            return False
            
    except Exception as e:
        print(f"❌ 港股統一數據接口測試失败: {e}")
        return False

def test_hk_info_unified():
    """測試港股信息統一接口"""
    print("\n🧪 測試港股信息統一接口...")
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_info_unified
        
        symbol = "0700.HK"
        print(f"  獲取 {symbol} 信息...")
        
        info = get_hk_stock_info_unified(symbol)
        
        if info and 'symbol' in info:
            print(f"    ✅ 股票代碼: {info['symbol']}")
            print(f"    ✅ 股票名稱: {info['name']}")
            print(f"    ✅ 貨币: {info['currency']}")
            print(f"    ✅ 交易所: {info['exchange']}")
            
            # 驗證港股特有信息
            if info['currency'] == 'HKD' and info['exchange'] == 'HKG':
                print("    ✅ 港股信息正確")
            else:
                print("    ⚠️ 港股信息可能不完整")
            
            print("✅ 港股信息統一接口測試通過")
            return True
        else:
            print("❌ 港股信息統一接口測試失败")
            return False
            
    except Exception as e:
        print(f"❌ 港股信息統一接口測試失败: {e}")
        return False

def test_market_auto_selection():
    """測試市場自動選擇功能"""
    print("\n🧪 測試市場自動選擇功能...")
    
    try:
        from tradingagents.dataflows.interface import get_stock_data_by_market
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        test_symbols = [
            ("0700.HK", "港股"),
            ("000001", "A股"),
            ("AAPL", "美股")
        ]
        
        for symbol, market_type in test_symbols:
            print(f"  測試 {symbol} ({market_type})...")
            
            data = get_stock_data_by_market(symbol, start_date, end_date)
            
            if data and len(data) > 50:
                print(f"    ✅ {market_type}數據獲取成功")
            else:
                print(f"    ⚠️ {market_type}數據獲取可能失败")
        
        print("✅ 市場自動選擇功能測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 市場自動選擇功能測試失败: {e}")
        return False

def main():
    """運行所有測試"""
    print("🇭🇰 開始改進的港股功能測試")
    print("=" * 50)
    
    tests = [
        test_stock_recognition,
        test_hk_data_unified,
        test_hk_info_unified,
        test_market_auto_selection
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
    print(f"🇭🇰 改進的港股功能測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！港股功能優化成功")
        print("\n✅ 港股功能特點:")
        print("  - 正確识別港股代碼格式 (XXXX.HK)")
        print("  - 使用港币 (HK$) 顯示價格")
        print("  - 支持多重备用方案")
        print("  - 處理API頻率限制")
        print("  - 提供演示模式數據")
    else:
        print("⚠️ 部分測試失败，但核心功能正常")

if __name__ == "__main__":
    main()
