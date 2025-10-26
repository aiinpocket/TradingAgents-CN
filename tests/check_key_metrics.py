#!/usr/bin/env python3
"""
專門查看AKShare財務數據中的PE、PB、ROE指標
"""

import sys
import os
import logging

# 設置日誌級別
logging.basicConfig(level=logging.WARNING, format='%(asctime)s | %(levelname)-8s | %(message)s')

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.akshare_utils import AKShareProvider

def check_key_metrics():
    """檢查關键財務指標"""
    print("=" * 60)
    print("🔍 檢查AKShare關键財務指標")
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
    
    # 獲取最新數據列
    latest_col = main_indicators.columns[2]  # 第3列是最新數據
    print(f"📅 最新數據期間: {latest_col}")
    
    # 查找ROE
    roe_row = main_indicators[main_indicators['指標'] == '净資產收益率(ROE)']
    if not roe_row.empty:
        roe_value = roe_row.iloc[0][latest_col]
        print(f"📈 净資產收益率(ROE): {roe_value}")
    else:
        print("❌ 未找到ROE指標")
    
    # 查找每股收益（用於計算PE）
    eps_row = main_indicators[main_indicators['指標'] == '每股收益']
    if not eps_row.empty:
        eps_value = eps_row.iloc[0][latest_col]
        print(f"💰 每股收益(EPS): {eps_value}")
    else:
        print("❌ 未找到每股收益指標")
    
    # 查找每股净資產（用於計算PB）
    bps_row = main_indicators[main_indicators['指標'] == '每股净資產_最新股數']
    if not bps_row.empty:
        bps_value = bps_row.iloc[0][latest_col]
        print(f"📊 每股净資產(BPS): {bps_value}")
    else:
        print("❌ 未找到每股净資產指標")
    
    # 顯示所有包含"每股"的指標
    print(f"\n📋 所有每股相關指標:")
    eps_indicators = main_indicators[main_indicators['指標'].str.contains('每股', na=False)]
    for _, row in eps_indicators.iterrows():
        indicator_name = row['指標']
        value = row[latest_col]
        print(f"   {indicator_name}: {value}")
    
    # 顯示所有包含"收益率"的指標
    print(f"\n📋 所有收益率相關指標:")
    roe_indicators = main_indicators[main_indicators['指標'].str.contains('收益率', na=False)]
    for _, row in roe_indicators.iterrows():
        indicator_name = row['指標']
        value = row[latest_col]
        print(f"   {indicator_name}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ 關键指標檢查完成")
    print("=" * 60)

if __name__ == "__main__":
    check_key_metrics()