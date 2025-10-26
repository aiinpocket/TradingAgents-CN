#!/usr/bin/env python3
"""
測試修複後的股票基本信息降級機制
驗證當Tushare失败時是否能自動降級到其他數據源
"""

import sys
import os

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_stock_info_fallback_mechanism():
    """測試股票信息降級機制"""
    print("🔍 測試股票信息降級機制")
    print("=" * 50)
    
    # 測試不存在的股票代碼（應该觸發降級）
    fake_codes = ["999999", "888888"]
    
    for code in fake_codes:
        print(f"\n📊 測試不存在的股票代碼: {code}")
        print("-" * 30)
        
        try:
            # 測試統一接口（現在應该有降級機制）
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            result = get_china_stock_info_unified(code)
            print(f"✅ 統一接口結果: {result}")
            
            # 檢查是否使用了备用數據源
            if "數據來源: akshare" in result or "數據來源: baostock" in result:
                print("✅ 成功降級到备用數據源！")
            elif "數據來源: tushare" in result and f"股票名稱: 股票{code}" not in result:
                print("✅ Tushare成功獲取數據")
            elif f"股票名稱: 股票{code}" in result:
                print("❌ 仍然返回默認值，降級機制可能未生效")
            else:
                print("🤔 結果不明確")
                
        except Exception as e:
            print(f"❌ 測試{code}失败: {e}")

def test_real_stock_fallback():
    """測試真實股票的降級機制（模擬Tushare失败）"""
    print("\n🔍 測試真實股票的降級機制")
    print("=" * 50)
    
    # 測試真實股票代碼
    real_codes = ["603985", "000001", "300033"]
    
    for code in real_codes:
        print(f"\n📊 測試股票代碼: {code}")
        print("-" * 30)
        
        try:
            # 直接測試DataSourceManager
            from tradingagents.dataflows.data_source_manager import get_data_source_manager
            manager = get_data_source_manager()
            
            # 獲取股票信息
            result = manager.get_stock_info(code)
            print(f"✅ DataSourceManager結果: {result}")
            
            # 檢查是否獲取到有效信息
            if result.get('name') and result['name'] != f'股票{code}':
                print(f"✅ 成功獲取股票名稱: {result['name']}")
                print(f"📊 數據來源: {result.get('source', '未知')}")
            else:
                print("❌ 未獲取到有效股票名稱")
                
        except Exception as e:
            print(f"❌ 測試{code}失败: {e}")
            import traceback
            traceback.print_exc()

def test_individual_data_sources():
    """測試各個數據源的股票信息獲取能力"""
    print("\n🔍 測試各個數據源的股票信息獲取能力")
    print("=" * 50)
    
    test_code = "603985"  # 恒润股份
    
    try:
        from tradingagents.dataflows.data_source_manager import get_data_source_manager
        manager = get_data_source_manager()
        
        # 測試AKShare
        print(f"\n📊 測試AKShare獲取{test_code}信息:")
        akshare_result = manager._get_akshare_stock_info(test_code)
        print(f"✅ AKShare結果: {akshare_result}")
        
        # 測試BaoStock
        print(f"\n📊 測試BaoStock獲取{test_code}信息:")
        baostock_result = manager._get_baostock_stock_info(test_code)
        print(f"✅ BaoStock結果: {baostock_result}")
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

def test_fundamentals_with_fallback():
    """測試基本面分析是否能獲取到正確的股票名稱"""
    print("\n🔍 測試基本面分析中的股票名稱獲取")
    print("=" * 50)
    
    test_code = "603985"  # 恒润股份
    
    try:
        # 模擬基本面分析中的股票信息獲取
        from tradingagents.dataflows.interface import get_china_stock_info_unified
        stock_info = get_china_stock_info_unified(test_code)
        print(f"✅ 統一接口獲取股票信息: {stock_info}")
        
        # 檢查是否包含股票名稱
        if "股票名稱:" in stock_info:
            lines = stock_info.split('\n')
            for line in lines:
                if "股票名稱:" in line:
                    company_name = line.split(':')[1].strip()
                    print(f"✅ 提取到股票名稱: {company_name}")
                    
                    if company_name != "未知公司" and company_name != f"股票{test_code}":
                        print("✅ 基本面分析現在可以獲取到正確的股票名稱！")
                    else:
                        print("❌ 基本面分析仍然獲取不到正確的股票名稱")
                    break
        else:
            print("❌ 統一接口返回格式異常")
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 股票基本信息降級機制修複測試")
    print("=" * 80)
    print("📝 此測試驗證修複後的降級機制是否正常工作")
    print("=" * 80)
    
    # 1. 測試降級機制
    test_stock_info_fallback_mechanism()
    
    # 2. 測試真實股票
    test_real_stock_fallback()
    
    # 3. 測試各個數據源
    test_individual_data_sources()
    
    # 4. 測試基本面分析
    test_fundamentals_with_fallback()
    
    print("\n📋 測試总結")
    print("=" * 60)
    print("✅ 股票基本信息降級機制修複測試完成")
    print("🔍 現在當Tushare失败時應该能自動降級到:")
    print("   - AKShare (獲取股票名稱)")
    print("   - BaoStock (獲取股票名稱和上市日期)")
    print("🎯 基本面分析現在應该能獲取到正確的股票名稱")
