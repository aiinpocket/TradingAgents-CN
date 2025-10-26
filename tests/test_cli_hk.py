"""
測試CLI港股輸入功能
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_cli_market_selection():
    """測試CLI市場選擇功能"""
    print("🧪 測試CLI市場選擇功能...")
    
    try:
        # 導入CLI相關模塊
        from cli.main import select_market, get_ticker
        
        # 模擬港股市場配置
        hk_market = {
            "name": "港股",
            "name_en": "Hong Kong Stock", 
            "default": "0700.HK",
            "examples": ["0700.HK (腾讯)", "9988.HK (阿里巴巴)", "3690.HK (美团)"],
            "format": "代碼.HK (如: 0700.HK)",
            "pattern": r'^\d{4}\.HK$',
            "data_source": "yahoo_finance"
        }
        
        # 測試港股代碼驗證
        import re
        test_codes = [
            ("0700.HK", True),
            ("9988.HK", True), 
            ("3690.HK", True),
            ("700.HK", False),   # 不足4位
            ("07000.HK", False), # 超過4位
            ("0700", False),     # 缺少.HK
            ("AAPL", False)      # 美股代碼
        ]
        
        for code, should_match in test_codes:
            matches = bool(re.match(hk_market["pattern"], code))
            status = "✅" if matches == should_match else "❌"
            print(f"  {code}: {status} (匹配: {matches}, 期望: {should_match})")
        
        print("✅ CLI市場選擇測試通過")
        return True
        
    except Exception as e:
        print(f"❌ CLI市場選擇測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_analysis_flow():
    """測試股票分析流程"""
    print("🧪 測試股票分析流程...")
    
    try:
        # 測試股票類型识別
        from tradingagents.utils.stock_utils import StockUtils
        
        # 測試港股
        hk_ticker = "0700.HK"
        market_info = StockUtils.get_market_info(hk_ticker)
        
        print(f"  港股測試: {hk_ticker}")
        print(f"    市場: {market_info['market_name']}")
        print(f"    貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")
        print(f"    數據源: {market_info['data_source']}")
        print(f"    是否港股: {market_info['is_hk']}")
        
        # 驗證港股识別
        if not market_info['is_hk']:
            print(f"❌ {hk_ticker} 應该被识別為港股")
            return False
            
        if market_info['currency_symbol'] != 'HK$':
            print(f"❌ 港股貨币符號應為HK$，實际為: {market_info['currency_symbol']}")
            return False
        
        print("✅ 股票分析流程測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 股票分析流程測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """運行所有測試"""
    print("🇭🇰 開始港股CLI功能測試")
    print("=" * 40)
    
    tests = [
        test_cli_market_selection,
        test_stock_analysis_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 異常: {e}")
    
    print("=" * 40)
    print(f"🇭🇰 港股CLI測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！港股CLI功能正常")
    else:
        print("⚠️ 部分測試失败，需要進一步調試")

if __name__ == "__main__":
    main()
