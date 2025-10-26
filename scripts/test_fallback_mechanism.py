#!/usr/bin/env python3
"""
測試數據源降級機制
驗證當Tushare返回空數據時是否能正確降級到其他數據源
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_data_source_availability():
    """測試數據源可用性"""
    print("🔍 檢查數據源可用性...")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        manager = DataSourceManager()
        
        print(f"📊 默認數據源: {manager.default_source.value}")
        print(f"📊 當前數據源: {manager.current_source.value}")
        print(f"📊 可用數據源: {[s.value for s in manager.available_sources]}")
        
        return manager
        
    except Exception as e:
        print(f"❌ 數據源管理器初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_fallback_mechanism(manager):
    """測試降級機制"""
    print("\n🔄 測試降級機制...")
    print("=" * 60)
    
    # 測試股票代碼 - 選擇一個可能在Tushare中没有數據的代碼
    test_symbol = "300033"  # 同創科技
    start_date = "2025-01-10"
    end_date = "2025-01-17"
    
    print(f"📊 測試股票: {test_symbol}")
    print(f"📊 時間範围: {start_date} 到 {end_date}")
    
    try:
        # 調用數據獲取方法
        result = manager.get_stock_data(test_symbol, start_date, end_date)
        
        print(f"\n📋 獲取結果:")
        print(f"   結果長度: {len(result) if result else 0}")
        print(f"   前200字符: {result[:200] if result else 'None'}")
        
        # 檢查是否成功
        if result and "❌" not in result and "錯誤" not in result:
            print("✅ 數據獲取成功")
            return True
        else:
            print("⚠️ 數據獲取失败或返回錯誤")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中發生異常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_sources(manager):
    """測試特定數據源"""
    print("\n🎯 測試特定數據源...")
    print("=" * 60)
    
    test_symbol = "000001"  # 平安銀行 - 更常见的股票
    start_date = "2025-01-10"
    end_date = "2025-01-17"
    
    # 測試每個可用的數據源
    for source in manager.available_sources:
        print(f"\n📊 測試數據源: {source.value}")
        
        try:
            # 臨時切換到该數據源
            original_source = manager.current_source
            manager.current_source = source
            
            result = manager.get_stock_data(test_symbol, start_date, end_date)
            
            # 恢複原數據源
            manager.current_source = original_source
            
            if result and "❌" not in result and "錯誤" not in result:
                print(f"   ✅ {source.value} 獲取成功")
            else:
                print(f"   ❌ {source.value} 獲取失败")
                print(f"   錯誤信息: {result[:100] if result else 'None'}")
                
        except Exception as e:
            print(f"   ❌ {source.value} 異常: {e}")

def main():
    """主函數"""
    print("🧪 數據源降級機制測試")
    print("=" * 80)
    
    # 1. 檢查數據源可用性
    manager = test_data_source_availability()
    if not manager:
        print("❌ 無法初始化數據源管理器，測試终止")
        return
    
    # 2. 測試降級機制
    success = test_fallback_mechanism(manager)
    
    # 3. 測試特定數據源
    test_specific_sources(manager)
    
    # 4. 总結
    print("\n📋 測試总結")
    print("=" * 60)
    if success:
        print("✅ 降級機制測試通過")
    else:
        print("⚠️ 降級機制可能存在問題")
    
    print(f"📊 可用數據源數量: {len(manager.available_sources)}")
    print(f"📊 建议: 確保至少有2個數據源可用以支持降級")

if __name__ == "__main__":
    main()
