#!/usr/bin/env python3
"""
AKShare財務數據獲取調試腳本
"""

import sys
import os
import logging

# 設置日誌級別為DEBUG以查看詳細信息
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s')

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.akshare_utils import AKShareProvider

def test_akshare_financial_data():
    """測試AKShare財務數據獲取"""
    print("=" * 60)
    print("🔍 AKShare財務數據獲取調試測試")
    print("=" * 60)
    
    # 1. 獲取AKShare提供者
    print("\n1. 獲取AKShare提供者...")
    provider = AKShareProvider()
    print(f"   連接狀態: {provider.connected}")
    
    if not provider.connected:
        print("❌ AKShare未連接，無法繼续測試")
        return
    
    # 2. 直接調用get_financial_data方法
    print("\n2. 直接調用get_financial_data方法...")
    symbol = "600519"
    
    try:
        financial_data = provider.get_financial_data(symbol)
        print(f"   返回結果類型: {type(financial_data)}")
        print(f"   返回結果: {financial_data}")
        
        if financial_data:
            print("✅ 成功獲取財務數據")
            for key, value in financial_data.items():
                if hasattr(value, '__len__'):
                    print(f"   - {key}: {len(value)}條記錄")
                else:
                    print(f"   - {key}: {type(value)}")
        else:
            print("❌ 未獲取到財務數據")
            
    except Exception as e:
        print(f"❌ 調用get_financial_data失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 測試條件判斷
    print("\n3. 測試條件判斷...")
    test_data = {}
    print(f"   空字典 any(test_data.values()): {any(test_data.values())}")
    
    test_data = {'main_indicators': None}
    print(f"   包含None any(test_data.values()): {any(test_data.values())}")
    
    test_data = {'main_indicators': {}}
    print(f"   包含空字典 any(test_data.values()): {any(test_data.values())}")
    
    test_data = {'main_indicators': {'pe': 18.5}}
    print(f"   包含數據 any(test_data.values()): {any(test_data.values())}")
    
    print("\n" + "=" * 60)
    print("✅ 調試測試完成")
    print("=" * 60)

if __name__ == "__main__":
    test_akshare_financial_data()