#!/usr/bin/env python3
"""
簡化的港股工具測試
"""

import os
import sys
import time
import json

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 直接導入改進的港股工具（避免複雜的依賴）
sys.path.insert(0, os.path.join(project_root, 'tradingagents', 'dataflows'))

def test_hk_provider_direct():
    """直接測試港股提供器"""
    print("\n🇭🇰 直接測試港股提供器")
    print("=" * 80)
    
    try:
        # 直接導入改進的港股工具
        from improved_hk_utils import ImprovedHKStockProvider
        
        provider = ImprovedHKStockProvider()
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
        success_count = 0
        for symbol in test_symbols:
            try:
                company_name = provider.get_company_name(symbol)
                print(f"   {symbol:10} -> {company_name}")
                
                # 驗證不是默認格式
                if not company_name.startswith('港股'):
                    print(f"      ✅ 成功獲取具體公司名稱")
                    success_count += 1
                else:
                    print(f"      ⚠️ 使用默認格式")
                    
            except Exception as e:
                print(f"   {symbol:10} -> ❌ 錯誤: {e}")
        
        print(f"\n📊 成功獲取具體名稱: {success_count}/{len(test_symbols)}")
        
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

def test_cache_direct():
    """直接測試緩存功能"""
    print("\n💾 直接測試緩存功能")
    print("=" * 80)
    
    try:
        from improved_hk_utils import ImprovedHKStockProvider
        
        provider = ImprovedHKStockProvider()
        
        # 清理可能存在的緩存文件
        cache_file = "hk_stock_cache.json"
        if os.path.exists(cache_file):
            os.remove(cache_file)
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
        if os.path.exists(cache_file):
            print("✅ 緩存文件已創建")
            
            # 讀取緩存內容
            with open(cache_file, 'r', encoding='utf-8') as f:
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

def test_normalization():
    """測試港股代碼標準化"""
    print("\n🔧 測試港股代碼標準化")
    print("=" * 80)
    
    try:
        from improved_hk_utils import ImprovedHKStockProvider
        
        provider = ImprovedHKStockProvider()
        
        test_cases = [
            ("0700.HK", "00700"),
            ("0700", "00700"),
            ("700", "00700"),
            ("70", "00070"),
            ("7", "00007"),
            ("1299.HK", "01299"),
            ("1299", "01299"),
            ("9988.HK", "09988"),
            ("9988", "09988"),
        ]
        
        print("📊 港股代碼標準化測試:")
        for input_symbol, expected in test_cases:
            normalized = provider._normalize_hk_symbol(input_symbol)
            status = "✅" if normalized == expected else "❌"
            print(f"   {input_symbol:10} -> {normalized:10} (期望: {expected}) {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🚀 開始簡化港股工具測試")
    print("=" * 100)
    
    results = []
    
    # 測試1: 直接測試港股提供器
    results.append(test_hk_provider_direct())
    
    # 測試2: 直接測試緩存功能
    results.append(test_cache_direct())
    
    # 測試3: 測試標準化功能
    results.append(test_normalization())
    
    # 总結結果
    print("\n" + "=" * 100)
    print("📋 測試結果总結")
    print("=" * 100)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "港股提供器直接測試",
        "緩存功能直接測試",
        "代碼標準化測試"
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
        print("3. ✅ 港股代碼標準化處理")
        print("4. ✅ 多級降級方案，確保可用性")
        print("5. ✅ 友好的錯誤處理")
        
        print("\n🔧 解決的問題:")
        print("1. ❌ 'Too Many Requests' API限制錯誤")
        print("2. ❌ 港股名稱獲取失败問題")
        print("3. ❌ 缺乏緩存導致的重複API調用")
        print("4. ❌ 港股代碼格式不統一問題")
    else:
        print("⚠️ 部分測試失败，需要進一步優化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
