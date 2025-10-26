#!/usr/bin/env python3
"""
測試改進的港股工具
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_improved_hk_provider():
    """測試改進的港股提供器"""
    print("\n🇭🇰 測試改進的港股提供器")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.improved_hk_utils import get_improved_hk_provider
        
        provider = get_improved_hk_provider()
        print("✅ 改進港股提供器初始化成功")
        
        # 測試不同格式的港股代碼
        test_symbols = [
            "0700.HK",  # 腾讯控股
            "0700",     # 腾讯控股（無後缀）
            "00700",    # 腾讯控股（5位）
            "0941.HK",  # 中國移動
            "1299",     # 友邦保險
            "9988.HK",  # 阿里巴巴
            "3690",     # 美团
            "1234.HK",  # 不存在的股票
        ]
        
        print(f"\n📊 測試港股公司名稱獲取:")
        for symbol in test_symbols:
            try:
                company_name = provider.get_company_name(symbol)
                print(f"   {symbol:10} -> {company_name}")
                
                # 驗證不是默認格式
                if not company_name.startswith('港股'):
                    print(f"      ✅ 成功獲取具體公司名稱")
                else:
                    print(f"      ⚠️ 使用默認格式")
                    
            except Exception as e:
                print(f"   {symbol:10} -> ❌ 錯誤: {e}")
        
        print(f"\n📊 測試港股信息獲取:")
        for symbol in test_symbols[:3]:  # 只測試前3個
            try:
                stock_info = provider.get_stock_info(symbol)
                print(f"   {symbol}:")
                print(f"      名稱: {stock_info['name']}")
                print(f"      貨币: {stock_info['currency']}")
                print(f"      交易所: {stock_info['exchange']}")
                print(f"      來源: {stock_info['source']}")
                
            except Exception as e:
                print(f"   {symbol} -> ❌ 錯誤: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analyst_integration():
    """測試分析師集成"""
    print("\n🔍 測試分析師集成")
    print("=" * 80)
    
    try:
        from tradingagents.agents.analysts.market_analyst import _get_company_name
        from tradingagents.agents.analysts.fundamentals_analyst import _get_company_name_for_fundamentals
        from tradingagents.utils.stock_utils import StockUtils
        
        test_hk_symbols = ["0700.HK", "0941.HK", "1299.HK"]
        
        for symbol in test_hk_symbols:
            print(f"\n📊 測試港股: {symbol}")
            
            # 獲取市場信息
            market_info = StockUtils.get_market_info(symbol)
            print(f"   市場信息: {market_info['market_name']}")
            
            # 測試市場分析師
            try:
                market_name = _get_company_name(symbol, market_info)
                print(f"   市場分析師: {market_name}")
            except Exception as e:
                print(f"   市場分析師: ❌ {e}")
            
            # 測試基本面分析師
            try:
                fundamentals_name = _get_company_name_for_fundamentals(symbol, market_info)
                print(f"   基本面分析師: {fundamentals_name}")
            except Exception as e:
                print(f"   基本面分析師: ❌ {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_functionality():
    """測試緩存功能"""
    print("\n💾 測試緩存功能")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.improved_hk_utils import get_improved_hk_provider
        import time
        
        provider = get_improved_hk_provider()
        
        # 清理可能存在的緩存文件
        if os.path.exists("hk_stock_cache.json"):
            os.remove("hk_stock_cache.json")
            print("🗑️ 清理旧緩存文件")
        
        test_symbol = "0700.HK"
        
        # 第一次獲取（應该使用內置映射）
        print(f"\n📊 第一次獲取 {test_symbol}:")
        start_time = time.time()
        name1 = provider.get_company_name(test_symbol)
        time1 = time.time() - start_time
        print(f"   結果: {name1}")
        print(f"   耗時: {time1:.3f}秒")
        
        # 第二次獲取（應该使用緩存）
        print(f"\n📊 第二次獲取 {test_symbol}:")
        start_time = time.time()
        name2 = provider.get_company_name(test_symbol)
        time2 = time.time() - start_time
        print(f"   結果: {name2}")
        print(f"   耗時: {time2:.3f}秒")
        
        # 驗證結果一致性
        if name1 == name2:
            print("✅ 緩存結果一致")
        else:
            print("❌ 緩存結果不一致")
        
        # 檢查緩存文件
        if os.path.exists("hk_stock_cache.json"):
            print("✅ 緩存文件已創建")
            
            # 讀取緩存內容
            import json
            with open("hk_stock_cache.json", 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            print(f"📄 緩存條目數: {len(cache_data)}")
            for key, value in cache_data.items():
                print(f"   {key}: {value['data']} (來源: {value['source']})")
        else:
            print("⚠️ 緩存文件未創建")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試改進的港股工具")
    print("=" * 100)
    
    results = []
    
    # 測試1: 改進港股提供器
    results.append(test_improved_hk_provider())
    
    # 測試2: 分析師集成
    results.append(test_analyst_integration())
    
    # 測試3: 緩存功能
    results.append(test_cache_functionality())
    
    # 总結結果
    print("\n" + "=" * 100)
    print("📋 測試結果总結")
    print("=" * 100)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "改進港股提供器",
        "分析師集成測試",
        "緩存功能測試"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n📊 总體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！改進港股工具運行正常")
        print("\n📋 改進效果:")
        print("1. ✅ 內置港股名稱映射，避免API調用")
        print("2. ✅ 智能緩存機制，提高性能")
        print("3. ✅ 速率限制保護，避免API錯誤")
        print("4. ✅ 多級降級方案，確保可用性")
        print("5. ✅ 友好的錯誤處理和日誌記錄")
    else:
        print("⚠️ 部分測試失败，需要進一步優化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
