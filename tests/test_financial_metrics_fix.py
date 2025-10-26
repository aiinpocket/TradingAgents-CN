#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試財務指標修複效果
驗證是否使用真實財務數據而不是分類估算
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
import logging

# 設置日誌級別
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_financial_metrics():
    """測試財務指標獲取"""
    print("🔧 測試財務指標修複效果")
    print("=" * 80)
    
    # 測試股票列表
    test_symbols = [
        "000001",  # 平安銀行
        "000002",  # 万科A
        "300001",  # 特锐德（創業板）
        "600036",  # 招商銀行
        "600519",  # 贵州茅台
    ]
    
    provider = OptimizedChinaDataProvider()
    
    for symbol in test_symbols:
        print(f"\n📊 測試股票: {symbol}")
        print("-" * 50)
        
        try:
            # 獲取基本面數據
            fundamentals = provider.get_fundamentals_data(symbol, force_refresh=True)
            
            # 檢查是否包含數據來源說明
            if "✅ **數據說明**: 財務指標基於Tushare真實財務數據計算" in fundamentals:
                print(f"✅ {symbol}: 使用真實財務數據")
            elif "⚠️ **數據說明**: 部分財務指標為估算值" in fundamentals:
                print(f"⚠️ {symbol}: 使用估算財務數據")
            else:
                print(f"❓ {symbol}: 數據來源不明確")
            
            # 提取關键財務指標
            lines = fundamentals.split('\n')
            pe_line = next((line for line in lines if "市盈率(PE)" in line), None)
            pb_line = next((line for line in lines if "市净率(PB)" in line), None)
            roe_line = next((line for line in lines if "净資產收益率(ROE)" in line), None)
            
            if pe_line:
                print(f"  PE: {pe_line.split(':')[1].strip()}")
            if pb_line:
                print(f"  PB: {pb_line.split(':')[1].strip()}")
            if roe_line:
                print(f"  ROE: {roe_line.split(':')[1].strip()}")
                
        except Exception as e:
            print(f"❌ {symbol}: 測試失败 - {e}")

def test_tushare_connection():
    """測試Tushare連接"""
    print("\n🔧 測試Tushare連接")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        provider = get_tushare_provider()
        if provider.connected:
            print("✅ Tushare連接成功")
            
            # 測試獲取財務數據
            test_symbol = "000001"
            financial_data = provider.get_financial_data(test_symbol)
            
            if financial_data:
                print(f"✅ 成功獲取{test_symbol}財務數據")
                print(f"  資產负债表: {len(financial_data.get('balance_sheet', []))}條記錄")
                print(f"  利润表: {len(financial_data.get('income_statement', []))}條記錄")
                print(f"  現金流量表: {len(financial_data.get('cash_flow', []))}條記錄")
            else:
                print(f"⚠️ 未獲取到{test_symbol}財務數據")
        else:
            print("❌ Tushare連接失败")
            
    except Exception as e:
        print(f"❌ Tushare測試失败: {e}")

def main():
    """主函數"""
    print("🚀 開始測試財務指標修複效果")
    print("=" * 80)
    
    # 測試Tushare連接
    test_tushare_connection()
    
    # 測試財務指標
    test_financial_metrics()
    
    print("\n✅ 測試完成")
    print("=" * 80)
    print("說明:")
    print("- ✅ 表示使用真實財務數據")
    print("- ⚠️ 表示使用估算數據（Tushare不可用時的备用方案）")
    print("- ❌ 表示測試失败")

if __name__ == "__main__":
    main()