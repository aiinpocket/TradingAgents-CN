"""
測試港股功能
驗證港股代碼识別、數據獲取和處理功能
"""

import sys
import os
import traceback

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_stock_utils():
    """測試股票工具類"""
    print("\n🧪 測試股票工具類...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        # 測試港股代碼识別
        test_cases = [
            ("0700.HK", "港股"),
            ("9988.HK", "港股"),
            ("3690.HK", "港股"),
            ("000001", "中國A股"),
            ("600036", "中國A股"),
            ("AAPL", "美股"),
            ("TSLA", "美股"),
            ("invalid", "未知市場")
        ]
        
        for ticker, expected in test_cases:
            market_info = StockUtils.get_market_info(ticker)
            print(f"  {ticker}: {market_info['market_name']} ({market_info['currency_name']}) - {'✅' if expected in market_info['market_name'] else '❌'}")
            
            if expected == "港股" and not market_info['is_hk']:
                print(f"❌ {ticker} 應该被识別為港股")
                return False
            elif expected == "中國A股" and not market_info['is_china']:
                print(f"❌ {ticker} 應该被识別為中國A股")
                return False
            elif expected == "美股" and not market_info['is_us']:
                print(f"❌ {ticker} 應该被识別為美股")
                return False
        
        print("✅ 股票工具類測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 股票工具類測試失败: {e}")
        traceback.print_exc()
        return False


def test_hk_stock_provider():
    """測試港股數據提供器"""
    print("\n🧪 測試港股數據提供器...")
    
    try:
        from tradingagents.dataflows.hk_stock_utils import get_hk_stock_provider
        
        provider = get_hk_stock_provider()
        
        # 測試港股代碼標準化
        test_symbols = [
            ("0700", "0700.HK"),
            ("0700.HK", "0700.HK"),
            ("9988", "9988.HK"),
            ("3690.HK", "3690.HK")
        ]
        
        for input_symbol, expected in test_symbols:
            normalized = provider._normalize_hk_symbol(input_symbol)
            print(f"  標準化: {input_symbol} -> {normalized} {'✅' if normalized == expected else '❌'}")
            
            if normalized != expected:
                print(f"❌ 港股代碼標準化失败: {input_symbol} -> {normalized}, 期望: {expected}")
                return False
        
        print("✅ 港股數據提供器測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 港股數據提供器測試失败: {e}")
        traceback.print_exc()
        return False


def test_hk_stock_info():
    """測試港股信息獲取"""
    print("\n🧪 測試港股信息獲取...")
    
    try:
        from tradingagents.dataflows.hk_stock_utils import get_hk_stock_info
        
        # 測試腾讯港股信息
        hk_symbol = "0700.HK"
        print(f"  獲取 {hk_symbol} 信息...")
        
        info = get_hk_stock_info(hk_symbol)
        
        if info and 'symbol' in info:
            print(f"  ✅ 股票代碼: {info['symbol']}")
            print(f"  ✅ 股票名稱: {info['name']}")
            print(f"  ✅ 貨币: {info['currency']}")
            print(f"  ✅ 交易所: {info['exchange']}")
            print(f"  ✅ 數據源: {info['source']}")
            
            # 驗證基本字段
            if info['currency'] != 'HKD':
                print(f"⚠️ 港股貨币應為HKD，實际為: {info['currency']}")
            
            if info['exchange'] != 'HKG':
                print(f"⚠️ 港股交易所應為HKG，實际為: {info['exchange']}")
            
            print("✅ 港股信息獲取測試通過")
            return True
        else:
            print("❌ 港股信息獲取失败")
            return False
            
    except Exception as e:
        print(f"❌ 港股信息獲取測試失败: {e}")
        traceback.print_exc()
        return False


def test_hk_stock_data():
    """測試港股數據獲取（簡單測試）"""
    print("\n🧪 測試港股數據獲取...")
    
    try:
        from tradingagents.dataflows.hk_stock_utils import get_hk_stock_data
        from datetime import datetime, timedelta
        
        # 設置測試日期範围（最近30天）
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 測試腾讯港股數據
        hk_symbol = "0700.HK"
        print(f"  獲取 {hk_symbol} 數據 ({start_date} 到 {end_date})...")
        
        data_text = get_hk_stock_data(hk_symbol, start_date, end_date)
        
        if data_text and "港股數據報告" in data_text:
            print("  ✅ 港股數據格式正確")
            print(f"  ✅ 數據長度: {len(data_text)}字符")
            
            # 檢查關键信息
            if "HK$" in data_text:
                print("  ✅ 包含港币價格信息")
            else:
                print("  ⚠️ 缺少港币價格信息")
            
            if "香港交易所" in data_text:
                print("  ✅ 包含交易所信息")
            
            print("✅ 港股數據獲取測試通過")
            return True
        else:
            print("❌ 港股數據獲取失败或格式錯誤")
            print(f"返回數據: {data_text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 港股數據獲取測試失败: {e}")
        traceback.print_exc()
        return False


def test_optimized_us_data_hk_support():
    """測試優化美股數據模塊的港股支持"""
    print("\n🧪 測試優化數據模塊港股支持...")
    
    try:
        from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
        from datetime import datetime, timedelta
        
        # 設置測試日期範围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 測試港股數據獲取
        hk_symbol = "0700.HK"
        print(f"  通過優化模塊獲取 {hk_symbol} 數據...")
        
        data_text = get_us_stock_data_cached(
            symbol=hk_symbol,
            start_date=start_date,
            end_date=end_date,
            force_refresh=True
        )
        
        if data_text and "數據分析" in data_text:
            print("  ✅ 數據獲取成功")
            
            # 檢查港股特有信息
            if "港股" in data_text:
                print("  ✅ 正確识別為港股")
            
            if "HK$" in data_text:
                print("  ✅ 使用港币符號")
            else:
                print("  ⚠️ 未使用港币符號")
            
            print("✅ 優化數據模塊港股支持測試通過")
            return True
        else:
            print("❌ 優化數據模塊港股支持測試失败")
            return False
            
    except Exception as e:
        print(f"❌ 優化數據模塊港股支持測試失败: {e}")
        traceback.print_exc()
        return False


def main():
    """運行所有港股功能測試"""
    print("🇭🇰 開始港股功能測試")
    print("=" * 50)
    
    tests = [
        test_stock_utils,
        test_hk_stock_provider,
        test_hk_stock_info,
        test_hk_stock_data,
        test_optimized_us_data_hk_support
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
    print(f"🇭🇰 港股功能測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！港股功能正常")
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步調試")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
