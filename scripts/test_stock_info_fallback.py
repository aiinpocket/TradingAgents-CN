#!/usr/bin/env python3
"""
測試股票基本信息獲取的降級機制
驗證當Tushare失败時是否有备用方案
"""

import sys
import os

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tushare_stock_info_failure():
    """測試Tushare股票信息獲取失败的情况"""
    print("🔍 測試Tushare股票信息獲取失败情况")
    print("=" * 50)
    
    # 測試不存在的股票代碼
    fake_codes = ["999999", "888888", "777777"]
    
    for code in fake_codes:
        print(f"\n📊 測試不存在的股票代碼: {code}")
        print("-" * 30)
        
        try:
            # 1. 測試Tushare直接獲取
            print(f"🔍 步骤1: 測試Tushare直接獲取...")
            from tradingagents.dataflows.interface import get_china_stock_info_tushare
            tushare_result = get_china_stock_info_tushare(code)
            print(f"✅ Tushare結果: {tushare_result}")
            
            # 2. 測試統一接口
            print(f"🔍 步骤2: 測試統一接口...")
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            unified_result = get_china_stock_info_unified(code)
            print(f"✅ 統一接口結果: {unified_result}")
            
            # 3. 檢查是否有降級機制
            if "❌" in tushare_result and "❌" in unified_result:
                print("❌ 確認：没有降級到其他數據源")
            elif "❌" in tushare_result and "❌" not in unified_result:
                print("✅ 有降級機制：統一接口成功獲取數據")
            else:
                print("🤔 結果不明確")
                
        except Exception as e:
            print(f"❌ 測試{code}失败: {e}")

def test_akshare_stock_info():
    """測試AKShare是否支持股票基本信息獲取"""
    print("\n🔍 測試AKShare股票基本信息獲取能力")
    print("=" * 50)
    
    test_codes = ["603985", "000001", "300033"]
    
    for code in test_codes:
        print(f"\n📊 測試股票代碼: {code}")
        print("-" * 30)
        
        try:
            # 直接測試AKShare
            import akshare as ak
            
            # 嘗試獲取股票基本信息
            try:
                # 方法1: 股票信息
                stock_info = ak.stock_individual_info_em(symbol=code)
                print(f"✅ AKShare個股信息: {stock_info.head() if not stock_info.empty else '空數據'}")
            except Exception as e:
                print(f"❌ AKShare個股信息失败: {e}")
            
            try:
                # 方法2: 股票基本信息
                stock_basic = ak.stock_zh_a_spot_em()
                stock_data = stock_basic[stock_basic['代碼'] == code]
                if not stock_data.empty:
                    print(f"✅ AKShare基本信息: {stock_data[['代碼', '名稱', '涨跌幅', '現價']].iloc[0].to_dict()}")
                else:
                    print(f"❌ AKShare基本信息: 未找到{code}")
            except Exception as e:
                print(f"❌ AKShare基本信息失败: {e}")
                
        except Exception as e:
            print(f"❌ AKShare測試失败: {e}")

def test_baostock_stock_info():
    """測試BaoStock是否支持股票基本信息獲取"""
    print("\n🔍 測試BaoStock股票基本信息獲取能力")
    print("=" * 50)
    
    test_codes = ["sh.603985", "sz.000001", "sz.300033"]
    
    try:
        import baostock as bs
        
        # 登錄BaoStock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"❌ BaoStock登錄失败: {lg.error_msg}")
            return
        
        print("✅ BaoStock登錄成功")
        
        for code in test_codes:
            print(f"\n📊 測試股票代碼: {code}")
            print("-" * 30)
            
            try:
                # 獲取股票基本信息
                rs = bs.query_stock_basic(code=code)
                if rs.error_code == '0':
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if data_list:
                        print(f"✅ BaoStock基本信息: {data_list[0]}")
                    else:
                        print(f"❌ BaoStock基本信息: 無數據")
                else:
                    print(f"❌ BaoStock查詢失败: {rs.error_msg}")
                    
            except Exception as e:
                print(f"❌ BaoStock測試失败: {e}")
        
        # 登出
        bs.logout()
        
    except ImportError:
        print("❌ BaoStock未安裝")
    except Exception as e:
        print(f"❌ BaoStock測試失败: {e}")

def analyze_current_fallback_mechanism():
    """分析當前的降級機制"""
    print("\n🔍 分析當前降級機制")
    print("=" * 50)
    
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        
        # 檢查DataSourceManager的方法
        manager = DataSourceManager()
        
        print("📊 DataSourceManager可用方法:")
        methods = [method for method in dir(manager) if not method.startswith('_')]
        for method in methods:
            print(f"   - {method}")
        
        # 檢查是否有股票信息的降級方法
        if hasattr(manager, '_try_fallback_sources'):
            print("✅ 有_try_fallback_sources方法 (用於歷史數據)")
        else:
            print("❌ 没有_try_fallback_sources方法")
        
        if hasattr(manager, '_try_fallback_stock_info'):
            print("✅ 有_try_fallback_stock_info方法 (用於基本信息)")
        else:
            print("❌ 没有_try_fallback_stock_info方法")
        
        # 檢查get_stock_info方法的實現
        import inspect
        source = inspect.getsource(manager.get_stock_info)
        print(f"\n📝 get_stock_info方法源碼:")
        print(source)
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    print("🧪 股票基本信息降級機制測試")
    print("=" * 80)
    print("📝 此測試檢查當Tushare失败時是否有备用數據源")
    print("=" * 80)
    
    # 1. 測試Tushare失败情况
    test_tushare_stock_info_failure()
    
    # 2. 測試AKShare能力
    test_akshare_stock_info()
    
    # 3. 測試BaoStock能力
    test_baostock_stock_info()
    
    # 4. 分析當前機制
    analyze_current_fallback_mechanism()
    
    print("\n📋 測試总結")
    print("=" * 60)
    print("🔍 如果發現没有降級機制，需要:")
    print("   1. 為get_stock_info添加降級逻辑")
    print("   2. 實現AKShare/BaoStock的股票信息獲取")
    print("   3. 確保基本面分析能獲取到股票名稱")
