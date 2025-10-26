#!/usr/bin/env python3
"""
檢查AKShare財務數據結構
"""

import sys
import os
import logging

# 設置日誌級別
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.akshare_utils import AKShareProvider

def analyze_akshare_data():
    """分析AKShare財務數據結構"""
    print("=" * 60)
    print("🔍 分析AKShare財務數據結構")
    print("=" * 60)
    
    provider = AKShareProvider()
    if not provider.connected:
        print("❌ AKShare未連接")
        return
    
    symbol = "600519"
    financial_data = provider.get_financial_data(symbol)
    
    if not financial_data:
        print("❌ 未獲取到財務數據")
        return
    
    main_indicators = financial_data.get('main_indicators')
    if main_indicators is None:
        print("❌ 未獲取到主要財務指標")
        return
    
    print(f"\n📊 主要財務指標數據結構分析:")
    print(f"   數據類型: {type(main_indicators)}")
    print(f"   數據形狀: {main_indicators.shape}")
    print(f"   列名: {list(main_indicators.columns)}")
    
    print(f"\n📋 前5行數據:")
    print(main_indicators.head())
    
    print(f"\n🔍 查找PE、PB、ROE相關指標:")
    
    # 查找包含關键詞的行
    pe_rows = main_indicators[main_indicators['指標'].str.contains('市盈率|PE', na=False, case=False)]
    pb_rows = main_indicators[main_indicators['指標'].str.contains('市净率|PB', na=False, case=False)]
    roe_rows = main_indicators[main_indicators['指標'].str.contains('净資產收益率|ROE', na=False, case=False)]
    
    # 獲取最新數據列（第3列，索引為2）
    latest_col = main_indicators.columns[2] if len(main_indicators.columns) > 2 else None
    print(f"   最新數據列: {latest_col}")
    
    print(f"\n📈 PE相關指標 ({len(pe_rows)}條):")
    if not pe_rows.empty:
        for _, row in pe_rows.iterrows():
            latest_value = row[latest_col] if latest_col else 'N/A'
            print(f"   {row['指標']}: {latest_value}")
    else:
        print("   未找到PE相關指標")
    
    print(f"\n📈 PB相關指標 ({len(pb_rows)}條):")
    if not pb_rows.empty:
        for _, row in pb_rows.iterrows():
            latest_value = row[latest_col] if latest_col else 'N/A'
            print(f"   {row['指標']}: {latest_value}")
    else:
        print("   未找到PB相關指標")
    
    print(f"\n📈 ROE相關指標 ({len(roe_rows)}條):")
    if not roe_rows.empty:
        for _, row in roe_rows.iterrows():
            latest_value = row[latest_col] if latest_col else 'N/A'
            print(f"   {row['指標']}: {latest_value}")
    else:
        print("   未找到ROE相關指標")
    
    # 專門查找ROE指標
    roe_exact = main_indicators[main_indicators['指標'] == '净資產收益率(ROE)']
    if not roe_exact.empty:
        roe_value = roe_exact.iloc[0][latest_col] if latest_col else 'N/A'
        print(f"\n🎯 精確匹配 - 净資產收益率(ROE): {roe_value}")
        
        # 顯示ROE的歷史數據（前5個季度）
        print(f"   歷史數據:")
        for i in range(2, min(7, len(main_indicators.columns))):
            col_name = main_indicators.columns[i]
            value = roe_exact.iloc[0][col_name]
            print(f"     {col_name}: {value}")
    
    # 查找可能的PE、PB替代指標
    print(f"\n🔍 查找可能的PE、PB替代指標:")
    
    # 查找每股相關指標
    eps_rows = main_indicators[main_indicators['指標'].str.contains('每股收益|每股净利润', na=False, case=False)]
    print(f"\n📈 每股收益相關指標 ({len(eps_rows)}條):")
    for _, row in eps_rows.iterrows():
        latest_value = row[latest_col] if latest_col else 'N/A'
        print(f"   {row['指標']}: {latest_value}")
    
    # 查找每股净資產相關指標
    bps_rows = main_indicators[main_indicators['指標'].str.contains('每股净資產', na=False, case=False)]
    print(f"\n📈 每股净資產相關指標 ({len(bps_rows)}條):")
    for _, row in bps_rows.iterrows():
        latest_value = row[latest_col] if latest_col else 'N/A'
        print(f"   {row['指標']}: {latest_value}")
    
    # 顯示所有指標名稱
    print(f"\n📋 所有指標名稱:")
    for i, indicator in enumerate(main_indicators['指標']):
        print(f"   {i:2d}. {indicator}")
    
    print("\n" + "=" * 60)
    print("✅ 數據結構分析完成")
    print("=" * 60)

if __name__ == "__main__":
    analyze_akshare_data()