#!/usr/bin/env python3
"""
調試完整的AKShare數據獲取和解析流程
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設置詳細的日誌級別
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
from tradingagents.dataflows.akshare_utils import get_akshare_provider

def debug_full_flow():
    """調試完整的數據獲取和解析流程"""
    symbol = "600519"
    
    print("🔍 開始調試完整流程...")
    
    # 1. 初始化數據提供器
    provider = OptimizedChinaDataProvider()
    print(f"✅ 數據提供器初始化完成")
    
    # 2. 獲取AKShare財務數據
    print(f"\n📊 獲取AKShare財務數據...")
    akshare_provider = get_akshare_provider()
    financial_data = akshare_provider.get_financial_data(symbol)
    stock_info = akshare_provider.get_stock_info(symbol)
    
    print(f"   財務數據键: {list(financial_data.keys()) if financial_data else 'None'}")
    print(f"   股票信息: {stock_info}")
    
    # 3. 模擬股價獲取
    print(f"\n💰 模擬股價獲取...")
    current_price = "1800.0"  # 模擬股價
    try:
        price_value = float(current_price.replace('¥', '').replace(',', ''))
        print(f"   解析股價: {price_value}")
    except Exception as e:
        print(f"   股價解析失败: {e}")
        price_value = 10.0
    
    # 4. 調用解析函數
    print(f"\n🔧 調用解析函數...")
    try:
        metrics = provider._parse_akshare_financial_data(financial_data, stock_info, price_value)
        if metrics:
            print(f"✅ 解析成功!")
            print(f"   PE: {metrics.get('pe', 'N/A')}")
            print(f"   PB: {metrics.get('pb', 'N/A')}")
            print(f"   ROE: {metrics.get('roe', 'N/A')}")
            print(f"   數據來源: {metrics.get('data_source', 'N/A')}")
        else:
            print(f"❌ 解析失败，返回None")
    except Exception as e:
        print(f"❌ 解析異常: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 測試_get_real_financial_metrics函數
    print(f"\n🔍 測試_get_real_financial_metrics函數...")
    try:
        print(f"   調用參數: symbol={symbol}, price_value={price_value}")
        real_metrics = provider._get_real_financial_metrics(symbol, price_value)
        print(f"   返回結果: {real_metrics}")
        if real_metrics:
            print(f"✅ 真實財務指標獲取成功!")
            print(f"   PE: {real_metrics.get('pe', 'N/A')}")
            print(f"   PB: {real_metrics.get('pb', 'N/A')}")
            print(f"   ROE: {real_metrics.get('roe', 'N/A')}")
            print(f"   數據來源: {real_metrics.get('data_source', 'N/A')}")
        else:
            print(f"❌ 真實財務指標獲取失败")
    except Exception as e:
        print(f"❌ 真實財務指標獲取異常: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. 測試_estimate_financial_metrics函數
    print(f"\n🔍 測試_estimate_financial_metrics函數...")
    try:
        print(f"   調用參數: symbol={symbol}, current_price={current_price}")
        estimated_metrics = provider._estimate_financial_metrics(symbol, current_price)
        print(f"   返回結果: {estimated_metrics}")
        if estimated_metrics:
            print(f"✅ 財務指標估算成功!")
            print(f"   PE: {estimated_metrics.get('pe', 'N/A')}")
            print(f"   PB: {estimated_metrics.get('pb', 'N/A')}")
            print(f"   ROE: {estimated_metrics.get('roe', 'N/A')}")
            print(f"   數據來源: {estimated_metrics.get('data_source', 'N/A')}")
        else:
            print(f"❌ 財務指標估算失败")
    except Exception as e:
        print(f"❌ 財務指標估算異常: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "="*60)
    print(f"✅ 調試完成")
    print(f"="*60)

if __name__ == "__main__":
    debug_full_flow()