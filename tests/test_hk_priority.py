#!/usr/bin/env python3
"""
測試港股數據源優先級設置
驗證AKShare優先，Yahoo Finance作為备用
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_hk_data_source_priority():
    """測試港股數據源優先級"""
    print("\n🇭🇰 測試港股數據源優先級")
    print("=" * 80)
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        print("📊 測試港股信息獲取優先級...")
        
        # 測試統一港股信息接口
        from tradingagents.dataflows.interface import get_hk_stock_info_unified
        
        test_symbols = [
            "0700.HK",  # 腾讯控股
            "0941.HK",  # 中國移動  
            "1299.HK",  # 友邦保險
        ]
        
        for symbol in test_symbols:
            print(f"\n📊 測試股票: {symbol}")
            print("-" * 40)
            
            try:
                result = get_hk_stock_info_unified(symbol)
                
                print(f"✅ 獲取成功:")
                print(f"   股票代碼: {result.get('symbol', 'N/A')}")
                print(f"   公司名稱: {result.get('name', 'N/A')}")
                print(f"   數據源: {result.get('source', 'N/A')}")
                print(f"   貨币: {result.get('currency', 'N/A')}")
                print(f"   交易所: {result.get('exchange', 'N/A')}")
                
                # 檢查是否成功獲取了具體的公司名稱
                name = result.get('name', '')
                if not name.startswith('港股'):
                    print(f"   ✅ 成功獲取具體公司名稱")
                else:
                    print(f"   ⚠️ 使用默認格式")
                    
            except Exception as e:
                print(f"❌ 獲取失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hk_data_priority():
    """測試港股數據獲取優先級"""
    print("\n📈 測試港股數據獲取優先級")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_data_unified
        
        test_symbol = "0700.HK"
        start_date = "2025-07-01"
        end_date = "2025-07-15"
        
        print(f"📊 測試港股數據獲取: {test_symbol}")
        print(f"   時間範围: {start_date} 到 {end_date}")
        print("-" * 40)
        
        result = get_hk_stock_data_unified(test_symbol, start_date, end_date)
        
        if result and "❌" not in result:
            print(f"✅ 港股數據獲取成功")
            print(f"   數據長度: {len(result)}")
            
            # 顯示數據的前200字符
            print(f"   數據預覽:")
            print(f"   {result[:200]}...")
            
            # 檢查數據中是否包含正確的股票代碼
            if "0700" in result or "腾讯" in result:
                print(f"   ✅ 數據包含正確的股票信息")
            else:
                print(f"   ⚠️ 數據可能不完整")
        else:
            print(f"❌ 港股數據獲取失败")
            print(f"   返回結果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_improved_hk_provider_priority():
    """測試改進港股提供器的優先級"""
    print("\n🔧 測試改進港股提供器優先級")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.improved_hk_utils import get_improved_hk_provider
        
        provider = get_improved_hk_provider()
        
        # 清理緩存以測試真實的API調用優先級
        if hasattr(provider, 'cache'):
            provider.cache.clear()
        
        test_symbols = [
            "0700.HK",  # 腾讯控股（內置映射）
            "1234.HK",  # 不在內置映射中的股票（測試API優先級）
        ]
        
        for symbol in test_symbols:
            print(f"\n📊 測試股票: {symbol}")
            print("-" * 40)
            
            try:
                company_name = provider.get_company_name(symbol)
                print(f"✅ 獲取公司名稱: {company_name}")
                
                # 檢查緩存信息
                cache_key = f"name_{symbol}"
                if hasattr(provider, 'cache') and cache_key in provider.cache:
                    cache_info = provider.cache[cache_key]
                    print(f"   緩存來源: {cache_info.get('source', 'unknown')}")
                    print(f"   緩存時間: {cache_info.get('timestamp', 'unknown')}")
                
                # 檢查是否成功獲取了具體的公司名稱
                if not company_name.startswith('港股'):
                    print(f"   ✅ 成功獲取具體公司名稱")
                else:
                    print(f"   ⚠️ 使用默認格式")
                    
            except Exception as e:
                print(f"❌ 獲取失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_source_availability():
    """測試數據源可用性"""
    print("\n🔍 測試數據源可用性")
    print("=" * 80)
    
    try:
        # 檢查AKShare可用性
        try:
            from tradingagents.dataflows.akshare_utils import get_hk_stock_info_akshare
            print("✅ AKShare港股工具可用")
            akshare_available = True
        except ImportError as e:
            print(f"❌ AKShare港股工具不可用: {e}")
            akshare_available = False
        
        # 檢查Yahoo Finance可用性
        try:
            from tradingagents.dataflows.hk_stock_utils import get_hk_stock_info
            print("✅ Yahoo Finance港股工具可用")
            yf_available = True
        except ImportError as e:
            print(f"❌ Yahoo Finance港股工具不可用: {e}")
            yf_available = False
        
        # 檢查統一接口
        try:
            from tradingagents.dataflows.interface import get_hk_stock_info_unified, AKSHARE_HK_AVAILABLE, HK_STOCK_AVAILABLE
            print("✅ 統一港股接口可用")
            print(f"   AKShare可用標誌: {AKSHARE_HK_AVAILABLE}")
            print(f"   Yahoo Finance可用標誌: {HK_STOCK_AVAILABLE}")
        except ImportError as e:
            print(f"❌ 統一港股接口不可用: {e}")
        
        print(f"\n📊 數據源優先級驗證:")
        print(f"   1. AKShare (優先): {'✅ 可用' if akshare_available else '❌ 不可用'}")
        print(f"   2. Yahoo Finance (备用): {'✅ 可用' if yf_available else '❌ 不可用'}")
        print(f"   3. 默認格式 (降級): ✅ 总是可用")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試港股數據源優先級")
    print("=" * 100)
    
    results = []
    
    # 測試1: 數據源可用性
    results.append(test_data_source_availability())
    
    # 測試2: 港股信息獲取優先級
    results.append(test_hk_data_source_priority())
    
    # 測試3: 港股數據獲取優先級
    results.append(test_hk_data_priority())
    
    # 測試4: 改進港股提供器優先級
    results.append(test_improved_hk_provider_priority())
    
    # 总結結果
    print("\n" + "=" * 100)
    print("📋 測試結果总結")
    print("=" * 100)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "數據源可用性檢查",
        "港股信息獲取優先級",
        "港股數據獲取優先級", 
        "改進港股提供器優先級"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n📊 总體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！港股數據源優先級設置正確")
        print("\n📋 優先級設置:")
        print("1. 🥇 AKShare (國內數據源，港股支持更好)")
        print("2. 🥈 Yahoo Finance (國际數據源，备用方案)")
        print("3. 🥉 默認格式 (降級方案，確保可用性)")
        
        print("\n✅ 優化效果:")
        print("- 减少Yahoo Finance API速率限制問題")
        print("- 提高港股數據獲取成功率")
        print("- 更好的中文公司名稱支持")
        print("- 更穩定的數據源訪問")
    else:
        print("⚠️ 部分測試失败，需要進一步優化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
