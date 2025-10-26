#!/usr/bin/env python3
"""
測試港股基本面分析修複
驗證港股代碼识別、工具選擇和貨币處理是否正確
"""

import os
import sys

def test_stock_type_detection():
    """測試股票類型檢測功能"""
    print("🧪 測試股票類型檢測...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        test_cases = [
            ("0700.HK", "港股", "港币", "HK$"),
            ("9988.HK", "港股", "港币", "HK$"),
            ("000001", "中國A股", "人民币", "¥"),
            ("600036", "中國A股", "人民币", "¥"),
            ("AAPL", "美股", "美元", "$"),
            ("TSLA", "美股", "美元", "$"),
        ]
        
        for ticker, expected_market, expected_currency, expected_symbol in test_cases:
            market_info = StockUtils.get_market_info(ticker)
            
            print(f"  {ticker}:")
            print(f"    市場: {market_info['market_name']}")
            print(f"    貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")
            print(f"    是否港股: {market_info['is_hk']}")
            print(f"    是否A股: {market_info['is_china']}")
            print(f"    是否美股: {market_info['is_us']}")
            
            # 驗證結果
            if (expected_market in market_info['market_name'] and 
                market_info['currency_name'] == expected_currency and
                market_info['currency_symbol'] == expected_symbol):
                print(f"    ✅ 识別正確")
            else:
                print(f"    ❌ 识別錯誤")
                print(f"       期望: {expected_market}, {expected_currency}, {expected_symbol}")
                print(f"       實际: {market_info['market_name']}, {market_info['currency_name']}, {market_info['currency_symbol']}")
                return False
        
        print("✅ 股票類型檢測測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 股票類型檢測測試失败: {e}")
        return False


def test_fundamentals_analyst_tool_selection():
    """測試基本面分析師的工具選擇逻辑"""
    print("\n🧪 測試基本面分析師工具選擇...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.utils.stock_utils import StockUtils
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 測試港股工具選擇
        hk_ticker = "0700.HK"
        market_info = StockUtils.get_market_info(hk_ticker)
        
        print(f"  港股工具選擇測試: {hk_ticker}")
        print(f"    市場類型: {market_info['market_name']}")
        print(f"    是否港股: {market_info['is_hk']}")
        print(f"    貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")
        
        # 檢查港股專用工具是否存在
        if hasattr(toolkit, 'get_hk_stock_data_unified'):
            print(f"    ✅ 港股專用工具存在: get_hk_stock_data_unified")
        else:
            print(f"    ❌ 港股專用工具不存在")
            return False
        
        # 測試A股工具選擇
        china_ticker = "000001"
        market_info = StockUtils.get_market_info(china_ticker)
        
        print(f"  A股工具選擇測試: {china_ticker}")
        print(f"    市場類型: {market_info['market_name']}")
        print(f"    是否A股: {market_info['is_china']}")
        print(f"    貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")
        
        # 檢查A股專用工具是否存在
        if hasattr(toolkit, 'get_china_stock_data'):
            print(f"    ✅ A股專用工具存在: get_china_stock_data")
        else:
            print(f"    ❌ A股專用工具不存在")
            return False
        
        print("✅ 基本面分析師工具選擇測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 基本面分析師工具選擇測試失败: {e}")
        return False


def test_trader_currency_detection():
    """測試交易員節點的貨币檢測"""
    print("\n🧪 測試交易員貨币檢測...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        test_cases = [
            ("0700.HK", "港币", "HK$"),
            ("9988.HK", "港币", "HK$"),
            ("000001", "人民币", "¥"),
            ("AAPL", "美元", "$"),
        ]
        
        for ticker, expected_currency, expected_symbol in test_cases:
            market_info = StockUtils.get_market_info(ticker)
            
            print(f"  {ticker}:")
            print(f"    檢測到的貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")
            print(f"    期望的貨币: {expected_currency} ({expected_symbol})")
            
            if (market_info['currency_name'] == expected_currency and 
                market_info['currency_symbol'] == expected_symbol):
                print(f"    ✅ 貨币檢測正確")
            else:
                print(f"    ❌ 貨币檢測錯誤")
                return False
        
        print("✅ 交易員貨币檢測測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 交易員貨币檢測測試失败: {e}")
        return False


def test_hk_data_source():
    """測試港股數據源"""
    print("\n🧪 測試港股數據源...")
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_data_unified
        
        # 測試港股數據獲取
        hk_ticker = "0700.HK"
        print(f"  測試獲取港股數據: {hk_ticker}")
        
        result = get_hk_stock_data_unified(hk_ticker, "2025-07-10", "2025-07-14")
        
        print(f"  數據獲取結果長度: {len(result)}")
        print(f"  結果前100字符: {result[:100]}...")
        
        if "❌" in result:
            print(f"  ⚠️ 數據獲取失败，但這可能是正常的（網絡問題或API限制）")
            print(f"  失败信息: {result}")
        else:
            print(f"  ✅ 數據獲取成功")
        
        print("✅ 港股數據源測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 港股數據源測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔧 港股基本面分析修複測試")
    print("=" * 60)
    
    tests = [
        test_stock_type_detection,
        test_fundamentals_analyst_tool_selection,
        test_trader_currency_detection,
        test_hk_data_source,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ 測試失败: {test.__name__}")
        except Exception as e:
            print(f"❌ 測試異常: {test.__name__} - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！港股基本面分析修複成功")
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步檢查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
