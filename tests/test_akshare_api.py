#!/usr/bin/env python3
"""
直接測試AKShare API
"""

import akshare as ak
import logging

# 設置日誌級別
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')

def test_akshare_apis():
    """測試AKShare各個財務數據API"""
    print("=" * 60)
    print("🔍 直接測試AKShare財務數據API")
    print("=" * 60)
    
    symbol = "600519"
    
    # 1. 測試主要財務指標API
    print(f"\n1. 測試主要財務指標API: stock_financial_abstract")
    try:
        data = ak.stock_financial_abstract(symbol=symbol)
        if data is not None and not data.empty:
            print(f"✅ 成功獲取主要財務指標: {len(data)}條記錄")
            print(f"   列名: {list(data.columns)}")
            print(f"   前3行數據:")
            print(data.head(3))
        else:
            print("❌ 主要財務指標為空")
    except Exception as e:
        print(f"❌ 主要財務指標API失败: {e}")
    
    # 2. 測試資產负债表API
    print(f"\n2. 測試資產负债表API: stock_balance_sheet_by_report_em")
    try:
        data = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        if data is not None and not data.empty:
            print(f"✅ 成功獲取資產负债表: {len(data)}條記錄")
            print(f"   列名: {list(data.columns)}")
        else:
            print("❌ 資產负债表為空")
    except Exception as e:
        print(f"❌ 資產负债表API失败: {e}")
    
    # 3. 測試利润表API
    print(f"\n3. 測試利润表API: stock_profit_sheet_by_report_em")
    try:
        data = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        if data is not None and not data.empty:
            print(f"✅ 成功獲取利润表: {len(data)}條記錄")
            print(f"   列名: {list(data.columns)}")
        else:
            print("❌ 利润表為空")
    except Exception as e:
        print(f"❌ 利润表API失败: {e}")
    
    # 4. 測試現金流量表API
    print(f"\n4. 測試現金流量表API: stock_cash_flow_sheet_by_report_em")
    try:
        data = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        if data is not None and not data.empty:
            print(f"✅ 成功獲取現金流量表: {len(data)}條記錄")
            print(f"   列名: {list(data.columns)}")
        else:
            print("❌ 現金流量表為空")
    except Exception as e:
        print(f"❌ 現金流量表API失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API測試完成")
    print("=" * 60)

if __name__ == "__main__":
    test_akshare_apis()