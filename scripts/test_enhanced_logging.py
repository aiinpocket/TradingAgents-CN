#!/usr/bin/env python3
"""
測試增强的Tushare日誌功能
驗證詳細日誌是否能幫助追蹤數據獲取問題
"""

import sys
import os
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_enhanced_logging():
    """測試增强的日誌功能"""
    print("🔍 測試增强的Tushare日誌功能")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        
        manager = DataSourceManager()
        
        # 測試用例1: 正常股票代碼
        print("\n📊 測試用例1: 正常股票代碼 (000001)")
        print("-" * 60)
        
        symbol = "000001"
        start_date = "2025-01-10"
        end_date = "2025-01-17"
        
        result = manager.get_stock_data(symbol, start_date, end_date)
        
        print(f"結果長度: {len(result) if result else 0}")
        print(f"結果預覽: {result[:100] if result else 'None'}")
        
        # 測試用例2: 可能有問題的股票代碼
        print("\n📊 測試用例2: 創業板股票 (300033)")
        print("-" * 60)
        
        symbol = "300033"
        start_date = "2025-01-10"
        end_date = "2025-01-17"
        
        result = manager.get_stock_data(symbol, start_date, end_date)
        
        print(f"結果長度: {len(result) if result else 0}")
        print(f"結果預覽: {result[:100] if result else 'None'}")
        
        # 測試用例3: 可能不存在的股票代碼
        print("\n📊 測試用例3: 可能不存在的股票代碼 (999999)")
        print("-" * 60)
        
        symbol = "999999"
        start_date = "2025-01-10"
        end_date = "2025-01-17"
        
        result = manager.get_stock_data(symbol, start_date, end_date)
        
        print(f"結果長度: {len(result) if result else 0}")
        print(f"結果預覽: {result[:100] if result else 'None'}")
        
        # 測試用例4: 未來日期範围
        print("\n📊 測試用例4: 未來日期範围")
        print("-" * 60)
        
        symbol = "000001"
        start_date = "2025-12-01"
        end_date = "2025-12-31"
        
        result = manager.get_stock_data(symbol, start_date, end_date)
        
        print(f"結果長度: {len(result) if result else 0}")
        print(f"結果預覽: {result[:100] if result else 'None'}")
        
        print("\n✅ 增强日誌測試完成")
        print("📋 請查看日誌文件以獲取詳細的調試信息")
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

def test_direct_tushare_provider():
    """直接測試Tushare Provider"""
    print("\n🔍 直接測試Tushare Provider")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return
        
        # 測試直接調用
        symbol = "300033"
        start_date = "2025-01-10"
        end_date = "2025-01-17"
        
        print(f"📊 直接調用Provider: {symbol}")
        data = provider.get_stock_daily(symbol, start_date, end_date)
        
        if data is not None and not data.empty:
            print(f"✅ 直接調用成功: {len(data)}條數據")
            print(f"📊 數據列: {list(data.columns)}")
            print(f"📊 日期範围: {data['trade_date'].min()} 到 {data['trade_date'].max()}")
        else:
            print(f"❌ 直接調用返回空數據")
            
    except Exception as e:
        print(f"❌ 直接測試失败: {e}")
        import traceback
        traceback.print_exc()

def test_adapter_layer():
    """測試適配器層"""
    print("\n🔍 測試適配器層")
    print("=" * 80)
    
    try:
        from tradingagents.dataflows.tushare_adapter import get_tushare_adapter
        
        adapter = get_tushare_adapter()
        
        if not adapter.provider or not adapter.provider.connected:
            print("❌ 適配器未連接")
            return
        
        # 測試適配器調用
        symbol = "300033"
        start_date = "2025-01-10"
        end_date = "2025-01-17"
        
        print(f"📊 調用適配器: {symbol}")
        data = adapter.get_stock_data(symbol, start_date, end_date)
        
        if data is not None and not data.empty:
            print(f"✅ 適配器調用成功: {len(data)}條數據")
            print(f"📊 數據列: {list(data.columns)}")
        else:
            print(f"❌ 適配器調用返回空數據")
            
    except Exception as e:
        print(f"❌ 適配器測試失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("🧪 增强日誌功能測試")
    print("=" * 80)
    print("📝 此測試将生成詳細的日誌信息，幫助追蹤數據獲取問題")
    print("📁 請查看 logs/tradingagents.log 文件獲取完整日誌")
    print("=" * 80)
    
    # 1. 測試增强日誌功能
    test_enhanced_logging()
    
    # 2. 直接測試Provider
    test_direct_tushare_provider()
    
    # 3. 測試適配器層
    test_adapter_layer()
    
    print("\n📋 測試总結")
    print("=" * 60)
    print("✅ 增强日誌功能測試完成")
    print("📊 現在每個數據獲取步骤都有詳細的日誌記錄")
    print("🔍 包括:")
    print("   - API調用前後的狀態")
    print("   - 參數轉換過程")
    print("   - 返回數據的詳細信息")
    print("   - 異常的完整堆棧")
    print("   - 緩存操作的詳細過程")
    print("📁 詳細日誌請查看: logs/tradingagents.log")

if __name__ == "__main__":
    main()
