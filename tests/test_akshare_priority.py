#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試AKShare數據源優先級和財務指標修複效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.optimized_china_data import get_optimized_china_data_provider
from tradingagents.dataflows.akshare_utils import get_akshare_provider
from tradingagents.dataflows.tushare_utils import get_tushare_provider

def test_data_source_connection():
    """測試數據源連接狀態"""
    print("=" * 60)
    print("📡 測試數據源連接狀態")
    print("=" * 60)
    
    # 測試AKShare連接
    try:
        akshare_provider = get_akshare_provider()
        print(f"🔗 AKShare連接狀態: {'✅ 已連接' if akshare_provider.connected else '❌ 未連接'}")
    except Exception as e:
        print(f"❌ AKShare連接失败: {e}")
    
    # 測試Tushare連接
    try:
        tushare_provider = get_tushare_provider()
        print(f"🔗 Tushare連接狀態: {'✅ 已連接' if tushare_provider.connected else '❌ 未連接'}")
    except Exception as e:
        print(f"❌ Tushare連接失败: {e}")
    
    print()

def test_akshare_financial_data():
    """測試AKShare財務數據獲取"""
    print("=" * 60)
    print("📊 測試AKShare財務數據獲取")
    print("=" * 60)
    
    test_symbols = ['000001', '000002', '600519']
    
    try:
        akshare_provider = get_akshare_provider()
        if not akshare_provider.connected:
            print("❌ AKShare未連接，跳過測試")
            return
        
        for symbol in test_symbols:
            print(f"\n🔍 測試股票: {symbol}")
            try:
                financial_data = akshare_provider.get_financial_data(symbol)
                if financial_data:
                    print(f"✅ {symbol}: AKShare財務數據獲取成功")
                    
                    # 檢查主要財務指標
                    main_indicators = financial_data.get('main_indicators', {})
                    if main_indicators:
                        pe = main_indicators.get('市盈率', main_indicators.get('PE', 'N/A'))
                        pb = main_indicators.get('市净率', main_indicators.get('PB', 'N/A'))
                        roe = main_indicators.get('净資產收益率', main_indicators.get('ROE', 'N/A'))
                        print(f"   📈 PE: {pe}, PB: {pb}, ROE: {roe}")
                    else:
                        print(f"   ⚠️ 主要財務指標為空")
                else:
                    print(f"❌ {symbol}: AKShare財務數據獲取失败")
            except Exception as e:
                print(f"❌ {symbol}: AKShare財務數據獲取異常: {e}")
    
    except Exception as e:
        print(f"❌ AKShare財務數據測試失败: {e}")
    
    print()

def test_financial_metrics_with_data_source():
    """測試財務指標計算和數據源標识"""
    print("=" * 60)
    print("🧮 測試財務指標計算和數據源標识")
    print("=" * 60)
    
    test_symbols = ['000001', '000002', '600519']
    
    provider = get_optimized_china_data_provider()
    
    for symbol in test_symbols:
        print(f"\n🔍 測試股票: {symbol}")
        try:
            # 獲取基本面數據
            fundamentals = provider.get_fundamentals_data(symbol, force_refresh=True)
            
            # 檢查數據來源標识
            if "AKShare" in fundamentals:
                data_source = "AKShare"
            elif "Tushare" in fundamentals:
                data_source = "Tushare"
            else:
                data_source = "未知"
            
            print(f"📊 數據來源: {data_source}")
            
            # 提取PE、PB、ROE信息
            lines = fundamentals.split('\n')
            pe_line = next((line for line in lines if '市盈率(PE)' in line), None)
            pb_line = next((line for line in lines if '市净率(PB)' in line), None)
            roe_line = next((line for line in lines if '净資產收益率(ROE)' in line), None)
            
            if pe_line:
                pe_value = pe_line.split('**')[2].strip() if '**' in pe_line else pe_line.split(':')[1].strip()
                print(f"📈 PE: {pe_value}")
            
            if pb_line:
                pb_value = pb_line.split('**')[2].strip() if '**' in pb_line else pb_line.split(':')[1].strip()
                print(f"📈 PB: {pb_value}")
            
            if roe_line:
                roe_value = roe_line.split('**')[2].strip() if '**' in roe_line else roe_line.split(':')[1].strip()
                print(f"📈 ROE: {roe_value}")
            
            # 檢查是否有0倍的異常值
            if pe_line and ('0.0倍' in pe_line or '0倍' in pe_line):
                print(f"⚠️ 發現PE異常值: {pe_value}")
            
            if pb_line and ('0.00倍' in pb_line or '0倍' in pb_line):
                print(f"⚠️ 發現PB異常值: {pb_value}")
                
        except Exception as e:
            print(f"❌ {symbol}: 財務指標測試失败: {e}")
    
    print()

def test_data_source_priority():
    """測試數據源優先級"""
    print("=" * 60)
    print("🔄 測試數據源優先級")
    print("=" * 60)
    
    provider = get_optimized_china_data_provider()
    
    # 測試一個股票的財務指標獲取過程
    symbol = '000001'
    print(f"🔍 測試股票: {symbol}")
    
    try:
        # 直接調用內部方法測試
        real_metrics = provider._get_real_financial_metrics(symbol, 10.0)
        
        if real_metrics:
            data_source = real_metrics.get('data_source', '未知')
            print(f"✅ 財務數據獲取成功")
            print(f"📊 數據來源: {data_source}")
            print(f"📈 PE: {real_metrics.get('pe', 'N/A')}")
            print(f"📈 PB: {real_metrics.get('pb', 'N/A')}")
            print(f"📈 ROE: {real_metrics.get('roe', 'N/A')}")
            
            if data_source == 'AKShare':
                print("✅ 優先使用AKShare數據源成功")
            elif data_source == 'Tushare':
                print("⚠️ 使用Tushare备用數據源")
            else:
                print("❓ 數據源不明確")
        else:
            print("❌ 財務數據獲取失败")
            
    except Exception as e:
        print(f"❌ 數據源優先級測試失败: {e}")
    
    print()

def main():
    """主測試函數"""
    print("🚀 開始AKShare數據源優先級和財務指標修複測試")
    print()
    
    # 1. 測試數據源連接
    test_data_source_connection()
    
    # 2. 測試AKShare財務數據獲取
    test_akshare_financial_data()
    
    # 3. 測試數據源優先級
    test_data_source_priority()
    
    # 4. 測試財務指標和數據源標识
    test_financial_metrics_with_data_source()
    
    print("=" * 60)
    print("✅ 測試完成")
    print("=" * 60)

if __name__ == "__main__":
    main()