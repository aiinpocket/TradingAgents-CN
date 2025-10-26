#!/usr/bin/env python3
"""
股票基本信息獲取測試腳本
專門測試股票名稱、行業等基本信息的獲取功能
"""

import sys
import os

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_stock_info_retrieval():
    """測試股票基本信息獲取功能"""
    print("🔍 測試股票基本信息獲取功能")
    print("=" * 50)
    
    # 測試股票代碼
    test_codes = ["603985", "000001", "300033"]
    
    for code in test_codes:
        print(f"\n📊 測試股票代碼: {code}")
        print("-" * 30)
        
        try:
            # 1. 測試Tushare股票信息獲取
            print(f"🔍 步骤1: 測試Tushare股票信息獲取...")
            from tradingagents.dataflows.interface import get_china_stock_info_tushare
            tushare_info = get_china_stock_info_tushare(code)
            print(f"✅ Tushare信息: {tushare_info}")
            
            # 2. 測試統一股票信息獲取
            print(f"🔍 步骤2: 測試統一股票信息獲取...")
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            unified_info = get_china_stock_info_unified(code)
            print(f"✅ 統一信息: {unified_info}")
            
            # 3. 測試DataSourceManager直接調用
            print(f"🔍 步骤3: 測試DataSourceManager...")
            from tradingagents.dataflows.data_source_manager import get_china_stock_info_unified as manager_info
            manager_result = manager_info(code)
            print(f"✅ Manager結果: {manager_result}")
            
            # 4. 測試TushareAdapter直接調用
            print(f"🔍 步骤4: 測試TushareAdapter...")
            from tradingagents.dataflows.tushare_adapter import get_tushare_adapter
            adapter = get_tushare_adapter()
            adapter_result = adapter.get_stock_info(code)
            print(f"✅ Adapter結果: {adapter_result}")
            
            # 5. 測試TushareProvider直接調用
            print(f"🔍 步骤5: 測試TushareProvider...")
            from tradingagents.dataflows.tushare_utils import TushareProvider
            provider = TushareProvider()
            provider_result = provider.get_stock_info(code)
            print(f"✅ Provider結果: {provider_result}")
            
        except Exception as e:
            print(f"❌ 測試{code}失败: {e}")
            import traceback
            traceback.print_exc()

def test_tushare_stock_basic_api():
    """直接測試Tushare的stock_basic API"""
    print("\n🔍 直接測試Tushare stock_basic API")
    print("=" * 50)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return
        
        # 測試stock_basic API
        test_codes = ["603985", "000001", "300033"]
        
        for code in test_codes:
            print(f"\n📊 測試股票代碼: {code}")
            
            # 轉換為Tushare格式
            ts_code = provider._normalize_symbol(code)
            print(f"🔍 轉換後的代碼: {ts_code}")
            
            # 直接調用API
            try:
                basic_info = provider.api.stock_basic(
                    ts_code=ts_code,
                    fields='ts_code,symbol,name,area,industry,market,list_date'
                )
                
                print(f"✅ API返回數據形狀: {basic_info.shape if basic_info is not None else 'None'}")
                
                if basic_info is not None and not basic_info.empty:
                    print(f"📊 返回數據:")
                    print(basic_info.to_dict('records'))
                else:
                    print("❌ API返回空數據")
                    
            except Exception as e:
                print(f"❌ API調用失败: {e}")
                
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

def test_stock_basic_all():
    """測試獲取所有股票基本信息"""
    print("\n🔍 測試獲取所有股票基本信息")
    print("=" * 50)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return
        
        # 獲取所有A股基本信息
        print("🔍 獲取所有A股基本信息...")
        all_stocks = provider.api.stock_basic(
            exchange='',
            list_status='L',
            fields='ts_code,symbol,name,area,industry,market,list_date'
        )
        
        print(f"✅ 獲取到{len(all_stocks)}只股票")
        
        # 查找測試股票
        test_codes = ["603985", "000001", "300033"]
        
        for code in test_codes:
            print(f"\n📊 查找股票: {code}")
            
            # 在所有股票中查找
            found_stocks = all_stocks[all_stocks['symbol'] == code]
            
            if not found_stocks.empty:
                stock_info = found_stocks.iloc[0]
                print(f"✅ 找到股票:")
                print(f"   代碼: {stock_info['symbol']}")
                print(f"   名稱: {stock_info['name']}")
                print(f"   行業: {stock_info['industry']}")
                print(f"   地区: {stock_info['area']}")
                print(f"   市場: {stock_info['market']}")
                print(f"   上市日期: {stock_info['list_date']}")
            else:
                print(f"❌ 未找到股票: {code}")
                
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 股票基本信息獲取測試")
    print("=" * 80)
    print("📝 此測試專門檢查股票名稱、行業等基本信息的獲取")
    print("=" * 80)
    
    # 1. 測試股票信息獲取鏈路
    test_stock_info_retrieval()
    
    # 2. 直接測試Tushare API
    test_tushare_stock_basic_api()
    
    # 3. 測試獲取所有股票信息
    test_stock_basic_all()
    
    print("\n📋 測試总結")
    print("=" * 60)
    print("✅ 股票基本信息測試完成")
    print("🔍 如果發現問題，請檢查:")
    print("   - Tushare API連接狀態")
    print("   - 股票代碼格式轉換")
    print("   - API返回數據解析")
    print("   - 緩存機制影響")
