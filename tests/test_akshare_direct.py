#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接測試AKShare財務數據獲取功能
"""

import akshare as ak
import pandas as pd

def test_akshare_financial_apis():
    """測試AKShare財務數據API"""
    print("=" * 60)
    print("🧪 直接測試AKShare財務數據API")
    print("=" * 60)
    
    symbol = '000001'
    print(f"🔍 測試股票: {symbol}")
    
    # 測試資產负债表
    try:
        print("\n📊 測試資產负债表...")
        balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        if not balance_sheet.empty:
            print(f"✅ 資產负债表獲取成功，共{len(balance_sheet)}條記錄")
            print(f"📅 最新報告期: {balance_sheet.iloc[0]['報告期']}")
        else:
            print("❌ 資產负债表為空")
    except Exception as e:
        print(f"❌ 資產负债表獲取失败: {e}")
    
    # 測試利润表
    try:
        print("\n📊 測試利润表...")
        income_statement = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        if not income_statement.empty:
            print(f"✅ 利润表獲取成功，共{len(income_statement)}條記錄")
            print(f"📅 最新報告期: {income_statement.iloc[0]['報告期']}")
        else:
            print("❌ 利润表為空")
    except Exception as e:
        print(f"❌ 利润表獲取失败: {e}")
    
    # 測試現金流量表
    try:
        print("\n📊 測試現金流量表...")
        cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        if not cash_flow.empty:
            print(f"✅ 現金流量表獲取成功，共{len(cash_flow)}條記錄")
            print(f"📅 最新報告期: {cash_flow.iloc[0]['報告期']}")
        else:
            print("❌ 現金流量表為空")
    except Exception as e:
        print(f"❌ 現金流量表獲取失败: {e}")
    
    # 測試主要財務指標
    try:
        print("\n📊 測試主要財務指標...")
        main_indicators = ak.stock_financial_abstract_ths(symbol=symbol)
        if not main_indicators.empty:
            print(f"✅ 主要財務指標獲取成功，共{len(main_indicators)}條記錄")
            print("📈 主要指標:")
            for col in main_indicators.columns[:5]:  # 顯示前5列
                print(f"   {col}: {main_indicators.iloc[0][col]}")
        else:
            print("❌ 主要財務指標為空")
    except Exception as e:
        print(f"❌ 主要財務指標獲取失败: {e}")

def test_akshare_stock_info():
    """測試AKShare股票基本信息"""
    print("\n" + "=" * 60)
    print("📋 測試AKShare股票基本信息")
    print("=" * 60)
    
    symbol = '000001'
    print(f"🔍 測試股票: {symbol}")
    
    try:
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        if not stock_info.empty:
            print(f"✅ 股票信息獲取成功")
            print("📋 基本信息:")
            for _, row in stock_info.head(10).iterrows():  # 顯示前10項
                print(f"   {row['item']}: {row['value']}")
        else:
            print("❌ 股票信息為空")
    except Exception as e:
        print(f"❌ 股票信息獲取失败: {e}")

def main():
    """主測試函數"""
    print("🚀 開始直接測試AKShare財務數據API")
    print()
    
    test_akshare_financial_apis()
    test_akshare_stock_info()
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")
    print("=" * 60)

if __name__ == "__main__":
    main()