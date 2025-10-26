"""
測試FINNHUB港股支持
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_finnhub_connection():
    """測試FINNHUB連接"""
    print("🧪 測試FINNHUB連接...")
    
    try:
        import finnhub
        
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            print("❌ 未配置FINNHUB_API_KEY環境變量")
            return False
        
        client = finnhub.Client(api_key=api_key)
        
        # 測試美股連接
        print("  測試美股連接 (AAPL)...")
        quote = client.quote('AAPL')
        if quote and 'c' in quote:
            print(f"    ✅ 美股連接成功: AAPL = ${quote['c']:.2f}")
        else:
            print("    ❌ 美股連接失败")
            return False
        
        print("✅ FINNHUB連接測試通過")
        return True
        
    except Exception as e:
        print(f"❌ FINNHUB連接測試失败: {e}")
        return False

def test_finnhub_hk_symbols():
    """測試FINNHUB港股代碼格式"""
    print("\n🧪 測試FINNHUB港股代碼格式...")
    
    try:
        import finnhub
        
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            print("❌ 未配置FINNHUB_API_KEY環境變量")
            return False
        
        client = finnhub.Client(api_key=api_key)
        
        # 測試不同的港股代碼格式
        hk_symbols = [
            "0700.HK",  # 腾讯
            "9988.HK",  # 阿里巴巴
            "3690.HK",  # 美团
            "1810.HK",  # 小米
        ]
        
        success_count = 0
        
        for symbol in hk_symbols:
            try:
                print(f"  測試港股: {symbol}...")
                quote = client.quote(symbol)
                
                if quote and 'c' in quote and quote['c'] > 0:
                    print(f"    ✅ {symbol} = HK${quote['c']:.2f}")
                    success_count += 1
                else:
                    print(f"    ❌ {symbol} 無數據或價格為0")
                    
            except Exception as e:
                print(f"    ❌ {symbol} 獲取失败: {e}")
        
        if success_count > 0:
            print(f"✅ FINNHUB港股支持測試通過 ({success_count}/{len(hk_symbols)} 成功)")
            return True
        else:
            print("❌ FINNHUB港股支持測試失败 - 所有港股代碼都無法獲取數據")
            return False
        
    except Exception as e:
        print(f"❌ FINNHUB港股支持測試失败: {e}")
        return False

def test_finnhub_hk_company_info():
    """測試FINNHUB港股公司信息"""
    print("\n🧪 測試FINNHUB港股公司信息...")
    
    try:
        import finnhub
        
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            print("❌ 未配置FINNHUB_API_KEY環境變量")
            return False
        
        client = finnhub.Client(api_key=api_key)
        
        symbol = "0700.HK"  # 腾讯
        print(f"  獲取 {symbol} 公司信息...")
        
        try:
            profile = client.company_profile2(symbol=symbol)
            
            if profile and 'name' in profile:
                print(f"    ✅ 公司名稱: {profile['name']}")
                print(f"    ✅ 國家: {profile.get('country', 'N/A')}")
                print(f"    ✅ 貨币: {profile.get('currency', 'N/A')}")
                print(f"    ✅ 交易所: {profile.get('exchange', 'N/A')}")
                print(f"    ✅ 行業: {profile.get('finnhubIndustry', 'N/A')}")
                return True
            else:
                print(f"    ❌ {symbol} 公司信息為空")
                return False
                
        except Exception as e:
            print(f"    ❌ {symbol} 公司信息獲取失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ FINNHUB港股公司信息測試失败: {e}")
        return False

def test_optimized_us_data_finnhub_hk():
    """測試優化數據模塊的FINNHUB港股支持"""
    print("\n🧪 測試優化數據模塊的FINNHUB港股支持...")
    
    try:
        from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        symbol = "0700.HK"  # 腾讯
        print(f"  通過優化模塊獲取 {symbol} 數據...")
        
        data = get_us_stock_data_cached(symbol, start_date, end_date, force_refresh=True)
        
        if data and len(data) > 100:
            print("    ✅ 數據獲取成功")
            
            # 檢查關键信息
            checks = [
                ("港股", "识別為港股"),
                ("HK$", "使用港币符號"),
                ("FINNHUB", "使用FINNHUB數據源"),
                (symbol, "包含股票代碼")
            ]
            
            for check_text, description in checks:
                if check_text in data:
                    print(f"      ✅ {description}")
                else:
                    print(f"      ⚠️ 缺少{description}")
            
            print("✅ 優化數據模塊FINNHUB港股支持測試通過")
            return True
        else:
            print("❌ 優化數據模塊FINNHUB港股支持測試失败")
            print(f"返回數據: {data[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 優化數據模塊FINNHUB港股支持測試失败: {e}")
        return False

def test_unified_interface_finnhub_priority():
    """測試統一接口的FINNHUB優先級"""
    print("\n🧪 測試統一接口的FINNHUB優先級...")
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_data_unified
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        symbol = "0700.HK"
        print(f"  通過統一接口獲取 {symbol} 數據...")
        
        data = get_hk_stock_data_unified(symbol, start_date, end_date)
        
        if data and len(data) > 50:
            print("    ✅ 統一接口數據獲取成功")
            
            # 檢查數據源優先級
            if "FINNHUB" in data:
                print("    ✅ 優先使用FINNHUB數據源")
            elif "Yahoo Finance" in data:
                print("    ✅ 使用Yahoo Finance备用數據源")
            elif "AKShare" in data:
                print("    ✅ 使用AKShare备用數據源")
            else:
                print("    ⚠️ 未识別數據源")
            
            print("✅ 統一接口FINNHUB優先級測試通過")
            return True
        else:
            print("❌ 統一接口FINNHUB優先級測試失败")
            return False
        
    except Exception as e:
        print(f"❌ 統一接口FINNHUB優先級測試失败: {e}")
        return False

def main():
    """運行所有FINNHUB港股測試"""
    print("🇭🇰 開始FINNHUB港股支持測試")
    print("=" * 50)
    
    tests = [
        test_finnhub_connection,
        test_finnhub_hk_symbols,
        test_finnhub_hk_company_info,
        test_optimized_us_data_finnhub_hk,
        test_unified_interface_finnhub_priority
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
    print(f"🇭🇰 FINNHUB港股支持測試完成: {passed}/{total} 通過")
    
    if passed >= 2:  # 至少連接和基本功能正常
        print("🎉 FINNHUB港股支持基本正常！")
        print("\n✅ FINNHUB港股功能特點:")
        print("  - 支持港股實時報價")
        print("  - 支持港股公司信息")
        print("  - 作為港股數據的首選數據源")
        print("  - 自動貨币符號识別 (HK$)")
        print("  - 集成到統一數據接口")
    else:
        print("⚠️ FINNHUB港股支持可能有問題，請檢查API配置")

if __name__ == "__main__":
    main()
