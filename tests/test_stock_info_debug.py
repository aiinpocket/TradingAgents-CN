#!/usr/bin/env python3
"""
股票信息獲取調試測試
專門診斷為什么某些股票顯示"未知公司"
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_stock_code_normalization():
    """測試股票代碼標準化"""
    print("\n🔧 測試股票代碼標準化")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        provider = get_tushare_provider()
        
        test_codes = ["000858", "600036", "000001", "300001"]
        
        for code in test_codes:
            normalized = provider._normalize_symbol(code)
            print(f"📊 {code} -> {normalized}")
        
        return True
        
    except Exception as e:
        print(f"❌ 股票代碼標準化測試失败: {e}")
        return False


def test_tushare_api_direct():
    """直接測試Tushare API"""
    print("\n🔧 直接測試Tushare API")
    print("=" * 60)
    
    try:
        import tushare as ts
        import os
        
        token = os.getenv('TUSHARE_TOKEN')
        if not token:
            print("❌ TUSHARE_TOKEN未設置")
            return False
        
        ts.set_token(token)
        pro = ts.pro_api()
        
        # 測試獲取000858的信息
        print("🔄 測試獲取000858.SZ的基本信息...")
        
        try:
            basic_info = pro.stock_basic(
                ts_code='000858.SZ',
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            
            if not basic_info.empty:
                info = basic_info.iloc[0]
                print(f"✅ 找到股票信息:")
                print(f"   代碼: {info['ts_code']}")
                print(f"   名稱: {info['name']}")
                print(f"   行業: {info.get('industry', 'N/A')}")
                print(f"   地区: {info.get('area', 'N/A')}")
                return True
            else:
                print("❌ 未找到000858.SZ的信息")
                
                # 嘗試搜索所有包含858的股票
                print("🔄 搜索所有包含858的股票...")
                all_stocks = pro.stock_basic(
                    exchange='',
                    list_status='L',
                    fields='ts_code,symbol,name,area,industry,market,list_date'
                )
                
                matches = all_stocks[all_stocks['symbol'].str.contains('858', na=False)]
                if not matches.empty:
                    print(f"✅ 找到{len(matches)}只包含858的股票:")
                    for idx, row in matches.iterrows():
                        print(f"   {row['ts_code']} - {row['name']}")
                else:
                    print("❌ 未找到任何包含858的股票")
                
                return False
                
        except Exception as e:
            print(f"❌ API調用失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Tushare API測試失败: {e}")
        return False


def test_stock_list_search():
    """測試股票列表搜索"""
    print("\n🔧 測試股票列表搜索")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return False
        
        # 獲取股票列表
        print("🔄 獲取完整股票列表...")
        stock_list = provider.get_stock_list()
        
        if stock_list.empty:
            print("❌ 股票列表為空")
            return False
        
        print(f"✅ 獲取到{len(stock_list)}只股票")
        
        # 搜索000858
        print("🔄 搜索000858...")
        matches = stock_list[stock_list['symbol'] == '000858']
        
        if not matches.empty:
            print("✅ 找到000858:")
            for idx, row in matches.iterrows():
                print(f"   {row['ts_code']} - {row['name']} - {row.get('industry', 'N/A')}")
        else:
            print("❌ 在股票列表中未找到000858")
            
            # 搜索包含858的股票
            partial_matches = stock_list[stock_list['symbol'].str.contains('858', na=False)]
            if not partial_matches.empty:
                print(f"✅ 找到{len(partial_matches)}只包含858的股票:")
                for idx, row in partial_matches.head(5).iterrows():
                    print(f"   {row['ts_code']} - {row['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 股票列表搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alternative_stock_codes():
    """測試其他股票代碼"""
    print("\n🔧 測試其他股票代碼")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_adapter import get_tushare_adapter
        
        adapter = get_tushare_adapter()
        
        # 測試几個已知的股票代碼
        test_codes = [
            ("000001", "平安銀行"),
            ("600036", "招商銀行"),
            ("000002", "万科A"),
            ("600519", "贵州茅台"),
            ("000858", "五粮液")  # 這個可能是問題代碼
        ]
        
        for code, expected_name in test_codes:
            print(f"🔄 測試 {code} (期望: {expected_name})...")
            
            info = adapter.get_stock_info(code)
            
            if info and info.get('name') and info['name'] != f'股票{code}':
                print(f"✅ {code}: {info['name']}")
                if expected_name in info['name']:
                    print(f"   ✅ 名稱匹配")
                else:
                    print(f"   ⚠️ 名稱不匹配，期望: {expected_name}")
            else:
                print(f"❌ {code}: 獲取失败或返回未知")
        
        return True
        
    except Exception as e:
        print(f"❌ 其他股票代碼測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔍 股票信息獲取調試測試")
    print("=" * 70)
    print("💡 調試目標:")
    print("   - 診斷為什么000858顯示'未知公司'")
    print("   - 檢查股票代碼標準化")
    print("   - 驗證Tushare API響應")
    print("   - 測試股票列表搜索")
    print("=" * 70)
    
    # 運行所有測試
    tests = [
        ("股票代碼標準化", test_stock_code_normalization),
        ("Tushare API直接測試", test_tushare_api_direct),
        ("股票列表搜索", test_stock_list_search),
        ("其他股票代碼測試", test_alternative_stock_codes)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}測試異常: {e}")
            results.append((test_name, False))
    
    # 总結
    print("\n📋 股票信息調試測試总結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！")
        print("💡 如果000858仍顯示未知，可能是:")
        print("   1. 该股票代碼在Tushare中不存在")
        print("   2. 股票已退市或暂停交易")
        print("   3. 需要使用不同的查詢方式")
    else:
        print("\n⚠️ 部分測試失败，請檢查具體問題")
    
    input("按回車键退出...")


if __name__ == "__main__":
    main()
